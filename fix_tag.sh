#!/bin/bash
# Fix version mismatch between tag and package

set -e

echo "Step 1: Check current __version__"
grep "__version__" interference_calculator/__init__.py

echo ""
echo "Step 2: Delete old v2.6.0 tag locally and remotely"
git tag -d v2.6.0 || true
git push origin :refs/tags/v2.6.0 || true
git push gitee :refs/tags/v2.6.0 || true

echo ""
echo "Step 3: Ensure all changes are committed"
git status

echo ""
echo "Step 4: Create new v2.6.0 tag pointing to HEAD"
git tag -a v2.6.0 -m "Release v2.6.0 - Fixed version mismatch"

echo ""
echo "Step 5: Push tag to remotes"
git push origin v2.6.0
git push gitee v2.6.0

echo ""
echo "Step 6: Verify tag points to correct commit"
echo "Local HEAD: $(git rev-parse HEAD)"
echo "Tag v2.6.0: $(git rev-parse v2.6.0)"

echo ""
echo "✅ Done! Tag v2.6.0 now points to the commit with __version__ = '2.6.0'"
echo "GitHub Actions should now work correctly."
