#!/usr/bin/env python3
"""Create or update a Gitee release from GitHub Actions build artifacts."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4


API_BASE = "https://gitee.com/api/v5"


class GiteeApiError(RuntimeError):
    """Raised when the Gitee API returns an unexpected response."""


def _json_or_text(payload: bytes) -> Any:
    if not payload:
        return None
    try:
        return json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError:
        return payload.decode("utf-8", errors="replace")


def _format_api_error(method: str, path: str, status: int, payload: bytes) -> str:
    body = _json_or_text(payload)
    if isinstance(body, dict):
        message = body.get("message") or body.get("error") or json.dumps(body, ensure_ascii=False)
    else:
        message = str(body)
    return f"Gitee API {method} {path} failed with HTTP {status}: {message}"


def _multipart_body(fields: dict[str, str], file_path: Path) -> tuple[bytes, str]:
    boundary = f"----interference-calculator-{uuid4().hex}"
    chunks: list[bytes] = []

    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")

    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    chunks.append(f"--{boundary}\r\n".encode("utf-8"))
    chunks.append(
        (
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode("utf-8")
    )
    chunks.append(file_path.read_bytes())
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


class GiteeClient:
    def __init__(
        self,
        owner: str,
        repo: str,
        token: str,
        api_base: str = API_BASE,
        timeout_seconds: int = 900,
    ) -> None:
        self.owner = owner
        self.repo = repo
        self.token = token
        self.api_base = api_base.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def request(
        self,
        method: str,
        path: str,
        fields: dict[str, str] | None = None,
        file_path: Path | None = None,
    ) -> Any:
        fields = {"access_token": self.token, **(fields or {})}
        url = f"{self.api_base}{path}"
        data: bytes | None = None
        headers: dict[str, str] = {"Accept": "application/json"}

        if method in {"GET", "DELETE"}:
            url = f"{url}?{urlencode(fields)}"
        elif file_path is not None:
            curl = shutil.which("curl")
            if curl:
                return self._curl_multipart_request(curl, method, path, fields, file_path)
            data, content_type = _multipart_body(fields, file_path)
            headers["Content-Type"] = content_type
        else:
            data = urlencode(fields).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return _json_or_text(response.read())
        except HTTPError as exc:
            payload = exc.read()
            raise GiteeApiError(_format_api_error(method, path, exc.code, payload)) from exc
        except URLError as exc:
            raise GiteeApiError(f"Gitee API {method} {path} failed: {exc.reason}") from exc

    def _curl_multipart_request(
        self,
        curl: str,
        method: str,
        path: str,
        fields: dict[str, str],
        file_path: Path,
    ) -> Any:
        url = f"{self.api_base}{path}"
        command = [
            curl,
            "--fail-with-body",
            "--silent",
            "--show-error",
            "--location",
            "--connect-timeout",
            "30",
            "--max-time",
            str(self.timeout_seconds),
            "--retry",
            "2",
            "--retry-delay",
            "10",
            "--request",
            method,
        ]
        for name, value in fields.items():
            command.extend(["--form", f"{name}={value}"])
        command.extend(["--form", f"file=@{file_path}", url])

        completed = subprocess.run(command, capture_output=True, check=False)
        if completed.returncode != 0:
            payload = completed.stdout or completed.stderr
            body = _json_or_text(payload)
            message = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
            raise GiteeApiError(f"Gitee API {method} {path} failed with curl exit {completed.returncode}: {message}")
        return _json_or_text(completed.stdout)

    def list_releases(self) -> list[dict[str, Any]]:
        releases: list[dict[str, Any]] = []
        for page in range(1, 11):
            data = self.request(
                "GET",
                f"/repos/{self.owner}/{self.repo}/releases",
                {"page": str(page), "per_page": "100"},
            )
            if not isinstance(data, list):
                raise GiteeApiError("Gitee releases response was not a list")
            releases.extend(data)
            if len(data) < 100:
                break
        return releases

    def find_release_by_tag(self, tag_name: str) -> dict[str, Any] | None:
        for release in self.list_releases():
            if release.get("tag_name") == tag_name:
                return release
        return None

    def create_release(
        self,
        tag_name: str,
        name: str,
        body: str,
        target_commitish: str,
        prerelease: bool,
    ) -> dict[str, Any]:
        data = self.request(
            "POST",
            f"/repos/{self.owner}/{self.repo}/releases",
            {
                "tag_name": tag_name,
                "name": name,
                "body": body,
                "target_commitish": target_commitish,
                "prerelease": str(prerelease).lower(),
            },
        )
        if not isinstance(data, dict):
            raise GiteeApiError("Gitee create release response was not an object")
        return data

    def update_release(self, release_id: int | str, tag_name: str, name: str, body: str) -> dict[str, Any]:
        data = self.request(
            "PATCH",
            f"/repos/{self.owner}/{self.repo}/releases/{release_id}",
            {
                "tag_name": tag_name,
                "name": name,
                "body": body,
            },
        )
        if not isinstance(data, dict):
            raise GiteeApiError("Gitee update release response was not an object")
        return data

    def list_assets(self, release_id: int | str) -> list[dict[str, Any]]:
        data = self.request(
            "GET",
            f"/repos/{self.owner}/{self.repo}/releases/{release_id}/attach_files",
        )
        if not isinstance(data, list):
            raise GiteeApiError("Gitee release assets response was not a list")
        return data

    def delete_asset(self, release_id: int | str, asset_id: int | str) -> None:
        self.request(
            "DELETE",
            f"/repos/{self.owner}/{self.repo}/releases/{release_id}/attach_files/{asset_id}",
        )

    def upload_asset(self, release_id: int | str, asset_path: Path) -> dict[str, Any]:
        data = self.request(
            "POST",
            f"/repos/{self.owner}/{self.repo}/releases/{release_id}/attach_files",
            {
                "owner": self.owner,
                "repo": self.repo,
                "release_id": str(release_id),
            },
            file_path=asset_path,
        )
        if not isinstance(data, dict):
            raise GiteeApiError(f"Gitee upload response for {asset_path.name} was not an object")
        return data


def asset_name(asset: dict[str, Any]) -> str:
    for key in ("name", "filename", "file_name"):
        value = asset.get(key)
        if isinstance(value, str) and value:
            return Path(value).name
    url = asset.get("browser_download_url") or asset.get("download_url")
    if isinstance(url, str) and url:
        return Path(url).name
    return ""


def collect_asset_paths(paths: list[str]) -> list[Path]:
    assets = [Path(path) for path in paths]
    missing = [str(path) for path in assets if not path.is_file()]
    if missing:
        raise SystemExit(f"Asset path does not exist or is not a file: {', '.join(missing)}")
    return sorted(assets, key=lambda path: (path.stat().st_size, path.name))


def sync_release(
    client: GiteeClient,
    tag_name: str,
    name: str,
    body: str,
    target_commitish: str,
    prerelease: bool,
    asset_paths: list[Path],
    max_upload_attempts: int = 3,
) -> None:
    release = client.find_release_by_tag(tag_name)
    if release is None:
        print(f"Creating Gitee release {tag_name}", flush=True)
        release = client.create_release(tag_name, name, body, target_commitish, prerelease)
    else:
        print(f"Updating Gitee release {tag_name}", flush=True)
        release_id = release.get("id")
        if release_id is None:
            raise GiteeApiError(f"Gitee release {tag_name} does not include an id")
        release = client.update_release(release_id, tag_name, name, body)

    release_id = release.get("id")
    if release_id is None:
        raise GiteeApiError(f"Gitee release {tag_name} does not include an id")

    def find_existing_asset(name: str) -> dict[str, Any] | None:
        for asset in client.list_assets(release_id):
            if asset_name(asset) == name:
                return asset
        return None

    for asset_path in asset_paths:
        for attempt in range(1, max_upload_attempts + 1):
            existing = find_existing_asset(asset_path.name)
            if existing is not None:
                asset_id = existing.get("id")
                if asset_id is None:
                    raise GiteeApiError(f"Existing Gitee asset {asset_path.name} does not include an id")
                print(
                    f"Replacing Gitee release asset {asset_path.name} "
                    f"({asset_path.stat().st_size} bytes)",
                    flush=True,
                )
                client.delete_asset(release_id, asset_id)
            else:
                print(
                    f"Uploading Gitee release asset {asset_path.name} "
                    f"({asset_path.stat().st_size} bytes)",
                    flush=True,
                )

            try:
                client.upload_asset(release_id, asset_path)
                print(f"Uploaded Gitee release asset {asset_path.name}", flush=True)
                break
            except GiteeApiError:
                if attempt >= max_upload_attempts:
                    raise
                delay_seconds = attempt * 15
                print(
                    f"Upload attempt {attempt} failed for {asset_path.name}; "
                    f"retrying in {delay_seconds} seconds",
                    flush=True,
                )
                time.sleep(delay_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True, help="Gitee repository owner")
    parser.add_argument("--repo", required=True, help="Gitee repository name")
    parser.add_argument("--tag", required=True, help="Release tag, for example v2.5.0")
    parser.add_argument("--name", required=True, help="Release display name")
    parser.add_argument("--body-file", required=True, help="Markdown release notes file")
    parser.add_argument("--target-commitish", default="main", help="Target branch or commit for a new release")
    parser.add_argument("--prerelease", action="store_true", help="Mark the Gitee release as prerelease")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=900,
        help="Per-request timeout for the Gitee API",
    )
    parser.add_argument("--assets", nargs="+", required=True, help="Release asset files to upload")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = os.environ.get("GITEE_ACCESS_TOKEN")
    if not token:
        raise SystemExit("GITEE_ACCESS_TOKEN is required")

    body_path = Path(args.body_file)
    if not body_path.is_file():
        raise SystemExit(f"Release notes file does not exist: {body_path}")
    body = body_path.read_text(encoding="utf-8")
    asset_paths = collect_asset_paths(args.assets)

    client = GiteeClient(args.owner, args.repo, token, timeout_seconds=args.timeout_seconds)
    sync_release(
        client=client,
        tag_name=args.tag,
        name=args.name,
        body=body,
        target_commitish=args.target_commitish,
        prerelease=args.prerelease,
        asset_paths=asset_paths,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
