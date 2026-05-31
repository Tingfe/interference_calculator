import math
import unittest

import interference_calculator as ic


class PeriodicTableTests(unittest.TestCase):
    def test_periodic_table_uses_updated_ciaaw_ame_schema(self):
        self.assertEqual(ic.periodic_table['element'].nunique(), 92)
        self.assertIn('mass uncertainty', ic.periodic_table.columns)
        self.assertIn('abundance low', ic.periodic_table.columns)
        self.assertIn('abundance kind', ic.periodic_table.columns)
        self.assertTrue((ic.periodic_table['mass source'] == 'AME2020').all())
        self.assertIn('226Ra', set(ic.periodic_table['isotope']))


class MoleculeTests(unittest.TestCase):
    def test_molecule_parses_charged_isotope_formula(self):
        molecule = ic.Molecule('C2 15N O3 2+')

        self.assertEqual(molecule.elements, ['N', 'C', 'O'])
        self.assertEqual(molecule.isotopes, ['15N', '12C', '16O'])
        self.assertEqual(molecule.charge, 2)
        self.assertEqual(molecule.chargesign, '+')
        self.assertAlmostEqual(molecule.mass, 86.98375559918199)
        self.assertGreater(molecule.mass_uncertainty, 0)
        self.assertAlmostEqual(molecule.abundance, 0.003556781781163718)

    def test_molecule_formats_deuterium_alias(self):
        molecule = ic.Molecule('D2 O -')

        self.assertEqual(molecule.isotopes, ['2H', '16O'])
        self.assertEqual(molecule.formula(), 'D2 O -')
        self.assertEqual(molecule.formula(HtoD=False, all_isotopes=True), '2H2 16O -')

    def test_isotope_notation_with_spaces_uses_isotope_parser(self):
        molecule = ic.Molecule('16O 40Ca -')

        self.assertEqual(molecule.isotopes, ['16O', '40Ca'])
        self.assertEqual(molecule.formula(), 'O Ca -')


class InterferenceTests(unittest.TestCase):
    def test_interference_accepts_scalar_charge(self):
        data = ic.interference(['Ca', 'O', 'H', 'Si'], 'Fe', charge=1)

        self.assertEqual(
            list(data.columns),
            ['molecule', 'charge', 'mass/charge', 'mass/charge diff',
             'MRP', 'probability', 'target'],
        )
        self.assertEqual(data['target'].sum(), 1)
        self.assertEqual(data['molecule'].iloc[0], 'O Ca -')
        self.assertEqual(data.loc[data['target'], 'molecule'].iat[0], 'Fe -')
        self.assertTrue(math.isinf(data.loc[data['target'], 'MRP'].iat[0]))

    def test_interference_infers_charged_target_mz(self):
        data = ic.interference(['As'], '75As', targetrange=0.01, charge=1, chargesign='+')

        target_mz = data.loc[data['target'], 'mass/charge'].iat[0]
        self.assertAlmostEqual(target_mz, ic.Molecule('75As +').mass)

    def test_interference_keeps_neutral_target_neutral(self):
        data = ic.interference(['As'], '75As', targetrange=0.01, charge=1, chargesign='o')

        target = data.loc[data['target']].iloc[0]
        self.assertEqual(target['charge'], 0)
        self.assertAlmostEqual(target['mass/charge'], ic.Molecule('75As').mass)

    def test_standard_ratio_calculates_relative_ratios(self):
        data = ic.standard_ratio(['O'])

        self.assertEqual(data['isotope'].tolist(), ['16O', '17O', '18O'])
        self.assertAlmostEqual(data.loc[data['isotope'] == '16O', 'ratio'].iat[0], 1.0)
        self.assertGreater(data.loc[data['isotope'] == '18O', 'inverse ratio'].iat[0], 400)

    def test_original_maintenance_api_is_general_scan_only(self):
        self.assertTrue(hasattr(ic, 'interference'))
        self.assertTrue(hasattr(ic, 'standard_ratio'))
        self.assertFalse(hasattr(ic, 'inorganic_interference'))


if __name__ == '__main__':
    unittest.main()
