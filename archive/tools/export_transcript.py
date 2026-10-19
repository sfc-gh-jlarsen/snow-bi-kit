"""Export a Cortex Code conversation history (.history.jsonl) to a readable markdown transcript.

    python tools/export_transcript.py <history.jsonl> <out.md>

Keeps user and assistant text, notes which tools ran, strips injected
system/hook blocks, and redacts private work-item numbers and vault paths.
"""

import json
import re
import sys

STRIP_BLOCKS = re.compile(r"<(system_context_from_session_hook|system-reminder|user-prompt-submit-hook)>.*?</\1>", re.S)
REDACTIONS = [
    (re.compile(r"/(?:Users|home)/[^\s`)]*"), "[local path]"),
    (re.compile(r"\$[A-Z_]+_HOME/[^\s`)]*"), "[private path]"),
    (re.compile(r"\bnotes/\d{4}-\d{2}/[\w.-]*wi\d+[\w.-]*"), "[private notes]"),
    (re.compile(r"\btasks/current/[\w.-]*wi\d+[\w.-]*"), "[private task]"),
    (re.compile(r"\bWI-\d+\b"), "[work item]"),
    (re.compile(r"\bwi\d+\b"), "[work item]"),
]


def clean(text: str) -> str:
    text = STRIP_BLOCKS.sub("", text)
    for rx, repl in REDACTIONS:
        text = rx.sub(repl, text)
    return text.strip()


def main(src: str, dst: str) -> None:
    out = [
        "# Design conversation transcript",
        "",
        "> **Internal only.** Contains customer and people names from the design discussion. "
        "Remove `docs/internal/` before publishing this repo publicly.",
        "> Exported from the Cortex Code session history; injected system context removed, "
        "private tracking references redacted, tool calls summarised.",
        "",
    ]
    turn = 0
    pending_tools: list[str] = []
    with open(src, encoding="utf-8") as f:
        for line in f:
            msg = json.loads(line)
            role = msg.get("role")
            texts, tools = [], []
            for block in msg.get("content") or []:
                if block.get("type") == "text":
                    t = clean(block.get("text", ""))
                    if t:
                        texts.append(t)
                elif block.get("type") == "tool_use":
                    tools.append(block.get("name", "tool"))
            if role == "user" and texts:
                if pending_tools:
                    out.append(f"_Tools used: {', '.join(sorted(set(pending_tools)))}_\n")
                    pending_tools = []
                turn += 1
                out += [f"---\n\n## Turn {turn}: Joe", "", "\n\n".join(texts), ""]
            elif role == "assistant":
                pending_tools += tools
                if texts:
                    out += ["### Cortex Code", "", "\n\n".join(texts), ""]
    if pending_tools:
        out.append(f"_Tools used: {', '.join(sorted(set(pending_tools)))}_\n")
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
