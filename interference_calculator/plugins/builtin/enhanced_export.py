#!/usr/bin/env python
"""
Example Plugin: Enhanced Data Export

This plugin provides additional export formats for interference calculation results,
including JSON and CSV with custom formatting options.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any

from .. import Plugin, PluginMetadata


class EnhancedExportPlugin(Plugin):
    """Plugin for enhanced data export functionality."""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.export_formats = ['json', 'csv_enhanced']
    
    def initialize(self) -> bool:
        """Initialize the export plugin."""
        print(f"Enhanced Export Plugin v{self.metadata.version} initialized")
        return True
    
    def export_to_json(self, data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export calculation results to JSON format."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Data exported to JSON: {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def export_to_enhanced_csv(self, data: List[Dict[str, Any]], 
                                output_path: str, 
                                delimiter: str = ',') -> bool:
        """Export calculation results to CSV with enhanced formatting."""
        try:
            if not data:
                return False
            
            fieldnames = list(data[0].keys())
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
            
            print(f"Data exported to enhanced CSV: {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported export formats."""
        return self.export_formats.copy()
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        print("Enhanced Export Plugin cleaned up")


# Create plugin instance
plugin_instance = EnhancedExportPlugin(
    PluginMetadata(
        name="Enhanced Export",
        version="1.0.0",
        description="Provides JSON and enhanced CSV export formats",
        author="Interference Calculator Team",
        min_app_version="2.6.0"
    )
)
