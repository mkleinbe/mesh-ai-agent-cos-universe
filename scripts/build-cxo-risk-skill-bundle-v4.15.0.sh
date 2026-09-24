#!/usr/bin/env bash
set -euo pipefail

VERSION=4.15.0
ROOT="dist/cxo-risk-skill-bundle/v${VERSION}"
ZIP="dist/mesh-cxo-risk-skills-v${VERSION}.zip"
CHECKSUM="${ZIP}.sha256"
SOURCE_COMMIT="${GITHUB_SHA:-UNKNOWN}"

SKILLS=(mesh-cro mesh-cfo mesh-coo mesh-cmo)

rm -rf "$ROOT"
rm -f "$ZIP" "$CHECKSUM"
mkdir -p "$ROOT/skills" "$ROOT/scripts"

for skill in "${SKILLS[@]}"; do
  src="chatgpt/skills/${skill}"
  test -d "$src"
  cp -R "$src" "$ROOT/skills/${skill}"
done

cp contracts/executive-risk.v1.schema.json "$ROOT/executive-risk.v1.schema.json"
cp contracts/executive-risk.v2.schema.json "$ROOT/executive-risk.v2.schema.json"
cp scripts/cxo_risk_router.py "$ROOT/scripts/cxo_risk_router.py"
cp docs/release-v4.15.0-cxo-risk.md "$ROOT/RELEASE.md"

cat > "$ROOT/MANIFEST.txt" <<EOF
release=v${VERSION}
source_repository=mkleinbe/mesh-ai-agent-cos-universe
source_commit=${SOURCE_COMMIT}
skill_count=4
skills=mesh-cro mesh-cfo mesh-coo mesh-cmo
shared_contract=mesh.executive-risk.v2
compatibility_contract=mesh.executive-risk.v1
risk_router=scripts/cxo_risk_router.py
acceptance_principal=QUALIFIED_HUMAN
installation_mode=human_controlled_skill_update
qnap_runtime_change=false
canonical_runtime_contract=4.0.0
qnap_deployment_release=4.4.2
EOF

(
  cd "$(dirname "$ROOT")"
  zip -qr "../$(basename "$ZIP")" "$(basename "$ROOT")"
)
(
  cd dist
  sha256sum "$(basename "$ZIP")" > "$(basename "$CHECKSUM")"
)

echo "bundle=$ZIP"
echo "checksum=$CHECKSUM"
