# Changelog / 更新日志

本更新日志面向最终用户，重点说明使用体验、功能能力、稳定性和发布渠道变化。
内部实现细节、CI 机制和测试项保留在提交历史与发布文档中。

This changelog focuses on product changes that matter to users. Internal
implementation details, CI mechanics, and test-only changes are kept in commit
history and release documentation.

## [Unreleased]

### 中文

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

[Unreleased]: https://github.com/Tingfe/interference_calculator/compare/v2.5.0...HEAD
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
