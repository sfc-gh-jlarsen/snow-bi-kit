---
name: bi-kit-build
description: "Build (or change) the dashboard, HTML report or app described in a snow-bi-kit PROJECT_BRIEF.md, using company standards, the kit's visual library, an optional reference picture, and 'how this was built' panels on every chart. Builds on Snowflake's bundled Streamlit skill for the Streamlit and Snowflake mechanics. Use when: the brief is approved and the analyst says build it, make the dashboard, change this chart, add a filter, make it look like this picture, match our brand. Triggers: build it, build my dashboard, build from my brief, change this chart, add a filter, make it look like this. Do NOT use for: scoping a new request (bi-kit-start), reviewing quality or security (bi-kit-check), or production hand-off (bi-kit-handoff)."
---

# Build it

Build what the brief says, to company standards, with "How this was built" panels on. Load the `bi-kit-library` skill first and follow its `voice.md`. Find company standards with `standards-lookup.md` (bi-kit-library).

**Division of labour:** load Snowflake's bundled `developing-with-streamlit-in-snowflake` skill for Streamlit and Snowflake mechanics (connection, caching, layout widgets, deployment). This skill adds only the kit's conventions, so every app looks and behaves the same way: the visual library, brand and formats, the "How this was built" panel, and the number to match. If the two disagree on mechanics, follow the Streamlit skill; on conventions, follow this one.

## Before building
1. Read `PROJECT_BRIEF.md`. If it's missing or not approved, offer *start a project* first. For a tiny ask ("one chart from this query") you may proceed after confirming outcome, data and look in one question.
2. Read company standards (if any). Note warehouse, prototype location, brand, formats, fiscal calendar, debug policy.
3. **Confirm the build plan** from the brief in library names (`visuals.md` (bi-kit-library)), each mapped to fields. Ask once: "Build this?"

## Building
4. **Surface** (from the brief):
   - **Streamlit app**: follow `references/build-patterns.md`.
   - **HTML report**: follow `references/html-report.md`.
   - **Agent**: hand over to the bundled `agent-studio` skill with the brief's measures and data.
5. **Every visual** goes through the app's `run_visual(...)` helper (`references/build-patterns.md`) so it gets a "How this was built" panel. Filters become **query parameters**, never string-built SQL. Pandas steps after the query go in a named function passed as `transform`, so the panel shows them.
6. **Number to match**: show it on the matching KPI with `tie_out(...)`.
7. Use the library's build notes, brand palette and formats; the fiscal calendar for YTD/QTD.
8. **Existing app**: change only what the build plan lists. Keep the app's existing structure; add the helper and panels to the visuals you touch.

## Checking before you say it's done (quietly)
9. Read the app back: every chart/KPI/table goes through `run_visual`; no user input in f-string SQL; no passwords or admin roles.
10. If a shell and connection are available, run it (`streamlit run app/streamlit_app.py --server.headless true`) and fix errors. Re-run each visual's SQL yourself and compare row counts and totals to what the app shows.
11. Check the number to match. If it differs, say so plainly with the difference and the likely reason (filter, definition, period); never adjust numbers to force a match.

## Run / deploy
12. Offer to run it locally or deploy it to the prototype location from standards using the bundled Streamlit skill. Ask before creating anything in Snowflake.

## Reply (one screen)
- What was built (visuals by name), where it is, how to open it.
- Number to match: **matches** / **differs by X (why)**.
- Anything assumed or left out ("needs a source: plant returns").
- **What to do next**: "Look it over; tell me what to change. When you're happy, say *check my work*."

## Changes later
For "change this chart / add a filter / make it look like this", edit the app the same way (steps 5–11).
