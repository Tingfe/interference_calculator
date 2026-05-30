# UX Improvements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver five independent UX improvements as a single release (v2.1.0).

**Architecture:** All changes live in `interference_calculator/ui.py` (plus a small `setup.py` touch for the optional Excel dependency). No API changes to the core modules. Modules are ordered from simplest/lowest-risk to most complex.

**Tech Stack:** Python 3.9+, PyQt5, pandas, numpy, openpyxl (optional)

**Implementation order:**
1. Module 3 — Input experience (auto-complete, validation, preview)
2. Module 1 — Data export (CSV + Excel)
3. Bonus — Column width optimization
4. Module 4 — Result interaction (filter, column menu, chips)
5. Module 2 — Progress feedback (QThread worker)

---

## File Map

| File | Change | Responsibility |
|------|--------|---------------|
| `interference_calculator/ui.py` | Modify | All UI changes |
| `setup.py` | Modify | Add `[export]` extras for openpyxl |

---

## Task 3.1 — Element Auto-completion

**Files:** `interference_calculator/ui.py`

**Goal:** Add `QCompleter` to the `ElementInput` multi-line text field so users see element suggestions as they type.

### Steps

**Step 3.1.1 — Add `setCompleter()` and completion insertion to `ElementInput`**

Replace the `ElementInput` class in `ui.py`. Change the `__init__` method and add three new methods:

**Change `__init__`** — add `self._completer = None` after the `self.setTabChangesFocus(True)` line:

```python
def __init__(self, parent=None):
    widgets.QPlainTextEdit.__init__(self, parent=parent)
    self.setObjectName('elementsInput')
    self.setLineWrapMode(widgets.QPlainTextEdit.WidgetWidth)
    self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
    self.setMinimumHeight(118)
    self.setMaximumHeight(156)
    if hasattr(self, 'setTabChangesFocus'):
        self.setTabChangesFocus(True)
    self._completer = None
```

**Add three new methods** after `setPlaceholderText`:

```python
def setCompleter(self, completer):
    """Attach a QCompleter to this text edit."""
    if self._completer:
        self._completer.activated.disconnect()
    self._completer = completer
    if completer is None:
        return
    completer.setWidget(self)
    completer.setCompletionMode(widgets.QCompleter.PopupCompletion)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    completer.setFilterMode(QtCore.Qt.MatchContains)
    completer.activated.connect(self._insert_completion)

def _insert_completion(self, completion):
    """Replace the current word with the selected completion."""
    if self._completer.widget() != self:
        return
    # completion is "Fe (Iron)" — extract "Fe"
    symbol = completion.split(' ', 1)[0]
    tc = self.textCursor()
    tc.select(QtGui.QTextCursor.WordUnderCursor)
    tc.removeSelectedText()
    tc.insertText(symbol)
    self.setTextCursor(tc)

def keyPressEvent(self, event):
    if self._completer and self._completer.popup().isVisible():
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return,
                           QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab):
            event.ignore()
            return
    super(ElementInput, self).keyPressEvent(event)
    # Show completer popup for the current word
    if self._completer is None:
        return
    tc = self.textCursor()
    tc.select(QtGui.QTextCursor.WordUnderCursor)
    current_word = tc.selectedText().strip()
    if not current_word:
        self._completer.popup().hide()
        return
    self._completer.setCompletionPrefix(current_word)
    if self._completer.completionCount() > 0:
        self._completer.complete()
    else:
        self._completer.popup().hide()
```

**Step 3.1.2 — Wire the completer in `MainWidget.__init__`**

After `self.element_set_input = widgets.QComboBox(...)` block (around line 1273), add:

```python
# Auto-completion for element symbols
_element_data = periodic_table[['element', 'element name']].drop_duplicates()
_completer_entries = sorted(
    f"{row['element']} ({row['element name']})"
    for _, row in _element_data.iterrows()
)
self._element_completer = widgets.QCompleter(_completer_entries, self)
self.atoms_input.setCompleter(self._element_completer)
```

**Step 3.1.3 — Verify**

Run the GUI:
```bash
cd /Users/tyongs/code/interference_calculator
python -c "from interference_calculator.ui import MainWidget; print('ElementInput completer OK')"
```

No errors means the import and instantiation work. Full visual test requires running the GUI (if a display is available).

---

## Task 3.2 — Real-time Input Validation

**Files:** `interference_calculator/ui.py`

**Goal:** Validate element input as the user types: red border on invalid tokens, element count label.

### Steps

**Step 3.2.1 — Add validation timer, count label, and `_debounced_validate` slot**

In `MainWidget.__init__`, after the `self.atoms_input = ElementInput(parent=self)` line, add:

```python
self.atoms_input.setObjectName('elementsInput')
self._elements_validation_timer = QtCore.QTimer(self)
self._elements_validation_timer.setSingleShot(True)
self._elements_validation_timer.setInterval(300)
self._elements_validation_timer.timeout.connect(self._validate_elements_input)
self.atoms_input.textChanged.connect(self._elements_validation_timer.start)
```

After `add_set_label` creation (around line 1440), add an element count label inside the atoms group:

```python
self.elements_count_label = widgets.QLabel(parent=self.atoms_group)
self.elements_count_label.setObjectName('helperText')
self.elements_count_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
```

Then add it to the layout after `self.atoms_layout.addWidget(self.atoms_input)`:

```python
self.atoms_layout.addWidget(self.atoms_input)
self.atoms_layout.addWidget(self.elements_count_label)  # NEW
```

**Step 3.2.2 — Add `_validate_elements_input` method**

Add to `MainWidget` (before `resize_table_sections`):

```python
def _validate_elements_input(self):
    """Check element input for invalid tokens; update border and count label."""
    text = self.atoms_input.text()
    tokens = re.findall(_isotope_rx, text) if text.strip() else []
    invalid = []
    valid_count = 0
    for t in tokens:
        if (periodic_table['element'] == t).any():
            valid_count += 1
        else:
            invalid.append(t)

    # Update border
    stylesheet = self.atoms_input.styleSheet()
    if invalid:
        self.atoms_input.setStyleSheet(
            "QPlainTextEdit#elementsInput { border: 2px solid #dc2626; }"
        )
    elif tokens:
        self.atoms_input.setStyleSheet("")
    else:
        self.atoms_input.setStyleSheet("")

    # Update count label
    lang = self.language
    if invalid:
        msg = _text(lang, 'missing_element').format(invalid[0])
        self.elements_count_label.setText(
            f"{valid_count} elements · {msg}"
        )
        self.elements_count_label.setStyleSheet("color: #dc2626; font-size: 11px;")
    elif valid_count > 0:
        self.elements_count_label.setText(
            f"{valid_count} elements"
        )
        self.elements_count_label.setStyleSheet("color: #64748b; font-size: 11px;")
    else:
        self.elements_count_label.setText("")
```

**Step 3.2.3 — Verify**

```bash
cd /Users/tyongs/code/interference_calculator
python -c "
from interference_calculator.ui import MainWidget
from interference_calculator.molecule import periodic_table
print('Elements:', periodic_table['element'].nunique())
print('Validation module loads OK')
"
```

---

## Task 3.3 — Target m/z Live Preview

**Files:** `interference_calculator/ui.py`

**Goal:** Show a live `→ 74.9216 m/z` preview next to the target input.

### Steps

**Step 3.3.1 — Add preview label and timer**

In `MainWidget.__init__`, after `self.mz_input = widgets.QLineEdit(parent=self)`, add:

```python
self._mz_preview_label = widgets.QLabel(parent=self)
self._mz_preview_label.setObjectName('helperText')
self._mz_preview_timer = QtCore.QTimer(self)
self._mz_preview_timer.setSingleShot(True)
self._mz_preview_timer.setInterval(300)
self._mz_preview_timer.timeout.connect(self._update_mz_preview)
self.mz_input.textChanged.connect(self._mz_preview_timer.start)
```

In the workflow layout, after `self.workflow_layout.addWidget(self.mz_input, 1, 1, 1, 2)` (around line 1390), we need to break this into its own row or place the preview alongside. Instead of the current spanning approach, change to:

```python
self.workflow_layout.addWidget(self.target_label, 1, 0)
self.target_mz_container = widgets.QHBoxLayout()
self.target_mz_container.setSpacing(4)
self.target_mz_container.addWidget(self.mz_input, stretch=1)
self.target_mz_container.addWidget(self._mz_preview_label)
self.workflow_layout.addLayout(self.target_mz_container, 1, 1, 1, 2)
```

**Step 3.3.2 — Add `_update_mz_preview` method**

Add to `MainWidget`:

```python
def _update_mz_preview(self):
    """Parse the target input and show m/z preview."""
    text = self.mz_input.text().strip()
    if not text:
        self._mz_preview_label.setText('')
        return
    try:
        # Try numeric
        mz = float(text)
        self._mz_preview_label.setText(f'→ {mz:.4f} m/z')
        self._mz_preview_label.setStyleSheet("color: #64748b; font-size: 11px;")
        return
    except ValueError:
        pass
    try:
        # Try molecule
        charges, chargesign = _current_data(self.charge_preset_input)
        if not chargesign:
            chargesign = '+'
        m = Molecule(text)
        if not m.charge and chargesign not in ('o', '0'):
            if charges[0] == 1:
                target = f'{text} {chargesign}'
            else:
                target = f'{text} {charges[0]}{chargesign}'
            m = Molecule(target)
        mz = m.mass / m.charge if m.charge else m.mass
        self._mz_preview_label.setText(f'→ {mz:.4f} m/z')
        self._mz_preview_label.setStyleSheet("color: #64748b; font-size: 11px;")
    except Exception:
        self._mz_preview_label.setText('→ ?')
        self._mz_preview_label.setStyleSheet("color: #dc2626; font-size: 11px;")
```

**Step 3.3.3 — Verify**

```bash
cd /Users/tyongs/code/interference_calculator
python -c "
from interference_calculator.molecule import Molecule
m = Molecule('75As +')
print(f'm/z = {m.mass / m.charge:.6f}')  # Should print ~74.92
print('m/z preview logic OK')
"
```

---

## Task 1.1 — Data Export Button + CSV

**Files:** `interference_calculator/ui.py`

**Goal:** Add an Export button with dropdown to the action bar; implement CSV export.

### Steps

**Step 1.1.1 — Add export button to the action bar**

In `MainWidget.__init__`, after `self.help_button = widgets.QToolButton(...)` block (around line 1327), add:

```python
self.export_button = widgets.QPushButton('Export ▾', parent=self)
self.export_menu = widgets.QMenu(self)
self.export_menu.addAction('CSV…', self.export_csv)
self.export_menu.addAction('Excel…', self.export_xlsx)
self.export_button.setMenu(self.export_menu)
```

In the button layout (`self.button_layout`), add it after `self.standard_ratio_button`:

```python
self.button_layout.addWidget(self.interference_button, stretch=1)
self.button_layout.addWidget(self.standard_ratio_button)
self.button_layout.addWidget(self.export_button)       # NEW
self.button_layout.addWidget(self.spectrum_button)
self.button_layout.addWidget(self.help_button)
```

**Step 1.1.2 — Add `export_csv` method**

Add to `MainWidget`:

```python
def export_csv(self):
    """Export current result table as CSV."""
    model = self.table_output.model()
    if model is None or model.rowCount() == 0:
        self.set_status('No data to export.')
        return
    df = model._data
    path, _ = widgets.QFileDialog.getSaveFileName(
        self, 'Export CSV', '', 'CSV Files (*.csv)'
    )
    if not path:
        return
    try:
        df.to_csv(path, index=False)
        self.set_status(f'Exported {len(df)} rows to {path}')
    except Exception as e:
        widgets.QMessageBox.critical(self, 'Export Error', str(e))
```

**Step 1.1.3 — Wire keyboard shortcut**

In `keyPressEvent`, add a handler for Ctrl+E:

```python
elif (key == QtCore.Qt.Key_E and mod == QtCore.Qt.ControlModifier):
    self.export_csv()
```

**Step 1.1.4 — Add localization for export strings**

In `_UI_TEXT` dict, add to both 'en' and 'zh' sections:

For 'en':
```python
'export': 'Export',
'export_csv': 'Export as CSV…',
'export_xlsx': 'Export as Excel…',
'export_no_data': 'No data to export.',
```

For 'zh':
```python
'export': '导出',
'export_csv': '导出为 CSV…',
'export_xlsx': '导出为 Excel…',
'export_no_data': '没有数据可导出。',
```

**Step 1.1.5 — Update `apply_language`**

In `apply_language()`, add:
```python
self.export_button.setText(self._tr('export'))
self.export_menu.actions()[0].setText(self._tr('export_csv'))
self.export_menu.actions()[1].setText(self._tr('export_xlsx'))
```

---

## Task 1.2 — Excel Export

**Files:** `interference_calculator/ui.py`, `setup.py`

**Goal:** Implement Excel export via pandas + openpyxl.

### Steps

**Step 1.2.1 — Add `export_xlsx` method**

Add to `MainWidget` right after `export_csv`:

```python
def export_xlsx(self):
    """Export current result table as Excel (.xlsx)."""
    model = self.table_output.model()
    if model is None or model.rowCount() == 0:
        self.set_status(self._tr('export_no_data'))
        return
    try:
        import openpyxl  # noqa: F401 — verify available
    except ImportError:
        reply = widgets.QMessageBox.question(
            self, 'Missing dependency',
            'Excel export requires openpyxl.\n\n'
            'Install: pip install interference-calculator[export]\n\n'
            'Continue with CSV instead?',
            widgets.QMessageBox.Yes | widgets.QMessageBox.No
        )
        if reply == widgets.QMessageBox.Yes:
            self.export_csv()
        return
    df = model._data
    path, _ = widgets.QFileDialog.getSaveFileName(
        self, 'Export Excel', '', 'Excel Files (*.xlsx)'
    )
    if not path:
        return
    try:
        df.to_excel(path, index=False, engine='openpyxl')
        self.set_status(f'Exported {len(df)} rows to {path}')
    except Exception as e:
        widgets.QMessageBox.critical(self, 'Export Error', str(e))
```

**Step 1.2.2 — Update `setup.py` extras**

Add `'openpyxl'` to the export extras in `setup.py`:

```python
extras_require = {
    'data': ['requests'],
    'export': ['openpyxl'],    # NEW
},
```

---

## Task B.1 — Column Width Optimization

**Files:** `interference_calculator/ui.py`

**Goal:** Change ion/molecule column to `ResizeToContents` with max width cap.

### Steps

**Step B.1.1 — Change resize mode in `resize_table_sections`**

In `resize_table_sections()`, after the existing loop that sets resize mode for all columns, add:

```python
# Let the ion/molecule column resize to content with a max-width cap
for column in range(model.columnCount()):
    colname = model._data.columns[column]
    if colname in ('ion', 'molecule'):
        try:
            header.setSectionResizeMode(column, widgets.QHeaderView.ResizeToContents)
        except AttributeError:
            header.setResizeMode(column, widgets.QHeaderView.ResizeToContents)
```

Also change the width for 'ion' from 190 to a smaller default:
```python
widths = {
    'molecule': 160,   # was 190
    'ion': 160,        # was 190
    ...
}
```

---

## Task 4.1 — Search / Filter Bar

**Files:** `interference_calculator/ui.py`

**Goal:** Add a filter bar above the results table using `QSortFilterProxyModel`.

### Steps

**Step 4.1.1 — Add `InterferenceFilterProxy` class**

Add to the top of `ui.py`, after the `_SpectrumCanvas` class (or before `MainWindow`):

```python
class InterferenceFilterProxy(QtCore.QSortFilterProxyModel):
    """Filter proxy supporting simple query syntax: type:oxide risk>0.01"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_text = ''

    def set_filter_text(self, text):
        self._filter_text = text.strip()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self._filter_text:
            return True
        model = self.sourceModel()
        if model is None:
            return True

        tokens = self._filter_text.split()
        for token in tokens:
            # Check for column:value syntax
            colon = token.find(':')
            if colon > 0:
                col_key = token[:colon]
                col_val = token[colon+1:]
                # Find matching column
                matched = False
                for col in range(model.columnCount()):
                    hdr = model.headerData(col, QtCore.Qt.Horizontal).lower()
                    if col_key.lower() in hdr:
                        idx = model.index(source_row, col)
                        cell = model.data(idx, QtCore.Qt.DisplayRole)
                        if cell and col_val.lower() in str(cell).lower():
                            matched = True
                            break
                if not matched:
                    return False
                continue

            # Check for column>value syntax
            gt = max(token.find('>'), token.find('≥'))
            if gt > 0:
                col_key = token[:gt]
                col_val_str = token[gt+1:]
                try:
                    col_val = float(col_val_str)
                except ValueError:
                    return False
                matched = False
                for col in range(model.columnCount()):
                    hdr = model.headerData(col, QtCore.Qt.Horizontal).lower()
                    if col_key.lower() in hdr:
                        idx = model.index(source_row, col)
                        raw = model.data(idx, QtCore.Qt.EditRole)
                        if raw is not None:
                            try:
                                cell_val = float(raw)
                                if cell_val > col_val:
                                    matched = True
                            except (ValueError, TypeError):
                                pass
                            break
                if not matched:
                    return False
                continue

            # Check for column<value syntax
            lt = max(token.find('<'), token.find('≤'))
            if lt > 0:
                col_key = token[:lt]
                col_val_str = token[lt+1:]
                try:
                    col_val = float(col_val_str)
                except ValueError:
                    return False
                matched = False
                for col in range(model.columnCount()):
                    hdr = model.headerData(col, QtCore.Qt.Horizontal).lower()
                    if col_key.lower() in hdr:
                        idx = model.index(source_row, col)
                        raw = model.data(idx, QtCore.Qt.EditRole)
                        if raw is not None:
                            try:
                                cell_val = float(raw)
                                if cell_val < col_val:
                                    matched = True
                            except (ValueError, TypeError):
                                pass
                            break
                if not matched:
                    return False
                continue

            # Default: match against the first column (ion/molecule)
            idx0 = model.index(source_row, 0)
            cell0 = model.data(idx0, QtCore.Qt.DisplayRole)
            if cell0 is None or token.lower() not in str(cell0).lower():
                return False

        return True
```

**Step 4.1.2 — Add search bar widget**

In `MainWidget.__init__`, after `self.results_header` setup and before `self.empty_state`, insert:

```python
self.filter_bar = widgets.QLineEdit(parent=self.results_panel)
self.filter_bar.setPlaceholderText('Filter results…')
self.filter_bar.setClearButtonEnabled(True)
self.filter_bar.textChanged.connect(self._apply_filter)
self.filter_bar.hide()  # hidden until there are results
```

Wire it into the layout after results_header:

```python
self.results_layout.addWidget(self.results_header)
self.results_layout.addWidget(self.filter_bar)   # NEW
self.results_layout.addWidget(self.results_stack, stretch=1)
```

**Step 4.1.3 — Add `_apply_filter` method**

Add to `MainWidget`:

```python
def _apply_filter(self, text):
    proxy = self.table_output.model()
    if isinstance(proxy, InterferenceFilterProxy):
        proxy.set_filter_text(text)
```

**Step 4.1.4 — Wire proxy into `calculate_interference`**

In `calculate_interference()`, after creating the model and setting it on the table:

Replace:
```python
model = TableModel(display_data, table='interference', language=self.language)
self.table_output.setModel(model)
```

With:
```python
source_model = TableModel(display_data, table='interference', language=self.language)
proxy = InterferenceFilterProxy(self)
proxy.setSourceModel(source_model)
proxy.set_filter_text(self.filter_bar.text())
self.table_output.setModel(proxy)
```

Also in `show_standard_ratio()`, replace the setModel call similarly.

**Step 4.1.5 — Show filter bar when results exist**

In `calculate_interference()`, after `self.results_stack.setCurrentWidget(self.table_output)`, add:
```python
self.filter_bar.show()
```

In `apply_language()` (or at init), set the placeholder:
```python
self.filter_bar.setPlaceholderText(self._tr('filter_results'))
```

Add `'filter_results': 'Filter results…'` to `_UI_TEXT['en']` and `'filter_results': '筛选结果…'` to `_UI_TEXT['zh']`.

---

## Task 4.2 — Column Visibility Context Menu

**Files:** `interference_calculator/ui.py`

**Goal:** Right-click on table header to show/hide columns.

### Steps

**Step 4.2.1 — Enable context menu on header**

In `MainWidget.__init__`, after `self.table_output = TableView(html_cols=None)`, add:

```python
self.table_output.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
self.table_output.horizontalHeader().customContextMenuRequested.connect(
    self._show_column_menu
)
```

**Step 4.2.2 — Add `_show_column_menu` method**

Add to `MainWidget`:

```python
def _show_column_menu(self, pos):
    header = self.table_output.horizontalHeader()
    menu = widgets.QMenu(self)
    model = self.table_output.model()
    if model is None:
        return
    # Get the source model if using a proxy
    source = model.sourceModel() if isinstance(model, InterferenceFilterProxy) else model
    if source is None:
        return
    for col in range(source.columnCount()):
        colname = source._data.columns[col]
        display = _column_display(self.language, colname)
        action = menu.addAction(display)
        action.setCheckable(True)
        # Find visual column index (in case of proxy)
        vis_col = col
        action.setChecked(not header.isSectionHidden(vis_col))
        action.toggled.connect(lambda checked, c=vis_col: header.setSectionHidden(c, not checked))
    menu.exec_(header.mapToGlobal(pos))
```

---

## Task 4.3 — Quick-filter Chips

**Files:** `interference_calculator/ui.py`

**Goal:** Clicking a summary chip sets/clears the filter.

### Steps

**Step 4.3.1 — Make chips clickable and store references**

In `MainWidget.__init__`, after the metric labels are created:

```python
self.mode_metric_label = self.create_metric_label(parent=self.results_header)
self.window_metric_label = self.create_metric_label(parent=self.results_header)
self.mrp_metric_label = self.create_metric_label(parent=self.results_header)
self.count_metric_label = self.create_metric_label(parent=self.results_header)
```

Store them for chip interaction. Make the count chip clickable after creation (in `update_result_summary` or via a dedicated method). Add:

After `update_result_summary` is first called (end of `__init__`), connect the chip:

```python
self.count_metric_label.mousePressEvent = lambda e: self._on_chip_click(e)
self.count_metric_label.setCursor(QtCore.Qt.PointingHandCursor)
```

**Step 4.3.2 — Add `_on_chip_click` method**

```python
def _on_chip_click(self, event):
    """Toggle filter between 'unresolved only' and 'all'."""
    if self.filter_bar.text():
        self.filter_bar.setText('')
    else:
        self.filter_bar.setText('ok:no')
```

**Step 4.3.3 — Mark chip as active when filter is on**

In `_apply_filter`, add visual feedback:

```python
def _apply_filter(self, text):
    proxy = self.table_output.model()
    if isinstance(proxy, InterferenceFilterProxy):
        proxy.set_filter_text(text)
    # Update chip highlight
    if text:
        self.count_metric_label.setStyleSheet(
            "background: #fef3c7; color: #92400e; border: 1px solid #f59e0b;"
            " border-radius: 4px; padding: 4px 8px; font-size: 12px; font-weight: 500;"
        )
    else:
        self.count_metric_label.setStyleSheet("")
```

---

## Task 2.1 — Calculation Worker (QThread)

**Files:** `interference_calculator/ui.py`

**Goal:** Move calculation to a background thread with progress feedback.

### Steps

**Step 2.1.1 — Add `CalculationWorker` class**

Add to `ui.py` before `MainWindow` class:

```python
class CalculationWorker(QtCore.QObject):
    """Run interference calculation in a background thread."""
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(str)

    def __init__(self, atoms, mz, mzrange, maxsize, charges, chargesign,
                 risk_preset, instrument_mrp):
        super().__init__()
        self.atoms = atoms
        self.mz = mz
        self.mzrange = mzrange
        self.maxsize = maxsize
        self.charges = charges
        self.chargesign = chargesign
        self.risk_preset = risk_preset
        self.instrument_mrp = instrument_mrp
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            self.progress.emit(5)
            from interference_calculator.inorganic import inorganic_interference
            from interference_calculator.main import interference
            import numpy as np
            import pandas as pd

            if self._cancel:
                return

            if self.risk_preset:
                data = inorganic_interference(
                    self.atoms, self.mz, targetrange=self.mzrange,
                    maxsize=self.maxsize, charge=self.charges,
                    chargesign=self.chargesign, risk_preset=self.risk_preset,
                )
            else:
                data = interference(
                    self.atoms, self.mz, targetrange=self.mzrange,
                    maxsize=self.maxsize, charge=self.charges,
                    chargesign=self.chargesign,
                )
                data['type'] = 'enumerated'
                data['formation factor'] = ''
                data['relative risk'] = data['probability']

            if self._cancel:
                return
            self.progress.emit(50)

            # Compute Δppm and resolved columns
            target_mask = data['target'].astype(bool)
            if target_mask.any():
                target_mz = data.loc[target_mask, 'mass/charge'].iat[0]
            else:
                target_mz = np.nan

            if target_mz:
                data['Δppm'] = data['mass/charge diff'] / target_mz * 1e6
            else:
                data['Δppm'] = np.nan

            if self.instrument_mrp:
                data['resolved'] = (data['MRP'] <= self.instrument_mrp).astype(object)
                data.loc[target_mask, 'resolved'] = ''
            else:
                data['resolved'] = ''

            data.index = range(1, data.shape[0] + 1)

            # Build display DataFrame
            display_data = data[['molecule', 'type', 'charge', 'mass/charge',
                                 'mass/charge diff', 'Δppm', 'MRP',
                                 'probability', 'relative risk', 'resolved',
                                 'target']].copy()
            display_data.columns = ['ion', 'type', 'z', 'm/z', 'Δm/z',
                                    'Δppm', 'MRP', 'prob.', 'risk', 'ok',
                                    'target']

            self.progress.emit(90)

            # Attach spectrum metadata
            spectrum_data = data.copy()
            spectrum_data.attrs['window_half_mz'] = float(self.mzrange)
            if target_mz and np.isfinite(target_mz):
                spectrum_data.attrs['window_half_ppm'] = float(
                    self.mzrange / target_mz * 1e6
                )

            result = {
                'display_data': display_data,
                'spectrum_data': spectrum_data,
                'candidate_count': int((~display_data['target'].astype(bool)).sum()),
                'unresolved_count': int(
                    sum((v != '') and not bool(v) for v in display_data['ok'])
                ),
            }
            self.progress.emit(100)
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))
```

**Step 2.1.2 — Update `calculate_interference` to use the worker**

Replace the current `calculate_interference` method:

```python
@QtCore.pyqtSlot()
def calculate_interference(self):
    if not (self.check_atoms_input() and
            self.check_charges_input() and
            self.check_mz_input()):
        return

    if not self.mz:
        qmsg = widgets.QMessageBox(self)
        qmsg.setText(self._tr('long_warning'))
        qmsg.setInformativeText(mz_warning_for(self.language))
        qmsg.setIcon(widgets.QMessageBox.Warning)
        qmsg.setStandardButtons(widgets.QMessageBox.Ok | widgets.QMessageBox.Cancel)
        if qmsg.exec_() == widgets.QMessageBox.Cancel:
            return

    self.maxsize = self.maxsize_input.value()
    self.mzrange = self.targetrange_mz()
    if self.mzrange is None:
        return

    risk_preset = _current_data(self.mode_input)

    # Disable inputs during calculation
    self.interference_button.setEnabled(False)
    self.standard_ratio_button.setEnabled(False)
    self._progress_bar = widgets.QProgressBar(self.statusbar)
    self._progress_bar.setMaximumWidth(160)
    self._progress_bar.setRange(0, 0)  # indeterminate
    self.statusbar.addPermanentWidget(self._progress_bar)
    self.set_status('Calculating…')

    # Setup worker thread
    self._calc_thread = QtCore.QThread(self)
    self._calc_worker = CalculationWorker(
        self.atoms, self.mz, self.mzrange, self.maxsize,
        self.charges, self.chargesign, risk_preset,
        self.instrument_mrp_input.value(),
    )
    self._calc_worker.moveToThread(self._calc_thread)
    self._calc_thread.started.connect(self._calc_worker.run)
    self._calc_worker.finished.connect(self._on_calc_finished)
    self._calc_worker.error.connect(self._on_calc_error)
    self._calc_worker.progress.connect(self._on_calc_progress)
    self._calc_worker.finished.connect(self._calc_thread.quit)
    self._calc_worker.finished.connect(self._calc_worker.deleteLater)
    self._calc_thread.finished.connect(self._calc_thread.deleteLater)
    self._calc_thread.start()
```

**Step 2.1.3 — Add result/error/progress handlers**

Add to `MainWidget`:

```python
def _on_calc_finished(self, result):
    """Handle completed calculation from worker thread."""
    display_data = result['display_data']
    spectrum_data = result['spectrum_data']

    source_model = TableModel(
        display_data, table='interference', language=self.language
    )
    proxy = InterferenceFilterProxy(self)
    proxy.setSourceModel(source_model)
    proxy.set_filter_text(self.filter_bar.text())
    self.table_output.setModel(proxy)
    self.table_output.setColumnHidden(
        display_data.columns.get_loc('target'), True
    )
    self.resize_table_sections()

    self.result_metrics = {
        'kind': 'interference',
        'candidate_count': result['candidate_count'],
        'unresolved_count': result['unresolved_count'],
    }
    self.results_stack.setCurrentWidget(self.table_output)
    self.filter_bar.show()
    self.update_result_summary()
    self.spectrum_window.plot_spectrum(spectrum_data)
    self.set_status(
        self._tr('candidate_count').format(result['candidate_count']),
        time=5000,
    )

    # Re-enable inputs
    self.interference_button.setEnabled(True)
    self.standard_ratio_button.setEnabled(True)
    self.statusbar.removeWidget(self._progress_bar)
    self._progress_bar = None

def _on_calc_error(self, msg):
    widgets.QMessageBox.critical(self, 'Calculation Error', msg)
    self.interference_button.setEnabled(True)
    self.standard_ratio_button.setEnabled(True)
    if self._progress_bar:
        self.statusbar.removeWidget(self._progress_bar)
        self._progress_bar = None

def _on_calc_progress(self, value):
    if self._progress_bar:
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(value)
```

---

## Verification

After all tasks, run the existing test suite:

```bash
cd /Users/tyongs/code/interference_calculator
python -m pytest tests/ -v
```

Expected output: all tests pass (no regressions on the core API).

Verify the GUI loads without import errors:

```bash
python -c "
from interference_calculator.ui import MainWidget, MainWindow, run
from interference_calculator import interference, standard_ratio, inorganic_interference
print('All modules import OK')
"
```
