"""Table components for displaying interference calculation results.

This module contains:
- TableModel: QAbstractTableModel backed by pandas DataFrame
- TableView: QTableView with HTML support and context menu
- HTMLDelegate: Item delegate for rendering HTML in table cells
"""

import re

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets as widgets

from interference_calculator.molecule import Molecule
from interference_calculator.ui_components.utils import _text, _type_display, _column_display


class TableModel(QtCore.QAbstractTableModel):
    """Take a pandas DataFrame and set data in a QTableModel (read-only)."""
    
    def __init__(self, data, table='interference', language='en', parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._data = data
        self.table = table
        self.language = language

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                colname = self._data.columns[index.column()]
                value = self._data.iloc[index.row(), index.column()]
                if self.table == 'interference':
                    if colname in ('molecule', 'ion'):
                        # formula
                        try:
                            m = Molecule(value)
                        except Exception:
                            return str(value)
                        else:
                            return re.sub(r'<[^>]+>', '', m.formula(style='html', all_isotopes=True))
                    elif colname in ('mass/charge', 'm/z'):
                        return '{:.6f}'.format(value)
                    elif colname in ('mass/charge diff', '\u0394mass/charge', '\u0394m/z'):
                        return '{:.7f}'.format(value)
                    elif colname == '\u0394ppm':
                        if pd.isna(value):
                            return ''
                        return '{:.2f}'.format(value)
                    elif 'MRP' in colname:
                        if np.isinf(value):
                            return '\u221e'
                        return '{:.0f}'.format(value)
                    elif colname in ('probability', 'prob.'):
                        return '{:.5g}'.format(value)
                    elif colname in ('formation factor', 'relative risk', 'risk'):
                        if value == '':
                            return ''
                        return '{:.3g}'.format(value)
                    elif colname in ('resolved', 'ok'):
                        if value == '':
                            return ''
                        return _text(self.language, 'yes') if bool(value) else _text(self.language, 'no')
                    elif colname == 'type':
                        return _type_display(self.language, value)
                    else:
                        return '{}'.format(value)
                elif self.table == 'std_ratios':
                    if colname == 'isotope':
                        # formula
                        try:
                            m = Molecule(value)
                        except Exception:
                            return str(value)
                        else:
                            return re.sub(r'<[^>]+>', '', m.formula(style='html', all_isotopes=True))
                    elif colname == 'mass':
                        return '{:.6f}'.format(value)
                    elif colname in ('abundance', 'ratio'):
                        return '{:.5g}'.format(value)
                    elif colname == 'inverse ratio':
                        return '{:.2f}'.format(value)
                    else:
                        return '{}'.format(value)
            elif role == QtCore.Qt.TextAlignmentRole:
                if index.column() == 0:
                    return QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
                else:
                    return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
            elif role == QtCore.Qt.EditRole:
                return self._data.iloc[index.row(), index.column()]
            elif role == QtCore.Qt.BackgroundRole:
                if 'target' in self._data.columns and self._data['target'].iloc[index.row()]:
                    return QtGui.QColor(*_red, alpha=32)
                if self._data.columns[index.column()] in ('resolved', 'ok'):
                    value = self._data.iloc[index.row(), index.column()]
                    if value != '' and not bool(value):
                        return QtGui.QColor(230, 156, 62, alpha=42)

    def headerData(self, rowcol, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return _column_display(self.language, self._data.columns[rowcol])
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[rowcol]

    def sort(self, column, order):
        # QtCore.Qt.AscendingOrder = 0
        # QtCore.Qt.DescendingOrder = 1
        ascending = not bool(order)
        colname = self._data.columns[column]
        self._data.sort_values(colname, ascending=ascending, inplace=True)
        self.beginResetModel()
        self.endResetModel()

    def copy(self, selection):
        mask = np.zeros(self._data.shape, dtype=bool)
        for s in selection:
            mask[s.row(), s.column()] = True
        output = self._data.where(mask)
        output = output.dropna(how='all', axis=(0,1))
        pasteboard = widgets.QApplication.clipboard()
        pasteboard.setText(output.to_csv(index=False))


class TableView(widgets.QTableView):
    """Implement a QTableView which can display HTML in arbitrary columns."""
    
    def __init__(self, html_cols=None, parent=None):
        widgets.QTableView.__init__(self, parent=parent)
        self.language = 'en'
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(widgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(widgets.QAbstractItemView.ExtendedSelection)
        self.setWordWrap(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(30)
        self.horizontalHeader().setHighlightSections(False)
        self.setShowGrid(True)
        if html_cols is not None:
            if isinstance(html_cols, int):
                html_cols = [html_cols]
            [self.setItemDelegateForColumn(c, HTMLDelegate(parent=parent)) for c in html_cols]

    def set_language(self, language):
        self.language = language

    def copy(self):
        self.model().copy(self.selectedIndexes())

    def contextMenuEvent(self, event):
        menu = widgets.QMenu(self)
        copy_action = menu.addAction(_text(self.language, 'copy'))
        copy_action.setShortcut('Ctrl+C')
        select_all_action = menu.addAction(_text(self.language, 'select_all'))
        select_all_action.setShortcut('Ctrl+A')
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == copy_action:
            self.copy()
        elif action == select_all_action:
            self.selectAll()


class HTMLDelegate(widgets.QStyledItemDelegate):
    """Display HTML in a table cell."""
    
    def __init__(self, parent=None):
        widgets.QStyledItemDelegate.__init__(self, parent=parent)

    def createEditor(self, parent, option, index):
        """Disable editing."""
        return None

    def paint(self, painter, option, index):
        """Paint QTextDocument."""
        options = widgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = widgets.QApplication.style()
        textbox = QtGui.QTextDocument()
        textbox.setHtml(options.text)
        textbox.setTextWidth(options.rect.width())
        options.text = ''
        style.drawControl(widgets.QStyle.CE_ItemViewItem, options, painter)
        context = QtGui.QAbstractTextDocumentLayout.PaintContext()
        textrect = style.subElementRect(widgets.QStyle.SE_ItemViewItemText, options)

        painter.save()
        painter.translate(textrect.topLeft())
        painter.setClipRect(textrect.translated(-textrect.topLeft()))
        textbox.documentLayout().draw(painter, context)
        painter.restore()

    def sizeHint(self, option, index):
        """Set size hint for HTMLDelegate."""
        options = widgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        textbox = QtGui.QTextDocument()
        textbox.setHtml(options.text)
        textbox.setTextWidth(options.rect.width())

        return QtCore.QSize(textbox.idealWidth(), textbox.size().height())


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'np':
        import numpy as np
        return np
    elif name == 'pd':
        import pandas as pd
        return pd
    elif name == '_red':
        # Import from ui module for color constant
        from interference_calculator.ui import _red
        return _red
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
