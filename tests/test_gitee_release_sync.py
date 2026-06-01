from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "sync_gitee_release.py"
SPEC = importlib.util.spec_from_file_location("sync_gitee_release", SCRIPT_PATH)
sync_gitee_release = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(sync_gitee_release)


class FakeGiteeClient:
    def __init__(self, release=None, assets=None, upload_failures=0):
        self.release = release
        self.assets = assets or []
        self.upload_failures = upload_failures
        self.created = []
        self.updated = []
        self.deleted = []
        self.uploaded = []

    def find_release_by_tag(self, tag_name):
        return self.release if self.release and self.release.get("tag_name") == tag_name else None

    def create_release(self, tag_name, name, body, target_commitish, prerelease):
        self.created.append((tag_name, name, body, target_commitish, prerelease))
        self.release = {"id": 9, "tag_name": tag_name}
        return self.release

    def update_release(self, release_id, tag_name, name, body):
        self.updated.append((release_id, tag_name, name, body))
        return {"id": release_id, "tag_name": tag_name}

    def list_assets(self, release_id):
        return self.assets

    def delete_asset(self, release_id, asset_id):
        self.deleted.append((release_id, asset_id))

    def upload_asset(self, release_id, asset_path):
        if self.upload_failures:
            self.upload_failures -= 1
            raise sync_gitee_release.GiteeApiError("temporary upload failure")
        self.uploaded.append((release_id, asset_path.name))
        return {"id": len(self.uploaded), "name": asset_path.name}


class GiteeReleaseSyncTests(unittest.TestCase):
    def test_collect_asset_paths_sorts_by_size_then_file_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            beta = root / "b.zip"
            alpha = root / "a.whl"
            beta.write_text("beta", encoding="utf-8")
            alpha.write_text("alpha", encoding="utf-8")

            assets = sync_gitee_release.collect_asset_paths([str(beta), str(alpha)])

        self.assertEqual([asset.name for asset in assets], ["b.zip", "a.whl"])

    def test_filter_asset_paths_by_size_skips_large_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            small = root / "small.whl"
            large = root / "large.zip"
            small.write_bytes(b"123")
            large.write_bytes(b"123456")

            with redirect_stdout(io.StringIO()):
                assets = sync_gitee_release.filter_asset_paths_by_size([small, large], max_asset_bytes=3)

        self.assertEqual([asset.name for asset in assets], ["small.whl"])

    def test_sync_release_creates_missing_release_and_uploads_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "app.zip"
            asset.write_text("payload", encoding="utf-8")
            client = FakeGiteeClient()

            with redirect_stdout(io.StringIO()):
                sync_gitee_release.sync_release(
                    client=client,
                    tag_name="v2.6.0",
                    name="Interference Calculator v2.6.0",
                    body="notes",
                    target_commitish="main",
                    prerelease=False,
                    asset_paths=[asset],
                )

        self.assertEqual(client.created, [("v2.6.0", "Interference Calculator v2.6.0", "notes", "main", False)])
        self.assertEqual(client.uploaded, [(9, "app.zip")])

    def test_sync_release_replaces_same_named_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "app.zip"
            asset.write_text("payload", encoding="utf-8")
            client = FakeGiteeClient(
                release={"id": 7, "tag_name": "v2.6.0"},
                assets=[{"id": 42, "name": "app.zip"}],
            )

            with redirect_stdout(io.StringIO()):
                sync_gitee_release.sync_release(
                    client=client,
                    tag_name="v2.6.0",
                    name="Interference Calculator v2.6.0",
                    body="notes",
                    target_commitish="main",
                    prerelease=False,
                    asset_paths=[asset],
                )

        self.assertEqual(client.updated, [(7, "v2.6.0", "Interference Calculator v2.6.0", "notes")])
        self.assertEqual(client.deleted, [(7, 42)])
        self.assertEqual(client.uploaded, [(7, "app.zip")])

    def test_sync_release_retries_upload_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "app.zip"
            asset.write_text("payload", encoding="utf-8")
            client = FakeGiteeClient(
                release={"id": 7, "tag_name": "v2.6.0"},
                upload_failures=1,
            )

            with redirect_stdout(io.StringIO()), mock.patch.object(sync_gitee_release.time, "sleep"):
                sync_gitee_release.sync_release(
                    client=client,
                    tag_name="v2.6.0",
                    name="Interference Calculator v2.6.0",
                    body="notes",
                    target_commitish="main",
                    prerelease=False,
                    asset_paths=[asset],
                )

        self.assertEqual(client.uploaded, [(7, "app.zip")])


if __name__ == "__main__":
    unittest.main()
