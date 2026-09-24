#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/"contracts/executive-risk.v1.schema.json").read_text())

def main()->int:
    if len(sys.argv)!=2:
        print("usage: validate-executive-risk.py risk.json")
        return 2
    data=json.loads(Path(sys.argv[1]).read_text())
    errors=sorted(Draft202012Validator(SCHEMA).iter_errors(data),key=lambda e:list(e.path))
    if errors:
        print("INVALID")
        for error in errors:
            print("- "+error.message)
        return 1
    print("VALID mesh.executive-risk.v1")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
