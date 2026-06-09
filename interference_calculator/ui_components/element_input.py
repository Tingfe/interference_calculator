"""Element input widget with chip-based UI.

This module provides ElementInput, a widget for selecting chemical elements
using interactive chips with add/remove functionality and element picker dialog.
"""

import re

from PyQt5 import QtCore
from PyQt5 import QtWidgets as widgets

from interference_calculator.molecule import periodic_table
from interference_calculator.ui_components.utils import _text


_isotope_rx = re.compile(r'(\d*[A-Z][a-z]{0,2})')


def _periodic_element_rows():
    """Return periodic table rows sorted by atomic number."""
    return (
        periodic_table[['atomic number', 'element', 'element name']]
        .drop_duplicates('element')
        .sort_values('atomic number')
    )


class ElementInput(widgets.QWidget):
    """Chip-based element input supporting add/remove/search elements."""
    
    editingFinished = QtCore.pyqtSignal()
    elementsChanged = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        widgets.QWidget.__init__(self, parent=parent)
        self.setObjectName('elementsInput')
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setToolTip('')
        self.language = 'en'
        self._elements = []
        self._read_only = False

        self._chip_container = widgets.QWidget()
        self._chip_container.setObjectName('elementChipCanvas')
        self._chip_container.setToolTip('')
        self._chip_container.setSizePolicy(widgets.QSizePolicy.Expanding, widgets.QSizePolicy.MinimumExpanding)
        self._chip_widgets = []

        self._placeholder_text = _text(self.language, 'elements_empty_hint')
        self._placeholder_label = widgets.QLabel(self._placeholder_text, self._chip_container)
        self._placeholder_label.setObjectName('elementPlaceholder')
        self._placeholder_label.setToolTip('')

        self._add_btn = widgets.QPushButton(_text(self.language, 'add_element'), self._chip_container)
        self._add_btn.setFixedHeight(20)
        self._add_btn.setMinimumWidth(42)
        self._add_btn.setStyleSheet(
            "font-size: 11px; font-weight: 600; background: #dbeafe; "
            "border: 1px solid #bfdbfe; border-radius: 3px; padding: 0 5px; "
            "min-height: 20px; max-height: 20px;"
        )
        self._add_btn.setToolTip(_text(self.language, 'add_element_tooltip'))
        self._add_btn.clicked.connect(self._show_element_picker)

        self._scroll_area = widgets.QScrollArea(self)
        self._scroll_area.setObjectName('elementScroll')
        self._scroll_area.setToolTip('')
        self._scroll_area.setFrameShape(widgets.QFrame.NoFrame)
        self._scroll_area.setWidgetResizable(False)
        self._scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self._scroll_area.setWidget(self._chip_container)
        self._scroll_area.viewport().installEventFilter(self)

        layout = widgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._scroll_area)
        self._rebuild_chips()

    def text(self):
        return ' '.join(self._elements)

    def setText(self, text):
        atoms = re.findall(_isotope_rx, str(text))
        self.set_elements(atoms)

    def elements(self):
        return list(self._elements)

    def set_elements(self, elements):
        self._elements = []
        for el in elements:
            if el and (periodic_table['element'] == el).any():
                if el not in self._elements:
                    self._elements.append(el)
        self._rebuild_chips()
        self.elementsChanged.emit(self._elements)

    def add_elements(self, new_elements):
        changed = False
        for el in new_elements:
            if el and (periodic_table['element'] == el).any() and el not in self._elements:
                self._elements.append(el)
                changed = True
        if changed:
            self._rebuild_chips()
            self.elementsChanged.emit(self._elements)

    def _rebuild_chips(self):
        for chip in self._chip_widgets:
            if chip not in (self._add_btn, self._placeholder_label):
                chip.deleteLater()
        self._chip_widgets = []
        for el in self._elements:
            chip = self._create_chip(el)
            self._chip_widgets.append(chip)
        self._add_btn.setVisible(not self._read_only)
        self._add_btn.setEnabled(not self._read_only)
        if not self._read_only:
            self._add_btn.show()
        self._chip_widgets.append(self._add_btn)
        if not self._elements and not self._read_only and self._placeholder_text:
            self._placeholder_label.setText(self._placeholder_text)
            self._placeholder_label.show()
            self._chip_widgets.append(self._placeholder_label)
        else:
            self._placeholder_label.hide()
        self._sync_container_height()
        QtCore.QTimer.singleShot(0, self._sync_container_height)

    def _create_chip(self, element):
        dense_mode = len(self._elements) > 36
        chip = widgets.QFrame(self._chip_container)
        chip.setObjectName('elementChip')
        chip.setSizePolicy(widgets.QSizePolicy.Fixed, widgets.QSizePolicy.Fixed)
        chip.setFixedHeight(18)
        chip.setStyleSheet(
            "QFrame#elementChip { background: #dbeafe; border: 1px solid #bfdbfe; "
            "border-radius: 3px; padding: 0; }"
        )
        if dense_mode and not self._read_only:
            chip.setToolTip(_text(self.language, 'remove_element_tooltip'))
            chip.setCursor(QtCore.Qt.PointingHandCursor)
            chip.mouseDoubleClickEvent = lambda event, e=element: self._remove_element(e)
        layout = widgets.QHBoxLayout(chip)
        layout.setContentsMargins(4, 0, 4 if dense_mode else 3, 0)
        layout.setSpacing(2)
        label = widgets.QLabel(element, chip)
        label.setStyleSheet("color: #1e40af; font-size: 11px; font-weight: 600;")
        layout.addWidget(label)
        extra_width = 10
        if not dense_mode:
            btn = widgets.QPushButton('×', chip)
            btn.setFixedSize(12, 14)
            btn.setVisible(not self._read_only)
            btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; color: #64748b; "
                "font-size: 11px; padding: 0; min-width: 12px; max-width: 12px; "
                "min-height: 14px; max-height: 14px; }"
                "QPushButton:hover { color: #dc2626; font-weight: bold; }"
            )
            btn.clicked.connect(lambda checked, e=element: self._remove_element(e))
            layout.addWidget(btn)
            extra_width = 26
        chip.setLayout(layout)
        chip.setFixedWidth(label.sizeHint().width() + extra_width)
        chip.show()
        return chip

    def set_language(self, language):
        self.language = language
        self._add_btn.setText(_text(self.language, 'add_element'))
        self._add_btn.setToolTip(_text(self.language, 'add_element_tooltip'))
        self.setPlaceholderText(_text(self.language, 'elements_empty_hint'))
        for chip in self._chip_widgets:
            if chip is not self._add_btn and chip.toolTip():
                chip.setToolTip(_text(self.language, 'remove_element_tooltip'))

    def _remove_element(self, element):
        if self._read_only:
            return
        if element in self._elements:
            self._elements.remove(element)
            self._rebuild_chips()
            self.elementsChanged.emit(self._elements)

    def _show_element_picker(self):
        if self._read_only:
            return
        dialog = widgets.QDialog(self)
        dialog.setWindowTitle(_text(self.language, 'select_elements_title'))
        dialog.resize(500, 500)
        layout = widgets.QVBoxLayout(dialog)

        search_input = widgets.QLineEdit(dialog)
        search_input.setPlaceholderText(_text(self.language, 'search_elements'))
        layout.addWidget(search_input)

        list_widget = widgets.QListWidget(dialog)
        list_widget.setSelectionMode(widgets.QAbstractItemView.MultiSelection)
        layout.addWidget(list_widget, stretch=1)

        btn_layout = widgets.QHBoxLayout()
        select_all_btn = widgets.QPushButton(_text(self.language, 'select_all_visible'), dialog)
        clear_btn = widgets.QPushButton(_text(self.language, 'clear_selection'), dialog)
        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch(1)
        ok_btn = widgets.QPushButton(_text(self.language, 'add_selected'), dialog)
        ok_btn.setObjectName('primaryButton')
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        all_elements = self._available_element_rows()
        _all_items = []
        for _, row in all_elements.iterrows():
            item = widgets.QListWidgetItem(f"{row['element']}  ({row['element name']})")
            item.setData(QtCore.Qt.UserRole, row['element'])
            list_widget.addItem(item)
            _all_items.append(item)

        if not _all_items:
            item = widgets.QListWidgetItem(_text(self.language, 'all_elements_added'))
            item.setFlags(QtCore.Qt.NoItemFlags)
            list_widget.addItem(item)
            search_input.setEnabled(False)
            select_all_btn.setEnabled(False)
            clear_btn.setEnabled(False)
            ok_btn.setEnabled(False)

        def apply_search(text):
            query = text.lower()
            for item in _all_items:
                item.setHidden(query not in item.text().lower())

        def select_visible():
            list_widget.clearSelection()
            for item in _all_items:
                if not item.isHidden():
                    item.setSelected(True)

        search_input.textChanged.connect(apply_search)
        select_all_btn.clicked.connect(select_visible)
        clear_btn.clicked.connect(list_widget.clearSelection)

        def add_selected():
            selected = [item.data(QtCore.Qt.UserRole) for item in list_widget.selectedItems()]
            self.add_elements(selected)
            dialog.accept()

        ok_btn.clicked.connect(add_selected)
        dialog.exec_()

    def _available_element_rows(self):
        """Return periodic-table elements that are not already selected."""
        selected = set(self._elements)
        all_elements = _periodic_element_rows()
        if not selected:
            return all_elements
        return all_elements[~all_elements['element'].isin(selected)]

    def setPlaceholderText(self, text):
        self._placeholder_text = str(text or '')
        self._placeholder_label.setText(self._placeholder_text)
        self._rebuild_chips()

    def setReadOnly(self, read_only):
        """Compatibility with the previous text edit based element input."""
        self._read_only = bool(read_only)
        self._rebuild_chips()

    def resizeEvent(self, event):
        widgets.QWidget.resizeEvent(self, event)
        self._sync_container_height()
        QtCore.QTimer.singleShot(0, self._sync_container_height)

    def eventFilter(self, obj, event):
        if obj is self._scroll_area.viewport() and event.type() == QtCore.QEvent.Resize:
            QtCore.QTimer.singleShot(0, self._sync_container_height)
        return widgets.QWidget.eventFilter(self, obj, event)

    def _sync_container_height(self):
        """Resize the chip canvas so QScrollArea scrolls instead of clipping."""
        if not hasattr(self, '_scroll_area'):
            return
        width = max(40, self._scroll_area.viewport().width())
        spacing = 2
        margin = 3
        x = margin
        y = margin
        line_height = 0
        max_x = max(width - margin, margin + 1)
        for widget in self._chip_widgets:
            if widget.isHidden():
                continue
            hint = widget.sizeHint()
            if widget is self._placeholder_label:
                widget_width = min(hint.width(), max(max_x - x, 80))
            else:
                widget_width = widget.width() if widget.width() > 0 else hint.width()
            widget_height = widget.height() if widget.height() > 0 else hint.height()
            widget_width = max(widget_width, widget.minimumWidth())
            widget_height = max(widget_height, widget.minimumHeight())
            if x + widget_width > max_x and x > margin:
                x = margin
                y += line_height + spacing
                line_height = 0
            widget.setGeometry(x, y, widget_width, widget_height)
            x += widget_width + spacing
            line_height = max(line_height, widget_height)
        height = max(y + line_height + margin, 30)
        self._chip_container.setMinimumSize(width, height)
        self._chip_container.resize(width, height)
