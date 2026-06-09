# User Plugins Directory

Place your custom plugin YAML configuration files here.

## Plugin Structure

Each plugin requires:
1. A YAML configuration file (e.g., `my_plugin.yaml`)
2. A Python module implementing the plugin logic

## Example Plugin Configuration

```yaml
metadata:
  name: "My Custom Plugin"
  version: "1.0.0"
  description: "Description of what this plugin does"
  author: "Your Name"
  min_app_version: "2.6.0"

plugin:
  module: "/path/to/your/plugin.py"
  class: "MyPluginClass"

settings:
  # Plugin-specific settings
  option1: value1
  option2: value2
```

## Creating a Plugin

1. Create a Python file with a class that inherits from `Plugin`
2. Implement required methods: `initialize()`, `cleanup()`
3. Create a YAML config file in this directory
4. The plugin will be automatically discovered on application startup

See builtin plugins for examples.
