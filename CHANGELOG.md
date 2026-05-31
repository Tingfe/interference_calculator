# Changelog

## [2.1.0] - 2026-05-31

### Added
- Defined the project branch model: `main` is the inorganic-materials
  specialist edition, while the original-function maintenance line is kept for
  conservative refactoring of the upstream-style calculator.
- Completed bilingual coverage for visible GUI text, tooltips, dialogs, status
  messages, filters, element selector controls, and help-related UI paths.
- Added localization regression tests to keep Chinese and English UI keys in
  sync.
- Added an element selector that only offers elements not already selected.
- Added interactive spectrum tools: peak hover details, click-to-select result
  table rows, instrument-MRP unresolved band shading, and PNG export.

### Changed
- Element input now starts empty, uses compact chips, and has a cleaner empty
  state for selecting elements rather than typing long lists.
- Spectrum drawing now uses the Qt default UI font to avoid missing-font alias
  warnings.
- Standalone release builds include Excel export support via `openpyxl`.

### Fixed
- Fixed stale `QThread` references after calculation completion, which could
  crash the GUI on a subsequent calculation.
- Fixed the isotope-ratio view toggle so users can return to interference
  results without recalculating.
- Fixed element-input styling so the inner chip canvas no longer inherits an
  extra border, and removed empty tooltips from the blank element area.
- Fixed Chinese spectrum-window scaling so the target-centered axis respects
  the full GDMS ppm window and MRP band in both languages.

## [2.0.6] - 2026-05-30

### Fixed
- Spectrum window on Windows now positions within the visible screen area
  instead of rendering off-screen (was ~560px past the right edge on 1920px
  displays). The window is clamped to the available screen geometry and falls
  back to vertical stacking if horizontal space is insufficient.


### Changed
- CI workflow now installs UPX on macOS (brew) and Windows (choco) runners
  to compress final executables, reducing download size significantly.
- macOS build uses `--strip` to strip debug symbols from binaries.
- Both builds exclude 30+ unused PyQt5 submodules (Network, WebEngine,
  Multimedia, Qml, Quick, Sql, Xml, etc.) to reduce bundled size.

## [2.0.5] - 2026-05-30

### Changed
- README installation section now features three tiers: standalone app
  (downloadable ``.exe`` / ``.dmg``, no Python required), ``pip install``,
  and source install.
- README running instructions updated accordingly for each installation path.

## [2.0.4] - 2026-05-30

### Added
- GitHub Actions now builds and publishes standalone applications for
  Windows (single ``.exe``) and macOS (``.dmg``) automatically on every
  version tag push.

### Changed
- README usage section now recommends ``pip install`` and the
  ``interference_calculator`` CLI entry point as the primary workflow.

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

[2.1.0]: https://github.com/Tingfe/interference_calculator/compare/v2.0.6...v2.1.0
[2.0.6]: https://github.com/Tingfe/interference_calculator/compare/v2.0.5...v2.0.6
[2.0.5]: https://github.com/Tingfe/interference_calculator/compare/v2.0.4...v2.0.5
[2.0.4]: https://github.com/Tingfe/interference_calculator/compare/v2.0.3...v2.0.4
[2.0.3]: https://github.com/Tingfe/interference_calculator/compare/v2.0.2...v2.0.3
[2.0.2]: https://github.com/Tingfe/interference_calculator/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/Tingfe/interference_calculator/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/Tingfe/interference_calculator/releases/tag/v2.0.0
