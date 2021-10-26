#!/bin/bash

# set -x # TO REMOVE

VERSION=$1

set -euo pipefail

request_approval_to_continue() {
    echo
    echo $1
    echo
    echo 'Continue with release? Only "yes" will be accepted to approve.'
    read CONTINUE
    [ "$CONTINUE" == "yes" ] || exit 1
}

show_help () {
    echo Usage: $0 VERSION
    echo
    echo VERSION should ideally be a valid semver string or a valid bump rule: patch, minor, major, prepatch, preminor, premajor, prerelease.
    exit 0
}

show_git_diff_staged() {
    echo
    echo Current staged diff:
    echo
    git diff --staged
}

# Show help if needed
([ "$VERSION" == "-h" ] || [ "$VERSION" == "--help" ] || [ "$VERSION" == "" ]) && show_help

# Ensure we are on master branch (we do not backport fixes for older major versions yet)
[ "$(git rev-parse --abbrev-ref HEAD)" == "master" ] || (echo ERROR: not on "master" branch, aborting. && exit 1)

# Ensure pyproject.toml and CHANGELOG.md do not have unstaged modifications
git diff --exit-code CHANGELOG.md &> /dev/null || (echo ERROR: CHANGELOG.md file has unstaged changes, aborting. && exit 1)
git diff --exit-code pyproject.toml &> /dev/null || (echo ERROR: pyproject.toml file has unstaged changes, aborting. && exit 1)

# Bump the version with poetry and re-read it
poetry version $VERSION
VERSION=$(poetry version --short)

request_approval_to_continue "New version will be: $VERSION"

# Update `CHANGELOG.md` (TODO: generate it from JIRA issue ids?)
sed -i "1 i\# ${VERSION} ($(date +'%Y/%m/%d'))\n\n" CHANGELOG.md
vi CHANGELOG.md
CHANGELOG=$(sed '2,${/^#/Q}' CHANGELOG.md)

git add pyproject.toml CHANGELOG.md
show_git_diff_staged

request_approval_to_continue "Ready to commit"

# Commit these changes
git commit -m "Release v$VERSION"

request_approval_to_continue "Ready to create annotated tag"

# Tag with last CHANGELOG.md item content as annotation
sed '2,${/^#/Q}' CHANGELOG.md | git tag -a -F- v$VERSION

# Bump the version with poetry again to mark it for development
echo
echo Bump the version with poetry again to mark it for development
echo
poetry version prerelease
VERSION=$(poetry version --short)

git add pyproject.toml
show_git_diff_staged

request_approval_to_continue "Ready to commit"

# Commit this changes
git commit -m "Develop v$VERSION"

request_approval_to_continue "Ready to push to all remote repositories. On GitHub, this will trigger a Github Actions job to publish packages to PyPI"

# FIXME: uncomment when ready
# for remote in $(git remote); do git push $remote --follow-tags ; done
