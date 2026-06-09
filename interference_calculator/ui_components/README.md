# UI Components Package

This package contains modular UI components extracted from the main `ui.py` file to improve maintainability and enable independent testing.

## Architecture

The `ui_components` package provides a modular architecture for the interference calculator's user interface:

```
ui_components/
├── __init__.py          # Package exports
├── table.py             # TableModel, TableView, HTMLDelegate
├── element_input.py     # ElementInput widget
├── filter_proxy.py      # InterferenceFilterProxy
├── worker.py            # CalculationWorker
└── utils.py             # Shared utility functions
```

## Components

### Table Components (`table.py`)
- **TableModel**: QAbstractTableModel backed by pandas DataFrame for displaying calculation results
- **TableView**: QTableView with HTML support, sorting, and context menu
- **HTMLDelegate**: Item delegate for rendering HTML-formatted chemical formulas in table cells

### Element Input (`element_input.py`)
- **ElementInput**: Chip-based widget for selecting chemical elements with:
  - Interactive add/remove chips
  - Element picker dialog with search
  - Periodic table ordering
  - Language support (Chinese/English)

### Filter Proxy (`filter_proxy.py`)
- **InterferenceFilterProxy**: QSortFilterProxyModel with advanced query syntax:
  - Plain text search across all columns
  - Column-specific filters: `col:value`, `col=value`
  - Numeric comparisons: `col>10`, `col<=5`
  - Regex matching: `col~pattern`
  - Negation: `-term`
  - OR logic: `term1|term2`

### Worker (`worker.py`)
- **CalculationWorker**: QObject designed for QThread execution
  - Non-blocking interference calculations
  - Progress reporting via signals
  - Error handling
  - Cancellation support

### Utilities (`utils.py`)
- **_text()**: Localized text retrieval
- **_type_display()**: Localized type display strings
- **_column_display()**: Localized column headers
- **_ui_font()**: QFont helper

## Usage

### Import from ui_components (recommended for new code)

```python
from interference_calculator.ui_components import (
    TableModel,
    TableView,
    ElementInput,
    InterferenceFilterProxy,
    CalculationWorker,
)

# Use components independently
model = TableModel(data, table='interference', language='en')
view = TableView()
view.setModel(model)
```

### Import from ui module (backward compatible)

```python
from interference_calculator.ui import (
    TableModel,
    TableView,
    ElementInput,
    InterferenceFilterProxy,
    CalculationWorker,
)
# All components still available in ui.py for backward compatibility
```

Both approaches work identically. The `ui_components` package is the preferred way for new development as it promotes modularity.

## Design Decisions

### Why keep some components in ui.py?

- **Spectrum widget** (~1200 lines): Too large to extract in a single refactoring pass; will be split in future iterations
- **MainWidget/MainWindow** (~2000 lines): Core application logic tightly integrated with multiple components; requires careful planning to decompose

### Backward Compatibility

All classes remain accessible from `ui.py` to ensure existing code continues working without modification. This dual-import approach allows gradual migration to the modular architecture.

### Testing

All 57 existing tests pass without modification, confirming full backward compatibility:

```bash
python3 -m pytest tests/ -v
# 57 passed, 2 skipped
```

## Future Work

Planned extractions for future refactoring phases:
1. **Spectrum widget**: Split into separate visualization module
2. **MainWidget**: Decompose into ControlPanel, ResultsView, and other sub-components
3. **Shared mixins**: Extract common behavior patterns into mixin classes

## Benefits

1. **Improved Maintainability**: Smaller, focused modules are easier to understand and modify
2. **Independent Testing**: Components can be tested in isolation
3. **Reusability**: Components can be imported and used independently
4. **Clearer Dependencies**: Module boundaries make dependencies explicit
5. **Easier Onboarding**: New developers can understand individual components without reading 5000-line file

## Migration Guide

For existing code using `ui.py`, no changes are required. For new development:

**Before:**
```python
from interference_calculator.ui import TableModel, TableView
```

**After (recommended):**
```python
from interference_calculator.ui_components import TableModel, TableView
```

Both work identically. Choose the approach that best fits your needs.
