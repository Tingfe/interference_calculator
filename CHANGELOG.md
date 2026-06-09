# Changelog / 更新日志

本更新日志面向最终用户，重点说明使用体验、功能能力、稳定性和发布渠道变化。
内部实现细节、CI 机制和测试项保留在提交历史与发布文档中。

This changelog focuses on product changes that matter to users. Internal
implementation details, CI mechanics, and test-only changes are kept in commit
history and release documentation.

## [2.6.1] - 2026-06-09

### 中文

#### Bug 修复

##### 无机干扰计算模板扩展 (maxsize > 3)
- **问题**: `inorganic_interference` 函数即使设置 `maxsize=6`，也只生成 ≤3 原子的分子
- **根因**: 模板驱动方法硬编码了 maxsize=3 的限制
- **修复**: 添加 4-5 原子模板支持
  - 三氧化物 (MO₃⁺)、三氢化物 (MH₃⁺)
  - 混合加合物 (MO₂H⁺, MOH₂⁺)
  - 四氧化物 (MO₄⁺) 及更大混合团簇
- **影响**: 现在 `maxsize` 参数真正生效，支持深度分析

##### 分子离子多电荷支持
- **问题**: 只有原子离子支持多电荷，所有分子模板固定为单电荷
- **根因**: `molecular_charge` 变量被硬编码为 1 或 `charges[0]`
- **修复**: 所有分子模板现在遍历用户指定的所有电荷状态
- **影响**: 设置 `charge=[1, 2]` 时，会生成 MO⁺ 和 MO²⁺ 等双电荷分子

#### 文档改进

##### 形成因子理论依据完善
- **文献调研**: 深度调研 12+ 篇关键文献 (JJF 1159-2006 国标、ACS 论文等)
- **置信度标注**: 所有形成因子添加 ★★★★★ 到 ★☆☆☆☆ 置信度评级
  - ★★★★★ ICP-MS 氧化物/双电荷: 基于国际标准，不确定度 <20%
  - ★★★☆☆ GDMS/SIMS: 从 ICP-MS 外推，不确定度 50-100%
  - ★☆☆☆☆ maxsize ≥ 4: 纯理论推测，无实验验证
- **参数调整**: 基于文献证据优化 GDMS 参数
  - 双电荷: 1.0e-2 → 5.0e-3 (辉光放电能量分布更温和)
  - 等离子体加合物: 1.0e-4 → 5.0e-5 (低气压碰撞频率低)
- **用户校准**: 添加详细的用户校准流程文档和示例代码
- **透明度**: 明确标注哪些值有文献支撑，哪些是经验估计

### English

#### Bug Fixes

##### Inorganic Interference Template Extension (maxsize > 3)
- **Issue**: `inorganic_interference` only generated molecules with ≤3 atoms even when `maxsize=6` was set
- **Root Cause**: Template-driven approach had hardcoded maxsize=3 limit
- **Fix**: Added support for 4-5 atom templates
  - Trioxides (MO₃⁺), trihydrides (MH₃⁺)
  - Mixed adducts (MO₂H⁺, MOH₂⁺)
  - Tetraoxides (MO₄⁺) and larger mixed clusters
- **Impact**: `maxsize` parameter now works correctly for deep analysis

##### Multi-Charge Support for Molecular Ions
- **Issue**: Only atomic ions supported multiple charges; all molecular templates were fixed at single charge
- **Root Cause**: `molecular_charge` variable was hardcoded to 1 or `charges[0]`
- **Fix**: All molecular templates now iterate over all user-specified charge states
- **Impact**: Setting `charge=[1, 2]` generates both MO⁺ and MO²⁺ doubly charged molecules

#### Documentation Improvements

##### Formation Factor Theoretical Foundation
- **Literature Review**: Comprehensive survey of 12+ key references (JJF 1159-2006 standard, ACS papers, etc.)
- **Confidence Ratings**: All formation factors annotated with ★★★★★ to ★☆☆☆☆ confidence levels
  - ★★★★★ ICP-MS oxide/double charge: Based on international standards, uncertainty <20%
  - ★★★☆☆ GDMS/SIMS: Extrapolated from ICP-MS, uncertainty 50-100%
  - ★☆☆☆☆ maxsize ≥ 4: Pure theoretical estimates, no experimental validation
- **Parameter Adjustments**: Optimized GDMS parameters based on literature evidence
  - Doubly charged: 1.0e-2 → 5.0e-3 (milder energy distribution in glow discharge)
  - Plasma adducts: 1.0e-4 → 5.0e-5 (lower collision frequency at low pressure)
- **User Calibration**: Added detailed calibration procedure documentation with code examples
- **Transparency**: Clearly marked which values have literature support vs. empirical estimates

---

## [2.6.0] - 2026-06-09

### 中文

#### 新增功能

##### 性能优化 (Issue #2)
- **预过滤剪枝算法**: 在生成组合前提前排除无效同位素，加速干扰计算
- **并行计算支持**: 通过 multiprocessing.Pool 实现多核并行处理
- **新增参数**: `use_pruning`（默认 True）、`n_workers`（可选）
- **性能提升**: maxsize=4 场景下速度提升 2.9 倍

##### 内存优化 (Issue #3)
- **生成器模式**: 组合枚举使用生成器，避免一次性加载所有数据
- **流式处理架构**: 分批处理减少峰值内存占用
- **数据类型优化**: 使用 float32 替代 float64
- **内存降低**: 减少 29.5%-50% 内存使用

##### UI 组件模块化 (Issue #4)
- **提取 6 个独立 UI 组件**:
  - TableModel、TableView、HTMLDelegate 表格组件
  - ElementInput 元素选择器（芯片样式选择界面）
  - InterferenceFilterProxy 高级查询语法过滤器
  - CalculationWorker 后台计算工作线程
- **100% 向后兼容**: 所有现有代码无需修改即可继续工作

##### 配置持久化系统 (Issue #5)
- **JSON 配置存储**: 自动保存和恢复用户设置
- **命名预设管理**: 支持保存和加载自定义配置预设
- **导入导出功能**: 支持配置的导入和导出为 JSON 文件
- **最近目标峰追踪**: 自动记录最近使用的 10 个目标峰
- **应用生命周期自动保存/恢复**: 跨会话保持用户偏好

##### 插件系统 (Issue #6)
- **YAML 配置插件框架**: 灵活的插件扩展机制
- **2 个内置插件**: Enhanced Export（增强导出）、Custom Rules（自定义规则）
- **热重载支持**: 无需重启应用即可加载新插件
- **完整的插件 API 文档**: 便于开发者创建自定义插件

##### 测试增强 (Issue #7)
- **84+ 新单元测试**: 覆盖核心功能和边界情况
- **性能基准测试套件**: 自动化性能回归检测
- **边界情况测试**: 确保极端输入下的稳定性
- **截图对比框架**: GUI 视觉回归测试

##### 日志系统 (Issue #8)
- **结构化日志**: 5 个日志级别（DEBUG 到 CRITICAL）
- **错误跟踪和诊断信息**: 详细的运行时上下文
- **JSON 诊断报告导出**: 便于问题排查和技术支持
- **与现有错误处理集成**: 无缝整合到异常处理流程

##### API 文档 (Issue #9)
- **Sphinx 文档系统**: 自动生成 HTML API 文档
- **Google 风格 docstrings**: 标准化的文档注释格式
- **类型注解最佳实践**: 完整的类型提示覆盖
- **HTML 文档生成**: 美观的在线文档浏览体验

##### 用户手册增强 (Issue #10)
- **从 234 行扩展到 378 行**: 更详细的使用说明
- **3 个新章节**: 插件系统、日志系统、性能优化
- **FAQ 扩展到 14 个问题**: 覆盖常见使用场景
- **配置管理指南**: 详细的配置持久化使用说明
- **故障排除章节**: 常见问题解决方案

##### 国际化 (Issue #11)
- **日语翻译**: 完整的 UI 文本翻译
- **TranslationManager 核心类**: 统一的翻译管理机制
- **运行时语言切换**: 无需重启应用即可切换语言
- **支持 3 种语言**: 英语、中文、日语

##### Poetry 迁移 (Issue #12)
- **完整的 pyproject.toml 配置**: 现代化依赖管理
- **依赖分组**: main、dev、extras 三组依赖
- **开发工具链集成**: flake8、black、isort、mypy
- **保持 setup.py 向后兼容**: pip 安装仍然可用

##### CI/CD 优化 (Issue #13)
- **增强的工作流**: 5 个独立的 CI 作业
- **多版本测试矩阵**: 12 种 Python/OS 组合测试
- **代码质量检查**: flake8/black/isort/mypy 自动化检查
- **Dependabot 集成**: 自动依赖更新提醒
- **性能回归检测**: 自动识别性能下降

##### 变更
- **性能**: 默认启用预过滤剪枝算法，所有计算自动受益
- **内存**: 优化数据类型（float32 替代 float64）
- **架构**: UI 组件提取到 ui_components/ 包
- **构建**: 现代化依赖管理，支持 Poetry

##### 改进
- **文档**: 完整的 API 参考和用户指南
- **测试**: 全面的测试覆盖和基准测试
- **日志**: 结构化诊断和错误跟踪
- **国际化**: 运行时语言切换支持

##### 性能指标
- **计算速度**: 2.9 倍提升（maxsize=4）
- **内存使用**: 减少 29.5%-50%
- **测试覆盖**: 新增 84+ 测试用例

##### 迁移指南
- **对用户**: 无需任何操作，完全向后兼容
- **对开发者**: 
  - 新代码使用 `ui_components` 导入
  - 启用流式模式: `interference(..., use_streaming=True)`
  - 使用 Poetry: `poetry install`（setup.py 仍然有效）

---

### English

#### Added

##### Performance Optimization (Issue #2)
- **Pre-filtering pruning algorithm**: Eliminates invalid isotopes before combination generation to accelerate interference calculation
- **Parallel computing support**: Multi-core parallel processing via multiprocessing.Pool
- **New parameters**: `use_pruning` (default True), `n_workers` (optional)
- **Performance improvement**: 2.9x speedup for maxsize=4 scenarios

##### Memory Optimization (Issue #3)
- **Generator pattern**: Combination enumeration uses generators to avoid loading all data at once
- **Streaming processing architecture**: Batch processing reduces peak memory usage
- **Data type optimization**: Use float32 instead of float64
- **Memory reduction**: 29.5%-50% less memory usage

##### UI Modularization (Issue #4)
- **Extracted 6 independent UI components**:
  - TableModel, TableView, HTMLDelegate table components
  - ElementInput element selector (chip-style selection interface)
  - InterferenceFilterProxy with advanced query syntax
  - CalculationWorker for background processing
- **100% backward compatible**: All existing code works without modification

##### Configuration Persistence (Issue #5)
- **JSON-based configuration storage**: Automatic save and restore of user settings
- **Named presets management**: Support for saving and loading custom configuration presets
- **Import/export functionality**: Import and export configurations as JSON files
- **Recent targets tracking**: Automatically track the last 10 used target peaks
- **Automatic save/restore on app lifecycle**: Cross-session persistence of user preferences

##### Plugin System (Issue #6)
- **YAML-based plugin framework**: Flexible plugin extension mechanism
- **2 built-in plugins**: Enhanced Export, Custom Rules
- **Hot-reload support**: Load new plugins without restarting the application
- **Complete plugin API documentation**: Easy for developers to create custom plugins

##### Testing Enhancement (Issue #7)
- **84+ new unit tests**: Coverage for core functionality and edge cases
- **Performance benchmark suite**: Automated performance regression detection
- **Edge case testing**: Ensure stability under extreme inputs
- **Screenshot comparison framework**: GUI visual regression testing

##### Logging System (Issue #8)
- **Structured logging**: 5 log levels (DEBUG to CRITICAL)
- **Error tracking and diagnostic information**: Detailed runtime context
- **JSON diagnostic report export**: Easy troubleshooting and technical support
- **Integration with existing error handling**: Seamless integration into exception handling flow

##### API Documentation (Issue #9)
- **Sphinx documentation system**: Auto-generated HTML API documentation
- **Google-style docstrings**: Standardized documentation comment format
- **Type annotations best practices**: Complete type hint coverage
- **HTML documentation generation**: Beautiful online documentation browsing experience

##### User Manual Enhancement (Issue #10)
- **Expanded from 234 to 378 lines**: More detailed usage instructions
- **3 new chapters**: Plugin system, logging system, performance optimization
- **FAQ expanded to 14 questions**: Cover common usage scenarios
- **Configuration management guide**: Detailed configuration persistence usage guide
- **Troubleshooting section**: Solutions to common problems

##### Internationalization (Issue #11)
- **Japanese translation**: Complete UI text translation
- **TranslationManager core class**: Unified translation management mechanism
- **Runtime language switching**: Switch languages without restarting the application
- **Support for 3 languages**: English, Chinese, Japanese

##### Poetry Migration (Issue #12)
- **Complete pyproject.toml configuration**: Modern dependency management
- **Dependency groups**: main, dev, extras three dependency groups
- **Development toolchain integration**: flake8, black, isort, mypy
- **Maintained setup.py backward compatibility**: pip installation still available

##### CI/CD Optimization (Issue #13)
- **Enhanced workflow**: 5 independent CI jobs
- **Multi-version test matrix**: 12 Python/OS combination tests
- **Code quality checks**: Automated flake8/black/isort/mypy checks
- **Dependabot integration**: Automatic dependency update notifications
- **Performance regression detection**: Automatically identify performance degradation

##### Changed
- **Performance**: Default pre-filtering pruning enabled, all calculations benefit automatically
- **Memory**: Optimized data types (float32 instead of float64)
- **Architecture**: UI components extracted to ui_components/ package
- **Build**: Modern dependency management with Poetry support

##### Improved
- **Documentation**: Complete API reference and user guide
- **Testing**: Comprehensive test coverage with benchmarks
- **Logging**: Structured diagnostics and error tracking
- **i18n**: Runtime language switching support

##### Performance Metrics
- **Calculation speed**: 2.9x faster (maxsize=4)
- **Memory usage**: 29.5%-50% reduction
- **Test coverage**: 84+ new tests added

##### Migration Guide
- **For Users**: No action required, fully backward compatible
- **For Developers**: 
  - Use `ui_components` imports for new code
  - Enable streaming mode: `interference(..., use_streaming=True)`
  - Use Poetry: `poetry install` (setup.py still works)

## [Unreleased]

### 中文

#### 配置持久化系统 (Issue #5)
- **用户偏好保存**: 实现完整的配置持久化系统，自动保存和恢复用户设置
  - 语言偏好、仪器模式、MRP预设等跨会话保持
  - 配置文件存储在平台特定目录（Windows: %APPDATA%，macOS/Linux: ~/.config）
- **命名预设功能**: 支持保存和加载自定义配置预设
  - 快速切换不同的工作配置
  - 预设文件独立存储，便于分享和备份
- **导入导出功能**: 支持配置的导入和导出为JSON文件
  - 便于在不同设备间同步配置
  - 支持团队共享标准配置模板
- **最近目标峰追踪**: 自动记录最近使用的10个目标峰
  - 快速访问常用目标质量数
  - 提高工作效率

#### 架构重构 (Issue #4)
- **UI组件模块化**: 创建 `ui_components` 包,将大型 ui.py 文件拆分为多个独立模块
  - `table.py`: TableModel, TableView, HTMLDelegate 表格组件
  - `element_input.py`: ElementInput 元素选择器组件
  - `filter_proxy.py`: InterferenceFilterProxy 结果过滤器
  - `worker.py`: CalculationWorker 后台计算工作线程
  - `utils.py`: 共享工具函数和辅助方法
- **向后兼容**: 保持完全 API 兼容,所有现有代码无需修改即可继续工作
- **测试通过**: 57个测试全部通过,确保功能完整性
- **模块化优势**: 
  - 新组件可独立导入和使用: `from interference_calculator.ui_components import TableModel`
  - 为未来进一步拆分奠定基础(如 Spectrum 和 MainWidget)
  - 提高代码可维护性和可测试性

#### 性能优化
- `interference()` 函数新增预过滤剪枝算法，在生成组合前提前排除无效同位素，
  maxsize=4-5 场景下可获得 10-100 倍速度提升。
- 新增并行计算支持，通过环境变量 `IC_USE_PARALLEL=1` 或 `n_workers` 参数启用，
  利用多核 CPU 加速大规模计算。
- 新增实验性 GPU 加速接口 `interference_gpu()`（需要 CuPy），为未来 GPU 优化预留框架。
- 内存使用增加不超过 20%，保持完全 API 兼容，现有代码无需修改即可受益。

#### 内存优化
- 新增流式处理模式 (`use_streaming=True`)，通过生成器模式和分批处理减少峰值内存占用，
  maxsize=4+ 场景下可降低 30-70% 内存使用。
- 数值列采用 float32 数据类型替代 float64，节省约 50% 内存，同时保持足够的精度
  （质谱计算通常需要 4-6 位有效数字，float32 提供 7 位）。
- 完全向后兼容，默认禁用流式模式以保持原有行为。

#### 发布访问
- Gitee 发行版现在可以作为国内 Python 安装包下载入口；Windows 和 macOS 桌面
  安装包继续链接到正式 GitHub 构建产物。
- 已发布的 GitHub 版本可以更可靠地镜像到 Gitee，国内用户在 GitHub 访问不稳定时
  更容易获得对应版本下载。
- 新增实验性的 Gitee 侧 Windows `.zip` 打包路径；当 Gitee 流水线运行在 Windows
  执行环境时，可直接生成 Windows 免安装包，否则会明确跳过并继续使用 GitHub
  安装包链接。

#### 文档
- 发布指南和双仓库同步说明已更新，明确 GitHub 与 Gitee 两个发布渠道如何配合：
  桌面安装包以 GitHub 为准，Gitee 可作为国内包下载镜像。

### English

#### Configuration Persistence System (Issue #5)
- **User Preference Saving**: Implemented complete configuration persistence system for automatic save and restore of user settings
  - Language preference, instrument mode, MRP presets persist across sessions
  - Configuration files stored in platform-specific directories (Windows: %APPDATA%, macOS/Linux: ~/.config)
- **Named Presets**: Support for saving and loading custom configuration presets
  - Quickly switch between different work configurations
  - Preset files stored independently for easy sharing and backup
- **Import/Export Functionality**: Support for importing and exporting configurations as JSON files
  - Easy synchronization of settings across different devices
  - Enable teams to share standard configuration templates
- **Recent Target Tracking**: Automatically track the last 10 used target peaks
  - Quick access to frequently used mass numbers
  - Improved workflow efficiency

#### Architecture Refactoring (Issue #4)
- **UI Component Modularization**: Created `ui_components` package to split the large ui.py file into independent modules
  - `table.py`: TableModel, TableView, HTMLDelegate table components
  - `element_input.py`: ElementInput element selector component
  - `filter_proxy.py`: InterferenceFilterProxy result filter
  - `worker.py`: CalculationWorker background computation worker thread
  - `utils.py`: Shared utility functions and helpers
- **Backward Compatible**: Full API compatibility maintained; all existing code works without modification
- **Tests Passing**: All 57 tests pass, ensuring functional integrity
- **Modularization Benefits**:
  - Components can be imported independently: `from interference_calculator.ui_components import TableModel`
  - Lays foundation for future splitting (e.g., Spectrum and MainWidget)
  - Improves code maintainability and testability

#### Performance Optimization
- Added pre-filtering pruning algorithm to `interference()` function that excludes
  invalid isotopes before generating combinations, achieving 10-100x speedup for
  maxsize=4-5 scenarios.
- Added parallel computation support via environment variable `IC_USE_PARALLEL=1`
  or `n_workers` parameter, utilizing multi-core CPUs for large-scale calculations.
- Added experimental GPU acceleration interface `interference_gpu()` (requires CuPy)
  as a framework for future GPU optimization.
- Memory footprint increase is less than 20%, with full API compatibility maintained;
  existing code benefits automatically without modifications.

#### Memory Optimization
- Added streaming processing mode (`use_streaming=True`) that reduces peak memory
  usage by 30-70% for maxsize=4+ scenarios through generator patterns and batch processing.
- Numeric columns now use float32 instead of float64, saving ~50% memory while maintaining
  sufficient precision (mass spectrometry typically requires 4-6 significant digits,
  float32 provides 7).
- Fully backward compatible; streaming mode is disabled by default to preserve existing behavior.

#### Release Access
- Gitee releases can now act as a domestic download path for the Python package
  files, while Windows and macOS desktop installers continue to link back to the
  canonical GitHub builds.
- Existing GitHub releases can be mirrored to Gitee more reliably, making it
  easier for users in China to access versioned downloads when GitHub network
  access is unstable.
- Add an experimental Gitee-side Windows `.zip` packaging path. It can publish a
  Windows standalone package when the Gitee pipeline runs on Windows, and skips
  clearly when only a non-Windows runner is available.

#### Documentation
- Release and repository-sync guides now explain how the GitHub and Gitee
  release channels work together, including which platform should be used for
  desktop installers and which one can be used as a domestic package mirror.

## [2.5.0] - 2026-06-01

### 中文

#### 主要亮点
- 新增实验性的 GD90Trace `.TRR` 原始文件导入，并支持较早的 Elsima `.GDR`
  原始格式。用户可以更接近 GDMS 原始数据进行目标峰选择，而不再局限于 Excel 导出
  谱图。
- 原始文件导入增加多 Run 选择器；如果某个 Run 的同位素集合与主 Run 不一致，会被
  标记出来，便于识别异常数据。

#### 易用性
- 导入同位素列表现在显示天然丰度；理论 m/z 和实测 m/z 仍在下方目标信息中展示。
- 目标导入按钮、GDMS 目标区域、左侧控制面板和数值调节控件进一步收紧布局，在启动
  状态和导入数据后都更稳定。
- README 截图和产品名称已刷新，与当前界面保持一致。

### English

#### Highlights
- Added experimental import for GD90Trace `.TRR` raw files and older Elsima
  `.GDR` raw files, allowing users to work closer to original GDMS data rather
  than only exported Excel profiles.
- Added a multi-run selector for raw-file imports. Runs with isotope sets that
  differ from the main run are marked so users can spot inconsistent raw data.

#### Usability
- Imported isotope choices now show natural abundance, while theoretical and
  observed m/z details remain in the target summary below.
- The target import button, GDMS target area, left control panel, and spin-box
  controls have been tightened and made more consistent across startup and
  imported-data states.
- README screenshots and product naming were refreshed to match the current
  interface.

## [2.4.2] - 2026-05-31

### 中文

#### 修复
- 修复帮助窗口在帮助文本包含 `Fe{56}` 等同位素标签时崩溃的问题。

### English

#### Fixed
- The Help window no longer crashes when help text contains isotope labels such
  as `Fe{56}`.

## [2.4.1] - 2026-05-31

### 中文

#### 易用性
- 桌面界面启动时默认使用中文，同时保留英文切换。
- 文档中的产品名称调整为更明确的无机质谱峰干扰计算器。

### English

#### Usability
- The desktop interface now starts in Chinese by default, with English still
  available from the language selector.
- Documentation now uses the clearer product name
  `Inorganic MS Interference Calculator` for the inorganic edition.

## [2.4.0] - 2026-05-31

### 中文

#### 谱图
- 新增可选的实验性实测峰形叠加，可在目标峰居中的谱图中对比 GDMS 实测峰形与理论
  干扰候选峰。
- 新增可选的 m/z 可视化匹配功能，用于观察实测峰中心与理论同位素位置的对应关系；
  该功能只影响显示，不改变干扰计算结果。
- 当导入数据中存在有效 FWHM 和质量范围时，可自动估算仪器 MRP 和扫描窗口宽度。

#### 工作流
- 元素组合预设改为追加尚未选择的元素，不再清空当前选择。导入样品元素后，可以
  继续补充等离子体、背景或基体来源元素。

#### 修复
- 修正实测峰图例颜色与实际曲线颜色不一致的问题。
- 修正谱图工具栏按钮选中后文字可能难以阅读的问题。

### English

#### Spectrum View
- Added an optional experimental overlay for real imported GDMS peak profiles,
  so users can compare measured peak shapes against theoretical interference
  candidates in the target-centered spectrum.
- Added optional visual m/z matching for imported profiles. This helps users
  see how measured peak centers line up with theoretical isotope positions
  without changing the interference calculation itself.
- Added automatic estimates for instrument MRP and sweep width from imported
  peak data when valid FWHM and mass-range information are available.

#### Workflow
- Element presets now append missing elements instead of replacing the current
  selection, making it easier to keep imported sample elements while adding
  plasma, background, or matrix sources.

#### Fixed
- The imported-profile legend color now matches the actual profile trace.
- Spectrum toolbar text remains readable when buttons are selected.

## [2.3.0] - 2026-05-31

### 中文

#### 主要亮点
- 导入的 GDMS 谱图目标峰成为首选目标选择流程；手动选择仍作为显式覆盖方式保留。
- 目标峰选择器按元素周期表顺序排列，长列表更容易浏览。
- 导入目标峰摘要支持多行显示，避免理论 m/z 与实测 m/z 信息在左侧面板中被截断。

#### 安装
- Windows 发布包改为 `.zip` 目录版应用，减少单文件程序每次解压运行时导致的长时间
  无反馈。
- macOS 在未配置 Apple 签名时可发布未签名 DMG；配置完整凭据后可自动签名和公证。
- Excel 导入支持已纳入默认安装，因为 GDMS 谱图导入已经是主流程的一部分。

#### 稳定性
- 启动阶段减少非必要计算模块加载，让界面更快出现。
- 直接从源码运行时，导入路径和依赖提示更加可靠。

### English

#### Highlights
- Imported GDMS profile targets became the primary target-selection workflow.
  Manual target selection is still available as an explicit override.
- The target selector now follows periodic-table order, making long target
  lists easier to scan.
- Imported target summaries wrap across multiple lines so theoretical and
  observed m/z information is not clipped in the left panel.

#### Installation
- Windows releases now use a zipped app folder instead of a single executable,
  reducing the long blank startup period caused by runtime extraction.
- macOS releases can be published unsigned when Apple signing is not configured,
  and can use signing/notarization automatically when the required credentials
  are available.
- Excel import support is included by default because GDMS profile import is now
  part of the main workflow.

#### Reliability
- Startup loads less nonessential calculation code before the interface appears.
- Running the app directly from source has clearer import and dependency
  behavior.

## [2.2.0] - 2026-05-31

### 中文

#### GDMS 导入
- 新增 GDMS Excel 谱图导入。导出的同位素谱图可以自动填充元素列表，并提供带实测
  m/z 摘要的目标峰选择。

#### 文档
- README、软件介绍和图文用户手册已补充 GDMS 谱图导入工作流。

### English

#### GDMS Import
- Added GDMS Excel profile import. Exported isotope profiles can now populate
  the element list and provide selectable target peaks with observed m/z
  summaries.

#### Documentation
- README, Help, and the illustrated user manual now cover the GDMS profile
  import workflow.

## [2.1.0] - 2026-05-31

### 中文

#### 主要亮点
- 项目明确为两个版本线：`main` 是无机材料 / 无机质谱专用版，
  `maintenance/original` 是现代化后的通用扫描维护线。
- 可见 GUI 文本、工具提示、对话框、状态消息、筛选器、元素选择控件和帮助界面均已
  覆盖中英文。
- 元素选择器只显示尚未添加的元素，减少重复选择。
- 谱图交互增强：支持峰悬停详情、点击峰联动结果表、未分辨区间阴影和 PNG 导出。

#### 易用性
- 元素输入默认留空，并使用紧凑元素标签，大元素集合更容易管理。
- 独立发布版内置 Excel 支持。

#### 修复
- 修复一次计算结束后再次计算可能触发的线程崩溃。
- 用户从同位素比率视图返回干扰结果时不再需要重新计算。
- 优化元素输入空状态，移除空白区域的误导性提示。
- 谱图缩放在中英文界面下都能正确遵循 GDMS ppm 全窗口和 MRP 区间。

### English

#### Highlights
- The project now has two clear editions: the inorganic-materials specialist
  edition on `main`, and a modernized general-scan maintenance line on
  `maintenance/original`.
- Visible GUI text, tooltips, dialogs, status messages, filters, element
  selector controls, and Help paths are covered in both Chinese and English.
- The element selector now only offers elements that have not already been
  added.
- Spectrum interaction was expanded with peak hover details, click-to-select
  result rows, unresolved-band shading, and PNG export.

#### Usability
- Element input starts empty and uses compact chips, making large element sets
  easier to manage.
- Standalone releases include Excel support.

#### Fixed
- Fixed a calculation-thread crash that could occur after one calculation had
  already completed.
- Users can now return from the isotope-ratio view to interference results
  without recalculating.
- Cleaned up the element-input empty state and removed confusing blank-area
  tooltips.
- Spectrum scaling now respects the full GDMS ppm window and MRP band in both
  languages.

## [2.0.6] - 2026-05-30

### 中文

#### 修复
- Windows 下谱图窗口会打开在可见屏幕区域内，不再跑到屏幕外。

#### 安装
- 通过可执行文件压缩和未使用 GUI 模块裁剪，发布包体积进一步减小。

### English

#### Fixed
- On Windows, the spectrum window now opens within the visible screen area
  instead of appearing off-screen.

#### Installation
- Release packages are smaller thanks to executable compression and unused
  GUI-module exclusions.

## [2.0.5] - 2026-05-30

### 中文

#### 文档
- 安装说明现在清晰区分独立应用下载、`pip install` 和源码安装三种方式。
- 不同安装方式对应的运行说明已同步更新。

### English

#### Documentation
- Installation guidance now clearly separates standalone app downloads,
  `pip install`, and source installation.
- Running instructions were updated for each installation path.

## [2.0.4] - 2026-05-30

### 中文

#### 安装
- 版本发布开始提供 Windows 和 macOS 独立应用下载，普通桌面使用不再需要安装 Python。

#### 文档
- README 使用说明已同步到包安装和命令行入口。

### English

#### Installation
- Version releases now provide standalone Windows and macOS app downloads, so
  users do not need to install Python for normal desktop use.

#### Documentation
- README usage guidance was aligned with package and command-line installation.

## [2.0.3] - 2026-05-30

### 中文

#### 视觉识别
- 新增 Windows 和 macOS 应用图标，并统一来自同一视觉源，桌面环境中更容易识别。

### English

#### Visual Identity
- Added Windows and macOS application icons generated from the same visual
  source, improving recognition in the desktop environment.

## [2.0.2] - 2026-05-30

### 中文

#### 性能
- 大型科学计算库改为按需加载，界面启动更快。

#### 谱图
- 谱图改用原生 Qt 绘制，不再依赖外部绘图库，同时保留对数强度棒图、颜色分类、
  峰标注、缩放和双语标签。
- 谱图窗口不再需要额外绘图库即可使用。

### English

#### Performance
- GUI startup is faster because large scientific libraries are loaded later,
  only when needed.

#### Spectrum View
- The spectrum view now uses native Qt rendering instead of an external plotting
  library, while keeping log-scale stems, color categories, peak labels, zoom,
  and bilingual labels.
- The spectrum window is available without installing an extra plotting
  dependency.

## [2.0.1] - 2026-05-30

### 中文

#### 显示
- 启用高 DPI 缩放，2K/4K 显示器上的文字和控件保持清晰可读。

#### 文档
- README 改为中英文双语，中文为默认入口，并提供页面内语言切换。

#### 安装
- 发布流程提供跨平台源码包和 wheel。

### English

#### Display
- Enabled high-DPI scaling so text and controls remain readable on 2K/4K
  displays.

#### Documentation
- README became bilingual, with Chinese as the default entry and in-page
  language links.

#### Installation
- Cross-platform source and wheel packages are built for release use.

## [2.0.0] - 2026-05-30

### 中文

#### 大版本升级
- 引入现代化 PyQt5 桌面界面，支持中英文切换、结果摘要、紧凑结果表和以目标峰
  居中的谱图视图。
- 内置 GDMS、ICP-MS 和 SIMS 仪器预设，为电荷态、目标窗口、风险模型和质量分辨率
  提供实用默认值。
- 新增无机质谱干扰筛查能力，覆盖常见原子、分子、等离子体、背景和基体簇干扰。
- 新增基于同位素概率和方法特异形成倾向的相对风险评分。
- 新增常用无机元素集合，包括广谱筛查用的全元素预设。
- 新增图文用户手册。

#### 数据
- 同位素数据升级为 CIAAW 2024 同位素组成和 AME2020 原子质量，并包含不确定度与
  丰度区间信息。

#### 默认设置
- GDMS 默认目标窗口为 `2000 ppm` 全窗口，即以校准目标峰为中心的 `±1000 ppm`。
- 谱图坐标以目标峰为中心，可显示为 `Δppm` 或 `Δm/z`。

### English

#### Major Release
- Introduced a modern PyQt5 desktop interface with Chinese/English switching,
  result summaries, a compact result table, and a target-centered spectrum view.
- Added instrument presets for GDMS, ICP-MS, and SIMS with practical defaults
  for charge state, target window, risk model, and mass resolving power.
- Added inorganic mass-spectrometry interference screening for common atomic,
  molecular, plasma, background, and matrix-cluster interferences.
- Added a relative-risk score based on isotope probability and
  method-specific formation tendencies.
- Added common inorganic element sets, including a broad all-elements preset.
- Added an illustrated user manual.

#### Data
- Updated isotope data to CIAAW 2024 isotopic compositions and AME2020 atomic
  masses, including uncertainty and abundance-interval information.

#### Defaults
- GDMS now uses a `2000 ppm` full target window by default, equivalent to
  `±1000 ppm` around the calibrated target peak.
- Spectrum axes are centered on the target peak and can be shown as `Δppm` or
  `Δm/z`.

[Unreleased]: https://github.com/Tingfe/interference_calculator/compare/v2.6.0...HEAD
[2.6.0]: https://github.com/Tingfe/interference_calculator/compare/v2.5.0...v2.6.0
[2.5.0]: https://github.com/Tingfe/interference_calculator/compare/v2.4.2...v2.5.0
[2.4.2]: https://github.com/Tingfe/interference_calculator/compare/v2.4.1...v2.4.2
[2.4.1]: https://github.com/Tingfe/interference_calculator/compare/v2.4.0...v2.4.1
[2.4.0]: https://github.com/Tingfe/interference_calculator/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/Tingfe/interference_calculator/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/Tingfe/interference_calculator/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/Tingfe/interference_calculator/compare/v2.0.6...v2.1.0
[2.0.6]: https://github.com/Tingfe/interference_calculator/compare/v2.0.5...v2.0.6
[2.0.5]: https://github.com/Tingfe/interference_calculator/compare/v2.0.4...v2.0.5
[2.0.4]: https://github.com/Tingfe/interference_calculator/compare/v2.0.3...v2.0.4
[2.0.3]: https://github.com/Tingfe/interference_calculator/compare/v2.0.2...v2.0.3
[2.0.2]: https://github.com/Tingfe/interference_calculator/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/Tingfe/interference_calculator/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/Tingfe/interference_calculator/releases/tag/v2.0.0
