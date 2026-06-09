# API Documentation

This directory contains the Sphinx-based API documentation for Interference Calculator.

## Building the Documentation

### Prerequisites

Install the required packages:

```bash
pip install -r requirements.txt
```

### Build HTML Documentation

```bash
cd docs/api
make html
```

The generated HTML files will be in `docs/api/_build/html/`.

### View Documentation

Open `docs/api/_build/html/index.html` in your web browser.

## Documentation Style Guide

This project uses **Google-style docstrings** with Napoleon extension.

### Example

```python
def calculate_interference(atoms: dict, target: str) -> list:
    """Calculate interference for given atoms and target.
    
    Args:
        atoms: Dictionary mapping element symbols to quantities.
        target: Target element or mass to analyze.
    
    Returns:
        List of interference results sorted by relevance.
    
    Raises:
        ValueError: If atoms dictionary is empty.
    
    Example:
        >>> calculate_interference({'Fe': 1}, 'Fe')
        [{'mass': 55.9349, 'abundance': 0.917}]
    """
    pass
```

### Type Hints

All public API functions should include type hints:

```python
from typing import Dict, List, Optional

def process_data(data: Dict[str, float], 
                 threshold: Optional[float] = None) -> List[float]:
    """Process data with optional threshold.
    
    Args:
        data: Input data dictionary.
        threshold: Optional filtering threshold.
    
    Returns:
        Processed values as list.
    """
    pass
```

## Automated Documentation Generation

The documentation is automatically generated from:
- Module docstrings
- Function/class docstrings  
- Type annotations
- Inline comments (for complex logic)

Run `make html` to regenerate after code changes.
