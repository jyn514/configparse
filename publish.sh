#!/usr/bin/env bash
set -e

VERSION_FILE=src/__init__.py
VERSION_VAR=__version__
VERSION_REGEX="\([0-9]\d*\)\.\([0-9]\d*\)\.\([0-9]\d*\)"

case "$1" in
	test) shift; REPO='--repository-url https://test.pypi.org/legacy/';;
	*) REPO= ;;
esac
rm -rf dist

read -r major minor patch < <(sed -n "s/$VERSION_VAR = \"$VERSION_REGEX\"/\1 \2 \3/p" "$VERSION_FILE")
case "$1" in
	major) major=$(( major + 1 ));;
	minor) minor=$(( minor + 1 ));;
	patch|*) patch=$(( patch + 1 ));;
esac
sed -i "s/$VERSION_VAR = \"$VERSION_REGEX\"/$VERSION_VAR = \"$major.$minor.$patch\"/" "$VERSION_FILE"

VERSION="$(grep "$VERSION_VAR" "$VERSION_FILE" | cut -d " " -f 3 | tr -d \")"
git diff "$VERSION_FILE"
echo "does this diff changing the version to $VERSION look right?"
read -r REPLY
[ "$REPLY" = y ] || { echo "aborting"; exit 1; }

git add "$VERSION_FILE"
git commit -m "bump version number to $VERSION"
git tag "$VERSION"
git push --tags && git push

pip install --user --upgrade setuptools twine wheel
python setup.py bdist_wheel sdist
twine upload $REPO dist/*
