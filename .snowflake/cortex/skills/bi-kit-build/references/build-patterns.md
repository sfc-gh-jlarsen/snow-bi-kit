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

## The helper
Paste the helper block from `how-built-helper.md` (bi-kit-library) once near the top of the app: `run_visual`, `how_built`, `tie_out`, `DEBUG`, `BRAND`.

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
Use the bundled Streamlit skill. Location, warehouse, compute pool, roles and external access belong to the project's deployment config (`snowflake.yml` targets), which that skill reads or creates. Standards don't set them.
