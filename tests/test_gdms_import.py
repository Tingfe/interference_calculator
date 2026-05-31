import os
import tempfile
import unittest

from interference_calculator.gdms_import import (
    extract_profile_elements,
    label_to_isotope,
    parse_gdms_profile_xlsx,
    summarize_profile,
)


class GDMSImportTests(unittest.TestCase):
    def test_label_to_isotope_accepts_gdms_brace_labels(self):
        self.assertEqual(label_to_isotope('Fe{56}'), ('Fe', 56, '56Fe'))
        self.assertEqual(label_to_isotope(' U{238} '), ('U', 238, '238U'))
        self.assertIsNone(label_to_isotope('56Fe'))

    def test_summarize_profile_returns_apex_centroid_and_fwhm(self):
        summary = summarize_profile(
            [55.90, 55.92, 55.94, 55.96, 55.98],
            [0.0, 4.0, 10.0, 4.0, 0.0],
        )

        self.assertEqual(summary.point_count, 5)
        self.assertAlmostEqual(summary.apex_mz, 55.94)
        self.assertAlmostEqual(summary.apex_intensity, 10.0)
        self.assertAlmostEqual(summary.centroid_mz, 55.94)
        self.assertAlmostEqual(summary.fwhm, 1.0 / 30.0)

    def test_parse_gdms_profile_xlsx_extracts_profiles_and_elements(self):
        try:
            import openpyxl
        except ImportError as exc:
            raise unittest.SkipTest(f'openpyxl is optional: {exc}')

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet['A1'] = 'Fe{56}'
        sheet['A2'] = 'Mass'
        sheet['B2'] = 'Values'
        sheet['C2'] = 'Peaks'
        sheet['D1'] = 'U{238}'
        sheet['D2'] = 'Mass'
        sheet['E2'] = 'Values'
        sheet['F2'] = 'Peaks'
        for row, (mass, value) in enumerate(
            [(55.90, 0), (55.92, 4), (55.94, 10), (55.96, 4), (55.98, 0)],
            start=3,
        ):
            sheet.cell(row, 1).value = mass
            sheet.cell(row, 2).value = value
            sheet.cell(row, 4).value = mass + 182.0
            sheet.cell(row, 5).value = value / 2.0

        handle = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        handle.close()
        try:
            workbook.save(handle.name)
            profiles = parse_gdms_profile_xlsx(handle.name)
        finally:
            workbook.close()
            os.remove(handle.name)

        self.assertEqual([profile.label for profile in profiles], ['Fe{56}', 'U{238}'])
        self.assertEqual([profile.isotope for profile in profiles], ['56Fe', '238U'])
        self.assertEqual(extract_profile_elements(profiles), ['Fe', 'U'])
        self.assertAlmostEqual(profiles[0].centroid_mz, 55.94)
        self.assertEqual(
            profiles[0].profile_points,
            ((55.90, 0.0), (55.92, 4.0), (55.94, 10.0), (55.96, 4.0), (55.98, 0.0)),
        )


if __name__ == '__main__':
    unittest.main()
