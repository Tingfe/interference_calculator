#!/usr/bin/env python
"""
Internationalization (i18n) manager for Interference Calculator.

Provides runtime language switching and translation management.
"""

from typing import Dict, Optional


class TranslationManager:
    """Manages translations and language switching."""
    
    def __init__(self):
        self.current_language = 'en'
        self.translations: Dict[str, Dict] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load available translations."""
        # English (default)
        self.translations['en'] = {
            'name': 'English',
            'native_name': 'English'
        }
        
        # Chinese
        self.translations['zh'] = {
            'name': 'Chinese',
            'native_name': '中文'
        }
        
        # Japanese
        try:
            from interference_calculator.i18n_ja import get_japanese_translations
            ja_data = get_japanese_translations()
            self.translations['ja'] = {
                'name': 'Japanese',
                'native_name': '日本語',
                'ui_text': ja_data['ui_text'],
                'type_display': ja_data['type_display'],
                'column_display': ja_data['column_display'],
                'mode_names': ja_data['mode_names'],
                'charge_options': ja_data['charge_options'],
            }
        except ImportError:
            pass  # Japanese translations not available
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the current language.
        
        Args:
            language_code: Language code ('en', 'zh', 'ja')
        
        Returns:
            True if language was changed successfully
        """
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False
    
    def get_current_language(self) -> str:
        """Get current language code."""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, Dict]:
        """Get all available languages."""
        return self.translations.copy()
    
    def translate(self, key: str, default: str = None) -> str:
        """
        Translate a text key to current language.
        
        Args:
            key: Translation key
            default: Default value if translation not found
        
        Returns:
            Translated text or default
        """
        lang_data = self.translations.get(self.current_language, {})
        
        # Try to get from ui_text first
        ui_text = lang_data.get('ui_text', {})
        if key in ui_text:
            return ui_text[key]
        
        # Fall back to default
        return default or key
    
    def translate_type(self, type_value: str) -> str:
        """Translate ion type display."""
        lang_data = self.translations.get(self.current_language, {})
        type_display = lang_data.get('type_display', {})
        return type_display.get(type_value, type_value)
    
    def translate_column(self, column_name: str) -> str:
        """Translate column header."""
        lang_data = self.translations.get(self.current_language, {})
        column_display = lang_data.get('column_display', {})
        return column_display.get(column_name, column_name)
    
    def translate_mode(self, mode: str) -> str:
        """Translate mode name."""
        lang_data = self.translations.get(self.current_language, {})
        mode_names = lang_data.get('mode_names', {})
        return mode_names.get(mode, mode)
    
    def translate_charge(self, charge: str) -> str:
        """Translate charge option."""
        lang_data = self.translations.get(self.current_language, {})
        charge_options = lang_data.get('charge_options', {})
        return charge_options.get(charge, charge)


# Global translation manager instance
translation_manager = TranslationManager()


def get_translation_manager() -> TranslationManager:
    """Get the global translation manager."""
    return translation_manager


def set_language(language_code: str) -> bool:
    """Convenience function to set language."""
    return translation_manager.set_language(language_code)


def translate(key: str, default: str = None) -> str:
    """Convenience function to translate text."""
    return translation_manager.translate(key, default)
