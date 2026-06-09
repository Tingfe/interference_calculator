#!/usr/bin/env python
"""
Japanese translations for Interference Calculator.

This module provides Japanese language support for the UI.
"""

# UI Text translations
UI_TEXT_JA = {
    # Main window
    'title': '無機質量分析干渉計算機',
    'calculate': '計算',
    'clear': 'クリア',
    'help': 'ヘルプ',
    'export': 'エクスポート',
    'import': 'インポート',
    
    # Labels
    'mode': 'モード',
    'target_peak': 'ターゲットピーク',
    'window_width': 'ウィンドウ幅',
    'elements': '元素',
    'ion_model': 'イオンモデル',
    'charge': '電荷',
    'max_atoms': '最大原子数',
    'instrument_mrp': '仪器MRP',
    
    # Results
    'results': '結果',
    'candidate_peaks': '候補ピーク',
    'unresolved': '未分解',
    'total': '合計',
    
    # Table columns
    'ion': 'イオン',
    'type': 'タイプ',
    'mz': 'm/z',
    'delta_mz': 'Δm/z',
    'delta_ppm': 'Δppm',
    'mrp_required': '必要MRP',
    'probability': '確率',
    'risk': 'リスク',
    'resolvable': '分解可能',
    
    # Messages
    'yes': 'はい',
    'no': 'いいえ',
    'calculating': '計算中...',
    'done': '完了',
    'error': 'エラー',
    'warning': '警告',
    'info': '情報',
    
    # Element selection
    'add_element': '元素を追加',
    'select_elements': '元素を選択',
    'selected_elements': '選択された元素',
    
    # Combinations
    'add_combination': '組み合わせを追加',
    'all_elements': '全元素',
    'plasma_background': 'プラズマ背景',
    'light_elements': '軽元素',
    'halogens_sulfur': 'ハロゲン/硫黄',
    
    # Spectrum
    'spectrum': 'スペクトル',
    'isotope_ratios': '同位体比',
    'observed_peak': '観測ピーク',
    'match_mz': 'm/z一致',
    
    # File operations
    'open_file': 'ファイルを開く',
    'save_results': '結果を保存',
    'file_format': 'ファイル形式',
    
    # Settings
    'settings': '設定',
    'language': '言語',
    'theme': 'テーマ',
    'auto_save': '自動保存',
    
    # Status
    'ready': '準備完了',
    'processing': '処理中',
    'complete': '完了',
}

# Type display translations
TYPE_DISPLAY_JA = {
    'atomic': '原子イオン',
    'doubly charged': '二重電荷',
    'oxide': '酸化物',
    'dioxide': '二酸化物',
    'hydride': '水素化物',
    'hydroxide': '水酸化物',
    'nitride': '窒化物',
    'carbide': '炭化物',
    'sulfide': '硫化物',
    'halide': 'ハロゲン化物',
    'plasma adduct': 'プラズマ付加体',
    'background molecule': '背景分子',
    'cluster': 'クラスター',
}

# Column display translations
COLUMN_DISPLAY_JA = {
    'Ion': 'イオン',
    'Type': 'タイプ',
    'Charge': '電荷',
    'm/z': 'm/z',
    'Δm/z': 'Δm/z',
    'Δppm': 'Δppm',
    'MRP': 'MRP',
    'Probability': '確率',
    'Risk': 'リスク',
    'Resolvable': '分解可能',
}

# Mode names
MODE_NAMES_JA = {
    'GDMS': 'GDMS',
    'ICP-MS': 'ICP-MS',
    'SIMS': 'SIMS',
}

# Charge options
CHARGE_OPTIONS_JA = {
    '1+': '1+',
    '1+, 2+': '1+, 2+',
    '1+, 2+, 3+': '1+, 2+, 3+',
    '1-': '1-',
    'neutral': '中性',
}


def get_japanese_translations():
    """Get all Japanese translations."""
    return {
        'ui_text': UI_TEXT_JA,
        'type_display': TYPE_DISPLAY_JA,
        'column_display': COLUMN_DISPLAY_JA,
        'mode_names': MODE_NAMES_JA,
        'charge_options': CHARGE_OPTIONS_JA,
    }
