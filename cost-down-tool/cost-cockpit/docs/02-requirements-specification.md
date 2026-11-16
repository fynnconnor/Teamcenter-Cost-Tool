# Requirements specification

Cost Cockpit, version 0.1 · 16 November 2026 · basis for the alignment with Product gH2 and R&D

This document turns the first brainstorming into requirements that can be tested. For each of the 13 requirements it states what the user gets, how the Cost Cockpit delivers it, and how to check it on the demo data. Chapter 3 proposes further requirements that the brainstorming does not mention but that the build will need a decision on. Chapter 4 lists add-ins and platform features worth using.

Expected values refer to the synthetic demo data in `seed/` and the golden results in `engine/golden/`.

## 1. Coverage at a glance

| ID | Requirement | Delivered by | Phase |
|---|---|---|---|
| R1 | Detailed cost transparency | Tables Product, CBS Element, Cost Version, Cost Item; model-driven app; Power BI pages 1-3 | 1 |
| R2 | Split by cost type and by NCA / EPC scope | Columns Cost type (item) and Scope, TIC category (element); Power BI page 4 | 1 |
| R3 | Feature-to-TIC dependency | Tables Feature, Feature Impact; flow 03; Power BI pages 6 and 8 | 2 |
| R4 | Cost-driver analysis | Power BI page 3 (Pareto, top items, confidence) | 1 |
| R5 | Teamcenter interface for prices and suppliers | Staging table, mapping table, dataflows A and B; connector template | 1 (file), 4 (service) |
| R6 | Versioning | Cost Version with release flow 02; auditing; Power BI page 5 | 1 |
| R7 | Scaling effects by project size | Scaling rule per CBS element; flow 03; what-if measures; Power BI pages 6-7 | 2 |
| R8 | Regional cost differences | Tables Region, Regional Factor; flow 03; what-if measures | 2 |
| R9 | Benchmarking own vs. competitors | Table Benchmark; Power BI page 9 | 3 |
| R10 | Target per cost component | Table Target; Power BI page 10 | 3 |
| R11 | Idea repository | Table Idea; idea box page; flow 05a | 3 |
| R12 | Measure list and prioritisation | Table Measure with score; command *Convert to measure*; Power BI page 11; flow 05b | 3 |
| R13 | Interface to the LCOH Suite | Table CAPEX Dataset; flow 04 | 4 |

## 2. Requirements in detail

### R1 Detailed cost transparency

**User story.** As a product manager I see the complete cost of a product at reference size, from the total down to the single priced item, so that I know where the money is.

**Solution.** Every cost is a *cost item* (quantity × unit price × FX rate) booked on a leaf of the cost breakdown structure (CBS). Elements sum up their children. The model-driven app maintains the data; Power BI shows tree, matrix and cards.

**Acceptance.**

1. DEMO-V001 shows a total of 91,380,000 EUR and 913.8 EUR/kW.
2. Electrolyser modules (DEMO-1) show 27,000,000 EUR, of which cell stacks 20,000,000 EUR.
3. Drilling from total to *Cell stack* takes at most three clicks in the decomposition tree.
4. A cost item in USD (transformer-rectifier set, 13,200,000 USD at 0.90) shows 11,880,000 EUR.

**To decide.** The real CBS: number of levels, coding, and whether it follows the structure the LCOH Suite uses.

### R2 Split by cost type and scope

**User story.** As a cost engineer I separate material from engineering effort and NCA scope from EPC scope, because they are influenced by different people.

**Solution.** Cost type is a property of the cost item (seven values, among them Material and Engineering hours). Scope and TIC category are properties of the CBS leaf element. Engineering effort is entered as hours × hourly rate.

**Acceptance.**

1. DEMO-V001 by scope: NCA 46,880,000 EUR, EPC 44,500,000 EUR.
2. DEMO-V001 by cost type: Engineering hours 7,500,000 EUR.
3. Each split adds up to the version total.

**To decide.** Whether one CBS element can carry two scopes (then it must be split into two elements), and the final list of cost types and TIC categories.

### R3 Feature-to-TIC dependency

**User story.** As a product manager I see which TIC elements a product feature moves and by how much, so that feature decisions are made with their cost.

**Solution.** A *feature* has one or more *feature impacts*, each on one CBS element, as fixed amount, amount per MW or percent of the element. Selecting features in a scenario adds their effect lines.

**Acceptance.**

1. Feature *Outdoor installation* shows an impact of -40 % on *Foundations and buildings*.
2. Scenario SCN-200-ES with the features Outdoor installation and Redundant rectifier contains two feature lines: -4,418,654 EUR and +3,000,000 EUR.
3. Removing a feature from the scenario and recalculating removes its line.

**To decide.** Who maintains feature impacts (R&D, product management), and whether features can depend on each other.

### R4 Cost-driver analysis

**User story.** As a product manager I see the largest cost drivers at a glance.

**Solution.** Pareto chart and top-item table in Power BI, by item, element, supplier or cost type, with the share of cost that rests on low-confidence prices.

**Acceptance.**

1. The largest item of DEMO-V001 is *Cell stack* with 21.9 %.
2. The cumulative share reaches 100 % at the last item.
3. The page reacts to the version slicer.

### R5 Teamcenter interface

**User story.** As a cost engineer I take prices, quantities and suppliers from Teamcenter instead of typing them.

**Solution.** Teamcenter export file or service call fills a staging table. A mapping table assigns each Teamcenter item to a CBS element and cost type once. A dataflow upserts cost items of the draft version and creates missing suppliers.

**Acceptance.**

1. Importing `export-template.csv` updates six cost items of DEMO-V002; one row (item 100099) appears as *Not mapped*.
2. Importing the same file again creates no duplicates.
3. After the item 100099 is added to the mapping table, the next refresh loads it.
4. Cost items without a Teamcenter item (engineering hours) are unchanged.

**To decide.** Where prices and supplier assignments are maintained today, which attributes hold them, and how often the import runs. See `teamcenter/README.md`.

### R6 Versioning

**User story.** As a product manager I compare the cost status of today with earlier ones and see what changed.

**Solution.** Work happens in a draft version. *Release* freezes it and opens the next draft as a copy. Power BI compares any two versions. Dataverse auditing records who changed which field.

**Acceptance.**

1. Releasing DEMO-V002 produces a released DEMO-V002 and a draft DEMO-V003 with 14 items and the same total.
2. A released version cannot be edited by an editor.
3. Version comparison DEMO-V002 vs. DEMO-V001 shows -1,000,000 EUR: cell stacks -1,000,000, purification +200,000, product engineering -200,000.

**To decide.** Release rhythm (per milestone, quarterly) and who may release.

### R7 Scaling effects

**User story.** As a sales developer I get the cost for any project size without rebuilding the calculation.

**Solution.** Each CBS leaf carries a scaling rule: per module, power law with exponent, or fixed. A scenario applies the rules for a chosen size. Power BI shows the same calculation live with a size slider.

**Acceptance.**

1. Scenario SCN-100-DE (reference size, base region) equals the baseline: 91,380,000 EUR.
2. Scenario SCN-20-IN: cell stacks cost 3,600,000 EUR (one module instead of five, material factor 0.9).
3. The curve *cost per kW over size* falls with size and is identical in Power BI what-if and in stored scenarios.

**To decide.** The scaling rule and exponent per element. Start with estimates, then calibrate against two or three known project sizes.

### R8 Regional cost differences

**User story.** As a sales developer I see what the plant costs at another project site, especially for the TIC part.

**Solution.** A factor per region and cost type relative to the base region. Construction and engineering react strongly, equipment hardly.

**Acceptance.**

1. SCN-200-ES totals 152,180,369 EUR = 760.9 EUR/kW.
2. SCN-20-IN totals 20,535,270 EUR = 1,026.8 EUR/kW.
3. Changing a regional factor and recalculating changes only the lines of that cost type.

**To decide.** The list of regions and the source of the factors: own projects, EPC partner feedback, purchased data.

### R9 Benchmarking

**User story.** As a product manager I compare our cost with competitors and public studies on the same basis.

**Solution.** A benchmark table with value in EUR/kW, plant size, year, scope, TIC category, source and confidence. Power BI compares own and external values.

**Acceptance.**

1. The page shows the demo product (913.8 EUR/kW) next to the two public ISPT values.
2. Every benchmark has a source and a note on what is included.

**To decide.** Who collects competitor data and how sensitive data is protected. No software delivers this data.

### R10 Target per cost component

**User story.** As head of product I set a target per cost component and see the gap.

**Solution.** A target in EUR/kW per CBS element, with year and basis. Power BI shows current, target and gap.

**Acceptance.**

1. Electrolyser modules: current 270.0, target 230.0, gap 40.0 EUR/kW.
2. Sum of targets 790 EUR/kW against 913.8 EUR/kW current.

**To decide.** Level of the CBS at which targets are set, and how targets are derived (benchmark, top-down from LCOH, bottom-up).

### R11 Idea repository

**User story.** As any colleague I submit a cost-down idea in a minute and see what became of it.

**Solution.** Idea box page (or quick-create form) writing to the Idea table; Teams message to the product owner; status visible to the submitter.

**Acceptance.**

1. A submitted idea appears in the view *New ideas* and triggers a Teams message.
2. The submitter sees the status of their ideas.

**To decide.** Licences for occasional submitters, and whether ideas may be anonymous.

### R12 Measure list and prioritisation

**User story.** As product owner I turn ideas into measures with owner, saving, effort and due date, rank them, and track them to the point where the saving shows in a released version.

**Solution.** Command *Convert to measure*. Measure table with degree of implementation (DI1 to DI5), probability, weighted saving and a priority score = weighted saving ÷ implementation cost. Power BI shows funnel, ranking, coverage of target gaps.

**Acceptance.**

1. Measure M-001: weighted saving 840,000 EUR, priority score 4.24.
2. Ranking by score: M-001, M-002, M-003.
3. Electrolyser modules: weighted measures cover 8.4 of the 40.0 EUR/kW gap.

**To decide.** The definition of each DI level, and the score formula.

### R13 Interface to the LCOH Suite

**User story.** As LCOH analyst I use the released CAPEX of a scenario in the LCOH Suite without copying numbers.

**Solution.** *Publish* writes the scenario per scope and TIC category into the table CAPEX Dataset. The LCOH Suite reads that table. The Cost Cockpit stays a separate app.

**Acceptance.**

1. Publishing SCN-200-ES creates one row per scope and TIC category; the rows sum to 152,180,369 EUR.
2. Publishing again replaces the rows of that scenario.
3. The LCOH Suite shows the values with scenario code and version code.

**To decide.** Where the LCOH Suite stores data and the agreed column contract.

## 3. Further requirements to decide

These points are not in the brainstorming. Each needs a yes, no or later from the product team; the default assumed in the build is stated.

| ID | Proposed requirement | Why it matters | Default in the build |
|---|---|---|---|
| N1 | Roles and confidentiality: who may see supplier prices and competitor data | Supplier prices and benchmarks are sensitive | Four security roles; column security possible on unit price |
| N2 | Audit trail of changes | Traceability of cost changes | Dataverse auditing on five tables |
| N3 | Data quality indicators: price age, confidence, items without price | A cost figure is only as good as its oldest price | Fields exist; one card and one view in the report |
| N4 | Reference basis of "per kW" | EUR/kW differs by factor if the basis is AC input, DC input or hydrogen output | Product reference size in MW as entered; basis to be written into the product description |
| N5 | Currency and price year | Mixed currencies and price years distort comparisons | FX rate stored per item and frozen with the version; one escalation factor per scenario |
| N6 | Uncertainty range per cost element | Early estimates are ranges, not points | Not built; confidence field only. Later: low / high factor per element |
| N7 | Four-eyes release of a version | A released version feeds targets and the LCOH Suite | Not built; add an approval step to flow 02 |
| N8 | Price history per item (several quotes) | Shows price trends and negotiation effects | Not built; versions keep history at release points |
| N9 | Link of measures to engineering changes in Teamcenter | Proves that a measure was implemented | Not built; add a text field for the change number |
| N10 | Annual volume and learning effects | Cost-down through volume is a main lever | Not built; later a learning-rate parameter per element |
| N11 | Operating cost or CO2 per element | Would extend the tool towards LCOH and footprint | Out of scope; stays in the LCOH Suite |
| N12 | Languages | Users may expect German labels | English only |
| N13 | Export for management reporting | Slides and Excel are still needed | Power BI export to PowerPoint and Excel |
| N14 | Reminders and escalation for overdue measures | Keeps the pipeline moving | Weekly e-mail in flow 05b |
| N15 | Data volume | Decides whether Power BI import mode and the flows are sufficient | Designed for up to about 20,000 cost items per version |
| N16 | Several products and variants | Variants share most of the structure | Supported: every table hangs on Product; copying a CBS between products is manual |

## 4. Add-ins and platform features

| Add-in or feature | Use in the Cost Cockpit | Cost and conditions |
|---|---|---|
| Editable grid (Power Apps grid control) | Bulk editing of cost items, factors and targets in the app | Built in |
| Hierarchy view for CBS Element | Tree display of the cost structure | Built in; switch on per table |
| *Edit in Excel* (Microsoft Power Apps Office add-in) | Edit and paste many rows in Excel, publish back to Dataverse | Free add-in; Excel desktop or online; allowed by IT? |
| Dataverse dataflows | Teamcenter file import, later ERP actuals | Built in with Dataverse |
| Dataverse auditing and column security | Audit trail, hiding unit prices | Built in |
| Approvals in Teams | Idea decision, optional version release | Built in with Power Automate |
| Power BI decomposition tree, waterfall, funnel | Cost tree, version bridge, measure funnel | Built in |
| Power BI custom visuals *Tornado chart*, *Sankey chart* (Microsoft) or *Deneb* | Sensitivity of cost to exponents and factors; flow of cost from scope to category | Free from AppSource; tenant must allow custom visuals |
| Power BI embedded in the model-driven app | Analysis without leaving the app | Built in; viewers need Power BI Pro |
| Power Platform pipelines and Managed Environments | Controlled transport Dev > Test > Prod | Needs premium licences for all users of managed environments |
| Copilot in Power Apps and Power BI | Generate first versions of forms, pages and visuals; question-and-answer on the data | Depends on tenant settings and licences |
| Copilot Studio agent in Teams | "What does a 300 MW plant in Spain cost?" answered from scenarios | Later; paid by message credits |
| AI Builder document processing | Read prices from supplier quotes | Later; paid credits |
| Fabric link for Dataverse | Large volumes, Python simulation, uncertainty ranges | Later; needs Fabric capacity |
| Teamcenter Power BI integration (release 2606) | Alternative source for BOM data | Depends on installed release and Siemens licence |
| Purchased data packages for regional factors | Regional factors and benchmark prices | Paid; evaluate after the first own calibration |

Community tools such as XrmToolBox can speed up administration, but they are third-party desktop software; use them only if IT allows.
