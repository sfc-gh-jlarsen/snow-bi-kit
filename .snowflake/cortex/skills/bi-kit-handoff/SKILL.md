---
name: bi-kit-handoff
description: "Package a working snow-bi-kit prototype for the team that will industrialize it: README, HANDOFF.md, architecture diagram, inventory of every Snowflake object used (from Snowflake, not memory), grants needed, refresh and schedule needs, what's prototype-grade, open questions, the latest check results, and a production copy with debug panels off or removed. Use when: hand this off, the data team takes it from here, make this production, prototype is done, package for engineering. Triggers: hand off, hand this off, handoff pack, give this to the data team, productionize, industrialize this prototype. Do NOT use for: promoting/deploying to prod (the receiving team owns that), or scoping new work (bi-kit-start)."
---

# Hand it off

Package the prototype so the receiving team (company standards `handoff.receiving_team`, or ask) can take it over without a meeting. Writes documentation and a production **copy** only; never changes the prototype or Snowflake. Load the `bi-kit-library` skill first and follow its `voice.md`. Find company standards with `standards-lookup.md` (bi-kit-library).

## Steps
1. **Check first.** Run *bi-kit-check* on the project (quietly) and keep the report. If there are **Fix now** items, tell the analyst and offer to fix them before packaging; continue if they say so, listing them as open items.
2. **Inventory from Snowflake** (read-only, small warehouse):
   - Sources: every table, view or semantic view queried in the app, resolved to fully qualified names with `DESCRIBE`, plus owner (`SHOW OBJECTS LIKE … ` → owner) and row-access/masking policies (`POLICY_REFERENCES`).
   - Objects the prototype created: the Streamlit app / report / agent and any views or tables in the prototype schema (`SHOW STREAMLITS`, `SHOW VIEWS`, `SHOW TABLES IN SCHEMA <prototype>`), with grants (`SHOW GRANTS ON …`).
   - Compute: warehouse, compute pool, external access integration.
   The inventory must match what `SHOW` returns. Don't list anything you didn't see.
3. **Grants needed in production**: derive from the inventory: owner role for the app, `USAGE`/`SELECT` for each source, viewer roles from the brief. Write them as a short SQL block the receiving team can review (not run).
4. **Write the pack** in `handoff/` using `references/handoff-template.md`: `HANDOFF.md`, `README.md`, `architecture.md` (Mermaid), plus copies of `PROJECT_BRIEF.md` and `checks/CHECK_REPORT.md`. Include the receiving team's `handoff.required_fields` if standards list them.
5. **Production copy** in `handoff/production/`: copy the app/report and set `DEBUG = False` (or remove the `how_built` calls if standards `debug.production` is `remove`). Read the copy back to confirm no panel can render and nothing else changed.
6. **Prototype-grade list**: honest, specific: caching, hard-coded dates, owner's-rights shortcuts, missing data sources, manual refresh, sample-based charts, anything from *Worth considering*.
7. **Reply** (one screen): what's in the pack, the 3 most important things the receiving team must know, open items, and **What to do next**: "Send `handoff/` to <receiving team> via <intake>." Offer to draft the message.

## Rules
- Facts come from Snowflake and the project files. If something can't be verified, put it under *Open questions*, not in the inventory.
- No credentials in the pack. Grep `handoff/` with the patterns in `secret-patterns.md` from the `bi-kit-check` skill before replying.
- Keep the analyst's language for business meaning; keep object names exact.
