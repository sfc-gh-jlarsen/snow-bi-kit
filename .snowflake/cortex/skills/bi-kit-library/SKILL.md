---
name: bi-kit-library
description: "Shared reference for the snow-bi-kit skills (bi-kit-setup, bi-kit-start, bi-kit-build, bi-kit-apply-standards, bi-kit-handoff): plain-English voice for analysts new to code, the visual library (chart types and when to use them), Tableau/Power BI terms mapped to Snowflake and Streamlit, how to read a reference picture, and where company standards are found. Load this whenever another bi-kit skill runs. Triggers: bi-kit library, which chart should I use, visual library, Tableau term, Power BI term, what's the Snowflake word for. Do NOT use on its own to build or scope a dashboard (use bi-kit-start or bi-kit-build)."
---

# snow-bi-kit library

Shared rules and reference used by every bi-kit skill. Read only the file you need, when you need it.

| File | Read when |
|---|---|
| `references/voice.md` | Always: how to talk to analysts (plain words, short replies, "What to do next") |
| `references/standards-lookup.md` | Before using company standards: where to find them (project file, then stage), and defaults if none |
| `references/visuals.md` | Choosing, naming or building a chart, KPI or table; every visual uses a name from here |
| `references/bi-terms.md` | The analyst uses Tableau or Power BI words (workbook, calculated field, measure, extract…) |
| `references/how-built-helper.md` | Writing or retrofitting a Streamlit app: the `run_visual` / `how_built` helper to paste in |
| `references/secret-patterns.md` | Before saying an app is done or handing it off: grep for passwords, keys, admin roles |
| `references/image-readback.md` | The analyst gives a screenshot, mockup, slide or PDF of the look they want |

## Rules
- These files are the single copy. Other bi-kit skills refer to them by name; don't copy their content into project files.
- If this skill isn't installed, tell the analyst once: "The bi-kit-library skill is missing; install it alongside the other bi-kit skills." Then continue as best you can.
