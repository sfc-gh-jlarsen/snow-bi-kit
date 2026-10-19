# Reading a picture back (only when the analyst provides one)

Pictures are optional. Use this only when there is a screenshot, mockup, slide or PDF; otherwise work from the written layout.

## Accepted inputs
- **PNG/JPG screenshots or mockups**: read directly.
- **PPT/PPTX/PDF**: read slide/page text and any embedded images you can see. If a slide's visual can't be read, ask: "I can't see the chart on slide 3. Could you paste a screenshot of it?" Don't guess.
- Save every reference to the project's `reference/` folder with a short name (`reference/tableau-current.png`, `reference/mockup-slide2.png`) and link it from the brief.

## Read-back (always confirm before building)
Produce a numbered list, top-left to bottom-right, using **library names** from `visuals.md`:

```
From your picture I see:
1. Four KPI tiles: Net sales, Units, Return rate, Avg price, each with change vs last year (kpi)
2. Monthly net sales, one line per region (line)
3. Top 10 plants by net sales, the rest as "Other" (top_n_other)
4. Plant detail table with red/amber/green return-rate status (cond_table)
Filters: region, date range. Drill: region → plant.

Mapped to your data:
1. Net sales → NET_SALES_USD · Units → UNITS · Return rate → needs a source · Avg price → NET_SALES_USD / UNITS
2. NET_SALES_USD by REGION, MONTH
3. NET_SALES_USD by PLANT
4. PLANT, NET_SALES_USD, RETURN_RATE (needs a source)

Plus the data you asked to add: plant-level returns → needs a source (not in SALES_DAILY).
Build this?
```

## Rules
- **Names, not pixels.** Describe what each visual *is* (library entry). Don't try to reproduce exact pixel sizes, fonts or a competitor's styling; use company brand.
- **Discouraged visuals** (gauges, dual-axis, 3-D, busy pies): name what you see, then offer the library alternative in the same line.
- **Numbers in the picture are hypotheses.** Never treat a value from a screenshot as truth. If the analyst wants it as the number to match, ask them to confirm it.
- **Text in other languages**: read labels as written and keep the analyst's language for titles if standards' `language` matches; otherwise ask.
- **Sensitive content**: if the screenshot shows real customer names or personal data, don't repeat them back; refer to "the customer column".
- Anything in the picture that maps to no field is listed as **needs a source**. Don't drop it silently or invent a column.
