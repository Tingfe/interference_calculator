# Changelog / 更新日志

## [2.0.7] - 2026-05-31

### English

#### Changed
- Re-scoped `maintenance/original` as the modern maintenance line for the
  original general calculator instead of an old-code archive.
- Kept the refreshed CIAAW 2024 / AME2020 isotope database, Python 3.9+ support,
  PyQt5 GUI, QPainter spectrum, packaging, and tests.
- Simplified the GUI to the original general isotope-combination scan and
  isotope-ratio workflows.
- Set the general scan default window back to absolute `m/z`, which supports
  open-ended scans without a target peak.
- Updated README, user manual, and help text to describe the branch split:
  `maintenance/original` for general scanning, `main` for the inorganic edition.

#### Removed
- Removed GDMS, ICP-MS, and SIMS presets from this maintenance branch.
- Removed the inorganic template API from this maintenance branch; use `main`
  for `inorganic_interference()` and inorganic-MS workflows.

### 中文

#### 变更
- 将 `maintenance/original` 明确调整为原作者通用计算器的现代化维护线，而不是旧代码归档。
- 保留 CIAAW 2024 / AME2020 同位素数据库、Python 3.9+、PyQt5 GUI、QPainter 谱图、
  打包流程和测试。
- 将 GUI 收窄为原始通用同位素组合扫描和同位素比功能。
- 通用扫描默认窗口恢复为绝对 `m/z`，支持无目标峰的开放式扫描。
- 更新 README、用户手册和帮助文本，明确分支分工：`maintenance/original`
  用于通用扫描，`main` 用于无机专用版。

#### 移除
- 从本维护分支移除 GDMS、ICP-MS 和 SIMS 预设。
- 从本维护分支移除无机模板 API；需要 `inorganic_interference()` 和无机质谱流程时
  使用 `main` 分支。

## [2.0.6] - 2026-05-30

### English

#### Fixed
- Spectrum window on Windows now positions within the visible screen area
  instead of rendering off-screen. The window is clamped to the available screen
  geometry and falls back to vertical stacking if horizontal space is
  insufficient.

#### Changed
- CI workflow installs UPX on macOS and Windows runners to compress final
  executables.
- macOS build uses `--strip` to remove debug symbols.
- Release builds exclude unused PyQt5 submodules to reduce bundled size.

### 中文

#### 修复
- 修复 Windows 下谱图窗口可能显示到屏幕外的问题；窗口会限制在可见屏幕区域内，
  横向空间不足时改为垂直排列。

#### 变更
- CI 在 macOS 和 Windows runner 上安装 UPX，用于压缩最终可执行文件。
- macOS 构建使用 `--strip` 去除调试符号。
- 发布构建排除未使用的 PyQt5 子模块，以降低打包体积。

[2.0.7]: https://github.com/Tingfe/interference_calculator/compare/v2.0.6...maintenance/original
[2.0.6]: https://github.com/Tingfe/interference_calculator/compare/v2.0.5...v2.0.6
