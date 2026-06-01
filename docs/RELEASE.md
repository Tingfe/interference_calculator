# Release Guide / 发布指南

> Gitee sync note: this document is written for the Gitee mirror branch.
> Gitee hosts synchronized source code, tags, and mirrored release assets when
> `GITEE_ACCESS_TOKEN` is configured. Official Windows/macOS binaries are still
> built by GitHub Actions first, then copied to Gitee Releases.
>
> Gitee 同步说明：本文面向 Gitee 镜像分支。Gitee 保存同步后的源码和标签；
> 配置 `GITEE_ACCESS_TOKEN` 后也会保存镜像后的发行版附件。Windows/macOS 正式
> 安装包仍先由 GitHub Actions 构建，再复制到 Gitee Releases。

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
- `CHANGELOG.md` contains a matching `## [X.Y.Z]` section with English and
  Chinese release notes.

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

When `GITEE_ACCESS_TOKEN` is configured, the same workflow also syncs the
release tag, release notes, and all built assets to the Gitee repository
release page. This sync happens after the GitHub Release succeeds, so Gitee
receives the exact same build outputs instead of rebuilding them separately.

## 自动发布内容

每个版本标签会生成一个 GitHub Release，包含：

- 源码包（`.tar.gz`）；
- Python wheel（`.whl`）；
- Windows 免安装目录版应用（`InterferenceCalculator-Windows-vX.Y.Z.zip`）；
- macOS 磁盘映像（配置签名时为 `InterferenceCalculator-macOS-vX.Y.Z.dmg`；
  未配置 Apple 签名 secrets 时为
  `InterferenceCalculator-macOS-unsigned-vX.Y.Z.dmg`）；
- 从 `CHANGELOG.md` 当前版本段落自动提取的中英文更新日志。

配置 `GITEE_ACCESS_TOKEN` 后，同一个 workflow 还会把发布标签、发布说明和所有
构建产物同步到 Gitee 仓库的发行版页面。该同步步骤发生在 GitHub Release 成功
之后，因此 Gitee 得到的是同一套构建产物，而不是重新构建出的另一套文件。

## Gitee Release Sync

To enable Gitee release sync, configure this GitHub repository secret:

- `GITEE_ACCESS_TOKEN`: a Gitee personal access token that can push tags and
  create/update releases for `tyongs/interference_calculator`.

The workflow uses `tyongs` as the default Gitee HTTPS username. If the token
belongs to another Gitee account with write access, configure a GitHub
repository variable named `GITEE_USERNAME`.

If `GITEE_ACCESS_TOKEN` is missing, the workflow publishes the GitHub Release
normally and logs a warning that Gitee sync was skipped.

Existing GitHub Releases can be mirrored manually with the
`Sync Gitee Release` workflow. Run it from GitHub Actions and provide the
existing tag name, such as `v2.5.0`. The workflow downloads the current GitHub
Release notes and assets, pushes the same tag to Gitee, and uploads the assets
to the matching Gitee Release.

## Gitee 发行版同步

如需启用 Gitee 发行版同步，需要在 GitHub 仓库中配置以下 secret：

- `GITEE_ACCESS_TOKEN`：可向 `tyongs/interference_calculator` 推送标签并
  创建 / 更新发行版的 Gitee 私人令牌。

workflow 默认使用 `tyongs` 作为 Gitee HTTPS 用户名。如果该令牌属于另一个具有
写权限的 Gitee 账号，请额外配置 GitHub repository variable：
`GITEE_USERNAME`。

如果没有配置 `GITEE_ACCESS_TOKEN`，workflow 会正常发布 GitHub Release，并输出
一条 Gitee 同步已跳过的 warning。

已有的 GitHub Release 可以通过 `Sync Gitee Release` workflow 手动镜像。进入
GitHub Actions 后运行该 workflow，并填写已有标签名，例如 `v2.5.0`。workflow
会下载当前 GitHub Release 的发布说明和附件，把同一标签推送到 Gitee，并上传到
对应的 Gitee 发行版。

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

5. Push `main`, then push the version tag. The tag-triggered workflow publishes
   GitHub Release first, then syncs the same artifacts to Gitee when configured.

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

5. 推送 `main`，然后推送版本标签。标签触发的 workflow 会先发布 GitHub Release；
   如果已配置 Gitee 同步，则继续把同一套产物同步到 Gitee。

## Notes About Unsigned Apps

The Windows app is currently unsigned. The macOS workflow publishes an unsigned,
non-notarized DMG when Apple signing secrets are missing; Gatekeeper may block
it after download. When the macOS secrets are configured, the workflow signs and
notarizes the DMG automatically.

## 关于未签名应用

当前 Windows 应用未做代码签名。macOS workflow 在缺少 Apple 签名 secrets 时会
发布未签名、未公证的 DMG，下载后可能被 Gatekeeper 拦截；配置完整 macOS
secrets 后，workflow 会自动签名并公证 DMG。
