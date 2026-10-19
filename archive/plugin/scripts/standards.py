"""Find, validate and export snow-bi-kit company standards.

    python standards.py check   [--project DIR]          # which file is used, and what's missing
    python standards.py brand   --project DIR            # write DIR/bi_kit_brand.json for the app
    python standards.py get KEY [--project DIR]          # e.g. get access.build_role

Lookup order: DIR/bi-kit/company-standards.yaml, then <kit>/standards/company-standards.yaml.
The example file is never used automatically.
"""

from __future__ import annotations

import json
import os
import sys

import yaml

KIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = [
    "company.name", "company.standards_owner",
    "environments.prototype.database", "environments.prototype.schema_pattern",
    "access.build_role", "compute.warehouse",
    "handoff.receiving_team", "handoff.intake",
]


def find(project: str = ".") -> str | None:
    for p in (os.path.join(project, "bi-kit", "company-standards.yaml"),
              os.path.join(KIT_ROOT, "standards", "company-standards.yaml")):
        if os.path.exists(p):
            return p
    return None


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get(doc: dict, dotted: str):
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def missing(doc: dict) -> list[str]:
    return [k for k in REQUIRED if get(doc, k) in (None, "", [], {})]


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    project = argv[argv.index("--project") + 1] if "--project" in argv else "."
    path = find(project)
    if path is None:
        print("No company standards found. Ask your analytics lead to run setup (bi-kit-setup).")
        return 1
    doc = load(path)

    if cmd == "check":
        gaps = missing(doc)
        print(f"Using: {path}")
        print("Missing required: " + (", ".join(gaps) if gaps else "none"))
        return 1 if gaps else 0
    if cmd == "brand":
        out = os.path.join(project, "bi_kit_brand.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(doc.get("brand") or {}, f, indent=2)
        print(out)
        return 0
    if cmd == "get" and len(argv) > 1:
        print(json.dumps(get(doc, argv[1])))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
