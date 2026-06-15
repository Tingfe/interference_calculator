"""Shared utility functions for UI components.

This module contains helper functions used across multiple UI component modules.
It is dependency-free (only imports Qt) so that ui.py and ui_components/* can
share constants and helpers without creating circular imports.
"""

from PyQt5 import QtGui


# ---------------------------------------------------------------------------
# Colour palette constants
#
# Qt uses 0-255 ints, Matplotlib uses 0-1 floats for RGB.
# Palette follows a data-dense scientific tool system: blue for primary data,
# amber for unresolved/risk states, red for destructive/error states.
#
# These live here (rather than in ui.py) so that ui_components modules can
# import them without pulling in the whole ui.py module (circular import).
# ---------------------------------------------------------------------------
_red = (220, 38, 38)    # dc2626
_blue = (30, 64, 175)   # 1e40af
_amber = (217, 119, 6)  # d97706
_blueF = [c / 255 for c in _blue]
_redF = [c / 255 for c in _red]
_amberF = [c / 255 for c in _amber]
_mutedF = [100 / 255, 116 / 255, 139 / 255]


# UI text dictionaries (imported from ui.py to avoid circular dependencies)
# These will be populated when the module is first imported
_UI_TEXT = {}
_TYPE_DISPLAY = {}
_COLUMN_DISPLAY = {}


def _text(language, key):
    """Get localized text string."""
    if not _UI_TEXT:
        # Lazy import to avoid circular dependency
        from interference_calculator.ui import _UI_TEXT as ui_text
        _UI_TEXT.update(ui_text)
    return _UI_TEXT.get(language, _UI_TEXT['en']).get(key, _UI_TEXT['en'][key])


def _type_display(language, value):
    """Get localized type display string."""
    if not _TYPE_DISPLAY:
        from interference_calculator.ui import _TYPE_DISPLAY as ui_type_display
        _TYPE_DISPLAY.update(ui_type_display)
    return _TYPE_DISPLAY.get(language, _TYPE_DISPLAY['en']).get(value, value)


def _column_display(language, value):
    """Get localized column header string."""
    if not _COLUMN_DISPLAY:
        from interference_calculator.ui import _COLUMN_DISPLAY as ui_column_display
        _COLUMN_DISPLAY.update(ui_column_display)
    return _COLUMN_DISPLAY.get(language, _COLUMN_DISPLAY['en']).get(value, value)


def _ui_font(point_size=None, weight=None):
    """Create a QFont with optional point size and weight."""
    font = QtGui.QFont()
    if point_size is not None:
        font.setPointSize(point_size)
    if weight is not None:
        font.setWeight(weight)
    return font
