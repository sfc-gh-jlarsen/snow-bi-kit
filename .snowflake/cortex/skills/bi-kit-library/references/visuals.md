# Visual library

The kit names and builds visuals only from this list. Analyst wording maps to an entry (aliases in brackets). If nothing fits, say so and offer the closest entry; don't improvise a new chart type.

Every entry is built the same way: one `run_visual(...)` per visual, drawn from its result and followed by `how_built(info)` (Streamlit; see bi-kit-build `references/build-patterns.md`), or as inline SVG/HTML plus a `<details>` panel (HTML report). Column names below are illustrative.

Legend: **Use** = when it's the right choice · **Avoid** = when to pick something else · **Shape** = what the query must return · **Build** = Altair mark/encoding (Streamlit) · **HTML** = report approach · **Watch** = common mistakes. ✔ = has a worked example (in `archive/gallery/`).

---

## Headline numbers

### `kpi` KPI tile with change ✔ [scorecard, BAN, big number, card]
- **Use:** one number that matters, plus its change vs a comparison (last year, plan, last month).
- **Shape:** 1 row: `VALUE`, `COMPARE_VALUE`, `DELTA_PCT` (computed in SQL as `(value - compare) / NULLIF(compare, 0)`).
- **Build:** `st.metric(label, value, delta)` from the `VALUE` and `DELTA_PCT` columns; up to 4–5 per row via `st.columns`.
- **HTML:** large number + small coloured delta text; green/red from brand, plus an arrow so it isn't colour-only.
- **Watch:** say *what* the comparison is in the label ("vs LY"). Compute the delta in SQL, not by eye. Company standards may say "vs plan".

### `sparkline` Sparkline ✔ [mini trend, trendline in a tile]
- **Use:** shape of the recent trend next to a KPI or in a table row; no axes needed.
- **Shape:** `PERIOD`, `VALUE` (12–24 points).
- **Build:** `mark_line()` with `axis=None`, height ~40, no gridlines; often paired with `kpi`.
- **HTML:** inline SVG `<polyline>`; scale points to the box.
- **Watch:** don't use for exact reading; always pair with the number.

---

## Change over time

### `line` Line / multi-line ✔ [trend, time series]
- **Use:** how a measure moves over time; up to ~5 series.
- **Avoid:** more than 5–6 series (use `small_multiples`).
- **Shape:** `PERIOD`, `VALUE`, optional `SERIES`.
- **Build:** `mark_line(point=True)`, x `PERIOD:T`, y `VALUE:Q`, color `SERIES:N`.
- **HTML:** SVG polylines + legend.
- **Watch:** fill missing periods in SQL (calendar join) so gaps aren't silently bridged; label the time grain.

### `area` Area / stacked area [volume over time]
- **Use:** total over time and its composition.
- **Avoid:** comparing individual series precisely (only the bottom one has a flat baseline).
- **Shape:** as `line`.
- **Build:** `mark_area()`, color `SERIES:N`, stack default.
- **Watch:** stacked areas hide declines in middle layers.

### `slope` Slope chart ✔ [before/after, two-period comparison]
- **Use:** change between exactly two points for several items (e.g. 2024 vs 2025 by region).
- **Shape:** `ITEM`, `PERIOD` (2 values), `VALUE`.
- **Build:** `mark_line(point=True)`, x `PERIOD:O`, y `VALUE:Q`, detail/color `ITEM:N`, text labels at ends.
- **Watch:** only two periods; more than that, use `line`.

### `waterfall` Waterfall / bridge ✔ [walk, bridge from A to B]
- **Use:** explain how you got from one total to another (last year → this year by driver/region).
- **Shape:** `STEP`, `ORDER`, `AMOUNT` (signed); start and end totals as their own steps.
- **Build:** compute running `START`/`END` per step (window `SUM` in SQL or a pandas transform), then `mark_bar()` with `y=START`, `y2=END`, colour by up/down/total.
- **HTML:** SVG rects using the same start/end.
- **Watch:** the steps must sum exactly to end − start; show that as the check number.

---

## Comparing categories

### `bar` Bar / column ✔ [bar chart, column chart, ranking]
- **Use:** compare a measure across categories; ranking.
- **Shape:** `CATEGORY`, `VALUE`.
- **Build:** `mark_bar()`, horizontal when labels are long (`y=CATEGORY:N`, sort `-x`).
- **Watch:** start at zero; sort by value unless the category has a natural order.

### `stacked_bar` Stacked / 100% stacked bar ✔ [composition, part-to-whole by category]
- **Use:** totals by category *and* their mix.
- **Shape:** `CATEGORY`, `SEGMENT`, `VALUE`.
- **Build:** `mark_bar()`, color `SEGMENT:N`; 100% version uses `stack="normalize"`.
- **Watch:** more than ~5 segments gets unreadable; group the tail as "Other".

### `top_n_other` Top N with "Other" ✔ [top 10, leaderboard]
- **Use:** many categories but only the leaders matter.
- **Shape:** `CATEGORY`, `VALUE`, with everything below rank N collapsed in SQL: `IFF(rnk <= :n, category, 'Other')`.
- **Build:** `bar`, with "Other" pinned last and a muted colour.
- **Watch:** total must still equal the grand total; that's the check number.

### `pareto` Pareto ✔ [80/20]
- **Use:** how few items make up most of the total.
- **Shape:** `CATEGORY`, `VALUE`, `CUM_PCT` (window `SUM(...) OVER (ORDER BY value DESC) / SUM(...) OVER ()`).
- **Build:** layered: `mark_bar()` for VALUE + `mark_line(point=True)` for CUM_PCT on a 0–100% scale, plus an 80% rule.
- **Watch:** this is the one allowed two-scale chart; label both axes clearly.

### `bullet` Bullet chart ✔ [actual vs target, gauge replacement]
- **Use:** actual vs target (and bands) for several items. Replaces gauges/speedometers.
- **Shape:** `ITEM`, `ACTUAL`, `TARGET`, optional `POOR`, `OK` band limits.
- **Build:** layered: wide light `mark_bar` for bands, thin dark `mark_bar` for ACTUAL, `mark_tick` for TARGET.
- **Watch:** gauges and donuts asked for as "progress" → offer bullet.

### `dot_plot` Dot plot / lollipop [clean bar alternative]
- **Use:** many categories where bars feel heavy; comparing two values per category (dumbbell).
- **Shape:** `CATEGORY`, `VALUE` (+ `VALUE_2` for dumbbell).
- **Build:** `mark_circle()` (+ `mark_rule` connecting two values).

---

## Distribution and spread

### `box_whisker` Box-and-whisker ✔ [box plot, spread, outliers]
- **Use:** compare spread, median and outliers across groups (e.g. return rate by plant).
- **Shape:** raw rows: `GROUP`, `VALUE` (one row per observation, not pre-aggregated).
- **Build:** `mark_boxplot(extent=1.5)`.
- **Watch:** needs row-level data; cap rows with `SAMPLE` if huge and say so in the panel. Explain the box in a caption for first-time readers.

### `histogram` Histogram ✔ [distribution, frequency]
- **Use:** shape of one measure's distribution.
- **Shape:** raw `VALUE` rows, or pre-binned `BIN_START`, `COUNT` (preferred for large data: `WIDTH_BUCKET` in SQL).
- **Build:** `mark_bar()` with `bin=True` or on pre-binned columns.
- **Watch:** state the bin width.

### `scatter` Scatter with trend line ✔ [correlation, relationship]
- **Use:** relationship between two measures across items.
- **Shape:** `ITEM`, `X_VALUE`, `Y_VALUE`, optional `GROUP`, `SIZE`.
- **Build:** `mark_circle()` + `transform_regression()` line.
- **Watch:** correlation ≠ cause; label outliers instead of hiding them.

---

## Patterns across two dimensions

### `heatmap` Heatmap ✔ [matrix, calendar heatmap, highlight table]
- **Use:** a measure across two categorical dimensions (region × month, plant × product line).
- **Shape:** `ROW_DIM`, `COL_DIM`, `VALUE`.
- **Build:** `mark_rect()`, color `VALUE:Q` (sequential palette; diverging if centred on zero), optional text overlay.
- **Watch:** colour scales must have a legend; avoid red/green-only.

### `small_multiples` Small multiples ✔ [trellis, faceted chart, panel chart]
- **Use:** the same chart repeated per category; replaces spaghetti lines.
- **Shape:** as the base chart + `FACET`.
- **Build:** base chart `.facet(facet="FACET:N", columns=3)` with shared y unless told otherwise.

### `cohort` Cohort table [retention, by start month]
- **Use:** how groups that started at different times behave over their life.
- **Shape:** `COHORT`, `PERIOD_INDEX`, `VALUE` (often a %).
- **Build:** `heatmap` with cohort rows and period-index columns, or `st.dataframe` with conditional formatting.

---

## Tables

### `cond_table` Conditional-format table ✔ [traffic lights, RAG table, highlight table]
- **Use:** detail people will read row by row, with status called out.
- **Shape:** the detail columns + a `STATUS` column computed in SQL (not by colour rules alone).
- **Build:** `st.dataframe` with a pandas `Styler` background colours from brand; keep the status text visible.
- **HTML:** `<table>` with class per status.
- **Watch:** never colour-only; keep STATUS as text. Limit rows or paginate.

### `pivot_table` Crosstab / pivot [matrix table]
- **Use:** exact numbers across two dimensions (what Tableau users call a text table).
- **Shape:** long form `ROW_DIM`, `COL_DIM`, `VALUE`; pivot in SQL (`PIVOT`) or a pandas transform (shown in the debug panel).
- **Watch:** add row/column totals explicitly and tie them out.

---

## Part-to-whole and flow

### `treemap` Treemap [hierarchy share]
- **Use:** share of total across a two-level hierarchy (region → plant).
- **Build:** not native in Altair; use a Plotly treemap (`st.plotly_chart`) or prefer `stacked_bar`. Flag as **heavier**.

### `funnel` Funnel [conversion steps]
- **Use:** drop-off through ordered steps.
- **Shape:** `STEP`, `ORDER`, `COUNT`.
- **Build:** horizontal `bar` sorted by ORDER with conversion % labels; centred funnel shape only on request.

### `donut` Pie / donut [share]
- **Use:** only for 2–3 slices where one dominates.
- **Avoid:** anything else; offer `bar` or `stacked_bar`.
- **Build:** `mark_arc(innerRadius=50)`.

---

## Maps

### `map` Map [geo, filled map, point map]
- **Use:** location genuinely matters to the decision.
- **Watch:** support varies by surface. Streamlit: `st.map`/pydeck (still drawn from its `run_visual` result). CoWork charts don't support geographic maps. Default to a ranked `bar` by region unless the analyst insists.

---

## Discouraged (offer the alternative)

| Asked for | Why not | Offer |
|---|---|---|
| Dual-axis line/bar (two unrelated measures) | Readers compare the lines' crossing point, which means nothing | Two aligned charts, or `pareto` when it's cumulative % |
| Gauge / speedometer | Lots of ink, one number | `bullet` or `kpi` |
| 3-D anything | Distorts values | 2-D equivalent |
| Pie with many slices | Angles are hard to compare | `bar` / `top_n_other` |

---

## Interactions (apply to any entry)
- **Filter**: Streamlit widgets → passed as **query parameters** (`params=[...]`, `%s` / `?` placeholders), never string-concatenated into SQL. The debug panel shows the parameter values.
- **Drill-down**: a selected category re-runs a second visual with that category as a parameter.
- **Cross-filter**: Altair selections within one chart; across charts, use a shared widget.
- **Tooltip**: `tooltip=[...]` with formatted fields; never put critical info only in tooltips.
