#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from mesh_cos.ledger import TaskLedger
from mesh_cos.preflight import ProductionPreflight

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Mesh CoS production activation readiness")
    parser.add_argument("--require-slack", action="store_true", help="Require Agent Ops Slack credentials and channel")
    parser.add_argument("--require-answer-desk", action="store_true", help="Require the dedicated Answer Desk Slack channel")
    parser.add_argument("--require-ledger", action="store_true", help="Require an existing canonical SQLite ledger and verify its audit chain")
    parser.add_argument("--db-path", default=os.getenv("MESH_COS_DB_PATH", ""), help="Existing TaskLedger SQLite path")
    args = parser.parse_args()

    ledger = None
    if args.db_path:
        db_path = Path(args.db_path)
        if db_path.exists():
            ledger = TaskLedger(db_path)
        elif args.require_ledger:
            print(json.dumps({"ready": False, "checks": [{"name": "ledger", "status": "FAIL", "detail": "configured ledger path does not exist"}]}, indent=2))
            return 1
    elif args.require_ledger:
        print(json.dumps({"ready": False, "checks": [{"name": "ledger", "status": "FAIL", "detail": "MESH_COS_DB_PATH or --db-path is required"}]}, indent=2))
        return 1

    result = ProductionPreflight(
        root=ROOT,
        env=os.environ,
        ledger=ledger,
        require_slack=args.require_slack,
        require_answer_desk=args.require_answer_desk,
    ).check()
    print(json.dumps(result, indent=2))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
