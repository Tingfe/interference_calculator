#!/usr/bin/env python3
"""Validate a release tag and extract its changelog section for Gitee."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


def read_package_version() -> str:
    init_path = Path("interference_calculator/__init__.py")
    module = ast.parse(init_path.read_text(encoding="utf-8"), filename=str(init_path))
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__version__":
                value = ast.literal_eval(node.value)
                if isinstance(value, str) and value:
                    return value
    raise SystemExit("Could not find __version__ in interference_calculator/__init__.py")


def extract_changelog_section(version: str) -> str:
    changelog_path = Path("CHANGELOG.md")
    changelog = changelog_path.read_text(encoding="utf-8").splitlines()
    start = None
    for index, line in enumerate(changelog):
        if re.match(rf"^## \[{re.escape(version)}\](?:\s|$)", line):
            start = index + 1
            break
    if start is None:
        raise SystemExit(f"CHANGELOG.md is missing ## [{version}]")

    end = len(changelog)
    for index in range(start, len(changelog)):
        if re.match(r"^## \[", changelog[index]):
            end = index
            break

    body = "\n".join(changelog[start:end]).strip()
    if not body:
        raise SystemExit(f"CHANGELOG.md section ## [{version}] is empty")
    for heading in ("### English", "### 中文"):
        if heading not in body:
            raise SystemExit(f"CHANGELOG.md section ## [{version}] must include {heading}")
    return body


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("Usage: prepare_release_notes.py VERSION OUTPUT_PATH")

    version = argv[1].removeprefix("v")
    output_path = Path(argv[2])
    package_version = read_package_version()
    if package_version != version:
        raise SystemExit(
            f"Tag version {version} does not match package __version__ {package_version}"
        )

    body = extract_changelog_section(version)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
