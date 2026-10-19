"""Deterministic secret / credential scan for snow-bi-kit projects.

    python scan_secrets.py <project_dir> [--json]

Uses gitleaks too if it's installed (extra coverage), but never depends on it.
Exit code 1 if any fix_now finding, else 0. Findings never echo the secret value.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT_EXT = {".py", ".sql", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg",
            ".html", ".js", ".ts", ".tsx", ".jsx", ".sh", ".env", ".ipynb", ""}


def load_rules(path: str = os.path.join(HERE, "secret_patterns.json")) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _iter_files(root: str, skip: list[str]):
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/") + "/"
        if any(s in rel_dir for s in skip):
            dirnames[:] = []
            continue
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
            if any(s in rel for s in skip):
                continue
            yield rel, os.path.join(dirpath, name)


def scan(root: str, rules_doc: dict | None = None) -> list[dict]:
    doc = rules_doc or load_rules()
    ignore = doc["ignore_if_line_contains"]
    content_rules = [(r, re.compile(r["regex"])) for r in doc["rules"] if "regex" in r]
    path_rules = [(r, re.compile(r["path_regex"])) for r in doc["rules"] if "path_regex" in r]
    findings: list[dict] = []

    for rel, full in _iter_files(root, doc["skip_paths"]):
        for rule, rx in path_rules:
            if rx.search(rel):
                findings.append(_finding(rule, rel, None))
        if os.path.splitext(rel)[1].lower() not in TEXT_EXT:
            continue
        try:
            with open(full, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if any(tok in line for tok in ignore):
                continue
            for rule, rx in content_rules:
                if rx.search(line):
                    findings.append(_finding(rule, rel, i))

    findings.extend(_gitleaks(root, {(f["file"], f["line"]) for f in findings}))
    return findings


def _finding(rule: dict, rel: str, line: int | None) -> dict:
    return {"rule": rule["id"], "severity": rule["severity"], "file": rel, "line": line,
            "why": rule["why"], "fix": rule["fix"]}


def _gitleaks(root: str, seen: set) -> list[dict]:
    exe = shutil.which("gitleaks")
    if not exe:
        return []
    try:
        out = subprocess.run(
            [exe, "detect", "--no-git", "--source", root, "--report-format", "json",
             "--report-path", "/dev/stdout", "--redact", "--exit-code", "0"],
            capture_output=True, text=True, timeout=120,
        )
        items = json.loads(out.stdout or "[]")
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        return []
    extra = []
    for it in items:
        rel = os.path.relpath(it.get("File", ""), root)
        key = (rel, it.get("StartLine"))
        if key in seen:
            continue
        extra.append({"rule": f"gitleaks:{it.get('RuleID')}", "severity": "fix_now", "file": rel,
                      "line": it.get("StartLine"), "why": "A credential scanner flagged this as a likely secret.",
                      "fix": "Remove it, rotate it, and use the app's connection or a Snowflake secret."})
    return extra


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    root, as_json = argv[0], "--json" in argv
    findings = scan(root)
    if as_json:
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            print(f"[{f['severity']}] {loc} ({f['rule']}): {f['why']} Fix: {f['fix']}")
        if not findings:
            print("No credentials found.")
    return 1 if any(f["severity"] == "fix_now" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
