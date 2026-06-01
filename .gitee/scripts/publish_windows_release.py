#!/usr/bin/env python3
"""Build and upload an experimental Windows zip from a Gitee release pipeline."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


OWNER = "tyongs"
REPO = "interference_calculator"
APP_NAME = "InterferenceCalculator"


def package_version() -> str:
    init_text = Path("interference_calculator/__init__.py").read_text(encoding="utf-8")
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", init_text)
    if not match:
        raise SystemExit("Could not find __version__ in interference_calculator/__init__.py")
    return match.group(1)


def release_tag(version: str) -> str:
    candidates = [
        os.environ.get("GITEE_REF_NAME"),
        os.environ.get("CI_COMMIT_REF_NAME"),
        os.environ.get("GITEE_BRANCH"),
    ]
    for candidate in candidates:
        if candidate:
            tag = candidate.removeprefix("refs/tags/")
            break
    else:
        tag = ""

    if not tag:
        completed = subprocess.run(
            ["git", "describe", "--tags", "--exact-match"],
            capture_output=True,
            text=True,
            check=False,
        )
        tag = completed.stdout.strip()
    if not tag:
        tag = f"v{version}"
    if tag.startswith("v") and tag[1:] != version:
        raise SystemExit(f"Tag version {tag[1:]} does not match package __version__ {version}")
    return tag


def changelog_body(version: str) -> str:
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8").splitlines()
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
    for heading in ("### 中文", "### English"):
        if heading not in body:
            raise SystemExit(f"CHANGELOG.md section ## [{version}] must include {heading}")
    return body


def append_download_note(body: str, tag: str) -> str:
    return (
        body.rstrip()
        + f"""

## Gitee Windows Package / Gitee Windows 安装包

This Gitee release may include a Windows standalone zip built directly by the
experimental Gitee Windows pipeline. If the zip is absent, the runner did not
provide a Windows-capable build environment; use the canonical GitHub installer:
https://github.com/Tingfe/interference_calculator/releases/tag/{tag}

本 Gitee 发行版可能包含由实验性 Gitee Windows 流水线直接构建的 Windows 免安装包。
如果没有看到该 zip 附件，说明当前 Gitee runner 不具备 Windows 构建环境，请使用
正式 GitHub 安装包：
https://github.com/Tingfe/interference_calculator/releases/tag/{tag}
"""
    )


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> int:
    version = package_version()
    tag = release_tag(version)

    run(
        [
            sys.executable,
            "packaging/windows/build_windows_zip.py",
            "--tag",
            tag,
            "--install",
            "--skip-non-windows",
        ]
    )

    zip_path = Path("dist") / f"{APP_NAME}-Windows-{tag}.zip"
    if not zip_path.is_file():
        print(
            "No Windows zip was produced. This is expected on non-Windows Gitee runners.",
            flush=True,
        )
        return 0

    if not os.environ.get("GITEE_ACCESS_TOKEN"):
        raise SystemExit("GITEE_ACCESS_TOKEN is required to upload the Windows zip")

    body_path = Path("release/windows_release_body.md")
    body_path.parent.mkdir(parents=True, exist_ok=True)
    body_path.write_text(append_download_note(changelog_body(version), tag), encoding="utf-8")

    run(
        [
            sys.executable,
            ".github/scripts/sync_gitee_release.py",
            "--owner",
            OWNER,
            "--repo",
            REPO,
            "--tag",
            tag,
            "--name",
            f"Interference Calculator {tag}",
            "--body-file",
            str(body_path),
            "--target-commitish",
            "main",
            "--max-asset-bytes",
            os.environ.get("GITEE_WINDOWS_MAX_ASSET_BYTES", "0"),
            "--assets",
            str(zip_path),
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
