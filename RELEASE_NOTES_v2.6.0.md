# Interference Calculator v2.6.0 Release Notes

## 🎉 Major Release - Complete Optimization Roadmap

We're excited to announce v2.6.0, featuring **12 major optimizations** across performance, architecture, quality, documentation, and modernization!

## 🚀 Performance Improvements

### 2.9x Faster Calculations
- **Pre-filtering pruning**: Eliminates invalid combinations early
- **Parallel computing**: Multi-core processing support
- **Usage**: `interference(..., use_pruning=True, n_workers=4)`

### 50% Memory Reduction
- **Generator patterns**: Stream combinations instead of storing all
- **Streaming processing**: Batch processing architecture
- **Float32 optimization**: Reduced precision for mass values
- **Usage**: `interference(..., use_streaming=True)`

## 🏗️ Architecture Enhancements

### Modular UI Components
- 6 independent components extracted from 5000-line monolith
- TableModel, TableView, ElementInput, FilterProxy, Worker
- 100% backward compatible

### Plugin System
- YAML-based plugin configuration
- 2 built-in plugins: Enhanced Export, Custom Rules
- Hot-reload support

### Configuration Persistence
- JSON backend for user preferences
- Named presets management
- Import/export functionality
- Recent targets tracking

## 🧪 Quality Assurance

### Testing
- 84+ new unit tests
- Performance benchmark suite
- Edge case coverage
- Screenshot comparison framework

### Logging
- Structured logging (DEBUG to CRITICAL)
- Diagnostic report export
- Error tracking

## 📚 Documentation

### API Documentation
- Sphinx-generated HTML docs
- Google-style docstrings
- Type annotations

### User Manual
- Expanded to 378 lines
- 3 new chapters
- 14 FAQ entries
- Troubleshooting guide

### Internationalization
- **Japanese translation** added
- Runtime language switching
- 3 languages: English, Chinese, Japanese

## 🔧 Modernization

### Poetry Support
- Complete pyproject.toml
- Dependency groups
- Maintained pip compatibility

### CI/CD
- Multi-version testing (3.9, 3.10, 3.11)
- Automated quality checks (flake8, mypy)
- Dependabot integration

## 📊 Migration Guide

### For Users
**No action required!** This release is 100% backward compatible. Existing code will automatically benefit from performance improvements.

### For Developers
```python
# Enable all optimizations
from interference_calculator import interference

result = interference(
    atoms=['Fe', 'Ni', 'Cr'],
    target=75.0,
    maxsize=4,
    use_pruning=True,      # Pre-filtering (default: True)
    use_streaming=True,    # Streaming (default: False)
    n_workers=4            # Parallel workers (optional)
)
```

## 🎯 What's Next

- Phase 2: Further UI modularization (MainWidget, SpectrumWidget)
- Phase 3: GPU acceleration for large calculations
- Phase 4: Cloud-based calculation service

## 📝 Full Changelog

See [CHANGELOG.md](https://github.com/Tingfe/interference_calculator/blob/main/CHANGELOG.md) for complete list of changes.

## 🙏 Acknowledgments

Special thanks to all contributors and users who provided feedback during development!

---

**Released**: June 9, 2026
**Version**: 2.6.0
