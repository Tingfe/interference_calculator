import unittest
import tempfile
import os
from interference_calculator.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        """Create temporary config directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ConfigManager(config_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_default_config_created(self):
        """Test default configuration is created."""
        self.assertEqual(self.config.get('version'), '1.0')
        self.assertEqual(self.config.get('language'), 'en')
        self.assertIn('GDMS', self.config.get('mrp_presets'))
    
    def test_save_and_load(self):
        """Test configuration can be saved and loaded."""
        self.config.set('test_key', 'test_value')
        self.config.save()
        
        # Create new instance to load
        new_config = ConfigManager(config_dir=self.temp_dir)
        self.assertEqual(new_config.get('test_key'), 'test_value')
    
    def test_preset_save_load(self):
        """Test preset save and load."""
        self.config.set('preset_test', 'value1')
        preset_path = self.config.save_preset('my_preset')
        
        # Modify and load preset
        self.config.set('preset_test', 'value2')
        success = self.config.load_preset('my_preset')
        
        self.assertTrue(success)
        self.assertEqual(self.config.get('preset_test'), 'value1')
    
    def test_recent_targets(self):
        """Test recent targets management."""
        self.config.add_recent_target(75.0)
        self.config.add_recent_target(56.0)
        self.config.add_recent_target(75.0)  # Duplicate should move to front
        
        recent = self.config.get('recent_targets')
        self.assertEqual(recent[0], 75.0)
        self.assertEqual(recent[1], 56.0)
        self.assertLessEqual(len(recent), 10)
    
    def test_export_import(self):
        """Test config export and import."""
        self.config.set('export_test', 'original')
        
        export_file = os.path.join(self.temp_dir, 'export.json')
        self.config.export_config(export_file)
        
        # Modify and import
        self.config.set('export_test', 'modified')
        success = self.config.import_config(export_file)
        
        self.assertTrue(success)
        self.assertEqual(self.config.get('export_test'), 'original')


if __name__ == '__main__':
    unittest.main()
