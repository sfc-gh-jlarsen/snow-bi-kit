# Checking the data the analyst named

Goal: confirm the sources exist, the analyst's role can read them, and what they look like. Keep it cheap (the current warehouse, `LIMIT`/`SAMPLE`). Read-only.

## For each named object
1. **Resolve the name.** Accept `DB.SCHEMA.OBJECT`, `SCHEMA.OBJECT` or `OBJECT`. For partial names use `SHOW OBJECTS LIKE '<name>' IN ACCOUNT` (or `IN DATABASE <db>` if they gave one) and pick the exact match; if several match, list them and ask.
2. **Can they read it?** `DESCRIBE TABLE|VIEW|SEMANTIC VIEW <fqn>`, then `SELECT * FROM <fqn> LIMIT 1`. If either fails with "does not exist or not authorized", report: "I can't read X with your current role (`<role>`). Ask the owner for access, or tell me another source." Don't try other roles.
3. **Profile lightly** (one query, small warehouse):
   - row count: `SELECT COUNT(*)` only if `SHOW TABLES` doesn't already give `rows`; never on views over very large data (use `SAMPLE (10000 ROWS)` instead);
   - date range on the obvious date column (`MIN`, `MAX`);
   - likely grain: the column set that's unique (check one candidate with `COUNT(*) = COUNT(DISTINCT ...)` on a sample);
   - columns that match the measures in the brief.
4. **Semantic view check.** `SHOW SEMANTIC VIEWS IN ACCOUNT` filtered to those whose base tables include the named tables (use `DESCRIBE SEMANTIC VIEW`), plus any in standards `trusted_data.semantic_views`. If one covers the data, recommend it: "Your company already defines these measures in `<sv>`. Building on it keeps the numbers consistent."
5. **Sensitivity.** If the account uses classification, `SELECT * FROM TABLE(<db>.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS('<fqn>', 'table'))` and note PII/confidential columns. If it errors, skip silently.

## Pasted SQL
- Run it with `LIMIT 100` wrapped as a subquery to confirm it works and capture the columns. Keep the original text verbatim in the brief.

## "It's the data behind my Tableau/Power BI report"
- Ask for the workbook/data source file (`.twb/.twbx/.tds/.pbit/.pbix`) or the table names. With a file, read connection details for the Snowflake tables it uses. For a semantic view from it, point them to the bundled semantic-view import (agent-studio). Don't guess tables from a dashboard picture.

## Not found / nothing named
- Offer: "I couldn't find `X`. Want me to search for similar tables or semantic views?" Search only on yes (object search / semantic view search), and show at most 5 candidates with one line each.

## Output block (goes in the brief and the reply)
```
Data check
- SALES_DB.CORE.SALES_DAILY: readable · 41.2M rows · 2023-01-01 → 2026-10-12 · one row per plant per product per day
- Covers measures: net sales (NET_SALES_USD), units (UNITS). Not found: return rate (needs a source)
- Governed option: SALES_DB.MART.SV_SALES already defines net sales. Recommended.
```
