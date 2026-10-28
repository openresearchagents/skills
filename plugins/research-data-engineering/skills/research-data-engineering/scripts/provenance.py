#!/usr/bin/env python3
"""Write a provenance sidecar (<file>.provenance.json) for a data file.

Records where the file came from, when it was retrieved, and its SHA-256, so a dataset can be
traced back to its source and checked for silent changes. Standard library only.

Example:
    python provenance.py data/raw/dph_2024_report.pdf \
        --source-url https://example.gov/report.pdf --page 14 --table "Table 3" \
        --published 2025-06-30 --note "Provisional 2024 counts"
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", type=pathlib.Path)
    p.add_argument("--source-url", required=True, help="Where the file (or the data in it) came from")
    p.add_argument("--query", help="Exact query, filters or API parameters used to produce the download")
    p.add_argument("--retrieved", help="Retrieval time, ISO 8601 (default: now, UTC)")
    p.add_argument("--published", help="Date the source made these values public, if known")
    p.add_argument("--page", help="Page number(s) in the source document")
    p.add_argument("--table", help="Table or figure identifier in the source")
    p.add_argument("--derived-from", nargs="*", default=[], help="Input files this file was built from")
    p.add_argument("--script", help="Script or command that produced this file")
    p.add_argument("--note", help="Anything else a reader needs (edition, caveats)")
    args = p.parse_args()

    if not args.file.is_file():
        print(f"not a file: {args.file}", file=sys.stderr)
        return 1

    record = {
        "file": args.file.name,
        "sha256": sha256(args.file),
        "bytes": args.file.stat().st_size,
        "source_url": args.source_url,
        "query": args.query,
        "retrieved": args.retrieved or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "published": args.published,
        "page": args.page,
        "table": args.table,
        "derived_from": [
            {"file": str(f), "sha256": sha256(pathlib.Path(f))} if pathlib.Path(f).is_file() else {"file": str(f)}
            for f in args.derived_from
        ],
        "script": args.script,
        "note": args.note,
    }
    record = {k: v for k, v in record.items() if v not in (None, [])}

    out = args.file.with_name(args.file.name + ".provenance.json")
    out.write_text(json.dumps(record, indent=2) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
