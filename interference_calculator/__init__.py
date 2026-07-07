# -*- coding: utf-8 -*-
""" Calculate mass interference and standard isotopic ratios for mass spectrometry. """

__version__ = '2.8.0'
__name__ = 'interference_calculator'
__author__ = 'Zan Peeters'
__maintainer__ = 'Tingfe'
__contributors__ = ['Zan Peeters', 'Tingfe']
__latest_contributor__ = 'Tingfe'
__url__ = 'https://gitee.com/tyongs/interference_calculator'
__license__ = 'BSD 3-Clause Clear'
__copyright__ = '(c) 2017 Zan Peeters'
__description__ = __doc__

_LAZY_ATTRS = {
    'Molecule': ('interference_calculator.molecule', 'Molecule'),
    'periodic_table': ('interference_calculator.molecule', 'periodic_table'),
    'mass_electron': ('interference_calculator.molecule', 'mass_electron'),
    'templates': ('interference_calculator.molecule', 'templates'),
    'interference': ('interference_calculator.main', 'interference'),
    'interference_gpu': ('interference_calculator.main', 'interference_gpu'),
    'standard_ratio': ('interference_calculator.main', 'standard_ratio'),
    'inorganic_interference': ('interference_calculator.inorganic', 'inorganic_interference'),
    'SAMPLE_PROFILE_PRESETS': ('interference_calculator.inorganic', 'SAMPLE_PROFILE_PRESETS'),
}

__all__ = [
    '__version__',
    'Molecule',
    'periodic_table',
    'mass_electron',
    'templates',
    'interference',
    'standard_ratio',
    'inorganic_interference',
    'SAMPLE_PROFILE_PRESETS',
]


def __getattr__(name):
    """Load heavy scientific modules only when the public API needs them."""
    try:
        module_name, attr_name = _LAZY_ATTRS[name]
    except KeyError:
        raise AttributeError(name)
    module = __import__(module_name, fromlist=[attr_name])
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
