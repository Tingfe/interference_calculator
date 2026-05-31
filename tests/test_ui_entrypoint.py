import os
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')


class UISourceEntrypointTests(unittest.TestCase):
    def test_ui_file_imports_when_executed_from_package_directory(self):
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / 'interference_calculator' / 'ui.py'
        code = textwrap.dedent(
            f"""
            import importlib.util
            import pathlib
            import sys

            script = pathlib.Path({str(script)!r})
            repo_root = str(script.parent.parent)
            sys.path = [
                str(script.parent),
                *[p for p in sys.path if p not in ('', repo_root)],
            ]

            spec = importlib.util.spec_from_file_location(
                'ui_direct_path_smoke',
                str(script),
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(module.__version__)
            """
        )
        proc = subprocess.run(
            [sys.executable, '-c', code],
            cwd=str(repo_root),
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0 and 'You need to have either PyQt4 or PyQt5' in proc.stderr:
            self.skipTest('GUI entrypoint smoke test requires PyQt')
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)


class UICalculationReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from interference_calculator import ui
            cls.ui = ui
        except ImportError as exc:
            raise unittest.SkipTest(f'GUI calculation reference tests require UI dependencies: {exc}')

    def test_delta_ppm_uses_theoretical_target_mz_reference(self):
        data_out = []
        errors = []
        worker = self.ui.CalculationWorker(
            ['Ar', 'Cl', 'As'],
            '75As',
            targetrange=0.05,
            maxsize=2,
            charge=(1,),
            chargesign='+',
            risk_preset='gdms',
            instrument_mrp=4000,
        )
        worker.finished.connect(data_out.append)
        worker.error.connect(errors.append)
        worker.run()

        self.assertFalse(errors)
        self.assertTrue(data_out)
        data = data_out[0]
        target_mz = data.loc[data['target'].astype(bool), 'mass/charge'].iat[0]
        self.assertEqual(data.attrs['delta_reference'], 'theoretical_target_mz')
        self.assertAlmostEqual(data.attrs['delta_reference_mz'], target_mz)
        non_target = data.loc[~data['target'].astype(bool)].copy()
        self.assertFalse(non_target.empty)
        expected_ppm = non_target['mass/charge diff'] / target_mz * 1e6
        for actual, expected in zip(non_target['Δppm'], expected_ppm):
            self.assertAlmostEqual(actual, expected)


class UIImportedElementSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from interference_calculator import ui
            cls.ui = ui
            cls.app = ui.widgets.QApplication.instance() or ui.widgets.QApplication([])
        except ImportError as exc:
            raise unittest.SkipTest(f'GUI imported element set tests require UI dependencies: {exc}')

    def test_main_window_defaults_to_chinese_language(self):
        window = self.ui.MainWindow()
        widget = window.centralWidget()

        self.assertEqual(widget.language, 'zh')
        self.assertEqual(widget.language_input.currentData(), 'zh')
        self.assertEqual(window.windowTitle(), '无机质谱峰干扰计算器')
        self.assertEqual(widget.interference_button.text(), '计算')
        self.assertEqual(widget.language_input.itemData(0), 'zh')
        window.close()

    def test_imported_element_set_restores_gdms_import_elements(self):
        window = self.ui.MainWindow()
        widget = window.centralWidget()
        widget._gdms_import_elements = ['U', 'B', 'Mg', 'Al']
        widget._refresh_imported_element_set_option()

        index = widget._find_imported_element_set_index()
        self.assertGreaterEqual(index, 0)
        self.assertIn('4', widget.element_set_input.itemText(index))

        widget.atoms_input.set_elements(['U'])
        widget.element_set_input.setCurrentIndex(index)
        widget.add_element_set(index)

        self.assertEqual(widget.atoms_input.elements(), ['U', 'B', 'Mg', 'Al'])
        self.assertEqual(widget.element_set_input.currentIndex(), 0)
        window.close()

    def test_element_set_appends_missing_elements_without_clearing_existing(self):
        window = self.ui.MainWindow()
        widget = window.centralWidget()
        widget.atoms_input.set_elements(['Fe', 'Ni'])

        ar_background_index = 2
        widget.element_set_input.setCurrentIndex(ar_background_index)
        widget.add_element_set(ar_background_index)

        self.assertEqual(
            widget.atoms_input.elements(),
            ['Fe', 'Ni', 'Ar', 'O', 'H', 'C', 'N', 'Cl', 'S'],
        )
        self.assertEqual(widget.element_set_input.currentIndex(), 0)
        window.close()

    def test_target_element_selector_uses_periodic_order(self):
        window = self.ui.MainWindow()
        widget = window.centralWidget()

        first_symbols = [
            widget._target_element_input.itemData(index)
            for index in range(10)
        ]

        self.assertEqual(
            first_symbols,
            ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne'],
        )
        self.assertEqual(
            self.ui._sort_elements_periodic(['U', 'B', 'Mg', 'Al']),
            ['B', 'Mg', 'Al', 'U'],
        )
        window.close()

    def test_imported_targets_use_periodic_order_then_mass_number(self):
        from interference_calculator.gdms_import import GDMSProfile

        window = self.ui.MainWindow()
        widget = window.centralWidget()
        widget._gdms_import_profiles = self.ui._sort_profiles_periodic([
            GDMSProfile('U{238}', 'U', 238, '238U', 4, 1, None, None, None, None),
            GDMSProfile('Fe{57}', 'Fe', 57, '57Fe', 2, 1, None, None, None, None),
            GDMSProfile('B{11}', 'B', 11, '11B', 3, 1, None, None, None, None),
            GDMSProfile('Fe{56}', 'Fe', 56, '56Fe', 1, 1, None, None, None, None),
        ])
        widget._refresh_imported_target_labels()

        labels = [
            widget.imported_target_input.itemData(index).label
            for index in range(1, widget.imported_target_input.count())
        ]

        self.assertEqual(labels, ['B{11}', 'Fe{56}', 'Fe{57}', 'U{238}'])
        window.close()

    def test_imported_target_summary_wraps_across_lines(self):
        from interference_calculator.gdms_import import GDMSProfile

        window = self.ui.MainWindow()
        widget = window.centralWidget()
        widget.language_input.setCurrentIndex(widget._find_combo_data(widget.language_input, 'en'))
        profile = GDMSProfile(
            'Fe{56}', 'Fe', 56, '56Fe', 1, 20, 55.928, 1000.0, 55.9279, 0.0123
        )

        widget._set_target_mz_label_from_profile(profile)
        label = widget._target_mz_result_label

        self.assertTrue(label.wordWrap())
        self.assertEqual(label.text().splitlines()[0], '56Fe')
        self.assertIn('theoretical m/z', label.text())
        self.assertIn('profile centroid m/z 55.9279', label.text())
        self.assertGreaterEqual(label.text().count('\n'), 2)
        window.close()

    def test_imported_profiles_attach_real_points_to_spectrum_metadata(self):
        from interference_calculator.gdms_import import GDMSProfile

        window = self.ui.MainWindow()
        widget = window.centralWidget()
        target_profile = GDMSProfile(
            'Fe{56}', 'Fe', 56, '56Fe', 1, 3, 55.928, 1000.0, 55.9279, 0.0123,
            profile_points=((55.920, 10.0), (55.9279, 1000.0), (55.936, 12.0)),
        )
        neighbor_profile = GDMSProfile(
            'Fe{57}', 'Fe', 57, '57Fe', 4, 3, 55.982, 800.0, 55.9818, 0.011,
            profile_points=((55.974, 8.0), (55.9818, 800.0), (55.990, 6.0)),
        )

        widget._gdms_import_profiles = [target_profile, neighbor_profile]
        widget._refresh_imported_target_labels()
        widget.imported_target_input.setCurrentIndex(1)
        widget.manual_target_toggle.setChecked(False)

        data = self.ui.pd.DataFrame({'mass/charge': [55.934936], 'target': [True]})
        data.attrs['target_mz'] = 55.934936
        data.attrs['delta_reference_mz'] = 55.934936
        widget._attach_gdms_profile_overlays(data)

        overlays = data.attrs['gdms_profile_overlays']
        self.assertEqual(data.attrs['gdms_profile_reference_mz'], 55.9279)
        self.assertEqual(len(overlays), 2)
        self.assertTrue(overlays[0]['is_target'])
        self.assertEqual(overlays[0]['points'][1], (55.9279, 1000.0))
        self.assertEqual(overlays[0]['observed_mz'], 55.9279)
        self.assertAlmostEqual(
            overlays[0]['match_mz'],
            widget._theoretical_target_mz_for_isotope('56Fe'),
        )
        window.close()

    def test_auto_mrp_uses_imported_profile_fwhm_when_enabled(self):
        from interference_calculator.gdms_import import GDMSProfile

        window = self.ui.MainWindow()
        widget = window.centralWidget()
        profile = GDMSProfile(
            'Fe{56}', 'Fe', 56, '56Fe', 1, 3, 55.928, 1000.0, 55.9279, 0.0123,
            profile_points=((55.920, 10.0), (55.9279, 1000.0), (55.936, 12.0)),
        )

        widget._gdms_import_profiles = [profile]
        widget._refresh_imported_target_labels()
        widget.imported_target_input.setCurrentIndex(1)

        self.assertTrue(widget.auto_mrp_toggle.isEnabled())
        widget.auto_mrp_toggle.click()

        self.assertTrue(widget.auto_mrp_toggle.isChecked())
        self.assertEqual(widget.instrument_mrp_input.value(), round(55.9279 / 0.0123))

        widget.auto_mrp_toggle.click()
        self.assertFalse(widget.auto_mrp_toggle.isChecked())
        window.close()

    def test_auto_sweep_uses_imported_profile_mass_range_when_enabled(self):
        from interference_calculator.gdms_import import GDMSProfile

        window = self.ui.MainWindow()
        widget = window.centralWidget()
        profile = GDMSProfile(
            'Fe{56}', 'Fe', 56, '56Fe', 1, 3, 55.936, 1000.0, 55.936, 0.0123,
            profile_points=((55.880, 10.0), (55.936, 1000.0), (55.992, 12.0)),
        )

        widget._gdms_import_profiles = [profile]
        widget._refresh_imported_target_labels()
        widget.imported_target_input.setCurrentIndex(1)

        self.assertTrue(widget.auto_sweep_toggle.isEnabled())
        widget.auto_sweep_toggle.click()

        expected = round((55.992 - 55.880) / 55.936 * 1e6)
        self.assertTrue(widget.auto_sweep_toggle.isChecked())
        self.assertEqual(widget.sweep_input.value(), expected)

        widget.auto_sweep_toggle.click()
        self.assertFalse(widget.auto_sweep_toggle.isChecked())
        window.close()

    def test_auto_sweep_is_disabled_without_valid_profile_points(self):
        from interference_calculator.gdms_import import GDMSProfile

        window = self.ui.MainWindow()
        widget = window.centralWidget()
        profile = GDMSProfile(
            'Fe{56}', 'Fe', 56, '56Fe', 1, 1, 55.936, 1000.0, 55.936, 0.0123,
            profile_points=((55.936, 1000.0),),
        )

        widget._gdms_import_profiles = [profile]
        widget._refresh_imported_target_labels()
        widget.imported_target_input.setCurrentIndex(1)

        self.assertFalse(widget.auto_sweep_toggle.isEnabled())
        self.assertFalse(widget.auto_sweep_toggle.isChecked())
        window.close()

    def test_auto_mrp_is_disabled_without_valid_fwhm(self):
        from interference_calculator.gdms_import import GDMSProfile

        window = self.ui.MainWindow()
        widget = window.centralWidget()
        profile = GDMSProfile(
            'Fe{56}', 'Fe', 56, '56Fe', 1, 3, 55.928, 1000.0, 55.9279, None,
            profile_points=((55.920, 10.0), (55.9279, 1000.0), (55.936, 12.0)),
        )

        widget._gdms_import_profiles = [profile]
        widget._refresh_imported_target_labels()
        widget.imported_target_input.setCurrentIndex(1)

        self.assertFalse(widget.auto_mrp_toggle.isEnabled())
        self.assertFalse(widget.auto_mrp_toggle.isChecked())
        window.close()

    def test_spectrum_profile_toggle_checked_state_keeps_readable_text_color(self):
        spectrum = self.ui.Spectrum(language='en')
        style = spectrum.toolbar.styleSheet()

        self.assertIn('QToolButton:checked', style)
        self.assertIn('color: #172033', style)
        self.assertIn('QToolButton:disabled', style)
        spectrum.close()

    def test_spectrum_maps_imported_profile_points_to_calibrated_delta_ppm(self):
        spectrum = self.ui.Spectrum(language='en')
        data = self.ui.pd.DataFrame({
            'molecule': ['56Fe'],
            'mass/charge': [55.934936],
            'mass/charge diff': [0.0],
            '\u0394ppm': [0.0],
            'probability': [1.0],
            'target': [True],
        })
        data.attrs['target_mz'] = 55.934936
        data.attrs['delta_reference_mz'] = 55.934936
        data.attrs['gdms_profile_reference_mz'] = 55.9279
        data.attrs['gdms_profile_overlays'] = ({
            'label': 'Fe{56}',
            'isotope': '56Fe',
            'points': ((55.9279, 0.0005), (55.9289, 0.00025)),
            'is_target': True,
        },)

        spectrum.plot_spectrum(data)

        self.assertFalse(spectrum._profile_toggle_btn.isChecked())
        self.assertFalse(spectrum._profiles_visible())
        spectrum._profile_toggle_btn.click()
        self.assertTrue(spectrum._profiles_visible())
        self.assertAlmostEqual(spectrum._profile_x_value(55.9279), 0.0)
        self.assertAlmostEqual(
            spectrum._profile_x_value(55.9289),
            (55.9289 - 55.9279) / 55.934936 * 1e6,
        )
        _, ys = spectrum._profile_xy_for(spectrum._profile_overlays[0])
        self.assertAlmostEqual(float(ys.max()), 100.0)
        spectrum.close()

    def test_spectrum_can_match_imported_profile_center_to_theoretical_mz(self):
        spectrum = self.ui.Spectrum(language='en')
        target_mz = 55.934936
        data = self.ui.pd.DataFrame({
            'molecule': ['56Fe'],
            'mass/charge': [target_mz],
            'mass/charge diff': [0.0],
            '\u0394ppm': [0.0],
            'probability': [1.0],
            'target': [True],
        })
        data.attrs['target_mz'] = target_mz
        data.attrs['delta_reference_mz'] = target_mz
        data.attrs['gdms_profile_reference_mz'] = 55.9279
        data.attrs['gdms_profile_overlays'] = ({
            'label': 'Fe{57}',
            'isotope': '57Fe',
            'points': ((55.9818, 800.0), (55.9828, 400.0)),
            'observed_mz': 55.9818,
            'match_mz': 55.9800,
            'is_target': False,
        },)

        spectrum.plot_spectrum(data)
        overlay = spectrum._profile_overlays[0]

        self.assertTrue(spectrum._profile_match_toggle_btn.isEnabled())
        self.assertFalse(spectrum._profile_match_toggle_btn.isChecked())
        self.assertAlmostEqual(
            spectrum._profile_x_value(55.9818, overlay),
            (55.9818 - 55.9279) / target_mz * 1e6,
        )

        spectrum._profile_match_toggle_btn.click()

        self.assertTrue(spectrum._profile_toggle_btn.isChecked())
        self.assertTrue(spectrum._profiles_visible())
        self.assertAlmostEqual(
            spectrum._profile_x_value(55.9818, overlay),
            (55.9800 - target_mz) / target_mz * 1e6,
        )
        self.assertAlmostEqual(
            spectrum._profile_x_value(55.9828, overlay),
            (55.9800 - target_mz + 0.0010) / target_mz * 1e6,
        )
        spectrum.close()

    def test_spectrum_match_guide_reports_visible_shift(self):
        spectrum = self.ui.Spectrum(language='en')
        target_mz = 55.934936
        data = self.ui.pd.DataFrame({
            'molecule': ['56Fe'],
            'mass/charge': [target_mz],
            'mass/charge diff': [0.0],
            '\u0394ppm': [0.0],
            'probability': [1.0],
            'target': [True],
        })
        data.attrs['target_mz'] = target_mz
        data.attrs['delta_reference_mz'] = target_mz
        data.attrs['gdms_profile_reference_mz'] = 55.9279
        data.attrs['gdms_profile_overlays'] = ({
            'label': 'Fe{57}',
            'isotope': '57Fe',
            'points': ((55.9818, 800.0), (55.9828, 400.0)),
            'observed_mz': 55.9818,
            'match_mz': 55.9800,
            'is_target': False,
        },)

        spectrum.plot_spectrum(data)
        overlay = spectrum._profile_overlays[0]
        raw_x = spectrum._profile_target_aligned_x_value(55.9818)

        spectrum._profile_match_toggle_btn.click()

        matched_x = spectrum._profile_x_value(55.9818, overlay)
        self.assertNotAlmostEqual(raw_x, matched_x)
        expected_shift = (55.9800 - target_mz) / target_mz * 1e6
        expected_shift -= (55.9818 - 55.9279) / target_mz * 1e6
        self.assertAlmostEqual(matched_x - raw_x, expected_shift)
        spectrum.close()


if __name__ == '__main__':
    unittest.main()
