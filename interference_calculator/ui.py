#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" GUI for interference calculator. """
from __future__ import division

try:
    from PyQt5 import QtCore, QtGui
    from PyQt5 import QtWidgets as widgets
except ImportError:
    try:
        from PyQt4 import QtCore, QtGui
        from PyQt4 import QtGui as widgets
        widgets.QStyleOptionViewItem = widgets.QStyleOptionViewItemV4
    except ImportError:
        raise ImportError('You need to have either PyQt4 or PyQt5 installed.')

class _LazyModule:
    __slots__ = ("_name", "_module")
    def __init__(self, name):
        self._name = name
        self._module = None
    def __getattr__(self, attr):
        if self._module is None:
            self._module = __import__(self._name)
        return getattr(self._module, attr)

np = _LazyModule("numpy")
pd = _LazyModule("pandas")

import sys, re
from importlib import resources
from pyparsing import ParseException
from interference_calculator.inorganic import inorganic_interference
from interference_calculator.main import standard_ratio
from interference_calculator.molecule import Molecule, periodic_table
from interference_calculator.ui_help import *
from interference_calculator import __version__

_isotope_rx = re.compile(r'(\d*[A-Z][a-z]{0,2})')
_charges_rx = re.compile(r'(\d+)')

_COMMON_INORGANIC_ELEMENTS = (
    'H', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F',
    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
    'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
    'Ga', 'Ge', 'As', 'Se', 'Br',
    'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In',
    'Sn', 'Sb', 'Te', 'I',
    'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho',
    'Er', 'Tm', 'Yb', 'Lu',
    'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi',
    'Th', 'U',
)

# Qt uses 0-255 ints, Matplotlib uses 0-1 floats for RGB.
# Palette follows a data-dense scientific tool system: blue for primary data,
# amber for unresolved/risk states, red for destructive/error states.
_red = (220, 38, 38)    #dc2626
_blue = (30, 64, 175)   #1e40af
_amber = (217, 119, 6)  #d97706
_blueF = [c/255 for c in _blue]
_redF = [c/255 for c in _red]
_amberF = [c/255 for c in _amber]
_mutedF = [100/255, 116/255, 139/255]

_TYPE_DISPLAY = {
    'en': {
        'doubly charged': '2+ atom',
        'plasma adduct': 'plasma',
        'background molecule': 'background',
        'enumerated': 'scan',
    },
    'zh': {
        'atomic': '原子离子',
        'doubly charged': '双电荷',
        'oxide': '氧化物',
        'dioxide': '二氧化物',
        'hydride': '氢化物',
        'hydroxide': '氢氧化物',
        'nitride': '氮化物',
        'carbide': '碳化物',
        'sulfide': '硫化物',
        'halide': '卤化物',
        'plasma adduct': '等离子体',
        'background molecule': '背景分子',
        'cluster': '团簇',
        'target': '目标峰',
        'enumerated': '通用扫描',
    },
}

_COLUMN_DISPLAY = {
    'en': {},
    'zh': {
        'ion': '离子',
        'type': '类型',
        'z': '电荷',
        'm/z': 'm/z',
        '\u0394m/z': '\u0394m/z',
        '\u0394ppm': '\u0394ppm',
        'MRP': 'MRP',
        'probability': '概率',
        'prob.': '概率',
        'relative risk': '风险',
        'risk': '风险',
        'ok': '可分辨',
        'isotope': '同位素',
        'mass': '质量',
        'abundance': '丰度',
        'ratio': '比值',
        'inverse ratio': '倒数比值',
        'standard': '数据源',
    },
}

_UI_TEXT = {
    'en': {
        'window_title': 'Inorganic mass interference calculator',
        'spectrum_window_title': 'Inorganic interference spectrum',
        'spectrum_target_title': 'Target-centered interference spectrum',
        'spectrum_title': 'Inorganic interference spectrum',
        'y_normalised': '{} (normalised)',
        'candidate': 'candidate',
        'not_resolved': 'not resolved',
        'target_peak': 'target',
        'ppm_from_target': '\u0394ppm from target',
        'mz_from_target': '\u0394m/z from target',
        'header_title': 'Inorganic mass interference',
        'header_subtitle': 'Inorganic peak screening',
        'language': 'Language',
        'workflow': 'workflow',
        'mode': 'mode',
        'target_group': 'target peak',
        'target': 'target',
        'window_width': 'window width',
        'target_hint': 'Full-width window; GDMS defaults to 2000 ppm.',
        'sample_plasma': 'sample / plasma',
        'elements': 'elements',
        'add_set': 'add set',
        'elements_hint': 'Include analyte, matrix, plasma, and background elements.',
        'ion_model': 'ion model',
        'ions': 'ions',
        'max_size': 'max size',
        'instrument_mrp': 'instrument MRP',
        'add_set_empty': 'add set...',
        'all_inorganic_elements': 'all inorganic elements',
        'ar_background': 'Ar plasma background',
        'light_background': 'light background',
        'halogens_sulfur': 'halogens / sulfur',
        'transition_matrix': 'transition matrix',
        'silicate_matrix': 'silicate matrix',
        'neutral': 'neutral',
        'off': 'off',
        'calculate': 'Calculate',
        'ratios': 'Ratios',
        'convert_invalid_target': 'Enter a valid target before converting the window unit.',
        'convert_target_required': 'Enter a target peak before converting the window unit.',
        'empty_atoms': 'Enter at least one element or isotope.',
        'missing_element': '{} is not an element or missing from the periodic table.',
        'ppm_requires_target': 'A ppm window requires a target peak.',
        'invalid_target': 'Enter target as a number or as a molecular formula.',
        'candidate_count': '{} candidate peaks',
        'isotope_count': '{} isotope rows',
        'help_title': 'Interference calculator help',
        'results_title': 'Results',
        'empty_title': 'Ready for peak screening',
        'empty_body': 'Enter a target peak and sample elements, then calculate interference candidates.',
        'summary_mode': 'Mode',
        'summary_window': 'Window',
        'summary_mrp': 'MRP',
        'summary_ready': 'Ready',
        'summary_candidates': 'Candidates',
        'summary_unresolved': 'Unresolved',
        'summary_isotopes': 'Isotopes',
        'open_spectrum': 'Open spectrum',
        'open_help': 'Open help',
        'yes': 'yes',
        'no': 'no',
    },
    'zh': {
        'window_title': '无机质谱峰干扰计算器',
        'spectrum_window_title': '无机干扰谱图',
        'spectrum_target_title': '以目标峰为中心的干扰谱图',
        'spectrum_title': '无机干扰谱图',
        'y_normalised': '{}（归一化）',
        'candidate': '候选峰',
        'not_resolved': '未分辨',
        'target_peak': '目标峰',
        'ppm_from_target': '相对目标峰 \u0394ppm',
        'mz_from_target': '相对目标峰 \u0394m/z',
        'header_title': '无机质谱峰干扰',
        'header_subtitle': '无机质谱峰筛查',
        'language': '语言',
        'workflow': '流程',
        'mode': '模式',
        'target_group': '目标峰',
        'target': '目标',
        'window_width': '窗口宽度',
        'target_hint': '完整窗口宽度；GDMS 默认 2000 ppm。',
        'sample_plasma': '样品 / 等离子体',
        'elements': '元素',
        'add_set': '添加组合',
        'elements_hint': '建议包含待测、基体、等离子体和背景元素。',
        'ion_model': '离子模型',
        'ions': '离子',
        'max_size': '最大原子数',
        'instrument_mrp': '仪器 MRP',
        'add_set_empty': '添加组合...',
        'all_inorganic_elements': '全元素（无机质谱）',
        'ar_background': 'Ar 等离子体背景',
        'light_background': '轻元素背景',
        'halogens_sulfur': '卤素 / 硫',
        'transition_matrix': '过渡金属基体',
        'silicate_matrix': '硅酸盐基体',
        'neutral': '中性',
        'off': '关闭',
        'calculate': '计算',
        'ratios': '同位素比',
        'convert_invalid_target': '切换窗口单位前，请先输入有效目标峰。',
        'convert_target_required': '切换窗口单位前，请先输入目标峰。',
        'empty_atoms': '请至少输入一个元素或同位素。',
        'missing_element': '{} 不是有效元素，或当前同位素库中缺少该元素。',
        'ppm_requires_target': 'ppm 窗口需要先输入目标峰。',
        'invalid_target': '目标峰请输入数值或分子式。',
        'candidate_count': '{} 个候选峰',
        'isotope_count': '{} 行同位素数据',
        'help_title': '软件介绍',
        'results_title': '结果',
        'empty_title': '准备开始峰干扰筛查',
        'empty_body': '输入目标峰和样品元素后，点击计算生成候选干扰峰。',
        'summary_mode': '模式',
        'summary_window': '窗口',
        'summary_mrp': 'MRP',
        'summary_ready': '就绪',
        'summary_candidates': '候选峰',
        'summary_unresolved': '未分辨',
        'summary_isotopes': '同位素',
        'open_spectrum': '打开谱图',
        'open_help': '打开帮助',
        'yes': '是',
        'no': '否',
    },
}


def _text(language, key):
    return _UI_TEXT.get(language, _UI_TEXT['en']).get(key, _UI_TEXT['en'][key])


def _type_display(language, value):
    return _TYPE_DISPLAY.get(language, _TYPE_DISPLAY['en']).get(value, value)


def _column_display(language, value):
    return _COLUMN_DISPLAY.get(language, _COLUMN_DISPLAY['en']).get(value, value)

def _resource_path(name):
    return str(resources.files('interference_calculator').joinpath(name))

_icon = _resource_path('icon.svg')
_display_button_icon = _resource_path('display_button_icon.svg')
_help_button_icon = _resource_path('help_button_icon.svg')



def _current_data(combo):
    try:
        return combo.currentData()
    except AttributeError:
        return combo.itemData(combo.currentIndex())

_APP_STYLESHEET = """
QMainWindow, QWidget {
    background: #f8fafc;
    color: #172033;
    font-size: 13px;
}
QFrame#header {
    background: #0f172a;
    border: none;
}
QLabel {
    background: transparent;
}
QLabel#appTitle {
    color: #ffffff;
    font-size: 19px;
    font-weight: 600;
}
QLabel#appSubtitle {
    color: #cbd5e1;
    font-size: 12px;
}
QLabel#fieldLabel {
    color: #334155;
    font-size: 12px;
    font-weight: 600;
}
QFrame#controlPanel {
    background: #f8fafc;
    border-right: 1px solid #dbeafe;
}
QScrollArea#controlScroll {
    background: #f8fafc;
    border: none;
}
QGroupBox {
    border: 1px solid #dbe4f0;
    border-radius: 6px;
    margin-top: 12px;
    padding: 10px 10px 10px 10px;
    background: #ffffff;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #334155;
}
QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    min-height: 30px;
    padding: 2px 8px;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    background: #ffffff;
    selection-background-color: #1e40af;
}
QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #1e40af;
}
QLineEdit:disabled, QPlainTextEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {
    background: #f1f5f9;
    color: #64748b;
    border-color: #dbe4f0;
}
QPlainTextEdit#elementsInput {
    min-height: 118px;
    max-height: 156px;
}
QLabel#helperText {
    color: #64748b;
    font-size: 11px;
    font-weight: 400;
}
QPushButton {
    min-height: 34px;
    padding: 4px 14px;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    background: #ffffff;
    font-weight: 500;
}
QPushButton:hover {
    background: #eff6ff;
    border-color: #93c5fd;
}
QPushButton:pressed {
    background: #dbeafe;
}
QPushButton:disabled {
    background: #e2e8f0;
    color: #94a3b8;
    border-color: #cbd5e1;
}
QPushButton#primaryButton {
    background: #1e40af;
    border-color: #1e40af;
    color: #ffffff;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background: #1d4ed8;
    border-color: #1d4ed8;
}
QPushButton#primaryButton:pressed {
    background: #1e3a8a;
    border-color: #1e3a8a;
}
QToolButton {
    min-width: 34px;
    min-height: 34px;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    background: #ffffff;
}
QToolButton:hover {
    background: #eff6ff;
    border-color: #93c5fd;
}
QToolButton:pressed {
    background: #dbeafe;
}
QSplitter::handle {
    background: #dbeafe;
}
QFrame#resultsHeader {
    background: #ffffff;
    border-bottom: 1px solid #dbe4f0;
}
QFrame#actionBar {
    background: #ffffff;
    border-top: 1px solid #dbe4f0;
}
QLabel#resultsTitle {
    color: #0f172a;
    font-size: 15px;
    font-weight: 600;
}
QLabel#metricChip {
    background: #eff6ff;
    color: #1e3a8a;
    border: 1px solid #bfdbfe;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 500;
}
QFrame#emptyState {
    background: #ffffff;
    border: none;
}
QLabel#emptyTitle {
    color: #0f172a;
    font-size: 18px;
    font-weight: 600;
}
QLabel#emptyBody {
    color: #64748b;
    font-size: 13px;
}
QTableView {
    background: #ffffff;
    alternate-background-color: #f8fbff;
    border: none;
    gridline-color: #e2e8f0;
    selection-background-color: #dbeafe;
    selection-color: #0f172a;
}
QTableView::item:hover {
    background: #eff6ff;
}
QHeaderView::section {
    background: #eef2ff;
    color: #1e3a8a;
    border: none;
    border-right: 1px solid #dbe4f0;
    border-bottom: 1px solid #dbe4f0;
    padding: 7px 8px;
    font-weight: 600;
}
QStatusBar {
    background: #ffffff;
    border-top: 1px solid #dbe4f0;
}
QToolTip {
    background: #0f172a;
    color: #ffffff;
    border: 1px solid #334155;
    padding: 6px;
}
"""

class TableModel(QtCore.QAbstractTableModel):
    """ Take a pandas DataFrame and set data in a QTableModel (read-only). """
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
                if index.row() < 2 and index.column() == 0:
                    print(f"[DEBUG] data() row={index.row()} col=0 colname={colname!r} value={value!r} table={self.table}")
                if self.table == 'interference':
                    if colname in ('molecule', 'ion'):
                        # formula
                        try:
                            m = Molecule(value)
                        except ParseException:
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
    """ Implement a QTableView which can display HTML in arbitrary columns """
    def __init__(self, html_cols=None, parent=None):
        widgets.QTableView.__init__(self, parent=parent)
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

    def copy(self):
        self.model().copy(self.selectedIndexes())

    def contextMenuEvent(self, event):
        menu = widgets.QMenu(self)
        copy_action = menu.addAction('Copy')
        copy_action.setShortcut('Ctrl+C')
        select_all_action = menu.addAction('Select All')
        select_all_action.setShortcut('Ctrl+A')
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == copy_action:
            self.copy()
        elif action == select_all_action:
            self.selectAll()


class ElementInput(widgets.QPlainTextEdit):
    """Compact multi-line input for element lists."""
    editingFinished = QtCore.pyqtSignal()

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

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)

    def setPlaceholderText(self, text):
        if hasattr(widgets.QPlainTextEdit, 'setPlaceholderText'):
            widgets.QPlainTextEdit.setPlaceholderText(self, text)

    def focusOutEvent(self, event):
        self.editingFinished.emit()
        widgets.QPlainTextEdit.focusOutEvent(self, event)


class HTMLDelegate(widgets.QStyledItemDelegate):
    """ Display HTML in a table cell. """
    def __init__(self, parent=None):
        widgets.QStyledItemDelegate.__init__(self, parent=parent)

    def createEditor(self, parent, option, index):
        """ disable editing """
        return None

    def paint(self, painter, option, index):
        """ paint QTextDocument """
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
        """ Set size hint for HTMLDelegate. """
        options = widgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        textbox = QtGui.QTextDocument()
        textbox.setHtml(options.text)
        textbox.setTextWidth(options.rect.width())

        return QtCore.QSize(textbox.idealWidth(), textbox.size().height())



class Spectrum(widgets.QWidget):
    """Interactive stem-plot spectrum drawn with Qt QPainter (no matplotlib)."""

    # ── colour palette ──────────────────────────────────────────────
    _BLUE     = QtGui.QColor(0x25, 0x63, 0xeb)   # candidate peaks
    _AMBER    = QtGui.QColor(0xf5, 0x9e, 0x0b)   # unresolved
    _RED      = QtGui.QColor(0xef, 0x44, 0x44)   # target
    _MUTED    = QtGui.QColor(0x64, 0x74, 0x8b)   # annotation text
    _GRID     = QtGui.QColor(0xcb, 0xd5, 0xe1)   # major grid
    _GRID_MNR = QtGui.QColor(0xe2, 0xe8, 0xf0)   # minor grid (y)
    _BG       = QtGui.QColor(0xf8, 0xfa, 0xfc)
    _CHART_BG = QtGui.QColor(0xff, 0xff, 0xff)
    _BORDER   = QtGui.QColor(0xdb, 0xe4, 0xf0)
    _TEXT     = QtGui.QColor(0x17, 0x20, 0x33)
    _TICK_CLR = QtGui.QColor(0x33, 0x41, 0x55)

    MAX_LABELS = 8
    _PLOT_FLOOR = 1.0e-4

    # ── init ────────────────────────────────────────────────────────
    def __init__(self, data=None, parent=None, language='en'):
        widgets.QWidget.__init__(self, parent=parent)
        self.language = language
        self.setWindowTitle(_text(self.language, 'spectrum_window_title'))
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.resize(920, 640)
        self.setMinimumSize(760, 520)
        self.setStyleSheet("QWidget { background: " + self._BG.name() + "; }")

        # ── toolbar ─────────────────────────────────────────────
        self.toolbar = widgets.QToolBar(self)
        self.toolbar.setStyleSheet(
            "QToolBar { background: #ffffff; border-bottom: 1px solid #dbe4f0; spacing: 4px; padding: 2px 6px; }")
        self.toolbar.setMovable(False)

        self._zoom_out_btn = widgets.QToolButton(self)
        self._zoom_out_btn.setText('−')
        self._zoom_out_btn.setToolTip('Zoom out (Y axis)')
        self._zoom_out_btn.clicked.connect(self._on_zoom_out)
        self.toolbar.addWidget(self._zoom_out_btn)

        self._zoom_in_btn = widgets.QToolButton(self)
        self._zoom_in_btn.setText('+')
        self._zoom_in_btn.setToolTip('Zoom in (Y axis)')
        self._zoom_in_btn.clicked.connect(self._on_zoom_in)
        self.toolbar.addWidget(self._zoom_in_btn)

        self.toolbar.addSeparator()

        self._reset_btn = widgets.QToolButton(self)
        self._reset_btn.setText('↺')
        self._reset_btn.setToolTip('Reset view')
        self._reset_btn.clicked.connect(self._on_reset_view)
        self.toolbar.addWidget(self._reset_btn)

        # ── chart canvas ─────────────────────────────────────────
        self._canvas = _SpectrumCanvas(self)
        self._canvas.setMinimumHeight(400)

        # ── layout ───────────────────────────────────────────────
        self.layout = widgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self._canvas, 1)
        self.setLayout(self.layout)

        # ── data state ───────────────────────────────────────────
        self._data = None
        self.x = None
        self.y = None
        self.x_label = 'm/z'
        self.x_centered = False
        self._target_mask = None
        self._unresolved_mask = None
        self._plot_window = {}
        self.intensity_column = 'probability'
        self._y_zoom = 1.0           # multiplier on y upper bound
        self._plot_floor = self._PLOT_FLOOR

        if data is not None:
            self.data = data
        self._canvas._spectrum = self

    # ── public API ──────────────────────────────────────────────────
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, newdata):
        self._plot_window = dict(getattr(newdata, 'attrs', {}))
        self._data = newdata.copy().sort_values('mass/charge').reset_index(drop=True)
        self._target_mask = self._target_mask_for(self._data)
        self.x, self.x_label, self.x_centered = self._x_values_for(self._data, self._target_mask)
        self._unresolved_mask = self._unresolved_mask_for(self._data)
        self.intensity_column = self._intensity_column_for(self._data)
        raw_y = pd.to_numeric(self._data[self.intensity_column], errors='coerce').fillna(0.0).values
        self.y = self._normalise_intensity(raw_y, self._target_mask)
        self._y_zoom = 1.0
        self._canvas.update()

    def plot_spectrum(self, data=None):
        """Set spectrum data and trigger redraw (kept for backward compat)."""
        if data is not None:
            self.data = data

    def set_language(self, language):
        """Update spectrum language and redraw existing data."""
        self.language = language
        self.setWindowTitle(_text(self.language, 'spectrum_window_title'))
        if self._data is not None:
            self.x, self.x_label, self.x_centered = self._x_values_for(self._data, self._target_mask)
        self._canvas.update()
        self._update_toolbar_tooltips()

    def _update_toolbar_tooltips(self):
        lang = self.language
        if lang == 'zh':
            self._zoom_out_btn.setToolTip('缩小 Y 轴')
            self._zoom_in_btn.setToolTip('放大 Y 轴')
            self._reset_btn.setToolTip('重置视图')
        else:
            self._zoom_out_btn.setToolTip('Zoom out (Y axis)')
            self._zoom_in_btn.setToolTip('Zoom in (Y axis)')
            self._reset_btn.setToolTip('Reset view')

    # ── toolbar slots ───────────────────────────────────────────────
    def _on_zoom_out(self):
        self._y_zoom = min(self._y_zoom * 1.5, 100.0)
        self._canvas.update()

    def _on_zoom_in(self):
        self._y_zoom = max(self._y_zoom / 1.5, 0.01)
        self._canvas.update()

    def _on_reset_view(self):
        self._y_zoom = 1.0
        self._canvas.update()

    # ── data-processing helpers (identical to old matplotlib version) ─
    def _target_mask_for(self, data):
        if 'target' not in data.columns:
            return np.zeros(data.shape[0], dtype=bool)
        return data['target'].astype(bool).values

    def _x_values_for(self, data, target_mask):
        if target_mask.any():
            if '\u0394ppm' in data.columns:
                values = pd.to_numeric(data['\u0394ppm'], errors='coerce')
                if values.notna().any():
                    return values.fillna(0.0).values, _text(self.language, 'ppm_from_target'), True
            if 'mass/charge diff' in data.columns:
                values = pd.to_numeric(data['mass/charge diff'], errors='coerce')
                if values.notna().any():
                    return values.fillna(0.0).values, _text(self.language, 'mz_from_target'), True
        values = pd.to_numeric(data['mass/charge'], errors='coerce').fillna(0.0)
        return values.values, 'm/z', False

    def _unresolved_mask_for(self, data):
        if 'resolved' not in data.columns:
            return np.zeros(data.shape[0], dtype=bool)
        values = data['resolved'].values
        mask = np.array([(value != '') and not bool(value) for value in values], dtype=bool)
        return mask & ~self._target_mask_for(data)

    def _intensity_column_for(self, data):
        if 'relative risk' in data.columns:
            values = pd.to_numeric(data['relative risk'], errors='coerce').fillna(0.0)
            if values.max() > 0:
                return 'relative risk'
        return 'probability'

    def _normalise_intensity(self, raw_y, target_mask):
        candidate_y = raw_y[~target_mask]
        if candidate_y.size and candidate_y.max() > 0:
            scale = candidate_y.max()
        elif raw_y.size and raw_y.max() > 0:
            scale = raw_y.max()
        else:
            scale = 1.0
        y = raw_y / scale * 100.0
        if target_mask.any():
            y[target_mask] = max(100.0, y[~target_mask].max() if (~target_mask).any() else 100.0)
        return np.clip(y, self._plot_floor, None)

    def _label_indices(self):
        priority = np.ones(self._data.shape[0], dtype=int)
        priority[self._unresolved_mask] = 2
        priority[self._target_mask] = 3
        ranking = pd.DataFrame({
            'row': np.arange(self._data.shape[0]),
            'priority': priority,
            'intensity': self.y,
        })
        ranking = ranking.sort_values(['priority', 'intensity'], ascending=[False, False])
        ordered_rows = ranking['row'].tolist()
        x_span = np.nanmax(self.x) - np.nanmin(self.x)
        min_dx = x_span / 20.0 if x_span else 0.0
        selected = []
        for row in ordered_rows:
            if self._target_mask[row]:
                selected.append(row)
            elif all(abs(self.x[row] - self.x[other]) >= min_dx for other in selected):
                selected.append(row)
            if len(selected) >= self.MAX_LABELS:
                return selected
        for row in ordered_rows:
            if row not in selected:
                selected.append(row)
            if len(selected) >= self.MAX_LABELS:
                break
    def _formula_label(self, value):
        """Return a plain-text formula label suitable for QPainter rendering."""
        try:
            formula = Molecule(value).formula(all_isotopes=True, style='html')
            # Strip HTML tags for QPainter plain-text rendering
            formula = re.sub(r'<[^>]+>', '', formula)
            return formula
        except Exception:
            return str(value)






    def _window_span_for_axis(self):
        if self.x_label.startswith('\u0394ppm'):
            return self._plot_window.get('window_half_ppm')
        if self.x_label.startswith('\u0394m/z'):
            return self._plot_window.get('window_half_mz')
        return None

    # ── drawing helpers (public for _SpectrumCanvas) ─────────────────
    def _draw(self, painter, rect):
        """Entry point called by _SpectrumCanvas.paintEvent."""
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # chart margins (room for tick labels + title)
        ml, mt, mr, mb = 72, 48, 24, 52
        cr = QtCore.QRectF(rect.left() + ml, rect.top() + mt,
                           rect.width() - ml - mr, rect.height() - mt - mb)

        # background
        painter.fillRect(rect, self._BG)
        painter.fillRect(cr, self._CHART_BG)
        painter.setPen(QtGui.QPen(self._BORDER, 1))
        painter.drawRect(cr)

        if self._data is None or self._data.empty:
            painter.setPen(self._TEXT)
            painter.setFont(QtGui.QFont('sans-serif', 13))
            painter.drawText(cr, QtCore.Qt.AlignCenter, _text(self.language, 'empty_title'))
            return

        x, y = self.x, self.y
        target_mask = self._target_mask
        unresolved_mask = self._unresolved_mask
        normal_mask = ~(target_mask | unresolved_mask)

        # ── axis ranges ──────────────────────────────────────────
        finite_x = x[np.isfinite(x)]
        if not finite_x.size:
            finite_x = np.array([0.0])

        if self.x_centered:
            span = np.nanmax(np.abs(finite_x))
            ws = self._window_span_for_axis()
            if ws is not None:
                span = max(span, ws)
            if span <= 0:
                span = 1.0 if 'ppm' in self.x_label else 1.0e-4
            x_min = -span * 1.08
            x_max = span * 1.08
        else:
            x_min = np.nanmin(finite_x)
            x_max = np.nanmax(finite_x)
            if x_min == x_max:
                padding = max(abs(x_min) * 1.0e-5, 1.0e-4)
            else:
                padding = (x_max - x_min) * 0.05
            x_min -= padding
            x_max += padding

        y_hi = max(150.0, np.nanmax(y) * 8.0) * self._y_zoom
        y_lo = self._plot_floor

        def x2p(v):
            return cr.left() + (v - x_min) / (x_max - x_min) * cr.width()

        def y2p(v):
            import math
            lv = math.log10(max(v, y_lo))
            lhi = math.log10(y_hi)
            llo = math.log10(y_lo)
            return cr.bottom() - (lv - llo) / (lhi - llo) * cr.height()

        # ── grid ─────────────────────────────────────────────────
        import math
        painter.setFont(QtGui.QFont('sans-serif', 9))
        # Y grid (log ticks: powers of 10)
        lo_exp = int(math.floor(math.log10(y_lo)))
        hi_exp = int(math.ceil(math.log10(y_hi)))
        for exp in range(lo_exp, hi_exp + 1):
            val = 10 ** exp
            if val < y_lo or val > y_hi:
                continue
            py = y2p(val)
            # major grid
            painter.setPen(QtGui.QPen(self._GRID, 1, QtCore.Qt.DotLine))
            painter.drawLine(QtCore.QPointF(cr.left(), py), QtCore.QPointF(cr.right(), py))
            # tick label
            painter.setPen(self._TICK_CLR)
            label = f'{val:.0e}' if val >= 1000 or val <= 0.001 else (f'{int(val)}' if val >= 1 else f'{val:g}')
            painter.drawText(QtCore.QRectF(cr.left() - 62, py - 8, 56, 16),
                             QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, label)
            # minor grid between powers of 10
            for frac in (2, 3, 4, 5, 6, 7, 8, 9):
                mval = val * frac
                if mval >= y_hi:
                    break
                my = y2p(mval)
                painter.setPen(QtGui.QPen(self._GRID_MNR, 1, QtCore.Qt.DotLine))
                painter.drawLine(QtCore.QPointF(cr.left(), my), QtCore.QPointF(cr.right(), my))

        # X grid (auto ticks)
        x_span = x_max - x_min
        if x_span > 0:
            nticks = max(3, min(12, int(cr.width() / 80)))
            step = self._nice_step(x_span / nticks)
            x0 = math.ceil(x_min / step) * step
            for xi in np.arange(x0, x_max + step * 0.5, step):
                px = x2p(xi)
                painter.setPen(QtGui.QPen(self._GRID, 1, QtCore.Qt.DotLine))
                painter.drawLine(QtCore.QPointF(px, cr.top()), QtCore.QPointF(px, cr.bottom()))
                painter.setPen(self._TICK_CLR)
                if abs(xi) < 1e-5:
                    xi = 0.0
                lbl = f'{xi:.4g}'
                tw = painter.fontMetrics().horizontalAdvance(lbl)
                painter.drawText(QtCore.QPointF(px - tw / 2, cr.bottom() + 14), lbl)

        # ── axis labels ──────────────────────────────────────────
        painter.setFont(QtGui.QFont('sans-serif', 11))
        painter.setPen(self._TEXT)
        # X label
        xlab = self.x_label
        xlw = painter.fontMetrics().horizontalAdvance(xlab)
        painter.drawText(QtCore.QPointF(cr.center().x() - xlw / 2, cr.bottom() + 38), xlab)
        # Y label
        intensity_label = _column_display(self.language, self.intensity_column)
        ylab = _text(self.language, 'y_normalised').format(intensity_label)
        painter.save()
        painter.translate(cr.left() - 62, cr.center().y())
        painter.rotate(-90)
        painter.drawText(QtCore.QPointF(-painter.fontMetrics().horizontalAdvance(ylab) / 2, 0), ylab)
        painter.restore()

        # ── title ────────────────────────────────────────────────
        painter.setFont(QtGui.QFont('sans-serif', 13, QtGui.QFont.Bold))
        ttl = _text(self.language, 'spectrum_target_title') if self.x_centered else _text(self.language, 'spectrum_title')
        ttw = painter.fontMetrics().horizontalAdvance(ttl)
        painter.drawText(QtCore.QPointF(cr.center().x() - ttw / 2, cr.top() - 14), ttl)

        # ── zero line (target-centred) ───────────────────────────
        if self.x_centered:
            zx = x2p(0.0)
            pen = QtGui.QPen(self._RED)
            pen.setStyle(QtCore.Qt.DashLine)
            pen.setWidthF(1.0)
            painter.setPen(pen)
            painter.drawLine(QtCore.QPointF(zx, cr.top()), QtCore.QPointF(zx, cr.bottom()))

        # ── draw stems ───────────────────────────────────────────
        self._draw_stems_qp(painter, normal_mask, self._BLUE, 2.0, 0.80,
                            _text(self.language, 'candidate'), x2p, y2p, cr)
        self._draw_stems_qp(painter, unresolved_mask, self._AMBER, 2.8, 0.95,
                            _text(self.language, 'not_resolved'), x2p, y2p, cr)
        self._draw_stems_qp(painter, target_mask, self._RED, 3.4, 1.0,
                            _text(self.language, 'target_peak'), x2p, y2p, cr)

        # ── legend ───────────────────────────────────────────────
        ly = cr.top() + 8
        for mask, color, label in [(normal_mask, self._BLUE, _text(self.language, 'candidate')),
                                    (unresolved_mask, self._AMBER, _text(self.language, 'not_resolved')),
                                    (target_mask, self._RED, _text(self.language, 'target_peak'))]:
            if not mask.any():
                continue
            lx = cr.right() - 180
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(QtCore.QRectF(lx, ly, 12, 12))
            painter.setPen(self._TEXT)
            painter.setFont(QtGui.QFont('sans-serif', 9))
            painter.drawText(QtCore.QRectF(lx + 16, ly, 160, 14), QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, label)
            ly += 16

        # ── peak annotations ─────────────────────────────────────
        self._draw_annotations(painter, x2p, y2p, cr)

    def _draw_stems_qp(self, painter, mask, colour, lw, alpha, label, x2p, y2p, cr):
        """Draw vertical stem lines + diamond markers for one category."""
        if not mask.any():
            return
        xx = self.x[mask]
        yy = self.y[mask]
        floor_y = y2p(self._plot_floor)
        c = QtGui.QColor(colour)
        c.setAlphaF(alpha)
        painter.setPen(QtGui.QPen(c, lw))
        for xi, yi in zip(xx, yy):
            px = x2p(xi)
            py = y2p(yi)
            # stem line
            painter.drawLine(QtCore.QPointF(px, floor_y), QtCore.QPointF(px, py))
        # diamond markers
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(c)
        d = 4 + lw * 1.2
        for xi, yi in zip(xx, yy):
            px, py = x2p(xi), y2p(yi)
            diamond = QtGui.QPolygonF([
                QtCore.QPointF(px, py - d),
                QtCore.QPointF(px + d, py),
                QtCore.QPointF(px, py + d),
                QtCore.QPointF(px - d, py),
            ])
            painter.drawPolygon(diamond)

    def _draw_annotations(self, painter, x2p, y2p, cr):
        """Label top peaks with molecule formulas (up to MAX_LABELS)."""
        label_indices = self._label_indices()
        offsets = [(-18, -28), (0, -42), (18, -28), (-28, -46), (28, -46)]
        painter.setFont(QtGui.QFont('sans-serif', 9))
        for label_number, row_number in enumerate(label_indices):
            row = self._data.iloc[row_number]
            label = self._formula_label(row['molecule'])
            offset = offsets[label_number % len(offsets)]
            colour = self._RED if self._target_mask[row_number] else (
                self._AMBER if self._unresolved_mask[row_number] else self._MUTED
            )

            px = x2p(self.x[row_number])
            py = y2p(self.y[row_number])
            tx, ty = px + offset[0], py + offset[1]

            fm = painter.fontMetrics()
            tw = fm.horizontalAdvance(label) + 8
            th = fm.height() + 4

            # arrow line
            painter.setPen(QtGui.QPen(colour, 0.6))
            painter.drawLine(QtCore.QPointF(px, py), QtCore.QPointF(tx, ty + th / 2))

            # background box
            bgc = QtGui.QColor(255, 255, 255, 200)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(bgc)
            painter.drawRoundedRect(QtCore.QRectF(tx - tw / 2, ty, tw, th), 4, 4)

            # label text
            painter.setPen(colour)
            painter.drawText(QtCore.QRectF(tx - tw / 2, ty, tw, th),
                             QtCore.Qt.AlignCenter, label)

    @staticmethod
    def _nice_step(rough):
        """Return a 'nice' step size for axis ticks."""
        import math
        if rough <= 0:
            return 1.0
        exp = math.floor(math.log10(rough))
        frac = rough / (10 ** exp)
        for nice in (1.0, 2.0, 2.5, 5.0, 10.0):
            if frac <= nice:
                return nice * (10 ** exp)
        return 10 ** (exp + 1)


class _SpectrumCanvas(widgets.QWidget):
    """Inner widget that paints the chart (so it fills available space)."""

    def __init__(self, spectrum, parent=None):
        widgets.QWidget.__init__(self, parent=parent)
        self._spectrum = spectrum
        self.setMouseTracking(True)

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        try:
            self._spectrum._draw(p, self.rect())
        finally:
            p.end()

    def wheelEvent(self, event):
        if self._spectrum is None:
            return
        delta = event.angleDelta().y()
        if delta > 0:
            self._spectrum._on_zoom_in()
        elif delta < 0:
            self._spectrum._on_zoom_out()



class MainWindow(widgets.QMainWindow):
    """ Main window for interference calculator ui. """
    def __init__(self):
        widgets.QMainWindow.__init__(self)
        self.setWindowTitle(_text('en', 'window_title'))
        self.setWindowIcon(QtGui.QIcon(_icon))
        self.resize(1360, 780)
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(_APP_STYLESHEET)
        self.setCentralWidget(MainWidget(parent=self))


class MainWidget(widgets.QWidget):
    """ Central widget class for interference calculator ui. """
    MODE_PRESETS = {
        'GDMS': {
            'risk_preset': 'gdms',
            'charge_index': 1,
            'maxsize': 3,
            'mrp': 4000,
            'window_unit': 'ppm',
            'window': 2000.0,
            'atoms': 'Fe Ni Cu Zn Ar O H C N Cl S',
            'target': '56Fe or 75As or 55.9349',
        },
        'ICP-MS': {
            'risk_preset': 'icp-ms',
            'charge_index': 1,
            'maxsize': 3,
            'mrp': 3000,
            'window_unit': 'ppm',
            'window': 400.0,
            'atoms': 'Ar O H C N Cl S Ca Fe As Se',
            'target': '75As or 80Se or 51V',
        },
        'SIMS': {
            'risk_preset': 'sims',
            'charge_index': 0,
            'maxsize': 3,
            'mrp': 5000,
            'window_unit': 'ppm',
            'window': 200.0,
            'atoms': 'Si O H C N Al Fe Ca',
            'target': '28Si or 56Fe or 27Al',
        },
    }

    def __init__(self, parent=None):
        widgets.QWidget.__init__(self, parent=parent)
        self.language = 'en'
        self.result_metrics = {'kind': 'ready'}
        self.atoms = []
        self.charges = [1, 2]
        self.mz = ''
        self.mzrange = 0.3
        self.maxsize = 3

        # Inputs
        self.mode_input = widgets.QComboBox(parent=self)
        self.mode_input.addItem('GDMS', 'gdms')
        self.mode_input.addItem('ICP-MS', 'icp-ms')
        self.mode_input.addItem('SIMS', 'sims')

        self.atoms_input = ElementInput(parent=self)
        self.atoms_input.setPlaceholderText('Fe Ni Cu Zn Ar O H C N Cl S')

        self.element_set_input = widgets.QComboBox(parent=self)
        self.element_set_input.addItem(_text(self.language, 'add_set_empty'), ())
        self.element_set_input.addItem(_text(self.language, 'all_inorganic_elements'), _COMMON_INORGANIC_ELEMENTS)
        self.element_set_input.addItem(_text(self.language, 'ar_background'), ('Ar', 'O', 'H', 'C', 'N', 'Cl', 'S'))
        self.element_set_input.addItem(_text(self.language, 'light_background'), ('H', 'C', 'N', 'O'))
        self.element_set_input.addItem(_text(self.language, 'halogens_sulfur'), ('F', 'Cl', 'Br', 'I', 'S'))
        self.element_set_input.addItem(_text(self.language, 'transition_matrix'), ('Fe', 'Ni', 'Cu', 'Zn', 'Co', 'Cr', 'Mn'))
        self.element_set_input.addItem(_text(self.language, 'silicate_matrix'), ('Si', 'Al', 'Ca', 'Mg', 'Na', 'K', 'O'))

        self.maxsize_label = widgets.QLabel(_text(self.language, 'max_size'), parent=self)
        self.maxsize_input = widgets.QSpinBox(parent=self)
        self.maxsize_input.setValue(self.maxsize)
        self.maxsize_input.setRange(1, 8)

        self.charge_preset_label = widgets.QLabel(_text(self.language, 'ions'), parent=self)
        self.charge_preset_input = widgets.QComboBox(parent=self)
        self.charge_preset_input.addItem('1+', ((1,), '+'))
        self.charge_preset_input.addItem('1+, 2+', ((1, 2), '+'))
        self.charge_preset_input.addItem('1+, 2+, 3+', ((1, 2, 3), '+'))
        self.charge_preset_input.addItem('1-', ((1,), '-'))
        self.charge_preset_input.addItem(_text(self.language, 'neutral'), ((0,), 'o'))
        self.charge_preset_input.setCurrentIndex(1)

        self.mz_input = widgets.QLineEdit(parent=self)
        self.mz_input.setPlaceholderText('56Fe or 75As or 55.9349')

        self.mzrange_label = widgets.QLabel(_text(self.language, 'window_width'), parent=self)
        self.mzrange_input = widgets.QDoubleSpinBox(parent=self)
        self.mzrange_input.setValue(self.mzrange)
        self.mzrange_input.setSingleStep(0.1)
        self.mzrange_input.setDecimals(3)
        self.mzrange_input.setRange(0.001, 100.0)

        self.window_unit_input = widgets.QComboBox(parent=self)
        self.window_unit_input.addItem('ppm', 'ppm')
        self.window_unit_input.addItem('m/z', 'mz')
        self._applying_preset = False
        self._window_unit = _current_data(self.window_unit_input)

        self.instrument_mrp_label = widgets.QLabel(_text(self.language, 'instrument_mrp'), parent=self)
        self.instrument_mrp_input = widgets.QSpinBox(parent=self)
        self.instrument_mrp_input.setRange(0, 1000000)
        self.instrument_mrp_input.setValue(4000)
        self.instrument_mrp_input.setSingleStep(500)
        self.instrument_mrp_input.setSpecialValueText(_text(self.language, 'off'))

        self.language_label = widgets.QLabel(_text(self.language, 'language'), parent=self)
        self.language_label.setObjectName('appSubtitle')
        self.language_input = widgets.QComboBox(parent=self)
        self.language_input.addItem('English', 'en')
        self.language_input.addItem('中文', 'zh')

        # Action button
        self.interference_button = widgets.QPushButton(_text(self.language, 'calculate'), parent=self)
        self.interference_button.setObjectName('primaryButton')
        self.standard_ratio_button = widgets.QPushButton(_text(self.language, 'ratios'), parent=self)
        self.help_button = widgets.QToolButton(parent=self)
        self.help_button.setObjectName('iconButton')
        self.help_button.setIcon(QtGui.QIcon(_help_button_icon))
        self.spectrum_button = widgets.QToolButton(parent=self)
        self.spectrum_button.setObjectName('iconButton')
        self.spectrum_button.setIcon(QtGui.QIcon(_display_button_icon))

        # Table and spectrum output
        self.table_output = TableView(html_cols=None)
        self.spectrum_window = Spectrum(parent=self)

        # Show input errors on statusbar
        self.statusbar = self.parent().statusBar()
        self.statusbar.setStyleSheet('color: #475569;')

        # Layout objects
        self.header = widgets.QFrame(parent=self)
        self.header.setObjectName('header')
        self.header_layout = widgets.QHBoxLayout()
        self.header_layout.setContentsMargins(20, 10, 20, 10)
        self.header_title_layout = widgets.QVBoxLayout()
        self.header_title_layout.setSpacing(2)
        self.title_label = widgets.QLabel(_text(self.language, 'header_title'), parent=self.header)
        self.title_label.setObjectName('appTitle')
        self.subtitle_label = widgets.QLabel(_text(self.language, 'header_subtitle'), parent=self.header)
        self.subtitle_label.setObjectName('appSubtitle')
        self.header_title_layout.addWidget(self.title_label)
        self.header_title_layout.addWidget(self.subtitle_label)
        self.header_layout.addLayout(self.header_title_layout)
        self.header_layout.addStretch(1)
        self.header_language_layout = widgets.QHBoxLayout()
        self.header_language_layout.setSpacing(8)
        self.header_language_layout.addWidget(self.language_label)
        self.header_language_layout.addWidget(self.language_input)
        self.header_layout.addLayout(self.header_language_layout)
        self.header.setLayout(self.header_layout)

        self.control_panel = widgets.QFrame(parent=self)
        self.control_panel.setObjectName('controlPanel')
        self.control_panel.setMinimumWidth(420)
        self.control_panel.setMaximumWidth(480)
        self.control_panel_layout = widgets.QVBoxLayout()
        self.control_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.control_panel_layout.setSpacing(0)
        self.control_scroll = widgets.QScrollArea(parent=self.control_panel)
        self.control_scroll.setObjectName('controlScroll')
        self.control_scroll.setFrameShape(widgets.QFrame.NoFrame)
        self.control_scroll.setWidgetResizable(True)
        self.control_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.controls_content = widgets.QWidget(parent=self.control_scroll)
        self.controls_content.setObjectName('controlContent')
        self.control_layout = widgets.QVBoxLayout(self.controls_content)
        self.control_layout.setContentsMargins(14, 8, 14, 10)
        self.control_layout.setSpacing(8)

        self.workflow_group = widgets.QGroupBox(_text(self.language, 'workflow'))
        self.workflow_group.setObjectName('workflowGroup')
        self.workflow_layout = widgets.QGridLayout()
        self.workflow_layout.setContentsMargins(12, 16, 12, 8)
        self.workflow_layout.setHorizontalSpacing(8)
        self.workflow_layout.setVerticalSpacing(4)
        self.mode_label = self.create_field_label(_text(self.language, 'mode'))
        self.mode_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.workflow_layout.addWidget(self.mode_label, 0, 0)
        self.workflow_layout.addWidget(self.mode_input, 0, 1, 1, 2)
        self.target_label = self.create_field_label(_text(self.language, 'target'))
        self.target_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.workflow_layout.addWidget(self.target_label, 1, 0)
        self.workflow_layout.addWidget(self.mz_input, 1, 1, 1, 2)
        self.window_width_label = self.create_field_label(_text(self.language, 'window_width'))
        self.window_width_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.workflow_layout.addWidget(self.window_width_label, 2, 0)
        self.target_range_layout = widgets.QHBoxLayout()
        self.target_range_layout.setSpacing(6)
        self.target_range_layout.addWidget(self.mzrange_input, stretch=1)
        self.target_range_layout.addWidget(self.window_unit_input)
        self.workflow_layout.addLayout(self.target_range_layout, 2, 1, 1, 2)
        self.target_hint_label = widgets.QLabel(parent=self.workflow_group)
        self.target_hint_label.setObjectName('helperText')
        self.target_hint_label.setWordWrap(True)
        self.workflow_layout.addWidget(self.target_hint_label, 3, 1, 1, 2)
        self.target_hint_label.hide()

        self.ion_model_label = self.create_field_label(_text(self.language, 'ion_model'))
        self.ion_model_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.parameter_row_layout = widgets.QHBoxLayout()
        self.parameter_row_layout.setSpacing(8)
        self.charge_field_layout = widgets.QVBoxLayout()
        self.charge_field_layout.setSpacing(3)
        self.charge_preset_label.setObjectName('fieldLabel')
        self.charge_field_layout.addWidget(self.charge_preset_label)
        self.charge_field_layout.addWidget(self.charge_preset_input)
        self.maxsize_field_layout = widgets.QVBoxLayout()
        self.maxsize_field_layout.setSpacing(3)
        self.maxsize_label.setObjectName('fieldLabel')
        self.maxsize_field_layout.addWidget(self.maxsize_label)
        self.maxsize_field_layout.addWidget(self.maxsize_input)
        self.mrp_field_layout = widgets.QVBoxLayout()
        self.mrp_field_layout.setSpacing(3)
        self.instrument_mrp_label.setObjectName('fieldLabel')
        self.mrp_field_layout.addWidget(self.instrument_mrp_label)
        self.mrp_field_layout.addWidget(self.instrument_mrp_input)
        self.parameter_row_layout.addLayout(self.charge_field_layout, stretch=2)
        self.parameter_row_layout.addLayout(self.maxsize_field_layout, stretch=1)
        self.parameter_row_layout.addLayout(self.mrp_field_layout, stretch=2)
        self.workflow_layout.addWidget(self.ion_model_label, 4, 0)
        self.workflow_layout.addLayout(self.parameter_row_layout, 4, 1, 1, 2)
        self.workflow_layout.setColumnMinimumWidth(0, 70)
        self.workflow_layout.setColumnStretch(1, 1)
        self.workflow_group.setLayout(self.workflow_layout)

        self.atoms_group = widgets.QGroupBox(_text(self.language, 'sample_plasma'))
        self.atoms_layout = widgets.QVBoxLayout()
        self.atoms_layout.setContentsMargins(14, 16, 14, 10)
        self.atoms_layout.setSpacing(5)
        self.elements_label = self.create_field_label(_text(self.language, 'elements'))
        self.add_set_label = self.create_field_label(_text(self.language, 'add_set'))
        self.atoms_layout.addWidget(self.elements_label)
        self.atoms_layout.addWidget(self.atoms_input)
        self.element_set_row_layout = widgets.QHBoxLayout()
        self.element_set_row_layout.setSpacing(8)
        self.add_set_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.add_set_label.setMinimumWidth(70)
        self.element_set_row_layout.addWidget(self.add_set_label)
        self.element_set_row_layout.addWidget(self.element_set_input, stretch=1)
        self.atoms_layout.addLayout(self.element_set_row_layout)
        self.atoms_group.setLayout(self.atoms_layout)

        self.button_bar = widgets.QFrame(parent=self.control_panel)
        self.button_bar.setObjectName('actionBar')
        self.button_layout = widgets.QHBoxLayout()
        self.button_layout.setContentsMargins(14, 8, 14, 10)
        self.button_layout.setSpacing(8)
        self.button_layout.addWidget(self.interference_button, stretch=1)
        self.button_layout.addWidget(self.standard_ratio_button)
        self.button_layout.addWidget(self.spectrum_button)
        self.button_layout.addWidget(self.help_button)
        self.button_bar.setLayout(self.button_layout)

        self.control_layout.addWidget(self.workflow_group)
        self.control_layout.addWidget(self.atoms_group)
        self.control_layout.addStretch(1)
        self.control_scroll.setWidget(self.controls_content)
        self.control_panel_layout.addWidget(self.control_scroll, stretch=1)
        self.control_panel_layout.addWidget(self.button_bar)
        self.control_panel.setLayout(self.control_panel_layout)

        self.results_panel = widgets.QWidget(parent=self)
        self.results_panel.setObjectName('resultsPanel')
        self.results_layout = widgets.QVBoxLayout()
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(0)
        self.results_header = widgets.QFrame(parent=self.results_panel)
        self.results_header.setObjectName('resultsHeader')
        self.results_header_layout = widgets.QHBoxLayout()
        self.results_header_layout.setContentsMargins(16, 10, 16, 10)
        self.results_header_layout.setSpacing(8)
        self.results_title_label = widgets.QLabel(parent=self.results_header)
        self.results_title_label.setObjectName('resultsTitle')
        self.results_header_layout.addWidget(self.results_title_label)
        self.results_header_layout.addStretch(1)
        self.mode_metric_label = self.create_metric_label(parent=self.results_header)
        self.window_metric_label = self.create_metric_label(parent=self.results_header)
        self.mrp_metric_label = self.create_metric_label(parent=self.results_header)
        self.count_metric_label = self.create_metric_label(parent=self.results_header)
        self.results_header_layout.addWidget(self.mode_metric_label)
        self.results_header_layout.addWidget(self.window_metric_label)
        self.results_header_layout.addWidget(self.mrp_metric_label)
        self.results_header_layout.addWidget(self.count_metric_label)
        self.results_header.setLayout(self.results_header_layout)

        self.empty_state = widgets.QFrame(parent=self.results_panel)
        self.empty_state.setObjectName('emptyState')
        self.empty_state_layout = widgets.QVBoxLayout()
        self.empty_state_layout.setContentsMargins(32, 32, 32, 32)
        self.empty_state_layout.addStretch(1)
        self.empty_title_label = widgets.QLabel(parent=self.empty_state)
        self.empty_title_label.setObjectName('emptyTitle')
        self.empty_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.empty_body_label = widgets.QLabel(parent=self.empty_state)
        self.empty_body_label.setObjectName('emptyBody')
        self.empty_body_label.setAlignment(QtCore.Qt.AlignCenter)
        self.empty_body_label.setWordWrap(True)
        self.empty_state_layout.addWidget(self.empty_title_label)
        self.empty_state_layout.addSpacing(8)
        self.empty_state_layout.addWidget(self.empty_body_label)
        self.empty_state_layout.addStretch(2)
        self.empty_state.setLayout(self.empty_state_layout)

        self.results_stack = widgets.QStackedWidget(parent=self.results_panel)
        self.results_stack.addWidget(self.empty_state)
        self.results_stack.addWidget(self.table_output)
        self.results_stack.setCurrentWidget(self.empty_state)

        self.results_layout.addWidget(self.results_header)
        self.results_layout.addWidget(self.results_stack, stretch=1)
        self.results_panel.setLayout(self.results_layout)

        self.body_splitter = widgets.QSplitter(QtCore.Qt.Horizontal, parent=self)
        self.body_splitter.addWidget(self.control_panel)
        self.body_splitter.addWidget(self.results_panel)
        self.body_splitter.setStretchFactor(0, 0)
        self.body_splitter.setStretchFactor(1, 1)
        self.body_splitter.setSizes([420, 940])

        self.layout = widgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.body_splitter, stretch=1)
        self.setLayout(self.layout)

        # Connect
        self.interference_button.clicked.connect(self.calculate_interference)
        self.standard_ratio_button.clicked.connect(self.show_standard_ratio)
        self.help_button.clicked.connect(self.show_help)
        self.language_input.currentIndexChanged.connect(self.apply_language)
        self.mode_input.currentIndexChanged.connect(self.apply_mode_preset)
        self.window_unit_input.currentIndexChanged.connect(self.apply_window_unit)
        self.element_set_input.activated.connect(self.add_element_set)
        self.atoms_input.editingFinished.connect(self.check_atoms_input)
        self.mz_input.editingFinished.connect(self.check_mz_input)
        self.mzrange_input.valueChanged.connect(self.update_result_summary)
        self.instrument_mrp_input.valueChanged.connect(self.update_result_summary)
        self.spectrum_button.clicked.connect(self.toggle_spectrum)

        # Set jump order for tab
        self.setTabOrder(self.language_input, self.mode_input)
        self.setTabOrder(self.mode_input, self.mz_input)
        self.setTabOrder(self.mz_input, self.mzrange_input)
        self.setTabOrder(self.mzrange_input, self.window_unit_input)
        self.setTabOrder(self.window_unit_input, self.atoms_input)
        self.setTabOrder(self.atoms_input, self.element_set_input)
        self.setTabOrder(self.element_set_input, self.charge_preset_input)
        self.setTabOrder(self.charge_preset_input, self.maxsize_input)
        self.setTabOrder(self.maxsize_input, self.instrument_mrp_input)
        self.setTabOrder(self.instrument_mrp_input, self.interference_button)
        self.setTabOrder(self.interference_button, self.standard_ratio_button)
        self.setTabOrder(self.standard_ratio_button, self.spectrum_button)
        self.setTabOrder(self.spectrum_button, self.help_button)
        self.setTabOrder(self.help_button, self.table_output)

        self.apply_mode_preset()
        self.apply_language()

    def _tr(self, key):
        """Return UI text for the active language."""
        return _text(self.language, key)

    def create_metric_label(self, parent=None):
        """Create a compact result metric chip."""
        label = widgets.QLabel(parent=parent)
        label.setObjectName('metricChip')
        label.setMinimumHeight(28)
        label.setAlignment(QtCore.Qt.AlignCenter)
        return label

    def create_field_label(self, text, parent=None):
        """Create a consistent label for stacked control fields."""
        label = widgets.QLabel(text, parent=parent)
        label.setObjectName('fieldLabel')
        return label

    def apply_language(self, index=None):
        """Apply selected UI language without changing calculation inputs."""
        self.language = _current_data(self.language_input) or 'en'
        window = self.window()
        if window is not None:
            window.setWindowTitle(self._tr('window_title'))

        self.element_set_input.setItemText(0, self._tr('add_set_empty'))
        self.element_set_input.setItemText(1, self._tr('all_inorganic_elements'))
        self.element_set_input.setItemText(2, self._tr('ar_background'))
        self.element_set_input.setItemText(3, self._tr('light_background'))
        self.element_set_input.setItemText(4, self._tr('halogens_sulfur'))
        self.element_set_input.setItemText(5, self._tr('transition_matrix'))
        self.element_set_input.setItemText(6, self._tr('silicate_matrix'))
        self.charge_preset_input.setItemText(4, self._tr('neutral'))
        self.instrument_mrp_input.setSpecialValueText(self._tr('off'))

        self.title_label.setText(self._tr('header_title'))
        self.subtitle_label.setText(self._tr('header_subtitle'))
        self.language_label.setText(self._tr('language'))
        self.workflow_group.setTitle(self._tr('workflow'))
        self.mode_label.setText(self._tr('mode'))
        self.target_label.setText(self._tr('target'))
        self.window_width_label.setText(self._tr('window_width'))
        self.target_hint_label.setText(self._tr('target_hint'))
        self.atoms_group.setTitle(self._tr('sample_plasma'))
        self.elements_label.setText(self._tr('elements'))
        self.add_set_label.setText(self._tr('add_set'))
        self.ion_model_label.setText(self._tr('ion_model'))
        self.charge_preset_label.setText(self._tr('ions'))
        self.maxsize_label.setText(self._tr('max_size'))
        self.mzrange_label.setText(self._tr('window_width'))
        self.instrument_mrp_label.setText(self._tr('instrument_mrp'))
        self.interference_button.setText(self._tr('calculate'))
        self.standard_ratio_button.setText(self._tr('ratios'))
        self.results_title_label.setText(self._tr('results_title'))
        self.empty_title_label.setText(self._tr('empty_title'))
        self.empty_body_label.setText(self._tr('empty_body'))
        self.spectrum_button.setAccessibleName(self._tr('open_spectrum'))
        self.help_button.setAccessibleName(self._tr('open_help'))

        self.set_tooltips()
        self.spectrum_window.set_language(self.language)
        self.refresh_table_language()
        self.update_result_summary()

    def set_tooltips(self):
        """Set localized widget tooltips."""
        self.mode_input.setToolTip(tooltip_text(self.language, 'mode'))
        self.atoms_input.setToolTip(tooltip_text(self.language, 'atoms'))
        self.element_set_input.setToolTip(tooltip_text(self.language, 'element_set'))
        self.charge_preset_input.setToolTip(tooltip_text(self.language, 'charge_preset'))
        self.mz_input.setToolTip(tooltip_text(self.language, 'mz'))
        self.mzrange_input.setToolTip(tooltip_text(self.language, 'mzrange'))
        self.window_unit_input.setToolTip(tooltip_text(self.language, 'window_unit'))
        self.maxsize_input.setToolTip(tooltip_text(self.language, 'maxsize'))
        self.instrument_mrp_input.setToolTip(tooltip_text(self.language, 'instrument_mrp'))
        self.interference_button.setToolTip(tooltip_text(self.language, 'interference_button'))
        self.standard_ratio_button.setToolTip(tooltip_text(self.language, 'standard_ratio_button'))
        self.spectrum_button.setToolTip(tooltip_text(self.language, 'spectrum_button'))
        self.help_button.setToolTip(tooltip_text(self.language, 'help_button'))

    def refresh_table_language(self):
        """Refresh localized table headers and display values."""
        model = self.table_output.model()
        if model is None or not hasattr(model, 'language'):
            return
        model.language = self.language
        if model.columnCount() > 0:
            model.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, model.columnCount() - 1)
        if model.rowCount() > 0 and model.columnCount() > 0:
            top_left = model.index(0, 0)
            bottom_right = model.index(model.rowCount() - 1, model.columnCount() - 1)
            model.dataChanged.emit(top_left, bottom_right)
        self.resize_table_sections()

    def update_result_summary(self, *args):
        """Refresh compact mode/window/result context above the table."""
        if not hasattr(self, 'mode_metric_label'):
            return

        mode = self.mode_input.currentText()
        unit = self.window_unit_input.currentText()
        window_value = self.mzrange_input.value()
        if _current_data(self.window_unit_input) == 'ppm':
            window = '{:.1f} {}'.format(window_value, unit)
        else:
            window = '{:.6f} {}'.format(window_value, unit)

        mrp_value = self.instrument_mrp_input.value()
        mrp = self._tr('off') if mrp_value == 0 else '{:d}'.format(mrp_value)
        metrics = getattr(self, 'result_metrics', {'kind': 'ready'})
        if metrics.get('kind') == 'interference':
            count_text = '{}: {}'.format(self._tr('summary_candidates'), metrics.get('candidate_count', 0))
            if metrics.get('unresolved_count', 0):
                count_text = '{} · {}: {}'.format(
                    count_text, self._tr('summary_unresolved'), metrics.get('unresolved_count', 0)
                )
        elif metrics.get('kind') == 'ratios':
            count_text = '{}: {}'.format(self._tr('summary_isotopes'), metrics.get('isotope_count', 0))
        else:
            count_text = self._tr('summary_ready')

        self.mode_metric_label.setText('{}: {}'.format(self._tr('summary_mode'), mode))
        self.window_metric_label.setText('{}: {}'.format(self._tr('summary_window'), window))
        self.mrp_metric_label.setText('{}: {}'.format(self._tr('summary_mrp'), mrp))
        self.count_metric_label.setText(count_text)

    def apply_mode_preset(self, index=None):
        """ Apply UI defaults for the selected calculation preset. """
        preset = self.MODE_PRESETS.get(self.mode_input.currentText())
        self._applying_preset = True
        try:
            if preset:
                self.charge_preset_input.setCurrentIndex(preset['charge_index'])
                self.maxsize_input.setValue(preset['maxsize'])
                self.instrument_mrp_input.setValue(preset['mrp'])
                self.window_unit_input.setCurrentIndex(
                    self.window_unit_input.findText(preset['window_unit'])
                )
                self.apply_window_unit()
                self.mzrange_input.setValue(preset['window'])
                self.atoms_input.setPlaceholderText(preset['atoms'])
                self.mz_input.setPlaceholderText(preset['target'])
            else:
                self.charge_preset_input.setCurrentIndex(3)
                self.maxsize_input.setValue(5)
                self.instrument_mrp_input.setValue(0)
                self.window_unit_input.setCurrentIndex(self.window_unit_input.findText('ppm'))
                self.apply_window_unit()
                self.mzrange_input.setValue(600.0)
                self.atoms_input.setPlaceholderText(self._tr('general_atoms_placeholder'))
                self.mz_input.setPlaceholderText(self._tr('general_target_placeholder'))
        finally:
            self._applying_preset = False
            self._window_unit = _current_data(self.window_unit_input)
            self.update_result_summary()

    def apply_window_unit(self, index=None):
        """Adjust range input precision and convert m/z/ppm window width values."""
        new_unit = _current_data(self.window_unit_input)
        old_unit = getattr(self, '_window_unit', new_unit)
        old_value = self.mzrange_input.value()
        converted_value = None
        if not self._applying_preset and old_unit != new_unit:
            converted_value = self.convert_window_value(old_value, old_unit, new_unit)

        if new_unit == 'ppm':
            self.mzrange_input.setDecimals(1)
            self.mzrange_input.setRange(0.1, 1000000.0)
            self.mzrange_input.setSingleStep(10.0)
        else:
            self.mzrange_input.setDecimals(6)
            self.mzrange_input.setRange(0.0001, 100.0)
            self.mzrange_input.setSingleStep(0.001)

        if converted_value is not None:
            self.mzrange_input.setValue(converted_value)
        self._window_unit = new_unit
        self.update_result_summary()

    def convert_window_value(self, value, old_unit, new_unit):
        """Convert current full-window value between m/z and ppm."""
        if old_unit == new_unit:
            return value

        if not self.check_charges_input() or not self.check_mz_input():
            self.warn(self._tr('convert_invalid_target'))
            return None

        target_mz = self.target_mz()
        if not target_mz:
            self.warn(self._tr('convert_target_required'))
            return None

        if old_unit == 'mz' and new_unit == 'ppm':
            return value / target_mz * 1e6
        if old_unit == 'ppm' and new_unit == 'mz':
            return target_mz * value / 1e6
        return None

    def add_element_set(self, index):
        """Append a selected element set to the element input."""
        elements = _current_data(self.element_set_input)
        if not elements:
            return
        current = re.findall(_isotope_rx, str(self.atoms_input.text()))
        for element in elements:
            if element not in current:
                current.append(element)
        self.atoms_input.setText(' '.join(current))
        self.element_set_input.setCurrentIndex(0)

    def warn(self, text, time=5000):
        """ Display a warning message in the status bar. """
        self.statusbar.setStyleSheet('color: #dc2626; font-weight: 500;')
        self.statusbar.showMessage(text, msecs=time)

    def set_status(self, text, time=5000):
        """Display a neutral status message in the status bar."""
        self.statusbar.setStyleSheet('color: #475569; font-weight: 400;')
        self.statusbar.showMessage(text, msecs=time)

    def resize_table_sections(self):
        """ Resize result table columns for the active Qt version. """
        header = self.table_output.horizontalHeader()
        model = self.table_output.model()
        try:
            for column in range(model.columnCount()):
                header.setSectionResizeMode(column, widgets.QHeaderView.Interactive)
        except AttributeError:
            for column in range(model.columnCount()):
                header.setResizeMode(column, widgets.QHeaderView.Interactive)

        widths = {
            'molecule': 190,
            'ion': 190,
            'isotope': 110,
            'mass/charge': 110,
            'm/z': 96,
            '\u0394mass/charge': 125,
            '\u0394m/z': 92,
            '\u0394ppm': 85,
            'mz/\u0394mz (MRP)': 120,
            'MRP': 78,
            'probability': 110,
            'prob.': 98,
            'formation factor': 120,
            'relative risk': 110,
            'risk': 96,
            'resolved': 85,
            'ok': 54,
            'type': 102,
            'charge': 70,
            'z': 44,
            'mass': 110,
            'abundance': 110,
            'ratio': 95,
            'inverse ratio': 120,
            'standard': 150,
        }
        for column in range(model.columnCount()):
            colname = model._data.columns[column]
            self.table_output.setColumnWidth(column, widths.get(colname, 100))

    def check_atoms_input(self):
        """ Validate input for atoms_input.
            Returns True on proper validation, False on error.
        """
        atoms = re.findall(_isotope_rx, str(self.atoms_input.text()))
        if not atoms:
            self.warn(self._tr('empty_atoms'))
            return False
        for a in atoms:
            if not (periodic_table['element'] == a).any(): 
                self.warn(self._tr('missing_element').format(a))
                return False
        self.atoms = atoms
        return True

    def check_charges_input(self):
        """ Read charge settings from the ion preset selector. """
        self.charges, self.chargesign = _current_data(self.charge_preset_input)
        return True

    def target_mz(self):
        """Return target m/z for window conversion."""
        if self.mz is None:
            return None
        if isinstance(self.mz, (int, float)):
            return float(self.mz)

        molecule = Molecule(self.mz)
        if not molecule.charge and self.chargesign not in ('o', '0'):
            if self.charges[0] == 1:
                target = '{} {}'.format(self.mz, self.chargesign)
            else:
                target = '{} {}{}'.format(self.mz, self.charges[0], self.chargesign)
            molecule = Molecule(target)
        if molecule.charge:
            return molecule.mass / molecule.charge
        return molecule.mass

    def targetrange_mz(self):
        """Return selected full target window as a half-width in m/z units."""
        half_window = self.mzrange_input.value() / 2.0
        if _current_data(self.window_unit_input) != 'ppm':
            return half_window

        target_mz = self.target_mz()
        if target_mz is None:
            self.warn(self._tr('ppm_requires_target'))
            return None
        return target_mz * half_window / 1e6

    def check_mz_input(self):
        """ Validate input for mz_input.
            Returns True on correct input, False on error.
        """
        mz = str(self.mz_input.text())
        if mz == '':
            self.mz = None
        else:
            try:
                self.mz = float(mz)
            except ValueError:
                try:
                    m = Molecule(mz)
                except:
                    self.warn(self._tr('invalid_target'))
                    return False
                else:
                    self.mz = mz
        return True

    def keyPressEvent(self, event):
        """ Link enter/return to calculate button,
            cmd/ctrl-enter/return to standard ratio,
            cmd/ctrl-c to table data copy,
            cmd/ctrl-a to select all in table,
            cmd/ctrl-h to open help,
            cmd/ctrl-d to display spectrum.
        """
        key = event.key()
        mod = event.modifiers()
        if (key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return):
            if mod == QtCore.Qt.ControlModifier:
                self.show_standard_ratio()
            else:
                self.calculate_interference()
        elif (key == QtCore.Qt.Key_C and mod == QtCore.Qt.ControlModifier):
            self.table_output.copy()
        elif (key == QtCore.Qt.Key_A and mod == QtCore.Qt.ControlModifier):
            self.table_output.selectAll()
        elif (key == QtCore.Qt.Key_H and mod == QtCore.Qt.ControlModifier):
            self.show_help()
        elif (key == QtCore.Qt.Key_D and mod == QtCore.Qt.ControlModifier):
            self.toggle_spectrum()
        else:
            super(MainWidget, self).keyPressEvent(event)

    @QtCore.pyqtSlot()
    def calculate_interference(self):
        """ Take input, calculate mass spectrum, display in table. """
        if not (self.check_atoms_input() and
                self.check_charges_input() and
                self.check_mz_input()):
            return

        if not self.mz:
            qmsg = widgets.QMessageBox(self)
            qmsg.setText(self._tr('long_warning'))
            qmsg.setInformativeText(mz_warning_for(self.language))
            qmsg.setIcon(widgets.QMessageBox.Warning)
            qmsg.setStandardButtons(widgets.QMessageBox.Ok|widgets.QMessageBox.Cancel)
            if qmsg.exec_() == widgets.QMessageBox.Cancel:
                return

        self.maxsize = self.maxsize_input.value()
        self.mzrange = self.targetrange_mz()
        if self.mzrange is None:
            return

        risk_preset = _current_data(self.mode_input)
        self.interference_button.setEnabled(False)
        widgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            if risk_preset:
                data = inorganic_interference(self.atoms, self.mz, targetrange=self.mzrange,
                    maxsize=self.maxsize, charge=self.charges, chargesign=self.chargesign,
                    risk_preset=risk_preset)
            else:
                data = interference(self.atoms, self.mz, targetrange=self.mzrange,
                    maxsize=self.maxsize, charge=self.charges, chargesign=self.chargesign)
                data['type'] = 'enumerated'
                data['formation factor'] = ''
                data['relative risk'] = data['probability']
        finally:
            widgets.QApplication.restoreOverrideCursor()
            self.interference_button.setEnabled(True)

        target_mask = data['target'].astype(bool)
        if target_mask.any():
            target_mz = data.loc[target_mask, 'mass/charge'].iat[0]
        else:
            target_mz = np.nan

        if target_mz:
            data['\u0394ppm'] = data['mass/charge diff'] / target_mz * 1e6
        else:
            data['\u0394ppm'] = np.nan

        instrument_mrp = self.instrument_mrp_input.value()
        if instrument_mrp:
            data['resolved'] = (data['MRP'] <= instrument_mrp).astype(object)
            data.loc[target_mask, 'resolved'] = ''
        else:
            data['resolved'] = ''

        data.index = range(1, data.shape[0] + 1)
        spectrum_data = data.copy()
        spectrum_data.attrs['window_half_mz'] = float(self.mzrange)
        if target_mz and np.isfinite(target_mz):
            spectrum_data.attrs['window_half_ppm'] = float(self.mzrange / target_mz * 1e6)

        display_data = data[['molecule', 'type', 'charge', 'mass/charge',
                             'mass/charge diff', '\u0394ppm', 'MRP',
                             'probability', 'relative risk', 'resolved',
                             'target']].copy()
        display_data.columns = ['ion', 'type', 'z', 'm/z', '\u0394m/z',
                                '\u0394ppm', 'MRP', 'prob.', 'risk', 'ok',
                                'target']

        model = TableModel(display_data, table='interference', language=self.language)
        self.table_output.setModel(model)
        self.table_output.setColumnHidden(display_data.columns.get_loc('target'), True)
        self.resize_table_sections()

        candidate_count = int((~display_data['target'].astype(bool)).sum())
        unresolved_count = int(sum((value != '') and not bool(value) for value in display_data['ok']))
        self.result_metrics = {
            'kind': 'interference',
            'candidate_count': candidate_count,
            'unresolved_count': unresolved_count,
        }
        self.results_stack.setCurrentWidget(self.table_output)
        self.update_result_summary()
        self.spectrum_window.plot_spectrum(spectrum_data)
        self.set_status(self._tr('candidate_count').format(candidate_count), time=5000)

    @QtCore.pyqtSlot()
    def show_standard_ratio(self):
        """ Show the standard ratios. """
        if not self.check_atoms_input():
            return

        data = standard_ratio(self.atoms)
        data['target'] = False
        if self.check_mz_input() and isinstance(self.mz, str):
            m = Molecule(self.mz)
            target_data = standard_ratio(m.elements)
            target_data['target'] = True
            data = pd.concat([data, target_data])
        data.index = range(1, data.shape[0] + 1)

        model = TableModel(data, table='std_ratios', language=self.language)
        self.table_output.setModel(model)
        self.table_output.setColumnHidden(data.columns.get_loc('target'), True)
        self.resize_table_sections()
        self.result_metrics = {'kind': 'ratios', 'isotope_count': data.shape[0]}
        self.results_stack.setCurrentWidget(self.table_output)
        self.update_result_summary()
        self.set_status(self._tr('isotope_count').format(data.shape[0]), time=5000)

    @QtCore.pyqtSlot()
    def show_help(self):
        """ Display help window. """
        dialog = widgets.QDialog(parent=self)
        dialog.resize(720, 760)
        dialog.setWindowTitle(self._tr('help_title'))
        icon = QtGui.QIcon(_icon)
        btn = widgets.QPushButton(icon, '', parent=dialog)
        btn.setStyleSheet('border: none')
        btn.setFixedSize(128, 128)
        btn.setIconSize(QtCore.QSize(128, 128))
        btn.move(20, 20)
        text = widgets.QTextBrowser(parent=dialog)
        text.setHtml(help_text_for(self.language).format(__version__))
        text.setOpenExternalLinks(True)
        text.setFrameShape(widgets.QFrame.NoFrame)
        text.setStyleSheet('background: #ffffff; padding: 16px;')
        layout = widgets.QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(text)
        btn.raise_()
        dialog.exec_()

    @QtCore.pyqtSlot()
    def toggle_spectrum(self):
        """ Show interference data in a spectrum. """
        if self.spectrum_window.isHidden():
            self.spectrum_window.show()
        else:
            self.spectrum_window.hide()


def run():
    """ Run the gui. """
    # Enable high-DPI scaling for 2K/4K displays.
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = widgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.move(200, 100)
    mainwindow.show()

    # Place spectrum window next to the main window,
    # but clamp it to stay within the available screen area.
    spec_win = mainwindow.centralWidget().spectrum_window
    screen = app.primaryScreen()
    sg = screen.availableGeometry() if screen else None

    mw_geo = mainwindow.frameGeometry()
    sx = mw_geo.x() + mw_geo.width()
    sy = mw_geo.y()

    if sg is not None:
        spec_w = spec_win.width()
        spec_h = spec_win.height()
        # Clamp to screen
        sx = max(sg.left(), min(sx, sg.right() - spec_w))
        sy = max(sg.top(), min(sy, sg.bottom() - spec_h))
        # If the main window + spectrum don't fit in one row, stack vertically
        if spec_w > sg.width() - 100:
            sx = sg.left() + 50
            sy = mw_geo.y() + mw_geo.height() + 30

    spec_win.move(sx, sy)
    sys.exit(app.exec_())


if __name__ == '__main__' or getattr(sys, 'frozen', False):
    run()
