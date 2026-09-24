#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
SCHEMAS={
    "mesh.executive-risk.v1":"executive-risk.v1.schema.json",
    "mesh.executive-risk.v2":"executive-risk.v2.schema.json",
}

def main()->int:
    if len(sys.argv)!=2:
        print("usage: validate-executive-risk.py risk.json")
        return 2
    data=json.loads(Path(sys.argv[1]).read_text())
    schema_name=SCHEMAS.get(data.get("contract_version"))
    if schema_name is None:
        print(f"INVALID unsupported contract: {data.get('contract_version')}")
        return 1
    schema=json.loads((ROOT/"contracts"/schema_name).read_text())
    errors=sorted(Draft202012Validator(schema).iter_errors(data),key=lambda e:list(e.path))
    if errors:
        print("INVALID")
        for error in errors:
            print("- "+error.message)
        return 1
    print(f"VALID {data['contract_version']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
