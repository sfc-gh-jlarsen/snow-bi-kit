"""snow-bi-kit runtime: every visual goes through one helper so the
"how this was built" panel always shows what actually ran.

Usage in a generated Streamlit app:

    import bi_kit_runtime as bi
    bi.configure(session, debug=True, brand=bi.load_brand("bi_kit_brand.json"))

    run = bi.run_visual(
        "Net sales by month",
        "SELECT month, SUM(net_sales_usd) AS net_sales FROM sales GROUP BY 1 ORDER BY 1",
        transform=add_rolling_avg,          # optional pandas step, shown in the panel
        library_entry="line",
        sources=["SALES_DB.CORE.SALES"],
    )
    bi.chart(run, lambda df: alt.Chart(df).mark_line().encode(x="MONTH:T", y="NET_SALES:Q"))

Rules the kit enforces (see verify_app.py):
  * apps never call session.sql / st.* chart functions directly for data visuals
  * every visual is rendered from run.data, the exact frame the panel describes
"""

from __future__ import annotations

import hashlib
import html
import inspect
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

import pandas as pd

logger = logging.getLogger("bi_kit")

_STATE: dict[str, Any] = {"session": None, "debug": False, "brand": None, "runs": []}


# --------------------------------------------------------------------------- config

def configure(session: Any, debug: bool = False, brand: Optional[dict] = None) -> None:
    """Set the Snowpark session, debug mode and brand once at the top of the app.

    debug can also be forced with the BI_KIT_DEBUG env var ("1"/"0") so the
    production build can switch it off without code edits.
    """
    env = os.environ.get("BI_KIT_DEBUG")
    if env is not None:
        debug = env == "1"
    _STATE.update(session=session, debug=debug, brand=brand, runs=[])
    if brand:
        _register_altair_theme(brand)


def debug_enabled() -> bool:
    return bool(_STATE["debug"])


def load_brand(path: str) -> Optional[dict]:
    """Load the brand block the build step copies from company standards."""
    if not os.path.exists(path):
        logger.warning("brand file %s not found; using defaults", path)
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- core

@dataclass
class VisualRun:
    title: str
    sql: str
    params: Optional[Sequence[Any]]
    data: pd.DataFrame
    raw_rows: int
    run_ms: int
    query_id: Optional[str]
    transform_source: Optional[str] = None
    library_entry: Optional[str] = None
    sources: list[str] = field(default_factory=list)
    fingerprint: str = ""
    tie_out: Optional[dict] = None


def _execute(sql: str, params: Optional[Sequence[Any]]) -> tuple[pd.DataFrame, Optional[str]]:
    session = _STATE["session"]
    if session is None:
        raise RuntimeError("bi_kit_runtime.configure(session, ...) must be called first")
    # Use the connector cursor so we get the real query ID for the debug panel.
    cur = session.connection.cursor()
    try:
        cur.execute(sql, params) if params else cur.execute(sql)
        query_id = getattr(cur, "sfqid", None)
        df = cur.fetch_pandas_all()
    finally:
        cur.close()
    return df, query_id


def _source_of(fn: Optional[Callable]) -> Optional[str]:
    if fn is None:
        return None
    try:
        return inspect.getsource(fn).strip()
    except (OSError, TypeError):
        return f"# source unavailable for {getattr(fn, '__name__', repr(fn))}"


def fingerprint(df: pd.DataFrame) -> str:
    """Order-insensitive content hash, so a re-run with a different row order still matches."""
    if df.empty:
        return "empty:" + ",".join(map(str, df.columns))
    norm = df.copy()
    norm.columns = [str(c) for c in norm.columns]
    norm = norm.astype(str).sort_values(list(norm.columns)).reset_index(drop=True)
    digest = hashlib.sha256(pd.util.hash_pandas_object(norm, index=False).values.tobytes()).hexdigest()
    return f"{norm.shape[0]}x{norm.shape[1]}:{digest[:16]}"


def run_visual(
    title: str,
    sql: str,
    params: Optional[Sequence[Any]] = None,
    transform: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
    library_entry: Optional[str] = None,
    sources: Optional[list[str]] = None,
) -> VisualRun:
    """Run the query, apply the optional pandas transform, and record everything."""
    start = time.perf_counter()
    raw, query_id = _execute(sql, params)
    data = transform(raw.copy()) if transform else raw
    run = VisualRun(
        title=title,
        sql=sql.strip(),
        params=params,
        data=data,
        raw_rows=len(raw),
        run_ms=int((time.perf_counter() - start) * 1000),
        query_id=query_id,
        transform_source=_source_of(transform),
        library_entry=library_entry,
        sources=sources or [],
        fingerprint=fingerprint(data),
    )
    run._transform = transform  # kept for self_check; not shown
    _STATE["runs"].append(run)
    return run


def self_check(run: VisualRun) -> bool:
    """Re-run the SQL shown in the panel, re-apply the shown transform, compare to what rendered."""
    raw, _ = _execute(run.sql, run.params)
    fn = getattr(run, "_transform", None)
    again = fingerprint(fn(raw.copy()) if fn else raw)
    ok = again == run.fingerprint
    if not ok:
        logger.error("self-check mismatch for %r: rendered %s, re-run %s", run.title, run.fingerprint, again)
    return ok


def self_check_all() -> dict[str, bool]:
    return {r.title: self_check(r) for r in _STATE["runs"]}


def tie_out(run: VisualRun, column: str, expected: float, tolerance: float = 0.005) -> dict:
    """Compare a KPI to the trusted number from the brief. tolerance is relative (0.5% default)."""
    actual = float(pd.to_numeric(run.data[column]).sum())
    diff = actual - expected
    rel = abs(diff) / abs(expected) if expected else abs(diff)
    run.tie_out = {
        "expected": expected,
        "actual": actual,
        "diff": diff,
        "status": "matches" if rel <= tolerance else "differs",
    }
    return run.tie_out


def runs() -> list[VisualRun]:
    return list(_STATE["runs"])


def write_manifest(path: str = ".bi-kit/runs.json") -> str:
    """Dump what ran (no data values) for hand-off and the build self-check."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    payload = [
        {
            "title": r.title,
            "sql": r.sql,
            "params": list(r.params) if r.params else None,
            "transform_source": r.transform_source,
            "library_entry": r.library_entry,
            "sources": r.sources,
            "rows_returned": r.raw_rows,
            "rows_rendered": len(r.data),
            "run_ms": r.run_ms,
            "query_id": r.query_id,
            "fingerprint": r.fingerprint,
            "tie_out": r.tie_out,
        }
        for r in _STATE["runs"]
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    return path


# --------------------------------------------------------------------------- Streamlit rendering

def _st():
    import streamlit as st  # imported lazily so the module works in HTML/report contexts

    return st


def debug_panel(run: VisualRun) -> None:
    if not debug_enabled():
        return
    st = _st()
    with st.expander(f"How this was built: {run.title}", expanded=False):
        st.code(run.sql, language="sql")
        if run.params:
            st.caption(f"Parameters: {list(run.params)}")
        if run.transform_source:
            st.caption("Python processing applied after the query")
            st.code(run.transform_source, language="python")
        meta = [
            f"rows returned: {run.raw_rows:,}",
            f"rows shown: {len(run.data):,}",
            f"run time: {run.run_ms:,} ms",
        ]
        if run.query_id:
            meta.append(f"query ID: {run.query_id}")
        if run.library_entry:
            meta.append(f"visual type: {run.library_entry}")
        st.caption(" · ".join(meta))
        if run.sources:
            st.caption("Sources: " + ", ".join(run.sources))
        if run.tie_out:
            t = run.tie_out
            label = "Matches" if t["status"] == "matches" else f"Differs by {t['diff']:,.2f}"
            st.caption(f"Check number: expected {t['expected']:,.2f}, got {t['actual']:,.2f}. {label}")


def _stretch(fn: Callable, *args: Any, **kwargs: Any) -> Any:
    """Full-width render across Streamlit versions (width='stretch' is newer; use_container_width is deprecated)."""
    try:
        return fn(*args, width="stretch", **kwargs)
    except TypeError:
        return fn(*args, use_container_width=True, **kwargs)


def chart(run: VisualRun, build: Callable[[pd.DataFrame], Any], **kwargs: Any) -> None:
    """Render an Altair chart built from run.data, then its debug panel."""
    st = _st()
    if run.title:
        st.markdown(f"**{run.title}**")
    _stretch(st.altair_chart, build(run.data), **kwargs)
    debug_panel(run)


def table(run: VisualRun, style: Optional[Callable[[pd.DataFrame], Any]] = None, **kwargs: Any) -> None:
    """Render a table (optionally styled, e.g. traffic-light formatting) from run.data."""
    st = _st()
    if run.title:
        st.markdown(f"**{run.title}**")
    _stretch(st.dataframe, style(run.data) if style else run.data, hide_index=True, **kwargs)
    debug_panel(run)


def kpi(
    run: VisualRun,
    value_col: str,
    label: Optional[str] = None,
    delta_col: Optional[str] = None,
    fmt: str = "{:,.0f}",
    delta_fmt: str = "{:+.1%}",
    container: Any = None,
) -> None:
    """Render a KPI tile from the first row of run.data."""
    st = _st()
    target = container or st
    row = run.data.iloc[0]
    delta = delta_fmt.format(row[delta_col]) if delta_col and pd.notna(row[delta_col]) else None
    target.metric(label or run.title, fmt.format(row[value_col]), delta)
    with (container or st.container()):
        debug_panel(run)


# --------------------------------------------------------------------------- HTML report rendering

def html_details(run: VisualRun) -> str:
    """Native <details> accordion for HTML reports: no JavaScript, sandbox-safe."""
    if not debug_enabled():
        return ""
    e = html.escape
    parts = [
        "<details class='bi-kit-debug'>",
        f"<summary>How this was built: {e(run.title)}</summary>",
        f"<pre><code>{e(run.sql)}</code></pre>",
    ]
    if run.params:
        parts.append(f"<p>Parameters: {e(str(list(run.params)))}</p>")
    if run.transform_source:
        parts.append("<p>Python processing applied after the query</p>")
        parts.append(f"<pre><code>{e(run.transform_source)}</code></pre>")
    meta = f"rows returned {run.raw_rows:,} · rows shown {len(run.data):,} · {run.run_ms:,} ms"
    if run.query_id:
        meta += f" · query ID {e(run.query_id)}"
    parts.append(f"<p>{meta}</p>")
    if run.sources:
        parts.append(f"<p>Sources: {e(', '.join(run.sources))}</p>")
    if run.tie_out:
        parts.append(f"<p>Check number: {e(run.tie_out['status'])} (expected {run.tie_out['expected']:,.2f})</p>")
    parts.append("</details>")
    return "\n".join(parts)


# --------------------------------------------------------------------------- brand

def _register_altair_theme(brand: dict) -> None:
    try:
        import altair as alt
    except ImportError:
        return
    palette = brand.get("chart_palette") or []
    font = brand.get("font_family", "sans-serif")

    def _theme():
        return {
            "config": {
                "range": {"category": palette} if palette else {},
                "font": font,
                "axis": {"labelFont": font, "titleFont": font, "grid": False},
                "legend": {"labelFont": font, "titleFont": font},
                "view": {"stroke": None},
            }
        }

    alt.themes.register("bi_kit", _theme)
    alt.themes.enable("bi_kit")
