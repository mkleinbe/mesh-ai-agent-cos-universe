from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ACTIVE_QNAP_DOCS = (
    "deployment/qnap/README-QNAP.md",
    "deployment/qnap/DEPLOYMENT-STEPS.md",
    "deployment/qnap/install-checklist.md",
    "deployment/qnap/upgrade-checklist.md",
    "deployment/qnap/CHATGPT-ACCEPTANCE.md",
    "deployment/qnap/.env.example",
)


def test_active_qnap_operator_docs_are_aligned_to_v441() -> None:
    for relative in ACTIVE_QNAP_DOCS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "4.3.0" not in text, relative
        assert "v4.3.0" not in text, relative
        assert "4.4.1" in text, relative


def test_current_qnap_commands_reference_exact_v441_asset_and_release_dir() -> None:
    steps = (ROOT / "deployment/qnap/DEPLOYMENT-STEPS.md").read_text(encoding="utf-8")
    assert "mesh-cos-mcp-qnap-v4.4.1.zip" in steps
    assert "mesh-cos-mcp-qnap-v4.4.1.zip.sha256" in steps
    assert "sudo sh ./v4.4.1/mesh-cos-mcp-deploy.sh" in steps

    env = (ROOT / "deployment/qnap/.env.example").read_text(encoding="utf-8")
    assert "MESH_COS_DEPLOYMENT_RELEASE=4.4.1" in env
    assert "MESH_COS_IMAGE=mesh-cos-mcp:qnap-v4.4.1-SOURCE_SHA12" in env
