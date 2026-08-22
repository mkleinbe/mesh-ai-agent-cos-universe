#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "4.0.0"


def replace_required(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        raise SystemExit(f"required token missing in {path}: {old!r}")
    path.write_text(text.replace(old, new))


replace_required(ROOT / "pyproject.toml", 'version = "3.0.0"', f'version = "{VERSION}"')
replace_required(ROOT / "src" / "mesh_cos" / "__init__.py", '__version__ = "3.0.0"', f'__version__ = "{VERSION}"')

package_path = ROOT / "mcp" / "package.json"
package = json.loads(package_path.read_text())
package["version"] = VERSION
package_path.write_text(json.dumps(package, indent=2) + "\n")

lock_path = ROOT / "mcp" / "package-lock.json"
lock = json.loads(lock_path.read_text())
lock["version"] = VERSION
lock["packages"][""]["version"] = VERSION
lock_path.write_text(json.dumps(lock, indent=2) + "\n")

for path in sorted((ROOT / "chatgpt" / "workspace-agents").glob("*.json")):
    manifest = json.loads(path.read_text())
    manifest["repository_release"] = VERSION
    path.write_text(json.dumps(manifest, indent=2) + "\n")

smoke = ROOT / "mcp" / "scripts" / "smoke-test.mjs"
text = smoke.read_text()
replacements = {
    "assert.equal(agents.length, 9);": "assert.equal(agents.length, 10);",
    "assert.equal(agents.some((agent) => agent.agent_id === 'message-ops'), false);": "assert.equal(agents.some((agent) => agent.agent_id === 'message-ops'), true);",
    "local-mcp-smoke-v3": "local-mcp-smoke-v4",
    "9-agent roster": "10-agent roster",
    "shared-capability principal exclusion": "Devil's Advocate shared-capability principal exclusion",
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"smoke-test token missing: {old}")
    text = text.replace(old, new)
smoke.write_text(text)

print("v4.0.0 release metadata synchronized")
