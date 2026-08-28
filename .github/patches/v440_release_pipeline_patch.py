from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}")
    target.write_text(text.replace(old, new, 1))


replace_once(
    ".github/workflows/release-v4.3.0.yml",
    "on:\n  pull_request:\n    branches: [main]\n  push:\n",
    "on:\n  push:\n",
)

replace_once(
    "scripts/build-qnap-release-bundle.sh",
    "[ -f docs/slack-agent-protocol.md ] && cp docs/slack-agent-protocol.md \"$RELEASE_DIR/cos-mcp/\"\ncp specs/qnap-published-chatgpt-app-v4.1.6.feature",
    """[ -f docs/slack-agent-protocol.md ] && cp docs/slack-agent-protocol.md \"$RELEASE_DIR/cos-mcp/\"\nif [ \"$VERSION\" = \"4.4.0\" ]; then\n  cp CHANGELOG-v4.4.0.md \"$RELEASE_DIR/cos-mcp/\"\n  cp docs/material-turn-v4.4.0.md \"$RELEASE_DIR/cos-mcp/\"\n  cp docs/architecture-v4.4.0-authority-execution.md \"$RELEASE_DIR/cos-mcp/\"\n  cp docs/security-review-v4.4.0-authority-closure.md \"$RELEASE_DIR/cos-mcp/\"\n  cp docs/runbook-v4.4.0-authority-execution.md \"$RELEASE_DIR/cos-mcp/\"\n  cp docs/release-v4.4.0-authority-closure.md \"$RELEASE_DIR/cos-mcp/\"\n  cp docs/chatgpt-published-app-production-acceptance-v4.4.0.md \"$RELEASE_DIR/cos-mcp/\"\n  cp docs/skills-v4.4.0.md \"$RELEASE_DIR/cos-mcp/\"\n  [ -f docs/verification-v4.4.0-authority-closure.md ] && cp docs/verification-v4.4.0-authority-closure.md \"$RELEASE_DIR/cos-mcp/\"\nfi\ncp specs/qnap-published-chatgpt-app-v4.1.6.feature""",
)

replace_once(
    "scripts/build-qnap-release-bundle.sh",
    "fi\n\nchmod +x \"$RELEASE_DIR\"/*.sh \"$RELEASE_DIR/cos-mcp/qnap-environment-probe.sh\"",
    """fi\n\nif [ \"$VERSION\" = \"4.4.0\" ]; then\n  test -f \"$RELEASE_DIR/cos-mcp/CHANGELOG-v4.4.0.md\"\n  test -f \"$RELEASE_DIR/cos-mcp/material-turn-v4.4.0.md\"\n  test -f \"$RELEASE_DIR/cos-mcp/architecture-v4.4.0-authority-execution.md\"\n  test -f \"$RELEASE_DIR/cos-mcp/security-review-v4.4.0-authority-closure.md\"\n  test -f \"$RELEASE_DIR/cos-mcp/runbook-v4.4.0-authority-execution.md\"\n  test -f \"$RELEASE_DIR/cos-mcp/release-v4.4.0-authority-closure.md\"\n  test -f \"$RELEASE_DIR/cos-mcp/chatgpt-published-app-production-acceptance-v4.4.0.md\"\n  test -f \"$RELEASE_DIR/cos-mcp/skills-v4.4.0.md\"\nfi\n\nchmod +x \"$RELEASE_DIR\"/*.sh \"$RELEASE_DIR/cos-mcp/qnap-environment-probe.sh\"""",
)

replace_once(
    ".github/workflows/ci.yml",
    "          bash -n scripts/build-qnap-release-v4.3.0.sh\n",
    "          bash -n scripts/build-qnap-release-v4.3.0.sh\n          bash -n scripts/build-chatgpt-skill-bundle-v4.4.0.sh\n          ! grep -q '^  pull_request:' .github/workflows/release-v4.3.0.yml\n",
)

replace_once(
    ".github/workflows/ci.yml",
    "          bash scripts/build-qnap-release-bundle.sh \"$CANDIDATE_VERSION\"\n          ZIP=\"dist/mesh-cos-mcp-qnap-v${CANDIDATE_VERSION}.zip\"\n",
    """          bash scripts/build-qnap-release-bundle.sh \"$CANDIDATE_VERSION\"\n          bash scripts/build-chatgpt-skill-bundle-v4.4.0.sh\n          ZIP=\"dist/mesh-cos-mcp-qnap-v${CANDIDATE_VERSION}.zip\"\n          SKILL_ZIP=\"dist/mesh-cos-chatgpt-skills-v${CANDIDATE_VERSION}.zip\"\n""",
)

replace_once(
    ".github/workflows/ci.yml",
    "          test -f \"$ZIP\" && test -f \"$ZIP.sha256\"\n          grep -q \"^version=${CANDIDATE_VERSION}$\" \"$BUNDLE/cos-mcp/release-metadata.txt\"\n",
    """          test -f \"$ZIP\" && test -f \"$ZIP.sha256\"\n          test -f \"$SKILL_ZIP\" && test -f \"$SKILL_ZIP.sha256\"\n          grep -q \"^version=${CANDIDATE_VERSION}$\" \"$BUNDLE/cos-mcp/release-metadata.txt\"\n          grep -q \"^source_commit=$GITHUB_SHA$\" dist/chatgpt-skill-bundle/v4.4.0/MANIFEST.txt\n          grep -q '^skill_count=8$' dist/chatgpt-skill-bundle/v4.4.0/MANIFEST.txt\n          grep -q '^agent_execution_model=logical_skill_agent$' dist/chatgpt-skill-bundle/v4.4.0/MANIFEST.txt\n          grep -q '^synchronous_workspace_agent_execution=false$' dist/chatgpt-skill-bundle/v4.4.0/MANIFEST.txt\n""",
)

replace_once(
    ".github/workflows/ci.yml",
    "          (cd dist && sha256sum -c \"mesh-cos-mcp-qnap-v${CANDIDATE_VERSION}.zip.sha256\")\n",
    """          (cd dist && sha256sum -c \"mesh-cos-mcp-qnap-v${CANDIDATE_VERSION}.zip.sha256\")\n          (cd dist && sha256sum -c \"mesh-cos-chatgpt-skills-v${CANDIDATE_VERSION}.zip.sha256\")\n""",
)

replace_once(
    ".github/workflows/ci.yml",
    "            dist/mesh-cos-mcp-qnap-v4.4.0.zip.sha256\n            dist/verification-receipt-current.txt\n",
    """            dist/mesh-cos-mcp-qnap-v4.4.0.zip.sha256\n            dist/mesh-cos-chatgpt-skills-v4.4.0.zip\n            dist/mesh-cos-chatgpt-skills-v4.4.0.zip.sha256\n            dist/verification-receipt-current.txt\n""",
)
