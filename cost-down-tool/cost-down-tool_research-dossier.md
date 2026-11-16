# Cost-down tool: in-house or external?

Research dossier for the make-or-buy decision on a product-cost monitoring tool
Status: 13 November 2026 · Desk research, no vendor contact yet

**Companion files**

| File | Use it for |
|---|---|
| `cost-down-tool_make-or-buy-research.pptx` | The compiled findings as slides |
| `cost-down-tool_decision-workbook.xlsx` | Editable matrices: requirements, long list, KPIs, fit scores, weighted scoring, 5-year cost model, roadmap, RFI questions, sources |
| This dossier | Full detail and reasoning behind every slide, with sources |

**How to read the numbers.** Statements marked with a source ID such as [S17] come from the source list in chapter 15. Everything called a *planning assumption* is my own estimate, built from the public signals described next to it. No vendor has been asked for a quote. Vendor prices in this market are not published, so the cost ranges for external tools are the weakest numbers in this document and should be replaced by RFI answers before the decision meeting.

---

## 1. Summary

**The question.** Should the cost-down tool be built in-house on the Microsoft suite or bought as an external product?

**The answer the evidence supports.** Build it in-house on the Power Platform (option B below), start with a lean MVP, and keep Siemens Teamcenter Product Cost Management as the fallback if deep should-costing of manufactured parts later becomes a core need. Run a short RFI with two or three vendors in parallel so the decision rests on quoted prices and not on my estimates.

**Why.**

1. **The requirements span three software categories, and no external product covers all of them.** Detailed cost roll-up and target costing belong to product cost management (PCM) tools. Project-size scaling and regional differences of total installed cost (TIC) belong to capital-project estimating tools. The idea repository and measure list belong to savings-management tools. The LCOH Suite link is specific to this organisation. The best external tool covers 23 of 39 possible fit points; an in-house design covers 37.
2. **External PCM tools are built for a different problem.** Their strength is calculating what a manufactured part should cost, using shipped labour, machine and material data, largely for automotive-style supplier negotiations. The need here is transparency and tracking at product, scope and TIC level, including engineering hours and the split between NCA scope and EPC scope.
3. **The Microsoft platform is already in use.** The LCOH Suite runs as a Power App. A second app on the same data platform gives the required interface almost for free and avoids the concern that the LCOH Suite itself becomes too large.
4. **Cost.** Planning assumptions give a 5-year total of about EUR 0.5M for in-house option B (range 0.33-0.68M), of which only about EUR 0.18M is cash-out, against about EUR 0.9M for an external PCM suite (range 0.49-1.59M), of which about EUR 0.7M is cash-out. A second tool and a custom integration would still be needed for ideas, measures and the LCOH link.
5. **Time.** An in-house MVP can be in use 10-12 weeks after the go decision. An external tool needs selection, procurement and IT security review before a typical implementation of several months [S19].

**What speaks for buying.** External tools exist today and ship reference data that an in-house tool does not have: Teamcenter PCM delivers factor costs for 67 countries and 454 regions [S5], aPriori 95 regional data libraries [S17], Tset market data for 79 countries [S31]. They carry lower key-person risk. If the main value were expected from supplier should-cost negotiations on manufactured parts, an external tool would be the better choice.

**The main risks of building** are dependency on one developer, scope creep, missing reference data and the Teamcenter interface. Chapter 10 lists mitigations for each.

| Option | Fit (of 39) | Weighted score (1-5) | 5-year cost, base | of which cash-out | First usable release |
|---|---|---|---|---|---|
| In-house B: Power Platform app | 37 | 4.07 | EUR 0.50M | EUR 0.18M | 10-12 weeks |
| In-house C: Fabric data platform | 35 | 3.65 | EUR 0.72M | EUR 0.28M | about 4 months |
| In-house A: Lean (Excel, SharePoint, Power BI) | 26 | 3.50 | EUR 0.24M | EUR 0.03M | 6-8 weeks |
| Teamcenter PCM | 23 | 3.03 | EUR 0.89M* | EUR 0.70M* | 6-12 months incl. selection |
| FACTON EPC | 22 | 2.75 | EUR 0.89M* | EUR 0.70M* | 6-12 months incl. selection |
| Cleopatra Enterprise | 19 | 2.68 | not estimated | not estimated | 5-9 months incl. selection |
| Tset | 19 | 2.63 | EUR 0.89M* | EUR 0.70M* | 5-9 months incl. selection |
| aPriori | 19 | 2.53 | upper end of range* | upper end* | 8-12 months incl. selection |

\* One generic "external PCM suite" cost scenario is used for all PCM products, because no vendor publishes prices. Release times for external tools are planning assumptions: two to four months for selection and procurement plus the implementation time from chapter 5. Fit and weighted scores are a preliminary desk assessment and need to be confirmed in demos.

---

## 2. Requirements

The task description lists a first brainstorming of requirements. For this research they were split into 13 items so that every solution can be scored against the same list.

| ID | Block | Requirement | Proposed priority |
|---|---|---|---|
| R1 | Cost transparency | Status-quo cost transparency at detail level (roll-up over the product / cost breakdown structure) | Must |
| R2 | Cost transparency | Separation of cost types (material vs. engineering effort) and of NCA scope vs. EPC scope | Must |
| R3 | Cost transparency | Show the dependency of product features on TIC topics | Must |
| R4 | Cost transparency | Analysis features such as identification of the largest cost drivers | Must |
| R5 | Cost transparency | Teamcenter interface as input for prices and suppliers | Must |
| R6 | Cost transparency | Versioning to compare over time | Must |
| R7 | Scenario simulation | Scaling effects: automatic cost transparency for different project sizes | Must |
| R8 | Scenario simulation | Regional cost differences by project site, especially for TIC topics | Must |
| R9 | Target costs | Cost benchmarking between own products and competitors | Should |
| R10 | Target costs | Target value per cost component | Must |
| R11 | Target costs | Idea repository fed by colleagues | Should |
| R12 | Target costs | Measure list and prioritisation, with tracking | Must |
| R13 | LCOH Suite | Interface to the LCOH Suite (Power App) to fill its database | Must |

The priorities are a proposal. The requirements catalogue to be agreed with Product gH2 and R&D (next step 2 in the task description) should confirm them.

**What the list implies**

- R1, R2, R4, R6 and R10 are classic product-cost-management functions.
- R7 and R8 concern total installed cost of a plant. PCM tools model production volume and manufacturing location, which is a different kind of scaling. Capital-project estimating tools model plant size and construction location.
- R3 (feature-to-TIC mapping) is specific to this product. No researched tool offers it as a standard function; it has to be configured or built in every option.
- R11 and R12 are savings-management functions that PCM tools do not offer.
- R9 depends on data more than on software. No tool ships competitor cost data for green-hydrogen plants. Chapter 13 lists public sources that can seed the benchmark table.
- R13 favours any solution on the same Microsoft platform as the LCOH Suite.

---

## 3. Market landscape

Eighteen products were screened. They fall into five categories.

| Category | Products screened | Covers | Does not cover |
|---|---|---|---|
| Product cost management (PCM) | Teamcenter Product Cost Management, aPriori, FACTON EPC, Tset, SAP Product Lifecycle Costing, DFMA, Costimator | R1, R2, R4, R6, R10; R5 in part | R7, R8 for TIC; R11, R12; R13 |
| Capital-project / TIC estimating | Cleopatra Enterprise, Aspen Capital Cost Estimator, CostOS, EcoSys | R7, R8, R9 for projects; R6 | R5, R3, R11, R12 |
| Parametric estimating | SEER, TruePlanning, 4cost | Early-phase estimates from parameters | Most of the list; aerospace and defence heritage |
| Savings / measure management | Valuedesk, Falcon | R11, R12 | The cost model itself |
| Data and platforms | costdata (benchmark data), Mendix with Teamcenter Connector (low-code) | Inputs for an own tool | Not a solution on their own |

Notes on products that were not shortlisted:

- **SAP Product Lifecycle Costing** is an early-costing tool on SAP HANA that hands costs over to SAP S/4HANA controlling. SAP describes a continuing roadmap towards profitability and break-even simulation [S54]. It is only relevant if the SAP landscape is the master for cost data. A maintenance end date could not be confirmed from public sources.
- **Aspen Capital Cost Estimator** uses design-based installation models with five to six regional bases (US, Europe, UK, Japan, Middle East, China depending on version) [S52]. It targets process-plant estimating departments and has no product-structure or Teamcenter orientation.
- **CostOS** (Nomitech) is an estimating tool comparable to Cleopatra. Capterra lists a starting price of USD 2,800 per user, which is the only price point found in this category and may be outdated [S53].
- **4cost** was not researched in depth; no usable public information came up.

The full long list with relevance ratings is in the workbook, sheet *Long list*.

---

## 4. External shortlist

Five products were shortlisted so that each plausible way of buying is represented: the Teamcenter-native product, the market leader for automatic should-costing, a German enterprise costing suite, a flexible SaaS newcomer, and the one tool built for TIC.

### 4.1 Siemens Teamcenter Product Cost Management

**What it is.** Siemens' product costing application: product costing, tool costing, profitability calculation, should-cost and purchase price analysis, and a CO2e footprint calculator [S5][S6]. Releases appear twice a year; 2606 is the current one [S1].

**Facts**

- **Reference data.** Production-site data for 67 countries and 454 regions in release 2406, with labour cost for two skill levels, labour burden for three shifts, floor-space cost and interest rates. Energy prices and interest rates are updated twice a year, the machine database four times a year, material prices quarterly. Version 9.3 listed about 10,000 materials [S5].
- **Teamcenter.** Product structures are imported directly from Teamcenter, including attribute mapping for make-or-buy, plant and technology [S1]. The 2026 beta programme listed a cost-management integration that manages and rolls up product cost targets and values inside Teamcenter [S11].
- **Interfaces.** The product has its own OpenAPI REST specification [S14]. Release 2606 adds an endpoint for aggregated profitability KPIs so that data can go to Power BI, Tableau or SAP Business Data Cloud without manual Excel export [S1][S2]. Release 2506 added Excel export of detailed cost breakdowns [S3].
- **Scenarios and targets.** Technical and business what-if scenarios for assemblies and versions; best, normal and worst case in profitability calculation [S6]. Target costing is a documented use case [S12].
- **Deployment and licence.** On-premises, or SaaS as Teamcenter X Product Cost Management with named end-user licences and add-on modules [S7]. AI copilots are in pilot [S1].
- **Price.** Not published. Third parties report Teamcenter X Essentials at roughly USD 150-200 per user and month, which is not specific to cost management, and AWS Marketplace lists a minimum of 20 named users for Teamcenter X [S13].

**Assessment.** The strongest external candidate because requirement R5 is native and the vendor is already the PLM supplier. The data model follows manufactured product structures. Plant-size scaling, construction location factors, the feature-to-TIC mapping, ideas and measures are outside its design, and the LCOH link would be an API project.

### 4.2 aPriori

**What it is.** A US platform that simulates manufacturing cost and manufacturability from 3D CAD geometry for design, sourcing and quoting [S18][S21].

**Facts**

- 95 regional data libraries according to the pricing page, 87 regional economic models according to the FAQ, and more than 450 manufacturing process simulations [S17][S18].
- PLM integration with Teamcenter and Windchill is part of the packaging [S17].
- Licence: named users on annual subscription, with a foundation package sized to the deployment plus regional libraries and modules [S19][S23].
- Price signals, all third party: an estimated USD 4,000-17,000 per month to start, about USD 400-2,000 per month for additional regional data, one-off setup USD 10,000-50,000, integrations USD 10,000-50,000 and digital-factory customisation USD 15,000-75,000 [S20]. One comparison says enterprise platforms of this kind typically start above USD 100,000 per year [S21].
- G2 user reviews report an average of 6 months to implement and 18 months to return on investment, and reviewers note that the annual cost is hard to absorb for smaller teams [S19].
- A Forrester study commissioned by aPriori models a composite manufacturer with USD 5 billion revenue: costs of USD 3.3M against benefits of USD 22.9M over three years [S22]. The scale of that composite is far from a 40-user cost-monitoring tool.

**Assessment.** Best in class for automatic cost-driver analysis of manufactured parts and well connected to Teamcenter. It needs 3D CAD as input and adds little for engineering hours, EPC scope, TIC, plant benchmarking or measure tracking. It sits at the expensive end of the market.

### 4.3 FACTON EPC

**What it is.** A German enterprise product costing suite covering quotation calculation, should costing, design-to-cost, product costing in controlling and management reporting, plus product carbon footprint [S24].

**Facts**

- Sold as EPC Standard and EPC Professional with add-on modules [S26].
- Runs on-premises or as SaaS; a cloud offer on Microsoft Azure was announced in 2016, and the Should Costing solution is listed on Microsoft Marketplace [S25][S28][S29].
- Interfaces to ERP and PLM exist. Public material names PTC Windchill and Power BI. A Teamcenter connector is not documented publicly and has to be confirmed [S26][S30].
- Should Costing ships benchmark data for wages, overheads and machines [S24].
- Published customers include Airbus, Porsche, Ford, Deutz, Brose, MANN+HUMMEL, mtu, Wittenstein, Safran, MAHLE, Hauni and Hettich. The vendor targets mechanical and plant engineering among other sectors [S24][S27].
- No price and no implementation duration are published. The vendor describes the standard solution as designed for rapid implementation [S25].

**Assessment.** Closest in spirit to the cost-transparency and target-costing blocks, with versioning as a core concept and references in plant engineering. Open points are the Teamcenter link, TIC scaling and regional construction factors. Ideas and measures are not covered.

### 4.4 Tset

**What it is.** A Vienna-based SaaS company, founded in 2018, for product cost and CO2e calculation. It raised a Series A of about EUR 12.7-13 million and reports between 70 and more than 100 employees depending on the source [S32][S33][S34].

**Facts**

- More than 50 calculation modules and validated market data for 79 countries covering materials, machine rates, energy and labour [S31][S38].
- Tset Studio lets customers build calculators from scratch, adapt Tset calculators or bring their own Excel logic. Calculators are versioned [S31][S37].
- API-first. Brose's IT built a SAP-to-Tset workflow on the open API; BMW Group runs its cost-engineering master data on an API-first architecture [S35][S36].
- Published customers: AGCO, Brose, Lego, thyssenkrupp, ZF and BMW Group [S33].
- Pricing is "flexible SaaS pricing based on company size, usage and required features"; no figures are published [S37].
- No Teamcenter connector is documented publicly.

**Assessment.** The most adaptable external product, because own calculation logic can be migrated instead of adopting a fixed method. The Teamcenter interface would be a project, the heritage is automotive, and the vendor is a venture-funded scale-up. It is worth checking whether a group-level relationship already exists.

### 4.5 Cleopatra Enterprise

**What it is.** A Dutch product for capital-project cost estimating, cost control and benchmarking, used in process industries, energy and EPC [S41][S43].

**Facts**

- Smart cost models, schedule integration, location-factor tables and flexible breakdown structures. The vendor states support for all AACE estimating methods [S39].
- Ships cost-engineering knowledge bases (CESK) and lets customers migrate their own cost data [S40].
- A benchmarking module derives metrics from completed and running projects and compares them, normalised for location and time [S41][S44].
- Integrates with SAP, Excel, Power BI and Oracle P6 [S42]. No Teamcenter integration was found.
- Standard and Professional editions, cloud or on-premises, prices on request [S40][S43].
- ITER Organization is a published user for assembly and installation estimates [S42].

**Assessment.** The only shortlisted product that answers R7 and R8 natively, and it handles NCA and EPC scope well through breakdown structures. It is not a product-costing tool: no bill-of-material logic, no Teamcenter link, no feature mapping, no ideas or measures. It would be a second system next to a product cost model.

### 4.6 Complementary products

| Product | What it adds | Commercial information | Role |
|---|---|---|---|
| Valuedesk (Bielefeld) | Capture of ideas, management and measurement of savings measures, dashboards, catalogue of optimisation methods [S46][S47] | Packages VD-READY (10 full users, 200 measures, 1-month term), VD-GROW (20 users, 400 measures, 12 months) and VD-ENTERPRISE; prices on request [S45] | Covers R11 and R12 without a cost model |
| Falcon (Nordantech, Hamburg) | Tracking of measure programmes with degree-of-implementation reporting [S50] | Third-party information: EUR 1,250 per month including 10 users, EUR 35 per additional user and month up to 50 users [S49] | Covers R12 |
| costdata (Cologne) | Benchmark database with more than 45 million data points in 18 segments for more than 130 countries, including wages, machine rates, material prices and location factors [S51] | Sold with the calculation software or as a data package alone; prices on request | Data source for an in-house tool |
| Mendix with Teamcenter Connector (Siemens) | Low-code apps directly on Teamcenter data; the Teamcenter Extension generates the integration building blocks [S16] | Mendix platform licence | Alternative build platform outside the Microsoft suite |

The costdata data package points to a hybrid that fits an in-house build well: buy the reference data, build the tool.

---

## 5. KPIs for the external decision

### 5.1 KPI matrix

| KPI | Teamcenter PCM | aPriori | FACTON EPC | Tset | Cleopatra |
|---|---|---|---|---|---|
| Fit to R1-R13 (of 39) | 23 | 19 | 22 | 19 | 19 |
| Teamcenter integration | Native | Standard integration | To be confirmed | Project via API | None found |
| Link to Power Platform / LCOH Suite | REST API, Power BI endpoint | Integration layer, API | Power BI named | Open API | Power BI, Excel |
| Reference data shipped | 67 countries, 454 regions | 95 regional libraries | Wages, overheads, machines | 79 countries | CESK knowledge bases, location factors |
| Plant-size scaling and construction regions | Workaround | Workaround | Workaround | Workaround | Native |
| Ideas and measure tracking | No | No | No | No | No |
| Deployment | On-premises or SaaS | Cloud or on-premises | On-premises or SaaS | SaaS | Cloud or on-premises |
| Licence model | Named users plus modules | Named users, annual | Editions plus modules | SaaS by size and usage | Quote |
| Public price signal | None | USD 48k-204k per year estimated by third party | None | None | None |
| Implementation time after contract | 4-9 months* | about 6 months [S19] | 4-9 months* | 3-6 months* | 3-6 months* |
| Vendor risk | Low | Low-medium | Low-medium | Medium | Low-medium |

\* Planning assumption.

The full matrix with 18 KPI rows per product is in the workbook, sheet *External KPIs*.

### 5.2 Cost and time: what is known

- **No PCM vendor publishes prices.** The only numeric signals concern aPriori and come from third-party sites [S20][S21].
- **A general rule of thumb for enterprise software** puts implementation services at one to three times the first-year licence fee [S56].
- **Planning assumption used in this dossier for an "external PCM suite":** licence EUR 60,000 / 110,000 / 200,000 per year (low / base / high) for about 10 editing users plus viewers; implementation services EUR 60,000 / 150,000 / 300,000; internal project effort 60 / 90 / 140 person-days; internal key-user effort 20 / 30 / 45 person-days per year.
- **Lead time before implementation.** RFI, demos, commercial negotiation, IT security and data-protection review typically take two to four months in a corporate environment (planning assumption).

### 5.3 What to ask vendors

The workbook sheet *RFI and open questions* holds a ready list. The three questions that separate the products fastest are:

1. Show on our sample data how engineering hours and the NCA / EPC scope split are represented.
2. How do you model plant-size scaling and regional construction factors?
3. Is the Teamcenter connector a standard product for our Teamcenter release, and what does a fixed-price implementation cost including the interface?

---

## 6. In-house options on the Microsoft suite

Three options were developed. They are stages of one path more than competing alternatives: A can be the MVP of B, and C is a possible later evolution of B.

### 6.1 Option A: Lean (Excel, SharePoint, Power BI)

**Idea.** Bring today's Excel cost data into a fixed structure, store it in SharePoint, analyse it in Power BI.

| Aspect | Design |
|---|---|
| Data storage | SharePoint lists and Excel files |
| Calculation | Excel formulas, Power Query, DAX measures |
| User interface | Excel for editing, Power BI for analysis, Teams tab |
| Teamcenter | Scheduled or manual export of BOM, prices and suppliers into SharePoint |
| LCOH Suite | Shared lists or export files |
| Versioning | Dated snapshots; limited audit trail |
| Scenarios | Parameter tables for scale exponent and regional factor; what-if parameters in Power BI |
| Ideas and measures | SharePoint list with form and status; tracking in Power BI |
| Licences | Included in Microsoft 365; Power BI Pro at USD 14 per user and month where not already licensed [S65] |
| Effort (planning assumption) | 60 developer person-days, 25 SME person-days, about 35 person-days per year to run |
| Time | MVP in 6-8 weeks, complete in about 3 months |

**Strengths.** Fastest and cheapest, no premium licences, ideal to prove the data model and the reports.

**Limits.** SharePoint lists are flat and not relational, have a 5,000-item list-view threshold, and Power Apps delegation limits apply; item-level security is cumbersome [S70]. Spreadsheet-based models carry a known error risk: field audits found errors in 0.38% to 2.5% of cells, and most large spreadsheets contain at least one error [S71]. The Teamcenter step stays manual.

**Best used as** prototype and phase-1 MVP, and as fallback.

### 6.2 Option B: Power Platform app ("Cost Cockpit")

**Idea.** A dedicated app with a relational cost database on the same platform as the LCOH Suite. Two apps share one data backbone, which answers the concern that building everything into the LCOH Suite would make it too large.

| Aspect | Design |
|---|---|
| Data storage | Dataverse tables for cost breakdown structure, cost items, versions, features, scenarios, regions, benchmarks, targets, ideas and measures |
| Calculation | Roll-ups and snapshot flows in Dataverse and Power Automate; DAX for analysis; scenario results stored per run |
| User interface | Model-driven app for data and workflow; an idea-box page for all colleagues in Teams and on mobile; embedded Power BI dashboards |
| Teamcenter | File import in phase 1; in phase 4 a custom connector to Teamcenter services through the on-premises data gateway, or the Teamcenter 2606 Power BI integration |
| LCOH Suite | Shared Dataverse tables, or a versioned CAPEX dataset that the LCOH Suite reads |
| Versioning | Explicit version table with a freeze flow, Dataverse auditing at table and column level [S59], version bridge in Power BI |
| Scenarios | Scaling rules and regional factors as tables per cost element; scenario builder; side-by-side comparison |
| Ideas and measures | Idea-to-measure workflow with approval, degree-of-implementation levels, prioritisation score and tracking against targets |
| Licences | Power Apps Premium USD 20 per user and month, or pay-as-you-go USD 10 per active user per app and month; Power BI Pro USD 14; Power Automate Premium USD 15 for flow owners [S62][S64][S65] |
| Effort (planning assumption) | 190 developer person-days, 60 SME person-days, about 50 person-days per year to run |
| Time | MVP in 10-12 weeks, full scope in 6-7 months |

**Platform facts that matter**

- Power Apps Premium includes 250 MB of Dataverse database and 2 GB of file capacity per user, pooled at tenant level; extra database capacity costs USD 40 per GB and month [S62].
- The per-app plan at USD 5 was closed to new Enterprise Agreement and MPSA customers on 2 January 2026; sources disagree on its availability through CSP [S63].
- Deployment pipelines require target environments to be Managed Environments, and all users in them need premium licences [S57].
- Dataverse is relational and supports role-based security down to row and column level, which SharePoint lists do not [S70].
- Power Apps now offers code apps, generative pages and AI-assisted creation of model-driven apps as generally available features, which shortens build time for standard screens [S68].
- A Forrester study commissioned by Microsoft reports a 50% reduction in app development time for professional developers using Power Apps [S67].

**Strengths.** Covers all 13 requirements by design, shares the platform with the LCOH Suite, keeps structure and logic under own control, offers role-based security and audit, and needs little cash-out.

**Limits.** Reference data and benchmarks have to be collected. The Teamcenter connector has to be built. Every app user needs a premium licence. The tool needs a named owner after go-live.

**Best used as** the target solution.

### 6.3 Option C: Fabric data platform

**Idea.** A cost data hub in Microsoft Fabric with a code-based scenario engine and Power BI on top.

| Aspect | Design |
|---|---|
| Data storage | OneLake Delta tables or Fabric SQL database |
| Calculation | Python and SQL in Fabric notebooks: scaling, regional factors, uncertainty ranges |
| User interface | Power BI reports with write-back through translytical task flows; a Power App for workflows |
| Teamcenter | Automated ingestion pipelines from Teamcenter services or exports, and from ERP |
| LCOH Suite | "Link to Microsoft Fabric" exposes Dataverse tables as shortcuts without copying [S61]; results are written back by flow or API |
| Licences | Fabric capacity (F2 about USD 263 per month pay-as-you-go, about USD 156 reserved), Power BI Pro for all viewers below F64, Power Apps Premium for app users [S65][S66] |
| Effort (planning assumption) | 320 developer person-days, 70 SME person-days, about 70 person-days per year to run |
| Time | MVP in about 4 months, full scope in 9-10 months |

**Platform facts.** Translytical task flows let report buttons write data back to Fabric databases through user data functions; several sources report general availability since March 2026 [S58][S73]. Reservations reduce Fabric capacity cost by about 41% [S66].

**Strengths.** Scales to ERP actuals and large BOM volumes, strongest simulation capability, clean analytics architecture.

**Limits.** Highest effort and skill demand, more IT involvement, and still needs the app layer of option B for ideas and measures. Over-sized for a first release.

**Best used as** a later evolution of B if data volume or simulation depth requires it.

### 6.4 Side by side

| | A: Lean | B: Power Platform | C: Fabric |
|---|---|---|---|
| Fit to R1-R13 (of 39) | 26 | 37 | 35 |
| Build effort, person-days (dev + SME) | 60 + 25 | 190 + 60 | 320 + 70 |
| Licences per year, base | about EUR 6,000 | about EUR 15,000 | about EUR 14,000 |
| 5-year cost, base (range) | EUR 0.24M (0.15-0.33) | EUR 0.50M (0.33-0.68) | EUR 0.72M (0.52-0.99) |
| MVP / full scope | 6-8 weeks / 3 months | 10-12 weeks / 6-7 months | 4 months / 9-10 months |
| Main risk | Fragility, manual steps | Key person, scope creep | Complexity, skills |

---

## 7. How the in-house solution works

This chapter is the implementation manual for option B. It also applies to A, with Excel and SharePoint in place of Dataverse, and to C, with Fabric tables.

### 7.1 Architecture in five layers

1. **Sources.** Teamcenter (product structure, prices, suppliers), existing Excel cost sheets, ERP actuals where available, public and purchased benchmark data, the LCOH Suite.
2. **Integration.** Power Query dataflows for files, Power Automate flows for scheduled loads and approvals, a custom connector to Teamcenter through the on-premises data gateway.
3. **Data backbone.** Dataverse in the same environment family as the LCOH Suite.
4. **Apps and reports.** The Cost Cockpit model-driven app, the idea-box page, Power BI reports.
5. **Governance.** Development, test and production environments, managed solutions, pipelines, security roles, auditing.

### 7.2 Data model

| Table | Content | Serves |
|---|---|---|
| Product and variant | Product, module size, design status | R1 |
| CBS element | Hierarchical cost breakdown structure; attributes for scope (NCA / EPC / owner), TIC category and responsible person | R1, R2 |
| Cost item | Lowest level: Teamcenter item ID, supplier, quantity, unit price, currency, cost type (material, engineering hours, manufacturing, logistics, services), price source, price date, confidence | R1, R2, R5 |
| Cost version | Snapshot header: name, date, status, baseline flag; cost values are stored per version | R6 |
| Feature and feature-CBS link | Product features or design options and their effect on cost elements (fixed amount, amount per MW, factor) | R3 |
| Scaling rule | Per CBS element: method (per module, power law, fixed), exponent, reference size, validity range | R7 |
| Region and regional factor | Factor per region and cost category (labour rate, labour productivity, materials, logistics, duties), with source and date | R8 |
| Scenario and scenario result | Project size, region, feature set, price year; computed cost per CBS element | R7, R8 |
| Benchmark | Own product or competitor, source, year, plant size, cost per CBS element in EUR per kW, confidence | R9 |
| Target | Target value per CBS element and target date, with basis (benchmark, top-down from LCOH, bottom-up) | R10 |
| Idea | Title, description, submitter, affected CBS element, estimated saving, effort, status | R11 |
| Measure and measure tracking | Owner, saving in EUR per kW, one-off cost, probability, degree of implementation, due date; planned vs. realised saving per version | R12 |
| Exchange rate and escalation index | Currency conversion and price-year adjustment | R6, R8 |

### 7.3 Calculation logic

**Roll-up.** The cost of a CBS element is the sum of its children; the cost of a leaf is quantity × unit price × exchange rate of its cost items. Every figure can be sliced by cost type, scope and TIC category, which gives the NCA / EPC and material / engineering views (R2) and the Pareto of cost drivers (R4).

**Scaling for project size S.** Each CBS element carries one of three rules:

- *Per module:* cost = cost per module × number of modules. Used for the modular product scope.
- *Power law:* cost(S) = cost(S_ref) × (S / S_ref)^n. Used for shared balance-of-plant and site scope. The "six-tenths rule" (n ≈ 0.6) is the conventional starting value in process-plant estimating; the exponent has to be calibrated per element from own projects and quotes.
- *Fixed:* cost independent of size, for example one-time engineering. Cost per kW falls in proportion to size.

Public studies illustrate why the rule must differ by element. Balance-of-plant cost for PEM systems is reported to fall from USD 848 per kW at 1 MW to USD 87 per kW at 1 GW, with most of the gain reached by about 100 MW [S79].

**Regional adjustment.** Cost(region) = Σ over cost categories of cost(category) × factor(region, category). Separate factors for labour, materials, equipment and indirect costs are used because construction labour varies far more between regions than equipment prices. Sources for factors are own projects, EPC partner feedback, public indices and purchasable data sets such as costdata or Intratec location factors [S51][S81].

**Feature dependency.** A feature switches cost effects on or off through the feature-CBS link. The report shows per feature which TIC elements move and by how much, and a scenario can be calculated with any feature set.

**Target gap.** Gap = current cost − target per CBS element. Measures are assigned to CBS elements. The dashboard shows how much of the gap is covered by measures at each degree of implementation.

**Degree of implementation.** A five-level scale is proposed, as commonly used in cost-reduction programmes: 1 idea, 2 evaluated, 3 decided, 4 implemented, 5 effective in the released cost version.

**Prioritisation.** Score = saving × probability ÷ (implementation effort + one-off cost), shown together with an impact / effort matrix.

**LCOH link.** A released scenario produces a CAPEX dataset (TIC in EUR per kW by scope, with version stamp) that the LCOH Suite reads.

### 7.4 Versioning

A "freeze" action copies the current cost lines into a released version that can no longer be edited. Dataverse auditing records who changed which field in working data [S59]. Power BI compares any two versions as a bridge chart by CBS element and by cause (price, quantity, design, scope).

### 7.5 Teamcenter interface

Five routes exist. The recommended sequence is T1 at the start and T3 or T2 later.

| Route | How | Effort | Precondition | Limit |
|---|---|---|---|---|
| T1 File export | Scheduled or manual export of BOM, prices and suppliers to SharePoint; loaded by Power Query | Days | Teamcenter key user | Manual step, no live data |
| T2 Teamcenter Power BI integration | Teamcenter 2606 ships a Power BI integration with templates for BOMs, programme plans, schedules and search results [S8][S9][S10] | Low to medium | Release 2606 or later; licensing to be confirmed | Reporting-oriented; exposure of price and supplier attributes must be tested |
| T3 Services via custom connector | A Power Automate custom connector calls Teamcenter services through the on-premises data gateway [S69] | 15-30 person-days | Service account, API documentation for the installed release, IT security approval | There is no single universal REST API for core Teamcenter data; integrations usually use the services layer with JSON [S14][S15] |
| T4 Existing middleware | An integration product already operated by IT also delivers to Dataverse or Fabric | Medium to high | Middleware in place | Depends on the IT roadmap |
| T5 Via Teamcenter PCM | Its own REST interface exposes calculations and KPIs [S1][S14] | Low to medium | Teamcenter PCM licence | Hybrid scenario only |

One point must be clarified before any design work: whether prices and supplier assignments are really maintained in Teamcenter, or whether Teamcenter holds the structure while prices sit in the ERP system or in Excel.

### 7.6 Security and operation

- Security roles: reader, editor per scope, measure owner, administrator. Competitor benchmarks and supplier prices can be restricted by role.
- Three environments with managed solutions and pipelines [S57].
- Release rhythm: quarterly after go-live.
- Run organisation: product owner in Product gH2, a developer with a trained deputy, IT for platform operation.

---

## 8. Roadmap for the in-house path

The roadmap assumes option B with a lean start. It takes about 30 weeks from the go decision to full scope.

| Phase | Weeks | Goal | Main work packages | Result / gate |
|---|---|---|---|---|
| 0 Mobilise and decide | 1-4 | Make-or-buy confirmed; scope and data sources clear | Requirements catalogue with Product gH2 and R&D; status-quo tool landscape and data inventory; cost breakdown structure, cost types, scope split, TIC categories; licence and environment check; RFI to 2-3 vendors; governance | Gate G0: decision paper, requirements catalogue, solution design, backlog |
| 1 MVP: cost transparency | 5-12 | One trusted, versioned cost baseline | Data model and app; import of the baseline from Excel and a Teamcenter export; tagging by cost type, scope and TIC category; first version freeze; Power BI cost tree, Pareto, NCA vs. EPC split, version bridge | Gate G1: MVP in use; continue, adjust or fall back to external |
| 2 Scenario simulation | 13-18 | Cost for any project size and region | Scaling rules per element; regional factor tables; scenario builder; comparison report; calibration against known projects | Release 2 |
| 3 Targets and cost-down | 19-24 | Targets per component and a managed measure pipeline | Benchmark table; target and gap view; idea box; measure list with degree of implementation and prioritisation; tracking dashboard | Release 3 |
| 4 Integrate and industrialise | 25-30 | Automated data flows and a supportable product | Automated Teamcenter interface; LCOH Suite link; security roles, auditing, pipelines; test cases against legacy Excel; training, documentation, hand-over | Release 4: go-live for all users |

**Effort (planning assumption).** 190 developer person-days (15, 45, 35, 40 and 35 for phases 0 to 4, plus 20 for project management, testing, training and documentation) and 60 SME person-days.

**Team**

| Role | Who | Load |
|---|---|---|
| Sponsor | Head of department | 2 hours per month |
| Product owner | Product gH2 | 0.2-0.3 FTE during build |
| Power Platform developer | Internal or external | about 1.0 FTE during build |
| Cost engineering SMEs | Product, R&D, Sales Development | about 0.2 FTE in total |
| Teamcenter key user / PLM IT | IT, Engineering | 10-15 person-days |
| IT / Power Platform CoE | IT | 5-10 person-days |
| Key users | Product, R&D, Procurement | 1-2 days per release |

**Two exit ramps keep the decision reversible.** At gate G0 the RFI answers are on the table. At gate G1 the MVP shows whether the data and the platform carry the concept. Until then, about 60 developer person-days are spent, and the cost breakdown structure, the cleaned baseline and the requirements catalogue are needed for an external tool as well.

---

## 9. Comparison

### 9.1 Requirement fit

Scale: 0 not covered, 1 workaround or heavy customisation, 2 largely covered by configuration, 3 native or designed in.

| Requirement | TC PCM | aPriori | FACTON | Tset | Cleopatra | In-house A | In-house B | In-house C |
|---|---|---|---|---|---|---|---|---|
| R1 Detailed cost roll-up | 3 | 2 | 3 | 3 | 2 | 2 | 3 | 3 |
| R2 Cost type and scope split | 2 | 1 | 2 | 2 | 2 | 3 | 3 | 3 |
| R3 Feature-to-TIC mapping | 1 | 0 | 1 | 1 | 1 | 2 | 3 | 3 |
| R4 Cost-driver analysis | 2 | 3 | 2 | 2 | 2 | 3 | 3 | 3 |
| R5 Teamcenter interface | 3 | 3 | 2 | 1 | 0 | 1 | 2 | 3 |
| R6 Versioning | 3 | 2 | 3 | 2 | 2 | 1 | 3 | 3 |
| R7 Scaling effects | 1 | 1 | 1 | 1 | 3 | 2 | 3 | 3 |
| R8 Regional differences | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 3 |
| R9 Benchmarking | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 2 |
| R10 Target per component | 3 | 2 | 3 | 2 | 1 | 2 | 3 | 3 |
| R11 Idea repository | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 2 |
| R12 Measures and prioritisation | 1 | 1 | 1 | 0 | 0 | 2 | 3 | 2 |
| R13 LCOH Suite interface | 1 | 1 | 1 | 2 | 1 | 2 | 3 | 2 |
| **Sum (of 39)** | **23** | **19** | **22** | **19** | **19** | **26** | **37** | **35** |

**Reading the matrix fairly.** The in-house scores describe a target design. Nothing of it exists today, whereas the external products can be demonstrated tomorrow. That difference is captured in the cost, time and risk criteria of the weighted scoring, not in the fit score.

### 9.2 Five-year cost

Planning assumptions: 10 editing users and 30 contributors or viewers; internal day rate EUR 800; external day rate EUR 1,100; USD list prices converted at 0.90. All inputs can be changed in the workbook, sheet *TCO model*.

| Scenario | One-off internal effort | One-off external | Licences, 5 years | Run effort, 5 years | Total, base | Range low-high | Cash-out, base |
|---|---|---|---|---|---|---|---|
| In-house A: Lean | 68,000 | 0 | 30,240 | 140,000 | 238,240 | 152,000-330,240 | 30,240 |
| In-house B: Power Platform | 124,000 | 104,500 | 75,060 | 200,000 | 503,560 | 329,300-676,860 | 179,560 |
| In-house C: Fabric platform | 158,400 | 211,200 | 69,444 | 280,000 | 719,044 | 518,024-993,848 | 280,644 |
| External PCM suite | 72,000 | 150,000 | 550,000 | 120,000 | 892,000 | 488,000-1,592,000 | 700,000 |
| External PCM suite + measure tool + LCOH link | 96,000 | 172,000 | 688,000 | 160,000 | 1,116,000 | 639,500-1,835,000 | 860,000 |

All figures in EUR.

**Observations**

- The in-house options consist mainly of internal effort. If that capacity exists, cash-out for option B is about a quarter of the cash-out for an external suite.
- The external ranges are wide because prices are unknown. At the low end, an external suite costs about the same as in-house option B at its base case. The RFI decides this point.
- Buying a PCM suite does not remove in-house work: the fifth scenario adds a measure-tracking tool and a custom link to the LCOH Suite to reach comparable scope.
- Data stewardship, meaning keeping cost data current, is needed in every option and is not included.

### 9.3 Weighted scoring

| Criterion | Weight | TC PCM | aPriori | FACTON | Tset | Cleopatra | In-house A | In-house B | In-house C |
|---|---|---|---|---|---|---|---|---|---|
| Functional fit (from 9.1) | 30% | 2.9 | 2.4 | 2.8 | 2.4 | 2.4 | 3.3 | 4.7 | 4.5 |
| Teamcenter integration | 10% | 5 | 4 | 3 | 2 | 1 | 2 | 3 | 4 |
| LCOH Suite / Power Platform integration | 10% | 2 | 2 | 2 | 3 | 2 | 4 | 5 | 4 |
| 5-year cost | 15% | 2 | 1 | 2 | 2 | 3 | 5 | 4 | 3 |
| Time to first usable release | 10% | 2 | 2 | 2 | 3 | 3 | 5 | 4 | 2 |
| Flexibility / ownership of cost logic | 10% | 2 | 2 | 3 | 3 | 3 | 4 | 5 | 5 |
| Reference data and methods out of the box | 5% | 5 | 5 | 4 | 4 | 4 | 1 | 1 | 1 |
| Sustainability and risk | 10% | 5 | 4 | 4 | 3 | 4 | 2 | 3 | 3 |
| **Weighted total (1-5)** | | **3.03** | **2.53** | **2.75** | **2.63** | **2.68** | **3.50** | **4.07** | **3.65** |

**Sensitivity.** In-house B stays ahead under any plausible weighting because it leads on fit, LCOH integration and flexibility at the same time. The ranking among external products is sensitive: with more weight on reference data and vendor stability, Teamcenter PCM extends its lead; with more weight on TIC scenarios, Cleopatra overtakes it. Weights and scores are editable in the workbook, sheet *Scoring*.

---

## 10. Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| **In-house:** key-person dependency on the developer | High | Medium | Two trained makers, managed solutions, documentation, IT CoE involved from phase 0 |
| **In-house:** scope creep | Medium | High | Separate app on a shared data backbone, MVP first, one product owner, gate after each phase |
| **In-house:** Teamcenter does not hold clean prices and suppliers | High | Medium | Data inventory in phase 0, price source and confidence per cost item, named data owners |
| **In-house:** no shipped reference data | Medium | High | Start with public studies and own projects; buy a data package if needed |
| **In-house:** Teamcenter API access delayed by IT security | Medium | Medium | Start with file export, clarify the API route in parallel, test the Teamcenter Power BI integration |
| **In-house:** premium licences needed for every app user | Low | Medium | Licence check in phase 0, pay-as-you-go for occasional users, Power BI for read-only audiences |
| **In-house:** errors in self-built calculation logic | High | Medium | Test cases against legacy Excel, peer review, version-locked scaling rules |
| **In-house:** no maintenance budget after go-live | Medium | Medium | Agree a run budget of about 0.25 FTE at gate G0 |
| **External:** functional mismatch with part-level should-costing tools | High | High | Scripted demo on own data before contract |
| **External:** second tool and custom integration still needed | Medium | High | Include that scope in the vendor comparison |
| **External:** high recurring cash-out for a small user group | Medium | High | Negotiate user tiers, check group frame agreements |
| **External:** vendor lock-in for logic and data | Medium | Medium | Contractual data export, API access, exit clause |
| **External:** months of selection and procurement before any value | Medium | High | Run the RFI in parallel to the in-house MVP |

---

## 11. Recommendation and next steps

**Recommendation**

1. Decide for the in-house path with option B as target and a lean start.
2. Keep the decision reversible through gates G0 and G1.
3. Send an RFI to Siemens or a Siemens partner for Teamcenter PCM, to one of FACTON or Tset, and to Cleopatra, so that quoted prices and durations replace the planning assumptions.
4. Treat reference data as a separate make-or-buy question. Buying a data package is compatible with building the tool.

**When the recommendation should be reversed**

- The main expected value shifts to supplier should-cost negotiation on manufactured parts.
- No developer capacity can be secured, internally or through a partner.
- The RFI shows that Teamcenter PCM licences already exist in the group or can be had at the low end of the range.
- IT security rules out Dataverse for cost data.

**Next steps, mapped to the task description**

| Step in task description | Action | Output |
|---|---|---|
| 1.1 External best practice incl. cost and time | Send RFI, book two scripted demos | Quoted licence and implementation cost, duration |
| 1.2 Internal development possibility | Clarify the open questions below; half-day design workshop with IT and the LCOH Suite owner | Confirmed architecture and licence position |
| 1.3 Alignment and decision with Dimi and SD Product gH2 | Decision meeting with this material and the RFI answers | Gate G0 decision |
| 2 Requirements catalogue with Product gH2 and R&D | Review the 13 requirements, confirm priorities, add missing ones, map today's tools | Requirements catalogue v1 |
| 3 Implementation | Start phase 1 | MVP |

---

## 12. Open questions

**Internal**

1. Where are prices and supplier data maintained today: Teamcenter attributes, ERP, Excel?
2. Which Teamcenter release is installed, is Active Workspace in use, and is the 2606 Power BI integration available?
3. Where does the LCOH Suite store its data (Dataverse, SharePoint, SQL), and who maintains it?
4. Which Microsoft licences exist (Microsoft 365 E3 or E5, Power Apps Premium, Fabric capacity)?
5. Do group-level frame agreements exist with a shortlisted vendor?
6. How many users will edit, contribute ideas, or only read?
7. Which cost breakdown structure is the reference?
8. Is developer capacity available internally, or is a Power Platform partner needed?
9. May cost data be stored in Dataverse or in a vendor cloud?

**For vendors** — see workbook sheet *RFI and open questions*.

---

## 13. Public cost references for benchmarking and calibration

These figures help to seed the benchmark table (R9) and to sanity-check scaling and regional logic (R7, R8). They also show why scope split and region matter so much for this product.

| Metric | Value | Source |
|---|---|---|
| Installed electrolyser cost outside China, 2024 | USD 2,000-2,600 per kW | IEA figures as reported by secondary sources [S82]; verify in the IEA Global Hydrogen Review |
| Chinese electrolyser built and installed in China, 2024 | USD 600-1,200 per kW | As above [S82] |
| System cost, China-made vs. Europe/US-made | about USD 600 vs. about USD 2,500 per kW | BNEF as reported by FuelCellChina [S80] |
| Alkaline full system outside China, 2025 | slightly above USD 2.0M per MW; China 50-60% lower | CRU [S75] |
| Installed cost of standard European / North American plants | USD 2,300 per kW alkaline, USD 2,550 per kW PEM | Electric Hydrogen white paper [S76] |
| Stack share of direct CAPEX | 20-50% in large PEM and alkaline projects | World Bank [S74] |
| 1 GW plant, 2020 baseline design | EUR 1,400 per kW alkaline, EUR 1,800 per kW PEM | ISPT [S77] |
| 1 GW advanced design | EUR 730 per kW | ISPT [S78]; technology and year basis to be checked |
| PEM balance-of-plant scaling | USD 848 per kW at 1 MW to USD 87 per kW at 1 GW | OSTI [S79] |

CRU notes that Chinese tender prices typically cover the stack only and exclude balance of plant and installation [S75]. A benchmark table therefore needs a scope field for every data point, which the proposed data model has.

---

## 14. Method and limits

- **Method.** Desk research on 13 November 2026 through web search in English and German, covering vendor sites, partner blogs, review platforms, analyst and press sources, Microsoft documentation and public hydrogen cost studies.
- **Vendor pages could not be opened directly** from the research environment because of its network restrictions. Facts were taken from search-result extracts of those pages. Key figures should be confirmed in the vendor conversations.
- **Prices.** No PCM vendor publishes prices. External cost ranges are planning assumptions.
- **Microsoft list prices** come from third-party licensing guides that cite Microsoft's pricing pages; the tenant's own price sheet will differ.
- **Fit and weighted scores** are a preliminary assessment by one person from public information.
- **Not covered.** Hands-on product tests, reference calls, legal and data-protection assessment, the company's internal IT standards.

---

## 15. Sources

| ID | Source | Type |
|---|---|---|
| S1 | [Siemens blog - What's new in Teamcenter Product Cost Management 2606](https://blogs.sw.siemens.com/teamcenter/teamcenter-product-cost-management-whats-new-in-version-2606/) | Vendor |
| S2 | [Kaizen PLM - What's new in Teamcenter Product Cost Management 2606](https://www.kaizenplm.ie/post/what-s-new-in-version-2606-teamcenter-product-cost-management) | Partner |
| S3 | [Siemens blog - Teamcenter Product Cost Management 2506](https://blogs.sw.siemens.com/teamcenter/teamcenter-product-cost-management-whats-new-in-version-2506/) | Vendor |
| S4 | [Siemens blog - Teamcenter Product Cost Management 2512](https://blogs.sw.siemens.com/teamcenter/whats-new-in-teamcenter-product-cost-management-version-2512/) | Vendor |
| S5 | [Siemens blog - Teamcenter Product Cost Management what's new series](https://blogs.sw.siemens.com/teamcenter/teamcenter-product-cost-management-whats-new/) | Vendor |
| S6 | [Siemens fact sheet - Teamcenter product costing](https://www.plm.automation.siemens.com/en_us/Images/Siemens-PLM-Teamcenter-Product-Costing-fs_tcm1023-204012.pdf) | Vendor |
| S7 | [Siemens fact sheet - Teamcenter X Product Cost Management](https://resources.sw.siemens.com/en-US/fact-sheet-reduce-costs-and-carbon-footprint-with-teamcenter-x-product-cost-management/) | Vendor |
| S8 | [Siemens blog - Introducing Teamcenter 2606](https://blogs.sw.siemens.com/teamcenter/teamcenter-2606/) | Vendor |
| S9 | [Siemens blog - Power BI integration for actionable analytics in Teamcenter](https://blogs.sw.siemens.com/teamcenter/power-bi-integration-teamcenter/) | Vendor |
| S10 | [Emixa - Teamcenter 2606 release guide](https://www.emixa.com/blog/teamcenter-2606-release-guide) | Partner |
| S11 | [Siemens blog - 2026 Teamcenter beta testing event](https://blogs.sw.siemens.com/teamcenter/plm-teamcenter-beta-event/) | Vendor |
| S12 | [PROLIM - Identifying and specifying target costs with Teamcenter PCM](https://www.prolim.com/identifying-and-specifying-target-costs-with-teamcenter/) | Partner |
| S13 | [G2 - Teamcenter pricing](https://www.g2.com/products/teamcenter/pricing); [AWS Marketplace - Teamcenter X](https://aws.amazon.com/marketplace/pp/prodview-gizsnllbv3mqo) | Third party |
| S14 | [Leo AI blog - The Teamcenter API](https://www.getleo.ai/blog/teamcenter-api-what-you-can-get) | Third party |
| S15 | [Siemens community - getting started with the REST API](https://community.sw.siemens.com/s/question/0D5Vb00000auM4fKAE/are-there-any-guides-for-getting-started-with-the-rest-api) | Community |
| S16 | [Mendix docs - Teamcenter Extension](https://docs.mendix.com/appstore/modules/siemens-plm/teamcenter-extension) | Vendor |
| S17 | [aPriori - Pricing and packaging](https://www.apriori.com/pricing/) | Vendor |
| S18 | [aPriori - FAQs](https://www.apriori.com/faqs/) | Vendor |
| S19 | [G2 - aPriori pricing and implementation statistics](https://www.g2.com/products/apriori-manufacturing-intelligence-platform/pricing) | Third party |
| S20 | [Software Finder - aPriori pricing estimates](https://softwarefinder.com/manufacturing-software/apriori) | Third party |
| S21 | [Emithran - Should-cost analysis software compared (2026)](https://www.emithran.com/blog/should-cost-analysis-software-comparison) | Third party |
| S22 | [Forrester - Total Economic Impact of aPriori (2022)](https://www.apriori.com/wp-content/uploads/2022/11/Forrester-Total-Economic-Impact-of-aPriori-Nov-8-2022-FINAL.pdf) | Analyst, commissioned |
| S23 | [aPriori - Product modules overview, cloud (2022)](https://www.apriori.com/wp-content/uploads/2022/08/aPriori-Product-Modules-Overview-Cloud-Solution-DS-062922-V14.pdf) | Vendor |
| S24 | [FACTON - Cost management software](https://www.facton.com/software) | Vendor |
| S25 | [FACTON - Services](https://www.facton.com/services) | Vendor |
| S26 | [FitGap - FACTON EPC Suite](https://us.fitgap.com/products/036767/facton-epc-suite) | Third party |
| S27 | [SoftGuide - FACTON EPC](https://www.softguide.com/program/facton) | Third party |
| S28 | [PRWeb - FACTON EPC Should Costing SaaS in the cloud (2016)](https://www.prweb.com/releases/facton_introduces_epc_should_costing_saas_solution_in_the_cloud/prweb13570922.htm) | Vendor |
| S29 | [Microsoft Marketplace - FACTON EPC Should Costing](https://marketplace.microsoft.com/en-us/product/factongmbh1583248282207.facton_epc_sc?tab=overview) | Marketplace |
| S30 | [Capterra - FACTON EPC](https://www.capterra.com/p/161502/Facton-EPC-Suite/) | Third party |
| S31 | [Tset - Cost and carbon product page](https://tset.com/product/cost-carbon) | Vendor |
| S32 | [Tset - About](https://tset.com/about) | Vendor |
| S33 | [Tset - Series A announcement](https://tset.com/press-and-news/series-a-funding-tset) | Vendor |
| S34 | [Vestbee - Tset raises EUR 12.7M](https://www.vestbee.com/insights/articles/tset-raises-12-7-m) | Press |
| S35 | [Tset - Customer story Brose](https://tset.com/customer-stories/brose) | Vendor |
| S36 | [Tset - API-first architecture with BMW Group](https://tset.com/blog/bmw-group-cost-engineering-api-first-approach) | Vendor |
| S37 | [Tset - FAQ](https://tset.com/faq) | Vendor |
| S38 | [Tset - Automotive](https://tset.com/industries/automotive) | Vendor |
| S39 | [Cleopatra Enterprise - Cost estimating software](https://cleopatraenterprise.com/cost-estimating-software-2/) | Vendor |
| S40 | [Cleopatra Enterprise - Cost estimating brochure (2025)](https://cleopatraenterprise.com/wp-content/uploads/2025/04/Cost-estimating-software-brochure.pdf) | Vendor |
| S41 | [Cleopatra Enterprise - Cost management software](https://cleopatraenterprise.com/cost-management-software/) | Vendor |
| S42 | [Cleopatra Enterprise - Power industry](https://cleopatraenterprise.com/industries/cleopatra-enterprise-for-power/) | Vendor |
| S43 | [SaaSrat - Cleopatra Enterprise review 2026](https://saasrat.com/products/cleopatra-enterprise) | Third party |
| S44 | [Cleopatra Enterprise - Metrics and benchmarking](https://cleopatraenterprise.com/blog/managing-project-costs-with-metrics-and-benchmarking/) | Vendor |
| S45 | [Valuedesk - Prices and packages](https://www.valuedesk.de/en/software/preise/) | Vendor |
| S46 | [Valuedesk - Cost cutting](https://www.valuedesk.de/en/loesungen/cost-cutting/) | Vendor |
| S47 | [Westfalen-Blatt - Der Kosten-Optimierer](https://www.westfalen-blatt.de/owl/bielefeld/der-kosten-optimierer-1153769) | Press |
| S48 | [IHC OWL - Hinter den Kulissen von Valuedesk](https://www.ihc-owl.de/hinter-den-kulissen-von-valuedesk-gmbh/) | Press |
| S49 | [trusted.de - Falcon review and prices](https://trusted.de/falcon) | Third party |
| S50 | [Capterra - Falcon reviews](https://www.capterra.com/p/210024/Falcon/reviews/) | Third party |
| S51 | [costdata - Market data](https://www.costdata.de/en/data) | Vendor |
| S52 | [AspenTech - Economic evaluation family brochure](https://www.aspentech.com/-/media/aspentech/home/resources/brochure/pdfs/fy23/q3/at-08059-new-economic-evaluation-family-brochure_0123.pdf) | Vendor |
| S53 | [Capterra UK - CostOS Estimating](https://www.capterra.co.uk/software/52188/costos-estimating) | Third party |
| S54 | [SAP Community - Deep dive into SAP Product Lifecycle Costing](https://community.sap.com/t5/product-lifecycle-management-blog-posts-by-sap/secure-profits-with-early-design-cost-control-a-deep-dive-into-sap-product/ba-p/14451316) | Vendor |
| S55 | [TrustRadius - Product cost management category](https://www.trustradius.com/categories/product-cost-management) | Third party |
| S56 | [ERP Research - Implementation cost breakdown](https://www.erpresearch.com/en-us/erp-implementation-cost-breakdown) | Third party |
| S57 | [Microsoft Learn - Pipelines in Power Platform](https://learn.microsoft.com/power-platform/alm/pipelines) | Microsoft |
| S58 | [Microsoft Learn - Translytical task flows](https://learn.microsoft.com/en-us/power-bi/create-reports/translytical-task-flow-overview) | Microsoft |
| S59 | [Microsoft Learn - Configure Dataverse auditing](https://learn.microsoft.com/power-apps/developer/data-platform/auditing/configure) | Microsoft |
| S60 | [Microsoft Learn - Dataverse long-term data retention](https://learn.microsoft.com/power-apps/developer/data-platform/long-term-retention) | Microsoft |
| S61 | [Microsoft Learn - Link Dataverse to Microsoft Fabric](https://learn.microsoft.com/en-us/training/modules/link-dataverse-fabric/synchronize-data) | Microsoft |
| S62 | [Superblocks - Power Apps pricing 2026](https://www.superblocks.com/blog/powerapps-pricing) | Third party |
| S63 | [SAMexpert - Power Apps per-app plan retired](https://samexpert.com/power-apps-per-app-plan-retired/) | Third party |
| S64 | [Redress Compliance - Power Platform licensing 2026](https://redresscompliance.com/microsoft-power-platform-licensing-complete) | Third party |
| S65 | [EPC Group - Power BI pricing and licensing 2026](https://www.epcgroup.net/insights/power-bi-pricing-licensing-2026) | Third party |
| S66 | [Embeddable - Power BI pricing 2026](https://embeddable.com/blog/power-bi-pricing) | Third party |
| S67 | [Forrester - Total Economic Impact of Microsoft Power Apps](https://tei.forrester.com/go/microsoft/powerappstei/?lang=en-us) | Analyst, commissioned |
| S68 | [Microsoft Power Platform blog - September 2026 feature update](https://microsoft.com/en-us/power-platform/blog/power-apps/whats-new-in-power-platform-september-2026-feature-update) | Microsoft |
| S69 | [Microsoft Learn - Create a custom connector from scratch](https://learn.microsoft.com/en-us/connectors/custom-connectors/define-blank) | Microsoft |
| S70 | [m365.fm - Why SharePoint is not a database for Power Apps](https://www.m365.fm/blog/why-sharepoint-is-not-a-database-for-power-apps--and-what-to-use-instead/) | Community |
| S71 | [Panko - Spreadsheet errors (arXiv 0804.0941)](https://arxiv.org/pdf/0804.0941.pdf) | Academic |
| S72 | [Microsoft - Copilot Studio](https://www.microsoft.com/copilot/microsoft-copilot-studio) | Microsoft |
| S73 | [Atlan - Translytical task flows](https://atlan.com/know/microsoft-fabric/translytical-task-flows/) | Third party |
| S74 | [World Bank - Technical report on electrolyser characteristics](https://documents1.worldbank.org/curated/en/099022326123011297/pdf/P506220-b45b0865-8706-4862-8792-d8cc71f84569.pdf) | Public study |
| S75 | [CRU - Chinese green hydrogen has cost benefits but challenges are emerging](https://www.crugroup.com/en/communities/thought-leadership/2025/chinese-green-hydrogen-has-cost-benefits-but-challenges-are-emerging/) | Analyst |
| S76 | [Electric Hydrogen - PEM vs. alkaline white paper (Dec 2024)](https://eh2.com/wp-content/uploads/2025/01/Final_PEM_vs_Alkaline_December_2024_Whitepaper.pdf) | Vendor study |
| S77 | [ISPT - Gigawatt green hydrogen plant (2020)](https://ispt.eu/media/ISPT-public-report-gigawatt-green-hydrogen-plant.pdf) | Public study |
| S78 | [ISPT - One-gigawatt advanced design (2022)](https://ispt.eu/media/Public-report-gigawatt-advanced-green-electrolyser-design.pdf) | Public study |
| S79 | [OSTI - Balance-of-plant scale-up cost estimation for PEM systems](https://www.osti.gov/pages/biblio/3376750-cost-estimation-balance-plant-equipment-scale-up-proton-exchange-membrane-water-electrolyzer-systems) | Academic |
| S80 | [FuelCellChina - BNEF: cost of electrolysers is rising instead of falling](https://www.fuelcellchina.com/Industry_information_details/3725.html) | Press |
| S81 | [Intratec - Plant location factors](https://methodology.intratec.us/industry-economics/location-factors/) | Data provider |
| S82 | [Secondary reporting of IEA Global Hydrogen Review cost figures](https://www.hyzenergy.com/blog/chinese-electrolyzer-cost-vs-western) | Secondary |
