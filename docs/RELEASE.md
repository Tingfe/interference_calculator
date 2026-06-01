# Release Guide / 发布指南

> Gitee sync note: this document is written for the Gitee mirror branch.
> Gitee hosts synchronized source code, tags, release notes, source
> distributions, and wheels when `GITEE_ACCESS_TOKEN` is configured. Official
> Windows/macOS binaries are still built and hosted by GitHub Actions /
> GitHub Releases, then linked from Gitee Releases.
>
> Gitee 同步说明：本文面向 Gitee 镜像分支。Gitee 保存同步后的源码和标签；
> 配置 `GITEE_ACCESS_TOKEN` 后也会保存发行版说明、源码包和 wheel。Windows/macOS
> 正式安装包仍由 GitHub Actions / GitHub Releases 构建和托管，并在 Gitee
> Releases 中提供链接。

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
- `CHANGELOG.md` contains a matching `## [X.Y.Z]` section with Chinese and
  English release notes.

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
- `CHANGELOG.md` 中存在对应的 `## [X.Y.Z]` 版本段落，并包含中文和英文更新日志。

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
release tag, release notes, source distribution, and wheel to the Gitee
repository release page. Windows and macOS standalone installers remain hosted
on GitHub Releases and are linked from the Gitee release notes, avoiding
unstable large-file uploads through the Gitee API.

## 自动发布内容

每个版本标签会生成一个 GitHub Release，包含：

- 源码包（`.tar.gz`）；
- Python wheel（`.whl`）；
- Windows 免安装目录版应用（`InterferenceCalculator-Windows-vX.Y.Z.zip`）；
- macOS 磁盘映像（配置签名时为 `InterferenceCalculator-macOS-vX.Y.Z.dmg`；
  未配置 Apple 签名 secrets 时为
  `InterferenceCalculator-macOS-unsigned-vX.Y.Z.dmg`）；
- 从 `CHANGELOG.md` 当前版本段落自动提取的中英文更新日志。

配置 `GITEE_ACCESS_TOKEN` 后，同一个 workflow 还会把发布标签、发布说明、源码包
和 wheel 同步到 Gitee 仓库的发行版页面。Windows 与 macOS 免安装程序仍托管在
GitHub Releases，并在 Gitee 发行版说明中提供链接，以避免 Gitee API 大文件上传
不稳定。

## Gitee Release Sync

To enable Gitee release sync, configure this GitHub repository secret:

- `GITEE_ACCESS_TOKEN`: a Gitee personal access token that can push tags and
  create/update releases for `tyongs/interference_calculator`.

The workflow uses `tyongs` as the default Gitee HTTPS username. If the token
belongs to another Gitee account with write access, configure a GitHub
repository variable named `GITEE_USERNAME`.

If `GITEE_ACCESS_TOKEN` is missing, the workflow publishes the GitHub Release
normally and logs a warning that Gitee sync was skipped.

Existing GitHub Releases can be mirrored manually with the `Sync Gitee Release`
workflow. Run it from GitHub Actions and provide the existing tag name, such as
`v2.5.0`. By default, the workflow uploads only the source distribution and
wheel, then links Windows/macOS installers to GitHub Releases. Enable the
`include_large_installers` option only when deliberately testing large Gitee
attachment uploads.

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
GitHub Actions 后运行该 workflow，并填写已有标签名，例如 `v2.5.0`。默认情况下，
workflow 只上传源码包和 wheel，并在 Gitee 发行版中链接 Windows/macOS 安装包的
GitHub Releases 地址。只有在明确测试 Gitee 大附件上传时，才启用
`include_large_installers` 选项。

## Gitee-Native Release Path

Gitee can also publish its own domestic release from the Gitee repository
pipeline. This path is intentionally limited to source distribution and wheel
assets unless dedicated Windows/macOS Gitee runners are configured.

Use this mode when GitHub access is slow or unreliable for domestic users:

1. Push the same version tag to the Gitee repository, for example `v2.5.0`.
2. Let the Gitee pipeline build and test the package from that tag.
3. The pipeline creates or updates the Gitee Release, uploads `.tar.gz` and
   `.whl` assets, and appends a link to the matching GitHub Release for
   Windows/macOS installers.

This does not conflict with GitHub Releases because both repositories use the
same tag name, package version, and `CHANGELOG.md` section. GitHub remains the
canonical desktop-app build source; Gitee provides a domestic mirror and
Python-package release surface.

An experimental Gitee-side Windows zip build is available through the shared
`packaging/windows/build_windows_zip.py` helper. It can only produce a real
Windows package when the Gitee pipeline runs on a Windows-capable executor. If
the pipeline runs on Gitee's default Linux/Python build environment, the
Windows build path must skip and the Gitee release should continue to link to
the GitHub Windows installer.

To enable the Gitee-native release pipeline, configure `GITEE_ACCESS_TOKEN` as
a protected variable/secret in Gitee Go for this repository. The token must be
allowed to create/update releases and upload release attachments for
`tyongs/interference_calculator`.

## Gitee 自行发布路径

Gitee 也可以通过 Gitee 仓库自己的流水线发布国内发行版。这个路径默认只发布源码包
和 wheel；除非后续配置专用的 Windows/macOS Gitee runner，否则不在 Gitee 侧重新
构建桌面安装包。

当国内用户访问 GitHub 较慢或不稳定时，可以使用这个模式：

1. 将同一个版本标签推送到 Gitee 仓库，例如 `v2.5.0`。
2. Gitee 流水线基于该标签构建并测试 Python 包。
3. 流水线创建或更新 Gitee Release，上传 `.tar.gz` 和 `.whl` 附件，并在发布说明
   中附加对应 GitHub Release 的 Windows/macOS 安装包链接。

这不会与 GitHub Release 冲突，因为两个仓库使用相同的标签名、包版本号和
`CHANGELOG.md` 版本段落。GitHub 仍是正式桌面应用构建来源；Gitee 提供国内镜像
和 Python 包发行入口。

项目同时提供实验性的 Gitee 侧 Windows `.zip` 打包辅助脚本：
`packaging/windows/build_windows_zip.py`。只有当 Gitee 流水线运行在可执行 Windows
构建的环境中时，它才能生成真正的 Windows 安装包；如果流水线运行在 Gitee 默认的
Linux/Python 构建环境中，则该路径应明确跳过，Gitee Release 继续链接到 GitHub 的
Windows 安装包。

启用 Gitee 自行发布流水线时，需要在该 Gitee 仓库的 Gitee Go 变量 / secret 中配置
`GITEE_ACCESS_TOKEN`。该令牌需要具备为 `tyongs/interference_calculator` 创建 / 更新
发行版并上传附件的权限。

## Release Checklist

Before tagging:

1. Update `interference_calculator/__init__.py`.
2. Add a new top section to `CHANGELOG.md` with Chinese notes first and English
   notes second.
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
2. 在 `CHANGELOG.md` 顶部新增版本段落，并按中文在前、英文在后的顺序写入更新日志。
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
