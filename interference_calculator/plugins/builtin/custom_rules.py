#!/usr/bin/env python
"""
Example Plugin: Custom Calculation Rules

This plugin allows users to define custom interference calculation rules
and validation logic.
"""

from typing import Dict, List, Any, Optional
from .. import Plugin, PluginMetadata


class CustomRulesPlugin(Plugin):
    """Plugin for custom calculation rules and validations."""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.custom_rules: List[Dict[str, Any]] = []
        self.validation_hooks: List[callable] = []
    
    def initialize(self) -> bool:
        """Initialize the custom rules plugin."""
        print(f"Custom Rules Plugin v{self.metadata.version} initialized")
        # Load default rules
        self._load_default_rules()
        return True
    
    def add_custom_rule(self, rule_name: str, condition: callable, 
                       action: callable) -> bool:
        """Add a custom calculation rule."""
        try:
            rule = {
                'name': rule_name,
                'condition': condition,
                'action': action
            }
            self.custom_rules.append(rule)
            print(f"Added custom rule: {rule_name}")
            return True
        except Exception as e:
            print(f"Error adding custom rule: {e}")
            return False
    
    def apply_rules(self, calculation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all custom rules to calculation data."""
        modified_data = calculation_data.copy()
        
        for rule in self.custom_rules:
            try:
                if rule['condition'](modified_data):
                    modified_data = rule['action'](modified_data)
            except Exception as e:
                print(f"Error applying rule {rule['name']}: {e}")
        
        return modified_data
    
    def add_validation_hook(self, hook: callable) -> bool:
        """Add a validation function that runs after calculations."""
        try:
            self.validation_hooks.append(hook)
            return True
        except Exception as e:
            print(f"Error adding validation hook: {e}")
            return False
    
    def validate_results(self, results: List[Dict[str, Any]]) -> List[str]:
        """Run all validation hooks and return warnings/errors."""
        issues = []
        
        for hook in self.validation_hooks:
            try:
                hook_issues = hook(results)
                if hook_issues:
                    issues.extend(hook_issues)
            except Exception as e:
                issues.append(f"Validation error: {str(e)}")
        
        return issues
    
    def get_rule_count(self) -> int:
        """Return number of active custom rules."""
        return len(self.custom_rules)
    
    def _load_default_rules(self) -> None:
        """Load default calculation rules."""
        # Example: Rule to flag high interference ratios
        def high_ratio_condition(data: Dict[str, Any]) -> bool:
            ratio = data.get('interference_ratio', 0)
            return ratio > 0.5
        
        def high_ratio_action(data: Dict[str, Any]) -> Dict[str, Any]:
            data['warning'] = 'High interference ratio detected'
            return data
        
        self.add_custom_rule('high_ratio_warning', 
                           high_ratio_condition, 
                           high_ratio_action)
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        self.custom_rules.clear()
        self.validation_hooks.clear()
        print("Custom Rules Plugin cleaned up")


# Create plugin instance
plugin_instance = CustomRulesPlugin(
    PluginMetadata(
        name="Custom Rules",
        version="1.0.0",
        description="Allows custom calculation rules and validations",
        author="Interference Calculator Team",
        min_app_version="2.6.0"
    )
)
