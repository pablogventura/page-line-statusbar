#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OXT_SRC="${ROOT}/oxt"
DIST="${ROOT}/dist"
NAME="foja"
VERSION="$(sed -n 's/.*<version value="\([^"]*\)".*/\1/p' "${OXT_SRC}/description.xml" | head -1)"
OUT="${DIST}/${NAME}.oxt"

mkdir -p "${DIST}"
rm -f "${OUT}"

STAGE="$(mktemp -d)"
cleanup() {
  rm -rf "${STAGE}"
}
trap cleanup EXIT

cp -a "${OXT_SRC}/." "${STAGE}/"
cp "${ROOT}/LICENSE" "${STAGE}/LICENSE"
find "${STAGE}" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "${STAGE}" -type f -name '*.pyc' -delete

(
  cd "${STAGE}"
  zip -qr "${OUT}" .
)

echo "Built ${OUT} (version ${VERSION})"
