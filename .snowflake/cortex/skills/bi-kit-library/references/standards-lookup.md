# Finding company standards

Company standards are one YAML file, `company-standards.yaml`, written by *bi-kit-setup*. They cover how apps look and behave (brand, formats, fiscal calendar, trusted data, house rules), not where apps deploy. Every skill finds them the same way, with no setup on the analyst's side:

1. **This project** (handy for testing): `./bi-kit/company-standards.yaml`. Use it if present and say so once.
2. **The company stage, by convention**: a stage named `STANDARDS` in a schema named `BI_KIT`, in any database (e.g. `@ANALYTICS.BI_KIT.STANDARDS/company-standards.yaml`).
   - Find it: `SHOW STAGES LIKE 'STANDARDS' IN ACCOUNT`, keep rows where `schema_name = 'BI_KIT'`.
   - Confirm the file: `LIST @<db>.BI_KIT.STANDARDS PATTERN = '.*company-standards[.]yaml'`.
   - **One match**: use it. **Several**: ask once (**single**, one option per stage). **None visible**: go to step 3.
   - Read it with the read tool on the stage path. If that doesn't work, download it from a shell (`snow stage copy @<db>.BI_KIT.STANDARDS/company-standards.yaml ./bi-kit/`) and read the local copy.
3. **Neither**: continue with simple defaults (Streamlit colours, the formats in the template, calendar year, panels on). Say once: "I didn't find company standards, so I'm using simple defaults. Ask your lead to run *set up the BI kit* if you have house rules." If a `BI_KIT` schema exists but the stage isn't readable, say: "Your company's standards look like they're at `<db>.BI_KIT.STANDARDS`, but your role can't read them. Ask your lead for read access."

Ignore keys you don't recognise (older standards files also listed environments, roles and compute; those now belong to each app's deployment config).

Never ask an analyst to fill in standards themselves. Blank keys are fine; use the default and move on.
