---
name: bi-kit-setup
description: "One-time setup for snow-bi-kit: an analytics lead records company standards (where prototypes live, roles, warehouse, brand colours and formats, fiscal calendar, trusted metric definitions, who receives hand-offs, debug policy) and publishes them to a Snowflake stage for everyone to use. Use when: setting up the BI kit, company standards, house rules, brand setup for dashboards, update our standards. Triggers: set up bi kit, bi-kit setup, company standards, our brand colors for dashboards, update company standards. Do NOT use for: building a dashboard (bi-kit-build) or Snowflake account/role administration."
---

# Company standards setup

For an analytics lead or admin, run once (about 15 minutes), then again only when standards change. Every other kit command reads the result.

Load the `bi-kit-library` skill first and follow its `voice.md`. Where standards are looked up: `standards-lookup.md` (bi-kit-library).

## Steps

1. **Find what exists** using the lookup in `standards-lookup.md`. If a file exists, show a 6-line summary and ask what to change. Otherwise start from `references/company-standards.template.yaml`. For a quick demo, offer `references/company-standards.example.yaml` (fictional company) instead of the interview.
2. **Interview in four batches** (ask-user-question, max 4 questions each, defaults pre-filled, "skip for now" allowed except REQUIRED keys):
   - **Where things live**: company name and standards owner; prototype database and schema pattern; dev/test/prod database and schema (optional now).
   - **Who can do what**: build role; shared-app owner role (must not be a personal or admin role); viewer roles; whether no-login (external) sharing is allowed; who may publish to CoWork; how row-level security is done today.
   - **Look and feel**: primary colour and chart palette (accept hex codes, a brand-guide screenshot, or "use defaults"); fonts; number, currency, percent and date formats; language and timezone; fiscal calendar (calendar year, shifted start month, or 4-4-5 with a calendar table).
   - **Trust and hand-off**: preferred semantic views or certified tables; standard metric definitions (name, definition, source column); receiving team and intake (Jira project, email, channel); extra fields they require; debug policy (on in prototypes; production off or remove).
3. **Confirm against Snowflake (read-only).** For the roles, warehouse, databases, compute pool and semantic views given, run `SHOW ROLES LIKE`, `SHOW WAREHOUSES LIKE`, `SHOW DATABASES LIKE`, `SHOW COMPUTE POOLS LIKE`, `SHOW SEMANTIC VIEWS LIKE`. Report anything missing as a short "check these" list. Don't block on it.
4. **Write the file** to `./bi-kit/company-standards.yaml` from the template, keeping comments; blank anything skipped. Re-read it and check every REQUIRED key in the template is filled.
5. **Publish to a stage (ask first).** Ask for the stage location (suggest `<prototype database>.BI_KIT.STANDARDS`). After they confirm:
   - `CREATE SCHEMA IF NOT EXISTS` / `CREATE STAGE IF NOT EXISTS <db>.<schema>.<stage>` (show the SQL before running).
   - Upload: `snow stage copy ./bi-kit/company-standards.yaml @<db>.<schema>.<stage>/` from a shell, or `PUT file://... @<stage> AUTO_COMPRESS=FALSE OVERWRITE=TRUE`.
   - Suggest `GRANT READ ON STAGE ... TO ROLE <build_role>` so analysts can read it (show, don't run unless asked).
   - Write `./bi-kit/standards-location.txt` with the full stage path, and tell the lead to share that one line with analysts.
6. **Reply** with one screen: what's set, what's still blank, where it's published, and **What to do next** (e.g. "Give analysts `standards-location.txt`, then they say *start a project*").

## Rules
- Never put passwords, tokens or keys in standards.
- No values from memory or other customers; only what the lead gives you or confirms.
- The stage copy is the single source. To change standards, edit and re-upload; don't edit copies in projects.
