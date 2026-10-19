# Research behind snow-bi-kit

Why the kit has this shape, and what it deliberately borrows from or avoids. (Internal notes with named sources live in `docs/internal/`.)

## The question
Analysts moving from Tableau/Power BI to building with Cortex Code would benefit from a "team of helpers": an optimizer, a best-practice reviewer, a security reviewer, a documenter, a hand-off coach and a project manager. Is that a good idea, is it already done, and what shape should it take?

## What exists (as of 2026-10)
- **Platform building blocks are GA in Cortex Code**: skills, plugins (skills + subagents + hooks), AGENTS.md, hooks, the skill catalog for sharing. Nothing in the product ships a curated analyst helper team.
- **Engineer-oriented role frameworks are mature**:
  - BMAD Method (persona agents for analyst/PM/architect/dev/QA; MIT);
  - GitHub Spec Kit (spec-driven kickoff; MIT);
  - Anthropic's Claude Code plugins (code-review with parallel independent reviewers and a confidence threshold; security-review; MIT);
  - large subagent catalogs (wshobson/agents, VoltAgent);
  - obra/superpowers.

  All of them target software engineers.
- **Snowflake-adjacent public repos**:
  - [Snowflake-Labs/coco-skills](https://github.com/Snowflake-Labs/coco-skills): curated CoCo skills and plugins, including the XO operator plugin.
  - [sfc-gh-myoung/ai_coding_rules](https://github.com/sfc-gh-myoung/ai_coding_rules): 195 portable coding rules delivered as a plugin (Apache-2.0).
  - [Snowflake-Labs/snowflake-ai-kit](https://github.com/Snowflake-Labs/snowflake-ai-kit): routes Snowflake prompts from other agents to CoCo.
- **Data-platform assistants for analysts** (e.g. Databricks Genie Code agent mode) protect non-engineers with **deterministic action policies** (approval gates, blocking destructive or scope-escalating actions, permission inheritance), not reviewer personas.
- **No prior art found** for an analyst-facing (ex-BI) kit, or for a **prototype → production hand-off** helper.

## What the evidence says about helper agents
- Separate helpers pay off for **read-only, independent review** (fresh context, no author bias) and for keeping noisy exploration out of the main thread (Anthropic multi-agent research write-up; Cognition's "Don't build multi-agents" exception for read-only subtasks; Anthropic's code-review plugin design).
- Many always-available personas, sequential persona pipelines and named characters add cost and confusion; practitioners converge on **3–4 helpers** invoked at known moments.
- Secret detection is a solved, deterministic problem (gitleaks, trufflehog). An LLM opinion should explain findings, not be the control.

## Resulting design choices
1. **Moments, not personas**: start → build → check → hand-off (+ a one-time setup for leads). The six roles fold into these.
2. **Lighter than ai_coding_rules and XO, by design.** Both expose their machinery (rule loading, gates, workflow stages, vaults). This kit hides it: the analyst sees commands and a few files.
3. **Skills first; parallel independent checks only where supported.** Works in CoCo Desktop and Snowsight.
4. **Deterministic gates, plain-language explanations**: secret scan, static app verifier, re-run self-check.
5. **Debug panels from what actually ran**: every visual goes through one helper, so "how this was built" can't drift from the chart. This is the trust bridge for BI users who are used to inspecting calculations.
6. **A number to match** in every brief: the fastest way for a BI migrant to trust a new dashboard.
7. **Wrap bundled skills** (Streamlit, performance analysis, semantic views, report publishing) instead of replacing them.
8. **Company standards captured once**, read by every command; no customer values in the kit.

## Open items
- How a catalog-installed plugin carries always-on standards in Snowsight (vs workspace files).
- Subagent support and shell availability in Snowsight CoCo (affects the parallel check and the secret-scan script; fallbacks exist).
- Effectiveness: compare plain CoCo against the kit on seeded tasks before adding anything.
