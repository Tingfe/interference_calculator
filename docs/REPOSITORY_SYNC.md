# Repository Sync / 双仓库同步

The project is maintained in two public repositories:

- GitHub: `https://github.com/Tingfe/interference_calculator`
- Gitee: `https://gitee.com/tyongs/interference_calculator`

本项目同时维护两个公开仓库：

- GitHub：`https://github.com/Tingfe/interference_calculator`
- Gitee：`https://gitee.com/tyongs/interference_calculator`

## Policy

GitHub remains the canonical release repository. GitHub Actions builds the
Windows package, macOS DMG, source distribution, wheel, and GitHub Release notes
from version tags.

Gitee mirrors source code, release tags, release notes, and release assets for
easier access in China, but its documentation may intentionally use Gitee
repository links and Gitee-specific notes. Do not force-push GitHub `main`
directly over Gitee `main`.

## 规则

GitHub 仍是正式发布仓库。GitHub Actions 会根据版本标签构建 Windows 程序、
macOS DMG、源码包、wheel 和 GitHub Release 更新日志。

Gitee 用于同步源码、版本标签、发布说明和发布附件，方便国内访问；但 Gitee
文档可以有意使用 Gitee 仓库链接和 Gitee 专属说明。不要把 GitHub 的 `main`
强制覆盖到 Gitee 的 `main`。

## Normal Sync Flow

After a new change is merged or committed to GitHub `main`:

```bash
git switch main
git status --short --branch
git push origin main
```

Then update the Gitee presentation branch from the latest Gitee `main` and merge
the GitHub changes into it:

```bash
git fetch origin --prune
git fetch gitee --prune
git switch codex/gitee-docs
git merge --no-ff origin/main
git push gitee codex/gitee-docs:main
git switch main
```

If a release tag is created, push the tag to GitHub to trigger the release
workflow:

```bash
git push origin vX.Y.Z
```

When `GITEE_ACCESS_TOKEN` is configured in GitHub Secrets, the GitHub release
workflow pushes the same tag to Gitee and uploads the already-built GitHub
Release assets to the Gitee release page. This keeps Windows, macOS, wheel, and
source-package downloads identical across both repositories.

## 常规同步流程

当新的代码或文档变更进入 GitHub `main` 后：

```bash
git switch main
git status --short --branch
git push origin main
```

然后基于最新的 Gitee `main` 更新 Gitee 展示分支，并把 GitHub 变更合入：

```bash
git fetch origin --prune
git fetch gitee --prune
git switch codex/gitee-docs
git merge --no-ff origin/main
git push gitee codex/gitee-docs:main
git switch main
```

如果创建了发布标签，推送 GitHub 标签即可触发发布 workflow：

```bash
git push origin vX.Y.Z
```

当 GitHub Secrets 中已配置 `GITEE_ACCESS_TOKEN` 时，GitHub 发布 workflow 会把同一
个标签推送到 Gitee，并把 GitHub Release 已经构建完成的附件上传到 Gitee 发行版
页面。这样两个仓库中的 Windows、macOS、wheel 和源码包下载文件保持完全一致。

## Conflict Rule

When conflicts occur, keep product code, tests, packaging metadata, changelog,
and shared documentation aligned with GitHub `main`. Keep repository URLs,
download guidance, and platform-specific repository notes appropriate for the
target repository.

## 冲突处理原则

如果发生冲突，产品代码、测试、打包元数据、更新日志和通用文档应与 GitHub
`main` 保持一致；仓库链接、下载指引和仓库平台相关说明应按目标仓库分别保留。
