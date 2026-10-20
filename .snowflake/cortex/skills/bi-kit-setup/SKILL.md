---
name: bi-kit-setup
description: "One-time setup for snow-bi-kit: an analytics lead records company standards for Streamlit (and Snowflake App Runtime) apps (brand colours and fonts, number and date formats, fiscal calendar, trusted semantic views and metric definitions, house rules like 'How this was built' panels) and publishes them to a Snowflake stage everyone reads. Use when: setting up the BI kit, company standards, house rules, brand setup for dashboards, update our standards. Triggers: set up bi kit, bi-kit setup, company standards, our brand colors for dashboards, update company standards. Do NOT use for: deployment targets, roles, warehouses or compute (those belong to each app's deployment config and the bundled Streamlit/Apps skills), building a dashboard (bi-kit-build), or Snowflake account/role administration."
---

# Company standards setup

For an analytics lead, run once (about 10 minutes), then again only when standards change. Every other kit command reads the result.

Load the `bi-kit-library` skill first and follow its `voice.md`. Where standards are looked up: `standards-lookup.md` (bi-kit-library).

**Scope:** standards say how apps **look and behave**: brand, formats, fiscal calendar, trusted data and metric definitions, house rules. They do **not** say where apps deploy, which roles own them, or which warehouse or compute pool they use. Those belong in each project's deployment config (`snowflake.yml` / `app.yml` targets), which the bundled Streamlit and Apps skills manage. If the lead starts listing those, say so in one line and move on.

## Steps

1. **Find what exists** using `standards-lookup.md`. If a file exists, show a 6-line summary and ask what to change (**single**: *Update it* / *Start over* / *Leave it*). Otherwise ask (**single**): *Interview me* / *Use the example company for a demo* (`references/company-standards.example.yaml`).
2. **Interview** with ask-user-question (max 4 questions per call). Use the type listed for each question. Every key is optional; "skip" keeps the default.

   **Question types:** **text** = typed answer, always with `defaultValue`. **single** = one pick (`type: "options"`). **multi** = several picks (`type: "options"`, `multiSelect: true`). Lists that come from Snowflake (semantic views) are looked up first with a read-only `SHOW`; "Something else" covers anything missing.

   **Batch 1: Who and look**
   | Question | Type |
   |---|---|
   | Company name | text |
   | Standards owner (person or team) | text |
   | Brand colours and font (hex codes and font name, or attach a brand-guide screenshot) | text, default: Streamlit defaults |
   | Logo on a stage (optional) | text, default `""` |

   **Batch 2: Formats**
   | Question | Type |
   |---|---|
   | Number / currency / percent / date formats | text, default `#,##0` · `$#,##0` · `0.0%` · `YYYY-MM-DD` |
   | Language and timezone | text, default `English · America/New_York` |
   | Fiscal calendar | single: Calendar year / Year starts in another month / 4-4-5 with a calendar table |
   | "How this was built" panels in production apps | single: Turned off (default) / Removed from the code |

   Follow-up only if needed: fiscal start month (**single**, Jan–Dec) or calendar table name (**text**).

   **Batch 3: Trusted data and hand-off**
   | Question | Type |
   |---|---|
   | Trusted semantic views or certified tables | multi (from `SHOW SEMANTIC VIEWS IN ACCOUNT`); "Something else" for tables |
   | Standard metric definitions (one per line: name: definition, source column) | text, default `""` |
   | Anything else every app should follow (plain words) | text, default `""` |
   | Who usually takes prototypes to production, and how to reach them (optional) | text, default `""` |

3. **Write the file** to `./bi-kit/company-standards.yaml` from `references/company-standards.template.yaml`, keeping comments; leave skipped keys at their defaults.
4. **Publish to the stage (ask first).** The kit finds standards by convention: a stage named `STANDARDS` in a schema named `BI_KIT`. Ask (**text**) which database to use, defaulting to one the lead's role can see (`SHOW DATABASES`), e.g. `ANALYTICS` → `ANALYTICS.BI_KIT.STANDARDS`. After they confirm, show then run:
   - `CREATE SCHEMA IF NOT EXISTS <db>.BI_KIT;`
   - `CREATE STAGE IF NOT EXISTS <db>.BI_KIT.STANDARDS;`
   - Upload: `snow stage copy ./bi-kit/company-standards.yaml @<db>.BI_KIT.STANDARDS/` from a shell, or `PUT file://./bi-kit/company-standards.yaml @<db>.BI_KIT.STANDARDS AUTO_COMPRESS=FALSE OVERWRITE=TRUE`.
   - Show (don't run unless asked) the grants analysts need to find and read it: `GRANT USAGE ON DATABASE <db> ...`, `GRANT USAGE ON SCHEMA <db>.BI_KIT ...`, `GRANT READ ON STAGE <db>.BI_KIT.STANDARDS TO ROLE <analyst role>;`
   - Then delete the local `./bi-kit/company-standards.yaml` if they agree, so the stage is the only copy analysts use.
5. **Reply** with one screen: what's set, where it's published, and **What to do next**: "Grant analysts read access to the stage; then they say *start a project*. No other setup needed on their side."

## Rules
- Never put passwords, tokens or keys in standards.
- No values from memory or other customers; only what the lead gives you or confirms.
- The stage copy is the single source. To change standards, re-run setup; it re-uploads.
