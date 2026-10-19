"""Headless self-check for a snow-bi-kit Streamlit app.

    python selfcheck.py path/to/streamlit_app.py [--connection NAME] [--timeout 300]

1. Static check (verify_app.py): every visual goes through the runtime.
2. Runs the app once with Streamlit's AppTest (debug on).
3. Re-runs every recorded visual's SQL + transform and compares with what rendered.
4. Writes <app dir>/.bi-kit/runs.json (SQL, sources, fingerprints; no data values).

Exit 0 = all good; 1 = findings. Output is for the kit, not the analyst.
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("bi_kit.selfcheck")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("app")
    ap.add_argument("--connection", default=None, help="Snowflake connection name (defaults to your default)")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    app = os.path.abspath(args.app)
    app_dir = os.path.dirname(app)
    if args.connection:
        os.environ["SNOWFLAKE_DEFAULT_CONNECTION_NAME"] = args.connection
    os.environ["BI_KIT_DEBUG"] = "1"

    sys.path.insert(0, HERE)
    import verify_app  # noqa: E402

    static = verify_app.check_file(app)
    for f in static:
        log.error("static: %s", f)

    # Import the app's own copy of the runtime first so the app and this script share one module.
    sys.path.insert(0, app_dir)
    bi = importlib.import_module("bi_kit_runtime")

    from streamlit.testing.v1 import AppTest  # noqa: E402

    cwd = os.getcwd()
    os.chdir(app_dir)  # apps load bi_kit_brand.json relative to their folder
    try:
        at = AppTest.from_file(app, default_timeout=args.timeout)
        at.run()
    finally:
        os.chdir(cwd)

    errors = [str(e.value) for e in at.exception] if at.exception else []
    for e in errors:
        log.error("app error: %s", e)

    results = bi.self_check_all()
    for title, ok in results.items():
        (log.info if ok else log.error)("visual %-45s %s", title[:45], "ok" if ok else "MISMATCH")
    if not results:
        log.error("no visuals were recorded; does the app call bi.run_visual?")

    manifest = bi.write_manifest(os.path.join(app_dir, ".bi-kit", "runs.json"))
    summary = {
        "static_findings": len(static),
        "app_errors": len(errors),
        "visuals": len(results),
        "mismatches": [t for t, ok in results.items() if not ok],
        "tie_outs": [{"title": r.title, **r.tie_out} for r in bi.runs() if r.tie_out],
        "manifest": manifest,
    }
    print(json.dumps(summary, indent=2, default=str))
    ok = not static and not errors and results and not summary["mismatches"]
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
