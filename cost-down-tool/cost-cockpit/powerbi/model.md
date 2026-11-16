# Power BI model and report

The report gives the analysis side of the Cost Cockpit: cost drivers, splits, version comparison, what-if scenarios, benchmarks, target gaps and the measure pipeline. Data comes from Dataverse; nothing is typed into Power BI.

Files: `queries.pq` (tables), `measures.dax` (measures and calculated columns). Build steps are in the build manual, chapter 9.

## Tables and relationships

Import mode. All relationships are one-to-many, single direction, from the first table to the second.

| From (one) | To (many) | Key |
|---|---|---|
| Product | CBS Element | Product Id |
| Product | Cost Version | Product Id |
| Product | Feature | Product Id |
| Cost Version | Cost Item | Cost Version Id |
| Cost Version | Scenario | Cost Version Id |
| CBS Element | Cost Item | CBS Element Id |
| CBS Element | Scenario Line | CBS Element Id |
| CBS Element | Feature Impact | CBS Element Id |
| CBS Element | Target | CBS Element Id |
| CBS Element | Measure | CBS Element Id |
| CBS Element | Idea | CBS Element Id |
| Supplier | Cost Item | Supplier Id |
| Region | Regional Factor | Region Id |
| Region | Scenario | Region Id |
| Feature | Feature Impact | Feature Id |
| Scenario | Scenario Line | Scenario Id |

Not related on purpose: **Compare Version** (second version slicer), **Size MW** (what-if size), **Benchmark** (compared by TIC category label).

Power BI may propose a relationship between Feature and Scenario Line through Feature Id; leave it inactive or delete it.

After loading: add the calculated columns listed at the end of `measures.dax` to CBS Element, hide all Id and Value columns, set the format of EUR measures to whole numbers with thousands separator and of EUR/kW measures to one decimal.

## Report pages

| Page | Visuals | Requirement |
|---|---|---|
| 1 Overview | Cards: Cost EUR, Cost EUR per kW, Target EUR per kW, Gap EUR per kW, Weighted Saving EUR. Slicers: Product, Cost Version. Donut: Cost EUR by Scope. Bar: Cost EUR by L1 Element | R1 |
| 2 Cost structure | Decomposition tree: Cost EUR explained by L1 Element > L2 Element > Cost Type > Cost Item. Matrix: L1 / L2 Element on rows, Scope on columns, Cost EUR and Cost Share | R1, R2 |
| 3 Cost drivers | Pareto: column chart Cost EUR by Cost Item sorted descending, line Cumulative Share. Table: top 20 items with Supplier, Cost Type, Confidence. Card: Share Low Confidence | R4 |
| 4 Splits | Stacked bars: Cost EUR by Cost Type and Scope; by TIC Category and Scope; by Supplier; by Price Source | R2, R5 |
| 5 Version comparison | Slicers: Cost Version, Compare Version. Waterfall: Delta EUR by L1 Element (breakdown L2 Element). Table: CBS Element, Cost EUR, Cost EUR Compare, Delta EUR, Delta Pct | R6 |
| 6 What-if scenario | Slicers: Size MW (single), Region (single), Feature (multi). Cards: WhatIf Cost EUR, WhatIf Cost EUR per kW, delta vs. reference. Bar: WhatIf Base Cost EUR by L1 Element. Line chart: WhatIf Cost EUR per kW by Size MW (put Size MW on the axis, no slicer on it) | R7, R8, R3 |
| 7 Stored scenarios | Matrix: Scenario on columns, L1 Element on rows, Scenario Cost EUR per kW. Stacked bar: Scenario Cost EUR by Scenario and Scope. Table: feature effect lines | R7, R8, R13 |
| 8 Feature effects | Matrix: Feature on rows, L1 Element on columns, Value and Impact Type. Bar: Scenario Feature Effect EUR by Feature for a chosen scenario | R3 |
| 9 Benchmarks | Bar: Value EUR per kW by Subject, colour by Own Product. Scatter: Value EUR per kW over Plant Size MW, label Subject. Table with Source and Confidence | R9 |
| 10 Targets | Clustered bar per L1 Element: Cost EUR per kW, Target EUR per kW. Bar: Gap EUR per kW and Open Gap EUR per kW. Table with Target Basis | R10 |
| 11 Measures | Funnel: Saving EUR by DI Level. Scatter: Weighted Saving EUR over implementation cost, size Priority Score. Table sorted by Priority Score. Cards: Secured Saving EUR, Overdue Measures, New Ideas | R11, R12 |

## Check against the demo data

| Page | Selection | Expected |
|---|---|---|
| Overview | DEMO-V001 | Cost 91,380,000 EUR; 913.8 EUR/kW; NCA scope 46,880,000; EPC scope 44,500,000 |
| Cost drivers | DEMO-V001 | Largest item Cell stack, 21.9 % |
| Version comparison | DEMO-V002 vs. DEMO-V001 | Delta -1,000,000 EUR: cell stacks -1,000,000, purification +200,000, product engineering -200,000 |
| What-if | 200 MW, Spain, Outdoor installation + Redundant rectifier | 152,180,369 EUR; 760.9 EUR/kW |
| What-if | 20 MW, India, no feature | 20,535,270 EUR; 1,026.8 EUR/kW |
| Targets | DEMO-V001 | Electrolyser modules: 270.0 current, 230.0 target, gap 40.0, weighted measures 8.4 EUR/kW |

All expected values are in `../engine/golden/`.

## Refresh, sharing, security

- Publish to a workspace that the Cost Cockpit users can open. Scheduled refresh up to eight times a day with Power BI Pro; add the action *Refresh a dataset* at the end of flows 02 and 03 if results must show up at once.
- The Dataverse connector respects the security roles of the account that refreshes the dataset, not of the viewer. If supplier prices must be hidden from some readers, build a second report without the Cost Item detail or add row-level security roles in the model.
- Suggested custom visuals: none required. The built-in decomposition tree, waterfall and funnel cover the pages above.
