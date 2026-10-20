# The "How this was built" helper

Shared by bi-kit-build (new apps) and bi-kit-apply-standards (existing apps). Paste once near the top of the app; fill `BRAND` from company standards.

Small on purpose: it runs the SQL, applies an optional pandas step, and shows a "How this was built" panel under the visual.

```python
import inspect
import time

import altair as alt
import pandas as pd
import streamlit as st

DEBUG = True  # "How this was built" panels. Hand-off sets this to False.

# Brand and formats: copied from company standards (or Streamlit defaults if none).
BRAND = {"palette": ["#29B5E8", "#11567F", "#FF9F36", "#7D44CF"], "font": "sans-serif"}


@st.cache_resource
def get_session():
    try:  # running in Snowflake
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:  # running locally: uses your default Snowflake connection
        return st.connection("snowflake").session()


def run_visual(title, sql, params=None, transform=None):
    """Run one visual's query. Returns (df, info) where info feeds the panel."""
    start = time.time()
    df = get_session().sql(sql, params=params or []).to_pandas()
    rows_returned = len(df)
    if transform:
        df = transform(df)
    info = {
        "title": title, "sql": sql, "params": params or [],
        "transform": inspect.getsource(transform) if transform else None,
        "rows_returned": rows_returned, "rows_shown": len(df),
        "seconds": round(time.time() - start, 2),
    }
    return df, info


def how_built(info, tie=None):
    if not DEBUG:
        return
    with st.expander("How this was built"):
        st.code(info["sql"].strip(), language="sql")
        if info["params"]:
            st.caption(f"Parameters: {info['params']}")
        if info["transform"]:
            st.caption("Python step after the query:")
            st.code(info["transform"], language="python")
        st.caption(f"Rows returned: {info['rows_returned']} · shown: {info['rows_shown']} · {info['seconds']} s")
        if tie:
            st.write(tie)


def tie_out(actual, expected, label="Number to match"):
    diff = actual - expected
    return f"**{label}:** expected {expected:,.0f}, got {actual:,.0f} → " + (
        "**matches**" if abs(diff) < 0.5 else f"**differs by {diff:,.0f}**")
```

