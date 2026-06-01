#!/usr/bin/env python3
"""Build the Windows standalone zip package.

This script must run on Windows for a real Windows desktop package. It can be
called from non-Windows CI with --skip-non-windows to make experimental Gitee
pipelines report a clear skip instead of failing the release.
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


APP_NAME = "InterferenceCalculator"
PACKAGE_DIR = Path("interference_calculator")


def package_version() -> str:
    init_text = (PACKAGE_DIR / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", init_text)
    if not match:
        raise SystemExit("Could not find __version__ in interference_calculator/__init__.py")
    return match.group(1)


def normalized_tag(tag: str | None, version: str) -> str:
    if not tag:
        return f"v{version}"
    tag = tag.removeprefix("refs/tags/")
    if tag.startswith("v") and tag[1:] != version:
        raise SystemExit(f"Tag version {tag[1:]} does not match package __version__ {version}")
    return tag


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def pyinstaller_args() -> list[str]:
    data_files = [
        "periodic_table.csv",
        "icon.svg",
        "icon.ico",
        "icon.icns",
        "display_button_icon.svg",
        "help_button_icon.svg",
    ]
    excluded_modules = [
        "PyQt5.QtNetwork",
        "PyQt5.QtMultimedia",
        "PyQt5.QtMultimediaWidgets",
        "PyQt5.QtQml",
        "PyQt5.QtQuick",
        "PyQt5.QtQuickWidgets",
        "PyQt5.QtWebEngine",
        "PyQt5.QtWebEngineWidgets",
        "PyQt5.QtWebChannel",
        "PyQt5.QtXml",
        "PyQt5.QtXmlPatterns",
        "PyQt5.QtSql",
        "PyQt5.QtTest",
        "PyQt5.QtPrintSupport",
        "PyQt5.QtHelp",
        "PyQt5.QtBluetooth",
        "PyQt5.QtNfc",
        "PyQt5.QtPositioning",
        "PyQt5.QtSensors",
        "PyQt5.QtSerialPort",
        "PyQt5.QtWebSockets",
        "PyQt5.QtDBus",
        "PyQt5.QtDesigner",
        "PyQt5.QtOpenGL",
        "PyQt5.QtOpenGLWidgets",
        "PyQt5.QtLocation",
        "PyQt5.QtPdf",
        "PyQt5.QtPdfWidgets",
        "PyQt5.QtScxml",
        "PyQt5.QtStateMachine",
        "PyQt5.QtTextToSpeech",
        "PyQt5.QtUiTools",
    ]

    args = [
        "--name",
        APP_NAME,
        "--windowed",
        "--noupx",
        "--icon",
        str(PACKAGE_DIR / "icon.ico"),
    ]
    for file_name in data_files:
        args.extend(["--add-data", f"{PACKAGE_DIR / file_name};{PACKAGE_DIR}"])
    args.extend(["--hidden-import", "PyQt5.QtSvg", "--hidden-import", "openpyxl"])
    for module_name in excluded_modules:
        args.extend(["--exclude-module", module_name])
    args.append(str(PACKAGE_DIR / "ui.py"))
    return args


def zip_directory(source_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source_dir))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default=os.environ.get("GITEE_REF_NAME") or os.environ.get("CI_COMMIT_REF_NAME"))
    parser.add_argument("--output-dir", default="dist")
    parser.add_argument("--install", action="store_true", help="Install build dependencies before packaging")
    parser.add_argument(
        "--skip-non-windows",
        action="store_true",
        help="Exit successfully when the current runner is not Windows",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if platform.system() != "Windows":
        message = f"Windows package build requires Windows; current runner is {platform.system()}."
        if args.skip_non_windows:
            print(f"{message} Skipping Windows zip build.", flush=True)
            return 0
        raise SystemExit(message)

    version = package_version()
    tag = normalized_tag(args.tag, version)
    output_dir = Path(args.output_dir)

    if args.install:
        run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        run([sys.executable, "-m", "pip", "install", ".[export]", "pyinstaller"])

    app_dir = output_dir / APP_NAME
    if app_dir.exists():
        shutil.rmtree(app_dir)

    run([sys.executable, "-m", "PyInstaller", *pyinstaller_args()])

    zip_path = output_dir / f"{APP_NAME}-Windows-{tag}.zip"
    zip_directory(app_dir, zip_path)
    print(f"Built Windows zip: {zip_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
