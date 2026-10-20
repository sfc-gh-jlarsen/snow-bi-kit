# HTML report pattern (snow-bi-kit)

Static, read-mostly reports shared in CoWork. Same truth rules as Streamlit: every number comes from a recorded query and carries a `<details>` "How this was built" panel while `DEBUG` is on.

## How to build
1. Write `report/build_report.py` with the same `run_visual` idea as `build-patterns.md` (run SQL with parameters, optional `transform`, keep the SQL and row counts), using a Snowpark session from the default connection:
   ```python
   from snowflake.snowpark import Session
   session = Session.builder.getOrCreate()
   ```
2. For each visual, write the chart as **inline SVG** (bars, lines, sparklines and bullets are simple rect/polyline/line), followed by a `<details><summary>How this was built</summary><pre>SQL…</pre>…</details>` block when `DEBUG` is on.
3. **No CDN or external scripts, no remote images, no inline event handlers.** CoWork reports render in a strict sandbox; follow the bundled `html-authoring` skill.
4. Run `build_report.py` to produce `report/report.html`, then publish with the bundled report-publishing skill, sharing with the roles the analyst names (never PUBLIC unless asked).

## Notes
- A report is a snapshot. Show "Data as of <timestamp>" at the top; re-run the build to refresh.
- Production version: rebuild with `DEBUG = False`.
- Keep it to one page where possible: KPIs, one or two trends, one breakdown, one table.
