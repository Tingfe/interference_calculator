import unittest

from interference_calculator.package_resources import resource_file, resource_path


class PackageResourceTests(unittest.TestCase):
    def test_resource_file_opens_periodic_table(self):
        periodic_table = resource_file(
            'interference_calculator',
            'periodic_table.csv',
        )

        with periodic_table.open(mode='r', encoding='utf-8') as fh:
            header = fh.readline()

        self.assertIn('element', header)

    def test_resource_path_returns_icon_path(self):
        icon_path = resource_path('interference_calculator', 'icon.svg')

        self.assertTrue(icon_path.endswith('icon.svg'))


if __name__ == '__main__':
    unittest.main()
