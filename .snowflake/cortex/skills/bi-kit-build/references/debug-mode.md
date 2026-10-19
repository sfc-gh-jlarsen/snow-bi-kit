# "How this was built" panels

The panels are how an analyst (and later the data team) sees **exactly how each number was made**. On for prototypes, off for production (company standards `debug`, default: on in prototypes, off in production).

## What every panel shows (collapsed by default)
- The exact SQL that ran, with parameter values.
- Any Python step applied after the query (the `transform` function's code).
- Rows returned, rows shown, run time.
- For the KPI tied to the brief's number to match: expected, actual, **matches** / **differs by X**.

Streamlit uses `st.expander`; HTML reports use `<details>`.

## Keeping panels truthful
- The panel is built from the same `info` that `run_visual` returned with the chart's data. Never write a panel by hand next to the code.
- Every visual draws only from its own `run_visual` result.
- When checking your work, re-run each panel's SQL and compare totals to what's on screen. Results that change between runs (`CURRENT_TIMESTAMP`, `RANDOM()`, `SAMPLE` without a seed) should be made deterministic (`SAMPLE ... SEED (42)`, pass "now" as a parameter).

## Production version (bi-kit-handoff)
- Copy the app and set `DEBUG = False`. Queries and charts are unchanged; only the panels disappear.
- `bi-kit-check` flags any **shared** app (granted to viewer roles) with `DEBUG = True`: panels expose SQL and object names to viewers.
