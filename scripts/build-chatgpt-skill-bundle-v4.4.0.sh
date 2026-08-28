#!/usr/bin/env bash
set -euo pipefail

VERSION=4.4.0
ROOT="dist/chatgpt-skill-bundle/v${VERSION}"
ZIP="dist/mesh-cos-chatgpt-skills-v${VERSION}.zip"
CHECKSUM="${ZIP}.sha256"
SOURCE_COMMIT="${GITHUB_SHA:-UNKNOWN}"

SKILLS=(
  mesh-chief-of-staff
  mesh-agentops-controller
  mesh-answer-decision-desk
  mesh-cro
  mesh-cfo
  mesh-coo
  mesh-cmo
  mesh-message-operations
)

rm -rf "$ROOT"
rm -f "$ZIP" "$CHECKSUM"
mkdir -p "$ROOT/skills"

for skill in "${SKILLS[@]}"; do
  src="chatgpt/skills/${skill}"
  if [ ! -d "$src" ]; then
    echo "missing required Skill directory: $src" >&2
    exit 1
  fi
  cp -R "$src" "$ROOT/skills/${skill}"
done

cp docs/skills-v4.4.0.md "$ROOT/SKILLS-v4.4.0.md"

cat > "$ROOT/MANIFEST.txt" <<EOF
release=v${VERSION}
source_repository=mkleinbe/mesh-ai-agent-cos-universe
source_commit=${SOURCE_COMMIT}
skill_count=${#SKILLS[@]}
workspace_agent_manifests_included=false
installation_mode=human_controlled_one_skill_at_a_time
agent_execution_model=logical_skill_agent
synchronous_workspace_agent_execution=false
skills=${SKILLS[*]}
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
