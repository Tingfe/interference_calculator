# 无机质谱干扰计算器优化路线图

## 执行摘要

### 项目概况
- **项目名称**: 无机质谱峰干扰计算器 (Inorganic MS Interference Calculator)
- **当前版本**: 2.5.0
- **技术栈**: Python 3.9+, PyQt5, NumPy, Pandas
- **核心功能**: GDMS/ICP-MS/SIMS 质谱峰干扰筛查、模板化无机干扰生成、目标峰中心谱图可视化
- **用户群体**: 质谱分析科研人员、GDMS/ICP-MS 实验室技术人员

### 优化愿景
通过五个阶段的系统性优化，将本项目从"可用的科学工具"提升为"高性能、易维护、可扩展的专业级质谱分析平台"。

### 关键成果指标 (KPI)
1. **性能**: 计算速度提升 10-100 倍（maxsize≥4 场景）
2. **内存**: 大规模计算内存占用降低 50-70%
3. **可维护性**: UI 代码单文件 <1000 行，测试覆盖率 >90%
4. **用户体验**: 配置持久化、预设管理、国际化扩展
5. **可扩展性**: 插件系统支持自定义物种模板和形成因子

---

## 详细路线图

### 第一阶段: 核心性能优化 (P0 - 高优先级)
**时间周期**: 3 周  
**影响范围**: 计算引擎、内存管理  
**风险等级**: 中（需保持 API 兼容性）

#### 1.1 计算引擎性能提升

**问题描述**:
- `interference()` 函数在 `maxsize≥4` 时遭遇组合爆炸
- 当前实现使用 `itertools.combinations_with_replacement` 生成所有同位素组合
- 例如：10 个元素 × maxsize=4 → 组合数可达数百万级别
- 无预过滤机制，大量无效组合进入质量计算阶段

**技术方案**:

##### A. 预过滤剪枝策略
```python
# 伪代码示例
def interference_optimized(atoms, target, targetrange, maxsize, ...):
    # 1. 根据目标 m/z 和窗口范围，预先排除不可能进入窗口的元素
    min_mz = target_mz - targetrange
    max_mz = target_mz + targetrange
    
    # 2. 基于最小/最大原子质量快速剪枝
    filtered_atoms = []
    for atom in atoms:
        min_possible_mass = get_min_isotope_mass(atom) * maxsize
        max_possible_mass = get_max_isotope_mass(atom) * maxsize
        if overlaps(min_possible_mass, max_possible_mass, min_mz, max_mz):
            filtered_atoms.append(atom)
    
    # 3. 对每个 size 进行增量式质量边界检查
    for size in range(1, maxsize + 1):
        generate_combinations_with_pruning(filtered_atoms, size, min_mz, max_mz)
```

**预期收益**:
- 减少 60-80% 的无效组合生成
- 对于典型 GDMS 场景（~50 元素），剪枝后剩余元素约 15-20 个

##### B. 并行计算架构
```python
from multiprocessing import Pool, cpu_count

def parallel_interference(atoms, target, targetrange, maxsize, ...):
    # 按分子大小拆分任务
    tasks = [(atoms, target, targetrange, size, ...) 
             for size in range(1, maxsize + 1)]
    
    with Pool(processes=cpu_count()) as pool:
        results = pool.starmap(_compute_size_chunk, tasks)
    
    return pd.concat(results)
```

**实施要点**:
- 使用 `multiprocessing.Pool` 而非 `threading`（Python GIL 限制）
- 每个 size 独立计算，天然适合并行
- 需要处理进程间数据序列化开销（使用共享内存或 numpy 数组）

**预期收益**:
- 4 核 CPU: 速度提升 3-4 倍
- 8 核 CPU: 速度提升 6-8 倍
- 需注意小任务并行开销，设置阈值（如 size≥3 才并行）

##### C. GPU 加速（可选，CuPy）
```python
try:
    import cupy as cp
    USE_GPU = True
except ImportError:
    USE_GPU = False

def gpu_accelerated_mass_calculation(isotope_masses, combinations):
    if USE_GPU:
        masses_gpu = cp.array(isotope_masses)
        combos_gpu = cp.array(combinations)
        # GPU 批量求和
        result = masses_gpu[combos_gpu].sum(axis=1)
        return cp.asnumpy(result)
    else:
        # 回退到 NumPy
        return np.array(isotope_masses)[combinations].sum(axis=1)
```

**适用场景**:
- maxsize≥5 且元素数量 >30 的极端情况
- 需要 NVIDIA GPU 和 CuPy 安装

**预期收益**:
- 相比纯 CPU: 额外 5-10 倍加速（取决于 GPU 型号）
- 但增加依赖复杂度，作为可选特性

**验收标准**:
- [ ] maxsize=4, 50 元素场景：计算时间从 ~30s 降至 <3s
- [ ] maxsize=3, 50 元素场景：计算时间从 ~2s 降至 <0.5s
- [ ] API 签名保持不变，向后兼容
- [ ] 单元测试覆盖所有剪枝边界条件

**实施难度**: ⭐⭐⭐ (中等)  
**时间估算**: 2 周

---

#### 1.2 内存优化

**问题描述**:
- 当前实现在生成所有组合后才进行质量过滤
- `isotope_combos` 和 `mass_combos` 列表在内存中完整保留
- maxsize=5, 50 元素时，中间数据结构可达 GB 级别

**技术方案**:

##### A. 生成器模式替代列表
```python
# 当前实现（内存密集）
isotope_combos = []
for size in range(1, maxsize + 1):
    i = itertools.combinations_with_replacement(picked_atoms['isotope'], size)
    isotope_combos.extend(list(i))  # ❌ 立即生成完整列表

# 优化实现（惰性求值）
def generate_isotope_combos(atoms, maxsize):
    """生成器：按需产生组合"""
    for size in range(1, maxsize + 1):
        for combo in itertools.combinations_with_replacement(atoms, size):
            yield combo

# 使用时
for combo in generate_isotope_combos(atoms, maxsize):
    mass = calculate_mass(combo)
    if in_range(mass, target_mz, targetrange):
        yield build_result(combo, mass)
```

##### B. 流式数据处理
```python
import pandas as pd

def streaming_interference(...):
    """使用迭代器逐步构建 DataFrame，避免一次性加载"""
    chunks = []
    chunk_size = 10000
    
    buffer = []
    for result in generate_filtered_results(...):
        buffer.append(result)
        if len(buffer) >= chunk_size:
            chunks.append(pd.DataFrame(buffer))
            buffer = []
    
    if buffer:
        chunks.append(pd.DataFrame(buffer))
    
    return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
```

##### C. 数据类型优化
```python
# 当前：默认 float64
data = pd.DataFrame({'mass/charge': masses})  # float64

# 优化：根据精度需求选择 float32
data = pd.DataFrame({
    'mass/charge': masses.astype(np.float32),  # 节省 50% 内存
    'probability': probs.astype(np.float32),
    'charge': charges.astype(np.int8),  # int8 足够表示电荷
})
```

**预期收益**:
- 峰值内存占用降低 50-70%
- maxsize=5, 50 元素场景：从 ~2GB 降至 ~500MB

**验收标准**:
- [ ] 内存分析工具（memory_profiler）验证峰值内存降低 ≥50%
- [ ] 计算结果与优化前完全一致（数值误差 <1e-6）
- [ ] 大数据集场景不再触发 MemoryError

**实施难度**: ⭐⭐ (低-中)  
**时间估算**: 1 周

---

### 第二阶段: 架构重构 (P1 - 中优先级)
**时间周期**: 4-5 周  
**影响范围**: UI 层、配置管理、扩展机制  
**风险等级**: 高（需保持 GUI 行为一致性）

#### 2.1 UI 代码模块化

**问题描述**:
- `ui.py` 文件近 5000 行，违反单一职责原则
- 控制逻辑、视图渲染、事件处理混杂
- 新增功能时需修改多处，容易引入回归错误

**技术方案**:

##### A. 组件拆分架构
```
interference_calculator/
├── ui/                          # 新建 UI 模块目录
│   ├── __init__.py
│   ├── main_window.py           # 主窗口框架 (~500 行)
│   ├── control_panel.py         # 左侧控制面板 (~800 行)
│   │   ├── mode_selector.py     # 工作模式选择
│   │   ├── target_input.py      # 目标峰输入
│   │   ├── element_selector.py  # 元素选择器
│   │   └── ion_model.py         # 离子模型设置
│   ├── results_view.py          # 右侧结果区 (~600 行)
│   │   ├── summary_bar.py       # 结果概览条
│   │   ├── results_table.py     # 候选峰表格
│   │   └── empty_state.py       # 空状态提示
│   ├── spectrum/                # 谱图模块
│   │   ├── spectrum_widget.py   # 谱图主控件 (~700 行)
│   │   ├── peak_renderer.py     # 峰渲染器
│   │   ├── profile_overlay.py   # 实测峰形叠加
│   │   └── toolbar.py           # 谱图工具栏
│   ├── dialogs/                 # 对话框
│   │   ├── help_dialog.py       # 帮助窗口
│   │   ├── isotope_ratio.py     # 同位素比查看器
│   │   └── run_selector.py      # Run 选择器
│   └── mixins/                  # 通用 Mixin 类
│       ├── localization.py      # 国际化支持
│       ├── state_management.py  # 状态管理
│       └── file_io.py           # 文件导入导出
└── ui_legacy.py                 # 兼容性入口（废弃警告）
```

##### B. MVVM 模式引入
```python
# viewmodel/main_vm.py
class MainViewModel(QtCore.QObject):
    """主窗口视图模型：分离状态管理与 UI 逻辑"""
    
    # 信号
    calculationStarted = QtCore.pyqtSignal()
    calculationFinished = QtCore.pyqtSignal(pd.DataFrame)
    elementsChanged = QtCore.pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self._mode = 'gdms'
        self._elements = []
        self._target = None
        self._results = None
    
    @property
    def mode(self):
        return self._mode
    
    @mode.setter
    def mode(self, value):
        if self._mode != value:
            self._mode = value
            self._update_defaults()  # 自动更新默认参数
    
    def calculate(self):
        """异步计算，发射信号通知结果"""
        self.calculationStarted.emit()
        worker = CalculationWorker(...)
        worker.finished.connect(self._on_calculation_done)
        worker.start()
```

##### C. 提取 Mixin 类
```python
# mixins/localization.py
class LocalizationMixin:
    """提供多语言支持的 Mixin"""
    
    def tr(self, text):
        """翻译文本"""
        return QCoreApplication.translate(self.__class__.__name__, text)
    
    def set_language(self, lang):
        """切换语言并刷新界面"""
        self._current_language = lang
        self.refresh_labels()

# mixins/state_management.py
class StateManagementMixin:
    """保存/恢复界面状态的 Mixin"""
    
    def save_state(self):
        """保存当前界面状态到字典"""
        return {
            'mode': self.mode_selector.currentText(),
            'elements': self.element_chips.get_elements(),
            'window_width': self.window_spinbox.value(),
        }
    
    def restore_state(self, state_dict):
        """从字典恢复界面状态"""
        self.mode_selector.setCurrentText(state_dict['mode'])
        # ...
```

**重构步骤**:
1. **Week 1**: 创建目录结构，提取 `ControlPanel` 组件
2. **Week 2**: 提取 `ResultsView` 和 `SpectrumWidget`
3. **Week 3**: 实现 `MainViewModel`，迁移状态管理逻辑
4. **Week 4**: 集成测试、修复回归问题、更新文档

**验收标准**:
- [ ] `ui.py` 拆分为 ≤10 个文件，单文件 <1000 行
- [ ] 所有现有功能正常工作（回归测试通过）
- [ ] 新增组件有独立的单元测试
- [ ] 代码可读性评分提升（使用 pylint/mccabe 量化）

**实施难度**: ⭐⭐⭐⭐⭐ (高)  
**时间估算**: 3-4 周

---

#### 2.2 配置持久化系统

**问题描述**:
- 用户每次启动需重新设置模式、元素、窗口宽度等
- 无法保存常用的仪器预设（如特定 GDMS 型号的参数）
- 缺少"最近使用的目标峰"历史记录

**技术方案**:

##### A. JSON 配置文件结构
```json
{
  "version": "2.6.0",
  "general": {
    "language": "zh-CN",
    "last_mode": "gdms",
    "theme": "light"
  },
  "presets": {
    "instruments": [
      {
        "name": "Thermo Fisher ELEMENT XR",
        "mode": "icp-ms",
        "default_mrp": 10000,
        "default_window_ppm": 400,
        "charges": [1, 2]
      }
    ],
    "element_sets": [
      {
        "name": "硅酸盐基体",
        "elements": ["Si", "O", "Al", "Fe", "Ca", "Na", "K"]
      }
    ]
  },
  "recent_targets": [
    {"formula": "75As", "timestamp": "2026-06-08T10:30:00"},
    {"formula": "56Fe", "timestamp": "2026-06-07T15:20:00"}
  ],
  "ui_state": {
    "window_geometry": "...",
    "splitter_positions": [...],
    "last_import_directory": "/home/user/gdms_data"
  }
}
```

##### B. 配置管理器实现
```python
# config/manager.py
import json
from pathlib import Path

class ConfigManager:
    """统一管理应用配置"""
    
    CONFIG_FILE = Path.home() / '.interference_calculator' / 'config.json'
    
    def __init__(self):
        self._config = self._load_or_create()
    
    def _load_or_create(self):
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default = self._create_default()
            self.save(default)
            return default
    
    def get(self, key, default=None):
        """获取配置项，支持嵌套键如 'general.language'"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            value = value.get(k, default)
        return value
    
    def set(self, key, value):
        """设置配置项并自动保存"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self.save()
    
    def add_recent_target(self, formula):
        """添加最近使用的目标峰（最多保留 10 个）"""
        recent = self._config.setdefault('recent_targets', [])
        # 移除重复项
        recent = [t for t in recent if t['formula'] != formula]
        recent.insert(0, {
            'formula': formula,
            'timestamp': datetime.now().isoformat()
        })
        self._config['recent_targets'] = recent[:10]
        self.save()
    
    def export_preset(self, name, preset_data):
        """导出预设到文件"""
        filepath = Path.home() / '.interference_calculator' / 'presets' / f'{name}.json'
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, indent=2, ensure_ascii=False)
    
    def import_preset(self, filepath):
        """从文件导入预设"""
        with open(filepath, 'r', encoding='utf-8') as f:
            preset = json.load(f)
        # 合并到现有配置
        self._merge_preset(preset)
        self.save()
```

##### C. UI 集成
```python
# 在主窗口初始化时加载配置
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        
        # 恢复上次使用的语言
        lang = self.config.get('general.language', 'zh-CN')
        self.set_language(lang)
        
        # 恢复最近的元素集合
        recent_elements = self.config.get('general.last_elements', [])
        if recent_elements:
            self.element_selector.set_elements(recent_elements)
    
    def closeEvent(self, event):
        """关闭窗口时保存状态"""
        self.config.set('ui_state.window_geometry', self.saveGeometry().data())
        self.config.set('general.last_mode', self.mode_selector.currentText())
        super().closeEvent(event)
```

**验收标准**:
- [ ] 用户偏好（语言、模式、元素）在重启后自动恢复
- [ ] 支持导出/导入预设文件（.json 格式）
- [ ] 最近使用的 10 个目标峰显示在下拉框顶部
- [ ] 配置文件位于用户主目录（跨平台兼容）

**实施难度**: ⭐⭐ (低)  
**时间估算**: 1 周

---

#### 2.3 插件系统架构

**问题描述**:
- 新增物种模板（如有机质谱中的溶剂加合物）需修改核心代码
- 形成因子因仪器/方法而异，硬编码在 `inorganic.py`
- 社区贡献者难以扩展功能

**技术方案**:

##### A. 插件接口定义
```python
# plugins/interfaces.py
from abc import ABC, abstractmethod

class SpeciesTemplatePlugin(ABC):
    """物种模板插件接口"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    @abstractmethod
    def generate_candidates(self, atoms: list, maxsize: int) -> list:
        """
        生成候选物种
        
        Args:
            atoms: 可用元素列表
            maxsize: 最大原子数
        
        Returns:
            候选物种列表，每个物种为 (formula, species_type, charge) 元组
        """
        pass

class FormationFactorPlugin(ABC):
    """形成因子插件接口"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def get_factors(self, species_type: str) -> float:
        """
        获取指定物种类型的形成因子
        
        Args:
            species_type: 物种类型（如 'oxide', 'hydride'）
        
        Returns:
            形成因子值
        """
        pass

class InstrumentPresetPlugin(ABC):
    """仪器预设插件接口"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def get_preset(self) -> dict:
        """
        获取仪器预设
        
        Returns:
            包含 mode, default_mrp, default_window_ppm, charges 的字典
        """
        pass
```

##### B. YAML 外部配置支持
```yaml
# plugins/custom_templates.yaml
plugin_type: species_template
name: "有机溶剂加合物"
description: "常见 LC-MS 溶剂加合物模板"

templates:
  - type: "acetonitrile adduct"
    formula_pattern: "M + CH3CN"
    mass_offset: 41.026549
    formation_factor: 1.0e-4
  
  - type: "methanol adduct"
    formula_pattern: "M + CH3OH"
    mass_offset: 32.026216
    formation_factor: 5.0e-5

formation_factors:
  acetonitrile adduct: 1.0e-4
  methanol adduct: 5.0e-5
  formic acid adduct: 2.0e-5
```

##### C. 插件加载器
```python
# plugins/loader.py
import importlib
import yaml
from pathlib import Path

class PluginLoader:
    """动态加载插件"""
    
    PLUGIN_DIRS = [
        Path.home() / '.interference_calculator' / 'plugins',
        Path(__file__).parent / 'builtin_plugins',
    ]
    
    def __init__(self):
        self._plugins = {
            'species_template': [],
            'formation_factor': [],
            'instrument_preset': [],
        }
    
    def discover_and_load(self):
        """扫描并加载所有插件"""
        for plugin_dir in self.PLUGIN_DIRS:
            if not plugin_dir.exists():
                continue
            
            # 加载 Python 插件
            for py_file in plugin_dir.glob('*.py'):
                if py_file.name.startswith('_'):
                    continue
                self._load_python_plugin(py_file)
            
            # 加载 YAML 配置插件
            for yaml_file in plugin_dir.glob('*.yaml'):
                self._load_yaml_plugin(yaml_file)
    
    def _load_python_plugin(self, filepath):
        """加载 Python 模块插件"""
        module_name = filepath.stem
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 查找实现了接口的类
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, SpeciesTemplatePlugin):
                if attr is not SpeciesTemplatePlugin:
                    self._plugins['species_template'].append(attr())
    
    def _load_yaml_plugin(self, filepath):
        """加载 YAML 配置插件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        plugin_type = config.get('plugin_type')
        if plugin_type == 'species_template':
            plugin = YAMLSpeciesTemplate(config)
            self._plugins['species_template'].append(plugin)
        elif plugin_type == 'formation_factor':
            plugin = YAMLFormationFactor(config)
            self._plugins['formation_factor'].append(plugin)
    
    def get_plugins(self, plugin_type):
        """获取指定类型的插件列表"""
        return self._plugins.get(plugin_type, [])
```

##### D. 热加载机制
```python
# plugins/hot_reload.py
import watchdog.observers
import watchdog.events

class PluginHotReloader:
    """监控插件目录变化，自动重新加载"""
    
    def __init__(self, plugin_loader):
        self.loader = plugin_loader
        self.observer = watchdog.observers.Observer()
    
    def start_watching(self):
        """开始监控插件目录"""
        for plugin_dir in PluginLoader.PLUGIN_DIRS:
            if plugin_dir.exists():
                handler = PluginChangeHandler(self.loader)
                self.observer.schedule(handler, str(plugin_dir), recursive=False)
        self.observer.start()
    
    def stop_watching(self):
        self.observer.stop()

class PluginChangeHandler(watchdog.events.FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(('.py', '.yaml')):
            print(f"检测到新插件: {event.src_path}")
            # 触发重新加载
    
    def on_modified(self, event):
        if event.src_path.endswith(('.py', '.yaml')):
            print(f"插件已更新: {event.src_path}")
            # 触发重新加载
```

**验收标准**:
- [ ] 支持 Python 类和 YAML 配置两种插件形式
- [ ] 插件放置在 `~/.interference_calculator/plugins/` 即可自动加载
- [ ] 新增物种模板无需修改核心代码
- [ ] 提供示例插件和开发文档

**实施难度**: ⭐⭐⭐⭐ (中高)  
**时间估算**: 2-3 周

---

### 第三阶段: 质量保证增强 (P1 - 中优先级)
**时间周期**: 2-3 周  
**影响范围**: 测试体系、日志系统  
**风险等级**: 低

#### 3.1 测试覆盖率提升

**现状分析**:
- 核心逻辑测试覆盖率 >90%（优秀）
- UI 测试依赖 `offscreen` 平台，缺乏视觉回归测试
- 缺少性能基准测试
- GDMS 文件格式边缘情况覆盖不足

**技术方案**:

##### A. 截图对比测试
```python
# tests/test_ui_screenshots.py
import pytest
from pytestqt.plugin import QtBot
from PIL import Image
import imagehash

@pytest.mark.gui
def test_main_window_snapshot(qtbot, snapshot_dir):
    """主界面截图对比测试"""
    from interference_calculator.ui import MainWindow
    
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    qtbot.waitForWindowShown(window)
    
    # 截取窗口
    screenshot = window.grab()
    image_path = snapshot_dir / 'main_window.png'
    screenshot.save(str(image_path))
    
    # 与基准截图对比（允许 5% 像素差异）
    baseline_path = BASELINE_DIR / 'main_window.png'
    assert images_similar(image_path, baseline_path, threshold=0.05)

def images_similar(img1_path, img2_path, threshold=0.05):
    """使用感知哈希比较图片相似度"""
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    
    hash1 = imagehash.average_hash(img1)
    hash2 = imagehash.average_hash(img2)
    
    # 计算哈希距离（0-64，越小越相似）
    distance = hash1 - hash2
    similarity = 1 - (distance / 64)
    
    return similarity >= (1 - threshold)
```

**所需依赖**:
```txt
pytest-qt>=4.2.0
Pillow>=9.0.0
ImageHash>=4.3.0
```

##### B. 性能回归测试套件
```python
# tests/test_performance.py
import pytest
import time
from interference_calculator.inorganic import inorganic_interference

@pytest.mark.performance
def test_interference_speed_maxsize3(benchmark):
    """maxsize=3 性能基准测试"""
    atoms = ['Ar', 'Cl', 'As', 'O', 'H', 'C', 'N', 'Fe', 'Cu', 'Zn']
    
    def run_calculation():
        return inorganic_interference(
            atoms, '75As', targetrange=0.074921,
            charge=[1, 2], maxsize=3, risk_preset='gdms'
        )
    
    # 使用 pytest-benchmark 自动统计
    result = benchmark(run_calculation)
    
    # 断言：平均耗时 <500ms
    assert benchmark.stats['mean'] < 0.5

@pytest.mark.performance
def test_interference_speed_maxsize4(benchmark):
    """maxsize=4 性能基准测试"""
    atoms = ['Ar', 'Cl', 'As', 'O', 'H', 'C', 'N', 'Fe', 'Cu', 'Zn']
    
    def run_calculation():
        return inorganic_interference(
            atoms, '75As', targetrange=0.074921,
            charge=[1, 2], maxsize=4, risk_preset='gdms'
        )
    
    result = benchmark(run_calculation)
    assert benchmark.stats['mean'] < 3.0  # 优化目标：<3s

@pytest.mark.performance
def test_memory_usage_large_dataset():
    """大数据集内存占用测试"""
    import tracemalloc
    
    atoms = list(periodic_table['element'].unique())[:50]  # 50 元素
    
    tracemalloc.start()
    result = inorganic_interference(
        atoms, '238U', targetrange=0.5,
        charge=[1, 2, 3], maxsize=4, risk_preset='gdms'
    )
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # 断言：峰值内存 <1GB
    assert peak < 1_000_000_000
```

**运行性能测试**:
```bash
pytest tests/test_performance.py -v --benchmark-only
```

##### C. GDMS 文件格式边缘情况
```python
# tests/test_gdms_edge_cases.py
import pytest
from interference_calculator.gdms_import import parse_gdms_profile_file

def test_empty_excel_file(tmp_path):
    """测试空 Excel 文件"""
    filepath = tmp_path / 'empty.xlsx'
    # 创建空工作簿
    wb = openpyxl.Workbook()
    wb.save(filepath)
    
    with pytest.raises(ValueError, match="No valid profile data found"):
        parse_gdms_profile_file(filepath)

def test_trr_corrupted_run(tmp_path):
    """测试损坏的 TRR Run 数据"""
    # 构造部分损坏的 TRR 文件
    filepath = create_corrupted_trr(tmp_path)
    
    runs = parse_gdms_raw_runs(filepath)
    assert len(runs) == 1  # 应跳过损坏的 Run
    assert runs[0].has_warning  # 标记警告

def test_gdr_legacy_format(tmp_path):
    """测试旧版 GDR 格式兼容性"""
    filepath = create_legacy_gdr(tmp_path)
    
    runs = parse_gdms_raw_runs(filepath)
    assert len(runs) > 0
    assert runs[0].isotopes  # 能正确解析同位素
```

##### D. 集成测试覆盖完整工作流
```python
# tests/test_integration.py
import pytest
from PyQt5.QtWidgets import QApplication
from interference_calculator.ui import MainWindow

@pytest.mark.integration
def test_full_gdms_workflow(qtbot, tmp_path):
    """完整 GDMS 工作流集成测试"""
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    qtbot.addWidget(window)
    
    # 1. 选择 GDMS 模式
    qtbot.mouseClick(window.mode_selector, QtCore.Qt.LeftButton)
    qtbot.keyClick(window.mode_selector, QtCore.Qt.Key_Down)
    qtbot.keyClick(window.mode_selector, QtCore.Qt.Key_Enter)
    
    # 2. 导入测试数据
    test_file = create_test_gdms_excel(tmp_path)
    window.import_button.click()
    qtbot.waitUntil(lambda: window.target_selector.count() > 0, timeout=5000)
    
    # 3. 选择目标峰
    window.target_selector.setCurrentIndex(1)
    
    # 4. 点击计算
    qtbot.mouseClick(window.calculate_button, QtCore.Qt.LeftButton)
    
    # 5. 等待计算完成
    qtbot.waitUntil(lambda: window.results_table.rowCount() > 0, timeout=10000)
    
    # 6. 验证结果
    assert window.results_table.rowCount() > 10
    assert '75As' in window.summary_label.text()
```

**验收标准**:
- [ ] 核心逻辑测试覆盖率 ≥95%
- [ ] UI 测试覆盖率 ≥80%（通过截图对比）
- [ ] 性能基准测试纳入 CI，失败时阻断合并
- [ ] 新增 10+ GDMS 边缘情况测试用例
- [ ] 集成测试覆盖 3 个完整工作流（GDMS/ICP-MS/SIMS）

**实施难度**: ⭐⭐⭐ (中)  
**时间估算**: 2 周

---

#### 3.2 日志和监控系统

**问题描述**:
- 调试困难，用户报告问题时缺乏上下文信息
- 无法追踪性能瓶颈（哪些计算步骤最慢）
- 错误堆栈对用户不友好

**技术方案**:

##### A. 分级日志系统
```python
# logging_config.py
import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO):
    """配置应用日志"""
    
    # 日志目录
    log_dir = Path.home() / '.interference_calculator' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 根日志器
    logger = logging.getLogger('interference_calculator')
    logger.setLevel(log_level)
    
    # 控制台处理器（仅 WARNING 及以上）
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_format = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器（DEBUG 及以上，轮转）
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger

# 使用示例
logger = logging.getLogger('interference_calculator.inorganic')

def inorganic_interference(...):
    logger.info("开始计算: atoms=%s, target=%s, maxsize=%d", 
                atoms, target, maxsize)
    
    start_time = time.time()
    # ... 计算逻辑 ...
    elapsed = time.time() - start_time
    
    logger.info("计算完成: 耗时 %.2fs, 结果数 %d", elapsed, len(results))
    return results
```

##### B. 错误追踪和报告
```python
# error_tracker.py
import traceback
import uuid
from datetime import datetime

class ErrorTracker:
    """错误追踪器：收集错误上下文并生成报告"""
    
    def __init__(self, logger):
        self.logger = logger
        self.error_log = Path.home() / '.interference_calculator' / 'error_reports'
        self.error_log.mkdir(parents=True, exist_ok=True)
    
    def capture_exception(self, exc: Exception, context: dict = None):
        """捕获异常并记录详细信息"""
        error_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # 构建错误报告
        report = {
            'error_id': error_id,
            'timestamp': timestamp,
            'exception_type': type(exc).__name__,
            'exception_message': str(exc),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'qt_version': QtCore.QT_VERSION_STR,
            }
        }
        
        # 保存到文件
        report_file = self.error_log / f'error_{error_id}.json'
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 记录日志
        self.logger.error(
            "错误 [%s]: %s - %s",
            error_id, type(exc).__name__, str(exc),
            exc_info=exc
        )
        
        return error_id

# 在 UI 中使用
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.error_tracker = ErrorTracker(logger)
    
    def calculate(self):
        try:
            results = inorganic_interference(...)
            self.display_results(results)
        except Exception as e:
            error_id = self.error_tracker.capture_exception(e, {
                'action': 'calculate',
                'atoms': self.elements,
                'target': self.target,
            })
            QMessageBox.critical(
                self,
                "计算错误",
                f"计算过程中发生错误。\n\n"
                f"错误 ID: {error_id}\n"
                f"该信息已保存，可在帮助菜单中提交错误报告。"
            )
```

##### C. 性能指标收集
```python
# performance_monitor.py
import time
from collections import defaultdict

class PerformanceMonitor:
    """性能监控器：收集关键操作的耗时"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def measure(self, operation_name):
        """装饰器：测量函数执行时间"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                
                self.metrics[operation_name].append(elapsed)
                
                # 如果超过阈值，记录警告
                if elapsed > self._get_threshold(operation_name):
                    logger.warning(
                        "性能警告: %s 耗时 %.2fs (阈值: %.2fs)",
                        operation_name, elapsed, 
                        self._get_threshold(operation_name)
                    )
                
                return result
            return wrapper
        return decorator
    
    def _get_threshold(self, operation):
        thresholds = {
            'interference_calculation': 5.0,  # 5秒
            'gdms_import': 10.0,              # 10秒
            'spectrum_render': 1.0,           # 1秒
        }
        return thresholds.get(operation, 1.0)
    
    def get_stats(self, operation_name):
        """获取某操作的统计数据"""
        times = self.metrics.get(operation_name, [])
        if not times:
            return None
        
        import statistics
        return {
            'count': len(times),
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'p95': sorted(times)[int(len(times) * 0.95)],
        }

# 使用示例
perf_monitor = PerformanceMonitor()

@perf_monitor.measure('interference_calculation')
def inorganic_interference(...):
    # ... 计算逻辑 ...
    pass
```

**验收标准**:
- [ ] 日志文件按日期轮转，单个文件 ≤5MB
- [ ] 错误报告包含完整的堆栈跟踪和系统信息
- [ ] 性能监控覆盖 5+ 关键操作
- [ ] 用户可通过 Help 菜单提交错误报告（打包为 ZIP）

**实施难度**: ⭐⭐ (低)  
**时间估算**: 1 周

---

### 第四阶段: 文档和用户体验 (P2 - 低优先级)
**时间周期**: 3-4 周  
**影响范围**: 文档、教程、国际化  
**风险等级**: 低

#### 4.1 API 文档完善

**问题描述**:
- 缺少自动生成的 API 参考文档
- 函数签名缺少类型注解
- 示例代码分散在 README 中

**技术方案**:

##### A. Sphinx 文档生成
```bash
# 安装依赖
pip install sphinx sphinx-rtd-theme autodoc

# 初始化文档
sphinx-quickstart docs/api
```

**conf.py 配置**:
```python
# docs/api/conf.py
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # 支持 Google/NumPy 风格文档字符串
    'sphinx.ext.viewcode',
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False
```

**索引文件**:
```rst
# docs/api/index.rst
API 参考文档
============

.. toctree::
   :maxdepth: 2
   
   modules

核心模块
--------

.. automodule:: interference_calculator.inorganic
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: interference_calculator.molecule
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: interference_calculator.main
   :members:
   :undoc-members:
   :show-inheritance:
```

##### B. 类型注解添加
```python
# interference_calculator/inorganic.py
from typing import List, Tuple, Optional, Dict, Union
import pandas as pd

def inorganic_interference(
    atoms: List[str],
    target: str,
    targetrange: float = 0.3,
    charge: Union[int, List[int]] = (1, 2),
    chargesign: str = '+',
    maxsize: int = 3,
    style: str = 'plain',
    risk_preset: str = 'gdms',
    formation_factors: Optional[Dict[str, float]] = None,
    matrix_atoms: Optional[List[str]] = None,
    plasma_atoms: Optional[List[str]] = None,
    background_atoms: Optional[List[str]] = None,
    include_background: bool = True,
) -> pd.DataFrame:
    """Screen common inorganic mass-spectrometry interference candidates.
    
    Args:
        atoms: List of element symbols to consider (e.g., ['Ar', 'Cl', 'As'])
        target: Target peak formula or m/z value (e.g., '75As' or 74.9216)
        targetrange: Half-window width in m/z units (default: 0.3)
        charge: Charge state(s) to consider (default: (1, 2))
        chargesign: Charge sign, one of '+', '-', 'o', '0' (default: '+')
        maxsize: Maximum number of atoms in candidate molecules (default: 3)
        style: Output formula style (default: 'plain')
        risk_preset: Risk model preset, one of 'gdms', 'icp-ms', 'sims'
        formation_factors: Custom formation factors (overrides preset)
        matrix_atoms: Explicit matrix elements (auto-detected if None)
        plasma_atoms: Explicit plasma elements (auto-detected if None)
        background_atoms: Explicit background elements (auto-detected if None)
        include_background: Whether to include background molecules
    
    Returns:
        DataFrame with columns: molecule, type, charge, mz, delta_mz,
        delta_ppm, mrp_required, probability, relative_risk, resolvable
    
    Example:
        >>> from interference_calculator import inorganic_interference
        >>> results = inorganic_interference(
        ...     ['Ar', 'Cl', 'As', 'O', 'H'],
        ...     '75As',
        ...     targetrange=0.074921,
        ...     charge=[1, 2],
        ...     maxsize=3,
        ...     risk_preset='gdms'
        ... )
        >>> print(results.head())
    """
    # ... 实现 ...
```

##### C. 示例代码库
```python
# examples/basic_screening.py
"""基础干扰筛查示例"""
import interference_calculator as ic

# GDMS 模式：筛查 As 目标峰附近的干扰
results = ic.inorganic_interference(
    atoms=['Ar', 'Cl', 'As', 'O', 'H'],
    target='75As',
    charge=[1, 2],
    maxsize=3,
    risk_preset='gdms'
)

# 筛选未分辨的高风险干扰
high_risk = results[
    (results['resolvable'] == False) & 
    (results['relative_risk'] > 1e-6)
]
print(high_risk[['molecule', 'delta_ppm', 'relative_risk']])
```

```python
# examples/gdms_import.py
"""GDMS 数据导入示例"""
from interference_calculator.gdms_import import parse_gdms_profile_file

# 解析 Excel 谱图文件
profiles = parse_gdms_profile_file('sample_profiles.xlsx')

for profile in profiles:
    print(f"元素: {profile.element}, 同位素: {profile.mass_number}")
    print(f"  质心 m/z: {profile.centroid_mass:.4f}")
    print(f"  峰顶 m/z: {profile.apex_mass:.4f}")
    print(f"  FWHM: {profile.fwhm:.4f}")
```

**验收标准**:
- [ ] Sphinx 自动生成 HTML API 文档
- [ ] 所有公共函数有类型注解和完整文档字符串
- [ ] 提供 5+ 示例脚本覆盖常见用例
- [ ] 文档部署到 GitHub Pages

**实施难度**: ⭐⭐ (低)  
**时间估算**: 1-2 周

---

#### 4.2 用户指南增强

**问题描述**:
- USER_MANUAL.md 较简略，缺少视频教程
- 新用户学习曲线陡峭
- 常见问题分散在 Issue 中

**技术方案**:

##### A. 视频教程录制
- **视频 1**: 快速入门（5 分钟）- GDMS 基本工作流
- **视频 2**: 高级功能（10 分钟）- 谱图分析、预设管理
- **视频 3**: 故障排除（5 分钟）- 常见问题解答

**嵌入方式**:
```markdown
## 视频教程

### 快速入门：GDMS 干扰筛查

[![快速入门视频](docs/images/video_thumbnail_1.png)](https://www.bilibili.com/video/BV1xxx)

> 时长：5 分钟 | 适合：首次使用者
```

##### B. Jupyter Notebook 交互式教程
```python
# tutorials/01_basics.ipynb
{
 "cells": [
  {
   "cell_type": "markdown",
   "source": [
    "# 无机质谱干扰计算器 - 交互式教程\n",
    "\n",
    "本教程通过实际代码演示如何使用干扰计算器。"
   ]
  },
  {
   "cell_type": "code",
   "source": [
    "import interference_calculator as ic\n",
    "\n",
    "# 第一次计算：简单的 As 目标峰筛查\n",
    "results = ic.inorganic_interference(\n",
    "    atoms=['Ar', 'Cl', 'As', 'O', 'H'],\n",
    "    target='75As',\n",
    "    maxsize=3,\n",
    "    risk_preset='gdms'\n",
    ")\n",
    "\n",
    "print(f\"找到 {len(results)} 个候选峰\")\n",
    "results.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "source": [
    "## 练习\n",
    "\n",
    "尝试修改 `atoms` 列表，添加更多元素，观察候选峰数量变化。"
   ]
  }
 ]
}
```

##### C. FAQ 知识库
```markdown
# 常见问题解答 (FAQ)

## 计算相关

### Q: 为什么 maxsize=4 时计算很慢？
A: 当 maxsize 增加时，组合数呈指数增长。建议：
   - 优先使用 maxsize=3，覆盖 90% 常见干扰
   - 如需 maxsize=4，确保元素列表精简（<20 个元素）
   - 考虑启用并行计算（未来版本支持）

### Q: "相对风险"值如何解读？
A: 相对风险是定性排序分数，计算公式为：
   ```
   相对风险 = 同位素概率 × 形成因子
   ```
   - >1e-4: 高风险，优先关注
   - 1e-6 ~ 1e-4: 中等风险
   - <1e-6: 低风险，通常可忽略
   
   注意：这不是定量校正因子，需结合标准样品校准。

## 数据导入

### Q: 支持哪些 GDMS 文件格式？
A: 目前支持：
   - Excel (.xlsx): GDMS 软件导出的谱图文件
   - TRR (.trr): GD90Trace 原始文件（实验性）
   - GDR (.gdr): Elsima 旧版原始文件（实验性）

### Q: 导入后如何选择目标峰？
A: 导入后，目标峰下拉框会显示文件中所有同位素谱图。
   优先从这里选择，而不是手动输入。下拉框显示天然丰度，
   下方详情显示理论 m/z 和实测 m/z。

## 谱图视图

### Q: "实测峰（测试）"是什么？
A: 这是实验性功能，会在谱图中叠加导入的真实峰形数据。
   默认关闭，因为可能影响性能。开启后可直观对比理论
   候选峰和实测峰位置。

### Q: "匹配 m/z"按钮的作用？
A: 该功能将每条实测峰的质心对齐到对应同位素的理论 m/z，
   并用参考线显示偏移量。仅用于目视检查，不改变计算结果。
```

##### D. 典型用例场景库
```markdown
# 典型用例场景

## 场景 1: GDMS 高纯金属杂质筛查

**背景**: 分析 99.999% 纯铜中的痕量砷（As）

**配置**:
```
模式: GDMS
目标: 75As
窗口: 2000 ppm
元素: Ar Cl As O H C N Fe Cu
离子: 1+, 2+
最大原子数: 3
MRP: 4000
```

**关注点**:
- ArCl+ 对 75As+ 的干扰（Δppm ≈ 0）
- Cu 基体相关的氧化物和团簇

---

## 场景 2: ICP-MS 稀土元素分析

**背景**: 地质样品中稀土元素（REE）测定

**配置**:
```
模式: ICP-MS
目标: 139La
窗口: 400 ppm
元素: La Ce Pr Nd Sm Ba O H C Ar
离子: 1+
最大原子数: 3
MRP: 10000
```

**关注点**:
- BaO+ 对稀土元素的干扰
- 双电荷离子（Ba++、Ce++）

---

## 场景 3: SIMS 表面深度剖析

**背景**: 半导体薄膜中硼（B）掺杂分布

**配置**:
```
模式: SIMS
目标: 11B
窗口: 200 ppm
元素: B Si O C H Ar
离子: 1+
最大原子数: 2
MRP: 5000
```

**关注点**:
- SiC+、BO+ 等轻元素干扰
- 高质量分辨率需求
```

**验收标准**:
- [ ] 用户手册扩充至 5000+ 字，包含 10+ 截图
- [ ] 录制 3 个视频教程并嵌入文档
- [ ] 提供 2 个 Jupyter Notebook 交互式教程
- [ ] FAQ 覆盖 20+ 常见问题
- [ ] 典型用例场景库包含 5+ 行业案例

**实施难度**: ⭐⭐ (低)  
**时间估算**: 2 周

---

#### 4.3 国际化扩展

**现状**: 中英文双语，但部分文本硬编码

**技术方案**:

##### A. i18n 资源文件提取
```python
# i18n/translations.py
TRANSLATIONS = {
    'zh-CN': {
        'app_title': '无机质谱峰干扰计算器',
        'menu_file': '文件(&F)',
        'menu_help': '帮助(&H)',
        'btn_calculate': '计算',
        'lbl_mode': '流程 / 模式:',
        'lbl_target': '目标峰:',
        'lbl_elements': '样品 / 等离子体 / 元素:',
        'lbl_window': '窗口宽度:',
        'lbl_mrp': '仪器 MRP:',
        'col_molecule': '离子',
        'col_type': '类型',
        'col_mz': 'm/z',
        'col_delta_ppm': 'Δppm',
        'col_resolvable': '可分辨',
        'msg_calc_complete': '计算完成，找到 {} 个候选峰',
        'msg_no_results': '未找到候选峰，请检查参数设置',
        # ... 更多翻译
    },
    'en-US': {
        'app_title': 'Inorganic MS Interference Calculator',
        'menu_file': '&File',
        'menu_help': '&Help',
        'btn_calculate': 'Calculate',
        'lbl_mode': 'Workflow / Mode:',
        'lbl_target': 'Target Peak:',
        'lbl_elements': 'Sample / Plasma / Elements:',
        'lbl_window': 'Window Width:',
        'lbl_mrp': 'Instrument MRP:',
        'col_molecule': 'Ion',
        'col_type': 'Type',
        'col_mz': 'm/z',
        'col_delta_ppm': 'Δppm',
        'col_resolvable': 'Resolvable',
        'msg_calc_complete': 'Calculation complete, {} candidates found',
        'msg_no_results': 'No candidates found, please check parameters',
    },
    'ja-JP': {
        'app_title': '無機質量分析干渉計算機',
        'menu_file': 'ファイル(&F)',
        'menu_help': 'ヘルプ(&H)',
        'btn_calculate': '計算',
        # ... 日语翻译（预留扩展点）
    },
    'de-DE': {
        'app_title': 'Anorganischer MS-Interferenzrechner',
        'menu_file': '&Datei',
        'menu_help': '&Hilfe',
        'btn_calculate': 'Berechnen',
        # ... 德语翻译（预留扩展点）
    },
}

class Translator:
    """翻译器：支持运行时语言切换"""
    
    def __init__(self, language='zh-CN'):
        self._language = language
        self._translations = TRANSLATIONS.get(language, TRANSLATIONS['zh-CN'])
    
    def tr(self, key, default=None):
        """翻译文本"""
        return self._translations.get(key, default or key)
    
    def set_language(self, language):
        """切换语言"""
        if language in TRANSLATIONS:
            self._language = language
            self._translations = TRANSLATIONS[language]
            return True
        return False
    
    def available_languages(self):
        """返回可用语言列表"""
        return list(TRANSLATIONS.keys())
```

##### B. 动态语言切换
```python
# ui/mixins/localization.py
class LocalizationMixin:
    """提供运行时语言切换能力"""
    
    def __init__(self):
        self.translator = Translator('zh-CN')
    
    def switch_language(self, language):
        """切换语言并刷新所有界面文本"""
        if self.translator.set_language(language):
            self.refresh_all_labels()
            self.retranslate_ui()
    
    def refresh_all_labels(self):
        """刷新所有标签文本"""
        self.setWindowTitle(self.tr('app_title'))
        self.file_menu.setTitle(self.tr('menu_file'))
        self.help_menu.setTitle(self.tr('menu_help'))
        self.calculate_button.setText(self.tr('btn_calculate'))
        # ... 刷新所有控件
    
    def retranslate_ui(self):
        """重新翻译整个 UI（递归遍历子控件）"""
        for widget in self.findChildren(QtWidgets.QWidget):
            if hasattr(widget, 'setText'):
                # 尝试从对象属性获取翻译键
                key = getattr(widget, '_translation_key', None)
                if key:
                    widget.setText(self.tr(key))
```

**验收标准**:
- [ ] 所有硬编码文本提取到 i18n 资源文件
- [ ] 支持运行时语言切换无需重启应用
- [ ] 预留日语、德语扩展点（至少 50% 翻译完成）
- [ ] 提供翻译贡献指南（如何添加新语言）

**实施难度**: ⭐⭐ (低)  
**时间估算**: 1 周

---

### 第五阶段: 现代化升级 (P2 - 低优先级)
**时间周期**: 2 周  
**影响范围**: 依赖管理、CI/CD  
**风险等级**: 低

#### 5.1 依赖管理现代化

**问题描述**:
- `setup.py` 硬编码依赖，缺乏版本约束
- 不支持 Poetry/Pipenv 等现代化工具
- PyQt6 作为潜在后端未考虑

**技术方案**:

##### A. 迁移到 Poetry
```toml
# pyproject.toml (Poetry 格式)
[tool.poetry]
name = "interference-calculator"
version = "2.6.0"
description = "Inorganic MS Interference Calculator"
authors = ["Tingfe <me@example.com>"]
license = "BSD-3-Clause-Clear"
readme = "README.rst"
homepage = "https://github.com/Tingfe/interference_calculator"
repository = "https://github.com/Tingfe/interference_calculator"
keywords = ["mass-spectrometry", "interference", "gdms", "icp-ms"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[tool.poetry.dependencies]
python = "^3.9"
numpy = "^1.21.0"
pandas = "^1.3.0"
openpyxl = "^3.0.0"
pyparsing = "^3.0.0"
PyQt5 = "^5.15.0"

# 可选依赖
requests = { version = "^2.28.0", optional = true }
cupy-cuda11x = { version = "^11.0.0", optional = true }  # GPU 加速

[tool.poetry.extras]
data = ["requests"]
gpu = ["cupy-cuda11x"]

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-qt = "^4.2.0"
pytest-benchmark = "^4.0.0"
sphinx = "^5.0.0"
black = "^22.0.0"
flake8 = "^5.0.0"
mypy = "^0.990"

[tool.poetry.scripts]
interference-calculator = "interference_calculator.ui:run"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

**迁移步骤**:
```bash
# 1. 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. 初始化 Poetry（保留现有 setup.py 作为过渡）
poetry init

# 3. 添加依赖
poetry add numpy pandas openpyxl pyparsing PyQt5
poetry add --group dev pytest pytest-qt sphinx black flake8 mypy

# 4. 生成 lock 文件
poetry lock

# 5. 测试安装
poetry install

# 6. 运行测试
poetry run pytest tests/ -v
```

##### B. PyQt6 兼容性层
```python
# compatibility/qt_backend.py
"""Qt 后端兼容性层：支持 PyQt5 和 PyQt6"""

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    QT_VERSION = 6
    IS_PYQT6 = True
except ImportError:
    try:
        from PyQt5 import QtCore, QtGui
        from PyQt5 import QtWidgets
        QT_VERSION = 5
        IS_PYQT6 = False
    except ImportError:
        raise ImportError("Requires either PyQt5 or PyQt6")

# 统一 API
if IS_PYQT6:
    # PyQt6 调整
    QtWidgets.QStyleOptionViewItem = QtWidgets.QStyleOptionViewItem
else:
    # PyQt5 兼容
    if hasattr(QtWidgets, 'QStyleOptionViewItemV4'):
        QtWidgets.QStyleOptionViewItem = QtWidgets.QStyleOptionViewItemV4
```

**验收标准**:
- [ ] Poetry 管理依赖，生成 poetry.lock
- [ ] 支持 `pip install` 和 `poetry install` 两种方式
- [ ] 明确最小版本要求（如 numpy>=1.21.0）
- [ ] PyQt6 作为可选后端（实验性支持）

**实施难度**: ⭐⭐ (低)  
**时间估算**: 1 周

---

#### 5.2 CI/CD 流程优化

**技术方案**:

##### A. 自动化代码质量检查
```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install flake8 black mypy
      
      - name: Run flake8
        run: flake8 interference_calculator/ --max-line-length=100
      
      - name: Check code formatting
        run: black --check interference_calculator/
      
      - name: Type checking
        run: mypy interference_calculator/ --ignore-missing-imports
```

##### B. 性能基准测试自动化
```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-benchmark
      
      - name: Run benchmarks
        run: pytest tests/test_performance.py --benchmark-only --benchmark-json=benchmark.json
      
      - name: Compare with baseline
        uses: benchmark-action/github-action-benchmark@v1
        with:
          name: Interference Calculator Benchmarks
          tool: 'pytest'
          output-file-path: benchmark.json
          fail-on-regression: true
          regression-threshold: 20  # 允许 20% 性能退化
```

##### C. 多 Python 版本兼容性测试
```yaml
# .github/workflows/test-multi-python.yml
name: Multi-Python Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-qt
      
      - name: Run tests
        run: pytest tests/ -v --tb=short
```

##### D. 自动化安全扫描
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 1'  # 每周一运行
  push:
    paths:
      - '**/requirements*.txt'
      - '**/setup.py'
      - '**/pyproject.toml'

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Dependency check
        run: |
          pip install safety
          safety check --json --output safety-report.json
      
      - name: Upload safety report
        uses: actions/upload-artifact@v3
        with:
          name: safety-report
          path: safety-report.json
```

**验收标准**:
- [ ] CI 流程包含代码质量检查（flake8/black/mypy）
- [ ] 性能基准测试自动运行，回归 >20% 时阻断合并
- [ ] 支持 Python 3.9-3.12 四版本测试
- [ ] 每周自动安全扫描，发现漏洞时创建 Issue

**实施难度**: ⭐⭐ (低)  
**时间估算**: 1 周

---

## 优先级矩阵

| 优化项 | 影响力 | 实施难度 | 优先级 | 预计时间 |
|--------|--------|----------|--------|----------|
| **1.1 计算引擎性能提升** | 🔴 高 | 🟡 中 | P0 | 2 周 |
| **1.2 内存优化** | 🔴 高 | 🟢 低 | P0 | 1 周 |
| **2.1 UI 代码模块化** | 🟡 中 | 🔴 高 | P1 | 3-4 周 |
| **2.2 配置持久化** | 🟡 中 | 🟢 低 | P1 | 1 周 |
| **2.3 插件系统** | 🟡 中 | 🟡 中 | P1 | 2-3 周 |
| **3.1 测试覆盖率提升** | 🟡 中 | 🟡 中 | P1 | 2 周 |
| **3.2 日志和监控** | 🟢 低 | 🟢 低 | P1 | 1 周 |
| **4.1 API 文档完善** | 🟢 低 | 🟢 低 | P2 | 1-2 周 |
| **4.2 用户指南增强** | 🟢 低 | 🟢 低 | P2 | 2 周 |
| **4.3 国际化扩展** | 🟢 低 | 🟢 低 | P2 | 1 周 |
| **5.1 依赖管理现代化** | 🟢 低 | 🟢 低 | P2 | 1 周 |
| **5.2 CI/CD 优化** | 🟢 低 | 🟢 低 | P2 | 1 周 |

**图例**:
- 🔴 高影响力：直接影响用户体验或核心功能
- 🟡 中影响力：改善可维护性或扩展性
- 🟢 低影响力：长期价值，短期收益不明显

---

## 风险评估

### 高风险项

#### 1. UI 代码重构可能导致回归错误
**风险描述**: 拆分 5000 行 monolithic 文件时，可能遗漏某些交互逻辑或信号连接

**缓解策略**:
- 采用渐进式重构：先提取独立组件，再整合
- 每个组件提取后立即运行回归测试
- 保留 `ui_legacy.py` 作为 fallback，新旧实现并行运行 1-2 个版本
- 邀请 3-5 名 beta 用户提前测试重构后的版本

**应急预案**:
- 如发现严重 bug，回滚到重构前版本
- 建立专门的 `refactor/ui-modularization` 分支，合入 main 前充分测试

---

#### 2. 并行计算引入线程安全问题
**风险描述**: `multiprocessing` 可能导致数据竞争或死锁

**缓解策略**:
- 使用不可变数据结构传递任务参数
- 避免共享状态，每个进程独立计算
- 添加超时机制（如单任务 >60s 自动终止）
- 在小数据集上充分测试并行逻辑

**应急预案**:
- 提供 `--no-parallel` 命令行开关禁用并行
- 检测 CPU 核心数 <2 时自动回退到串行

---

#### 3. 插件系统增加复杂度
**风险描述**: 过度设计导致核心代码臃肿，新用户学习成本上升

**缓解策略**:
- 插件系统作为可选特性，默认不加载
- 提供清晰的插件开发文档和示例
- 核心功能不依赖插件，保证开箱即用
- 定期审查内置插件，移除使用率低的

**应急预案**:
- 如社区反馈复杂度高，简化插件接口
- 考虑改为配置文件驱动而非代码插件

---

### 中风险项

#### 4. GPU 加速依赖 CuPy，增加安装难度
**缓解策略**:
- 作为可选 extras (`pip install interference-calculator[gpu]`)
- 自动检测 GPU 可用性，不可用时优雅降级
- 提供详细的 GPU 安装指南

#### 5. 国际化扩展可能遗漏部分文本
**缓解策略**:
- 使用自动化脚本扫描硬编码字符串
- 建立翻译审核流程（至少两人 review）
- 提供"报告翻译错误"入口

---

### 低风险项

#### 6. Poetry 迁移破坏现有 pip 用户
**缓解策略**:
- 同时保留 `setup.py` 和 `pyproject.toml`
- 在 README 中明确两种安装方式
- 监控 PyPI 下载统计，确认无负面影响

#### 7. Sphinx 文档维护负担
**缓解策略**:
- 将文档生成纳入 CI，自动部署到 GitHub Pages
- 鼓励社区贡献文档改进（类似代码 PR）

---

## 资源需求

### 人力资源

| 角色 | 人数 | 职责 | 投入时间 |
|------|------|------|----------|
| **核心开发者** | 1-2 | 负责性能优化、架构重构 | 全职 3-4 个月 |
| **UI/UX 设计师** | 1 (兼职) | 协助界面重构、视频教程制作 | 20% 投入，2 个月 |
| **技术文档撰写** | 1 (兼职) | API 文档、用户指南、FAQ | 30% 投入，1.5 个月 |
| **测试工程师** | 1 (兼职) | 编写测试用例、性能基准 | 20% 投入，2 个月 |
| **社区贡献者** | 若干 | 翻译、插件开发、bug 报告 | 自愿参与 |

**总计**: 核心团队 1-2 人全职 3-4 个月，辅以兼职支持

---

### 技术栈

#### 新增依赖
```txt
# 性能优化
multiprocessing  # Python 标准库
cupy-cuda11x>=11.0.0  # 可选，GPU 加速

# 测试增强
pytest-qt>=4.2.0
pytest-benchmark>=4.0.0
Pillow>=9.0.0
ImageHash>=4.3.0
memory-profiler>=0.60.0

# 文档生成
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0

# 插件系统
PyYAML>=6.0
watchdog>=2.0.0  # 热加载

# 依赖管理（可选）
poetry>=1.3.0

# 日志
# Python 标准库 logging，无需额外依赖
```

#### 开发工具
- **代码质量**: flake8, black, mypy
- **性能分析**: cProfile, memory_profiler, py-spy
- **CI/CD**: GitHub Actions
- **文档托管**: GitHub Pages
- **视频录制**: OBS Studio, Camtasia（可选）

---

### 硬件需求

| 用途 | 配置要求 | 数量 |
|------|----------|------|
| **开发机器** | 8 核 CPU, 16GB RAM, SSD | 2 台 |
| **性能测试** | 16 核 CPU, 32GB RAM | 1 台（云服务器） |
| **GPU 测试** | NVIDIA RTX 3060+, CUDA 11+ | 1 台（可选） |
| **多平台测试** | Windows/macOS/Linux 各 1 台 | 3 台（或使用 VM） |

**预估成本**: 
- 云服务器（性能测试）: $50-100/月
- GPU 机器（可选）: $1000-1500（一次性）
- 其他利用现有设备

---

## 成功指标 (KPI)

### 性能指标

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|--------|--------|----------|
| **maxsize=3 计算时间** (50 元素) | ~2s | <0.5s | pytest-benchmark |
| **maxsize=4 计算时间** (50 元素) | ~30s | <3s | pytest-benchmark |
| **峰值内存占用** (maxsize=5, 50 元素) | ~2GB | <500MB | memory_profiler |
| **应用启动时间** | ~3s | <1.5s | 手动计时 |
| **谱图渲染帧率** | ~30fps | >60fps | Qt 性能监控 |

---

### 代码质量指标

| 指标 | 当前值 | 目标值 | 测量工具 |
|------|--------|--------|----------|
| **核心逻辑测试覆盖率** | >90% | ≥95% | pytest-cov |
| **UI 测试覆盖率** | ~50% | ≥80% | pytest-qt + 截图对比 |
| **单文件最大行数** | ~5000 (ui.py) | <1000 | wc -l |
| **圈复杂度平均值** | ~15 | <10 | mccabe |
| **类型注解覆盖率** | ~30% | ≥80% | mypy --strict |

---

### 用户体验指标

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|--------|--------|----------|
| **用户满意度评分** | N/A | ≥4.5/5 | GitHub Discussion 投票 |
| **平均问题解决时间** | ~2 天 | <1 天 | Issue 跟踪统计 |
| **文档阅读量** | N/A | >1000 次/月 | GitHub Pages 统计 |
| **新手上手时间** | ~30 分钟 | <10 分钟 | 用户调研 |
| **国际化支持语言数** | 2 | ≥4 | 代码统计 |

---

### 社区参与度指标

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|--------|--------|----------|
| **GitHub Stars** | 当前值 | +50% | GitHub API |
| **月度活跃贡献者** | ~2 | ≥5 | GitHub Insights |
| **Issue 响应时间** | ~1 天 | <12 小时 | Issue 跟踪统计 |
| **插件生态** | 0 | ≥5 个社区插件 | 插件目录统计 |
| **StackOverflow 问题数** | 0 | ≥10 | StackOverflow 搜索 |

---

## 里程碑时间表

### Gantt 图示意

```
阶段                     | W1  W2  W3  W4  W5  W6  W7  W8  W9  W10 W11 W12 W13 W14 W15 W16
-------------------------|-----------------------------------------------------------------
第一阶段: 性能优化        |███████████
  1.1 计算引擎           |████████
  1.2 内存优化           |    ████
                         |
第二阶段: 架构重构        |            ████████████████████
  2.1 UI 模块化          |            ██████████████
  2.2 配置持久化         |                      ████
  2.3 插件系统           |                          ██████████
                         |
第三阶段: 质量保证        |                                    ██████████
  3.1 测试覆盖率         |                                    ████████
  3.2 日志监控           |                                            ████
                         |
第四阶段: 文档与 UX       |                                            ██████████████
  4.1 API 文档           |                                            ██████
  4.2 用户指南           |                                                ████████
  4.3 国际化             |                                                        ████
                         |
第五阶段: 现代化升级      |                                                        ████████
  5.1 依赖管理           |                                                        ████
  5.2 CI/CD 优化         |                                                            ████
                         |
里程碑                   |    M1          M2              M3          M4          M5
```

**里程碑定义**:
- **M1 (Week 2)**: 第一阶段完成，发布 v2.6.0-alpha（性能优化预览版）
- **M2 (Week 6)**: 第二阶段完成，发布 v2.6.0-beta（架构重构预览版）
- **M3 (Week 8)**: 第三阶段完成，发布 v2.6.0-rc1（候选发布版 1）
- **M4 (Week 12)**: 第四阶段完成，发布 v2.6.0-rc2（候选发布版 2）
- **M5 (Week 14)**: 第五阶段完成，发布 v2.6.0 正式版

---

### 详细时间线

#### Month 1: 性能突破 (Weeks 1-4)

**Week 1-2**: 计算引擎优化
- Day 1-3: 实现预过滤剪枝算法
- Day 4-7: 集成并行计算框架
- Day 8-10: GPU 加速原型（可选）
- Day 11-14: 性能测试与调优

**Week 3**: 内存优化
- Day 15-17: 生成器模式改造
- Day 18-19: 流式数据处理实现
- Day 20-21: 数据类型优化与验证

**Week 4**: 稳定性测试与 alpha 发布
- Day 22-24: 回归测试、边界条件验证
- Day 25-26: 编写性能优化技术文档
- Day 27-28: 发布 v2.6.0-alpha，收集社区反馈

**交付物**:
- ✅ 计算速度提升 10-100 倍
- ✅ 内存占用降低 50-70%
- ✅ 向后兼容的 API
- ✅ 性能基准测试套件

---

#### Month 2: 架构重塑 (Weeks 5-8)

**Week 5-7**: UI 模块化重构
- Week 5: 提取 ControlPanel 组件
- Week 6: 提取 ResultsView 和 SpectrumWidget
- Week 7: 实现 MVVM 模式，迁移状态管理

**Week 8**: 配置持久化与插件系统
- Day 29-31: 实现 ConfigManager
- Day 32-35: 设计插件接口
- Day 36-38: 实现插件加载器
- Day 39-40: 编写插件示例和文档

**Week 9-10**: 集成测试与 beta 发布
- Week 9: 全面回归测试、修复 bug
- Week 10: 发布 v2.6.0-beta，邀请 beta 用户测试

**交付物**:
- ✅ UI 代码拆分为 ≤10 个文件
- ✅ 配置自动保存/恢复
- ✅ 插件系统支持自定义扩展
- ✅ 完整的回归测试报告

---

#### Month 3: 质量加固 (Weeks 9-12)

**Week 11-12**: 测试覆盖率提升
- Week 11: 截图对比测试、性能回归测试
- Week 12: GDMS 边缘情况测试、集成测试

**Week 13**: 日志和监控系统
- Day 43-45: 实现分级日志系统
- Day 46-47: 错误追踪器实现
- Day 48-49: 性能监控器集成

**Week 14**: RC1 发布
- Day 50-52: 最终回归测试
- Day 53-54: 修复 P0/P1 级别 bug
- Day 55-56: 发布 v2.6.0-rc1

**交付物**:
- ✅ 核心逻辑测试覆盖率 ≥95%
- ✅ UI 测试覆盖率 ≥80%
- ✅ 完善的日志和错误报告机制
- ✅ 性能监控 dashboard

---

#### Month 4: 文档完善与国际化 (Weeks 13-16)

**Week 15-16**: API 文档与用户指南
- Week 15: Sphinx 文档生成、类型注解添加
- Week 16: 视频教程录制、Jupyter Notebook 教程

**Week 17**: 国际化扩展
- Day 57-59: 提取 i18n 资源文件
- Day 60-61: 实现动态语言切换
- Day 62-63: 日语/德语翻译（社区协作）

**Week 18**: RC2 发布与最终测试
- Day 64-66: 文档审核、修正错误
- Day 67-68: 多语言界面测试
- Day 69-70: 发布 v2.6.0-rc2

**交付物**:
- ✅ 完整的 API 参考文档
- ✅ 5000+ 字用户手册 + 3 个视频教程
- ✅ 支持 4 种语言（中/英/日/德）
- ✅ 2 个 Jupyter Notebook 交互式教程

---

#### Month 5: 现代化收尾 (Weeks 17-18)

**Week 19**: 依赖管理现代化
- Day 71-73: 迁移到 Poetry
- Day 74-75: PyQt6 兼容性层实现

**Week 20**: CI/CD 优化与正式发布
- Day 76-78: 配置自动化代码质量检查
- Day 79-80: 性能基准测试自动化
- Day 81-82: 多 Python 版本测试配置
- Day 83-84: 安全扫描集成
- Day 85-86: 最终审查、发布 v2.6.0

**交付物**:
- ✅ Poetry 管理的依赖（poetry.lock）
- ✅ 支持 Python 3.9-3.12
- ✅ 自动化 CI/CD 流程
- ✅ 每周安全扫描

---

## 验收标准总览

### 第一阶段验收标准 (P0)
- [ ] maxsize=4, 50 元素场景：计算时间从 ~30s 降至 <3s
- [ ] maxsize=3, 50 元素场景：计算时间从 ~2s 降至 <0.5s
- [ ] 峰值内存占用降低 ≥50%（memory_profiler 验证）
- [ ] API 签名保持不变，所有现有测试通过
- [ ] 并行计算在 4 核/8 核 CPU 上分别提升 3-4 倍/6-8 倍

### 第二阶段验收标准 (P1)
- [ ] `ui.py` 拆分为 ≤10 个文件，单文件 <1000 行
- [ ] 用户偏好（语言、模式、元素）重启后自动恢复
- [ ] 支持导出/导入预设文件（.json 格式）
- [ ] 插件放置在 `~/.interference_calculator/plugins/` 即可自动加载
- [ ] 新增物种模板无需修改核心代码

### 第三阶段验收标准 (P1)
- [ ] 核心逻辑测试覆盖率 ≥95%
- [ ] UI 测试覆盖率 ≥80%（截图对比）
- [ ] 性能基准测试纳入 CI，失败时阻断合并
- [ ] 新增 10+ GDMS 边缘情况测试用例
- [ ] 日志文件按日期轮转，单个文件 ≤5MB

### 第四阶段验收标准 (P2)
- [ ] Sphinx 自动生成 HTML API 文档
- [ ] 所有公共函数有类型注解和完整文档字符串
- [ ] 用户手册扩充至 5000+ 字，包含 10+ 截图
- [ ] 录制 3 个视频教程并嵌入文档
- [ ] 支持运行时语言切换无需重启应用
- [ ] 预留日语、德语扩展点（至少 50% 翻译完成）

### 第五阶段验收标准 (P2)
- [ ] Poetry 管理依赖，生成 poetry.lock
- [ ] 支持 `pip install` 和 `poetry install` 两种方式
- [ ] CI 流程包含代码质量检查（flake8/black/mypy）
- [ ] 性能基准测试自动运行，回归 >20% 时阻断合并
- [ ] 支持 Python 3.9-3.12 四版本测试
- [ ] 每周自动安全扫描

---

## 后续迭代规划 (v2.7+)

### 短期规划 (v2.7 - v2.9)

**v2.7: 社区驱动功能**
- 基于插件系统的社区贡献模板
- 用户反馈驱动的 UX 微调
- 更多仪器预设（Agilent, Bruker, PerkinElmer 等）

**v2.8: 高级分析功能**
- 干扰校正建议（基于相对风险排序）
- 批量处理支持（一次分析多个目标峰）
- 结果导出为 Excel/PDF 报告

**v2.9: 云端协作（实验性）**
- 预设共享平台
- 匿名使用统计（opt-in）
- 在线更新同位素数据库

### 中长期愿景 (v3.0+)

**v3.0: 跨平台桌面应用重构**
- 评估 Electron + Python 后端架构
- 更现代化的 UI 设计系统
- 内置数据可视化工具箱

**v3.5: AI 辅助分析**
- 基于历史数据的干扰预测模型
- 智能参数推荐（根据样品类型自动选择元素集）
- 异常检测结果解释

**v4.0: 生态系统建设**
- 官方插件市场
- 开发者 SDK
- 企业级支持计划

---

## 结语

本优化路线图旨在将无机质谱干扰计算器从"可用的科学工具"提升为"专业级质谱分析平台"。通过五个阶段的系统性改进，我们预期实现：

1. **性能飞跃**: 计算速度提升 10-100 倍，内存占用降低 50-70%
2. **可维护性**: 代码结构清晰，单文件 <1000 行，测试覆盖率 >90%
3. **用户体验**: 配置持久化、预设管理、多语言支持、丰富文档
4. **可扩展性**: 插件系统支持社区贡献，降低新功能开发门槛
5. **质量保证**: 自动化测试、性能监控、安全扫描纳入 CI/CD

我们相信，通过这些优化，项目将更好地服务于全球质谱分析科研人员，成为 GDMS/ICP-MS/SIMS 工作流程中不可或缺的工具。

**下一步行动**:
1. 核心团队审阅本路线图，确认优先级和时间表
2. 创建 GitHub Project Board，跟踪每个优化项的进度
3. 启动第一阶段工作（性能优化），预计 2 周内完成
4. 定期（每两周）同步进展，调整计划应对意外情况

---

**文档版本**: 1.0  
**最后更新**: 2026-06-08  
**作者**: AI Assistant (基于深度分析报告)  
**审核者**: 待核心团队确认  
**状态**: 草案（待讨论和完善）发布版 1）
- **M4 (Week 12)**: 第四阶段完成，发布 v2.6.0-rc2（候选