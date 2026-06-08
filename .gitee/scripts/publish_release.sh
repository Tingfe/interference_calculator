#!/bin/sh
set -eu

if [ -z "${GITEE_ACCESS_TOKEN:-}" ]; then
  echo "GITEE_ACCESS_TOKEN is required in Gitee Go variables/secrets." >&2
  exit 1
fi

TAG_NAME="${GITEE_REF_NAME:-${CI_COMMIT_REF_NAME:-${GITEE_BRANCH:-}}}"
case "$TAG_NAME" in
  refs/tags/*) TAG_NAME="${TAG_NAME#refs/tags/}" ;;
esac

if [ -z "$TAG_NAME" ]; then
  TAG_NAME="$(git describe --tags --exact-match 2>/dev/null || true)"
fi

case "$TAG_NAME" in
  v*) ;;
  *)
    echo "Release pipeline must run on a vX.Y.Z tag, got '${TAG_NAME}'." >&2
    exit 1
    ;;
esac

VERSION="${TAG_NAME#v}"
BODY_FILE="release/release_body.md"

python3 .gitee/scripts/prepare_release_notes.py "$VERSION" "$BODY_FILE"

cat >> "$BODY_FILE" <<EOF

## Desktop Installers / 桌面安装包

Python packages are attached to this Gitee release. The Windows zip may also be
attached if the experimental Gitee Windows pipeline runs on a Windows-capable
executor. macOS installers, and Windows fallback downloads, remain available
from the canonical GitHub release:
https://github.com/Tingfe/interference_calculator/releases/tag/$TAG_NAME

Python 安装包会附加到本 Gitee 发行版。如果实验性的 Gitee Windows 流水线运行在
可执行 Windows 构建的环境中，Windows zip 也可能直接附加在这里。macOS 安装包以及
Windows 备用下载仍以正式 GitHub Release 为准：
https://github.com/Tingfe/interference_calculator/releases/tag/$TAG_NAME
EOF

python3 .github/scripts/sync_gitee_release.py \
  --owner tyongs \
  --repo interference_calculator \
  --tag "$TAG_NAME" \
  --name "Interference Calculator $TAG_NAME" \
  --body-file "$BODY_FILE" \
  --target-commitish main \
  --max-asset-bytes "${GITEE_MAX_ASSET_BYTES:-10485760}" \
  --assets dist/*
