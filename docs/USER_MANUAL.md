# 无机质谱峰干扰计算器 2.8.2 图文用户手册

本手册面向 GDMS、ICP-MS、SIMS 等无机质谱峰干扰筛查场景。软件默认使用中文界面，也支持切换到英文；下面以中文界面为例。

**版本**: v2.8.2 | **更新日期**: 2026年7月

## 1. 主界面

![主界面](images/main_zh.png)

主界面分为三块：

- 顶部栏：显示软件名称，并提供语言切换。
- 左侧控制栏：设置工作模式、目标峰、窗口、元素列表、离子模型和仪器 MRP。
- 右侧结果区：显示结果概览、候选峰表格和空状态提示。

## 2. 选择语言

右上角的语言下拉框可在 `English` 和 `中文` 之间切换。切换后会同步更新：

- 主窗口标题和控件标签
- 表格表头
- 状态栏提示
- Help 软件介绍
- 谱图窗口标题和图例

## 3. 选择工作模式

左侧 `流程 / 模式` 中提供三种无机质谱模式：

- `GDMS`：辉光放电质谱，默认窗口为 `2000 ppm`。
- `ICP-MS`：电感耦合等离子体质谱，默认窗口为 `400 ppm`。
- `SIMS`：二次离子质谱，默认窗口为 `200 ppm`。

建议 GDMS 用户从 `GDMS` 模式开始。

## 4. 导入 GDMS 谱图 / TRR 原始文件

如果已经从 GDMS 软件导出了 Excel 谱图文件，或保留了 GD90Trace `.TRR` / Elsima `.GDR` 原始文件，可以在目标峰区域点击 `导入`。

导入后软件会自动完成两件事：

- 从 `Fe{56}`、`U{238}` 这类谱图标题中提取元素，并填充到元素列表。
- 把文件中的同位素谱图加入目标峰下拉框，并优先用这些导入目标峰进行计算；下拉框显示同位素天然丰度，m/z 信息显示在下方目标详情中。
- 在 `添加组合` 中增加 `导入元素（N）` 预设；组合选择只追加当前缺失的元素，因此可以在保留导入样品元素的同时补充等离子体、背景或基体元素。

导入的 Excel 文件通常包含多个三列一组的谱图数据：`Mass`、`Values`、`Peaks`。软件会读取所有工作表，自动跳过空白表。TRR / GDR 文件会读取原始数据中的 Run，并从 `GDAnalysisComponent` 中提取同位素、`Mass` 点和 `Current` 强度。

如果原始文件包含多个 Run，软件会弹出 Run 选择器。通常同一个原始文件中每个 Run 的同位素集合应相同；如果某些 Run 的同位素集合与多数 Run 不一致，软件会先提示并在选择器中标记 `同位素不一致`，避免误选不完整或异常的 Run。

界面中的谱图 m/z 是实测峰形摘要：Excel 导入会读取 `Mass` / `Values` 点后计算质心，无法计算质心时使用峰顶位置；TRR / GDR 导入会优先使用原始文件保存的 `m_CentroidMassValue` 作为 observed peak 位置。

如果没有谱图文件，或者目标峰不在导入文件中，也可以勾选 `手动目标` 后手动选择目标峰和元素。

## 5. 输入目标峰

在未导入 GDMS 文件时，目标峰区域会直接显示手动元素 / 同位素选择。导入 GDMS 文件后，软件默认隐藏手动目标控件，要求用户优先从导入目标峰列表中选择。

勾选 `手动目标` 后，可以手动选择：

- 同位素形式：`75As`、`56Fe`
- 分子式形式：`40Ar35Cl`
- 数值形式：`74.9216`

如果目标峰没有显式电荷，软件会根据离子模型补充电荷并计算 m/z。

## 6. 设置 Window

`窗口宽度` 表示完整窗口宽度，而不是 `±` 半宽。

例如：

- 输入 `2000 ppm`
- 软件实际搜索目标峰两侧各 `1000 ppm`
- 谱图中目标峰位于中心

GUI 默认并固定使用 `ppm` 完整窗口。导入目标峰包含有效 `Mass` 点列时，可勾选扫描窗口旁边的 `自动`，软件会按 `(最大 Mass - 最小 Mass) / observed m/z × 1e6` 估算完整 ppm 窗口；没有有效 Mass 范围时该开关会禁用。Python API 直接调用时，`targetrange` 仍然使用 `m/z` 半宽。

## 7. 输入元素列表

`样品 / 等离子体 / 元素` 是芯片式元素选择区。点击 `+ 添加` 后，在元素选择器中勾选需要参与干扰搜索的元素。

推荐把以下元素都放进去：

- 待测元素
- 基体元素
- 等离子体元素，例如 `Ar`
- 常见背景元素，例如 `O H C N Cl S`
- 可能形成干扰的卤素或硫元素

推荐元素示例：

```text
Ar Cl As O H
```

已添加元素会显示为紧凑芯片；元素很多时该区域会自动滚动。再次点击 `+ 添加` 时，选择器只显示尚未加入的元素，避免重复添加。

![全元素输入示例](images/main_zh.png)

## 8. 添加常用元素组合

`添加组合` 下拉框会把常用元素集合追加到元素区。它不会清空当前元素，只会补充尚未选择的元素。

常用组合包括：

- 全元素（无机质谱）：覆盖常见无机质谱可测元素，保留 Th/U，排除短寿命或非常规放射性元素，适合需要全面筛查时使用。
- 导入元素（N）：仅在导入 GDMS Excel / TRR / GDR 文件后出现，用于补回本次文件中提取但当前缺失的元素。
- Ar 等离子体背景
- 轻元素背景
- 卤素 / 硫
- 过渡金属基体
- 硅酸盐基体

## 9. 设置离子模型

`离子模型` 区域包含：

- `离子`：选择 `1+`、`1+, 2+`、`1+, 2+, 3+`、`1-` 或中性。
- `最大原子数`：控制候选分子或加合物的最大原子数。
- `仪器 MRP`：仪器质量分辨能力。导入目标峰包含有效 `FWHM` 时，可勾选 `自动`，软件会按 `observed m/z / FWHM` 估算 MRP；没有有效 `FWHM` 时该开关会禁用。

MRP 不改变候选峰生成范围。它只用于判断候选峰是否能与目标峰分辨，并在结果中标记为 `是` 或 `否`。

## 10. 计算干扰峰

点击 `计算` 后，结果表会显示：

- `离子`：候选离子或目标峰
- `类型`：原子离子、氧化物、等离子体加合物、背景分子等
- `电荷`
- `m/z`
- `Δm/z`
- `Δppm`
- `MRP`
- `概率`
- `风险`
- `可分辨`

结果上方的概览条会显示当前模式、窗口、MRP、候选峰数量和未分辨峰数量。

## 11. 判断结果

重点关注三列：

- `Δppm`：候选峰与目标峰的 ppm 偏差。
- `MRP`：分辨该干扰峰所需的质量分辨能力。
- `可分辨`：当前仪器 MRP 下是否能分辨。

参考点必须明确：`Δm/z`、`Δppm`、`MRP` 和谱图中心都相对理论目标 m/z 计算。导入文件中显示的 `谱图质心` / `谱图峰顶` 是从 Excel 的 `Mass` / `Values` 点计算得到的峰形摘要，不会被直接拿来和理论候选峰相减。

如果 `可分辨` 为 `否`，说明该候选峰在当前仪器条件下可能与目标峰重叠，需要优先关注。

`风险` 是定性排序分数，用于筛查优先级，不是定量校正因子。若通过 Python API 传入 `sample_profile`，风险会进一步乘以样品先验；结果表会新增 `sample prior`、`unweighted relative risk`、`expected relative intensity` 和 `risk rationale`，用于说明该风险来自基体、杂质还是背景元素。

内置画像是面向 GDMS 干扰筛查的定性先验，不是材料牌号标准或证书限值。当前包括：

- 高纯单质：Al、Cu、Fe、Ni、Ti、Si、Mg
- 常见合金/基体：铝合金、不锈钢、镍基合金、铜基合金
- 非金属/氧化物基体：硅酸盐/玻璃、石墨/碳基体

例如高纯铝画像中，Al 是基体，AlO、AlH、Al2 等基体相关干扰会得到更高权重；Fe、Si、Mg、Cu 等 ppm 级杂质会按预估含量降低权重；O、H、C、N、Cl、S 按背景活度参与计算。

## 12. 查看谱图

点击谱图按钮可以打开目标峰居中的干扰谱图。

![谱图](images/spectrum_zh.png)

谱图逻辑：

- 目标峰位于中心。
- ppm 模式下横轴为 `Δppm`。
- 如果已导入 GDMS Excel / TRR / GDR 文件，可在谱图工具栏手动打开 `实测峰（测试）`，叠加文件中的真实峰形。该功能默认关闭。
- 实测峰形会按所选目标峰的谱图质心 / 峰顶对齐到中心；每个同位素峰按自身峰顶归一化显示，原始强度可在悬停提示中查看。
- 需要目视比较实测峰中心和理论峰位时，可再打开 `匹配 m/z`。该开关会自动打开实测峰叠加，将每条实测峰的谱图质心 / 峰顶分别对齐到对应同位素的理论 `m/z`，并显示对齐参考线和偏移量标签；它只影响谱图叠加显示，不改变计算结果。
- 未分辨峰使用琥珀色高亮。
- 目标峰使用红色标记。
- 候选峰强度按相对风险或概率归一化显示。
- 淡红色背景带表示当前仪器 MRP 下目标峰附近的未分辨区。
- 鼠标悬停在谱峰上会显示离子式、类型、m/z、Δppm、MRP、风险和表格行号。
- 点击谱峰会自动定位并选中右侧结果表中对应行。
- 谱图工具栏中的 `PNG` 按钮可导出当前谱图图片。

## 13. 查看同位素比

点击 `同位素比` 可以查看当前元素的同位素丰度、比值、倒数比值和数据源。

该功能适合快速检查同位素组成，也可以用于确认数据库来源。

## 14. GDMS 推荐起步配置

```text
模式: GDMS
目标: 75As
窗口宽度: 2000 ppm
元素: Ar Cl As O H
离子: 1+, 2+
最大原子数: 3
仪器 MRP: 4000
```

这组参数会筛查 As 目标峰附近常见的 ArCl 等等离子体相关干扰。

## 15. 常见问题

### Window 为什么不是 ±？

因为很多仪器方法中设置的是完整窗口宽度。软件内部会自动把完整窗口换算为目标峰两侧的半宽。

### Instrument MRP 是否影响候选峰生成？

不影响。MRP 只影响结果中的可分辨判断和谱图高亮。

### observed / 谱图质心是否参与 Δppm 计算？

不直接参与。软件读取导入文件中的 `Mass` / `Values` 数据后计算 `谱图质心`，无法计算质心时使用 `谱图峰顶`。这些值用于帮助用户识别导入目标峰。干扰峰的 `Δm/z`、`Δppm`、MRP 和谱图中心使用理论目标 m/z 作为参考点，避免把理论候选峰位置和原始 observed 目标位置混用。

谱图工具栏中的 `匹配 m/z` 是额外的显示对齐功能。开启后，实测峰曲线会以各自的 observed center 为中心，对齐到对应同位素理论 `m/z`，并用参考线和偏移量标签显示移动量；它不会回写表格，也不会改变干扰峰筛查逻辑。

### 元素很多怎么办？

使用 `+ 添加` 打开元素选择器，或在 `添加组合` 中选择全元素（无机质谱）。元素区会自动滚动，适合全元素或长列表场景。

### 风险值能否用于定量校正？

不建议直接用于定量校正。`风险` 是筛查优先级分数，需要结合方法学和标准样品校准后才能用于定量模型。

### 如何保存我的配置？

v2.6.0 引入了配置持久化功能。您的设置(语言、模式、元素列表等)会自动保存到用户配置文件中，下次启动时自动恢复。

配置文件位置:
- macOS: `~/Library/Application Support/InterferenceCalculator/config.json`
- Windows: `%APPDATA%\InterferenceCalculator\config.json`
- Linux: `~/.config/InterferenceCalculator/config.json`

### 如何重置配置？

删除上述配置文件即可恢复默认设置。

### 软件崩溃了怎么办？

1. 检查日志文件(如果启用了日志)
2. 导出诊断信息(见第18节)
3. 联系技术支持时附上诊断文件

### 如何提高计算速度？

v2.7.0 已默认使用向量化核心计算路径，通常不需要额外打开并行或剪枝开关。若计算仍然很慢，优先从输入规模入手：

- 减少元素数量
- 降低 maxsize (最大原子数)
- 缩小窗口宽度
- 使用更简单的离子模型(如只用 1+ 而非 1+, 2+)

### 支持哪些文件格式导入？

- Excel (.xlsx, .xls) - GDMS 谱图导出
- TRR (.trr) - GD90Trace 原始文件
- GDR (.gdr) - Elsima 原始文件

### 如何更新软件？

- GitHub Releases: https://github.com/Tingfe/interference_calculator/releases
- PyPI: `pip install --upgrade interference-calculator`

### 可以自定义插件吗？

是的！v2.6.0 引入了插件系统。查看 `interference_calculator/plugins/README.md` 了解如何创建自定义插件。

### 如何报告 Bug？

请在 GitHub Issues 页面报告: https://github.com/Tingfe/interference_calculator/issues

报告时请提供:
1. 操作步骤
2. 预期行为
3. 实际行为
4. 诊断文件(如果有)

## 16. Python 调用

```python
import interference_calculator as ic

data = ic.inorganic_interference(
    ['Ar', 'Cl', 'As', 'O', 'H'],
    '75As',
    charge=[1, 2],
    maxsize=3,
    risk_preset='gdms',
)
```

GUI 中的 ppm 完整窗口会换算为 API 所需的 m/z 半宽。直接调用 API 时，`targetrange` 仍然表示 m/z 半宽。

高纯铝样品画像：

```python
data = ic.inorganic_interference(
    [],
    None,
    charge=[1],
    maxsize=3,
    risk_preset='gdms',
    sample_profile='high-purity-aluminum',
)
```

自定义样品画像：

```python
profile = {
    'matrix': {'Al': 0.99999},
    'expected_impurities_ppm': {'Fe': 10, 'Si': 20, 'Mg': 5, 'Cu': 1},
    'background': {'O': 'medium', 'H': 'medium', 'C': 'low', 'N': 'low'},
    'plasma': {'Ar': 'plasma'},
    'unknown_element_activity': 'trace',
}

data = ic.inorganic_interference(
    ['Al', 'Fe', 'Si', 'Mg', 'Cu', 'O', 'H', 'C', 'N', 'Ar'],
    27.0,
    targetrange=0.05,
    sample_profile=profile,
)
```

## 17. 插件系统 (v2.6.0 新增)

### 什么是插件?

插件系统允许用户扩展软件功能，无需修改核心代码。v2.6.0 引入了灵活的插件架构。

### 内置插件

软件自带两个示例插件:

1. **Enhanced Export** - 增强数据导出
   - 支持 JSON 格式导出
   - 增强的 CSV 格式(自定义分隔符)
   
2. **Custom Rules** - 自定义计算规则
   - 添加自定义干扰判断规则
   - 设置验证钩子函数

### 如何使用插件

插件配置文件位于 `interference_calculator/plugins/builtin/` 目录。

查看插件 README 了解如何创建自定义插件:
```bash
open interference_calculator/plugins/README.md
```

## 18. 日志和诊断 (v2.6.0 新增)

### 启用日志

可以通过编程方式启用详细日志:

```python
from interference_calculator.logging_system import setup_logging

# 启用DEBUG级别日志，输出到文件
logger = setup_logging(log_level="DEBUG", log_file="app.log")
```

### 诊断信息导出

当遇到问题时，可以导出诊断信息:

```python
from interference_calculator.logging_system import get_logger

logger = get_logger()
diag_file = logger.export_diagnostics("diagnostics.json")
print(f"诊断文件: {diag_file}")
```

诊断文件包含:
- 系统和Python版本信息
- 应用程序配置
- 错误历史记录
- 时间戳

## 19. 性能优化建议

### 批量处理元素

对于大量元素，建议使用批量模式:

```python
from interference_calculator.inorganic import inorganic_interference

elements = ['Fe', 'Cu', 'Zn', 'Ni', 'Co']
results = {}
for elem in elements:
    results[elem] = inorganic_interference(
        atoms={elem: 1}, 
        target=elem
    )
```

### 调整最大原子数

较小的 `maxsize` 值可以显著提升性能:
- `maxsize=2`: 快速筛查
- `maxsize=3`: 标准模式(推荐)
- `maxsize=4+`: 深度筛查(较慢)

### 使用合适的窗口宽度

更小的窗口宽度减少候选峰数量:
- GDMS: 2000 ppm (标准)
- ICP-MS: 400 ppm (高分辨)
- SIMS: 200 ppm (超高分辨)
