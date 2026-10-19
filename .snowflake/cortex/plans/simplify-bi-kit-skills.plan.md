# Plan: Simplify bi-kit skills

## Flow
`setup (once, admin) → start (discovery + brief + short plan) → build → check → handoff`
Demo audience only says "start a project" and "build it"; Joe runs setup beforehand.

## 1. Fix library paths
Every skill says "`KIT` = two folders up". From `.snowflake/cortex/skills/<skill>/` that is `.snowflake/cortex/`. Change to: "`KIT` = the repo root (four folders up)". Library stays at `library/`.

## 2. Setup (`bi-kit-setup`)
- Move from archive into `bi-kit-setup/references/`: `company-standards.template.yaml`, `company-standards.example.yaml` (copies; archive keeps originals so nothing is lost from git history view).
- Keep the 4-batch interview and read-only Snowflake checks.
- Replace "save to KIT/standards + republish" with: write `company-standards.yaml` locally, then (after confirming) `CREATE STAGE IF NOT EXISTS` at a location the lead names and `PUT` the file there.
- Drop `standards.py check`; validate by re-reading against REQUIRED keys in the template.

## 3. Standards lookup (shared rule, stated in each skill)
Order: `./bi-kit/company-standards.yaml` → stage path in `./bi-kit/standards-location.txt` (one line, e.g. `@ANALYTICS.BI_KIT.STANDARDS/company-standards.yaml`) → none: continue with safe defaults and say so once.
- Reading from the stage: try the read tool on the stage path; fallback `GET` to `./bi-kit/`. **Verify early** that reading a stage file works in Desktop.

## 4. Start (`bi-kit-start`) — discovery
- First question: new dashboard or existing app/code?
- **New**: current five questions (outcome, audience, data, measures + number to match, look).
- **Existing** (new `references/existing-app.md`): read the code, inventory data sources, charts and filters, run the data-intake check on those sources, then ask what should change and which number to trust.
- Output stays `PROJECT_BRIEF.md`; add a short **Build plan** section at the bottom (numbered visuals, data per visual, surface). This is the seed of a future Plan stage.
- Fix image-readback path to `../bi-kit-build/references/image-readback.md`.

## 5. Build (`bi-kit-build`)
- Streamlit mechanics (connection, caching, deploy, SiS) delegated to the bundled `developing-with-streamlit-in-snowflake` skill; agents to `agent-studio`.
- Kit adds only conventions, rewritten in `references/build-patterns.md`:
  - a small helper pattern written into the app: run SQL with parameters, render, and an `st.expander("How this was built")` showing SQL, row count, query ID;
  - brand colours/formats from standards; visual library names; fiscal calendar; number to match shown on the KPI.
- Remove: copying `bi_kit_runtime.py`, `verify_app.py`, `selfcheck.py`, `standards.py`. Replace self-check with "re-run each visual's SQL and compare totals".
- `debug-mode.md` and `html-report.md` rewritten to the same convention.
- Runtime stays in `archive/` (can come back if stricter consistency is wanted).

## 6. Check and handoff
- Check: inline the secret/admin-role patterns (from `secret_patterns.json`) into `references/checks.md`; drop `scan_secrets.py` and `verify_app.py`; standards via the shared lookup.
- Handoff: drop runtime references; production copy = set the debug flag off; receiving team from standards or ask.

## 7. Wrap up
- Update README (flow, stage-based standards, setup references).
- Grep skills for `runtime|scripts/|verify_app|selfcheck|scan_secrets|plugin` — expect zero hits.

## Assumptions
- Standards stay one YAML file. Brand JSON per project is dropped; build reads brand from standards directly.
- Archive is left untouched.
