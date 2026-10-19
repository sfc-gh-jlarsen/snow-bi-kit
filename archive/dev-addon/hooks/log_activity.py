"""PostToolUse hook (dev add-on): record each snow-bi-kit command invocation locally.

Appends one JSON line per bi-kit skill invocation to
~/.snowflake/cortex/snow-bi-kit-dev/activity.jsonl. The log-feedback skill
syncs these lines into Snowflake. Never blocks and never prints to the
conversation; any error is swallowed (dev telemetry must not break a session).
"""

import json
import os
import sys
from datetime import datetime, timezone

STATE_DIR = os.path.expanduser("~/.snowflake/cortex/snow-bi-kit-dev")
KIT_MANIFESTS = [
    os.path.expanduser("~/.snowflake/cortex/plugins/snow-bi-kit/.cortex-plugin/plugin.json"),
]


def kit_version() -> str:
    for path in KIT_MANIFESTS:
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f).get("version", "unknown")
        except (OSError, ValueError):
            continue
    return "unknown"


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "skill":
        return
    command = str((event.get("tool_input") or {}).get("command", ""))
    name = command.split(":")[-1]
    if not name.startswith("bi-kit-") or name == "bi-kit-log-feedback":
        return
    os.makedirs(STATE_DIR, exist_ok=True)
    row = {
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "session_id": event.get("session_id"),
        "command": name,
        "kit_version": kit_version(),
        "project_dir": event.get("cwd"),
        "synced": False,
    }
    with open(os.path.join(STATE_DIR, "activity.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - dev telemetry must never break the session
        pass
    sys.exit(0)
