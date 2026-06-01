# Release Guide / 发布指南

> Gitee sync note: this document is written for the Gitee mirror branch.
> Gitee hosts synchronized source code and tags. The official Windows/macOS
> binaries are still built by GitHub Actions and published on GitHub Releases.
>
> Gitee 同步说明：本文面向 Gitee 镜像分支。Gitee 保存同步后的源码和标签；
> Windows/macOS 正式安装包仍由 GitHub Actions 构建，并发布到 GitHub Releases。

GitHub Actions builds and publishes releases from version tags.

发布由 GitHub Actions 根据版本标签自动完成。

## Release Trigger

Create and push a tag that matches the package version:

```bash
git tag -a v2.1.0 -m "v2.1.0"
git push origin main
git push origin v2.1.0
git push gitee main
git push gitee v2.1.0
```

The release workflow validates that:

- the tag is named `vX.Y.Z`;
- `interference_calculator/__init__.py` contains the same `__version__`;
- `CHANGELOG.md` contains a matching `## [X.Y.Z]` section with English and
  Chinese release notes.

## 发布触发方式

创建并推送与包版本一致的标签：

```bash
git tag -a v2.1.0 -m "v2.1.0"
git push origin main
git push origin v2.1.0
git push gitee main
git push gitee v2.1.0
```

发布流程会检查：

- 标签名符合 `vX.Y.Z`；
- `interference_calculator/__init__.py` 中的 `__version__` 与标签一致；
- `CHANGELOG.md` 中存在对应的 `## [X.Y.Z]` 版本段落，并包含英文和中文更新日志。

## What The Workflow Publishes

For each release tag, the workflow creates a GitHub Release with:

- source distribution (`.tar.gz`);
- Python wheel (`.whl`);
- Windows standalone app directory (`InterferenceCalculator-Windows-vX.Y.Z.zip`);
- macOS disk image (`InterferenceCalculator-macOS-vX.Y.Z.dmg` when signed, or
  `InterferenceCalculator-macOS-unsigned-vX.Y.Z.dmg` without Apple signing
  secrets);
- bilingual release notes extracted from the matching `CHANGELOG.md` section.

Gitee should receive the same source commit and tag after the GitHub Release is
created. Do not treat the Gitee pipeline templates as the source of the official
binary artifacts unless a separate Gitee build-and-release process is explicitly
configured.

## 自动发布内容

每个版本标签会生成一个 GitHub Release，包含：

- 源码包（`.tar.gz`）；
- Python wheel（`.whl`）；
- Windows 免安装目录版应用（`InterferenceCalculator-Windows-vX.Y.Z.zip`）；
- macOS 磁盘映像（配置签名时为 `InterferenceCalculator-macOS-vX.Y.Z.dmg`；
  未配置 Apple 签名 secrets 时为
  `InterferenceCalculator-macOS-unsigned-vX.Y.Z.dmg`）；
- 从 `CHANGELOG.md` 当前版本段落自动提取的中英文更新日志。

GitHub Release 创建完成后，再把同一个源码提交和标签同步到 Gitee。除非单独配置
Gitee 构建和发布流程，否则不要把 Gitee pipeline 模板视为正式二进制安装包来源。

## Release Checklist

Before tagging:

1. Update `interference_calculator/__init__.py`.
2. Add a new top section to `CHANGELOG.md` with both English and Chinese
   notes.
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
2. 在 `CHANGELOG.md` 顶部新增版本段落，并同时写入英文和中文更新日志。
3. 必要时更新 README / 用户手册里的版本说明。
4. 本地运行测试：

```bash
.venv/bin/python -m unittest discover -s tests -v
git diff --check
```

5. 推送 `main`，然后推送版本标签。

## Notes About Unsigned Apps

The Windows app is currently unsigned. The macOS workflow publishes an unsigned,
non-notarized DMG when Apple signing secrets are missing; Gatekeeper may block
it after download. When the macOS secrets are configured, the workflow signs and
notarizes the DMG automatically.

## 关于未签名应用

当前 Windows 应用未做代码签名。macOS workflow 在缺少 Apple 签名 secrets 时会
发布未签名、未公证的 DMG，下载后可能被 Gatekeeper 拦截；配置完整 macOS
secrets 后，workflow 会自动签名并公证 DMG。
