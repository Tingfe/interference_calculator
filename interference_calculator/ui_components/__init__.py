"""UI components for interference calculator.

This package contains modular UI components extracted from ui.py to improve
maintainability and reduce file size. Each component is in its own module.

Components:
    - table: TableModel, TableView, HTMLDelegate
    - element_input: ElementInput widget
    - spectrum: Spectrum visualization widget (kept in ui.py due to size)
    - filter_proxy: InterferenceFilterProxy for result filtering
    - worker: CalculationWorker for background computation
    - utils: Shared utility functions
"""

from interference_calculator.ui_components.table import (
    TableModel,
    TableView,
    HTMLDelegate,
)
from interference_calculator.ui_components.element_input import ElementInput
# Spectrum kept in ui.py due to its large size (~1200 lines)
# from interference_calculator.ui_components.spectrum import Spectrum
from interference_calculator.ui_components.filter_proxy import InterferenceFilterProxy
from interference_calculator.ui_components.worker import CalculationWorker

__all__ = [
    'TableModel',
    'TableView',
    'HTMLDelegate',
    'ElementInput',
    # 'Spectrum',  # Kept in ui.py
    'InterferenceFilterProxy',
    'CalculationWorker',
]
