# snow-bi-kit

A simple Cortex Code starter for **people coming from Tableau or Power BI** who have never written code. You describe the dashboard you want in plain English, and Cortex Code builds it in Streamlit on Snowflake.

## How it works

Open this folder in Cortex Code. The skills load on their own, so there is nothing to install. Then just talk to it:

| Step | Say | You get |
|---|---|---|
| Setup *(once, by a lead)* | "set up the BI kit" | Company standards for how apps look and behave (brand, formats, fiscal calendar, trusted data and metrics, house rules), saved to a Snowflake stage everyone reads |
| Start | "start a project" | Discovery for a **new** dashboard or an **existing** app, ending in `PROJECT_BRIEF.md`: outcome, audience, data, one number to check against, and a short build plan |
| Build | "build it" | A Streamlit app (or HTML report) built from the brief. Every chart has a "How this was built" panel showing its SQL |
| Apply standards | "apply our standards to this app" | An existing Streamlit app restyled to company standards, with a "How this was built" panel under each chart. Same numbers, changes shown before saving |
| Hand off | "hand this off" | Documentation and a production copy so the data team can take it over |

Every skill loads `bi-kit-library` for shared rules, so each skill folder is self-contained; to share through the skill catalog (Desktop, CLI or Snowsight), share all six. Build uses Snowflake's built-in Streamlit (or Apps) skill for the mechanics, including deployment: where an app lives, its warehouse, compute and roles are set in the project's deployment config (`snowflake.yml` / `app.yml` targets), not in the kit's standards. The kit adds the house style so every app looks and works the same way.

## Company standards on a stage

`bi-kit-setup` writes `company-standards.yaml` and uploads it to a stage named `STANDARDS` in a schema named `BI_KIT`, in a database you choose (for example `@ANALYTICS.BI_KIT.STANDARDS`). Every skill finds it by that convention, so analysts need nothing but read access to the stage. With no standards at all, the kit uses simple defaults and says so. Details: `standards-lookup.md` in the `bi-kit-library` skill.

## What's in the repo

```
.snowflake/cortex/skills/   bi-kit-setup, bi-kit-start, bi-kit-build, bi-kit-apply-standards, bi-kit-handoff,
                            and bi-kit-library (shared: voice, visual library, Tableau/Power BI terms,
                            picture read-back, the how-built helper, secret patterns,
                            where standards are found)
docs/design/                design spec and research
archive/                    more advanced pieces kept for later demos (the check skill, plugin packaging, runtime and
                            self-check scripts, gallery app, tests, dev feedback add-on, tools)
```

## Requirements

- Cortex Code (Desktop recommended)
- A Snowflake connection with some data you can read

## Status

Simplified demo version; the skills no longer depend on anything in `archive/`. Not yet run end to end in a live session. Finding the standards stage by convention is tested; reading the file straight from the stage is not (the fallback downloads it into `./bi-kit/`).

## Before publishing publicly

- Remove `docs/internal/` (it names customers and people).
- Choose a license.
