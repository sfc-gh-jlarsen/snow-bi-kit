# BI terms → snow-bi-kit

When an analyst uses a Tableau or Power BI term, translate it with this table. Answer in their words first, then show how it's done here. Don't lecture.

| They say (Tableau / Power BI) | What it means | How we do it here |
|---|---|---|
| Data source / Dataset / Semantic model | The governed tables and joins a report sits on | A **semantic view** if one exists for the data (preferred: definitions are shared); otherwise the named tables/views in the brief |
| Extract vs Live | Copy of data vs querying the source | Always live against Snowflake; "extract-like" speed comes from caching (`st.cache_data` with a TTL) or a dynamic table the data team owns |
| Calculated field / Measure (DAX) | A formula on the data | A SQL expression in the visual's query, or a **metric** in the semantic view (preferred when others will reuse it) |
| LOD expression (FIXED / INCLUDE / EXCLUDE) | Aggregate at a different grain than the view | A window function (`SUM(x) OVER (PARTITION BY ...)`) or a subquery/CTE at the needed grain |
| Table calculation (running total, % of total, rank) | Computed over the result set | Window functions in SQL (`SUM() OVER (ORDER BY)`, `RATIO_TO_REPORT`, `RANK()`). If done in pandas, it's shown in the debug panel |
| Parameter / What-if | User-controlled input | A Streamlit widget passed as a **query parameter** |
| Quick filter / Slicer | Filter control | Streamlit widget (selectbox, multiselect, date range) → query parameter |
| Context filter / Report-level filter | Filter applied before everything else | A `WHERE` clause shared by all visuals (one place in the app) |
| Drill-down / Drill-through | Click to see detail | Selection → second visual with the selection as a parameter |
| Tooltip | Hover details | Altair `tooltip=[...]` |
| Dashboard actions / Cross-filter | One chart filters another | Shared widget, or an Altair selection within a chart |
| Row-level security (RLS) / User filter | Different people see different rows | A Snowflake **row access policy** on the table, plus caller's-rights connection (preview) or per-role views. Never filter by username in app code |
| Workbook / Report / .pbix | The thing you publish | A **Streamlit app** (interactive), an **HTML report** (static, shareable in CoWork), or an **agent** (questions in plain English) |
| Publish to Server / Service | Share with others | Grant a role access to the app; HTML reports publish to CoWork with role grants |
| Subscription / Email schedule | Get it in your inbox | Not built into Streamlit; CoWork automations or a scheduled task the data team owns (note in hand-off) |
| Refresh schedule | How fresh the data is | Query is live; the underlying table's freshness is the data team's pipeline (record need in the brief) |
| YoY / YTD / MTD / QTD | Period comparisons | SQL with explicit date windows against a calendar; **fiscal** calendar from company standards when defined |
| Rolling 12 / moving average | Smoothed trend | `AVG(...) OVER (ORDER BY period ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)` |
| Fiscal year / 4-4-5 calendar | Company's own calendar | From company standards (`fiscal_calendar`); never assume calendar = fiscal |
| Blending / Relationships | Combining sources | SQL joins on declared keys; if the grain differs, aggregate each side first (avoid double counting) |
| Sets / Groups | Ad-hoc buckets of members | `CASE` expression in SQL (kept in the query so the debug panel shows it) |
| Bins | Numeric buckets | `WIDTH_BUCKET` in SQL |
| Reference line / band | Target or average line | Layered `mark_rule` / `mark_rect` |
| Formatting (number/date) | Display formats | From company standards (number, currency, date formats) |
| Theme / Template | Look and feel | Brand block in company standards (palette, fonts, logo) |
