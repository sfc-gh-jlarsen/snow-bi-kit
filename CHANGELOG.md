# Changelog

## 0.1.0 (2026-10-13)
First version.
- Skills: `bi-kit-setup`, `bi-kit-start`, `bi-kit-build`, `bi-kit-check`, `bi-kit-handoff`.
- Runtime: `run_visual` / `kpi` / `chart` / `table`, debug panels (Streamlit expanders, HTML `<details>`), number-to-match tie-out, re-run self-check, run manifest; `BI_KIT_DEBUG` env switch for production builds.
- `verify_app.py` (no data rendered outside the runtime), `selfcheck.py` (headless AppTest run + re-run comparison).
- Visual library (~25 entries, 16 in the gallery), BI terms translation, voice rules.
- Company standards template + fictional example + validator.
- Deterministic secret scan with shared patterns (also used as a no-shell grep fallback).
- Dev add-on: activity hook, `bi-kit-log-feedback`, feedback/activity tables and views.
- Gallery app on deterministic synthetic data.
- Design spec, research summary, internal transcript.
