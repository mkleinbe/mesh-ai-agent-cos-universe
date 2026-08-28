from pathlib import Path

path = Path("src/mesh_cos/mcp_runtime.py")
text = path.read_text()
old = '''        raw_arguments = dict(args.get("arguments", {}))
        if tool_name == "skills.invoke_governed":
            capability = str(raw_arguments.get("capability") or "")
            permitted_capabilities = set(delegation.get("permitted_capabilities", []))
            if capability not in permitted_capabilities:
                raise PermissionError(
                    "Capability not allowed: capability is not explicitly permitted by the canonical delegation"
                )
        owner_args = self._owner_scoped_arguments(
'''
new = '''        raw_arguments = dict(args.get("arguments", {}))
        owner_args = self._owner_scoped_arguments(
'''
if text.count(old) != 1:
    raise SystemExit(f"expected one delegated capability pre-check, found {text.count(old)}")
text = text.replace(old, new, 1)
old_try = '''        try:
            result = self.call_agent(owner_id, tool_name, owner_args)
'''
new_try = '''        try:
            if tool_name == "skills.invoke_governed":
                capability = str(owner_args.get("capability") or "")
                permitted_capabilities = set(delegation.get("permitted_capabilities", []))
                if capability not in permitted_capabilities:
                    raise PermissionError(
                        "Capability not allowed: capability is not explicitly permitted by the canonical delegation"
                    )
            result = self.call_agent(owner_id, tool_name, owner_args)
'''
if text.count(old_try) != 1:
    raise SystemExit(f"expected one owner execution try block, found {text.count(old_try)}")
text = text.replace(old_try, new_try, 1)
path.write_text(text)
