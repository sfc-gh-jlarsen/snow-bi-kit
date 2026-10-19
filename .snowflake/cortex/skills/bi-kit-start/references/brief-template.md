# PROJECT_BRIEF.md template

Write exactly this structure, filled in. Keep it to one page. Mark anything inferred with *(assumed)* so the analyst can correct it.

```markdown
# <Project name>

**Status:** Draft, waiting for "looks right" · **Owner:** <analyst> · **Hand-off to:** <standards.handoff.receiving_team> · **Target date:** <date or "none">
**Starting point:** <new | existing app at `<path or FQN>`>

## Outcome
<One or two sentences: the question this answers and the decision it supports.>

## Who uses it
- Viewers: <who> · Snowflake logins: <all / some / none>
- Different rows for different people: <no / yes: by region, enforced by …>
- Language / timezone: <from standards unless stated> *(assumed)*

## Data
<Data check block from data-intake.md>
- Freshness needed: <live / hourly / daily / monthly>
- Starting query (verbatim, if provided): see `reference/starting_query.sql`

## Measures
| Measure | Definition | Source column | Confirmed |
|---|---|---|---|
| Net sales | Gross − returns, USD, excl. intercompany | NET_SALES_USD | yes |

**Number to match:** <measure, slice, period> = <value> (from <report>). Built dashboards show whether they match.

## Look
- Reference: <reference/mockup.png, or "description only", or "proposed by the kit">
- Layout (library names):
  1. <kpi ×4: Net sales, Units, Return rate, Avg price (vs LY)>
  2. <line: Net sales by month, by region>
  3. <top_n_other: Top 10 plants by net sales>
  4. <cond_table: Plant detail with return-rate status>
- Filters: <region, date range> · Drill: <region → plant>

## Recommended surface
**<Streamlit app | HTML report | Agent>**: <one-line reason>.
Other options: <one line each on why not>.

## Delivery & scale
- Export / schedule / email: <needs> · Mobile: <yes/no>
- Expected viewers: <n> · Data volume: <from data check>
- Sensitivity: <none found / PII in columns …>

## Scope check
- <"Looks like one project" or the issues found>

## Open questions
- <only real ones>

## Build plan
| # | Visual (library name) | Measure / data | Change |
|---|---|---|---|
| 1 | kpi ×4 | Net sales, Units, Return rate, Avg price from SALES_DAILY | add |
| 2 | line | Net sales by month, by region | add |
- Filters: <region, date range> · Surface: <Streamlit app> · Location: <prototype database.schema from standards, or ask>
- For an existing app: only list changes (add / change / remove); say "everything else stays as is".
```

## Choosing the surface (one-line reasons)
| Pick | When |
|---|---|
| **HTML report** | Fixed layout, read-mostly, shared in CoWork, no filters or only a few pre-set views; quickest to make and share. Static snapshot: refreshed when rebuilt. |
| **Streamlit app** | Filters, drill-down, interactivity, live data; the default for "dashboard". Viewers need a Snowflake login (or external embedding, if standards allow it). |
| **Agent** | Many different questions nobody can predict; users ask in plain English. Needs a semantic view over the data. Recommend alongside a dashboard, not instead of the agreed KPIs. |

Flag when access needs change the pick: viewers without logins means Streamlit external embedding (runs as a service account, so everyone sees the same rows) or an HTML report. Say this plainly if "different rows for different people" is also yes.
