#!/usr/bin/env bash
set -euo pipefail

VERSION=4.12.0
ROOT="dist/chatgpt-skill-bundle/v\${VERSION}"
ZIP="dist/mesh-cos-chief-of-staff-v\${VERSION}.zip"
CHECKSUM="\${ZIP}.sha256"
SOURCE_COMMIT="\${GITHUB_SHA:-$(git rev-parse HEAD)}"
SOURCE_DATE_EPOCH="$(git show -s --format=%ct "\$SOURCE_COMMIT")"

SKILLS=(
  mesh-chief-of-staff
)

rm -rf "\$ROOT"
rm -f "\$ZIP" "\$CHECKSUM"
mkdir -p "\$ROOT/skills"

for skill in "\${SKILLS[@]}"; do
  src="chatgpt/skills/\${skill}"
  if [ ! -d "\$src" ]; then
    echo "missing required Skill directory: \$src" >&2
    exit 1
  fi
  cp -R "\$src" "\$ROOT/skills/\${skill}"
done

cp docs/skills-v4.12.0.md "\$ROOT/SKILLS-v4.12.0.md"

cat > "\$ROOT/MANIFEST.txt" <<EOF
release=v\${VERSION}
source_repository=mkleinbe/mesh-ai-agent-cos-universe
source_commit=\${SOURCE_COMMIT}
skill_count=\${#SKILLS[@]}
workspace_agent_manifests_included=false
installation_mode=human_controlled_one_skill_at_a_time
agent_execution_model=logical_skill_agent
synchronous_workspace_agent_execution=false
skills=\${SKILLS[*]}
EOF

find "\$ROOT" -exec touch -d "@\${SOURCE_DATE_EPOCH}" {} +
(
  cd "$(dirname "\$ROOT")"
  find "$(basename "\$ROOT")" -type f -print | LC_ALL=C sort | zip -X -q "../$(basename "\$ZIP")" -@
)
(
  cd dist
  sha256sum "$(basename "\$ZIP")" > "$(basename "\$CHECKSUM")"
)
echo "bundle=\$ZIP"
echo "checksum=\$CHECKSUM"
