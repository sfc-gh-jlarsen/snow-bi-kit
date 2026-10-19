---
name: bi-kit-start
description: "Start a BI project with snow-bi-kit: discovery that turns a request (a new dashboard idea, or changes to an existing Streamlit app or report) into a one-page project brief with a short build plan (outcome, audience and access, data sources, key measures and a number to match, optional picture or description of the look). Use when: an analyst has a new dashboard/report idea or request, wants to scope a project, change or extend an existing app, start a project, kick off a dashboard, write a brief. Triggers: start a project, new dashboard project, kick off, scope this dashboard, project brief, I have a request for a report, I want to change this app. Do NOT use for: building the app (bi-kit-build), reviewing work (bi-kit-check), or general SQL questions."
---

# Start a project

Discovery: turn an analyst's idea into `PROJECT_BRIEF.md`, ending in a short build plan. Nothing gets built until they say the brief looks right.

Load the `bi-kit-library` skill first and follow its `voice.md`. Find company standards with `standards-lookup.md` (bi-kit-library); if there are none, continue with defaults and say so once.

## Step 1: New or existing?

If the request doesn't already say, ask one question: **"Are we building something new, or changing an app or report you already have?"**
- **New** → Step 2a.
- **Existing** (they point at a folder, a `streamlit_app.py`, a deployed Streamlit app, or an HTML report) → Step 2b.

## Step 2a: New dashboard

Ask the five questions in one batch (ask-user-question; free-text with suggested defaults). If the analyst already answered some in their request, pre-fill those and only ask for the gaps.
1. **Outcome**: what question does this answer, and what will someone do differently because of it?
2. **Audience & access**: who looks at it; do they all have Snowflake logins; should different people see different rows (region, plant…)?
3. **Data**: which tables, views or semantic view it comes from (names are fine, even partial), or a SQL query they already trust; and how fresh it must be (live / hourly / daily / monthly).
4. **Measures & a number to match**: the 3–5 key numbers and how each is defined, plus **one number from an existing report they trust** (e.g. "Q3 net sales for NA = $12.4M"). Pre-fill definitions from standards `trusted_data.metric_definitions` if present; the analyst confirms instead of retyping.
5. **Look** *(optional)*: a picture (screenshot, mockup, slide) if they have one, or a sentence, or "suggest something". **Never require a picture.**

## Step 2b: Existing app or report

Follow `references/existing-app.md`: read what's there first, show the analyst what you found in plain words, then ask only what reading the code can't tell you.

## Step 3: Check the data

Check every source named or found, using `references/data-intake.md`. Report it in one short block. Only offer a catalog search if a name can't be found or nothing was named.

## Step 4: The look

If they gave a picture: save it to `reference/` in the project folder and do the read-back from `image-readback.md` (bi-kit-library). Without a picture, write the layout from their sentence, or propose one from the outcome and measures using `visuals.md` (bi-kit-library).

## Step 5: Fill in the rest and sanity-check

- Infer and show for confirmation (don't ask separately unless it matters): recommended surface (HTML report / Streamlit app / agent; see `references/brief-template.md`), filters and drill paths, sensitivity (classification tags if present), owner and hand-off team (from standards).
- Flag scope problems plainly: "this is two projects", "this needs data you can't read", "this number has no definition", "external viewers but your standards don't allow external sharing".

## Step 6: Write the brief and build plan

Write `PROJECT_BRIEF.md` using `references/brief-template.md`, including the **Build plan** section at the end: numbered visuals, the data and measure behind each, filters, and the surface. For an existing app, the plan lists only what changes. Offer to create the project folder (`app/` or `report/`, `reference/`); create folders only after they agree.

Reply with the brief's headline lines and **What to do next**: "Say *looks right* and then *build it*, or tell me what to change."

## Rules
- Use the analyst's names and definitions; don't silently "improve" a definition. If two definitions conflict, ask.
- Never rewrite a pasted query; keep it verbatim as the starting point.
- A number read from a screenshot or an existing app is only the number to match if the analyst confirms it.
- Discovery is read-only: don't edit an existing app here.
