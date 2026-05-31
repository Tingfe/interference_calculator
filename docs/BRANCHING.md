# Branching Model / 分支模型

This repository has two long-lived product lines.

本仓库维护两条长期产品线。

## `maintenance/original`

This branch is the modern maintenance line for the original calculator. It keeps
general isotope-combination scanning and isotope-ratio calculation, while using
the refreshed isotope database, Python 3.9+, PyQt5, modern packaging, and tests.

本分支是原作者通用计算器的现代化维护线。它保留通用同位素组合扫描和同位素比计算，
同时使用更新后的同位素数据库、Python 3.9+、PyQt5、现代打包流程和测试。

Scope:

- General `interference()` calculation.
- Standard `standard_ratio()` calculation.
- Modernized data, dependencies, packaging, and compatibility fixes.
- No inorganic-materials-specific presets, templates, or risk models.

范围：

- 通用 `interference()` 计算。
- 标准 `standard_ratio()` 计算。
- 现代化数据、依赖、打包和兼容性维护。
- 不包含无机材料专项预设、模板或风险模型。

## `main`

`main` is the inorganic-materials specialist edition for GDMS, ICP-MS, and SIMS.
It carries the dedicated inorganic interference templates, instrument presets,
relative-risk scoring, and the main release line.

`main` 是面向 GDMS、ICP-MS 和 SIMS 的无机材料专用版，包含无机干扰模板、仪器预设、
相对风险评分和默认发布流程。

## Practical Rule / 实际规则

General calculator maintenance goes to `maintenance/original`; inorganic-MS
features go to `main`. Shared bug fixes should be cherry-picked deliberately.

通用计算器维护进入 `maintenance/original`；无机质谱专项功能进入 `main`。
两边都需要的修复应有意识地 cherry-pick。
