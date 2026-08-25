#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a consistent online backup of the canonical Mesh SQLite TaskLedger")
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    args = parser.parse_args()
    source = Path(args.source)
    destination = Path(args.destination)
    if not source.is_file():
        raise SystemExit("source ledger does not exist")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise SystemExit("destination already exists")

    src = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    dst = sqlite3.connect(destination)
    try:
        src.backup(dst)
        row = dst.execute("PRAGMA integrity_check").fetchone()
        if not row or row[0] != "ok":
            raise SystemExit("backup integrity check failed")
    finally:
        dst.close()
        src.close()

    print(json.dumps({"ok": True, "backup": str(destination), "sha256": sha256(destination)}, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
