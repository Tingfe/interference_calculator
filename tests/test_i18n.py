#!/usr/bin/env python
"""Tests for internationalization system."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from interference_calculator.i18n import (
    TranslationManager, get_translation_manager, 
    set_language, translate
)


class TestTranslationManager:
    """Test TranslationManager class."""
    
    def test_create_manager(self):
        """Test creating TranslationManager instance."""
        manager = TranslationManager()
        assert manager.current_language == 'en'
        assert len(manager.translations) >= 2  # At least en and zh
    
    def test_get_available_languages(self):
        """Test getting available languages."""
        manager = TranslationManager()
        langs = manager.get_available_languages()
        
        assert 'en' in langs
        assert 'zh' in langs
        assert langs['en']['name'] == 'English'
        assert langs['zh']['native_name'] == '中文'
    
    def test_set_language_english(self):
        """Test setting language to English."""
        manager = TranslationManager()
        result = manager.set_language('en')
        
        assert result is True
        assert manager.get_current_language() == 'en'
    
    def test_set_language_chinese(self):
        """Test setting language to Chinese."""
        manager = TranslationManager()
        result = manager.set_language('zh')
        
        assert result is True
        assert manager.get_current_language() == 'zh'
    
    def test_set_language_chinese(self):
        """Test setting language to Chinese."""
        manager = TranslationManager()
        result = manager.set_language('zh')
        
        assert result is True
        assert manager.get_current_language() == 'zh'
    
    def test_set_invalid_language(self):
        """Test setting invalid language code."""
        manager = TranslationManager()
        result = manager.set_language('invalid')
        
        assert result is False
        assert manager.get_current_language() == 'en'  # Should remain default
    
    def test_translate_basic(self):
        """Test basic translation."""
        manager = TranslationManager()
        
        # English should return key or default
        text = manager.translate('calculate', 'Calculate')
        assert text is not None
    
    def test_translate_missing_key(self):
        """Test translation with missing key."""
        manager = TranslationManager()
        
        result = manager.translate('nonexistent_key', 'Default Text')
        assert result == 'Default Text'
    
    def test_translate_no_default(self):
        """Test translation without default returns key."""
        manager = TranslationManager()
        
        result = manager.translate('nonexistent_key')
        assert result == 'nonexistent_key'
    
    def test_translate_type(self):
        """Test type translation."""
        manager = TranslationManager()
        
        # Should return the value or translated version
        result = manager.translate_type('atomic')
        assert isinstance(result, str)
    
    def test_translate_column(self):
        """Test column header translation."""
        manager = TranslationManager()
        
        result = manager.translate_column('Ion')
        assert isinstance(result, str)
    
    def test_translate_mode(self):
        """Test mode name translation."""
        manager = TranslationManager()
        
        result = manager.translate_mode('GDMS')
        assert isinstance(result, str)
    
    def test_translate_charge(self):
        """Test charge option translation."""
        manager = TranslationManager()
        
        result = manager.translate_charge('1+')
        assert isinstance(result, str)
    
    def test_language_switching(self):
        """Test switching between languages."""
        manager = TranslationManager()
        
        # Switch to Chinese
        manager.set_language('zh')
        assert manager.get_current_language() == 'zh'
        
        # Switch back to English
        manager.set_language('en')
        assert manager.get_current_language() == 'en'


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_get_translation_manager(self):
        """Test getting global translation manager."""
        manager = get_translation_manager()
        assert manager is not None
        assert isinstance(manager, TranslationManager)
    
    def test_set_language_function(self):
        """Test set_language convenience function."""
        result = set_language('en')
        assert result is True
    
    def test_translate_function(self):
        """Test translate convenience function."""
        result = translate('test_key', 'Test')
        assert result is not None
    
    def test_global_manager_persistence(self):
        """Test that global manager persists state."""
        manager1 = get_translation_manager()
        manager1.set_language('en')
        
        manager2 = get_translation_manager()
        assert manager1 is manager2  # Same instance



if __name__ == '__main__':
    pytest.main([__file__, '-v'])
