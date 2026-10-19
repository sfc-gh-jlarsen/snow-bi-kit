"""Static check for snow-bi-kit Streamlit apps.

Fails if the app renders data without going through bi_kit_runtime, because
then the "how this was built" panel could disagree with what's on screen.

    python verify_app.py path/to/streamlit_app.py [more.py ...]

Exit code 0 = clean, 1 = findings (printed one per line as file:line: message).
"""

from __future__ import annotations

import ast
import sys

# Streamlit calls that put data on screen. They must only appear inside the runtime.
DATA_RENDER_CALLS = {
    "altair_chart", "line_chart", "bar_chart", "area_chart", "scatter_chart", "map",
    "plotly_chart", "vega_lite_chart", "pyplot", "bokeh_chart", "pydeck_chart",
    "dataframe", "data_editor", "table", "metric",
}
# Ways to run SQL that bypass the runtime.
SQL_CALLS = {"sql", "execute", "query"}


def check_file(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)

    findings: list[str] = []
    st_aliases = {"st"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "streamlit":
                    st_aliases.add(a.asname or "streamlit")

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        attr = node.func.attr
        owner = node.func.value
        owner_name = owner.id if isinstance(owner, ast.Name) else None

        if attr in DATA_RENDER_CALLS and owner_name in st_aliases:
            findings.append(
                f"{path}:{node.lineno}: st.{attr}() renders data directly; use bi.chart/bi.table/bi.kpi so the debug panel matches"
            )
        elif attr in DATA_RENDER_CALLS and owner_name not in (None, "bi", "bi_kit_runtime") and attr == "metric":
            # columns/containers: col1.metric(...)
            findings.append(f"{path}:{node.lineno}: .metric() renders data directly; use bi.kpi(run, ..., container=col)")
        elif attr in SQL_CALLS and owner_name in {"session", "conn", "cursor", "cur"}:
            findings.append(f"{path}:{node.lineno}: {owner_name}.{attr}() runs SQL outside bi.run_visual; the panel won't show it")
    return findings


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    findings = [f for p in argv for f in check_file(p)]
    for f in findings:
        print(f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
