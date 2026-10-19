# snow-bi-kit

A simple Cortex Code starter for **people coming from Tableau or Power BI** who have never written code. You describe the dashboard you want in plain English, and Cortex Code builds it in Streamlit on Snowflake.

## How it works

Open this folder in Cortex Code. The skills load on their own, so there is nothing to install. Then just talk to it:

| Step | Say | You get |
|---|---|---|
| Setup *(once, by a lead)* | "set up the BI kit" | Company standards (roles, warehouse, brand colours, fiscal calendar, trusted metrics, who takes hand-offs), saved to a Snowflake stage everyone reads |
| Start | "start a project" | Discovery for a **new** dashboard or an **existing** app, ending in `PROJECT_BRIEF.md`: outcome, audience, data, one number to check against, and a short build plan |
| Build | "build it" | A Streamlit app (or HTML report) built from the brief. Every chart has a "How this was built" panel showing its SQL |
| Check | "check my work" | A short report on speed, cost and safety: *Fix now*, *Worth considering*, *Looks fine* |
| Hand off | "hand this off" | Documentation and a production copy so the data team can take it over |

Every skill loads `bi-kit-library` for shared rules, so each skill folder is self-contained; to share through the skill catalog (Desktop, CLI or Snowsight), share all six. Build uses Snowflake's built-in Streamlit skill for the Streamlit and Snowflake mechanics; the kit adds the house style so every app looks and works the same way.

## Company standards on a stage

`bi-kit-setup` writes `company-standards.yaml` and, if you agree, uploads it to a stage (for example `@ANALYTICS.BI_KIT.STANDARDS`). Analysts put that stage path in `./bi-kit/standards-location.txt`, and every skill reads it from there. With no standards at all, the kit uses simple defaults and says so. Details: `standards-lookup.md` in the `bi-kit-library` skill.

## What's in the repo

```
.snowflake/cortex/skills/   bi-kit-setup, bi-kit-start, bi-kit-build, bi-kit-check, bi-kit-handoff,
                            and bi-kit-library (shared: voice, visual library, Tableau/Power BI terms,
                            picture read-back, where standards are found)
docs/design/                design spec and research
archive/                    more advanced pieces kept for later demos (plugin packaging, runtime and
                            self-check scripts, gallery app, tests, dev feedback add-on, tools)
```

## Requirements

- Cortex Code (Desktop recommended)
- A Snowflake connection with some data you can read

## Status

Simplified demo version; the skills no longer depend on anything in `archive/`. Not yet run end to end in a live session. Reading standards straight from a stage path is untested; the fallback is downloading the file into `./bi-kit/`.

## Before publishing publicly

- Remove `docs/internal/` (it names customers and people).
- Choose a license.
