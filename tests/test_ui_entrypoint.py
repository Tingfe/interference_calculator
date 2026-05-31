import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


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


if __name__ == '__main__':
    unittest.main()
