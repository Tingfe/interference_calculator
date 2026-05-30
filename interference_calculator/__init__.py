# -*- coding: utf-8 -*-
""" Calculate mass interference and standard isotopic ratios for mass spectrometry. """
from interference_calculator.molecule import Molecule, periodic_table, mass_electron, templates
from interference_calculator.main import interference, standard_ratio
from interference_calculator.inorganic import inorganic_interference

__version__ = '2.0.4'
__name__ = 'interference_calculator'
__author__ = 'Zan Peeters'
__maintainer__ = 'Tingfe'
__contributors__ = ['Zan Peeters', 'Tingfe']
__latest_contributor__ = 'Tingfe'
__url__ = 'https://github.com/Tingfe/interference_calculator'
__license__ = 'BSD 3-Clause Clear'
__copyright__ = '(c) 2017 Zan Peeters'
__description__ = __doc__
