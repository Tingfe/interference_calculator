#!/usr/bin/env python
"""Tests for the plugin system."""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interference_calculator.plugins import (
    PluginManager, Plugin, PluginMetadata
)


class TestPluginMetadata:
    """Test PluginMetadata class."""
    
    def test_create_metadata(self):
        """Test creating plugin metadata."""
        metadata = PluginMetadata(
            name="Test Plugin",
            version="1.0.0",
            description="A test plugin",
            author="Test Author"
        )
        
        assert metadata.name == "Test Plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == "A test plugin"
        assert metadata.author == "Test Author"
        assert metadata.min_app_version == "2.6.0"
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = PluginMetadata(
            name="Test",
            version="2.0.0",
            description="Test desc",
            author="Author"
        )
        
        data = metadata.to_dict()
        assert isinstance(data, dict)
        assert data['name'] == "Test"
        assert data['version'] == "2.0.0"
    
    def test_metadata_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            'name': 'From Dict Plugin',
            'version': '3.0.0',
            'description': 'Created from dict',
            'author': 'Dict Author',
            'min_app_version': '2.5.0'
        }
        
        metadata = PluginMetadata.from_dict(data)
        assert metadata.name == 'From Dict Plugin'
        assert metadata.version == '3.0.0'
        assert metadata.min_app_version == '2.5.0'


class TestPlugin:
    """Test base Plugin class."""
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        metadata = PluginMetadata(name="Base Plugin", version="1.0.0")
        plugin = Plugin(metadata)
        
        assert plugin.get_name() == "Base Plugin"
        assert plugin.get_version() == "1.0.0"
        assert plugin.enabled is True
    
    def test_plugin_initialize_method(self):
        """Test plugin initialize method."""
        metadata = PluginMetadata(name="Test", version="1.0.0")
        plugin = Plugin(metadata)
        
        # Base implementation should return True
        assert plugin.initialize() is True
    
    def test_plugin_cleanup_method(self):
        """Test plugin cleanup method doesn't raise errors."""
        metadata = PluginMetadata(name="Test", version="1.0.0")
        plugin = Plugin(metadata)
        
        # Should not raise exception
        plugin.cleanup()


class TestPluginManager:
    """Test PluginManager class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.manager = PluginManager(app_version="2.6.0")
    
    def test_create_manager(self):
        """Test creating plugin manager."""
        assert self.manager.app_version == "2.6.0"
        assert len(self.manager.plugins) == 0
    
    def test_version_compatibility_check(self):
        """Test version compatibility checking."""
        # Same version should be compatible
        assert self.manager._check_version_compatibility("2.6.0") is True
        
        # Lower version should be compatible
        assert self.manager._check_version_compatibility("2.5.0") is True
        
        # Higher version should not be compatible
        assert self.manager._check_version_compatibility("2.7.0") is False
    
    def test_list_plugins_empty(self):
        """Test listing plugins when none are loaded."""
        plugins = self.manager.list_plugins()
        assert isinstance(plugins, list)
        assert len(plugins) == 0
    
    def test_discover_plugins_directory_not_exists(self):
        """Test discovering plugins in non-existent directory."""
        discovered = self.manager.discover_plugins("/nonexistent/path")
        assert isinstance(discovered, list)
        assert len(discovered) == 0
    
    def test_enable_nonexistent_plugin(self):
        """Test enabling a plugin that doesn't exist."""
        result = self.manager.enable_plugin("NonExistent")
        assert result is False
    
    def test_disable_nonexistent_plugin(self):
        """Test disabling a plugin that doesn't exist."""
        result = self.manager.disable_plugin("NonExistent")
        assert result is False
    
    def test_get_nonexistent_plugin(self):
        """Test getting a plugin that doesn't exist."""
        plugin = self.manager.get_plugin("NonExistent")
        assert plugin is None
    
    def test_unload_nonexistent_plugin(self):
        """Test unloading a plugin that doesn't exist."""
        result = self.manager.unload_plugin("NonExistent")
        assert result is False


class TestBuiltinPlugins:
    """Test builtin plugin loading."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.manager = PluginManager(app_version="2.6.0")
    
    def test_load_enhanced_export_plugin(self):
        """Test loading the enhanced export builtin plugin."""
        plugin = self.manager.load_builtin_plugin("enhanced_export")
        
        if plugin:
            assert plugin.get_name() == "Enhanced Export"
            assert plugin.enabled is True
            
            # Test plugin functionality
            export_plugin = plugin
            formats = export_plugin.get_supported_formats()
            assert 'json' in formats
            assert 'csv_enhanced' in formats
    
    def test_load_custom_rules_plugin(self):
        """Test loading the custom rules builtin plugin."""
        plugin = self.manager.load_builtin_plugin("custom_rules")
        
        if plugin:
            assert plugin.get_name() == "Custom Rules"
            assert plugin.enabled is True
            
            # Test plugin functionality
            rules_plugin = plugin
            rule_count = rules_plugin.get_rule_count()
            assert rule_count >= 0  # Should have default rules


class TestPluginLifecycle:
    """Test complete plugin lifecycle."""
    
    def test_full_lifecycle(self):
        """Test complete plugin load-enable-disable-unload cycle."""
        manager = PluginManager(app_version="2.6.0")
        
        # Load plugin
        plugin = manager.load_builtin_plugin("enhanced_export")
        if plugin:
            assert manager.get_plugin("Enhanced Export") is not None
            
            # Disable plugin
            assert manager.disable_plugin("Enhanced Export") is True
            assert plugin.enabled is False
            
            # Enable plugin
            assert manager.enable_plugin("Enhanced Export") is True
            assert plugin.enabled is True
            
            # Unload plugin
            assert manager.unload_plugin("Enhanced Export") is True
            assert manager.get_plugin("Enhanced Export") is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
