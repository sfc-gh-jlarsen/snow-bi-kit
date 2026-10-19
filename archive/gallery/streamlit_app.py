"""snow-bi-kit visual gallery: every implemented library entry on synthetic data.

Runs with no tables: data comes from a deterministic GENERATOR query, so it is
also the regression test for the library (selfcheck.py re-runs every visual).

    streamlit run gallery/streamlit_app.py          # uses your default Snowflake connection
    python plugin/runtime/selfcheck.py gallery/streamlit_app.py --connection <name>
"""

import os
import sys

import altair as alt
import pandas as pd
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plugin", "runtime"))  # local dev; deployed copies ship the file
import bi_kit_runtime as bi  # noqa: E402

st.set_page_config(page_title="snow-bi-kit gallery", layout="wide")


def _session():
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:
        return st.connection("snowflake").session()


brand = bi.load_brand(os.path.join(HERE, "bi_kit_brand.json")) or {}
debug = st.sidebar.toggle("Show how each chart was built", value=True)
bi.configure(_session(), debug=debug, brand=brand)
POS, NEG = brand.get("positive_color", "#2E7D32"), brand.get("negative_color", "#C62828")
SRC = ["synthetic: GENERATOR (no tables)"]

# Deterministic synthetic tire sales: 24 months × 12 plants × 3 product lines.
BASE = """
months AS (
  SELECT DATEADD(month, ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1, '2024-01-01'::DATE) AS month
  FROM TABLE(GENERATOR(ROWCOUNT => 24))
), plants AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) AS n FROM TABLE(GENERATOR(ROWCOUNT => 12))
), lines AS (
  SELECT column1 AS product_line, column2 AS weight
  FROM VALUES ('Consumer', 1.0), ('Commercial', 0.6), ('Off-the-Road', 0.3)
), sales AS (
  SELECT m.month,
         'P' || LPAD(p.n::STRING, 2, '0') AS plant,
         DECODE(MOD(p.n, 4), 0, 'North America', 1, 'Europe', 2, 'Asia Pacific', 'Latin America') AS region,
         l.product_line,
         ROUND((40000 + MOD(ABS(HASH(p.n, m.month, l.product_line)), 30000)) * l.weight
               * (1 + 0.15 * SIN(MONTH(m.month) / 12 * 2 * PI()))
               * (1 + 0.01 * DATEDIFF(month, '2024-01-01', m.month)), 2) AS net_sales_usd,
         ROUND(MOD(ABS(HASH(p.n, m.month, l.product_line, 'u')), 900) * l.weight + 100) AS units,
         ROUND(MOD(ABS(HASH(p.n, m.month, l.product_line, 'r')), 50) / 1000 + 0.01, 4) AS return_rate
  FROM months m CROSS JOIN plants p CROSS JOIN lines l
)"""


def q(select: str) -> str:
    return f"WITH {BASE}\n{select.strip()}"


def money(field: str, title: str):
    return alt.Y(f"{field}:Q", title=title, axis=alt.Axis(format="$,.0f"))


st.title("Visual library gallery")
st.caption("Synthetic tire sales (24 months, 12 plants, 3 product lines). Every chart is built from the query shown in its panel.")

tabs = st.tabs(["Headline", "Over time", "Categories", "Spread", "Two dimensions", "Tables"])

# ------------------------------------------------------------------ Headline
with tabs[0]:
    c1, c2, c3 = st.columns(3)
    sales_kpi = bi.run_visual(
        "Net sales 2025 (vs 2024)",
        q("""
        SELECT SUM(IFF(YEAR(month) = 2025, net_sales_usd, 0)) AS value,
               SUM(IFF(YEAR(month) = 2024, net_sales_usd, 0)) AS compare_value,
               (value - compare_value) / NULLIF(compare_value, 0) AS delta_pct
        FROM sales"""),
        library_entry="kpi", sources=SRC,
    )
    bi.tie_out(sales_kpi, "VALUE", expected=17_815_121.48)  # the "number to match" a brief would supply
    bi.kpi(sales_kpi, "VALUE", delta_col="DELTA_PCT", fmt="${:,.0f}", container=c1)

    units_kpi = bi.run_visual(
        "Units 2025 (vs 2024)",
        q("""
        SELECT SUM(IFF(YEAR(month) = 2025, units, 0)) AS value,
               SUM(IFF(YEAR(month) = 2024, units, 0)) AS compare_value,
               (value - compare_value) / NULLIF(compare_value, 0) AS delta_pct
        FROM sales"""),
        library_entry="kpi", sources=SRC,
    )
    bi.kpi(units_kpi, "VALUE", delta_col="DELTA_PCT", container=c2)

    rr_kpi = bi.run_visual(
        "Return rate 2025 (vs 2024)",
        q("""
        SELECT AVG(IFF(YEAR(month) = 2025, return_rate, NULL)) AS value,
               AVG(IFF(YEAR(month) = 2024, return_rate, NULL)) AS compare_value,
               (value - compare_value) / NULLIF(compare_value, 0) AS delta_pct
        FROM sales"""),
        library_entry="kpi", sources=SRC,
    )
    bi.kpi(rr_kpi, "VALUE", delta_col="DELTA_PCT", fmt="{:.2%}", container=c3)

    spark = bi.run_visual(
        "Net sales trend (sparkline)",
        q("SELECT month::TIMESTAMP_NTZ AS month, SUM(net_sales_usd) AS net_sales FROM sales GROUP BY 1 ORDER BY 1"),
        library_entry="sparkline", sources=SRC,
    )
    bi.chart(spark, lambda df: alt.Chart(df).mark_line(strokeWidth=2).encode(
        x=alt.X("MONTH:T", axis=None), y=alt.Y("NET_SALES:Q", axis=None, scale=alt.Scale(zero=False)),
    ).properties(height=50))

# ------------------------------------------------------------------ Over time
with tabs[1]:
    by_region = bi.run_visual(
        "Net sales by month and region",
        q("""
        SELECT month::TIMESTAMP_NTZ AS month, region, SUM(net_sales_usd) AS net_sales
        FROM sales GROUP BY 1, 2 ORDER BY 1, 2"""),
        library_entry="line", sources=SRC,
    )
    bi.chart(by_region, lambda df: alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("MONTH:T", title=None), y=money("NET_SALES", "Net sales"), color=alt.Color("REGION:N", title="Region"),
        tooltip=["MONTH:T", "REGION:N", alt.Tooltip("NET_SALES:Q", format="$,.0f")],
    ))

    slope = bi.run_visual(
        "Net sales by region, 2024 vs 2025",
        q("""
        SELECT region, YEAR(month)::STRING AS period, SUM(net_sales_usd) AS net_sales
        FROM sales GROUP BY 1, 2 ORDER BY 1, 2"""),
        library_entry="slope", sources=SRC,
    )

    def _slope(df):
        base = alt.Chart(df).encode(x=alt.X("PERIOD:O", title=None), y=money("NET_SALES", "Net sales"),
                                    color=alt.Color("REGION:N", title="Region"))
        return base.mark_line(point=True) + base.mark_text(dx=8, align="left").encode(
            text=alt.condition(alt.datum.PERIOD == "2025", "REGION:N", alt.value("")))

    bi.chart(slope, _slope)

    def waterfall_steps(df: pd.DataFrame) -> pd.DataFrame:
        """Turn signed steps into start/end bars: totals start at 0, changes stack on the running total."""
        df = df.sort_values("STEP_ORDER").reset_index(drop=True)
        running, starts, ends = 0.0, [], []
        for kind, amount in zip(df["KIND"], df["AMOUNT"]):
            if kind == "total":
                start, end = 0.0, float(amount)
            else:
                start, end = running, running + float(amount)
            starts.append(start)
            ends.append(end)
            running = end
        df["START_VALUE"], df["END_VALUE"] = starts, ends
        df["DIRECTION"] = ["total" if k == "total" else ("up" if a >= 0 else "down") for k, a in zip(df["KIND"], df["AMOUNT"])]
        return df

    wf = bi.run_visual(
        "From 2024 to 2025 net sales, by region",
        q("""
        , totals AS (
          SELECT SUM(IFF(YEAR(month) = 2024, net_sales_usd, 0)) AS y24,
                 SUM(IFF(YEAR(month) = 2025, net_sales_usd, 0)) AS y25 FROM sales
        ), changes AS (
          SELECT region AS step,
                 SUM(IFF(YEAR(month) = 2025, net_sales_usd, 0)) - SUM(IFF(YEAR(month) = 2024, net_sales_usd, 0)) AS amount
          FROM sales GROUP BY 1
        )
        SELECT '2024 total' AS step, 0 AS step_order, y24 AS amount, 'total' AS kind FROM totals
        UNION ALL
        SELECT step, ROW_NUMBER() OVER (ORDER BY amount DESC), amount, 'change' FROM changes
        UNION ALL
        SELECT '2025 total', 99, y25, 'total' FROM totals"""),
        transform=waterfall_steps, library_entry="waterfall", sources=SRC,
    )
    bi.chart(wf, lambda df: alt.Chart(df).mark_bar().encode(
        x=alt.X("STEP:N", sort=alt.SortField("STEP_ORDER"), title=None),
        y=money("START_VALUE", "Net sales"), y2="END_VALUE:Q",
        color=alt.Color("DIRECTION:N", scale=alt.Scale(domain=["total", "up", "down"],
                                                         range=[brand.get("primary_color", "#1F4E79"), POS, NEG]),
                        legend=None),
        tooltip=["STEP:N", alt.Tooltip("AMOUNT:Q", format="$,.0f")],
    ))

# ------------------------------------------------------------------ Categories
with tabs[2]:
    bar = bi.run_visual(
        "Net sales 2025 by product line",
        q("SELECT product_line, SUM(net_sales_usd) AS net_sales FROM sales WHERE YEAR(month) = 2025 GROUP BY 1 ORDER BY 2 DESC"),
        library_entry="bar", sources=SRC,
    )
    bi.chart(bar, lambda df: alt.Chart(df).mark_bar().encode(
        y=alt.Y("PRODUCT_LINE:N", sort="-x", title=None), x=alt.X("NET_SALES:Q", title="Net sales", axis=alt.Axis(format="$,.0f")),
    ))

    stacked = bi.run_visual(
        "Net sales 2025 by region and product line",
        q("""
        SELECT region, product_line, SUM(net_sales_usd) AS net_sales
        FROM sales WHERE YEAR(month) = 2025 GROUP BY 1, 2 ORDER BY 1, 2"""),
        library_entry="stacked_bar", sources=SRC,
    )
    bi.chart(stacked, lambda df: alt.Chart(df).mark_bar().encode(
        x=alt.X("REGION:N", title=None), y=money("NET_SALES", "Net sales"), color=alt.Color("PRODUCT_LINE:N", title="Product line"),
    ))

    topn = bi.run_visual(
        "Top 5 plants by net sales 2025 (rest as Other)",
        q("""
        , ranked AS (
          SELECT plant, SUM(net_sales_usd) AS net_sales, RANK() OVER (ORDER BY SUM(net_sales_usd) DESC) AS rnk
          FROM sales WHERE YEAR(month) = 2025 GROUP BY 1
        )
        SELECT IFF(rnk <= 5, plant, 'Other') AS plant, SUM(net_sales) AS net_sales, MIN(IFF(rnk <= 5, rnk, 99)) AS sort_order
        FROM ranked GROUP BY 1 ORDER BY sort_order"""),
        library_entry="top_n_other", sources=SRC,
    )
    bi.chart(topn, lambda df: alt.Chart(df).mark_bar().encode(
        y=alt.Y("PLANT:N", sort=alt.SortField("SORT_ORDER"), title=None),
        x=alt.X("NET_SALES:Q", title="Net sales", axis=alt.Axis(format="$,.0f")),
        color=alt.condition(alt.datum.PLANT == "Other", alt.value("#BBBBBB"), alt.value(brand.get("primary_color", "#1F4E79"))),
    ))

    pareto = bi.run_visual(
        "Plants: share of 2025 net sales (Pareto)",
        q("""
        , p AS (SELECT plant, SUM(net_sales_usd) AS net_sales FROM sales WHERE YEAR(month) = 2025 GROUP BY 1)
        SELECT plant, net_sales,
               SUM(net_sales) OVER (ORDER BY net_sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                 / SUM(net_sales) OVER () AS cum_pct
        FROM p ORDER BY net_sales DESC"""),
        library_entry="pareto", sources=SRC,
    )

    def _pareto(df):
        x = alt.X("PLANT:N", sort=alt.SortField("NET_SALES", order="descending"), title=None)
        bars = alt.Chart(df).mark_bar().encode(x=x, y=money("NET_SALES", "Net sales"))
        line = alt.Chart(df).mark_line(point=True, color=brand.get("negative_color", "#C62828")).encode(
            x=x, y=alt.Y("CUM_PCT:Q", title="Cumulative share", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])))
        rule = alt.Chart(pd.DataFrame({"y": [0.8]})).mark_rule(strokeDash=[4, 4]).encode(y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 1])))
        return alt.layer(bars, line + rule).resolve_scale(y="independent")

    bi.chart(pareto, _pareto)

    bullet = bi.run_visual(
        "Net sales 2025 vs target, by region",
        q("""
        SELECT region,
               SUM(IFF(YEAR(month) = 2025, net_sales_usd, 0)) AS actual,
               SUM(IFF(YEAR(month) = 2024, net_sales_usd, 0)) * 1.05 AS target,
               SUM(IFF(YEAR(month) = 2024, net_sales_usd, 0)) * 0.95 AS poor_limit,
               SUM(IFF(YEAR(month) = 2024, net_sales_usd, 0)) * 1.10 AS good_limit
        FROM sales GROUP BY 1 ORDER BY 1"""),
        library_entry="bullet", sources=SRC,
    )

    def _bullet(df):
        y = alt.Y("REGION:N", title=None)
        band = alt.Chart(df).mark_bar(color="#E6E6E6", size=24).encode(y=y, x=alt.X("GOOD_LIMIT:Q", title="Net sales", axis=alt.Axis(format="$,.0f")))
        poor = alt.Chart(df).mark_bar(color="#CFCFCF", size=24).encode(y=y, x="POOR_LIMIT:Q")
        actual = alt.Chart(df).mark_bar(color=brand.get("primary_color", "#1F4E79"), size=10).encode(y=y, x="ACTUAL:Q")
        target = alt.Chart(df).mark_tick(color="black", thickness=3, size=28).encode(y=y, x="TARGET:Q")
        return band + poor + actual + target

    bi.chart(bullet, _bullet)

# ------------------------------------------------------------------ Spread
with tabs[3]:
    box = bi.run_visual(
        "Monthly return rate by region (box-and-whisker)",
        q("SELECT region, plant, month::TIMESTAMP_NTZ AS month, return_rate FROM sales"),
        library_entry="box_whisker", sources=SRC,
    )
    st.caption("Box = middle half of months; line = median; whiskers = typical range; dots = unusual months.")
    bi.chart(box, lambda df: alt.Chart(df).mark_boxplot(extent=1.5).encode(
        x=alt.X("REGION:N", title=None), y=alt.Y("RETURN_RATE:Q", title="Return rate", axis=alt.Axis(format="%")),
    ))

    hist = bi.run_visual(
        "Distribution of monthly units per plant and product line",
        q("SELECT WIDTH_BUCKET(units, 0, 1100, 11) AS bucket, (bucket - 1) * 100 AS bin_start, COUNT(*) AS months FROM sales GROUP BY 1, 2 ORDER BY 1"),
        library_entry="histogram", sources=SRC,
    )
    st.caption("Bins of 100 units.")
    bi.chart(hist, lambda df: alt.Chart(df).mark_bar().encode(
        x=alt.X("BIN_START:O", title="Units (bin start)"), y=alt.Y("MONTHS:Q", title="Count"),
    ))

    scatter = bi.run_visual(
        "Plants: units vs net sales, 2025",
        q("""
        SELECT plant, region, SUM(units) AS units, SUM(net_sales_usd) AS net_sales
        FROM sales WHERE YEAR(month) = 2025 GROUP BY 1, 2 ORDER BY 1"""),
        library_entry="scatter", sources=SRC,
    )

    def _scatter(df):
        pts = alt.Chart(df).mark_circle(size=90).encode(
            x=alt.X("UNITS:Q", title="Units"), y=money("NET_SALES", "Net sales"), color=alt.Color("REGION:N", title="Region"),
            tooltip=["PLANT:N", "REGION:N", "UNITS:Q", alt.Tooltip("NET_SALES:Q", format="$,.0f")])
        trend = alt.Chart(df).transform_regression("UNITS", "NET_SALES").mark_line(strokeDash=[4, 4], color="gray").encode(
            x="UNITS:Q", y="NET_SALES:Q")
        return pts + trend

    bi.chart(scatter, _scatter)

# ------------------------------------------------------------------ Two dimensions
with tabs[4]:
    heat = bi.run_visual(
        "Net sales 2025 by region and month (heatmap)",
        q("""
        SELECT region, month::TIMESTAMP_NTZ AS month, SUM(net_sales_usd) AS net_sales
        FROM sales WHERE YEAR(month) = 2025 GROUP BY 1, 2 ORDER BY 1, 2"""),
        library_entry="heatmap", sources=SRC,
    )
    bi.chart(heat, lambda df: alt.Chart(df).mark_rect().encode(
        x=alt.X("month(MONTH):O", title=None), y=alt.Y("REGION:N", title=None),
        color=alt.Color("NET_SALES:Q", title="Net sales", scale=alt.Scale(scheme="blues"), legend=alt.Legend(format="$,.0f")),
        tooltip=["REGION:N", "MONTH:T", alt.Tooltip("NET_SALES:Q", format="$,.0f")],
    ))

    multiples = bi.run_visual(
        "Monthly net sales by product line, one panel per region (small multiples)",
        q("""
        SELECT region, product_line, month::TIMESTAMP_NTZ AS month, SUM(net_sales_usd) AS net_sales
        FROM sales GROUP BY 1, 2, 3 ORDER BY 1, 2, 3"""),
        library_entry="small_multiples", sources=SRC,
    )
    bi.chart(multiples, lambda df: alt.Chart(df).mark_line().encode(
        x=alt.X("MONTH:T", title=None), y=alt.Y("NET_SALES:Q", title="Net sales", axis=alt.Axis(format="$,.0s")),
        color=alt.Color("PRODUCT_LINE:N", title="Product line"),
    ).properties(width=260, height=150).facet(facet=alt.Facet("REGION:N", title=None), columns=2))

# ------------------------------------------------------------------ Tables
with tabs[5]:
    plants = bi.run_visual(
        "Plant detail 2025 with return-rate status",
        q("""
        SELECT plant, region, SUM(net_sales_usd) AS net_sales, SUM(units) AS units, AVG(return_rate) AS return_rate,
               CASE WHEN AVG(return_rate) > 0.036 THEN 'Red' WHEN AVG(return_rate) > 0.033 THEN 'Amber' ELSE 'Green' END AS status
        FROM sales WHERE YEAR(month) = 2025 GROUP BY 1, 2 ORDER BY return_rate DESC"""),
        library_entry="cond_table", sources=SRC,
    )
    status_colors = {"Red": "#F8D7DA", "Amber": "#FFF3CD", "Green": "#D4EDDA"}

    def _style(df):
        return df.style.format({"NET_SALES": "${:,.0f}", "UNITS": "{:,.0f}", "RETURN_RATE": "{:.2%}"}).apply(
            lambda row: [f"background-color: {status_colors.get(row['STATUS'], '')}" if c == "STATUS" else "" for c in row.index],
            axis=1)

    bi.table(plants, style=_style)
