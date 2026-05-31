# Release Guide / 发布指南

GitHub Actions builds and publishes releases from version tags.

发布由 GitHub Actions 根据版本标签自动完成。

## Release Trigger

Create and push a tag that matches the package version:

```bash
git tag -a v2.1.0 -m "v2.1.0"
git push origin main
git push origin v2.1.0
```

The release workflow validates that:

- the tag is named `vX.Y.Z`;
- `interference_calculator/__init__.py` contains the same `__version__`;
- `CHANGELOG.md` contains a matching `## [X.Y.Z]` section.

## 发布触发方式

创建并推送与包版本一致的标签：

```bash
git tag -a v2.1.0 -m "v2.1.0"
git push origin main
git push origin v2.1.0
```

发布流程会检查：

- 标签名符合 `vX.Y.Z`；
- `interference_calculator/__init__.py` 中的 `__version__` 与标签一致；
- `CHANGELOG.md` 中存在对应的 `## [X.Y.Z]` 版本段落。

## What The Workflow Publishes

For each release tag, the workflow creates a GitHub Release with:

- source distribution (`.tar.gz`);
- Python wheel (`.whl`);
- Windows standalone executable (`InterferenceCalculator-Windows-vX.Y.Z.exe`);
- macOS disk image (`InterferenceCalculator-macOS-vX.Y.Z.dmg`);
- release notes extracted from the matching `CHANGELOG.md` section.

## 自动发布内容

每个版本标签会生成一个 GitHub Release，包含：

- 源码包（`.tar.gz`）；
- Python wheel（`.whl`）；
- Windows 免安装可执行文件（`InterferenceCalculator-Windows-vX.Y.Z.exe`）；
- macOS 磁盘映像（`InterferenceCalculator-macOS-vX.Y.Z.dmg`）；
- 从 `CHANGELOG.md` 当前版本段落自动提取的更新日志。

## Release Checklist

Before tagging:

1. Update `interference_calculator/__init__.py`.
2. Add a new top section to `CHANGELOG.md`.
3. Update README / manual version references if needed.
4. Run tests locally:

```bash
.venv/bin/python -m unittest discover -s tests -v
git diff --check
```

5. Push `main`, then push the version tag.

## 发布前检查清单

打标签前：

1. 更新 `interference_calculator/__init__.py`。
2. 在 `CHANGELOG.md` 顶部新增版本段落。
3. 必要时更新 README / 用户手册里的版本说明。
4. 本地运行测试：

```bash
.venv/bin/python -m unittest discover -s tests -v
git diff --check
```

5. 推送 `main`，然后推送版本标签。

## Notes About Unsigned Apps

The generated Windows and macOS apps are currently unsigned. Windows SmartScreen
or macOS Gatekeeper may warn on first launch. Code signing and notarization can
be added later when signing certificates are available.

## 关于未签名应用

当前自动生成的 Windows 和 macOS 软件未做代码签名。首次运行时，Windows
SmartScreen 或 macOS Gatekeeper 可能会提示风险。后续取得签名证书后，可以在
发布流程中加入代码签名和 macOS notarization。
