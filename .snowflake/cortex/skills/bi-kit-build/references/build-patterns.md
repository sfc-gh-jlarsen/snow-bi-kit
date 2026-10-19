# Streamlit app pattern (snow-bi-kit)

Every kit app has the same shape so analysts (and the data team later) can find their way around. Streamlit mechanics come from the bundled Streamlit skill; this file is only the kit's conventions.

## Project layout
```
<project>/
  PROJECT_BRIEF.md
  reference/                 # optional pictures, starting query
  app/
    streamlit_app.py
    environment.yml          # or pyproject.toml, per the Streamlit skill
```

## The helper (paste once at the top of the app)
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

## Using it
```python
st.set_page_config(layout="wide")
alt.themes.register("brand", lambda: {"config": {"range": {"category": BRAND["palette"]}, "font": BRAND["font"]}})
alt.themes.enable("brand")

FQN = "SALES_DB.CORE.SALES_DAILY"   # from the brief: never guessed

st.title("Plant performance")
region = st.selectbox("Region", ["All", "North America", "Europe"])

# 1. KPI (library: kpi)
kpi, info = run_visual(
    "Net sales",
    f"SELECT SUM(net_sales_usd) AS value FROM {FQN} WHERE (? = 'All' OR region = ?)",
    params=[region, region],
)
value = kpi["VALUE"][0]
st.metric("Net sales", f"${value:,.0f}")
how_built(info, tie=tie_out(value, 12_400_000))   # number to match from the brief

# 2. Trend with a pandas step (library: line)
def add_rolling_3m(df):
    df = df.sort_values("MONTH")
    df["ROLLING_3M"] = df["NET_SALES"].rolling(3, min_periods=1).mean()
    return df

trend, info = run_visual(
    "Net sales by month",
    f"""SELECT DATE_TRUNC('month', day) AS month, SUM(net_sales_usd) AS net_sales
        FROM {FQN} WHERE (? = 'All' OR region = ?) GROUP BY 1 ORDER BY 1""",
    params=[region, region],
    transform=add_rolling_3m,
)
st.altair_chart(alt.Chart(trend).mark_line(point=True).encode(
    x=alt.X("MONTH:T", title=None), y=alt.Y("NET_SALES:Q", title="Net sales (USD)")),
    use_container_width=True)
how_built(info)
```

## Rules
- **Column names come back UPPER CASE** from Snowflake; use them as-is.
- **Parameters**: `?` placeholders with `params=[...]`, one value per placeholder, in order. Never f-string a user's selection into SQL; f-strings are only for object names from the brief.
- **Every visual** = `run_visual` → draw from that `df` → `how_built(info)` right under it. Don't draw from any other query.
- **Caching**: follow the Streamlit skill. Don't cache across users if rows differ per viewer.
- **Layout**: KPIs in `st.columns`, then trends, then breakdowns, then detail tables, in the brief's numbered order. `st.tabs` for distinct audiences or pages.
- **Brand and formats**: palette, font and number/currency/percent/date formats from standards. Use good/bad colours together with text or arrows, never colour alone.
- **Labels**: titles say what and over what period ("Net sales by month, last 24 months").

## Deploying (prototype)
Use the bundled Streamlit skill. Location, warehouse, compute pool and external access come from standards `environments.prototype` and `compute`; otherwise ask.
