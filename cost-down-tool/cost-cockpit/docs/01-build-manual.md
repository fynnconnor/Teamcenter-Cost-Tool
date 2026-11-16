# Build manual: Cost Cockpit

How to build the cost-down tool as a Power App on Dataverse with a Teamcenter interface
Version 0.1 · 16 November 2026

This manual takes you from an empty environment to a working app that meets the 13 requirements. It is written so that you can start today: chapters 2 to 6 need nothing but a Dataverse environment and give you a running app with demo data. The later chapters add the flows, the Teamcenter import, the report and the LCOH Suite link.

**What is tested and what is not.** The data model script, the demo data loaders and the calculation engine were tested in this repository (22 automated tests, against a simulated Dataverse endpoint). Flows, Power Fx formulas, DAX measures, Power Query code and the Teamcenter connector could not be run from here, because they need your tenant. They are written against the current Microsoft documentation and come with expected results on the demo data. Treat the first run of each as a test.

---

## 1. What you are building

```
 Teamcenter ──export file / services──▶ staging ──dataflow──▶┐
 Excel baseline ──import──────────────────────────────────────┤
                                                              ▼
                        ┌───────────── Dataverse (solution "Cost Cockpit") ─────────────┐
                        │ Product · CBS Element · Cost Version · Cost Item · Supplier    │
                        │ Feature · Feature Impact · Region · Regional Factor            │
                        │ Scenario · Scenario Line · CAPEX Dataset                       │
                        │ Benchmark · Target · Idea · Measure                            │
                        └───────────────────────────────────────────────────────────────┘
                           ▲               ▲                 ▲                  │
              model-driven app      idea box page     Power Automate      Power BI report
              "Cost Cockpit"        (canvas)          flows 01-05         (embedded)
                                                                               │
                                                     CAPEX Dataset ──▶ LCOH Suite (existing Power App)
```

| Component | Purpose | Files |
|---|---|---|
| Data model | 20 tables, 18 choices | `schema/`, `docs/03-data-dictionary.md` |
| Provisioning | Creates the data model | `scripts/provision_dataverse.py`, `scripts/provision_browser_console.js` |
| Demo data | Synthetic product to learn and test with | `seed/`, `scripts/load_seed_data.py`, `scripts/load_seed_browser_console.js` |
| Reference engine | Defines the calculation and the expected results | `engine/` |
| Model-driven app | Maintain all data | `app/model-driven-app.md`, `app/command-bar.fx` |
| Idea box | Submit ideas | `app/idea-box.md`, `app/idea-box.pa.yaml` |
| Flows | Amounts, release, scenario calculation, publication, notifications | `flows/` |
| Teamcenter import | Prices and suppliers from Teamcenter | `teamcenter/` |
| Report | Analysis | `powerbi/` |

How each requirement is met is listed in `docs/02-requirements-specification.md`.

**Design decisions you should know**

- **One app next to the LCOH Suite, not inside it.** Both share Dataverse; the table *CAPEX Dataset* is the contract between them.
- **Stored amounts.** *Amount (EUR)* is a stored number on every cost item, so that views, flows and Power BI can sum it.
- **Versions are copies.** Releasing a version freezes its cost items and copies them into the next draft.
- **Scenario arithmetic lives in Dataverse formula columns.** Power Automate has no power function; the flow writes inputs, the formula columns calculate.
- **Every import ends in a staging table.** File export today, service connector later; the mapping logic is built once.
- **Choice values are numbers** starting at 710000001. Flows and queries use the numbers, people see the labels.

---

## 2. Before you start

### 2.1 What you need

| Need | Detail | Who |
|---|---|---|
| A Dataverse environment for development | Type Developer or Sandbox, **with Dataverse**, base language **English**, currency EUR | You, if developer environments are allowed; otherwise IT |
| Role *System Customizer* or *System Administrator* in it | Needed to create tables | Automatic in your own developer environment |
| Power Apps Premium licence (or Developer Plan for building) | Dataverse, custom connectors, premium flows | IT licensing |
| Power BI Desktop and a Power BI Pro licence | Report | IT |
| A SharePoint folder | Drop folder for Teamcenter export files | You |
| Optional: Python 3.9 or later | Only for the script route of provisioning and for the reference engine | You |
| Later: on-premises data gateway, Teamcenter service account | Only for the service connector in phase 4 | IT / PLM IT |

If the environment's base language is not English, change `"language_code": 1033` in `schema/cost_cockpit.schema.json` to the language code of the environment (German: 1031) and run `python scripts/build_artifacts.py` before provisioning.

### 2.2 Send these requests today

They have lead time, and none of them blocks chapters 3 to 6.

> **To IT (Power Platform):** For an internal cost monitoring app next to the LCOH Suite I need (1) a Dataverse development environment, later a test and a production environment, (2) Power Apps Premium for about 10 editors and a licence option for about 30 occasional users, (3) confirmation that Dataverse may hold cost and supplier price data, (4) Power BI Pro for the same users, (5) whether an on-premises data gateway exists.
>
> **To PLM IT (Teamcenter):** For the same app I need to import prices, quantities and suppliers of a product structure. (1) In which Teamcenter attributes are prices and supplier assignments kept, or are they in the ERP system? (2) Which Teamcenter release is installed, and is Active Workspace in use? (3) Can a saved query or report export a CSV with item ID, revision, name, parent, quantity, unit, unit price, currency, supplier ID, supplier name and price date? (4) Is `/tc/JsonRestServices` reachable and may a service account be used later?
>
> **To the LCOH Suite owner:** Where does the LCOH Suite store its data (Dataverse, SharePoint, SQL)? I plan to provide CAPEX per scenario, scope and TIC category in a Dataverse table that the LCOH Suite can read.

### 2.3 Plan for day 1

| Time | Step | Result |
|---|---|---|
| 30 min | Chapter 3: environment | Empty environment with Dataverse |
| 30 min | Chapter 4: data model | 20 tables in the solution Cost Cockpit |
| 30 min | Chapter 4.4: formula columns | Seven formula columns |
| 15 min | Chapter 5: demo data | 132 rows |
| 2 h | Chapter 6: model-driven app | App with navigation, views, forms |
| 1 h | Chapter 9, pages 1-3 only | First report on the demo baseline |

At the end of the day you can show the demo product with 91.38 million EUR split by scope, cost type and element, and you know the tool chain.

---

## 3. Environment and solution

1. Open **admin.powerplatform.microsoft.com > Environments > New**. Name `Cost Cockpit Dev`, type *Developer* (or *Sandbox*), *Add a Dataverse data store: Yes*, language English, currency EUR. If the button is not available to you, ask IT (request above).
2. Open **make.powerapps.com**, select the new environment at the top right.
3. Note the environment URL: gear icon > *Session details* > *Instance url*, for example `https://org12345.crm4.dynamics.com`.
4. You do not create the solution by hand; the provisioning creates the publisher `costdowntool` (prefix `cdt`) and the solution **Cost Cockpit**.

Always work inside the solution *Cost Cockpit* (Solutions > Cost Cockpit). Apps, flows, dataflows and roles that you create there can later be transported to test and production.

---

## 4. Data model

Pick **one** of the three routes. All give the same result and all can be repeated safely.

### 4.1 Route A: browser console (no installation)

1. Open the environment URL in Edge or Chrome and wait until a page of the environment has loaded (any model-driven app, or the URL followed by `/main.aspx`).
2. Press **F12** and select the **Console** tab. If the browser asks you to confirm pasting, type `allow pasting` and press Enter.
3. Open `scripts/provision_browser_console.js` in a text editor, copy everything, paste it into the console and press Enter.
4. Watch the log. It prints `created` for each object and ends with a summary, for example `Summary: 237 created, 0 already existed, 0 missing, 0 failed`. The run takes several minutes.
5. If some objects failed, read the message, fix the cause and paste the script again. Existing objects are skipped.

The script calls the Web API of the environment you are signed in to, with your permissions, and nothing else.

### 4.2 Route B: Python script

```bash
cd cost-down-tool/cost-cockpit/scripts
python provision_dataverse.py --dry-run
```

The dry run writes all 237 requests to `out/payloads` so that you can read what will be created. Then run it for real. Get a token with the Azure CLI:

```bash
az login
python provision_dataverse.py --url https://<org>.crm4.dynamics.com --use-az
```

Without the Azure CLI, get a token in PowerShell with `(Get-AzAccessToken -ResourceUrl https://<org>.crm4.dynamics.com).Token`, put it in the environment variable `DATAVERSE_TOKEN` and run the script without `--use-az`. `--check` reports what exists and what is missing without changing anything.

### 4.3 Route C: by hand

Use `docs/03-data-dictionary.md` as the specification. In the solution: create the 18 global choices first (*New > More > Choice*, with exactly the listed values), then each table with its primary column, then the columns, then the lookups, then the alternate keys. Budget four to five hours. Take the names literally: flows, queries and formulas refer to the logical names.

### 4.4 Formula columns (all routes)

Seven formula columns are created by hand. In the solution open the table > *Columns > New column*.

1. *Display name* as in the table below.
2. *Data type*: **fx Formula**. Paste the formula.
3. *Advanced options*: set **Schema name** to the value in the table (type only the part after `cdt_`), set *Formula data type* and the number of decimal places.
4. Save.

| Table | Display name | Schema name | Type, decimals | Formula |
|---|---|---|---|---|
| Scenario | Size ratio | `cdt_SizeRatio` | Decimal, 6 | `If('Reference size (MW)' > 0, 'Project size (MW)' / 'Reference size (MW)', 0)` |
| Scenario | Module ratio | `cdt_ModuleRatio` | Decimal, 6 | `If('Module size (MW)' > 0 && 'Reference size (MW)' > 0, RoundUp('Project size (MW)' / 'Module size (MW)', 0) / RoundUp('Reference size (MW)' / 'Module size (MW)', 0), 0)` |
| Scenario Line | Scale factor | `cdt_ScaleFactor` | Float, 6 | `If('Scaling code' = 1, Float('Module ratio'), If('Scaling code' = 2, Power(Float('Size ratio'), Float('Scaling exponent')), Float(1)))` |
| Scenario Line | Final cost (EUR) | `cdt_FinalCostEUR` | Float, 2 | `Float('Base amount (EUR)') * 'Scale factor' * Float('Regional factor') * Float('Escalation factor')` |
| Scenario Line | Cost per kW (EUR/kW) | `cdt_CostPerKW` | Float, 2 | `If('Project size (MW)' > 0, 'Final cost (EUR)' / (Float('Project size (MW)') * 1000), Float(0))` |
| Measure | Weighted saving (EUR) | `cdt_WeightedSavingEUR` | Decimal, 2 | `'Saving (EUR)' * 'Probability (%)' / 100` |
| Measure | Priority score | `cdt_PriorityScore` | Decimal, 2 | see data dictionary, table Measure |

Create *Scale factor* before *Final cost (EUR)* and that before *Cost per kW (EUR/kW)*, because they build on each other. If the editor rejects a formula, check that the column names in quotes match the display names exactly.

### 4.5 Check

- Solutions > Cost Cockpit > Tables shows 20 tables.
- Table *Cost Item* > Keys shows *Cost item import key* with status **Active**. Keys are built in the background; wait until all 18 are active before loading data.
- Re-run the provisioning with check mode (`--check`, or `CHECK_ONLY = true` in the console script): nothing is missing.

---

## 5. Demo data

The demo product is synthetic: 100 MW reference plant, 20 MW modules, 14 cost items, total 91,380,000 EUR. It exists so that every later step has a known expected result.

**Browser route:** paste `scripts/load_seed_browser_console.js` into the console as in 4.1. Expected last line: `Seed data: 132 rows written, 0 failed`.

**Python route:** `python load_seed_data.py --url https://<org>.crm4.dynamics.com --use-az`.

If rows fail with a message about a key, the alternate keys are not active yet; wait a few minutes and run the loader again. It upserts, so nothing is duplicated.

Check in *make.powerapps.com > Tables > Cost Item > Data*: 28 rows, 14 per version.

Optional, with Python: `python engine/cost_engine.py` prints the expected totals; `python -m unittest` in `engine/` and `python -m unittest discover -s tests` in `scripts/` run the tests.

---

## 6. Model-driven app

Specification: `app/model-driven-app.md`. Order of work:

1. **Create the app.** Solution > *New > App > Model-driven app*, name `Cost Cockpit`.
2. **Navigation.** *Add page > Dataverse table*, select all Cost Cockpit tables. Arrange them into the areas and groups of chapter 1 of the specification (pencil icon next to *Navigation*).
3. **Views.** For each table open the view *Active ...* and add the columns from chapter 2 of the specification. Start with Cost Items, CBS Elements, Cost Versions and Scenarios; the others can keep their default for now.
4. **Forms.** For each table open the main form, add the columns in the order of the data dictionary and the sub-grids from chapter 3 of the specification. The form designer's *Table columns* pane lets you drag them in.
5. **Editable grids.** For Cost Items, Regional Factors, Targets and Teamcenter Import Rows: table > *Views/Forms settings* or in the app designer select the table's view > *Components > Add the Power Apps grid control* and set *Enable editing* to Yes.
6. **Hierarchy.** Table CBS Element > *Properties/Settings* > relationship *Parent element* > mark as **Hierarchical**. The form then offers the tree view.
7. **Business rules** from chapter 4 of the specification: table > *Business rules > New*. Set the scope to *Entity*.
8. **Save and publish**, then *Play*.

Check with the demo data: open Cost Versions > *Demo baseline V001* > sub-grid shows 14 cost items; the sum of *Amount (EUR)* in the grid footer is 91,380,000.

Do the **security roles** (chapter 5 of the specification) and the **command bar buttons** (chapter 6, formulas in `app/command-bar.fx`) after the flows exist; until then set the Yes/No request fields on the form by hand.

Tip: Copilot in the app designer can generate forms and pages from a description. It is a good accelerator for the many simple forms; keep the names of tables and columns unchanged.

---

## 7. Flows

Specifications: `flows/README.md` and one file per flow. Build them in the solution, in this order, and test each with the demo data before starting the next.

| Order | Flow | Why in this order | Test (expected) |
|---|---|---|---|
| 1 | 01 Cost item - set amount | Smallest flow; teaches the Dataverse trigger and expressions | Set quantity of *Cell stack* in DEMO-V002 to 6: Amount becomes 22,800,000. Set it back to 5 |
| 2 | 02 Cost version - release | Needed before real versions exist | Release DEMO-V002: new draft DEMO-V003 with 14 items |
| 3 | 03 Scenario - calculate | Core of the scenario requirements | SCN-100-DE = 91,380,000; SCN-200-ES = 152,180,369; SCN-20-IN = 20,535,270 EUR |
| 4 | 04 Scenario - publish CAPEX dataset | Needs calculated scenarios | Rows of SCN-200-ES sum to 152,180,369 EUR |
| 5 | 05 Idea - notify and review | Independent, optional | Teams message on a new idea |

Working method for each flow:

1. *New > Automation > Cloud flow > Automated*, choose the Dataverse trigger.
2. Add the actions in the order of the specification. **Rename each action** to the bold name before adding the next one.
3. Type expressions into the *Expression* tab (fx), not into the text field. Use *Enter custom value* for choice and lookup fields that receive an expression.
4. Save, run the test, open the run history and compare with the expected values. For flow 03 compare the scenario lines with `engine/golden/scenario_lines.csv` (columns base amount, scale factor, regional factor, final cost).
5. When it works, add error handling: put the actions in a *Scope* and add a parallel branch *configure run after: has failed* that resets the request flag and posts a message.

After flow 02 to 04 work, add the **command bar buttons** from `app/command-bar.fx`.

Typical pitfalls:

- *The flow does not start.* The filter in the trigger must use the logical column name and the number of the choice; the flow must be turned on; the connection must be valid.
- *"Resource not found for the segment"* in a lookup field. The entity set name is wrong. Open the table in make.powerapps.com > *Tools > Copy set name*.
- *Scale factor is empty.* The formula columns of chapter 4.4 are missing or have a different schema name than the flow expects.
- *The total is slightly off.* Compare line by line with the golden file; the usual cause is a missing regional factor (treated as 1) or a CBS element without scaling method.

---

## 8. Teamcenter import

Read `teamcenter/README.md` first. Start with the file route; it needs no IT project.

1. Create the SharePoint folder `CostCockpit/TeamcenterExport` and upload `teamcenter/export-template.csv` as a first test file.
2. **Dataflow A.** make.powerapps.com > *Dataflows > New dataflow > Start from blank*, name `CC Teamcenter export to staging`. *Blank query*, open the advanced editor, paste `dataflow_A_export_to_staging.pq`, set the parameters at the top (site URL, folder, version code `DEMO-V002`). Sign in to SharePoint when asked. *Next* > map to the existing table *Teamcenter Import Rows*, key *Import row key*, auto-map the columns. Refresh manually.
3. **Dataflow B.** New dataflow `CC staging to cost items` with four queries from `dataflow_B_staging_to_costitems.pq` (Staged, SuppliersOut, CostItemsOut, StagingStatusOut). Set the host name and the import run (`export-template`). Disable load for *Staged*. Map the three outputs as described in the file header: choose the alternate key for each table and map the three code columns to the lookups through their keys.
4. Refresh A, then B. Expected: six cost items of DEMO-V002 updated, DEMO-V002 total unchanged at 90,380,000 EUR, staging row for item 100099 in the view *Not mapped*.
5. Add item 100099 to *Teamcenter Mappings* (any CBS element, cost type Material), refresh B: the row is loaded and the version total rises by 250,000 EUR. Delete that cost item afterwards if you want the demo totals back.

Going live with real data: agree the export with PLM IT, replace the test file, set the version code of your draft version, and schedule both dataflows (A, then B thirty minutes later) or start them from a flow.

The service route with the custom connector (`teamcenter-connector.swagger.json`) replaces dataflow A in phase 4. Dataflow B, the mapping table and everything downstream stay as they are.

---

## 9. Power BI report

Specification: `powerbi/model.md`.

1. **Power BI Desktop > Transform data.** Create the parameter `EnvironmentHost` (host name without `https://`). Create the function `fnPick` and then one query per block from `powerbi/queries.pq`; name each query as printed above its block. Sign in with your organisational account. *Close & apply*.
2. **Model view.** Create the relationships from the table in `model.md` (drag the key from the "one" table to the "many" table). Delete relationships that Power BI created on its own and that are not in the list. Leave *Compare Version*, *Size MW* and *Benchmark* unrelated.
3. **Calculated columns.** On table CBS Element add the six columns listed at the end of `powerbi/measures.dax`, in the given order.
4. **Measures.** Open the DAX query view, paste the `DEFINE` block including the `EVALUATE` from `measures.dax`, and choose *Update model with changes*. If your version has no such button, add the measures one by one (*New measure*).
5. **Pages.** Build the eleven pages from `model.md`. For day 1, pages 1 to 3 are enough.
6. **Check** the numbers of the table *Check against the demo data* in `model.md`.
7. **Publish** to a workspace, set up the scheduled refresh (data source credentials: OAuth2, your account or a service account), and embed the report in the app as described in `app/model-driven-app.md`, chapter 7.

If a query fails with a message about the TDS endpoint, ask the environment admin to enable it: Power Platform admin center > environment > *Settings > Product > Features > TDS endpoint*.

---

## 10. Idea box

Follow `app/idea-box.md`: create the custom page, add the three data sources, paste `idea-box.pa.yaml` or build the 13 controls from the table, publish, add the page to the app. Then build flow 05a for the Teams notification.

Decide with IT how occasional submitters are licensed before you announce the idea box widely.

---

## 11. LCOH Suite link

1. Calculate and publish a scenario (flows 03 and 04). The table *CAPEX Datasets* now holds one row per scope and TIC category.
2. Agree the column contract with the LCOH Suite owner (list in `flows/04-scenario-publish-capex.md`).
3. Connect according to where the LCOH Suite stores its data (table in the same file): same Dataverse environment means adding *CAPEX Datasets* as a data source in the LCOH Suite; otherwise add the hand-over step to flow 04.
4. Test with SCN-200-ES: the LCOH Suite shows 152,180,369 EUR split as in `engine/golden/capex_dataset.csv`.

---

## 12. From demo data to real data

Do this together with Product gH2 and R&D; it is the content side of the requirements catalogue.

1. **Product.** Create the real product with reference size and module size. Write the basis of "kW" (for example rated AC input) into the description, the same basis the LCOH Suite uses.
2. **Cost breakdown structure.** Agree levels and codes. Enter elements top-down; set scope, TIC category and scaling method on every leaf. The view *Leaf elements* helps to find gaps.
3. **Baseline.** Create version V001 as draft. Bring the existing Excel cost data into the format of `seed/06_cdt_costitem.csv` (one row per item, import key = version code ~ CBS code ~ item ID or line number) and load it with *Import data from Excel* in the app, with *Edit in Excel*, or with the seed loader pointed at your own folder (`--seed <folder>`). Add Teamcenter items through the import of chapter 8.
4. **Reconcile.** The version total must equal the total of the Excel source. Then release V001.
5. **Scaling rules.** Start with estimates: per module for modular product scope, power law with an exponent around 0.6 to 0.8 for shared plant scope, fixed for one-time engineering. Calibrate against known projects of different size: calculate a scenario at that size and adjust the exponents until the element costs match.
6. **Regional factors.** Start with the base region at 1.0 and add regions as projects come up. Record the source of every factor.
7. **Targets, benchmarks, features, measures.** Enter them as they are agreed. Seed the benchmark table with the public references listed in the research workbook.
8. **Remove the demo data** when it is no longer needed: delete the product *Demo electrolysis plant* after deleting its versions, scenarios, features and CBS elements.

---

## 13. Test and acceptance

Use the acceptance criteria in `docs/02-requirements-specification.md`: 13 requirements, two to four checks each, all with expected values on the demo data. Record result and date per check. Repeat the checks after every change to flows, formula columns or measures; they take about an hour.

Before real users start, also test: an editor cannot change a released version; a reader cannot edit anything; a contributor can create an idea and nothing else; the audit history of a cost item shows a price change.

---

## 14. Transport, go-live and operation

1. **Environments.** Dev (build), Test (acceptance with real data), Prod (use). Ask IT to create Test and Prod when chapter 13 passes in Dev.
2. **Transport.** In Dev: Solutions > Cost Cockpit > *Export > Managed*. In Test and Prod: *Import solution*. With Managed Environments, use Power Platform pipelines instead. Connection references and environment variables are asked for at import.
3. **Not in the solution:** table data (products, CBS, factors), the dataflows' credentials and the Power BI report. Move reference data with the seed loader or a dataflow; re-point the report to the new environment through the parameter `EnvironmentHost`.
4. **Go-live checklist.** Security roles assigned; auditing on; flows on and owned by a service account or at least two people; dataflow and report refresh scheduled; released baseline loaded; quick guide for users; named product owner and deputy developer.
5. **Operation.** Monthly: check flow run history and refresh history. Quarterly: release a version, review factors and exponents, plan small enhancements. Keep changes in Dev and transport them; never edit Prod directly.

---

## 15. Timeline

| Phase | Weeks | Chapters | Result |
|---|---|---|---|
| 0 Mobilise and decide | 1-4 | 2, requirements specification | Environment, licences, requirements catalogue, agreed CBS |
| 1 MVP: cost transparency | 5-12 | 3-6, 7 (flows 01-02), 8 (file route), 9 (pages 1-5), 12 | Real baseline, versions, cost-driver report |
| 2 Scenario simulation | 13-18 | 7 (flow 03), 9 (pages 6-8), 12 (rules, factors) | Scenarios by size, region, features |
| 3 Targets and cost-down | 19-24 | 10, 7 (flow 05), 9 (pages 9-11) | Targets, benchmarks, idea box, measures |
| 4 Integrate and industrialise | 25-30 | 8 (service route), 11, 13, 14 | Automated import, LCOH link, production |

The technical build of chapters 3 to 9 on demo data can be done in the first one to two weeks. The calendar time goes into data, agreement on structures, and access.

---

## 16. Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Provisioning: HTTP 401 or "Not connected" | Token expired or wrong environment. Sign in again; in the browser route make sure the page of the environment is loaded |
| Provisioning: HTTP 403 | Your role lacks customisation rights. Ask for System Customizer |
| Provisioning: error about language or label | The environment's base language is not English. Change `language_code` in the schema file and rebuild (chapter 2.1) |
| Provisioning: a key failed | Keys are optional for the app but needed for imports. Create the key by hand: table > Keys > New, columns as in the data dictionary |
| Seed loader: "key not found" or 404 on rows | Alternate keys still being built. Wait and re-run |
| A choice column shows numbers in a flow | That is how flows see choices. Use the numbers from the data dictionary |
| Formula column cannot be saved | A referenced column name differs from the display name, or a formula column it depends on does not exist yet |
| Command button is not visible | The visibility formula returns false for the selected row, or the command is not published. Publish the app |
| Power Fx: name not recognised in a button formula | Add the table as data source in the command component library |
| Dataflow B loads nothing | The import run parameter does not match the staging rows, or no item is mapped. Check the query *Staged* in the editor: the column *Problem* says why |
| Power BI: numbers are doubled | A relationship is missing or bidirectional. Compare with the list in `model.md` |
| What-if cost does not change with the region | No single region is selected, or the region has no factors (then every factor is 1) |

---

## 17. Files in this folder

| Path | Content |
|---|---|
| `README.md` | Overview and quick start |
| `docs/01-build-manual.md` | This manual |
| `docs/02-requirements-specification.md` | Requirements, acceptance checks, further requirements, add-ins |
| `docs/03-data-dictionary.md` | Generated description of all tables, columns, keys, formulas, choices |
| `schema/cost_cockpit.schema.json` | Source of truth for the data model |
| `scripts/` | Provisioning and seed loaders (Python and browser console), generator, tests |
| `seed/` | Synthetic demo data |
| `engine/` | Reference calculation, tests, golden results |
| `app/` | Model-driven app specification, command formulas, idea box |
| `flows/` | Five flow specifications |
| `teamcenter/` | Export template, dataflow queries, connector definition |
| `powerbi/` | Queries, measures, model and page specification |

When the data model changes: edit `schema/cost_cockpit.schema.json`, run `python scripts/build_artifacts.py`, re-run the provisioning (it adds what is new), and update flows, queries and measures that use the changed columns.
