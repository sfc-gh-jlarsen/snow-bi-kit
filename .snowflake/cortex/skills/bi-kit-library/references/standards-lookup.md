# Finding company standards

Company standards are one YAML file (`company-standards.yaml`) written by *bi-kit-setup*. A company usually keeps the shared copy on a Snowflake stage so every analyst reads the same rules. Every skill looks for it the same way:

1. **This project**: `./bi-kit/company-standards.yaml`. Use it if present.
2. **The company stage**: if `./bi-kit/standards-location.txt` exists, it holds one line with a stage path, e.g. `@ANALYTICS.BI_KIT.STANDARDS/company-standards.yaml`.
   - Try reading the stage path directly with the read tool.
   - If that doesn't work, download it from a shell: `snow stage copy @ANALYTICS.BI_KIT.STANDARDS/company-standards.yaml ./bi-kit/`, then read the local copy. Say once that you downloaded it.
3. **Neither**: continue with safe prototype defaults (the analyst's current role, warehouse, database and schema; default Streamlit colours; calendar year). Say so once: "I didn't find company standards, so I'm using simple defaults. Ask your lead to run *set up the BI kit* if you have house rules."

Never ask an analyst to fill in standards themselves. Blank keys are fine; use the default and move on.
