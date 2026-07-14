# -*- coding: utf-8 -*-
"""Compatibility helpers for package resource lookup."""

try:
    from importlib import resources as _resources
    _resources.files
except (AttributeError, ImportError):
    import importlib_resources as _resources


def resource_file(package, name):
    """Return a traversable package resource for stdlib and legacy runtimes."""
    return _resources.files(package).joinpath(name)


def resource_path(package, name):
    """Return a filesystem path string for bundled PyInstaller resources."""
    return str(resource_file(package, name))
