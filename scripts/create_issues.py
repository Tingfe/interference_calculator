#!/usr/bin/env python3
"""
批量创建GitHub Issue脚本

此脚本使用GitHub CLI (gh) 为interference_calculator项目创建12个优化任务的Issue。

前置条件:
1. 安装GitHub CLI: brew install gh (macOS) 或 sudo apt install gh (Linux)
2. 认证: gh auth login
3. 确保已创建5个里程碑 (M1-M5)

使用方法:
    python scripts/create_issues.py

输出:
    - 创建12个Issue
    - 每个Issue关联正确的标签和里程碑
    - 输出Issue URL列表
"""

import subprocess
import json
import sys
from typing import Dict, List, Optional


def run_gh_command(args: List[str]) -> str:
    """运行GitHub CLI命令并返回输出"""
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令失败: {' '.join(e.cmd)}")
        print(f"错误信息: {e.stderr}")
        sys.exit(1)


def get_milestone_number(title: str) -> Optional[int]:
    """根据标题获取里程碑编号"""
    output = run_gh_command(['api', 'repos/Tingfe/interference_calculator/milestones'])
    milestones = json.loads(output)
    
    for milestone in milestones:
        if milestone['title'] == title:
            return milestone['number']
    
    return None


def create_issue(title: str, body: str, labels: List[str], milestone_title: str) -> str:
    """创建单个Issue并返回URL"""
    milestone_num = get_milestone_number(milestone_title)
    
    if milestone_num is None:
        print(f"⚠️  警告: 未找到里程碑 '{milestone_title}'，跳过此Issue")
        return None
    
    # 构建标签参数
    label_args = []
    for label in labels:
        label_args.extend(['--label', label])
    
    # 创建Issue
    cmd = [
        'issue', 'create',
        '--title', title,
        '--body', body,
        '--milestone', str(milestone_num)
    ] + label_args
    
    output = run_gh_command(cmd)
    
    # 提取URL (通常在输出的最后一行)
    lines = output.strip().split('\n')
    url = lines[-1] if lines else None
    
    return url


def main():
    """主函数：创建所有12个Issue"""
    
    print("🚀 开始创建优化计划Issue...")
    print("=" * 80)
    
    # 检查gh是否已安装和认证
    try:
        run_gh_command(['auth', 'status'])
        print("✅ GitHub CLI已认证")
    except:
        print("❌ GitHub CLI未认证，请先运行: gh auth login")
        sys.exit(1)
    
    # 定义12个Issue
    issues = [
        # Phase 1 - M1
        {
            'title': '[P0] Performance: Optimize interference() calculation engine with pruning and parallelization',
            'labels': ['P0', 'performance', 'enhancement'],
            'milestone': 'Phase 1: Core Performance Optimization',
            'body': '''## Background
The current `interference()` function in main.py uses brute-force combination enumeration, which causes exponential explosion when maxsize ≥ 4. For 10 elements with ~50 isotopes, maxsize=5 generates ~300 million combinations.

## Objective
Implement performance optimizations to achieve 10-100x speedup while maintaining API compatibility.

## Implementation Plan

### 1. Pre-filtering Pruning
- Add mass range validation before generating combinations
- Skip combinations that cannot fall within target m/z ± tolerance
- Implement early termination for low-probability branches

### 2. Parallel Computing
- Use multiprocessing.Pool for independent combination batches
- Add configurable worker count (default: CPU cores)
- Ensure thread-safe result aggregation

### 3. Optional GPU Acceleration
- Create CuPy-based backend interface
- Fallback to CPU if GPU unavailable
- Benchmark comparison report

## Acceptance Criteria
- [ ] Speed improvement: 10-100x faster for maxsize=4-5 scenarios
- [ ] Memory usage: No significant increase (< 20%)
- [ ] API compatibility: All existing tests pass without modification
- [ ] Backward compatibility: Default behavior unchanged
- [ ] Documentation: Update docstring with performance notes

## Estimated Effort
- Development: 2 weeks
- Testing: 3 days
- Documentation: 2 days

## Related Files
- interference_calculator/main.py (interference function)
- tests/test_core.py (add performance benchmarks)

## References
- Optimization Roadmap: docs/OPTIMIZATION_ROADMAP.md
'''
        },
        {
            'title': '[P0] Memory: Reduce memory footprint with generator patterns and streaming processing',
            'labels': ['P0', 'performance', 'enhancement'],
            'milestone': 'Phase 1: Core Performance Optimization',
            'body': '''## Background
Current implementation stores all isotope combinations in memory before filtering, causing GB-level memory usage for maxsize=5 with 50 elements.

## Objective
Reduce peak memory usage by 50-70% using generator patterns and streaming processing.

## Implementation Plan

### 1. Generator Pattern
- Replace list comprehensions with generators in combination generation
- Implement lazy evaluation for mass calculations
- Stream results instead of building complete DataFrame at once

### 2. Streaming DataFrame Construction
- Process results in chunks (e.g., 10,000 rows per chunk)
- Use pd.concat() only at the end
- Avoid intermediate list storage

### 3. Data Type Optimization
- Use float32 instead of float64 where precision allows
- Use int8 for charge states
- Optimize categorical columns

## Acceptance Criteria
- [ ] Peak memory reduced by ≥50% (verified with memory_profiler)
- [ ] Calculation results identical to original (numerical error <1e-6)
- [ ] No MemoryError for maxsize=5, 50 elements scenario
- [ ] Performance impact <10% slowdown (acceptable trade-off)

## Estimated Effort
- Development: 1 week
- Testing: 2 days

## Related Files
- interference_calculator/main.py
- interference_calculator/inorganic.py

## References
- docs/OPTIMIZATION_ROADMAP.md Section 1.2
'''
        },
        
        # Phase 2 - M2
        {
            'title': '[P1] Architecture: Modularize ui.py into separate components (MVVM pattern)',
            'labels': ['P1', 'refactoring', 'enhancement'],
            'milestone': 'Phase 2: Architecture Refactoring',
            'body': '''## Background
ui.py is nearly 5000 lines, making it difficult to maintain and extend. The monolithic structure mixes UI layout, business logic, and event handling.

## Objective
Refactor ui.py into modular components following MVVM pattern, reducing single file size to <1000 lines.

## Implementation Plan

### 1. Component Separation
- Extract ControlPanel widget (left panel, ~460px width)
- Extract ResultsView widget (right panel with table and spectrum)
- Extract SpectrumWidget (pure Qt drawing component)
- Create shared mixins for common functionality

### 2. MVVM Pattern
- Create ViewModel classes to manage state
- Separate data models from UI rendering
- Implement clear data flow: View → ViewModel → Model

### 3. Backward Compatibility
- Maintain existing API and behavior
- Provide deprecation warnings for old interfaces
- Ensure all tests pass without modification

## Acceptance Criteria
- [ ] ui.py split into 5+ modules, each <1000 lines
- [ ] All existing functionality preserved
- [ ] All tests pass (100% regression test coverage)
- [ ] Code review approval from 2+ maintainers
- [ ] Documentation updated with new architecture

## Estimated Effort
- Development: 3-4 weeks
- Testing: 1 week
- Documentation: 3 days

## Related Files
- interference_calculator/ui.py (main refactoring target)
- tests/test_ui_entrypoint.py (ensure no regressions)

## Risks
- High risk of regression bugs
- Requires extensive testing
- May break third-party integrations relying on internal APIs

## Mitigation
- Comprehensive test suite before refactoring
- Gradual migration with feature flags
- Clear deprecation timeline (6 months)
'''
        },
        {
            'title': '[P1] Feature: Add configuration persistence system with JSON backend',
            'labels': ['P1', 'enhancement'],
            'milestone': 'Phase 2: Architecture Refactoring',
            'body': '''## Background
Currently, user preferences (language, instrument presets, element selections) are lost when the application closes. Users must reconfigure settings on each launch.

## Objective
Implement a configuration persistence system that saves and restores user preferences across sessions.

## Implementation Plan

### 1. Configuration Storage
- Use JSON format for human-readable config files
- Store in platform-appropriate location:
  - Linux/macOS: ~/.config/interference_calculator/config.json
  - Windows: %APPDATA%/InterferenceCalculator/config.json
- Support multiple profiles (e.g., "GDMS_Default", "ICP_MS_Trace")

### 2. Configurable Settings
- Language preference (en/zh)
- Last used instrument mode (GDMS/ICP-MS/SIMS)
- Recently selected elements
- Custom MRP values
- Window position and size
- Spectrum display preferences

### 3. Import/Export Presets
- Export current settings to JSON file
- Import settings from file
- Share presets with colleagues
- Version control friendly

### 4. Recent Items Cache
- Track last 10 target m/z values
- Track last 5 element combinations
- Quick access from dropdown menu

## Acceptance Criteria
- [ ] Settings automatically saved on application close
- [ ] Settings restored on application launch
- [ ] Manual save/load buttons in UI
- [ ] Export/import preset functionality
- [ ] Config file schema documented
- [ ] Migration support for future config changes

## Estimated Effort
- Development: 1 week
- Testing: 2 days
- Documentation: 1 day

## Related Files
- interference_calculator/ui.py (add config load/save)
- New file: interference_calculator/config.py

## Example Config Structure
```json
{
  "version": "1.0",
  "language": "zh",
  "instrument_mode": "GDMS",
  "elements": ["Fe", "Ni", "Cr"],
  "charges": ["1+", "2+"],
  "mrp_presets": {
    "GDMS": 5000,
    "ICP-MS": 10000
  },
  "window_geometry": {...},
  "recent_targets": [75.0, 56.0, 63.0]
}
```
'''
        },
        {
            'title': '[P1] Architecture: Implement plugin system for extensibility (species templates, formation factors)',
            'labels': ['P1', 'refactoring', 'enhancement'],
            'milestone': 'Phase 2: Architecture Refactoring',
            'body': '''## Background
Currently, species templates and formation factors are hardcoded in inorganic.py. Adding new instrument types or custom species requires modifying source code.

## Objective
Implement a plugin system that allows users to define custom species templates, formation factors, and instrument presets via external YAML configuration files.

## Implementation Plan

### 1. Plugin Interface Definition
- Define abstract base classes for plugins:
  - SpeciesTemplatePlugin
  - FormationFactorPlugin
  - InstrumentPresetPlugin
- Specify required methods and data structures

### 2. YAML Configuration Format
```yaml
# plugins/custom_species.yaml
species_templates:
  - name: "custom_oxide"
    pattern: "{element}O"
    charge: 1
    formation_factor_gdms: 1.0e-3
    formation_factor_icpms: 1.0e-2
    
instrument_presets:
  - name: "TOF-SIMS"
    default_charges: ["1+"]
    max_combination_size: 3
    plasma_elements: ["Cs", "O"]
    formation_factors:
      oxide: 1.0e-2
      hydride: 1.0e-3
```

### 3. Plugin Discovery and Loading
- Scan plugins/ directory for YAML files
- Hot-reload on file changes (optional)
- Validate plugin schema before loading
- Error handling for invalid plugins

### 4. User Interface Integration
- "Load Plugin" button in UI
- Display active plugins list
- Enable/disable individual plugins
- Show plugin documentation/tooltips

## Acceptance Criteria
- [ ] Plugin interface defined with ABC
- [ ] YAML schema documented and validated
- [ ] At least 2 example plugins provided
- [ ] Plugins can be loaded/unloaded at runtime
- [ ] Invalid plugins rejected with clear error messages
- [ ] Documentation for writing custom plugins

## Estimated Effort
- Development: 2-3 weeks
- Testing: 1 week
- Documentation: 3 days

## Related Files
- interference_calculator/inorganic.py (extract hardcoded values)
- New directory: plugins/
- New file: interference_calculator/plugin_manager.py

## Benefits
- Users can add custom instrument types without code changes
- Easier to share community-contributed presets
- Reduced maintenance burden for core developers
- Better separation of data and logic
'''
        },
        
        # Phase 3 - M3
        {
            'title': '[P1] Testing: Increase test coverage with screenshot comparison and performance benchmarks',
            'labels': ['P1', 'testing', 'enhancement'],
            'milestone': 'Phase 3: Quality Assurance Enhancement',
            'body': '''## Background
Current test coverage is good for core logic (>90%) but UI testing relies on offscreen rendering which may miss real-world issues. Performance regression testing is also missing.

## Objective
Increase test coverage to 95%+ for core logic and 80%+ for UI, with automated screenshot comparison and performance benchmarks.

## Implementation Plan

### 1. Screenshot Comparison Tests
- Use pytest-qt for real Qt widget rendering
- Implement image diff algorithm (perceptual hash or pixel comparison)
- Store baseline screenshots in tests/baselines/
- Detect visual regressions automatically

```python
def test_spectrum_rendering(qtbot):
    spectrum = Spectrum()
    spectrum.plot_spectrum(test_data)
    assert_image_matches(spectrum, "baseline_spectrum.png", tolerance=0.01)
```

### 2. Performance Benchmarks
- Create benchmark suite for critical paths:
  - interference() calculation time
  - inorganic_interference() calculation time
  - GDMS file parsing speed
  - UI startup time
- Track metrics over time
- Alert on >10% regression

```python
def test_interference_performance(benchmark):
    result = benchmark(interference, 75.0, atoms, maxsize=4)
    assert result.shape[0] > 0
    assert benchmark.stats.mean < 1.0  # < 1 second
```

### 3. Edge Case Coverage
- Test with extreme inputs:
  - 100+ elements
  - maxsize=6-8
  - Very small/large m/z values
  - Malformed GDMS files
  - Unicode in molecule formulas
- Ensure graceful error handling

### 4. Integration Tests
- Test complete user workflows:
  - Load GDMS file → Calculate interference → Export results
  - Change language → Verify all labels updated
  - Select peak in spectrum → Table row highlighted
- Simulate user interactions with pytest-qt

## Acceptance Criteria
- [ ] Core logic coverage: ≥95%
- [ ] UI coverage: ≥80%
- [ ] 10+ screenshot comparison tests
- [ ] 5+ performance benchmark tests
- [ ] 20+ edge case tests
- [ ] 5+ integration tests covering full workflows
- [ ] CI runs all tests on every PR
- [ ] Performance dashboard showing trends

## Estimated Effort
- Development: 2 weeks
- Test writing: 1 week
- CI integration: 2 days

## Related Files
- tests/test_core.py (add benchmarks)
- tests/test_ui_entrypoint.py (add screenshot tests)
- New directory: tests/baselines/
- New file: tests/test_performance.py

## Tools
- pytest-qt: Qt widget testing
- pytest-benchmark: Performance measurement
- Pillow: Image comparison
- memory_profiler: Memory usage tracking
'''
        },
        {
            'title': '[P1] DevOps: Add logging and monitoring system with error tracking',
            'labels': ['P1', 'devops', 'enhancement'],
            'milestone': 'Phase 3: Quality Assurance Enhancement',
            'body': '''## Background
Currently, debugging is difficult due to lack of structured logging. When errors occur, there is no systematic way to collect diagnostic information or track performance metrics.

## Objective
Implement a comprehensive logging and monitoring system to improve debugging efficiency and enable proactive issue detection.

## Implementation Plan

### 1. Logging Infrastructure
- Use Python standard logging module
- Configure log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Support multiple handlers:
  - Console handler (colored output)
  - File handler (rotating logs, max 10MB)
  - Optional remote handler (Sentry for error tracking)

```python
import logging

logger = logging.getLogger(__name__)

def calculate_interference(...):
    logger.debug(f"Starting calculation for m/z={target_mz}, atoms={atoms}")
    try:
        result = _do_calculation(...)
        logger.info(f"Calculation completed: {len(result)} interferences found")
        return result
    except Exception as e:
        logger.error(f"Calculation failed: {e}", exc_info=True)
        raise
```

### 2. Performance Metrics Collection
- Track key metrics:
  - Calculation time per request
  - Memory usage during calculation
  - GDMS file parsing time
  - UI response time
- Store metrics in structured format (JSON lines)
- Optional: Send to monitoring service (Prometheus, Datadog)

### 3. Error Tracking and Reporting
- Capture unhandled exceptions
- Collect context: OS, Python version, package versions
- Generate crash reports with stack traces
- Optional: Auto-submit to Sentry/GitHub Issues
- User consent required before sending

### 4. Log Rotation and Management
- Rotate logs daily or when size exceeds 10MB
- Keep last 30 days of logs
- Compress old logs (gzip)
- Provide "Export Logs" button in UI for bug reports

### 5. User-Facing Diagnostics
- "About" dialog shows system info
- "Export Diagnostic Report" button
- Include: logs, config, system specs
- One-click copy to clipboard for support tickets

## Acceptance Criteria
- [ ] Logging configured for all major modules
- [ ] Log files rotated and compressed automatically
- [ ] Performance metrics collected for critical paths
- [ ] Crash reports generated with full context
- [ ] UI provides easy log export for bug reports
- [ ] Documentation for interpreting logs
- [ ] Optional Sentry integration for production builds

## Estimated Effort
- Development: 1 week
- Testing: 2 days
- Documentation: 1 day

## Related Files
- interference_calculator/main.py (add logging)
- interference_calculator/inorganic.py (add logging)
- interference_calculator/ui.py (add diagnostics UI)
- New file: interference_calculator/logging_config.py
- New file: interference_calculator/diagnostics.py

## Configuration Example
```python
# logging_config.py
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '~/.cache/interference_calculator/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'standard',
            'level': 'DEBUG'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG'
    }
}
```
'''
        },
        
        # Phase 4 - M4
        {
            'title': '[P2] Docs: Generate API documentation with Sphinx and type annotations',
            'labels': ['P2', 'documentation', 'enhancement'],
            'milestone': 'Phase 4: Documentation & UX',
            'body': '''## Background
The project lacks comprehensive API documentation. While docstrings exist, they are not easily discoverable or browsable. Type annotations are also incomplete.

## Objective
Generate professional API documentation using Sphinx and add comprehensive type annotations throughout the codebase.

## Implementation Plan

### 1. Type Annotations
- Add type hints to all public functions and methods
- Use typing module for complex types (List, Dict, Optional, Union)
- Add type stubs (.pyi files) for C extensions if needed
- Run mypy for static type checking

```python
from typing import List, Optional, Union
import pandas as pd

def interference(
    target_mz: float,
    atoms: List[str],
    chargesign: str = '+',
    ch: int = 1,
    maxsize: int = 3,
    tolerance_ppm: float = 10.0,
    use_pruning: bool = True
) -> pd.DataFrame:
    """Calculate isotopic interferences."""
    ...
```

### 2. Sphinx Documentation Setup
- Install Sphinx and extensions:
  - sphinx-autodoc
  - sphinx-napoleon (Google/NumPy style docstrings)
  - sphinx-rtd-theme (ReadTheDocs theme)
- Configure autodoc to extract docstrings
- Generate API reference automatically

### 3. Docstring Standards
- Adopt Google-style or NumPy-style docstrings
- Document all parameters, return values, exceptions
- Include examples in docstrings
- Add cross-references between related functions

```python
def inorganic_interference(atoms: List[str], target_formula: str) -> pd.DataFrame:
    """Calculate inorganic interferences using template matching.
    
    This function uses pre-defined species templates (atomic ions, oxides,
    hydrides, etc.) to efficiently identify potential interferences without
    exhaustive combination enumeration.
    
    Parameters
    ----------
    atoms : List[str]
        List of element symbols present in the sample.
    target_formula : str
        Target peak formula (e.g., "75As", "56Fe").
    
    Returns
    -------
    pd.DataFrame
        DataFrame with columns: molecule, m/z, probability, type, relative_risk
    
    Examples
    --------
    >>> df = inorganic_interference(['Ar', 'Cl', 'As'], '75As')
    >>> print(df.head())
    
    See Also
    --------
    interference : General-purpose interference calculation
    
    References
    ----------
    .. [1] CIAAW 2024 Isotopic Abundances
    .. [2] AME2020 Atomic Mass Evaluation
    """
```

### 4. Documentation Hosting
- Host on ReadTheDocs (free for open source)
- Or GitHub Pages with sphinx-book-theme
- Auto-build on every release
- Version-specific documentation (v2.5.0, v2.6.0, etc.)

### 5. Tutorial Notebooks
- Create Jupyter notebooks demonstrating:
  - Basic interference calculation
  - GDMS data import and analysis
  - Custom species templates
  - Performance optimization tips
- Render notebooks in documentation

## Acceptance Criteria
- [ ] 100% of public API has type annotations
- [ ] mypy passes with zero errors
- [ ] Sphinx documentation builds without warnings
- [ ] All functions have comprehensive docstrings
- [ ] Documentation hosted online (RTD or GitHub Pages)
- [ ] 3+ tutorial notebooks provided
- [ ] Search functionality in documentation
- [ ] Cross-references between related topics

## Estimated Effort
- Type annotations: 1 week
- Docstring improvements: 1 week
- Sphinx setup and deployment: 2 days
- Tutorial notebooks: 2 days

## Related Files
- All .py files in interference_calculator/ (add type hints)
- New directory: docs/api/ (Sphinx source)
- New file: docs/conf.py (Sphinx configuration)
- New directory: docs/tutorials/ (Jupyter notebooks)

## Tools
- Sphinx: Documentation generator
- mypy: Static type checker
- sphinx-autodoc: Auto-generate API docs
- Jupyter: Interactive tutorials
- ReadTheDocs: Documentation hosting
'''
        },
        {
            'title': '[P2] Docs: Enhance user manual with tutorials, videos, and FAQ',
            'labels': ['P2', 'documentation', 'enhancement'],
            'milestone': 'Phase 4: Documentation & UX',
            'body': '''## Background
The current USER_MANUAL.md is relatively brief and lacks practical examples, video tutorials, and troubleshooting guidance. New users may struggle to get started.

## Objective
Create comprehensive user documentation with step-by-step tutorials, video guides, and FAQ to reduce onboarding time to <10 minutes.

## Implementation Plan

### 1. Video Tutorials
- Record 5-7 short videos (2-5 minutes each):
  1. Installation and first launch
  2. Basic interference calculation (GDMS mode)
  3. Importing GDMS profile data (TRR/GDR/Excel)
  4. Interpreting results and spectrum view
  5. Advanced features (custom charges, multi-charge)
  6. Exporting results (CSV/Excel)
  7. Troubleshooting common issues
- Host on YouTube or Bilibili (for Chinese users)
- Embed videos in documentation
- Provide transcripts for accessibility

### 2. Interactive Tutorials
- Create guided walkthrough in the application:
  - "First Time Setup" wizard
  - Tooltips explaining each UI element
  - Context-sensitive help (F1 key)
- Use QWhatsThis or custom overlay system

### 3. Expanded User Manual
- Restructure USER_MANUAL.md into chapters:
  - Chapter 1: Getting Started (installation, system requirements)
  - Chapter 2: Quick Start (5-minute tutorial)
  - Chapter 3: User Interface Overview
  - Chapter 4: Calculation Modes (GDMS/ICP-MS/SIMS)
  - Chapter 5: Data Import (GDMS profiles)
  - Chapter 6: Interpreting Results
  - Chapter 7: Advanced Features
  - Chapter 8: Export and Reporting
  - Chapter 9: Troubleshooting
  - Chapter 10: FAQ
- Add screenshots for every major feature
- Include annotated diagrams explaining concepts

### 4. FAQ Section
- Compile common questions from GitHub Issues:
  - "Why is calculation slow for large maxsize?"
  - "How do I interpret Δppm values?"
  - "What does 'resolved' mean?"
  - "How accurate are the formation factors?"
  - "Can I add custom elements?"
  - "How do I cite this software?"
- Provide clear, concise answers with examples
- Link to relevant documentation sections

### 5. Cheat Sheet
- Create one-page quick reference:
  - Keyboard shortcuts
  - Common molecule formula syntax
  - Typical formation factors by instrument
  - Troubleshooting flowchart
- Printable PDF format
- Available in both English and Chinese

## Acceptance Criteria
- [ ] 5+ video tutorials recorded and published
- [ ] User manual expanded to 10+ chapters with screenshots
- [ ] FAQ section with 20+ common questions
- [ ] Interactive tutorial/wizard in application
- [ ] Printable cheat sheet (EN/ZH)
- [ ] Average onboarding time <10 minutes (user testing)
- [ ] Documentation translated to Chinese
- [ ] All videos have subtitles/captions

## Estimated Effort
- Video recording/editing: 1 week
- Manual expansion: 1 week
- FAQ compilation: 2 days
- Interactive tutorial: 3 days
- Translation: 2 days

## Related Files
- docs/USER_MANUAL.md (expand significantly)
- New directory: docs/videos/ (video metadata and transcripts)
- New file: docs/FAQ.md
- New file: docs/cheat_sheet_en.pdf
- New file: docs/cheat_sheet_zh.pdf

## Video Hosting Options
- **YouTube**: Global reach, auto-captions
- **Bilibili**: Better for Chinese audience
- **Both**: Maximize accessibility
- **Self-hosted**: Full control, higher cost

## Metrics for Success
- Track documentation page views (Google Analytics)
- Monitor video completion rates
- Survey new users on onboarding experience
- Count support requests (should decrease)
'''
        },
        {
            'title': '[P2] i18n: Extend internationalization support (Japanese, German)',
            'labels': ['P2', 'i18n', 'enhancement'],
            'milestone': 'Phase 4: Documentation & UX',
            'body': '''## Background
Currently, the application supports English and Chinese. However, the i18n implementation has some hard-coded strings and doesn\'t support dynamic language switching without restart.

## Objective
Complete the internationalization infrastructure to support additional languages (Japanese, German) and enable runtime language switching.

## Implementation Plan

### 1. Extract Hard-coded Strings
- Audit all source files for hard-coded user-facing strings
- Move all strings to i18n resource files
- Use consistent key naming convention

```python
# Before
self.label.setText("Target m/z:")

# After
self.label.setText(self.tr("target_mz_label"))
```

### 2. Translation Resource Files
- Use JSON or YAML format for translations
- Organize by module/component

```json
// translations/en.json
{
  "main_window": {
    "title": "Inorganic Mass Spectrometry Interference Calculator",
    "target_mz_label": "Target m/z:",
    "calculate_button": "Calculate",
    "export_button": "Export Results"
  },
  "spectrum": {
    "x_label_mz": "m/z",
    "x_label_ppm": "Δppm from target",
    "intensity_label": "Normalized Intensity"
  }
}

// translations/ja.json
{
  "main_window": {
    "title": "無機質量分析干渉計算機",
    "target_mz_label": "目標 m/z:",
    "calculate_button": "計算",
    "export_button": "結果をエクスポート"
  }
}
```

### 3. Runtime Language Switching
- Implement language change without application restart
- Update all UI elements dynamically
- Save language preference to config
- Provide language selector in UI (dropdown menu)

```python
def change_language(self, language_code: str):
    """Change application language at runtime."""
    self.current_language = language_code
    self.translations = load_translations(language_code)
    self._refresh_all_ui_texts()
    self.config.save('language', language_code)
```

### 4. Translation Workflow
- Provide translation template for contributors
- Use Crowdin or Transifex for collaborative translation (optional)
- Validate translations for completeness
- Allow community contributions via GitHub

### 5. Right-to-Left (RTL) Support Preparation
- Although Japanese and German are LTR, prepare infrastructure for future RTL languages (Arabic, Hebrew)
- Use Qt layout managers that support RTL
- Test mirror layouts

## Acceptance Criteria
- [ ] Zero hard-coded user-facing strings in code
- [ ] Japanese translation complete (≥95% coverage)
- [ ] German translation complete (≥95% coverage)
- [ ] Language can be switched at runtime without restart
- [ ] All UI elements update correctly after language change
- [ ] Translation template provided for future languages
- [ ] Documentation for translators
- [ ] Community contribution guide for translations

## Estimated Effort
- String extraction: 2 days
- Japanese translation: 3 days
- German translation: 3 days
- Runtime switching implementation: 2 days
- Testing and validation: 2 days

## Related Files
- interference_calculator/ui.py (replace hard-coded strings)
- New directory: translations/
- New files: translations/en.json, zh.json, ja.json, de.json
- New file: interference_calculator/i18n.py (translation manager)

## Languages Priority
1. ✅ English (existing)
2. ✅ Chinese (existing, needs completion)
3. 🇯🇵 Japanese (new - high priority for Asian market)
4. 🇩🇪 German (new - strong MS community in Europe)
5. 🇫🇷 French (future)
6. 🇪🇸 Spanish (future)

## Translation Quality
- Native speaker review required
- Technical terminology consistency
- Cultural appropriateness check
- UI layout testing (some languages are longer than English)
'''
        },
        
        # Phase 5 - M5
        {
            'title': '[P2] Build: Modernize dependency management with Poetry',
            'labels': ['P2', 'devops', 'enhancement'],
            'milestone': 'Phase 5: Modernization',
            'body': '''## Background
Currently, the project uses setup.py with hard-coded dependencies. This makes it difficult to manage development vs. production dependencies, lock versions, and ensure reproducible builds.

## Objective
Migrate from setup.py to Poetry for modern dependency management, enabling better version control and reproducible environments.

## Implementation Plan

### 1. Poetry Setup
- Install Poetry: `pip install poetry` or `curl -sSL https://install.python-poetry.org | python3 -`
- Initialize project: `poetry init`
- Migrate dependencies from setup.py to pyproject.toml

```toml
# pyproject.toml
[tool.poetry]
name = "interference-calculator"
version = "2.6.0"
description = "Inorganic mass spectrometry interference calculator"
authors = ["Tingfe <your.email@example.com>"]
license = "MIT"
readme = "README.rst"

[tool.poetry.dependencies]
python = "^3.9"
numpy = "^1.21.0"
pandas = "^1.3.0"
openpyxl = "^3.0.0"
pyparsing = "^3.0.0"
PyQt5 = "^5.15.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-qt = "^4.0.0"
pytest-benchmark = "^4.0.0"
mypy = "^0.900"
flake8 = "^5.0.0"
black = "^22.0.0"
sphinx = "^5.0.0"

[tool.poetry.scripts]
interference_calculator = "interference_calculator.ui:run"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 2. Dependency Locking
- Generate poetry.lock file for reproducible builds
- Commit lock file to version control
- CI uses locked versions for consistency

### 3. Virtual Environment Management
- Poetry manages virtual environments automatically
- Developers use: `poetry install` to set up environment
- No need for manual venv creation

### 4. Backward Compatibility
- Keep setup.py for legacy pip install support
- Generate setup.py from pyproject.toml using poetry build
- Document both installation methods

```bash
# New recommended method
poetry install

# Legacy method (still works)
pip install interference-calculator
```

### 5. PyQt6 Compatibility Layer
- Add optional PyQt6 support alongside PyQt5
- Use abstraction layer to support both backends
- Allow users to choose via environment variable

```python
# interference_calculator/qt_compat.py
import os

if os.environ.get('IC_USE_PYQT6'):
    from PyQt6 import QtCore, QtGui, QtWidgets
else:
    from PyQt5 import QtCore, QtGui, QtWidgets
```

## Acceptance Criteria
- [ ] pyproject.toml fully configured with all dependencies
- [ ] poetry.lock file generated and committed
- [ ] `poetry install` sets up working development environment
- [ ] `poetry build` creates distributable packages
- [ ] setup.py still works for backward compatibility
- [ ] CI/CD updated to use Poetry
- [ ] Documentation updated with Poetry instructions
- [ ] Optional PyQt6 support implemented

## Estimated Effort
- Migration: 3 days
- Testing: 2 days
- Documentation: 1 day

## Related Files
- pyproject.toml (enhance with Poetry config)
- setup.py (keep for compatibility, auto-generated)
- New file: interference_calculator/qt_compat.py
- .github/workflows/*.yml (update CI to use Poetry)

## Migration Steps
1. Install Poetry
2. Run `poetry init` and follow prompts
3. Add dependencies: `poetry add numpy pandas openpyxl pyparsing PyQt5`
4. Add dev dependencies: `poetry add --group dev pytest pytest-qt mypy black`
5. Test: `poetry run python -m unittest discover -s tests -v`
6. Build: `poetry build`
7. Commit pyproject.toml and poetry.lock
8. Update CI/CD workflows
9. Update documentation

## Benefits
- Reproducible builds with locked dependencies
- Clear separation of dev/prod dependencies
- Automatic virtual environment management
- Better dependency resolution
- Modern Python packaging standards
- Easier contribution setup for developers
'''
        },
        {
            'title': '[P2] CI/CD: Optimize continuous integration pipeline with automated quality checks',
            'labels': ['P2', 'devops', 'enhancement'],
            'milestone': 'Phase 5: Modernization',
            'body': '''## Background
The current CI/CD pipeline focuses on testing and releasing. It lacks automated code quality checks, security scanning, and performance regression detection.

## Objective
Enhance CI/CD pipeline with comprehensive quality gates, automated security scanning, and performance monitoring.

## Implementation Plan

### 1. Code Quality Checks
- Add flake8 for style checking
- Add mypy for type checking
- Add black for code formatting enforcement
- Fail build on quality violations

```yaml
# .github/workflows/quality.yml
name: Code Quality
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install flake8 mypy black
      - run: flake8 interference_calculator/
      - run: mypy interference_calculator/
      - run: black --check interference_calculator/
```

### 2. Multi-Python Version Testing
- Test on Python 3.9, 3.10, 3.11, 3.12
- Ensure compatibility across versions
- Use matrix strategy in GitHub Actions

```yaml
test:
  strategy:
    matrix:
      python-version: ['3.9', '3.10', '3.11', '3.12']
      os: [ubuntu-latest, windows-latest, macos-latest]
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install ".[export]"
    - run: python -m unittest discover -s tests -v
```

### 3. Security Scanning
- Add Dependabot for dependency updates
- Add Bandit for Python security linting
- Scan for known vulnerabilities in dependencies
- Auto-create PRs for security updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

### 4. Performance Regression Detection
- Run performance benchmarks on every PR
- Compare against baseline
- Fail if performance degrades >10%
- Store historical performance data

```yaml
benchmark:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - run: pip install pytest pytest-benchmark
    - run: pytest tests/test_performance.py --benchmark-json=benchmark.json
    - uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'pytest'
        output-file-path: benchmark.json
        fail-on-regression: true
        regression-threshold: 10
```

### 5. Automated Release Validation
- After release, verify:
  - PyPI package installs correctly
  - Windows ZIP extracts and runs
  - macOS DMG installs and launches
  - All tests pass on installed package
- Smoke test script for each platform

### 6. Coverage Reporting
- Generate coverage report on every PR
- Upload to Coveralls or Codecov
- Display coverage badge in README
- Fail if coverage drops below threshold

```yaml
coverage:
  runs-on: ubuntu-latest
  steps:
    - run: pip install coverage
    - run: coverage run -m unittest discover -s tests
    - run: coverage xml
    - uses: codecov/codecov-action@v3
      with:
        fail_ci_if_error: true
        verbose: true
```

### 7. Artifact Storage
- Store build artifacts for inspection:
  - Wheel packages
  - Test logs
  - Benchmark results
  - Coverage reports
- Retain for 90 days

## Acceptance Criteria
- [ ] Code quality checks run on every PR
- [ ] Tests run on Python 3.9-3.12 across 3 OS
- [ ] Dependabot configured for automatic updates
- [ ] Performance benchmarks tracked over time
- [ ] Coverage report uploaded to Codecov/Coveralls
- [ ] Release validation smoke tests pass
- [ ] Build artifacts stored and accessible
- [ ] CI completes in <15 minutes total

## Estimated Effort
- Workflow configuration: 3 days
- Testing and tuning: 2 days
- Documentation: 1 day

## Related Files
- .github/workflows/quality.yml (new)
- .github/workflows/test.yml (enhance with matrix)
- .github/workflows/benchmark.yml (new)
- .github/dependabot.yml (new)
- setup.cfg or pyproject.toml (add linter configs)

## Example Linter Configurations

### .flake8
```ini
[flake8]
max-line-length = 100
exclude = .venv,build,dist
ignore = E203,W503
```

### mypy.ini
```ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False  # Gradual typing
```

### pyproject.toml (black)
```toml
[tool.black]
line-length = 100
target-version = ['py39']
include = '\.pyi?$'
```

## CI/CD Metrics to Track
- Build success rate (target: >95%)
- Average build time (target: <15 min)
- Test coverage trend (target: increasing)
- Performance trend (target: stable or improving)
- Dependency update latency (target: <7 days)
'''
        },
    ]
    
    created_issues = []
    failed_issues = []
    
    for i, issue_data in enumerate(issues, 1):
        print(f"\n[{i}/{len(issues)}] 创建Issue: {issue_data['title'][:60]}...")
        
        try:
            url = create_issue(
                title=issue_data['title'],
                body=issue_data['body'],
                labels=issue_data['labels'],
                milestone_title=issue_data['milestone']
            )
            
            if url:
                print(f"✅ 成功: {url}")
                created_issues.append((issue_data['title'], url))
            else:
                print(f"⚠️  跳过")
                failed_issues.append(issue_data['title'])
                
        except Exception as e:
            print(f"❌ 失败: {e}")
            failed_issues.append(issue_data['title'])
    
    # 打印总结
    print("\n" + "=" * 80)
    print("📊 创建完成总结")
    print("=" * 80)
    print(f"✅ 成功创建: {len(created_issues)} 个Issue")
    print(f"❌ 失败/跳过: {len(failed_issues)} 个Issue")
    
    if created_issues:
        print("\n已创建的Issue列表:")
        for title, url in created_issues:
            print(f"  - {url}")
    
    if failed_issues:
        print("\n失败的Issue (请手动创建):")
        for title in failed_issues:
            print(f"  - {title}")
    
    print("\n💡 提示: 现在可以访问Project Board并将这些Issue添加进去")
    print("=" * 80)


if __name__ == '__main__':
    main()
