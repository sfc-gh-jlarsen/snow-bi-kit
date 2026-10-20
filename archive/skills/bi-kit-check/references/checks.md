# The three checks

Each check reports findings as: severity (fix_now | consider | fine), what, where, evidence, why it matters (analyst words), fix. Read-only.

## Speed
Evidence sources, cheapest first: the run time and row counts in each "How this was built" panel (run the app) → `INFORMATION_SCHEMA.QUERY_HISTORY_BY_USER` / `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` for the app's queries → the bundled `workload-performance-analysis` skill for per-query detail (spilling, pruning, cache use).

Look for:
- **Recomputed on every view**: slow (> ~3 s) or large-scan queries with no caching in the app and data that's only daily/monthly fresh (brief). Fix: `st.cache_data(ttl=...)` around the call, or a summary table/dynamic table owned by the data team.
- **Scanning far more than shown**: rows returned small but bytes scanned / partitions scanned large; filters not on clustered/date columns. Fix: filter on the date column first; ask the data team about clustering.
- **Row-level data pulled into Python**: rows returned ≫ rows shown (aggregation done in pandas). Fix: aggregate in SQL.
- **Same query repeated** across visuals with different `GROUP BY`. Fix: one query + transforms, or a shared CTE.
- **Wrong size compute**: warehouse not the standards default; a large warehouse for small queries. Fix: use the standards warehouse.
- **Box plots / histograms on millions of rows**. Fix: `SAMPLE ... SEED`, or pre-bin in SQL.

## Build
- **Standards**: built in the prototype location; app owner role is not personal/admin when shared; brand palette and formats used; fiscal calendar used for fiscal periods.
- **Library**: every visual is a type in `visuals.md` (bi-kit-library); discouraged visuals replaced or justified.
- **Truth**: every visual goes through `run_visual` and has a "How this was built" panel; no chart drawn from some other query; parameters used for filters (no f-string user input in SQL); number to match present and **matches** (a mismatch is fix_now).
- **Split or consolidate**:
  - *Split* when one app serves clearly different audiences or questions (different filters, different viewers), or a page has > ~8 visuals.
  - *Consolidate* when several apps/visuals query the same tables with the same filters (point to a shared semantic view or one shared query).
  - *Use the governed source* when a semantic view in standards covers the data but the app re-implements its measures.
- **Readability**: titles say what and over what period; units on axes; no colour-only meaning.

## Security
1. **Pattern scan** (`secret-patterns.md`): passwords, tokens/keys, private keys, cloud keys, connection strings with passwords, admin roles in code (fix_now); hard-coded users, browser login, `.env` files (consider).
2. **Debug panels in a shared app**: app granted to viewer roles (`SHOW GRANTS ON STREAMLIT <fqn>`) and `DEBUG = True` → fix_now (panels expose SQL and object names).
3. **Who sees what**:
   - Owner's-rights app (default `st.connection("snowflake")`) over data with row-level rules (brief says "different rows for different people", or a row access policy exists on the source: `POLICY_REFERENCES`) → fix_now: every viewer sees the owner's rows. Fix: caller's-rights connection (preview), per-role views, or separate apps.
   - App granted to roles beyond the brief's audience → consider.
   - External (no-login) embedding when standards `external_sharing_allowed: false` → fix_now.
4. **Sensitive columns** (classification tags, or obvious PII like email/phone/name) shown in a table to broad viewer roles without masking → consider (fix_now if standards say so).
5. **SQL built from user input** with f-strings/concatenation → fix_now (use parameters).

Explain each in plain words. Example: "Anyone with access to this app sees every region's numbers, because it runs with your access, not theirs."
