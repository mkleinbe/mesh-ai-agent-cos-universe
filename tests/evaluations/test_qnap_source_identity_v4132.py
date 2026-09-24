from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_qnap_candidate_image_identity_is_commit_qualified() -> None:
    prepare = read("deployment/qnap/scripts/mesh-cos-mcp-prepare.sh")
    assert 'EXPECTED_COMMIT_SHORT=$(printf' in prepare
    assert 'mesh-cos-mcp:qnap-v${RELEASE_VERSION}-${EXPECTED_COMMIT_SHORT}' in prepare


def test_qnap_deploy_forces_candidate_recreation() -> None:
    deploy = read("deployment/qnap/scripts/mesh-cos-mcp-deploy.sh")
    assert "--force-recreate" in deploy


def test_qnap_verifier_binds_metadata_image_and_mcp_source_commit() -> None:
    verify = read("deployment/qnap/scripts/mesh-cos-mcp-verify.sh")
    assert "EXPECTED_SOURCE_COMMIT=" in verify
    assert "envelope.source_commit!==expectedCommit" in verify
    assert "RUNNING_MESH_REVISION" in verify
    assert 'RUNNING_MESH_REVISION" = "$EXPECTED_SOURCE_COMMIT' in verify


def test_qnap_442_publisher_is_historical_and_v4150_does_not_repackage_qnap() -> None:
    historical = read(".github/workflows/release-v4.13.3.yml")
    current = read(".github/workflows/release-v4.15.0.yml")
    assert "workflow_dispatch:" in historical
    assert "branches: [main]" not in historical
    assert "gh release create" not in historical
    assert "contents: write" not in historical
    assert "gh release create v4.15.0" in current
    assert "mesh-cos-mcp-qnap-v4.4.2.zip" not in current
    assert "mesh-cxo-risk-skills-v4.15.0.zip" in current


def test_active_qnap_docs_do_not_reuse_v440_archive() -> None:
    for path in (
        "deployment/qnap/README-QNAP.md",
        "deployment/qnap/DEPLOYMENT-STEPS.md",
        "deployment/qnap/install-checklist.md",
        "deployment/qnap/upgrade-checklist.md",
        "deployment/qnap/CHATGPT-ACCEPTANCE.md",
    ):
        text = read(path)
        assert "4.4.2" in text
        assert "mesh-cos-mcp-qnap-v4.4.0.zip" not in text
