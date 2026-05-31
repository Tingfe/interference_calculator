import importlib
import unittest
from interference_calculator import __version__


class LocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.ui = importlib.import_module('interference_calculator.ui')
            cls.ui_help = importlib.import_module('interference_calculator.ui_help')
        except ImportError as exc:
            raise unittest.SkipTest(f'GUI localization requires UI dependencies: {exc}')

    def test_ui_text_keys_are_bilingual(self):
        ui_text = self.ui._UI_TEXT
        self.assertIn('en', ui_text)
        self.assertIn('zh', ui_text)
        self.assertEqual(set(ui_text['en']), set(ui_text['zh']))

    def test_tooltip_keys_are_bilingual(self):
        tooltips = self.ui_help._TOOLTIPS
        self.assertIn('en', tooltips)
        self.assertIn('zh', tooltips)
        self.assertEqual(set(tooltips['en']), set(tooltips['zh']))

    def test_help_and_warning_text_have_language_variants(self):
        self.assertEqual(set(self.ui_help._MZ_WARNINGS), {'en', 'zh'})
        self.assertIn('Software overview', self.ui_help.help_text_for('en'))
        self.assertIn('软件介绍', self.ui_help.help_text_for('zh'))
        self.assertIn('Are you sure?', self.ui_help.mz_warning_for('en'))
        self.assertIn('确定继续吗？', self.ui_help.mz_warning_for('zh'))

    def test_help_text_renders_version_without_interpreting_isotope_braces(self):
        for language in ('en', 'zh'):
            rendered = self.ui_help.render_help_text(language, __version__)
            self.assertIn(__version__, rendered)
            self.assertIn('Fe{56}', rendered)


if __name__ == '__main__':
    unittest.main()
