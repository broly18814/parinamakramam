#!/usr/bin/env bash
# Publish the GitHub Marketplace copy of the action to its own repository.
#
# Plain words: GitHub's Marketplace lists an action only if its action.yml is at the
# top of a repository of its own. This copies product/action/ (made by build.py) and
# the licence files into github.com/broly18814/parinama-verify-action, saves them
# there as one commit, and tags it with pkv's version (for example v0.2.1).
# Listing it in the Marketplace is then a step for the founder on GitHub's website
# (accepting the Marketplace developer agreement; see product/action/PUBLISHING.md).
#
# Usage, from anywhere in the project, with a clean working tree:
#   scripts/publish-action.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
root="$(pwd)"
ACTION_REPO="https://github.com/broly18814/parinama-verify-action.git"

if [ -n "$(git status --porcelain)" ]; then
  echo "The working tree has uncommitted changes; commit them first." >&2; exit 1
fi
python3 product/action/build.py --check
version="$(python3 -c 'import sys; sys.path.insert(0, "product/action"); import build; print(build.VERSION)')"
tag="v$version"
source_commit="$(git rev-parse HEAD)"

# Use this repository's own sign-in settings for GitHub (the repo-local credential helper).
cred=()
while IFS= read -r helper; do cred+=(-c "credential.https://github.com.helper=$helper"); done \
  < <(git config --get-all credential.https://github.com.helper || true)

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
git "${cred[@]}" clone --quiet "$ACTION_REPO" "$work/action"
cd "$work/action"
git checkout --quiet -B main 2> /dev/null || git symbolic-ref HEAD refs/heads/main   # a new, empty repository
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp "$root/product/action/action.yml" "$root/product/action/README.md" "$root/LICENSE" "$root/NOTICE" .

if git rev-parse --verify --quiet "refs/tags/$tag" > /dev/null; then
  if git diff --quiet "$tag" -- . 2>/dev/null && [ -z "$(git status --porcelain)" ]; then
    echo "$tag is already published with exactly these files; nothing to do."; exit 0
  fi
  echo "$tag already exists with different files. Release a new pkv version instead of changing a tag." >&2
  exit 1
fi

git add -A
git -c user.name="$(git -C "$root" config user.name)" -c user.email="$(git -C "$root" config user.email)" \
  commit --quiet -m "Parinama Verify action $version

Generated from broly18814/parinamakramam at $source_commit
(product/action/, made by product/action/build.py from product/verify/action.yml)."
git tag "$tag"
git "${cred[@]}" push --quiet origin main "refs/tags/$tag"
echo "Published $tag: $(git rev-parse HEAD)"
echo "https://github.com/broly18814/parinama-verify-action/releases/new?tag=$tag"
