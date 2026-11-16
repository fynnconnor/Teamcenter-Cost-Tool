# Power Automate flows

Five cloud flows carry the server-side logic. Build them inside the solution **Cost Cockpit** (*New > Automation > Cloud flow*), so that they travel with the app from Dev to Test to Prod.

| # | Flow | Trigger | Serves |
|---|---|---|---|
| 01 | Cost item - set amount | Cost item added or changed | R1 |
| 02 | Cost version - release | *Release requested* set to Yes | R6 |
| 03 | Scenario - calculate | *Calculation requested* set to Yes | R3, R7, R8 |
| 04 | Scenario - publish CAPEX dataset | *Publication requested* set to Yes | R13 |
| 05 | Idea - notify and review | Idea added | R11, R12 |

The Teamcenter import (R5) runs as dataflows, see `../teamcenter/`.

## Conventions used in the step descriptions

- **Connector:** Microsoft Dataverse (the green one, *When a row is added, modified or deleted*, *List rows*, *Add a new row* ...). It is a premium connector.
- **Expressions** are written as you type them into the expression editor, without the leading `@`. Where a value is embedded in text (filters, Fetch XML), it is written as `@{...}`.
- **Action names matter**, because expressions refer to them. Rename each action to the name printed in bold before you write expressions that use it. Spaces become underscores inside expressions: the action **Get product** is `outputs('Get_product')`.
- **Lookup fields** in *Add a new row* / *Update a row* expect the form `entitysetname(GUID)`, for example `cdt_products(@{...})`. Entity set names are the plural logical names: `cdt_products`, `cdt_cbselements`, `cdt_costversions`, `cdt_costitems`, `cdt_suppliers`, `cdt_scenarios`, `cdt_scenariolines`, `cdt_features`, `cdt_regions`. If *Add a new row* shows a different hint under the field, use that.
- **Lookup values in outputs** are named `_<column>_value`, for example `_cdt_product_value`.
- **Choice values** are numbers, see `../docs/03-data-dictionary.md`. Example: Version status Draft = 710000001, Released = 710000002.
- **Sum of an array** (Power Automate has no sum function): put the numbers into a *Select* action in text mode, then use
  `if(empty(body('Select_x')), 0, xpath(xml(json(concat('{"r":{"v":', string(body('Select_x')), '}}'))), 'sum(/r/v)'))`.
- **Loops:** switch on *Concurrency control* (degree 20) for every *Apply to each* that only creates or deletes rows. Do not use variables inside concurrent loops.
- **List rows** returns 5,000 rows at most by default. Where more are possible, switch on *Pagination* in the action settings and set the threshold to 100000.

## Test after building

Load the demo data, then check each flow against the golden results in `../engine/golden/`:

| Flow | Test | Expected |
|---|---|---|
| 01 | Change the quantity of *Cell stack* in DEMO-V002 from 5 to 6 | Amount (EUR) becomes 22,800,000 |
| 02 | Release DEMO-V002 | DEMO-V002 is Released, DEMO-V003 exists as Draft with 14 cost items and the same total |
| 03 | Calculate SCN-100-DE, SCN-200-ES, SCN-20-IN | Totals 91,380,000 / 152,180,369 / 20,535,270 EUR; lines equal `scenario_lines.csv` |
| 04 | Publish SCN-200-ES | CAPEX dataset rows equal the SCN-200-ES rows of `capex_dataset.csv` |
| 05 | Submit an idea | Teams message arrives |

None of the flows could be run from the development environment of this repository. Treat the first run of each as a test and compare with the expected values.
