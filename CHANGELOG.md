# Changelog / 更新日志

## [2.3.0] - 2026-05-31

### English

#### Changed
- Changed Windows release packaging from PyInstaller one-file `.exe` to a
  zipped app directory to avoid slow no-feedback startup while the runtime is
  extracted on every launch.
- Made imported GDMS profile targets the primary target-selection path and moved
  manual target selection behind an explicit manual override.
- Simplified the GDMS profile import button label to `Import` / `导入`.
- Ordered manual and imported target selectors by periodic-table order, with
  imported isotopes sorted by mass number within the same element.
- Wrapped the imported target m/z summary across multiple lines to avoid
  clipping in the left control panel.
- Added a dynamic imported-elements preset after GDMS Excel import so users can
  restore all file-derived elements after accidental edits.
- Clarified that profile centroid/apex m/z is calculated from imported
  Mass/Values points, while Δm/z, Δppm, MRP, and the spectrum center use the
  theoretical target m/z as the reference.

#### Fixed
- Delayed heavy top-level API and GUI calculation imports so startup does not
  load nonessential calculation modules before the interface is shown.
- Made package metadata extraction in `setup.py` robust after adding lazy
  public API loading.
- Promoted `openpyxl` to a default dependency because GDMS Excel import is now
  part of the primary workflow, not only an optional export path.
- Updated missing-dependency guidance for direct source runs and editable
  installs.
- Fixed direct source execution via `python interference_calculator/ui.py` so
  package imports resolve from the project root.
- Hardened the macOS release pipeline so tagged releases require Developer ID
  signing and Apple notarization instead of publishing ad-hoc signed DMG files
  that Gatekeeper reports as damaged.
- Set a valid macOS bundle identifier and synchronized the bundle version with
  the package version during CI packaging.

#### Added
- Added macOS signing and notarization documentation for the GitHub Release
  workflow secrets.

### 中文

#### 变更
- Windows 发布包从 PyInstaller 单文件 `.exe` 改为 `.zip` 目录版应用，避免每次
  启动前解压运行时造成长时间无反馈。
- 将导入的 GDMS 谱图目标峰作为首选目标选择路径，手动目标选择改为显式手动覆盖。
- 将 GDMS 谱图导入按钮文案简化为 `Import` / `导入`。
- 将手动和导入的目标峰选择器改为按周期表顺序排列，同一元素内按同位素质量数排列。
- 将导入目标峰的 m/z 摘要改为多行显示，避免在左侧控制栏中被遮挡或截断。
- GDMS Excel 导入后自动增加“导入元素”动态预设，误删后可一键恢复文件中的全部元素。
- 明确谱图质心 / 峰顶 m/z 由导入的 Mass / Values 点计算，而 Δm/z、Δppm、MRP
  和谱图中心均以理论目标 m/z 为参考点。

#### 修复
- 延迟包顶层 API 和 GUI 计算模块导入，减少界面显示前的非必要加载。
- 将 `setup.py` 的包元数据读取改为 AST 解析，兼容新的公开 API 懒加载实现。
- 将 `openpyxl` 提升为默认依赖，因为 GDMS Excel 导入已经是主工作流的一部分，
  不再只是可选导出功能。
- 更新直接运行源码和 editable install 场景下的缺失依赖提示。
- 修复通过 `python interference_calculator/ui.py` 直接运行源码时包导入路径无法
  解析的问题。
- 加强 macOS 发布流程：tag 发布时必须使用 Developer ID 签名并通过 Apple 公证，
  避免继续发布会被 Gatekeeper 判定为“已损坏”的 ad-hoc 签名 DMG。
- 设置合法的 macOS bundle identifier，并在 CI 打包时同步应用 bundle 版本和
  包版本。

#### 新增
- 增加 macOS 签名与公证文档，说明 GitHub Release workflow 需要配置的 secrets。

## [2.2.0] - 2026-05-31

### English

#### Added
- Added GDMS Excel profile import so exported isotope profiles can populate
  the element list and provide selectable target peaks with observed m/z
  summaries.
- Added unit coverage for GDMS profile label parsing and peak-profile summary
  statistics.

#### Changed
- Updated README, help text, and the illustrated user manual for the imported
  GDMS profile workflow.

### 中文

#### 新增
- 增加 GDMS Excel 谱图导入，可从导出的同位素谱图中自动填充元素列表，并提供
  带实测 m/z 摘要的目标峰选择。
- 增加 GDMS 谱图标签解析和峰形摘要统计的单元测试。

#### 变更
- 更新 README、软件介绍和图文用户手册，补充导入 GDMS 谱图的工作流。

## [2.1.0] - 2026-05-31

### English

#### Added
- Defined the project branch model: `main` is the inorganic-materials
  specialist edition, while `maintenance/original` is the modernized
  general-scan maintenance line with refreshed data and dependencies.
- Completed bilingual coverage for visible GUI text, tooltips, dialogs, status
  messages, filters, element selector controls, and help-related UI paths.
- Added localization regression tests to keep Chinese and English UI keys in
  sync.
- Added an element selector that only offers elements not already selected.
- Added interactive spectrum tools: peak hover details, click-to-select result
  table rows, instrument-MRP unresolved band shading, and PNG export.

#### Changed
- Element input now starts empty, uses compact chips, and has a cleaner empty
  state for selecting elements rather than typing long lists.
- Spectrum drawing now uses the Qt default UI font to avoid missing-font alias
  warnings.
- Standalone release builds include Excel export support via `openpyxl`.

#### Fixed
- Fixed stale `QThread` references after calculation completion, which could
  crash the GUI on a subsequent calculation.
- Fixed the isotope-ratio view toggle so users can return to interference
  results without recalculating.
- Fixed element-input styling so the inner chip canvas no longer inherits an
  extra border, and removed empty tooltips from the blank element area.
- Fixed Chinese spectrum-window scaling so the target-centered axis respects
  the full GDMS ppm window and MRP band in both languages.

### 中文

#### 新增
- 明确项目分支模型：`main` 作为无机材料 / 无机质谱专用版主线，
  `maintenance/original` 作为现代化通用扫描维护线，保留更新后的数据和依赖。
- 完成可见 GUI 文本、工具提示、对话框、状态消息、筛选器、元素选择器控件
  以及帮助相关界面的中英文覆盖。
- 增加本地化回归测试，确保中文和英文 UI key 保持同步。
- 增加元素选择器，只显示尚未添加的元素。
- 增加交互式谱图功能：峰悬停详情、点击峰联动结果表、仪器 MRP 未分辨区间阴影
  以及 PNG 导出。

#### 变更
- 元素输入默认留空，改用更紧凑的元素标签，并优化空状态，使用户优先选择元素
  而不是输入长列表。
- 谱图绘制改用 Qt 默认 UI 字体，避免缺失字体别名带来的启动警告。
- 独立发布版内置 `openpyxl`，支持 Excel 导出。

#### 修复
- 修复计算完成后残留 `QThread` 引用的问题，避免再次计算时 GUI 崩溃。
- 修复同位素比率视图切换后无法直接回到干扰结果的问题，无需重新计算。
- 修复元素输入区样式，让内部标签画布不再继承额外边框，并移除空白区域的空提示。
- 修复中文界面下谱图窗口缩放问题，确保以目标峰居中的 GDMS ppm 全窗口和 MRP 区间
  在双语界面中一致生效。

## [2.0.6] - 2026-05-30

### English

#### Fixed
- Spectrum window on Windows now positions within the visible screen area
  instead of rendering off-screen. The window is clamped to the available screen
  geometry and falls back to vertical stacking if horizontal space is
  insufficient.

#### Changed
- CI workflow now installs UPX on macOS and Windows runners to compress final
  executables and reduce download size.
- macOS build uses `--strip` to strip debug symbols from binaries.
- Both builds exclude unused PyQt5 submodules to reduce bundled size.

### 中文

#### 修复
- 修复 Windows 下谱图窗口可能出现在屏幕外的问题。窗口会限制在可见屏幕区域内，
  横向空间不足时自动改为垂直排列。

#### 变更
- CI 在 macOS 和 Windows runner 上安装 UPX，用于压缩最终可执行文件并减小下载体积。
- macOS 构建使用 `--strip` 去除二进制调试符号。
- Windows/macOS 构建排除未使用的 PyQt5 子模块，以降低打包体积。

## [2.0.5] - 2026-05-30

### English

#### Changed
- README installation section now features three tiers: standalone app
  (downloadable `.exe` / `.dmg`, no Python required), `pip install`, and source
  install.
- README running instructions updated accordingly for each installation path.

### 中文

#### 变更
- README 安装部分改为三种方式：独立应用（下载 `.exe` / `.dmg`，无需 Python）、
  `pip install` 和源码安装。
- README 针对不同安装路径同步更新运行说明。

## [2.0.4] - 2026-05-30

### English

#### Added
- GitHub Actions now builds and publishes standalone applications for Windows
  (single `.exe`) and macOS (`.dmg`) automatically on every version tag push.

#### Changed
- README usage section now recommends `pip install` and the
  `interference_calculator` CLI entry point as the primary workflow.

### 中文

#### 新增
- GitHub Actions 会在推送版本标签时自动构建并发布 Windows 独立 `.exe`
  和 macOS `.dmg` 应用。

#### 变更
- README 使用说明改为优先推荐 `pip install` 和 `interference_calculator`
  命令行入口。

## [2.0.3] - 2026-05-30

### English

#### Added
- Application icon files rendered from the same vector source: `icon.ico`
  (Windows, 16/32/48/256 px) and `icon.icns` (macOS, up to 1024 px).

### 中文

#### 新增
- 从同一份矢量源生成应用图标文件：`icon.ico`（Windows，16/32/48/256 px）
  和 `icon.icns`（macOS，最高 1024 px）。

## [2.0.2] - 2026-05-30

### English

#### Changed
- Lazy-load numpy and pandas to reduce GUI startup time.
- Replaced matplotlib-based spectrum view with a native Qt QPainter
  implementation, removing the matplotlib dependency while keeping log-scale
  stems, three-colour category display, peak annotations, zoom, and bilingual
  labels.

#### Removed
- Removed matplotlib dependency from the spectrum view.

#### Fixed
- The spectrum window is always available; no external plotting library is
  required.

### 中文

#### 变更
- 延迟加载 numpy 和 pandas，减少 GUI 启动时间。
- 用原生 Qt QPainter 谱图替代 matplotlib 谱图，移除 matplotlib 依赖，同时保留
  对数强度棒图、三色峰分类、峰标注、缩放和双语标签。

#### 移除
- 谱图功能不再依赖 matplotlib。

#### 修复
- 谱图窗口始终可用，不再需要额外绘图库。

## [2.0.1] - 2026-05-30

### English

#### Fixed
- Enable PyQt5 high-DPI auto-scaling so text and controls render at readable
  sizes on 2K/4K displays.

#### Changed
- README is now bilingual Chinese/English with Chinese as the default language
  and in-page language switcher links.
- CI: simplified GitHub Actions release workflow to build cross-platform sdist
  and wheel instead of per-platform PyInstaller executables.

### 中文

#### 修复
- 启用 PyQt5 高 DPI 自动缩放，使 2K/4K 显示器上的文字和控件保持可读尺寸。

#### 变更
- README 改为中英文双语，中文为默认入口，并提供页面内语言切换链接。
- CI 简化为构建跨平台源码包和 wheel，不再在该版本流程中按平台构建 PyInstaller
  可执行文件。

## [2.0.0] - 2026-05-30

### English

#### Added
- Modern PyQt5 GUI with bilingual Chinese/English switching, result summary
  chips, empty-state guidance, compact result table, and a target-centered
  spectrum view.
- GDMS, ICP-MS, and SIMS instrument presets with practical defaults for charge
  state, target window, risk model, and mass resolving power.
- Inorganic mass-spectrometry algorithm using interference templates for atomic
  ions, doubly charged ions, oxides, hydrides, hydroxides, nitrides, carbides,
  sulfides, halides, plasma adducts, background molecules, and small matrix
  clusters.
- Relative-risk screening score based on isotope probability and
  method-specific formation factors.
- Common inorganic element sets, including an all-elements preset for broad
  inorganic MS screening.
- `inorganic_interference()` Python API alongside the existing `interference()`
  and `standard_ratio()` APIs.
- Unit test suite covering core molecule parsing, interference search,
  inorganic screening, and data schema.
- Illustrated user manual (`docs/USER_MANUAL.md`).

#### Changed
- Upgraded the isotope database to CIAAW 2024 isotopic compositions and AME2020
  atomic masses, including uncertainty and abundance-interval metadata.
- GDMS default target window is `2000 ppm` as a full window, i.e. `±1000 ppm`
  around the calibrated target peak.
- The spectrum view uses `Δppm` or `Δm/z` centered on the target peak.
- Modernised the codebase to Python 3.9+.
- Periodic table data cleaned up and re-generated.

### 中文

#### 新增
- 现代化 PyQt5 GUI，支持中英文切换、结果摘要标签、空状态引导、紧凑结果表格
  以及以目标峰居中的谱图视图。
- 内置 GDMS、ICP-MS、SIMS 仪器预设，并为电荷态、目标窗口、风险模型和质量分辨率
  提供实用默认值。
- 增加无机质谱干扰算法，覆盖原子离子、双电荷离子、氧化物、氢化物、氢氧化物、
  氮化物、碳化物、硫化物、卤化物、等离子体加合物、背景分子和小型基体簇等模板。
- 增加基于同位素概率和方法特异形成因子的相对风险筛查评分。
- 增加常用无机元素组合，包括用于广谱无机质谱筛查的全元素预设。
- 在现有 `interference()` 和 `standard_ratio()` API 之外新增
  `inorganic_interference()` Python API。
- 增加单元测试套件，覆盖核心分子解析、干扰搜索、无机筛查和数据结构。
- 增加图文用户手册（`docs/USER_MANUAL.md`）。

#### 变更
- 同位素数据库升级为 CIAAW 2024 同位素组成和 AME2020 原子质量，并包含不确定度
  与丰度区间元数据。
- GDMS 默认目标窗口为 `2000 ppm` 全窗口，即以校准目标峰为中心的 `±1000 ppm`。
- 谱图视图使用以目标峰为中心的 `Δppm` 或 `Δm/z` 坐标。
- 代码库现代化到 Python 3.9+。
- 清理并重新生成周期表数据。

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
