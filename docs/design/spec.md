# snow-bi-kit design spec (v2)

Origin: a design discussion about giving analyst teams a lightweight helper kit for Cortex Code (see `research.md`). First customer: a manufacturer's analytics teams. Built for the **analyst persona** in general, not just the first customer.
v2 (2026-10-13) adds seven workflow inputs from the design discussion: data sources, brief intake, feedback loop, images, visual library, company standards, and debug mode.

## Goal
An analyst who used to build in Tableau or Power BI describes an outcome and says where the data lives. The kit then turns that into a brief, builds to company standards (including "make it look like this picture"), checks the work, and packages it for the data team. Throughout, the analyst sees plain English and a handful of files, never the machinery.

## Who it's for
- **Analysts** (primary): think in dashboards, measures, filters and "who can see this". They know which tables or views their data comes from, or can get that from another tool.
- **Analytics lead / admin** (once per company): runs setup to capture company standards.
- **Data team** (receiver): consumes the handoff pack.
- Output rule for everyone: about one screen, ending in "what to do next".

## Shape of the product
| Who | Command | When | Output |
|---|---|---|---|
| Lead/admin | `setup-standards` | Once, then on change | Company standards: house rules + brand + metric definitions + environment map |
| Analyst | `start-project` | "I have an idea / a request" | `PROJECT_BRIEF.md` (+ `reference/` images) |
| Analyst | `build-it` | "Build what's in my brief" / "change X" | The dashboard, report or app, built to standards, with debug panels on |
| Analyst | `check-my-work` | "Is this any good? Is it safe?" | Check report: *Fix now / Worth considering / Looks fine* |
| Analyst | `hand-off` | "The data team takes it from here" | Handoff pack + a production build (debug off) |

Analysts see 4 commands; setup is for leads. (v1 had 3 commands. `build-it` is added because images, the visual library, standards and debug mode all have to apply *while* building. Leaving that to whichever bundled skill happens to route makes it unenforceable.)

## Requirements

### R1 — Data sources: the analyst tells us; we don't go hunting by default
- R1.1: `start-project` asks the analyst for the source. Any of these is accepted:
  - table, view or semantic view names (full or partial);
  - a SQL query they already trust;
  - "the data behind Tableau/PBI report X", in which case we ask for the workbook or data source file, or the underlying table names.
- R1.2: The kit **verifies, not assumes**, and reports in one short block:
  - each named object exists and the analyst's current role can read it (no "authorized" surprises later);
  - key columns, grain (one row per what?), date range and row count, from a light profile (`LIMIT`/`SAMPLE`, small warehouse);
  - whether an existing **semantic view** already covers these tables. If one does, the kit recommends building on it, because the metric definitions are already governed.
- R1.3: Searching the catalog (`snowflake_object_search` / semantic view search) is **offered, not default**: "I couldn't find `SALES_DAILY`. Want me to search for similar tables?" It is used only if the analyst agrees, or names nothing.
- R1.4: A pasted query is kept verbatim as the starting point. The kit never silently rewrites it, and any optimization goes through `check-my-work`.

### R2 — Brief intake: what we must ask, and what we infer
`start-project` asks **5 required questions**, one screen, plain words:
1. **Outcome**: what question does this answer, and what will someone do differently because of it?
2. **Audience & access**:
   - Who looks at it?
   - Do they all have Snowflake logins?
   - Should different people see different rows (e.g. by region or plant)?

   (This drives surface choice, owner's- vs caller's-rights, and external embedding.)
3. **Data**: where it comes from (R1), and how fresh it must be (live / hourly / daily / monthly).
4. **Measures & a number to match**:
   - The 3–5 key numbers and how each is defined (e.g. "net sales = gross − returns, USD, excluding intercompany").
   - **One number they already trust from an existing report, used as the tie-out.**
   - Definitions found in company standards are pre-filled for confirmation, not re-asked.
5. **Look**: *optional*. A picture (screenshot, mockup, slide) if they have one; otherwise a sentence or two ("a few KPIs on top, monthly trend, top plants"). If they give neither, the kit proposes a layout from the library based on the outcome and measures. **A picture is never required.**

**Inferred, then shown in the brief for confirmation** (asked only if they can't be inferred or matter for this project):
- Surface recommendation (HTML report / Streamlit / agent), with a one-line reason each.
- Filters and drill paths (from the picture or measures).
- Delivery needs: export, schedule or email, mobile.
- Sensitivity: PII or confidential, from classification tags on the source columns where present.
- Scale: expected viewers, and data volume (from the profile).
- Timing and owner: target date, who the handoff goes to (default from standards).
- Language and locale: labels, number and date formats, timezone (default from standards; matters e.g. for regional teams working in other languages).

The brief ends with a **scope sanity check** ("this is two projects", "this needs data you don't have access to"). Nothing gets built until the analyst says "looks right".

### R3 — Images as input ("make it look like this, plus this data"), when provided
- R3.0: Images are an *optional accelerator*, not a gate. Description-only and "propose something" are equally supported paths. Every step below runs only when an image is supplied; without one, `build-it` starts from the brief's written layout (or the proposed one) and does the same read-back confirmation in text.
- R3.1: Accept PNG/JPG screenshots and mockups directly.
  - Desktop supports drag-drop.
  - Snowsight CoCo supports multi-image drag-and-drop per its changelog (2026-08-03), UNVERIFIED for this flow.
- R3.2: PPT/PDF mockups are accepted best-effort: extract slide text plus embedded images. If a slide can't be read as an image, the kit asks for a screenshot of that slide rather than guessing.
- R3.3: The kit **reads the picture back** before building. It produces a numbered layout list using the visual library names (R4), e.g. "1. Four KPI tiles with change vs last year. 2. Line chart, monthly, by region. 3. Bar, top 10 plants, rest grouped as 'Other'. 4. Detail table." It maps each item to fields from the data ("2 → `NET_SALES_USD` by `REGION`, `MONTH`"), marks any item with no data match as **needs a source**, and asks for confirmation.
- R3.4: Anything read from a BI screenshot (measures, filters, numbers) is a **hypothesis, not truth**. A number visible in a screenshot can become the tie-out number only if the analyst confirms it.
- R3.5: Reference images are saved to the project's `reference/` folder and linked from the brief, so `build-it` and `hand-off` use the same source.

### R4 — Visual and terms library (how we name and build things)
- R4.1: A hidden reference library of **visual types**. Each entry has:
  - plain definition;
  - when to use / when not to;
  - required data shape (columns and grain, with a SQL pattern);
  - how it's built on each surface (Streamlit chart spec; HTML report as inline SVG or `<details>`-friendly markup, no external libraries);
  - common gotchas.

  Starter set (≈25):
  - KPI tile with delta, sparkline, line / multi-line, bar / stacked / 100% stacked;
  - top-N with "Other", Pareto, waterfall, bullet chart, box-and-whisker, histogram;
  - heatmap, small multiples, treemap, scatter with trend line, slope chart, funnel;
  - cohort table, conditional-format table (traffic lights);
  - map (flagged: limits vary by surface), dual-axis (discouraged; suggest alternative).
- R4.2: A **BI-terms translation** section, mapping Tableau/PBI concepts to the kit's way:
  - calculated field, LOD expression, table calculation;
  - parameter / what-if, extract vs live, data source / dataset;
  - row-level security, drill-down, cross-filter, tooltip;
  - YoY / YTD / MTD / rolling 12, fiscal calendar.
- R4.3: Everything is consistent: the image read-back (R3.3), the brief and `build-it` use the same names. When an analyst uses a term, the kit maps it to the library entry. If there's no entry, it says so and builds the closest documented alternative instead of improvising.
- R4.4: Company standards (R5) can extend or override entries (e.g. "our KPI tiles always show vs plan, not vs last year").
- R4.5: Deliverable: a **gallery app** that renders every library entry on synthetic data. It's the analyst's "menu" and doubles as the library's regression test.

### R5 — Company standards (`setup-standards`)
- R5.1: An interview a lead completes once (≈15 minutes), editable later. It captures:
  - **Environments**: databases and schemas per stage (e.g. prototype / dev / test / prod), where prototypes may live, naming patterns.
  - **Access**: build role, viewer roles, service role for shared apps, whether external (no-login) sharing is allowed, and who may publish to CoWork.
  - **Compute**: default warehouse, compute pool and external access integration for Streamlit.
  - **Brand**: colors (hex), chart palette, fonts, logo (stage path), number, currency and date formats, fiscal calendar, default language and timezone.
  - **Trusted data**: preferred semantic views and certified tables, plus standard metric definitions (feeds R2 Q4).
  - **Handoff**: receiving team, intake channel (e.g. Jira project / email), required handoff fields, doc standards.
  - **Debug policy**: on in prototypes; off or removed for production (R6).
- R5.2: Stored in two layers:
  - a short **house rules** block, always loaded;
  - **standards files** read on demand (brand, metrics, environments).

  The house rules stay under ~1 screen, so they never crowd the context window.
- R5.3: Every command reads the standards; none hardcode them. Running a command with standards missing gives a clear "your lead hasn't run setup yet" message.

### R6 — Debug mode ("show me how this number was made")
- R6.1: In debug mode every chart, table and KPI gets an accordion block, collapsed by default (Streamlit `st.expander`, HTML `<details>`). It contains:
  - the exact SQL run, with filters and parameters substituted;
  - **any Python processing after the query** (the transform code itself, e.g. the pandas steps that pivot or compute a rolling average);
  - source objects, row count returned, run time, query ID;
  - the library entry used (R4).
- R6.2: Debug blocks must be **true, not decorative**. Generated code routes every visual through one small helper that runs the query, applies the transform and renders. The debug block is produced from what actually ran, not from a description written next to the code.
- R6.3: **Self-check (agent reflection)**: after building or changing a visual, `build-it` re-runs the SQL from the debug block, re-applies the shown transform, and confirms the result matches the data the chart rendered. On a mismatch, it fixes the code before telling the analyst it's done.
- R6.4: The tie-out number (R2 Q4) is shown in debug mode next to the matching KPI, marked "matches" or "differs by X".
- R6.5: **Production version**: `hand-off` produces a production build with debug off (one flag). If standards say "remove", the debug code is stripped instead. `check-my-work` flags any **shared** app with debug on, because it exposes SQL and object names to viewers.

### R7 — Check and hand-off (carried over from v1, adjusted)
- R7.1: `check-my-work` runs three independent read-only checks (speed & cost, how it's built, security), merged into one report. Details as in v1:
  - speed wraps the bundled `workload-performance-analysis`;
  - security runs a deterministic secret/credential scan first, then an LLM explanation.

  New checks:
  - debug-on-in-shared-app (R6.5);
  - visuals not in the library or off-brand (R4/R5);
  - tie-out mismatch (R6.4).
- R7.2: `hand-off` writes:
  - `HANDOFF.md`, `README.md`, a Mermaid architecture diagram;
  - the object inventory gathered from Snowflake;
  - required grants, refresh and schedule needs, and a "what's prototype-grade" list;
  - open questions;
  - the brief, the latest check report, and the production build (R6.5).

  It is formatted to the receiving team's required fields (R5).
- R7.3: Every finding says *why it matters to you* in analyst terms.

### R8 — Surfaces, routing, isolation
- R8.1: Works in **CoCo Desktop and CoCo in Snowsight**. Skills first; subagents are optional (the checks run in sequence when they're unavailable).
- R8.2: No name or trigger collisions with bundled skills. `build-it` *uses* the bundled Streamlit / report / agent skills and adds the kit's standards, library and debug mode on top. Each description says what it's NOT for.
- R8.3: No customer-specific values in the kit. They all come from standards.

### R9 — Development feedback loop (dev-only, never shipped)
- R9.1: A separate **dev add-on** (its own plugin, `…-dev`), installed only in the kit developer's test sessions. It adds:
  - `log-feedback`: the developer says "log feedback: the image read-back missed the legend". It records the feedback with the current command, kit version and project, and asks for a 1–5 rating and a category only if they're missing.
  - **Activity logging**: when the dev add-on is present, each kit command appends one row (command, kit version, start/end, success or error, short input summary, output files, debug self-check result).
- R9.2: Storage in the **demo account**, where testing happens, so it uses the same connection with no cross-account hop. Schema `ANALYST_KIT_DEV.FEEDBACK` (name per C2):
  - `KIT_ACTIVITY`: one row per command run.
  - `KIT_FEEDBACK`: `id, logged_at, session_id, kit_version, command, project, category (data|brief|image|library|build|debug|check|handoff|standards|other), severity, rating, feedback_text, expected, status (open|in_progress|fixed|wontfix), fixed_in_version, notes`.
  - Standard tables. Hybrid is not needed: one writer, low volume, status updated via `UPDATE` (see Decisions).
- R9.3: The **iteration loop**: the build session (this one) reads open feedback, fixes, bumps `kit_version`, and sets status to `fixed` with `fixed_in_version`. The test session reinstalls and retests. A one-query "what's open, by command" view drives each iteration.
- R9.4: The shipped kit contains **no** reference to the dev add-on, the feedback tables or the demo account.

## Constraints
- C1: Plain language everywhere. A banned-words list for analyst-facing output (e.g. subagent, orchestration, pathway, artifact, persona). No academic framing.
- C2: Zero hardcoded environment values. Every account, database, role and warehouse comes from standards (shipped kit) or the dev add-on's config (dev). Required keys are left blank and fail loudly.
- C3: Read-only by default:
  - `check-my-work` changes nothing;
  - `hand-off` writes docs plus a production *copy*;
  - `start-project` scaffolds only after confirmation;
  - `build-it` writes only inside the project and its prototype schema from standards.
- C4: Security: a deterministic gate first, LLM explanation second. An LLM opinion never clears a finding.
- C5: Small: 5 skills (4 analyst + 1 setup) plus reference libraries. Each SKILL.md is ≤ ~500 words; library and standards content loads on demand. A sixth command needs usage evidence from `KIT_ACTIVITY`.
- C6: Licensing: original content. Borrowed material keeps its license. No AGPL code vendored. Nothing customer-private in the kit repo.
- C7: **Invisible machinery.** The analyst never sees rule IDs, gate output, scratch files, progress chatter, or the reflection loop (R6.3). Internals can be rigorous; none of it is surfaced. Deliberately lighter-weight than ai_coding_rules and XO.
- C8: Profiling and self-checks use small warehouses and `LIMIT`/`SAMPLE` by default. The kit must not be the reason a demo account burns credits.

## Non-goals
- NG1: Project management over time (timelines, reminders, nagging). `start-project` covers kickoff and scope sanity only.
- NG2: Named characters or personas.
- NG3: Workflow stages, memory vaults, work items (the XO model).
- NG4: Teaching git or doing promotion. `hand-off` documents what to promote; promotion is the companion training series, Session 2.
- NG5: Replacing bundled skills; the kit wraps them.
- NG6: Hunting for data by default (R1.3).
- NG7: Pixel-perfect reproduction of a Tableau/PBI screenshot. The goal is "same story, same numbers, our standards", built from library visuals.
- NG8: Shipping feedback/activity tracking to customers (R9 is dev-only).

## Decisions
- Locked: 4 analyst commands + 1 setup (was 3). `build-it` is needed so images, library, standards and debug mode are enforced during building.
- Locked: the analyst names the data; catalog search is opt-in (design decision, 2026-10-13).
- Locked: the brief has 5 required questions, including **a tie-out number**. It's the single best trust-builder for BI migrants.
- Locked: debug blocks come from what actually ran (helper pattern) and are self-checked by re-running. A side description doesn't count as a debug block.
- Locked: the feedback/activity store is in the demo account, as standard tables, in a dev-only add-on. A separate internal account is the alternative, but it puts the store in a different account from where the testing runs.
- Locked: skills first, subagents optional; deterministic secret scan; no dependency on ai_coding_rules or XO.
- Deferred: **name** (now "snow-bi-kit"; command names use the `bi-kit-` prefix to avoid collisions with bundled skills).
- Deferred: **home**. A personal GitHub repo first, then a PR to `Snowflake-Labs/coco-skills`, plus a customer copy whose standards are filled in through their skill catalog.
- Deferred: **how standards reach every analyst's project**. Options:
  - (a) baked into the customer's copy of the kit plugin as reference files;
  - (b) written by setup into each workspace's AGENTS.md.

  Resolved by checking how a plugin installed from the catalog can carry always-on instructions, in both Desktop and Snowsight.
- Deferred: PPT/PDF image extraction in Snowsight (no shell); verify, or fall back to "please screenshot".
- Deferred: secret-scanner availability in Snowsight; fall back to the bundled pattern list.
- Deferred: whether to borrow a few ai_coding_rules Streamlit/Snowflake rules (Apache-2.0, attributed) as hidden content for "how it's built".
- Deferred: whether to switch `KIT_FEEDBACK` to a hybrid table. Only if two sessions write and update concurrently in practice.

## Acceptance criteria
- Done when all 5 commands work on CoCo Desktop and in Snowsight against the demo account, using synthetic tire-manufacturer-like data and a filled-in sample company standards.
- Seeded test set:
  - (a) a Streamlit app with a hardcoded password and a personal role: the check catches both;
  - (b) a slow dashboard on a full-scan query recomputed per view: at least one correct speed finding;
  - (c) a Tableau dashboard screenshot plus "add plant-level returns": the read-back lists every visual with correct library names, and returns are flagged **needs a source** if it isn't in the named tables;
  - (d) a PPT mockup: built from the slides, or a clear request for a screenshot;
  - (e) a prototype ready for handoff: the inventory matches `SHOW` output exactly, and the production build has debug off.
- Debug truth test: for every visual in (c) and (e), re-running the debug SQL and transform reproduces the rendered data, including at least one visual with a Python transform. The tie-out shows "matches" for the seeded number.
- Library: the gallery app renders all starter entries with no errors, on brand from standards.
- Comparison: the same tasks run with plain CoCo and with the kit, charted from `KIT_ACTIVITY` and `KIT_FEEDBACK`. The kit must find more true issues with no more false alarms, and outputs must fit one screen.
- One non-engineer test user goes from setup-filled standards through start → build → check → hand-off from a one-page guide, without help and without seeing internals (C7).
- No collisions: `/skill list` shows no clash, and adjacent prompts ("optimize this query", "make a README", "build a streamlit app") route as expected.
- The shipped package contains no dev add-on references (R9.4), verified by a grep.

## Sequence
Spec v2 (this) → Workshop-lite (command names, standards fields, library entries) → Provision (demo account: synthetic data, feedback schema, dev add-on) → Build (standards → library + gallery → `start-project` → `build-it` with debug + reflection → `check-my-work` → `hand-off`) → Prove (seeded set + debug truth test + A/B + test user) → Ship (repo + first-customer copy; demo in the companion training series, Session 2).
