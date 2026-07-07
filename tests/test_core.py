import math
import unittest
import warnings

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

    def test_interference_target_row_does_not_emit_mrp_divide_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', RuntimeWarning)
            data = ic.interference(['As'], '75As', targetrange=0.01, charge=1, chargesign='+')

        self.assertEqual(data['target'].sum(), 1)
        divide_warnings = [
            item for item in caught
            if issubclass(item.category, RuntimeWarning)
            and 'divide by zero' in str(item.message)
        ]
        self.assertEqual(divide_warnings, [])

    def test_standard_ratio_calculates_relative_ratios(self):
        data = ic.standard_ratio(['O'])

        self.assertEqual(data['isotope'].tolist(), ['16O', '17O', '18O'])
        self.assertAlmostEqual(data.loc[data['isotope'] == '16O', 'ratio'].iat[0], 1.0)
        self.assertGreater(data.loc[data['isotope'] == '18O', 'inverse ratio'].iat[0], 400)


class InorganicInterferenceTests(unittest.TestCase):
    def test_inorganic_mode_finds_argon_chloride_near_arsenic(self):
        data = ic.inorganic_interference(
            ['Ar', 'Cl', 'As', 'O', 'H'],
            '75As',
            targetrange=0.02,
            charge=[1, 2],
            maxsize=3,
        )

        argon_chloride = data[data['type'] == 'plasma adduct']
        self.assertFalse(argon_chloride.empty)
        self.assertTrue(argon_chloride['molecule'].str.contains('Cl').any())
        self.assertTrue(argon_chloride['molecule'].str.contains('Ar').any())
        self.assertIn('relative risk', data.columns)
        self.assertIn('m/z uncertainty', data.columns)
        self.assertEqual(data['target'].sum(), 1)
        row = argon_chloride.iloc[0]
        molecule = ic.Molecule(row['molecule'])
        self.assertAlmostEqual(row['mass/charge'], molecule.mass / molecule.charge)

    def test_inorganic_mode_respects_maxsize_for_adducts(self):
        data = ic.inorganic_interference(
            ['Ar', 'Cl', 'As'],
            '74.921',
            targetrange=0.02,
            charge=[1, 2],
            maxsize=1,
        )

        self.assertNotIn('plasma adduct', set(data['type']))
        self.assertIn('atomic', set(data['type']))

    def test_inorganic_mode_risk_presets_change_relative_risk(self):
        gdms = ic.inorganic_interference(
            ['Ar', 'Cl', 'As'],
            '75As',
            targetrange=0.02,
            risk_preset='gdms',
        )
        icp_ms = ic.inorganic_interference(
            ['Ar', 'Cl', 'As'],
            '75As',
            targetrange=0.02,
            risk_preset='icp-ms',
        )

        gdms_adduct = gdms.loc[gdms['type'] == 'plasma adduct', 'relative risk'].max()
        icp_ms_adduct = icp_ms.loc[icp_ms['type'] == 'plasma adduct', 'relative risk'].max()
        self.assertGreater(icp_ms_adduct, gdms_adduct)

    def test_inorganic_mode_accepts_custom_formation_factors(self):
        data = ic.inorganic_interference(
            ['Ar', 'Cl', 'As'],
            '75As',
            targetrange=0.02,
            formation_factors={'plasma adduct': 0.5},
        )

        factor = data.loc[data['type'] == 'plasma adduct', 'formation factor'].iat[0]
        self.assertEqual(factor, 0.5)

    def test_inorganic_mode_can_disable_plasma_role(self):
        data = ic.inorganic_interference(
            ['Ar', 'Cl', 'As'],
            '75As',
            targetrange=0.02,
            plasma_atoms=[],
        )

        self.assertNotIn('plasma adduct', set(data['type']))

    def test_inorganic_mode_generates_background_molecules(self):
        data = ic.inorganic_interference(
            ['C', 'N', 'O'],
            31.989,
            targetrange=0.02,
            maxsize=2,
        )

        self.assertIn('background molecule', set(data['type']))

    def test_inorganic_mode_rejects_unknown_risk_preset(self):
        with self.assertRaises(ValueError):
            ic.inorganic_interference(['Ar', 'Cl'], '75As', risk_preset='unknown')

    def test_inorganic_mode_weights_risk_with_sample_profile(self):
        profile = {
            'matrix': {'Al': 0.99999},
            'expected_impurities_ppm': {'Fe': 10.0, 'Cu': 1.0},
            'background': {'O': 'medium'},
            'unknown_element_activity': 'ultra_trace',
        }
        data = ic.inorganic_interference(
            ['Al', 'Fe', 'Cu', 'O'],
            None,
            charge=[1],
            maxsize=2,
            sample_profile=profile,
        )

        self.assertIn('sample prior', data.columns)
        self.assertIn('unweighted relative risk', data.columns)
        self.assertIn('expected relative intensity', data.columns)
        self.assertIn('risk rationale', data.columns)

        oxides = data[data['type'] == 'oxide']
        al_oxide_risk = oxides[
            oxides['molecule'].str.contains('Al')
        ]['relative risk'].max()
        fe_oxide_risk = oxides[
            oxides['molecule'].str.contains('Fe')
        ]['relative risk'].max()
        self.assertGreater(al_oxide_risk, fe_oxide_risk)
        cu_atomic_prior = data[
            (data['type'] == 'atomic') & data['molecule'].str.contains('Cu')
        ]['sample prior'].max()
        self.assertAlmostEqual(cu_atomic_prior, 1.0e-6)

    def test_inorganic_mode_sample_profile_preset_expands_atoms(self):
        data = ic.inorganic_interference(
            [],
            None,
            charge=[1],
            maxsize=2,
            sample_profile='high-purity-aluminum',
        )

        self.assertFalse(data.empty)
        self.assertIn('Al', ''.join(data['molecule'].astype(str).tolist()))
        self.assertIn('sample prior', data.columns)

    def test_inorganic_mode_includes_common_sample_profile_presets(self):
        expected_profiles = {
            'high-purity-aluminum',
            'high-purity-copper',
            'high-purity-iron',
            'high-purity-nickel',
            'high-purity-titanium',
            'high-purity-silicon',
            'high-purity-magnesium',
            'aluminum-alloy',
            'stainless-steel',
            'nickel-base-alloy',
            'copper-base-alloy',
            'silicate-glass',
            'graphite-carbon',
        }

        self.assertTrue(expected_profiles.issubset(ic.SAMPLE_PROFILE_PRESETS))

    def test_inorganic_mode_accepts_sample_profile_aliases(self):
        data = ic.inorganic_interference(
            [],
            None,
            charge=[1],
            maxsize=1,
            sample_profile='stainless steel',
        )

        self.assertFalse(data.empty)
        self.assertIn('sample prior', data.columns)
        self.assertTrue(data['risk rationale'].astype(str).str.contains('Cr:matrix').any())

    def test_inorganic_mode_sample_profile_roles_drive_candidate_generation(self):
        data = ic.inorganic_interference(
            [],
            None,
            charge=[1],
            maxsize=2,
            sample_profile='graphite',
        )

        clusters = data[data['type'] == 'cluster']
        self.assertFalse(clusters.empty)
        self.assertTrue(clusters['risk rationale'].astype(str).str.contains('C:matrix').any())

    def test_inorganic_mode_rejects_unknown_sample_profile(self):
        with self.assertRaises(ValueError):
            ic.inorganic_interference(['Al'], None, sample_profile='unknown-profile')


if __name__ == '__main__':
    unittest.main()
