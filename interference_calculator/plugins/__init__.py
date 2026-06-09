#!/usr/bin/env python
"""
Plugin system for Interference Calculator.

This module provides a flexible plugin architecture that allows users to extend
the functionality of the application through YAML configuration and Python plugins.
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


class PluginMetadata:
    """Metadata for a plugin."""
    
    def __init__(self, name: str, version: str, description: str = "", 
                 author: str = "", min_app_version: str = "2.6.0"):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.min_app_version = min_app_version
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'min_app_version': self.min_app_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'PluginMetadata':
        return cls(
            name=data.get('name', 'Unknown'),
            version=data.get('version', '0.1.0'),
            description=data.get('description', ''),
            author=data.get('author', ''),
            min_app_version=data.get('min_app_version', '2.6.0')
        )


class Plugin:
    """Base class for all plugins."""
    
    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.enabled = True
    
    def initialize(self) -> bool:
        """Called when the plugin is loaded. Return True if successful."""
        return True
    
    def cleanup(self) -> None:
        """Called when the plugin is unloaded."""
        pass
    
    def get_name(self) -> str:
        return self.metadata.name
    
    def get_version(self) -> str:
        return self.metadata.version


class PluginManager:
    """Manages plugin loading, initialization, and lifecycle."""
    
    def __init__(self, app_version: str = "2.6.0"):
        self.app_version = app_version
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
    
    def load_plugin_from_config(self, config_path: str) -> Optional[Plugin]:
        """Load a plugin from a YAML configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            metadata = PluginMetadata.from_dict(config.get('metadata', {}))
            
            # Check version compatibility
            if not self._check_version_compatibility(metadata.min_app_version):
                print(f"Warning: Plugin {metadata.name} requires app version "
                      f"{metadata.min_app_version}, current is {self.app_version}")
                return None
            
            # Load plugin module
            module_path = config.get('plugin', {}).get('module', '')
            if module_path:
                plugin_class = self._load_plugin_module(module_path, config)
                if plugin_class:
                    plugin = plugin_class(metadata)
                    if plugin.initialize():
                        self.plugins[metadata.name] = plugin
                        self.plugin_configs[metadata.name] = config
                        return plugin
            
            return None
        except Exception as e:
            print(f"Error loading plugin from {config_path}: {e}")
            return None
    
    def load_builtin_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Load a built-in plugin by name."""
        builtin_plugins_dir = Path(__file__).parent / 'builtin'
        config_path = builtin_plugins_dir / f'{plugin_name}.yaml'
        
        if config_path.exists():
            return self.load_plugin_from_config(str(config_path))
        return None
    
    def discover_plugins(self, plugins_dir: str = None) -> List[str]:
        """Discover available plugins in a directory."""
        if plugins_dir is None:
            plugins_dir = str(Path(__file__).parent / 'plugins')
        
        discovered = []
        plugins_path = Path(plugins_dir)
        
        if plugins_path.exists():
            for yaml_file in plugins_path.glob('*.yaml'):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    metadata = PluginMetadata.from_dict(config.get('metadata', {}))
                    discovered.append(metadata.name)
                except Exception as e:
                    print(f"Error reading {yaml_file}: {e}")
        
        return discovered
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a loaded plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a loaded plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            return True
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a loaded plugin by name."""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins with their status."""
        result = []
        for name, plugin in self.plugins.items():
            result.append({
                'name': name,
                'version': plugin.get_version(),
                'enabled': plugin.enabled,
                'metadata': plugin.metadata.to_dict()
            })
        return result
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].cleanup()
                del self.plugins[plugin_name]
                if plugin_name in self.plugin_configs:
                    del self.plugin_configs[plugin_name]
                return True
            except Exception as e:
                print(f"Error unloading plugin {plugin_name}: {e}")
                return False
        return False
    
    def _check_version_compatibility(self, min_version: str) -> bool:
        """Check if the current app version meets the minimum requirement."""
        # Simple version comparison (can be enhanced with packaging library)
        try:
            current_parts = [int(x) for x in self.app_version.split('.')]
            required_parts = [int(x) for x in min_version.split('.')]
            
            for current, required in zip(current_parts, required_parts):
                if current > required:
                    return True
                elif current < required:
                    return False
            return True
        except ValueError:
            return True  # If parsing fails, assume compatible
    
    def _load_plugin_module(self, module_path: str, config: Dict) -> Optional[type]:
        """Load a plugin class from a module path."""
        try:
            spec = importlib.util.spec_from_file_location(
                "plugin_module", module_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                class_name = config.get('plugin', {}).get('class', 'Plugin')
                plugin_class = getattr(module, class_name, None)
                
                if plugin_class and issubclass(plugin_class, Plugin):
                    return plugin_class
            
            return None
        except Exception as e:
            print(f"Error loading plugin module {module_path}: {e}")
            return None


# Global plugin manager instance
plugin_manager = PluginManager()
