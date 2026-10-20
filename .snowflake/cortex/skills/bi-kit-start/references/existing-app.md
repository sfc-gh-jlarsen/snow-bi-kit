# Discovery for an existing app or report

Goal: understand what's already there before asking anything, so the analyst only answers what the code can't tell you. Read-only.

## 1. Find it
- **Local folder or file**: read `streamlit_app.py` (or the main `.py`), any other pages (`pages/`), `environment.yml` / `requirements.txt` / `pyproject.toml`, and any `PROJECT_BRIEF.md` or README.
- **Deployed Streamlit app**: `SHOW STREAMLITS LIKE '<name>' IN ACCOUNT`, then `DESCRIBE STREAMLIT <fqn>` for its location, main file and warehouse. Read the source from its stage or workspace if the analyst's role can.
- **HTML report**: read the `.html` and any script that builds it.
- If you can't find or read it, say so and ask them to point you at the folder or paste the code.

## 2. Inventory (from the code, not guesses)
List, in plain words:
- **Data sources**: every table, view or semantic view queried (fully qualified where the code says so). Note SQL that's built from user input with f-strings; mention it so build fixes it.
- **What's on screen**: each chart, KPI and table, named with `visuals.md` (bi-kit-library) entries, and the measure behind each.
- **Filters and pages**.
- **How it connects**: `get_active_session()`, `st.connection("snowflake")`, or a hard-coded login (flag it; build will fix it).

Run the data check (`data-intake.md`) on the sources you found.

## 3. Show it back, then ask
Show the inventory as a short numbered list ("Here's what your app does today"), then ask in one ask-user-question call:

| # | Question | Type |
|---|---|---|
| 1 | **What should change?** New charts, fixes, a different look, new data, new audience | text |
| 2 | **Is anything wrong today?** Numbers that look off, slowness, confusing parts | text, default `"Nothing I know of"` |
| 3 | **Number to match**: one number you trust from this app or another report | text |
| 4 | **Audience**: same people as now? | single: Same people / Different people / Same people, but they need to see different rows |

## 4. Into the brief
- Fill `PROJECT_BRIEF.md` as usual; set **Starting point** to the existing app's location.
- In **Build plan**, list only the changes, each marked *add*, *change* or *remove*, and say what stays as is.
