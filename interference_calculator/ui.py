#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" GUI for interference calculator. """
from __future__ import division

import os
import re
import sys


if __package__ in (None, '') and not getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

from importlib import resources
from pyparsing import ParseException
from interference_calculator.gdms_import import (
    extract_profile_elements,
    parse_gdms_profile_xlsx,
)
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
        'sweep': 'sweep',
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
        'interferences': 'Interferences',
        'convert_invalid_target': 'Enter a valid target before converting the window unit.',
        'convert_target_required': 'Enter a target peak before converting the window unit.',
        'empty_atoms': 'Enter at least one element or isotope.',
        'missing_element': '{} is not an element or missing from the periodic table.',
        'ppm_requires_target': 'A ppm window requires a target peak.',
        'invalid_target': 'Enter target as a number or as a molecular formula.',
        'candidate_count': '{} candidate peaks',
        'isotope_count': '{} isotope rows',
        'interference_restored': 'Restored interference results.',
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
        'export': 'Export',
        'export_csv': 'Export as CSV…',
        'export_xlsx': 'Export as Excel…',
        'export_no_data': 'No data to export.',
        'filter_results': 'Filter results…',
        'show_all_columns': 'Show all columns',
        'copy': 'Copy',
        'select_all': 'Select All',
        'add_element': '+ Add',
        'add_element_tooltip': 'Open element selector',
        'elements_empty_hint': 'Click Add to choose elements',
        'remove_element_tooltip': 'Double-click to remove',
        'select_elements_title': 'Select elements',
        'search_elements': 'Search elements…',
        'select_all_visible': 'Select visible',
        'clear_selection': 'Clear',
        'add_selected': 'Add selected',
        'all_elements_added': 'All elements have been added.',
        'target_element_placeholder': 'Select element…',
        'target_isotope_placeholder': 'Select isotope…',
        'import_gdms': 'Import GDMS',
        'imported_target_placeholder': 'Imported targets…',
        'gdms_profile_files_filter': 'GDMS Excel Profiles (*.xlsx *.xlsm);;All Files (*)',
        'gdms_import_missing': 'GDMS Excel import requires openpyxl.\n\nInstall or update dependencies: pip install -e .',
        'gdms_import_error': 'GDMS Import Error',
        'gdms_import_no_profiles': 'No GDMS isotope profiles were found in this file.',
        'gdms_import_loaded': 'Imported {} targets and {} elements from {}.',
        'gdms_import_target_status': 'Selected imported target {}.',
        'gdms_observed': 'observed',
        'gdms_fwhm': 'FWHM',
        'zoom_out_y': 'Zoom out (Y axis)',
        'zoom_in_y': 'Zoom in (Y axis)',
        'reset_view': 'Reset view',
        'export_spectrum': 'Export spectrum',
        'export_spectrum_tooltip': 'Export current spectrum as PNG',
        'spectrum_png_filter': 'PNG Image (*.png)',
        'spectrum_exported': 'Spectrum exported to {}',
        'spectrum_export_error': 'Spectrum export error',
        'spectrum_mrp_band': 'MRP {} unresolved band',
        'spectrum_peak_selected': 'Selected spectrum peak row {}.',
        'spectrum_source_row': 'row',
        'filter_unresolved': 'Unresolved',
        'filter_risk_high': 'Risk > 0.01',
        'filter_risk_medium': 'Risk > 0.001',
        'filter_atomic': 'Atomic',
        'filter_oxide': 'Oxide',
        'filter_hydride': 'Hydride',
        'filter_sulfide_halide': 'Sulfide|Halide',
        'filter_doubly': '2+',
        'filter_plasma': 'Plasma',
        'filter_target_peak': 'Target peak',
        'element_count': '{} elements',
        'element_count_error': '{} elements · {}',
        'calculating': 'Calculating…',
        'exported_rows': 'Exported {} rows to {}',
        'export_error': 'Export Error',
        'missing_dependency': 'Missing dependency',
        'excel_export_missing': 'Excel export requires openpyxl.\n\nInstall or update dependencies: pip install -e .\n\nContinue with CSV instead?',
        'csv_files_filter': 'CSV Files (*.csv)',
        'excel_files_filter': 'Excel Files (*.xlsx)',
        'calculation_error': 'Calculation Error',
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
        'sweep': '扫描窗口',
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
        'interferences': '干扰峰',
        'convert_invalid_target': '切换窗口单位前，请先输入有效目标峰。',
        'convert_target_required': '切换窗口单位前，请先输入目标峰。',
        'empty_atoms': '请至少输入一个元素或同位素。',
        'missing_element': '{} 不是有效元素，或当前同位素库中缺少该元素。',
        'ppm_requires_target': 'ppm 窗口需要先输入目标峰。',
        'invalid_target': '目标峰请输入数值或分子式。',
        'candidate_count': '{} 个候选峰',
        'isotope_count': '{} 行同位素数据',
        'interference_restored': '已恢复干扰峰结果。',
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
        'export': '导出',
        'export_csv': '导出为 CSV…',
        'export_xlsx': '导出为 Excel…',
        'export_no_data': '没有数据可导出。',
        'filter_results': '筛选结果…',
        'show_all_columns': '显示全部列',
        'copy': '复制',
        'select_all': '全选',
        'add_element': '+ 添加',
        'add_element_tooltip': '打开元素选择器',
        'elements_empty_hint': '点击“添加”选择元素',
        'remove_element_tooltip': '双击移除',
        'select_elements_title': '选择元素',
        'search_elements': '搜索元素…',
        'select_all_visible': '选择当前可见',
        'clear_selection': '清除选择',
        'add_selected': '添加所选',
        'all_elements_added': '所有元素都已添加。',
        'target_element_placeholder': '选择元素…',
        'target_isotope_placeholder': '选择同位素…',
        'import_gdms': '导入GDMS',
        'imported_target_placeholder': '导入的目标峰…',
        'gdms_profile_files_filter': 'GDMS Excel 谱图 (*.xlsx *.xlsm);;所有文件 (*)',
        'gdms_import_missing': 'GDMS Excel 导入需要 openpyxl。\n\n安装或更新依赖：pip install -e .',
        'gdms_import_error': 'GDMS 导入错误',
        'gdms_import_no_profiles': '未在该文件中找到 GDMS 同位素谱图。',
        'gdms_import_loaded': '已导入 {} 个目标峰和 {} 个元素，来源：{}。',
        'gdms_import_target_status': '已选择导入目标峰 {}。',
        'gdms_observed': '实测',
        'gdms_fwhm': 'FWHM',
        'zoom_out_y': '缩小 Y 轴',
        'zoom_in_y': '放大 Y 轴',
        'reset_view': '重置视图',
        'export_spectrum': '导出谱图',
        'export_spectrum_tooltip': '将当前谱图导出为 PNG',
        'spectrum_png_filter': 'PNG 图像 (*.png)',
        'spectrum_exported': '谱图已导出到 {}',
        'spectrum_export_error': '谱图导出错误',
        'spectrum_mrp_band': 'MRP {} 未分辨区',
        'spectrum_peak_selected': '已选择谱图峰第 {} 行。',
        'spectrum_source_row': '行',
        'filter_unresolved': '未分辨',
        'filter_risk_high': '风险 > 0.01',
        'filter_risk_medium': '风险 > 0.001',
        'filter_atomic': '原子离子',
        'filter_oxide': '氧化物',
        'filter_hydride': '氢化物',
        'filter_sulfide_halide': '硫化物|卤化物',
        'filter_doubly': '2+',
        'filter_plasma': '等离子体',
        'filter_target_peak': '目标峰',
        'element_count': '{} 个元素',
        'element_count_error': '{} 个元素 · {}',
        'calculating': '计算中…',
        'exported_rows': '已导出 {} 行到 {}',
        'export_error': '导出错误',
        'missing_dependency': '缺少依赖',
        'excel_export_missing': 'Excel 导出需要 openpyxl。\n\n安装或更新依赖：pip install -e .\n\n是否改为导出 CSV？',
        'csv_files_filter': 'CSV 文件 (*.csv)',
        'excel_files_filter': 'Excel 文件 (*.xlsx)',
        'calculation_error': '计算错误',
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

def _ui_font(point_size=None, weight=None):
    font = QtGui.QFont()
    if point_size is not None:
        font.setPointSize(point_size)
    if weight is not None:
        font.setWeight(weight)
    return font

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
QWidget#elementsInput {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
}
QWidget#elementChipCanvas {
    background: transparent;
    border: none;
}
QFrame#elementChip {
    min-height: 18px;
    max-height: 18px;
}
QScrollArea#elementScroll {
    background: transparent;
    border: none;
}
QLabel#elementPlaceholder {
    background: transparent;
    border: none;
    color: #94a3b8;
    font-size: 11px;
    font-weight: 400;
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
        self._add_btn.setStyleSheet("font-size: 11px; font-weight: 600; background: #dbeafe; border: 1px solid #bfdbfe; border-radius: 3px; padding: 0 5px; min-height: 20px; max-height: 20px;")
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
                "QPushButton { background: transparent; border: none; color: #64748b; font-size: 11px; padding: 0; min-width: 12px; max-width: 12px; min-height: 14px; max-height: 14px; }"
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
        all_elements = periodic_table[['element', 'element name']].drop_duplicates().sort_values('element')
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
    peakSelected = QtCore.pyqtSignal(int)

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
    _MRP_BAND = QtGui.QColor(0xef, 0x44, 0x44, 26)

    MAX_LABELS = 8
    _PLOT_FLOOR = 1.0e-4
    _PICK_RADIUS = 14

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
        self._zoom_out_btn.setToolTip(_text(self.language, 'zoom_out_y'))
        self._zoom_out_btn.clicked.connect(self._on_zoom_out)
        self.toolbar.addWidget(self._zoom_out_btn)

        self._zoom_in_btn = widgets.QToolButton(self)
        self._zoom_in_btn.setText('+')
        self._zoom_in_btn.setToolTip(_text(self.language, 'zoom_in_y'))
        self._zoom_in_btn.clicked.connect(self._on_zoom_in)
        self.toolbar.addWidget(self._zoom_in_btn)

        self.toolbar.addSeparator()

        self._reset_btn = widgets.QToolButton(self)
        self._reset_btn.setText('↺')
        self._reset_btn.setToolTip(_text(self.language, 'reset_view'))
        self._reset_btn.clicked.connect(self._on_reset_view)
        self.toolbar.addWidget(self._reset_btn)

        self.toolbar.addSeparator()

        self._export_btn = widgets.QToolButton(self)
        self._export_btn.setText('PNG')
        self._export_btn.setToolTip(_text(self.language, 'export_spectrum_tooltip'))
        self._export_btn.clicked.connect(self.export_png)
        self.toolbar.addWidget(self._export_btn)

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
        self._peak_points = []
        self._selected_source_row = None

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
        if '_source_row' not in self._data.columns:
            self._data['_source_row'] = np.arange(self._data.shape[0])
        self._target_mask = self._target_mask_for(self._data)
        self.x, self.x_label, self.x_centered = self._x_values_for(self._data, self._target_mask)
        self._unresolved_mask = self._unresolved_mask_for(self._data)
        self.intensity_column = self._intensity_column_for(self._data)
        raw_y = pd.to_numeric(self._data[self.intensity_column], errors='coerce').fillna(0.0).values
        self.y = self._normalise_intensity(raw_y, self._target_mask)
        if self._selected_source_row is not None:
            source_rows = set(self._data['_source_row'].astype(int).tolist())
            if self._selected_source_row not in source_rows:
                self._selected_source_row = None
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
        self._zoom_out_btn.setToolTip(_text(self.language, 'zoom_out_y'))
        self._zoom_in_btn.setToolTip(_text(self.language, 'zoom_in_y'))
        self._reset_btn.setToolTip(_text(self.language, 'reset_view'))
        self._export_btn.setToolTip(_text(self.language, 'export_spectrum_tooltip'))

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

    def export_png(self):
        """Export the currently rendered spectrum canvas as a PNG image."""
        path, _ = widgets.QFileDialog.getSaveFileName(
            self, _text(self.language, 'export_spectrum'), '', _text(self.language, 'spectrum_png_filter')
        )
        if not path:
            return
        if not path.lower().endswith('.png'):
            path += '.png'
        try:
            image = QtGui.QImage(self._canvas.size(), QtGui.QImage.Format_ARGB32)
            image.fill(self._BG)
            painter = QtGui.QPainter(image)
            try:
                self._canvas.render(painter)
            finally:
                painter.end()
            if not image.save(path, 'PNG'):
                raise IOError(path)
        except Exception as exc:
            widgets.QMessageBox.critical(self, _text(self.language, 'spectrum_export_error'), str(exc))
        else:
            widgets.QMessageBox.information(self, _text(self.language, 'export_spectrum'),
                                            _text(self.language, 'spectrum_exported').format(path))

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
        return selected
    def _formula_label(self, value):
        """Return a plain-text formula label suitable for QPainter rendering."""
        try:
            formula = Molecule(value).formula(all_isotopes=True, style='html')
            # Strip HTML tags for QPainter plain-text rendering
            formula = re.sub(r'<[^>]+>', '', formula)
            return formula
        except Exception:
            return str(value)






    def _source_row_for_peak(self, row_number):
        if self._data is None or row_number is None:
            return None
        if '_source_row' in self._data.columns:
            try:
                return int(self._data.iloc[row_number]['_source_row'])
            except Exception:
                return None
        return int(row_number)

    def _format_peak_value(self, value, digits=6):
        try:
            if pd.isna(value):
                return ''
        except Exception:
            pass
        if isinstance(value, (int, float, np.integer, np.floating)):
            if np.isinf(value):
                return '∞'
            return f'{float(value):.{digits}g}'
        return str(value)

    def _peak_tooltip_html(self, row_number):
        row = self._data.iloc[row_number]
        formula = self._formula_label(row.get('molecule', ''))
        source_row = self._source_row_for_peak(row_number)
        lines = [f'<b>{formula}</b>']
        if 'type' in row:
            lines.append(f"{_column_display(self.language, 'type')}: {_type_display(self.language, row['type'])}")
        if 'mass/charge' in row:
            lines.append(f"m/z: {self._format_peak_value(row['mass/charge'], 7)}")
        if 'mass/charge diff' in row:
            lines.append(f"Δm/z: {self._format_peak_value(row['mass/charge diff'], 7)}")
        if 'Δppm' in row:
            lines.append(f"Δppm: {self._format_peak_value(row['Δppm'], 4)}")
        if 'MRP' in row:
            lines.append(f"MRP: {self._format_peak_value(row['MRP'], 5)}")
        if 'relative risk' in row:
            lines.append(f"{_column_display(self.language, 'risk')}: {self._format_peak_value(row['relative risk'], 4)}")
        if 'resolved' in row and row['resolved'] != '':
            resolved = _text(self.language, 'yes') if bool(row['resolved']) else _text(self.language, 'no')
            lines.append(f"{_column_display(self.language, 'ok')}: {resolved}")
        if source_row is not None:
            lines.append(f"{_text(self.language, 'spectrum_source_row')}: {source_row + 1}")
        return '<br/>'.join(lines)

    def _update_peak_points(self, x2p, y2p):
        self._peak_points = []
        if self._data is None or self.x is None or self.y is None:
            return
        for row_number in range(self._data.shape[0]):
            xi = self.x[row_number]
            yi = self.y[row_number]
            if not (np.isfinite(xi) and np.isfinite(yi)):
                continue
            self._peak_points.append((row_number, x2p(xi), y2p(yi), self._source_row_for_peak(row_number)))

    def _peak_at_pos(self, pos):
        if not self._peak_points:
            return None
        px = pos.x()
        py = pos.y()
        radius2 = self._PICK_RADIUS * self._PICK_RADIUS
        best = None
        best_dist = None
        for row_number, xpix, ypix, source_row in self._peak_points:
            dist = (px - xpix) ** 2 + (py - ypix) ** 2
            if dist <= radius2 and (best_dist is None or dist < best_dist):
                best = row_number
                best_dist = dist
        return best

    def tooltip_for_pos(self, pos):
        row_number = self._peak_at_pos(pos)
        if row_number is None:
            return ''
        return self._peak_tooltip_html(row_number)

    def select_peak_at(self, pos):
        row_number = self._peak_at_pos(pos)
        if row_number is None:
            return False
        source_row = self._source_row_for_peak(row_number)
        if source_row is None:
            return False
        self._selected_source_row = source_row
        self._canvas.update()
        self.peakSelected.emit(source_row)
        return True

    def _window_span_for_axis(self):
        if 'ppm' in self.x_label:
            return self._plot_window.get('window_half_ppm')
        if 'm/z' in self.x_label:
            return self._plot_window.get('window_half_mz')
        return None

    def _mrp_half_width_for_axis(self):
        mrp = self._plot_window.get('instrument_mrp')
        try:
            mrp = float(mrp)
        except (TypeError, ValueError):
            return None
        if mrp <= 0 or not self.x_centered:
            return None
        if 'ppm' in self.x_label:
            return 1.0e6 / mrp
        if 'm/z' in self.x_label:
            target_mz = self._plot_window.get('target_mz')
            try:
                target_mz = float(target_mz)
            except (TypeError, ValueError):
                return None
            if target_mz <= 0:
                return None
            return target_mz / mrp
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
            self._peak_points = []
            painter.setPen(self._TEXT)
            painter.setFont(_ui_font(13))
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

        self._update_peak_points(x2p, y2p)
        self._draw_mrp_band(painter, x2p, cr)

        # ── grid ─────────────────────────────────────────────────
        import math
        painter.setFont(_ui_font(9))
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
        painter.setFont(_ui_font(11))
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
        painter.setFont(_ui_font(13, QtGui.QFont.Bold))
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
        self._draw_selected_peak(painter, x2p, y2p)

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
            painter.setFont(_ui_font(9))
            painter.drawText(QtCore.QRectF(lx + 16, ly, 160, 14), QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, label)
            ly += 16

        # ── peak annotations ─────────────────────────────────────
        self._draw_annotations(painter, x2p, y2p, cr)

    def _draw_mrp_band(self, painter, x2p, cr):
        """Draw the instrument-MRP unresolved zone around the calibrated target."""
        half_width = self._mrp_half_width_for_axis()
        if half_width is None or half_width <= 0:
            return
        left = max(cr.left(), x2p(-half_width))
        right = min(cr.right(), x2p(half_width))
        if right <= cr.left() or left >= cr.right() or right <= left:
            return
        band_rect = QtCore.QRectF(left, cr.top(), right - left, cr.height())
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._MRP_BAND)
        painter.drawRect(band_rect)
        painter.setPen(QtGui.QPen(self._RED, 1, QtCore.Qt.DotLine))
        painter.drawLine(QtCore.QPointF(left, cr.top()), QtCore.QPointF(left, cr.bottom()))
        painter.drawLine(QtCore.QPointF(right, cr.top()), QtCore.QPointF(right, cr.bottom()))

        label = _text(self.language, 'spectrum_mrp_band').format(
            self._format_peak_value(self._plot_window.get('instrument_mrp'), 5)
        )
        painter.setFont(_ui_font(8))
        fm = painter.fontMetrics()
        label_width = fm.horizontalAdvance(label) + 8
        x = min(max(left + 4, cr.left() + 4), cr.right() - label_width - 4)
        y = cr.bottom() - fm.height() - 6
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(255, 255, 255, 210))
        painter.drawRoundedRect(QtCore.QRectF(x, y, label_width, fm.height() + 4), 3, 3)
        painter.setPen(self._RED)
        painter.drawText(QtCore.QRectF(x + 4, y + 2, label_width - 8, fm.height()),
                         QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, label)

    def _draw_selected_peak(self, painter, x2p, y2p):
        """Highlight the spectrum peak most recently selected by clicking."""
        if self._selected_source_row is None or self._data is None:
            return
        selected_rows = [
            row_number for row_number in range(self._data.shape[0])
            if self._source_row_for_peak(row_number) == self._selected_source_row
        ]
        if not selected_rows:
            return
        row_number = selected_rows[0]
        px = x2p(self.x[row_number])
        py = y2p(self.y[row_number])
        color = self._RED if self._target_mask[row_number] else (
            self._AMBER if self._unresolved_mask[row_number] else self._BLUE
        )
        painter.setBrush(QtCore.Qt.NoBrush)
        pen = QtGui.QPen(color, 2.2)
        painter.setPen(pen)
        painter.drawEllipse(QtCore.QPointF(px, py), 10, 10)

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
        painter.setFont(_ui_font(9))
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

    def mouseMoveEvent(self, event):
        if self._spectrum is None:
            return widgets.QWidget.mouseMoveEvent(self, event)
        tooltip = self._spectrum.tooltip_for_pos(event.pos())
        if tooltip:
            self.setCursor(QtCore.Qt.PointingHandCursor)
            widgets.QToolTip.showText(event.globalPos(), tooltip, self)
        else:
            self.unsetCursor()
            widgets.QToolTip.hideText()
        return widgets.QWidget.mouseMoveEvent(self, event)

    def leaveEvent(self, event):
        self.unsetCursor()
        widgets.QToolTip.hideText()
        return widgets.QWidget.leaveEvent(self, event)

    def mousePressEvent(self, event):
        if self._spectrum is not None and event.button() == QtCore.Qt.LeftButton:
            if self._spectrum.select_peak_at(event.pos()):
                event.accept()
                return
        return widgets.QWidget.mousePressEvent(self, event)



class InterferenceFilterProxy(QtCore.QSortFilterProxyModel):
    """Filter proxy for interference results supporting query syntax.

    Query syntax (space-separated tokens, AND logic; | for OR within a token):
    - Plain text: case-insensitive substring match in ALL columns.
    - col:val      substring match — column 'col' contains 'val'.
    - col=val      exact match (case-insensitive).
    - col>N, col<N, col>=N, col<=N  numeric comparison.
    - col~rx       regex match — 'col' matches Python re pattern.
    - -token       negation — reject row if token appears in ANY column.
    - expr1|expr2  OR within a single token (e.g. oxide|hydride).
    """
    def __init__(self, parent=None):
        QtCore.QSortFilterProxyModel.__init__(self, parent=parent)
        self._filter_text = ''
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def set_filter_text(self, text):
        self._filter_text = text
        self.invalidateFilter()

    def lessThan(self, left, right):
        """Compare raw DataFrame values directly — bypass DisplayRole HTML cost."""
        model = self.sourceModel()
        if model is None or not hasattr(model, '_data'):
            return super().lessThan(left, right)
        col = model._data.columns[left.column()]
        lv = model._data.iloc[left.row(), left.column()]
        rv = model._data.iloc[right.row(), right.column()]
        try:
            return float(lv) < float(rv)
        except (ValueError, TypeError):
            pass
        try:
            return str(lv).lower() < str(rv).lower()
        except (ValueError, TypeError):
            return super().lessThan(left, right)

    @staticmethod
    def _token_matches(token, data_row):
        """Return True if a single token matches the row (OR branches resolved)."""
        # Split on | for OR logic — if ANY sub-token matches, accept
        for sub in token.split('|'):
            sub = sub.strip()
            if not sub:
                continue
            if InterferenceFilterProxy._sub_token_matches(sub, data_row):
                return True
        return False

    @staticmethod
    def _sub_token_matches(token, data_row):
        """Match a single (non-OR) token against a row."""
        # Negation
        if token.startswith('-') and len(token) > 1:
            neg_val = token[1:].lower()
            for c in data_row.index:
                if neg_val in str(data_row[c]).lower():
                    return False
            return True

        # Regex operator ~
        if '~' in token:
            col, _, pat = token.partition('~')
            col = col.strip()
            pat = pat.strip()
            if col in data_row.index and pat:
                try:
                    return bool(re.search(pat, str(data_row[col])))
                except re.error:
                    return False
            return True

        # Exact match =
        if '=' in token and '>=' not in token and '<=' not in token:
            col, _, val = token.partition('=')
            col = col.strip()
            val = val.strip()
            if col in data_row.index:
                return str(data_row[col]).lower() == val.lower()
            return True

        # Comparison operators (longer ops first)
        for op in ('>=', '<='):
            if op in token:
                col, _, val_str = token.partition(op)
                col = col.strip()
                if col in data_row.index:
                    cell_val = data_row[col]
                    if cell_val == '' or (isinstance(cell_val, float) and np.isnan(cell_val)):
                        return False
                    try:
                        cv = float(cell_val)
                        qv = float(val_str)
                        if op == '>=':
                            return cv >= qv
                        if op == '<=':
                            return cv <= qv
                    except (ValueError, TypeError):
                        pass
                return True

        for op in ('>', '<'):
            if op in token:
                col, _, val_str = token.partition(op)
                col = col.strip()
                if col in data_row.index:
                    cell_val = data_row[col]
                    if cell_val == '' or (isinstance(cell_val, float) and np.isnan(cell_val)):
                        return False
                    try:
                        cv = float(cell_val)
                        qv = float(val_str)
                        if op == '>':
                            return cv > qv
                        if op == '<':
                            return cv < qv
                    except (ValueError, TypeError):
                        pass
                return True

        # Colon operator — substring match on named column
        if ':' in token:
            col, _, val = token.partition(':')
            col = col.strip()
            val = val.strip()
            if col in data_row.index:
                return val.lower() in str(data_row[col]).lower()
            return True

        # Default: search ALL columns
        token_lower = token.lower()
        for c in data_row.index:
            if token_lower in str(data_row[c]).lower():
                return True
        return False

    def filterAcceptsRow(self, source_row, source_parent):
        if not self._filter_text.strip():
            return True

        model = self.sourceModel()
        if model is None or not hasattr(model, '_data') or model._data is None:
            return True

        tokens = self._filter_text.strip().split()
        data_row = model._data.iloc[source_row]

        # AND logic across space-separated tokens
        for token in tokens:
            if not self._token_matches(token, data_row):
                return False

        return True


class CalculationWorker(QtCore.QObject):
    """Background worker for interference calculation."""

    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(object)  # pd.DataFrame
    error = QtCore.pyqtSignal(str)

    def __init__(self, atoms, mz, targetrange, maxsize, charge, chargesign,
                 risk_preset=None, instrument_mrp=0, language='en'):
        QtCore.QObject.__init__(self)
        self.atoms = atoms
        self.mz = mz
        self.targetrange = targetrange
        self.maxsize = maxsize
        self.charge = charge
        self.chargesign = chargesign
        self.risk_preset = risk_preset
        self.instrument_mrp = instrument_mrp
        self.language = language
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    @QtCore.pyqtSlot()
    def run(self):
        """Perform the calculation in a background thread."""
        try:
            self.progress.emit(0)
            if self._cancelled:
                return
            if self.risk_preset:
                data = inorganic_interference(
                    self.atoms, self.mz, targetrange=self.targetrange,
                    maxsize=self.maxsize, charge=self.charge,
                    chargesign=self.chargesign, risk_preset=self.risk_preset)
            if self._cancelled:
                return

            # ── Post-process DataFrame (was in _on_calc_finished) ──
            target_mask = data['target'].astype(bool)
            if target_mask.any():
                target_mz = data.loc[target_mask, 'mass/charge'].iat[0]
            else:
                target_mz = None

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
            # ── End post-process ──

            self.progress.emit(100)
            self.finished.emit(data)
        except Exception as exc:
            self.error.emit(str(exc))


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
        self._filter_active = False
        self._result_count_base = ''
        self._last_interference_display_data = None
        self._last_interference_spectrum_data = None
        self._last_interference_metrics = None
        self._calc_request_id = 0
        self._calc_thread = None
        self._calc_worker = None
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
        self.atoms_input.setMinimumHeight(132)
        self.atoms_input.setMaximumHeight(170)
        self.atoms_input.elementsChanged.connect(self._on_elements_changed)

        # Element preset combo replaces existing elements
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
        self.mz_input.setVisible(False)
        self._mz_preview_label = widgets.QLabel(parent=self)
        self._mz_preview_label.setVisible(False)
        self._mz_preview_timer = QtCore.QTimer(self)
        self._mz_preview_timer.setSingleShot(True)
        self._mz_preview_timer.setInterval(300)
        self._mz_preview_timer.timeout.connect(self._update_mz_preview)
        self.mz_input.textChanged.connect(self._mz_preview_timer.start)

        # Element + isotope selector for target
        self._target_element_input = widgets.QComboBox(parent=self)
        self._target_element_input.setEditable(True)
        self._target_element_input.setInsertPolicy(widgets.QComboBox.NoInsert)
        self._target_element_input.setPlaceholderText(_text(self.language, 'target_element_placeholder'))
        self._target_element_input.setToolTip(tooltip_text(self.language, 'mz'))
        _sorted_elements = sorted(
            periodic_table[['element', 'element name']].drop_duplicates().to_records(index=False),
            key=lambda x: x[0]
        )
        for elem, name in _sorted_elements:
            self._target_element_input.addItem(f'{elem}  ({name})', elem)
        self._target_element_input.setCurrentIndex(-1)
        self._target_element_input.setMinimumWidth(130)

        self._target_isotope_input = widgets.QComboBox(parent=self)
        self._target_isotope_input.setEnabled(False)
        self._target_isotope_input.setPlaceholderText(_text(self.language, 'target_isotope_placeholder'))
        self._target_isotope_input.setToolTip(tooltip_text(self.language, 'mz'))
        self._target_isotope_input.setMinimumWidth(150)
        self._target_element_input.currentIndexChanged.connect(self._on_target_element_changed)
        self._target_isotope_input.currentIndexChanged.connect(self._on_target_isotope_changed)

        self._gdms_import_profiles = []
        self.import_gdms_button = widgets.QPushButton(_text(self.language, 'import_gdms'), parent=self)
        self.import_gdms_button.setToolTip(tooltip_text(self.language, 'gdms_import'))
        self.import_gdms_button.setMinimumWidth(96)
        self.imported_target_input = widgets.QComboBox(parent=self)
        self.imported_target_input.addItem(_text(self.language, 'imported_target_placeholder'), None)
        self.imported_target_input.setEnabled(False)
        self.imported_target_input.setVisible(False)
        self.imported_target_input.setMinimumWidth(180)

        self.instrument_mrp_label = widgets.QLabel(_text(self.language, 'instrument_mrp'), parent=self)
        self.instrument_mrp_input = widgets.QSpinBox(parent=self)
        self.instrument_mrp_input.setRange(0, 1000000)
        self.instrument_mrp_input.setValue(4000)
        self.instrument_mrp_input.setSingleStep(500)
        self.instrument_mrp_input.setSpecialValueText(_text(self.language, 'off'))

        # No separate mzrange/window_unit picker — sweep_input replaces both
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
        self.export_button = widgets.QPushButton('{} ▾'.format(_text(self.language, 'export')), parent=self)
        self.export_menu = widgets.QMenu(self)
        self.export_menu.addAction(_text(self.language, 'export_csv'), self.export_csv)
        self.export_menu.addAction(_text(self.language, 'export_xlsx'), self.export_xlsx)
        self.export_button.setMenu(self.export_menu)

        # Table and spectrum output
        self.table_output = TableView(html_cols=None)
        # Column visibility via right-click header
        _header = self.table_output.horizontalHeader()
        _header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        _header.customContextMenuRequested.connect(self._show_column_menu)
        self.spectrum_window = Spectrum(parent=self)
        self.spectrum_window.peakSelected.connect(self._select_result_row_from_spectrum)

        # Show input errors on statusbar
        self.statusbar = self.parent().statusBar()
        self.statusbar.setStyleSheet('color: #475569;')
        self._progress_bar = widgets.QProgressBar(parent=self.statusbar)
        self._progress_bar.setMaximumWidth(160)
        self._progress_bar.setMaximumHeight(18)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self._progress_bar)

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
        self.workflow_layout = widgets.QFormLayout()
        self.workflow_layout.setContentsMargins(12, 16, 12, 8)
        self.workflow_layout.setHorizontalSpacing(12)
        self.workflow_layout.setVerticalSpacing(6)
        self.mode_label = self.create_field_label(_text(self.language, 'mode'))
        self.workflow_layout.addRow(self.mode_label, self.mode_input)
        target_group = widgets.QWidget()
        target_group_layout = widgets.QVBoxLayout(target_group)
        target_group_layout.setContentsMargins(0, 0, 0, 0)
        target_group_layout.setSpacing(2)
        sel_row = widgets.QHBoxLayout()
        sel_row.setSpacing(4)
        sel_row.addWidget(self._target_element_input, stretch=1)
        sel_row.addWidget(self._target_isotope_input, stretch=1)
        target_group_layout.addLayout(sel_row)
        import_row = widgets.QHBoxLayout()
        import_row.setSpacing(4)
        import_row.addWidget(self.import_gdms_button)
        import_row.addWidget(self.imported_target_input, stretch=1)
        target_group_layout.addLayout(import_row)
        mz_label = widgets.QLabel(parent=self)
        mz_label.setObjectName('helperText')
        mz_label.setStyleSheet("color: #1e40af; font-size: 13px; font-weight: bold;")
        mz_label.setToolTip(tooltip_text(self.language, 'mz'))
        self._target_mz_result_label = mz_label
        target_group_layout.addWidget(mz_label)
        self.target_label = self.create_field_label(_text(self.language, 'target'))
        self.workflow_layout.addRow(self.target_label, target_group)
        self.sweep_label = self.create_field_label(_text(self.language, 'sweep'))
        sweep_widget = widgets.QWidget()
        sweep_widget_layout = widgets.QHBoxLayout(sweep_widget)
        sweep_widget_layout.setContentsMargins(0, 0, 0, 0)
        sweep_widget_layout.setSpacing(4)
        sweep_input = widgets.QSpinBox(parent=self)
        sweep_input.setRange(100, 100000)
        sweep_input.setValue(2000)
        sweep_input.setSuffix(' ppm')
        sweep_input.setSingleStep(100)
        sweep_input.setToolTip(tooltip_text(self.language, 'mzrange'))
        sweep_widget_layout.addWidget(sweep_input, stretch=1)
        self.workflow_layout.addRow(self.sweep_label, sweep_widget)
        self.sweep_input = sweep_input
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
        ion_row = widgets.QWidget()
        ion_row_layout = widgets.QHBoxLayout(ion_row)
        ion_row_layout.setContentsMargins(0, 0, 0, 0)
        ion_row_layout.addLayout(self.parameter_row_layout)
        self.workflow_layout.addRow(self.ion_model_label, ion_row)
        self.workflow_group.setLayout(self.workflow_layout)

        self.atoms_group = widgets.QGroupBox(_text(self.language, 'sample_plasma'))
        self.atoms_layout = widgets.QVBoxLayout()
        self.atoms_layout.setContentsMargins(14, 16, 14, 10)
        self.atoms_layout.setSpacing(5)
        self.elements_label = self.create_field_label(_text(self.language, 'elements'))
        self.atoms_layout.addWidget(self.elements_label)
        self.atoms_layout.addWidget(self.atoms_input, stretch=1)
        self.elements_count_label = widgets.QLabel(parent=self.atoms_group)
        self.elements_count_label.setObjectName('helperText')
        self.elements_count_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.atoms_layout.addWidget(self.elements_count_label)
        self.element_set_row_layout = widgets.QHBoxLayout()
        self.element_set_row_layout.setSpacing(8)
        self.add_set_label = self.create_field_label(_text(self.language, 'add_set'))
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
        self.button_layout.addWidget(self.export_button)
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
        self.count_metric_label.setCursor(QtCore.Qt.PointingHandCursor)
        self.count_metric_label.installEventFilter(self)
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

        # Filter bar
        self.filter_container = widgets.QWidget(parent=self.results_panel)
        self.filter_container.setVisible(False)
        self.filter_container.setObjectName('filterContainer')
        _filter_container_layout = widgets.QHBoxLayout(self.filter_container)
        _filter_container_layout.setContentsMargins(16, 4, 16, 4)
        self.filter_bar = widgets.QLineEdit(parent=self.filter_container)
        self.filter_bar.setPlaceholderText(_text(self.language, 'filter_results'))
        self.filter_bar.setClearButtonEnabled(True)
        self.filter_bar.textChanged.connect(self._apply_filter)
        _filter_container_layout.addWidget(self.filter_bar)
        self.results_layout.addWidget(self.filter_container)

        # Quick-filter preset chips
        self._filter_chip_bar = widgets.QWidget(parent=self.results_panel)
        self._filter_chip_bar.setVisible(False)
        self._filter_chip_bar.setObjectName('filterChipBar')
        _chip_layout = widgets.QHBoxLayout(self._filter_chip_bar)
        _chip_layout.setContentsMargins(16, 0, 16, 4)
        _chip_layout.setSpacing(6)

        self._filter_chips = []
        self._chip_unresolved = self._make_filter_chip('filter_unresolved', 'ok:no', '#fef3c7')
        self._chip_risk_high = self._make_filter_chip('filter_risk_high', 'risk>0.01', '#fee2e2')
        self._chip_risk_medium = self._make_filter_chip('filter_risk_medium', 'risk>0.001', '#fff7ed')
        self._chip_atomic = self._make_filter_chip('filter_atomic', 'type:atomic', '#e0f2fe')
        self._chip_oxide = self._make_filter_chip('filter_oxide', 'type:oxide|type:dioxide', '#e0f2fe')
        self._chip_hydride = self._make_filter_chip('filter_hydride', 'type:hydride|type:hydroxide', '#ecfdf5')
        self._chip_sulfide = self._make_filter_chip('filter_sulfide_halide', 'type:sulfide|type:halide', '#f3e8ff')
        self._chip_doubly = self._make_filter_chip('filter_doubly', 'z:2', '#fed7aa')
        self._chip_plasma = self._make_filter_chip('filter_plasma', 'type:plasma', '#fce7f3')
        self._chip_target = self._make_filter_chip('filter_target_peak', 'target:True', '#fef2f2')

        _chip_layout.addWidget(self._chip_unresolved)
        _chip_layout.addWidget(self._chip_risk_high)
        _chip_layout.addWidget(self._chip_risk_medium)
        _chip_layout.addWidget(self._chip_atomic)
        _chip_layout.addWidget(self._chip_oxide)
        _chip_layout.addWidget(self._chip_hydride)
        _chip_layout.addWidget(self._chip_sulfide)
        _chip_layout.addWidget(self._chip_doubly)
        _chip_layout.addWidget(self._chip_plasma)
        _chip_layout.addWidget(self._chip_target)
        _chip_layout.addStretch(1)
        self.results_layout.addWidget(self._filter_chip_bar)

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
        self.import_gdms_button.clicked.connect(self.import_gdms_profiles)
        self.imported_target_input.currentIndexChanged.connect(self._on_imported_target_changed)
        self.language_input.currentIndexChanged.connect(self.apply_language)
        self.mode_input.currentIndexChanged.connect(self.apply_mode_preset)
        self.charge_preset_input.currentIndexChanged.connect(self._on_target_isotope_changed)

        self.element_set_input.activated.connect(self.add_element_set)
        self.mz_input.editingFinished.connect(self.check_mz_input)
        # sweep_input handled below
        self.instrument_mrp_input.valueChanged.connect(self.update_result_summary)
        self.spectrum_button.clicked.connect(self.toggle_spectrum)

        # Set jump order for tab
        self.setTabOrder(self.language_input, self.mode_input)
        self.setTabOrder(self.mode_input, self._target_element_input)
        self.setTabOrder(self._target_element_input, self._target_isotope_input)
        self.setTabOrder(self._target_isotope_input, self.import_gdms_button)
        self.setTabOrder(self.import_gdms_button, self.imported_target_input)
        self.sweep_input.valueChanged.connect(self.update_result_summary)
        self.setTabOrder(self.imported_target_input, self.sweep_input)
        self.setTabOrder(self.sweep_input, self.atoms_input)
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
        self.sweep_label.setText(self._tr('sweep'))
        self.target_label.setText(self._tr('target'))
        self.atoms_group.setTitle(self._tr('sample_plasma'))
        self.elements_label.setText(self._tr('elements'))
        self.add_set_label.setText(self._tr('add_set'))
        self.ion_model_label.setText(self._tr('ion_model'))
        self.charge_preset_label.setText(self._tr('ions'))
        self.maxsize_label.setText(self._tr('max_size'))

        self.instrument_mrp_label.setText(self._tr('instrument_mrp'))
        self.interference_button.setText(self._tr('calculate'))
        self._update_ratio_button_label()
        self.results_title_label.setText(self._tr('results_title'))
        self.empty_title_label.setText(self._tr('empty_title'))
        self.empty_body_label.setText(self._tr('empty_body'))
        self.spectrum_button.setAccessibleName(self._tr('open_spectrum'))
        self.help_button.setAccessibleName(self._tr('open_help'))
        self.export_button.setText('{} ▾'.format(self._tr('export')))
        self.export_menu.actions()[0].setText(self._tr('export_csv'))
        self.export_menu.actions()[1].setText(self._tr('export_xlsx'))
        self.filter_bar.setPlaceholderText(self._tr('filter_results'))
        self._target_element_input.setPlaceholderText(self._tr('target_element_placeholder'))
        self._target_isotope_input.setPlaceholderText(self._tr('target_isotope_placeholder'))
        self.import_gdms_button.setText(self._tr('import_gdms'))
        if self.imported_target_input.count() > 0:
            self.imported_target_input.setItemText(0, self._tr('imported_target_placeholder'))
        self._refresh_imported_target_labels()
        self.atoms_input.set_language(self.language)
        self.table_output.set_language(self.language)
        for chip in getattr(self, '_filter_chips', []):
            chip.setText(self._tr(chip._label_key))
        self._validate_elements_input()

        self.set_tooltips()
        self.spectrum_window.set_language(self.language)
        self.refresh_table_language()
        self.update_result_summary()

    def set_tooltips(self):
        """Set localized widget tooltips."""
        self.mode_input.setToolTip(tooltip_text(self.language, 'mode'))
        self.atoms_input.setToolTip('')
        self.element_set_input.setToolTip(tooltip_text(self.language, 'element_set'))
        self.charge_preset_input.setToolTip(tooltip_text(self.language, 'charge_preset'))
        self.mz_input.setToolTip(tooltip_text(self.language, 'mz'))
        self._target_element_input.setToolTip(tooltip_text(self.language, 'mz'))
        self._target_isotope_input.setToolTip(tooltip_text(self.language, 'mz'))
        self._target_mz_result_label.setToolTip(tooltip_text(self.language, 'mz'))
        self.import_gdms_button.setToolTip(tooltip_text(self.language, 'gdms_import'))
        self.imported_target_input.setToolTip(tooltip_text(self.language, 'gdms_import'))
        self.sweep_input.setToolTip(tooltip_text(self.language, 'mzrange'))

        self.maxsize_input.setToolTip(tooltip_text(self.language, 'maxsize'))
        self.instrument_mrp_input.setToolTip(tooltip_text(self.language, 'instrument_mrp'))
        self.interference_button.setToolTip(tooltip_text(self.language, 'interference_button'))
        self.standard_ratio_button.setToolTip(tooltip_text(self.language, 'standard_ratio_button'))
        self.spectrum_button.setToolTip(tooltip_text(self.language, 'spectrum_button'))
        self.help_button.setToolTip(tooltip_text(self.language, 'help_button'))

    def refresh_table_language(self):
        """Refresh localized table headers and display values."""
        model = self.table_output.model()
        if model is None:
            return
        if isinstance(model, InterferenceFilterProxy):
            model = model.sourceModel()
        if not hasattr(model, 'language'):
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
        window = '{:.0f} ppm'.format(self.sweep_input.value())

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
        self.window_metric_label.setText('{}: {}'.format(self._tr('summary_window'), window)
        )
        self.mrp_metric_label.setText('{}: {}'.format(self._tr('summary_mrp'), mrp))
        self.count_metric_label.setText(count_text)
        self._result_count_base = count_text

    def _copy_table_data(self, data):
        """Copy a DataFrame while preserving attrs used by the spectrum."""
        copied = data.copy()
        copied.attrs = dict(getattr(data, 'attrs', {}))
        return copied

    def _has_interference_cache(self):
        """Return True when a previous interference result can be restored."""
        return (
            self._last_interference_display_data is not None and
            self._last_interference_spectrum_data is not None and
            self._last_interference_metrics is not None
        )

    def _update_ratio_button_label(self):
        """Switch the ratio button label based on the active result view."""
        if not hasattr(self, 'standard_ratio_button'):
            return
        if self.result_metrics.get('kind') == 'ratios' and self._has_interference_cache():
            self.standard_ratio_button.setText(self._tr('interferences'))
        else:
            self.standard_ratio_button.setText(self._tr('ratios'))

    def _set_filter_text(self, text):
        """Set filter text and proxy state without recursive signal churn."""
        self.filter_bar.blockSignals(True)
        self.filter_bar.setText(text)
        self.filter_bar.blockSignals(False)
        model = self.table_output.model()
        if isinstance(model, InterferenceFilterProxy):
            model.set_filter_text(text)
        self._update_filtered_count()

    def _show_interference_results(self, display_data, spectrum_data, metrics,
                                   filter_text='', status_text=None):
        """Display cached or freshly calculated interference results."""
        self.table_output.setUpdatesEnabled(False)
        self.table_output.setVisible(False)

        model = TableModel(display_data, table='interference', language=self.language)
        proxy = InterferenceFilterProxy(self)
        proxy.setSourceModel(model)
        self.table_output.setModel(proxy)
        self.table_output.setColumnHidden(display_data.columns.get_loc('target'), True)
        self.resize_table_sections()
        self.filter_container.setVisible(True)
        self._filter_chip_bar.setVisible(True)

        self._spectrum_data = self._copy_table_data(spectrum_data)
        self.result_metrics = dict(metrics)
        self.results_stack.setCurrentWidget(self.table_output)
        self.update_result_summary()
        self._set_filter_text(filter_text)
        self.spectrum_window.plot_spectrum(self._spectrum_data)
        self._update_ratio_button_label()

        self.table_output.setVisible(True)
        self.table_output.setUpdatesEnabled(True)
        self.table_output.setFocus()

        if status_text:
            self.set_status(status_text, time=5000)

    def _cache_interference_results(self, display_data, spectrum_data, metrics):
        """Cache the latest interference result so ratios can be toggled back."""
        self._last_interference_display_data = self._copy_table_data(display_data)
        self._last_interference_spectrum_data = self._copy_table_data(spectrum_data)
        self._last_interference_metrics = dict(metrics)

    def _restore_interference_results(self):
        """Restore the last interference table without recalculating."""
        if not self._has_interference_cache():
            return False
        self._show_interference_results(
            self._last_interference_display_data,
            self._last_interference_spectrum_data,
            self._last_interference_metrics,
            filter_text='',
            status_text=self._tr('interference_restored'),
        )
        return True

    def apply_mode_preset(self, index=None):
        """ Apply UI defaults for the selected calculation preset. """
        preset = self.MODE_PRESETS.get(self.mode_input.currentText())
        if preset:
            self.charge_preset_input.setCurrentIndex(preset['charge_index'])
            self.maxsize_input.setValue(preset['maxsize'])
            self.instrument_mrp_input.setValue(preset['mrp'])
            self.sweep_input.setValue(int(preset['window']))
            self.atoms_input.setPlaceholderText(self._tr('elements_empty_hint'))
            self.mz_input.setPlaceholderText(preset['target'])
        self.update_result_summary()

    def add_element_set(self, index):
        """Replace element input with selected preset."""
        elements = _current_data(self.element_set_input)
        if not elements:
            return
        self.atoms_input.set_elements(list(elements))
        self.element_set_input.setCurrentIndex(0)

    def import_gdms_profiles(self):
        """Import GDMS Excel profile exports and use them as target choices."""
        path, _ = widgets.QFileDialog.getOpenFileName(
            self, self._tr('import_gdms'), '', self._tr('gdms_profile_files_filter')
        )
        if not path:
            return
        try:
            profiles = parse_gdms_profile_xlsx(path)
        except RuntimeError:
            widgets.QMessageBox.critical(
                self, self._tr('missing_dependency'), self._tr('gdms_import_missing')
            )
            return
        except Exception as e:
            widgets.QMessageBox.critical(self, self._tr('gdms_import_error'), str(e))
            return

        if not profiles:
            self.warn(self._tr('gdms_import_no_profiles'))
            return

        elements = [
            element for element in extract_profile_elements(profiles)
            if (periodic_table['element'] == element).any()
        ]
        self._gdms_import_profiles = list(profiles)
        self.atoms_input.set_elements(elements)
        self._refresh_imported_target_labels()
        self.imported_target_input.setCurrentIndex(0)
        self.set_status(
            self._tr('gdms_import_loaded').format(
                len(profiles), len(elements), os.path.basename(path)
            ),
            time=7000,
        )

    def _refresh_imported_target_labels(self):
        """Refresh imported target selector text after import or language switch."""
        if not hasattr(self, 'imported_target_input'):
            return
        current = _current_data(self.imported_target_input)
        self.imported_target_input.blockSignals(True)
        self.imported_target_input.clear()
        self.imported_target_input.addItem(self._tr('imported_target_placeholder'), None)
        for profile in getattr(self, '_gdms_import_profiles', []):
            self.imported_target_input.addItem(
                self._format_imported_target_label(profile), profile
            )
        has_profiles = bool(getattr(self, '_gdms_import_profiles', []))
        self.imported_target_input.setVisible(has_profiles)
        self.imported_target_input.setEnabled(has_profiles)
        if current is not None:
            index = self._find_combo_data(self.imported_target_input, current)
            if index >= 0:
                self.imported_target_input.setCurrentIndex(index)
        self.imported_target_input.blockSignals(False)

    def _format_imported_target_label(self, profile):
        observed = profile.centroid_mz if profile.centroid_mz is not None else profile.apex_mz
        if observed is not None:
            return '{}  m/z {:.4f}'.format(profile.label, observed)
        return '{}  {}'.format(profile.label, profile.isotope)

    def _on_imported_target_changed(self, index):
        """Apply a target selected from imported GDMS profiles."""
        profile = _current_data(self.imported_target_input)
        if profile is None:
            return
        self._set_target_from_isotope(profile.isotope)
        self._set_target_mz_label_from_profile(profile)
        self.set_status(
            self._tr('gdms_import_target_status').format(profile.label), time=3000
        )

    def _set_target_from_isotope(self, isotope):
        """Select the target element/isotope controls from a string like 56Fe."""
        match = re.match(r'^(\d+)([A-Z][a-z]?)$', str(isotope or ''))
        if not match:
            return False
        element = match.group(2)
        element_index = self._find_combo_data(self._target_element_input, element)
        if element_index < 0:
            return False
        self._target_element_input.setCurrentIndex(element_index)
        isotope_index = self._find_combo_data(self._target_isotope_input, isotope)
        if isotope_index >= 0:
            self._target_isotope_input.setCurrentIndex(isotope_index)
        else:
            self.mz_input.blockSignals(True)
            self.mz_input.setText(str(isotope))
            self.mz_input.blockSignals(False)
            self.mz = str(isotope)
        return True

    def _set_target_mz_label_from_profile(self, profile):
        """Show theoretical and observed m/z for an imported target."""
        isotope = profile.isotope
        label = self._target_mz_result_label.text()
        rows = periodic_table[periodic_table['isotope'] == isotope]
        if not rows.empty:
            mass = rows.iloc[0]['mass']
            charges, _ = _current_data(self.charge_preset_input)
            charge = charges[0]
            label = '{}  \u2192  m/z = {:.4f}'.format(isotope, mass / charge)
        observed = profile.centroid_mz if profile.centroid_mz is not None else profile.apex_mz
        extras = []
        if observed is not None:
            extras.append('{} {:.4f}'.format(self._tr('gdms_observed'), observed))
        if profile.fwhm is not None:
            extras.append('{} {:.4g}'.format(self._tr('gdms_fwhm'), profile.fwhm))
        if extras:
            label = '{}  ·  {}'.format(label, '  ·  '.join(extras))
        self._target_mz_result_label.setText(label)

    def _find_combo_data(self, combo, value):
        """Return the first combo index with matching user data."""
        try:
            return combo.findData(value)
        except AttributeError:
            for index in range(combo.count()):
                if combo.itemData(index) == value:
                    return index
        return -1

    def warn(self, text, time=5000):
        """ Display a warning message in the status bar. """
        self.statusbar.setStyleSheet('color: #dc2626; font-weight: 500;')
        self.statusbar.showMessage(text, msecs=time)

    def set_status(self, text, time=5000):
        """Display a neutral status message in the status bar."""
        self.statusbar.setStyleSheet('color: #475569; font-weight: 400;')
        self.statusbar.showMessage(text, msecs=time)

    def _on_elements_changed(self, elements):
        """Update atoms list and count display when elements change."""
        self.atoms = elements
        count = len(elements)
        if count > 0:
            self.elements_count_label.setText(self._tr('element_count').format(count))
            self.elements_count_label.setStyleSheet("color: #64748b; font-size: 11px;")
        else:
            self.elements_count_label.setText('')
        # Also update validate-style display for edge cases
        self._validate_elements_input()

    def _validate_elements_input(self):
        """Check element input for invalid tokens; update border and count label."""
        tokens = self.atoms if hasattr(self, 'atoms') else []
        invalid = []
        valid_count = 0
        for t in tokens:
            if (periodic_table['element'] == t).any():
                valid_count += 1
            else:
                invalid.append(t)

        # Chip input handles styling natively

        if invalid:
            msg = _text(self.language, 'missing_element').format(invalid[0])
            self.elements_count_label.setText(
                self._tr('element_count_error').format(valid_count, msg)
            )
            self.elements_count_label.setStyleSheet("color: #dc2626; font-size: 11px;")
        elif valid_count > 0:
            self.elements_count_label.setText(
                self._tr('element_count').format(valid_count)
            )
            self.elements_count_label.setStyleSheet("color: #64748b; font-size: 11px;")
        else:
            self.elements_count_label.setText("")

    def _on_target_element_changed(self, index):
        """Populate isotope selector when element is chosen."""
        elem = self._target_element_input.currentData()
        if not elem:
            self._target_isotope_input.setEnabled(False)
            self._target_isotope_input.clear()
            self.mz_input.clear()
            if hasattr(self, '_target_mz_result_label'):
                self._target_mz_result_label.setText('')
            return
        isotopes = periodic_table[periodic_table['element'] == elem]
        self._target_isotope_input.blockSignals(True)
        self._target_isotope_input.clear()
        for _, row in isotopes.iterrows():
            abun = row['abundance']
            label = f"{row['isotope']}  ({abun*100:.1f}%)"
            self._target_isotope_input.addItem(label, row['isotope'])
        self._target_isotope_input.blockSignals(False)
        self._target_isotope_input.setEnabled(True)
        # Auto-select the most abundant isotope
        max_pos = isotopes['abundance'].idxmax()
        for pos in range(len(isotopes)):
            if isotopes.index[pos] == max_pos:
                self._target_isotope_input.setCurrentIndex(pos)
                break

    def _on_target_isotope_changed(self, index):
        """Update target m/z display when isotope is selected."""
        isotope = self._target_isotope_input.currentData()
        if not isotope:
            self._target_mz_result_label.setText('')
            self.mz_input.clear()
            return
        row = periodic_table[periodic_table['isotope'] == isotope].iloc[0]
        mass = row['mass']
        charges, _ = _current_data(self.charge_preset_input)
        charge = charges[0]
        mz = mass / charge
        self.mz_input.blockSignals(True)
        self.mz_input.setText(str(isotope))
        self.mz_input.blockSignals(False)
        self.mz = str(isotope)
        self._target_mz_result_label.setText(f'{isotope}  →  m/z = {mz:.4f}')

    def _update_mz_preview(self):
        """Parse the target input and show m/z preview."""
        text = self.mz_input.text().strip()
        if not text:
            self._mz_preview_label.setText('')
            return
        try:
            mz = float(text)
            self._mz_preview_label.setText(f'→ {mz:.4f} m/z')
            self._mz_preview_label.setStyleSheet("color: #64748b; font-size: 11px;")
            return
        except ValueError:
            pass
        try:
            charges, chargesign = _current_data(self.charge_preset_input)
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

    def export_csv(self):
        """Export current result table as CSV."""
        model = self.table_output.model()
        if model is None or model.rowCount() == 0:
            self.set_status(self._tr('export_no_data'))
            return
        # If using a proxy model, get the underlying source model for the data
        if hasattr(model, 'sourceModel') and model.sourceModel() is not None:
            source = model.sourceModel()
        else:
            source = model
        df = source._data
        path, _ = widgets.QFileDialog.getSaveFileName(
            self, self._tr('export_csv'), '', self._tr('csv_files_filter')
        )
        if not path:
            return
        try:
            df.to_csv(path, index=False)
            self.set_status(self._tr('exported_rows').format(len(df), path))
        except Exception as e:
            widgets.QMessageBox.critical(self, self._tr('export_error'), str(e))

    def export_xlsx(self):
        """Export current result table as Excel (.xlsx)."""
        model = self.table_output.model()
        if model is None or model.rowCount() == 0:
            self.set_status(self._tr('export_no_data'))
            return
        try:
            import openpyxl  # noqa: F401
        except ImportError:
            reply = widgets.QMessageBox.question(
                self, self._tr('missing_dependency'),
                self._tr('excel_export_missing'),
                widgets.QMessageBox.Yes | widgets.QMessageBox.No
            )
            if reply == widgets.QMessageBox.Yes:
                self.export_csv()
            return
        if hasattr(model, 'sourceModel') and model.sourceModel() is not None:
            source = model.sourceModel()
        else:
            source = model
        df = source._data
        path, _ = widgets.QFileDialog.getSaveFileName(
            self, self._tr('export_xlsx'), '', self._tr('excel_files_filter')
        )
        if not path:
            return
        try:
            df.to_excel(path, index=False, engine='openpyxl')
            self.set_status(self._tr('exported_rows').format(len(df), path))
        except Exception as e:
            widgets.QMessageBox.critical(self, self._tr('export_error'), str(e))

    def _make_filter_chip(self, label_key, query, bg_color):
        """Create a clickable quick-filter preset chip."""
        chip = widgets.QLabel(self._tr(label_key), parent=self.results_panel)
        chip.setObjectName('filterChip')
        chip.setStyleSheet(
            f"QLabel#filterChip {{ background: {bg_color}; border: 1px solid #cbd5e1; "
            "border-radius: 4px; padding: 2px 8px; font-size: 11px; color: #334155; } "
            "QLabel#filterChip:hover { border-color: #1e40af; }"
        )
        chip.setCursor(QtCore.Qt.PointingHandCursor)
        chip._label_key = label_key
        chip._filter_query = query
        chip.mousePressEvent = lambda evt, q=query: self._apply_chip_filter(q)
        self._filter_chips.append(chip)
        return chip

    def _apply_chip_filter(self, query):
        """Apply a quick-filter chip's query to the filter bar."""
        if self.filter_bar.text() == query:
            self.filter_bar.clear()
        else:
            self.filter_bar.setText(query)

    def _apply_filter(self):
        """Apply filter text to the result table proxy model and update spectrum."""
        model = self.table_output.model()
        if isinstance(model, InterferenceFilterProxy):
            model.set_filter_text(self.filter_bar.text())
        # Update count metric label when filter changes
        self._update_filtered_count()
        # Sync spectrum to filtered data
        self._sync_filtered_spectrum()

    def _sync_filtered_spectrum(self):
        """Re-plot spectrum with only currently visible rows."""
        if self.result_metrics.get('kind') != 'interference':
            return
        spectrum_data = getattr(self, '_spectrum_data', None)
        if spectrum_data is None:
            return
        proxy = self.table_output.model()
        if not isinstance(proxy, InterferenceFilterProxy):
            self.spectrum_window.plot_spectrum(spectrum_data)
            return
        src = proxy.sourceModel()
        if src is None or not hasattr(src, '_data'):
            return
        # proxy sourceModel has same row count as spectrum_data
        visible_rows = []
        for row in range(src.rowCount()):
            if proxy.filterAcceptsRow(row, QtCore.QModelIndex()):
                visible_rows.append(row)
        # Always include the target row in the spectrum
        target_col = 'target'
        target_rows_indices = []
        if target_col in src._data.columns:
            target_series = src._data[target_col]
            for idx in range(len(target_series)):
                if target_series.iloc[idx] == True:
                    target_rows_indices.append(idx)
        for tr in target_rows_indices:
            if tr not in visible_rows:
                visible_rows.append(tr)
        visible_rows = sorted(visible_rows)

        if len(visible_rows) == src.rowCount():
            self.spectrum_window.plot_spectrum(spectrum_data)
        else:
            filtered = spectrum_data.iloc[visible_rows].reset_index(drop=True)
            self.spectrum_window.plot_spectrum(filtered)

    def _select_result_row_from_spectrum(self, source_row):
        """Select the result-table row corresponding to a clicked spectrum peak."""
        model = self.table_output.model()
        if model is None:
            return
        view_index = QtCore.QModelIndex()
        if isinstance(model, InterferenceFilterProxy):
            source_model = model.sourceModel()
            if source_model is None or source_row < 0 or source_row >= source_model.rowCount():
                return
            source_index = source_model.index(source_row, 0)
            view_index = model.mapFromSource(source_index)
            if not view_index.isValid():
                self._set_filter_text('')
                view_index = model.mapFromSource(source_index)
        else:
            if source_row < 0 or source_row >= model.rowCount():
                return
            view_index = model.index(source_row, 0)
        if not view_index.isValid():
            return
        self.table_output.selectRow(view_index.row())
        self.table_output.scrollTo(view_index, widgets.QAbstractItemView.PositionAtCenter)
        self.table_output.setFocus()
        self.set_status(self._tr('spectrum_peak_selected').format(source_row + 1), time=3000)

    def _update_filtered_count(self):
        """Show filtered/total row count in the count metric label."""
        model = self.table_output.model()
        if model is None or model.rowCount() == 0:
            return
        view_model = model
        if isinstance(view_model, InterferenceFilterProxy):
            src = view_model.sourceModel()
            total = src.rowCount() if src else 0
            visible = view_model.rowCount()
        else:
            total = view_model.rowCount()
            visible = total
        if visible < total:
            text = self.count_metric_label.text()
            # Append count only if not already showing it
            base = text.split(' (')[0] if ' (' in text else text
            self.count_metric_label.setText(f'{base} ({visible}/{total})')

    def _show_column_menu(self, position):
        """Show right-click column visibility menu on result table header."""
        header = self.table_output.horizontalHeader()
        view_model = self.table_output.model()
        if isinstance(view_model, InterferenceFilterProxy):
            src = view_model.sourceModel()
        else:
            src = view_model
        if src is None or not hasattr(src, '_data'):
            return
        menu = widgets.QMenu(self)
        for col in range(src.columnCount()):
            colname = src._data.columns[col]
            if colname == 'target':
                continue  # always hide target column
            display_name = _column_display(self.language, colname)
            action = menu.addAction(display_name)
            action.setCheckable(True)
            action.setChecked(not self.table_output.isColumnHidden(col))
            action.setData(col)
        menu.addSeparator()
        reset_action = menu.addAction(
            self._tr('show_all_columns')
        )
        action = menu.exec_(header.mapToGlobal(position))
        if action is None:
            return
        if action == reset_action:
            for col in range(src.columnCount()):
                colname = src._data.columns[col]
                if colname == 'target':
                    continue
                self.table_output.setColumnHidden(col, False)
            return
        col = action.data()
        self.table_output.setColumnHidden(col, not action.isChecked())

    def eventFilter(self, obj, event):
        """Handle clicks on quick-filter chips."""
        if obj is self.count_metric_label and event.type() == QtCore.QEvent.MouseButtonPress:
            kind = self.result_metrics.get('kind')
            if kind == 'interference':
                if self._filter_active:
                    # Clear filter
                    self._filter_active = False
                    self.filter_bar.clear()
                    self.count_metric_label.setStyleSheet("")
                else:
                    # Set filter to show unresolved
                    self._filter_active = True
                    self.filter_bar.setText('ok:no')
                    self.count_metric_label.setStyleSheet(
                        "background: #fef3c7; color: #92400e; border: 1px solid #f59e0b;"
                    )
                self.count_metric_label.setObjectName('metricChip')
            return True
        return super(MainWidget, self).eventFilter(obj, event)

    def resize_table_sections(self):
        """ Resize result table columns for the active Qt version. """
        header = self.table_output.horizontalHeader()
        view_model = self.table_output.model()
        if isinstance(view_model, InterferenceFilterProxy):
            source_model = view_model.sourceModel()
        else:
            source_model = view_model
        try:
            for column in range(source_model.columnCount()):
                header.setSectionResizeMode(column, widgets.QHeaderView.Interactive)
        except AttributeError:
            for column in range(source_model.columnCount()):
                header.setResizeMode(column, widgets.QHeaderView.Interactive)

        widths = {
            'molecule': 160,
            'ion': 160,
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
        for column in range(source_model.columnCount()):
            colname = source_model._data.columns[column]
            self.table_output.setColumnWidth(column, widths.get(colname, 100))

        # Let ion/molecule column resize to content with max-width cap
        for column in range(source_model.columnCount()):
            colname = source_model._data.columns[column]
            if colname in ('ion', 'molecule'):
                try:
                    header.setSectionResizeMode(column, widgets.QHeaderView.ResizeToContents)
                except AttributeError:
                    header.setResizeMode(column, widgets.QHeaderView.ResizeToContents)

    def _batch_table_update(self):
        """Disable table painting temporarily for bulk updates."""
        self.table_output.setUpdatesEnabled(False)
        self.table_output.setVisible(False)

    def _unbatch_table_update(self):
        """Re-enable table painting after bulk updates."""
        self.table_output.setVisible(True)
        self.table_output.setUpdatesEnabled(True)

    def check_atoms_input(self):
        """ Validate input for atoms_input.
            Returns True on proper validation, False on error.
        """
        atoms = self.atoms_input.elements() if hasattr(self, 'atoms_input') else self.atoms
        if not atoms:
            self.warn(self._tr('empty_atoms'))
            return False
        for a in atoms:
            if not (periodic_table['element'] == a).any(): 
                self.warn(self._tr('missing_element').format(a))
                return False
        self.atoms = list(atoms)
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
        half_window = self.sweep_input.value() / 2.0

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
        elif (key == QtCore.Qt.Key_E and mod == QtCore.Qt.ControlModifier):
            self.export_csv()
        else:
            super(MainWidget, self).keyPressEvent(event)

    @QtCore.pyqtSlot()
    def calculate_interference(self):
        """Take input, calculate mass spectrum, display in table."""
        if not (self.check_atoms_input() and
                self.check_charges_input() and
                self.check_mz_input()):
            return

        self.maxsize = self.maxsize_input.value()
        self.mzrange = self.targetrange_mz()
        if self.mzrange is None:
            return

        risk_preset = _current_data(self.mode_input)

        # Clean up any previous calculation thread
        self._cleanup_calc_thread()

        # Track this request so we can discard stale results
        self._calc_request_id += 1
        request_id = self._calc_request_id

        # Disable inputs during calculation
        self.interference_button.setEnabled(False)
        self.maxsize_input.setEnabled(False)
        self.charge_preset_input.setEnabled(False)
        self.atoms_input.setReadOnly(True)

        # Show progress bar
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)
        self.set_status(self._tr('calculating'))

        # Create and start the background worker
        worker = CalculationWorker(
            self.atoms, self.mz, self.mzrange, self.maxsize,
            self.charges, self.chargesign, risk_preset,
            instrument_mrp=self.instrument_mrp_input.value(),
            language=self.language,
        )
        thread = QtCore.QThread(self)
        self._calc_worker = worker
        self._calc_thread = thread
        worker.moveToThread(thread)
        worker.progress.connect(self._progress_bar.setValue)
        worker.finished.connect(
            lambda data, rid=request_id: self._on_calc_finished(data, rid)
        )
        worker.error.connect(self._on_calc_error)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.started.connect(worker.run)
        thread.finished.connect(
            lambda t=thread, w=worker: self._on_calc_thread_finished(t, w)
        )
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _cleanup_calc_thread(self):
        """Cancel and clean up any running calculation thread."""
        thread = self._calc_thread
        worker = self._calc_worker
        self._calc_thread = None
        self._calc_worker = None
        if thread is not None:
            try:
                running = thread.isRunning()
            except RuntimeError:
                return
            if running:
                if worker is not None:
                    try:
                        worker.cancel()
                    except RuntimeError:
                        pass
                try:
                    thread.quit()
                    thread.wait(2000)
                except RuntimeError:
                    pass

    def _on_calc_thread_finished(self, thread, worker):
        """Clear stale Qt thread wrappers once Qt has finished the worker thread."""
        if self._calc_thread is thread:
            self._calc_thread = None
        if self._calc_worker is worker:
            self._calc_worker = None

    def _on_calc_finished(self, data, request_id):
        """Handle completion of background calculation."""
        if request_id != self._calc_request_id:
            return  # stale result \u2014 discard

        self._progress_bar.setVisible(False)
        self._re_enable_inputs()

        target_mask = data['target'].astype(bool)
        if target_mask.any():
            target_mz = data.loc[target_mask, 'mass/charge'].iat[0]
        else:
            target_mz = np.nan

        spectrum_data = data.copy()
        spectrum_data['_source_row'] = np.arange(data.shape[0])
        spectrum_data.attrs['window_half_mz'] = float(self.mzrange)
        spectrum_data.attrs['instrument_mrp'] = float(self.instrument_mrp_input.value())
        if target_mz and np.isfinite(target_mz):
            spectrum_data.attrs['target_mz'] = float(target_mz)
            spectrum_data.attrs['window_half_ppm'] = float(self.mzrange / target_mz * 1e6)
        self._spectrum_data = spectrum_data

        display_data = data[['molecule', 'type', 'charge', 'mass/charge',
                             'mass/charge diff', '\u0394ppm', 'MRP',
                             'probability', 'relative risk', 'resolved',
                             'target']].copy()
        display_data.columns = ['ion', 'type', 'z', 'm/z', '\u0394m/z',
                                '\u0394ppm', 'MRP', 'prob.', 'risk', 'ok',
                                'target']

        candidate_count = int((~display_data['target'].astype(bool)).sum())
        unresolved_count = int(sum((value != '') and not bool(value) for value in display_data['ok']))

        metrics = {
            'kind': 'interference',
            'candidate_count': candidate_count,
            'unresolved_count': unresolved_count,
        }
        self._cache_interference_results(display_data, spectrum_data, metrics)
        self._show_interference_results(
            display_data, spectrum_data, metrics,
            filter_text='',
            status_text=self._tr('candidate_count').format(candidate_count),
        )

    def _on_calc_error(self, err_msg):
        """Handle error from background calculation."""
        self._progress_bar.setVisible(False)
        self._re_enable_inputs()
        widgets.QMessageBox.critical(self, self._tr('calculation_error'), err_msg)

    def _re_enable_inputs(self):
        """Re-enable inputs after calculation completes or errors."""
        self.interference_button.setEnabled(True)
        self.maxsize_input.setEnabled(True)
        self.charge_preset_input.setEnabled(True)
        self.atoms_input.setReadOnly(False)
        widgets.QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def show_standard_ratio(self):
        """Show isotope ratios, or restore interference results from ratio view."""
        if self.result_metrics.get('kind') == 'ratios' and self._restore_interference_results():
            return

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
        proxy = InterferenceFilterProxy(self)
        self._batch_table_update()
        proxy.setSourceModel(model)
        self.table_output.setModel(proxy)
        self.table_output.setColumnHidden(data.columns.get_loc('target'), True)
        self.resize_table_sections()
        self._unbatch_table_update()
        self.filter_container.setVisible(True)
        self._filter_chip_bar.setVisible(False)
        self._set_filter_text('')
        self.filter_bar.setFocus()
        self.result_metrics = {'kind': 'ratios', 'isotope_count': data.shape[0]}
        self.results_stack.setCurrentWidget(self.table_output)
        self.update_result_summary()
        self._update_ratio_button_label()
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
