---
name: bi-kit-log-feedback
description: "DEV ONLY (snow-bi-kit-dev). Log test feedback about a snow-bi-kit command to Snowflake, sync the local activity log, show what's open, or mark items fixed. Use when: log feedback, that didn't work, the kit got this wrong, note this for the kit, what feedback is open, mark feedback fixed. Triggers: log feedback, kit feedback, bi kit feedback, what's open for the kit, mark fixed in version."
---

# Log feedback (kit development only)

For the kit developer's test sessions. Not part of the shipped kit.

Config: `~/.snowflake/cortex/snow-bi-kit-dev/config.toml` with `connection`, `database`, `schema`, `warehouse` (copy from `config.example.toml` in this add-on). If it's missing or a value is blank, stop and say which key, and don't guess. Use that connection for every statement.

## First use
If `<database>.<schema>.KIT_FEEDBACK` doesn't exist, show the developer `../../sql/feedback_schema.sql` with the variables filled from config and run it only after they say yes.

## Log feedback ("log feedback: …")
1. Work out from the conversation: `command` (last bi-kit command used), `project` (project folder name), `session_id` if known, `kit_version` (from the installed snow-bi-kit `plugin.json`).
2. Extract `feedback_text` (their words, verbatim) and, if stated, `expected`.
3. Ask in **one** question only for what's missing: category, severity (blocker / major / minor / idea), rating 1–5. Offer your best guess as the default.
4. Insert with bound values (no string-built SQL from free text):
   ```sql
   INSERT INTO KIT_FEEDBACK (session_id, kit_version, command, project, category, severity, rating, feedback_text, expected)
   SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?;
   ```
   If parameter binding isn't available in the SQL tool, escape single quotes by doubling them.
5. Then **sync activity** (below) and reply in one line: "Logged (major, build): image read-back missed the legend."

## Sync activity
Read `~/.snowflake/cortex/snow-bi-kit-dev/activity.jsonl`; insert lines with `"synced": false` into `KIT_ACTIVITY` (`logged_at, session_id, command, kit_version, project_dir`); rewrite those lines with `"synced": true`. If the file doesn't exist, skip silently.

## What's open
`SELECT * FROM OPEN_FEEDBACK_BY_COMMAND;` plus the 10 newest open rows (`feedback_id`, command, severity, short text). For progress across versions, chart `KIT_VERSION_SCORECARD` (avg rating and runs by version).

## Mark fixed
"Mark <id or description> fixed in 0.1.1": `UPDATE KIT_FEEDBACK SET status = 'fixed', fixed_in_version = ?, updated_at = CURRENT_TIMESTAMP() WHERE feedback_id = ?;` Confirm which rows first if matching by description.
