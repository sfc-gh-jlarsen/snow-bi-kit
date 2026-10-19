---
name: bi-kit-check
description: "Check a snow-bi-kit dashboard, report or app before sharing it: speed and cost, how it's built (company standards, visual library, split or consolidate), and security (passwords, tokens, admin or personal roles in code, debug panels left on in shared apps). Returns one short report: Fix now / Worth considering / Looks fine. Read-only. Use when: is this any good, is this safe, check my work, review my dashboard before I share it, why is my dashboard slow. Triggers: check my work, review my dashboard, is this safe, is this ready to share, check before sharing. Do NOT use for: deep single-query tuning on its own (bundled workload-performance-analysis), account-wide security audits (bundled security skills), or building changes (bi-kit-build)."
---

# Check my work

Read-only. Never changes files or Snowflake objects; offers fixes instead. Load the `bi-kit-library` skill first and follow its `voice.md`.

## Inputs
- The project folder (brief, app or report). If unclear which project, ask once.
- Company standards, found with `standards-lookup.md` (bi-kit-library) (prototype location, roles, brand, debug policy). If none, check against the brief and say so once.

## Run three checks independently
If you can run helper agents in parallel, run each check as a separate read-only helper with only the project path, the standards file, and that check's section of `references/checks.md`, so each one judges without the others' assumptions. Otherwise run them one after another. Either way the analyst sees one report.

1. **Speed and cost**: `references/checks.md` § Speed. For query-level detail, use the bundled `workload-performance-analysis` skill on the app's query IDs (from query history for the app's queries). Don't reimplement it.
2. **How it's built**: § Build. Standards conformance, visual library use, brand, number to match, split or consolidate.
3. **Security**: § Security. **Pattern scan first**: grep the project with every pattern in `references/secret-patterns.md`. Then the judgement checks. An opinion never clears a scan finding.

## Merge into one report
Write `checks/CHECK_REPORT.md` in the project and show it (one screen):

```markdown
# Check: <project> (<date>)

## Fix now
- **A password is written in the app** (app/streamlit_app.py, line 12). Anyone who can open the app's code can log in as you. *Fix:* delete it, change the password, and use the app's Snowflake connection. I can make the code change.

## Worth considering
- **The trend chart re-reads 41M rows every time someone opens it** (about 8 s). Daily data doesn't need that. *Fix:* cache it for an hour, or ask the data team for a monthly summary table.

## Looks fine
- Uses your company colours and number formats · Number to match: **matches** ($12.4M) · Every chart shows how it was built

**What to do next:** fix the password (say "fix it"), then run *check my work* again.
```

Rules for findings:
- Each one: **what** (plain words) + **where** + **why it matters to you** + **fix**, offering to make the change.
- Order: security, then wrong numbers, then speed/cost, then polish.
- **Fix now** = credentials/admin role, wrong or unmatched number, debug on in a shared app, a data leak to viewers who shouldn't see rows. Everything else is *Worth considering*. Cap at ~5 *Worth considering*; mention "and 3 smaller things" if more.
- No finding without evidence (a line, a query ID, a measured time, a row count). Don't speculate.
