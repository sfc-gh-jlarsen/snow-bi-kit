---
name: bi-kit-apply-standards
description: "Apply company standards to an existing Streamlit app: brand colours, fonts and number/date formats, plus a 'How this was built' accordion (st.expander) under each chart, KPI and table showing its SQL. Keeps the same numbers and layout; shows the changes before saving. Use when: an analyst already has a Streamlit app and wants it to match house style, add how-this-was-built panels, make my app match our standards, retrofit an existing dashboard. Triggers: apply our standards, apply standards to this app, add how this was built, add the accordions, make this app match our brand, retrofit my streamlit app. Do NOT use for: new dashboards or changing what an app shows (bi-kit-start, then bi-kit-build), deployment (bundled Streamlit skill)."
---

# Apply standards to an existing app

Make an existing Streamlit app follow company standards and show how each number was made, **without changing what it shows**. No brief needed.

Load the `bi-kit-library` skill first and follow its `voice.md`. Find company standards with `standards-lookup.md` (bi-kit-library). The helper code is `how-built-helper.md` (bi-kit-library).

## The promise
- Same numbers, same charts, same layout, same filters. Only the look changes and panels are added.
- Every change is shown before it's saved. Nothing in Snowflake is created or changed.

## Steps

1. **Find the app.** If it isn't clear, ask (**text**): "Which app? (folder, file, or deployed app name)". For a deployed app, `SHOW STREAMLITS LIKE '<name>' IN ACCOUNT`, `DESCRIBE STREAMLIT <fqn>`, and read the source if the role can; otherwise ask for the folder.
2. **Read it and list what you'll touch**, in plain words:
   - **Visuals with a clear query** (`session.sql(...)`, `st.connection(...).query(...)`, `pd.read_sql(...)` over the Snowflake connection) → will get a panel.
   - **Visuals you can't trace to one query** (data from a file, built over several steps, from an API) → listed as "no panel here, and why". Don't rewrite them.
   - **Look**: colours, number and date formats that differ from standards.
   - **Safety**: grep with `secret-patterns.md` (bi-kit-library). Report anything found; offer to fix it as a separate, clearly marked change.
3. **Confirm the plan** (**single**: *Go ahead* / *Only the panels* / *Only the look* / *Let me pick*). If they pick *Let me pick*, ask (**multi**) which visuals to include.
4. **Make the changes:**
   - Add the helper block (`run_visual`, `how_built`, `tie_out`, `DEBUG`, `BRAND`) once near the top, filled from standards. Keep the app's existing session/connection if it has one; point `get_session()` at it rather than adding a second.
   - For each traced visual: move its query into `run_visual(title, sql, params=...)`, draw from the returned `df` exactly as before, and add `how_built(info)` right under it. Existing pandas steps after the query become a named `transform` function so the panel shows them.
   - **User input in f-string SQL**: convert to `?` parameters (same results, safer). Call this out in the summary.
   - Apply brand palette (Altair theme or the chart library's colour argument), font and formats. Don't change chart types, titles' meaning, or layout.
   - Set `DEBUG` from standards `house_rules.how_built_panels` (default on).
5. **Show the changes** as a short list per visual, plus the diff if they want it. Save only after they agree (**single**: *Save it* / *Change something*).
6. **Check it still works.** If a shell and connection are available, run it headless (`streamlit run <app> --server.headless true`) and fix errors. Re-run each panel's SQL and compare row counts and totals with what the original query returned; they must match. If anything differs, say so plainly and undo that visual's change.
7. **Reply** (one screen): visuals that got panels, visuals that didn't (and why), look changes, safety fixes, and **What to do next**: "Open the app and expand *How this was built* under any chart. To share it with a team, say *hand this off*."

## Rules
- Never change a query's logic, a filter's behaviour, or a number. Moving SQL into `run_visual` and switching to parameters are the only query edits.
- Don't add visuals, remove visuals, or reorder the page.
- If the app isn't Streamlit (e.g. an HTML report or an App Runtime/Next.js app), say so, apply only brand and formats where obvious, and suggest the matching bundled skill for anything more.
