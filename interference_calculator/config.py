"""Configuration persistence system for user preferences."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manage application configuration with JSON backend."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize config manager.
        
        Args:
            config_dir: Custom config directory. Uses platform default if None.
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Platform-specific config directory
            if os.name == 'nt':  # Windows
                self.config_dir = Path(os.environ['APPDATA']) / 'InterferenceCalculator'
            else:  # macOS/Linux
                self.config_dir = Path.home() / '.config' / 'interference_calculator'
        
        self.config_file = self.config_dir / 'config.json'
        self.presets_dir = self.config_dir / 'presets'
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create default config
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Default configuration
        return {
            'version': '1.0',
            'language': 'en',
            'instrument_mode': 'GDMS',
            'elements': [],
            'charges': ['1+'],
            'mrp_presets': {
                'GDMS': 5000,
                'ICP-MS': 10000,
                'SIMS': 5000
            },
            'window_geometry': None,
            'recent_targets': [],
            'spectrum_settings': {
                'x_axis_mode': 'm/z',  # 'm/z', 'delta_mz', 'delta_ppm'
                'y_log_scale': False,
                'show_grid': True
            }
        }
    
    def save(self) -> None:
        """Save current configuration to file."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def save_preset(self, name: str) -> str:
        """Save current settings as a named preset.
        
        Returns:
            Path to saved preset file.
        """
        preset_file = self.presets_dir / f"{name}.json"
        with open(preset_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        return str(preset_file)
    
    def load_preset(self, name: str) -> bool:
        """Load a named preset.
        
        Returns:
            True if successful, False otherwise.
        """
        preset_file = self.presets_dir / f"{name}.json"
        if not preset_file.exists():
            return False
        
        try:
            with open(preset_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except (json.JSONDecodeError, IOError):
            return False
    
    def list_presets(self) -> list:
        """List available presets."""
        return [f.stem for f in self.presets_dir.glob('*.json')]
    
    def export_config(self, filepath: str) -> None:
        """Export configuration to specified file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def import_config(self, filepath: str) -> bool:
        """Import configuration from file.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            self.config.update(imported)
            return True
        except (json.JSONDecodeError, IOError, KeyError):
            return False
    
    def add_recent_target(self, target_mz: float) -> None:
        """Add target m/z to recent list (max 10)."""
        recent = self.config.get('recent_targets', [])
        if target_mz in recent:
            recent.remove(target_mz)
        recent.insert(0, target_mz)
        self.config['recent_targets'] = recent[:10]
    
    def close(self) -> None:
        """Save configuration on shutdown."""
        self.save()
