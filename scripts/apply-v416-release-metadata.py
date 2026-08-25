#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACTIVE_RELEASE_FILES = [
    "Dockerfile",
    "deployment/qnap/.env.example",
    "deployment/qnap/DEPLOYMENT-STEPS.md",
    "deployment/qnap/upgrade-checklist.md",
    "deployment/qnap/install-checklist.md",
    "deployment/qnap/CHATGPT-ACCEPTANCE.md",
    "deployment/qnap/README-QNAP.md",
    "docs/qnap-production-preflight.md",
    "deployment/qnap/scripts/mesh-cos-mcp-prepare.sh",
    "tests/evaluations/test_qnap_deployment_automation.py",
    "tests/evaluations/test_shared_devils_advocate_integration.py",
    "tests/evaluations/test_shared_message_operations_refactor.py",
]

for relative in ACTIVE_RELEASE_FILES:
    path = ROOT / relative
    text = path.read_text()
    if "4.1.5" not in text and "4.1.6" not in text:
        raise SystemExit(f"expected release identity not found in {relative}")
    path.write_text(text.replace("4.1.5", "4.1.6"))

ci = ROOT / ".github/workflows/ci.yml"
text = ci.read_text().replace("4.1.5", "4.1.6").replace("actions/setup-node@v6", "actions/setup-node@v7")
needle = "            -e MESH_COS_AGENT_ID=cos \\\n            -e MESH_COS_LEDGER_PATH=/var/lib/mesh/ledger/taskledger.sqlite3 \\\n"
replacement = "            -e MESH_COS_AGENT_ID=cos \\\n            -e MESH_COS_DEPLOYMENT_RELEASE=4.1.6 \\\n            -e MESH_COS_LEDGER_PATH=/var/lib/mesh/ledger/taskledger.sqlite3 \\\n"
if needle not in text and replacement not in text:
    raise SystemExit("CI production docker-run identity insertion point not found")
text = text.replace(needle, replacement)
ci.write_text(text)

release = ROOT / ".github/workflows/release-production-readiness.yml"
text = release.read_text().replace("4.1.5", "4.1.6")
text = text.replace(
    "v4.1.6 QNAP Release Identity Preflight Reliability",
    "v4.1.6 Secure MCP Published App Production Identity",
)
release.write_text(text)

print("v4.1.6 active release metadata applied")
