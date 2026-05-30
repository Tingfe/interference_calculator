# Changelog

## [2.0.3] - 2026-05-30

### Added
- Application icon files rendered from the same vector source: `icon.ico`
  (Windows, 16/32/48/256 px) and `icon.icns` (macOS, up to 1024 px).

## [2.0.2] - 2026-05-30

### Changed
- Lazy-load numpy and pandas to reduce GUI startup time (~3x faster).
- Replaced matplotlib-based spectrum view with a native Qt QPainter
  implementation, removing the ~20 MB matplotlib dependency entirely.
  The spectrum retains all features: log-scale stem plot, 3-colour
  category display (candidate / unresolved / target), peak annotations,
  zoom (mouse wheel), and bilingual labels.

### Removed
- matplotlib dependency (replaced by built-in Qt painting).

### Fixed
- The spectrum window is always available; no external plotting library
  required.

## [2.0.1] - 2026-05-30

### Fixed
- Enable PyQt5 high-DPI auto-scaling (`AA_EnableHighDpiScaling`) so text and
  controls render at readable sizes on 2K/4K displays.

### Changed
- README is now bilingual Chinese/English with Chinese as the default language
  and in-page language switcher links.
- CI: simplified GitHub Actions release workflow to build cross-platform sdist
  and wheel instead of per-platform PyInstaller executables.

## [2.0.0] - 2026-05-30

### Added
- Modern PyQt5 GUI with bilingual (Chinese/English) switching, result summary
  chips, empty-state guidance, compact data-dense result table, and a
  target-centered spectrum view.
- GDMS, ICP-MS, and SIMS instrument presets with practical defaults for charge
  state, target window, risk model, and mass resolving power.
- Inorganic mass-spectrometry algorithm using interference templates for atomic
  ions, doubly charged ions, oxides, hydrides, hydroxides, nitrides, carbides,
  sulfides, halides, plasma adducts, background molecules, and small matrix
  clusters.
- `relative risk` screening score based on isotope probability and
  method-specific formation factors.
- Common inorganic element sets, including an all-elements preset for broad
  inorganic MS screening.
- `inorganic_interference()` Python API alongside the existing `interference()`
  and `standard_ratio()` APIs.
- Unit test suite (`tests/`) covering core molecule parsing, interference
  search, inorganic screening, and data schema.
- Illustrated user manual (`docs/USER_MANUAL.md`).

### Changed
- Upgraded the isotope database to CIAAW 2024 isotopic compositions and AME2020
  atomic masses, including uncertainty and abundance-interval metadata.
- GDMS default target window is `2000 ppm` (full window), i.e. `±1000 ppm` about
  the calibrated target peak.
- The spectrum view uses `Δppm` or `Δm/z` centered on the target peak.
- Modernised the codebase to Python 3.9+.
- Periodic table data cleaned up and re-generated.

[2.0.2]: https://github.com/Tingfe/interference_calculator/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/Tingfe/interference_calculator/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/Tingfe/interference_calculator/releases/tag/v2.0.0
