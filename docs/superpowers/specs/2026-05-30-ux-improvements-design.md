# UX Improvements for Interference Calculator

**Date:** 2026-05-30
**Version:** 2.1.0 (target)
**Status:** Design — approved

## Overview

Deliver a focused UX upgrade for the interference calculator GUI in a single release.
Four independent modules plus one small polish item discovered during code review.

---

## Module 1 — Data Export

### Goal
Allow users to save calculation results to CSV or Excel files.

### Design

- Add a **Export** `QPushButton` with dropdown menu (`QMenu`) to the bottom action bar, placed next to the existing Calculate / Ratios / Spectrum / Help buttons.
- Menu items:
  - **"Export as CSV…"** — calls `QFileDialog.getSaveFileName()` with filter `CSV Files (*.csv)`, writes currently-displayed DataFrame via `pandas.DataFrame.to_csv()` — zero extra dependencies.
  - **"Export as Excel…"** — calls `QFileDialog.getSaveFileName()` with filter `Excel Files (*.xlsx)`, writes via `pandas.DataFrame.to_excel()` — requires `openpyxl`.

### Dependencies

- `openpyxl` added to `extras_require = {'export': ['openpyxl']}` in `setup.py`.
- The button is always enabled; if the user picks Excel and `openpyxl` is unavailable, show a one-time dialog suggesting `pip install interference-calculator[export]`.

### Files touched

- `interference_calculator/ui.py` — add `export_data()` method, wire button
- `setup.py` / `pyproject.toml` — add `[export]` extras

---

## Module 2 — Calculation Progress Feedback

### Goal
Replace the current single `WaitCursor` with meaningful progress feedback, especially for long-running General Scan computations.

### Design

#### Background worker

- New class `CalculationWorker(QObject)` in `ui.py` (or separate `ui_worker.py`):
  - Signals: `progress(int)`, `finished(pd.DataFrame)`, `error(str)`
  - Slot `run()`: accepts input parameters, performs the calculation, emits `progress` periodically.
- For General Scan mode: estimate total isotope-combination count via `C(n+k-1, k)` where `n` = number of isotopes, `k` = molecule size; emit progress every N iterations.
- For Inorganic template mode (typically <1 second): emit a single `progress(100)` immediately, no need for fine-grained tracking.

#### UI integration

- Status bar area gains a `QProgressBar` (right-aligned, fixed width ~160px, hidden when idle).
- On "Calculate" click:
  1. Read inputs, validate (same as today).
  2. Disable the Calculate button and charge/maxsize/atoms inputs.
  3. Create `QThread` + `CalculationWorker`, move worker to thread.
  4. Connect: `worker.progress → progress_bar.setValue`; `worker.finished → on_calculation_done`; `worker.error → on_calculation_error`.
  5. Start thread.
- On completion (`on_calculation_done`):
  1. Update table, spectrum, summary chips (same as today).
  2. Hide progress bar, re-enable inputs.
  3. Show candidate count in status bar.
- On error: show error dialog, re-enable inputs.

#### Edge cases

- User clicks Calculate while a calculation is already running → ignore (button disabled).
- Calculation finishes after user changed inputs → discard stale result (check a monotonic counter).
- General Scan with no target + maxsize > 6 → warn before starting (already exists today).

### Files touched

- `interference_calculator/ui.py` — add `CalculationWorker` class, modify `calculate_interference()`
- `interference_calculator/main.py` — optionally expose a helper to estimate combination count

---

## Module 3 — Input Experience Enhancements

### Goal
Reduce input friction with auto-completion, real-time validation, and live target preview.

### 3a — Element Auto-completion

- Add `QCompleter` to `ElementInput`:
  - Source list: all 92 element symbols extracted from `periodic_table`.
  - Display: element symbol + name, e.g. `Fe (Iron)`, `Ar (Argon)`.
  - Case-insensitive matching.
  - Completion mode: `QCompleter.PopupCompletion` (popup only, does not auto-fill — user selects explicitly).
- The completer is purely assistive; manual typing remains fully supported.

### 3b — Real-time Input Validation

- Connect `ElementInput.textChanged` → validation callback.
- Parse current text into tokens, check each against `periodic_table`.
  - All valid → normal border (`#cbd5e1`).
  - Any invalid → red border (`#dc2626`) + status bar message "Unknown element: Xx".
- Debounce: 300 ms timer after last keystroke to avoid flicker on every character.
- Add a small inline label "12 elements" (or "12 elements · 1 unknown") next to the input.

### 3c — Target m/z Live Preview

- Connect target `QLineEdit.textChanged` → parser callback.
- Right side of the input field (inside the widget, using a `QLabel` overlay or `setStyleSheet` with padding):
  - Valid formula/number → show `→ 74.9216 m/z` in muted text.
  - Invalid → show nothing or `→ ?`.
- Debounce: 300 ms.

### Files touched

- `interference_calculator/ui.py` — add completer, validation logic, preview label

---

## Module 4 — Result Interaction Enhancements

### Goal
Make the result table more navigable with search/filter and column control.

### 4a — Search / Filter Bar

- Add a `QLineEdit` above the result table (inside the results panel, above `results_stack`).
  - Placeholder: `"Filter results…"` (localized).
  - Search icon inside the field (via `addAction` or stylesheet padding).
- Create a `QSortFilterProxyModel` subclass `InterferenceFilterProxy`:
  - `filterAcceptsRow`: matches the **ion** column against the search text (case-insensitive substring).
  - Supports simple query syntax:
    - `type:oxide` → filter to rows where type column contains "oxide".
    - `risk>0.01` → filter to rows where risk column > 0.01.
    - `m/z>50` → filter to rows where m/z > 50.
    - Multiple tokens: AND logic (row must match all).
  - When no search text → pass all rows.

### 4b — Column Visibility Menu

- Enable `QHeaderView.setContextMenuPolicy(Qt.CustomContextMenu)` on the result table header.
- Connect `customContextMenuRequested` → show a `QMenu` with checkable actions for each column.
- Default-hidden columns (tuned for inorganic MS workflow):
  - `mass uncertainty`
  - `m/z uncertainty`
  - `formation factor`

### 4c — Quick-filter Chips

- The summary chips below the results header become clickable.
- Click "Unresolved: 5" → set filter text to `ok:no` (or `resolved:false`).
- Click "Candidates: 42" → clear filter.
- Chips visually indicate when a filter is active (e.g., highlighted background).

### Files touched

- `interference_calculator/ui.py` — filter proxy, search bar, column menu, chip interactions

---

## Bonus — Column Width Optimization

### Goal
The `ion` / `molecule` column is hard-coded to 190px, which is wider than necessary for most entries.

### Change

- For the `ion` and `molecule` columns only, set `QHeaderView.ResizeToContents`.
- Set a `maxWidth` of ~250px to prevent extremely long adduct formulas from stretching the column beyond the viewport.
- Remove the hard-coded `'ion': 190` entry from the `widths` dict in `resize_table_sections()`.
- Keep all other columns with their existing fixed widths.

---

## Schema & Compatibility

- No changes to the `inorganic_interference()`, `interference()`, or `standard_ratio()` APIs.
- No changes to the periodic table or molecule parser.
- The resulting DataFrame columns are unchanged.

## Implementation Order

The modules are independent and can be developed in any order. Suggested order:

1. **Module 3** (input enhancements) — self-contained, immediately useful, low risk.
2. **Module 1** (export) — also self-contained, adds visible value.
3. **Bonus** (column width) — two-line change, quick win.
4. **Module 4** (result interaction) — moderate complexity, builds on existing TableView.
5. **Module 2** (progress feedback) — highest risk due to threading, best tackled when the rest is stable.

## Testing

- Module 1: manual test exporting CSV/XLSX with various datasets.
- Module 2: manual test with a deliberately slow calculation (General Scan, maxsize=8, no target).
- Module 3: manual test auto-completion and validation with valid/invalid inputs.
- Module 4: manual test filtering, column toggle, chip click.
- Existing `test_core.py` must continue to pass.
