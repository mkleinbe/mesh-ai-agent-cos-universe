#!/usr/bin/env bash
set -euo pipefail

VERSION=4.15.1
SKILL=mesh-agentops-controller
SOURCE="chatgpt/skills/${SKILL}"
STAGE="dist/${SKILL}-v${VERSION}"
ZIP="dist/${SKILL}-v${VERSION}.zip"
CHECKSUM="${ZIP}.sha256"
SOURCE_COMMIT="${GITHUB_SHA:-$(git rev-parse HEAD)}"
SOURCE_DATE_EPOCH="$(git show -s --format=%ct "${SOURCE_COMMIT}")"

rm -rf "${STAGE}"
rm -f "${ZIP}" "${CHECKSUM}"

test -f "${SOURCE}/SKILL.md"
test -f "${SOURCE}/agents/openai.yaml"

mkdir -p "${STAGE}"
cp -R "${SOURCE}" "${STAGE}/${SKILL}"

find "${STAGE}/${SKILL}" -exec touch -d "@${SOURCE_DATE_EPOCH}" {} +

(
  cd "${STAGE}"
  find "${SKILL}" -type f -print | LC_ALL=C sort | zip -X -q "../$(basename "${ZIP}")" -@
)

(
  cd dist
  sha256sum "$(basename "${ZIP}")" > "$(basename "${CHECKSUM}")"
)

archive_listing="$(unzip -Z1 "${ZIP}")"
test -n "${archive_listing}"
if printf '%s\n' "${archive_listing}" | grep -Ev '^mesh-agentops-controller/' >/dev/null; then
  echo "archive contains content outside mesh-agentops-controller/" >&2
  exit 1
fi

printf '%s\n' "${archive_listing}" | grep -qx 'mesh-agentops-controller/SKILL.md'
printf '%s\n' "${archive_listing}" | grep -qx 'mesh-agentops-controller/agents/openai.yaml'
printf '%s\n' "${archive_listing}" | grep -qx 'mesh-agentops-controller/references/production-readiness.md'
printf '%s\n' "${archive_listing}" | grep -qx 'mesh-agentops-controller/references/role-contract.md'
printf '%s\n' "${archive_listing}" | grep -qx 'mesh-agentops-controller/scripts/fme_behavior.py'

echo "bundle=${ZIP}"
echo "checksum=${CHECKSUM}"
echo "source_commit=${SOURCE_COMMIT}"
