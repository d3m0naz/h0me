#!/bin/sh
# Veröffentlicht site/ auf GitHub Pages (Branch gh-pages).
# Vorher committen. Aufruf: sh tools/deploy.sh
set -e
cd "$(dirname "$0")/.."
git push origin main
git branch -f gh-pages "$(git subtree split --prefix site)"
git push -f origin gh-pages
