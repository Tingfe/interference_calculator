# Branching Model / 分支模型

This project now has two long-lived product lines.

本项目现在维护两条长期产品线。

## `main` - Inorganic Materials Edition

`main` is the default branch and release branch. It is the modern inorganic
mass-spectrometry tool for GDMS, ICP-MS, and SIMS workflows.

`main` 是默认分支和发布分支。它面向 GDMS、ICP-MS 和 SIMS 等无机质谱 /
无机材料峰干扰筛查场景。

Scope:

- Bilingual PyQt GUI.
- GDMS, ICP-MS, and SIMS presets.
- Inorganic interference templates and relative-risk scoring.
- CIAAW 2024 / AME2020 isotope database.
- Target-centered spectrum view with peak hover details, click-to-table
  selection, MRP unresolved band, and PNG export.
- Windows and macOS standalone application releases.

范围：

- 中英文 PyQt 图形界面。
- GDMS、ICP-MS、SIMS 预设。
- 无机质谱干扰模板和相对风险评分。
- CIAAW 2024 / AME2020 同位素数据库。
- 目标峰居中的交互式谱图，支持峰详情、点击定位表格、MRP 未分辨区和 PNG 导出。
- Windows 与 macOS 免安装软件发布。

## `maintenance/original` - Original Function Maintenance

`maintenance/original` keeps the original calculator's product boundary. It is
for conservative refactoring and maintainability work around the upstream-style
general molecular enumeration and isotope-ratio features.

`maintenance/original` 保留原作者软件的功能边界，主要用于对原始通用分子组合
枚举和同位素比功能进行保守的可维护重构。

Scope:

- Preserve original general interference calculation behavior.
- Preserve standard isotope-ratio workflows.
- Avoid adding inorganic-materials-specific presets, templates, or GUI concepts.
- Accept bug fixes, compatibility updates, tests, and internal refactoring.

范围：

- 保留原始通用干扰计算行为。
- 保留标准同位素比功能。
- 不加入无机材料专用预设、模板或 GUI 概念。
- 接收 bug 修复、兼容性更新、测试和内部重构。

## Practical Rules

- Features for GDMS / inorganic materials go to `main`.
- Refactors meant to keep the original calculator maintainable go to
  `maintenance/original`.
- Fixes that apply to both lines should be cherry-picked deliberately.
- Releases are cut from `main` unless a maintenance release is explicitly
  needed for `maintenance/original`.

## 实际规则

- GDMS / 无机材料专项功能进入 `main`。
- 仅用于维护原始计算器的重构进入 `maintenance/original`。
- 两条线都需要的修复应有意识地 cherry-pick，而不是自动混入功能差异。
- 默认从 `main` 发布；只有明确需要时才从 `maintenance/original` 发布维护版本。
