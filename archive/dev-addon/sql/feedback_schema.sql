-- snow-bi-kit dev add-on: feedback + activity store (DEV ONLY).
-- Lives in the kit developer's demo account, where test sessions run.
-- Fill the three variables; blank values make the first statement fail on purpose.

SET kit_db     = '';   -- e.g. 'BI_KIT_DEV'
SET kit_schema = '';   -- e.g. 'FEEDBACK'
SET kit_wh     = '';   -- smallest warehouse you have

USE WAREHOUSE IDENTIFIER($kit_wh);
CREATE DATABASE IF NOT EXISTS IDENTIFIER($kit_db);
USE DATABASE IDENTIFIER($kit_db);
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($kit_schema);
USE SCHEMA IDENTIFIER($kit_schema);

-- One row per kit command invocation (synced from the local activity log written by the hook).
CREATE TABLE IF NOT EXISTS KIT_ACTIVITY (
  activity_id     STRING DEFAULT UUID_STRING(),
  logged_at       TIMESTAMP_TZ,
  session_id      STRING,
  command         STRING,          -- bi-kit-start | bi-kit-build | bi-kit-check | bi-kit-handoff | bi-kit-setup
  kit_version     STRING,
  project_dir     STRING,
  outcome         STRING,          -- filled from feedback when known: success | partial | failed
  synced_at       TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

-- One row per piece of test feedback.
CREATE TABLE IF NOT EXISTS KIT_FEEDBACK (
  feedback_id       STRING DEFAULT UUID_STRING(),
  logged_at         TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
  session_id        STRING,
  kit_version       STRING,
  command           STRING,
  project           STRING,
  category          STRING,        -- data | brief | image | library | build | debug | check | handoff | standards | voice | other
  severity          STRING,        -- blocker | major | minor | idea
  rating            NUMBER(1,0),   -- 1-5, how well the command did overall
  feedback_text     STRING,
  expected          STRING,        -- what should have happened
  status            STRING DEFAULT 'open',   -- open | in_progress | fixed | wontfix
  fixed_in_version  STRING,
  notes             STRING,
  updated_at        TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

-- What to work on next.
CREATE OR REPLACE VIEW OPEN_FEEDBACK_BY_COMMAND AS
SELECT command,
       COUNT(*)                                        AS open_items,
       COUNT_IF(severity = 'blocker')                  AS blockers,
       COUNT_IF(severity = 'major')                    AS majors,
       ROUND(AVG(rating), 1)                           AS avg_rating,
       MIN(logged_at)                                  AS oldest_open,
       ARRAY_AGG(category) WITHIN GROUP (ORDER BY category) AS categories
FROM KIT_FEEDBACK
WHERE status IN ('open', 'in_progress')
GROUP BY command
ORDER BY blockers DESC, majors DESC, open_items DESC;

-- Ratings and run counts by version, for charting progress across iterations.
-- Aggregate each side first so the join can't fan out and skew averages.
CREATE OR REPLACE VIEW KIT_VERSION_SCORECARD AS
WITH a AS (
  SELECT kit_version, command, COUNT(*) AS runs FROM KIT_ACTIVITY GROUP BY 1, 2
), f AS (
  SELECT kit_version, command, COUNT(*) AS feedback_items, ROUND(AVG(rating), 2) AS avg_rating
  FROM KIT_FEEDBACK GROUP BY 1, 2
)
SELECT COALESCE(a.kit_version, f.kit_version) AS kit_version,
       COALESCE(a.command, f.command)         AS command,
       COALESCE(a.runs, 0)                    AS runs,
       COALESCE(f.feedback_items, 0)          AS feedback_items,
       f.avg_rating
FROM a FULL OUTER JOIN f ON a.kit_version = f.kit_version AND a.command = f.command
ORDER BY 1, 2;
