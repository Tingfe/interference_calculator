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

    def test_imported_element_set_restores_gdms_import_elements(self):
        window = self.ui.MainWindow()
        widget = window.centralWidget()
        widget._gdms_import_elements = ['U', 'B', 'Mg', 'Al']
        widget._refresh_imported_element_set_option()

        index = widget._find_imported_element_set_index()
        self.assertGreaterEqual(index, 0)
        self.assertIn('(4)', widget.element_set_input.itemText(index))

        widget.atoms_input.set_elements(['U'])
        widget.element_set_input.setCurrentIndex(index)
        widget.add_element_set(index)

        self.assertEqual(widget.atoms_input.elements(), ['U', 'B', 'Mg', 'Al'])
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


if __name__ == '__main__':
    unittest.main()
