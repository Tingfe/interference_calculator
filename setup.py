#!/usr/bin/env python
""" Setuptools setup file for interference calculator. """
from setuptools import setup, find_packages
import ast
import os

metadata_path = os.path.join('interference_calculator', '__init__.py')
with open(metadata_path, mode='rt', encoding='utf-8') as fh:
    metadata_source = fh.read()

metadata_tree = ast.parse(metadata_source, filename=metadata_path)
metadata = {'__doc__': ast.get_docstring(metadata_tree)}
for node in metadata_tree.body:
    if not isinstance(node, ast.Assign):
        continue
    try:
        value = ast.literal_eval(node.value)
    except (SyntaxError, ValueError):
        if isinstance(node.value, ast.Name) and node.value.id == '__doc__':
            value = metadata['__doc__']
        else:
            continue
    for target in node.targets:
        if isinstance(target, ast.Name) and target.id.startswith('__'):
            metadata[target.id] = value

globals().update(metadata)

with open('README.rst', mode='rt', encoding='utf-8') as fh:
    __long_description__ = fh.read()

try:
    import PyQt5
    pyqtdep = 'PyQt5'
except ImportError:
    try:
        import PyQt4
        pyqtdep = 'PyQt4'
    except ImportError:
        pyqtdep = 'PyQt5'

setup(
    name = __name__,
    version = __version__,
    description = __description__,
    long_description = __long_description__,
    url = __url__,
    author = __author__,
    author_email = 'me@example.com',
    maintainer = __maintainer__,
    license = __license__,
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering'
    ],
    keywords = 'interference mass-spectrometry isotope element standard ratio',
    python_requires = '>=3.9',

    install_requires = [
        'numpy',
        'openpyxl',
        'pandas',
        'pyparsing',
        pyqtdep,
    ],
    extras_require = {
        'data': ['requests'],
        'export': [],
        'test': ['pytest>=7.0'],
    },
    entry_points = {
        'gui_scripts': ['interference_calculator=interference_calculator.ui:run']
    },

    packages = find_packages(),
    package_data = {'interference_calculator': [
        'periodic_table.csv',
        'icon.svg',
        'icon.ico',
        'icon.icns',
        'display_button_icon.svg',
        'help_button_icon.svg',
        'checkbox_checked.svg',
        'spinbox_plus.svg',
        'spinbox_minus.svg']
    },
    zip_safe = False
)
