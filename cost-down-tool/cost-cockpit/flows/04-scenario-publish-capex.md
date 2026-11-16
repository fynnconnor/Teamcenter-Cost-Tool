# Flow 04: Scenario - publish CAPEX dataset

Aggregates the lines of a calculated scenario per scope and TIC category and writes them to the table **CAPEX Dataset**. This table is the interface to the LCOH Suite (requirement R13): the LCOH Suite reads it, the Cost Cockpit owns it.

## Trigger

**When a row is added, modified or deleted** (Dataverse): Change type Modified, table Scenarios, scope Organization, Select columns `cdt_publishrequested`, Filter rows `cdt_publishrequested eq true and (cdt_status eq 710000002 or cdt_status eq 710000003)`.

## Actions

1. **Get product**, **Get version**, **Get region**: three *Get a row by ID* actions with `_cdt_product_value`, `_cdt_costversion_value`, `_cdt_region_value` of the trigger.

2. **List old datasets**: *List rows*, CAPEX Datasets, Filter rows `_cdt_scenario_value eq @{triggerOutputs()?['body/cdt_scenarioid']}`; then **Delete old datasets**: *Apply to each* > *Delete a row*.

3. **List lines**: *List rows*, Scenario Lines, Filter rows `_cdt_scenario_value eq @{triggerOutputs()?['body/cdt_scenarioid']}`, Select columns `cdt_scope,cdt_ticcategory,cdt_finalcosteur`, pagination on.

4. **Scopes**: *Compose*, `createArray(710000001, 710000002, 710000003)`. **Categories**: *Compose*, `createArray(710000001, 710000002, 710000003, 710000004, 710000005, 710000006, 710000007, 710000008)`.

5. **Per scope**: *Apply to each* over `outputs('Scopes')`. Inside **Per category**: *Apply to each* over `outputs('Categories')`. Inside:

   a. **Cell lines**: *Filter array*, From `outputs('List_lines')?['body/value']`, advanced mode: `@and(equals(item()?['cdt_scope'], items('Per_scope')), equals(item()?['cdt_ticcategory'], items('Per_category')))`.

   b. **Condition**: `length(body('Cell_lines'))` is greater than `0`. If yes:

      - **Select cell**: *Select*, From `body('Cell_lines')`, Map in text mode `item()?['cdt_finalcosteur']`.
      - **Cell sum**: *Compose*, `xpath(xml(json(concat('{"r":{"v":', string(body('Select_cell')), '}}'))), 'sum(/r/v)')`.
      - **Add dataset row**: *Add a new row*, CAPEX Datasets

| Field | Value |
|---|---|
| Name | `concat(triggerOutputs()?['body/cdt_code'], ' ', items('Per_scope'), ' ', items('Per_category'))` |
| Dataset key | `concat(triggerOutputs()?['body/cdt_code'], '~', sub(items('Per_scope'), 710000000), '~', sub(items('Per_category'), 710000000))` |
| Scenario (Scenarios) | `cdt_scenarios(@{triggerOutputs()?['body/cdt_scenarioid']})` |
| Product code | `outputs('Get_product')?['body/cdt_code']` |
| Version code | `outputs('Get_version')?['body/cdt_code']` |
| Region code | `outputs('Get_region')?['body/cdt_code']` |
| Project size (MW) | `triggerOutputs()?['body/cdt_sizemw']` |
| Scope | `items('Per_scope')` (custom value) |
| TIC category | `items('Per_category')` (custom value) |
| Cost (EUR) | `outputs('Cell_sum')` |
| Cost (EUR/kW) | `div(outputs('Cell_sum'), mul(triggerOutputs()?['body/cdt_sizemw'], 1000))` |
| Published on | `utcNow()` |

6. **Finish**: *Update a row*, Scenarios: Status = Published, Publication requested = No.

## Hand-over to the LCOH Suite

Which step follows depends on where the LCOH Suite keeps its data. Clarify this with its owner (open question 3 of the research).

| LCOH Suite stores data in | Hand-over |
|---|---|
| Dataverse, same environment | Nothing to build. Add the table CAPEX Datasets as data source in the LCOH Suite app and filter by scenario or dataset key |
| Dataverse, other environment | Add step 7: *Add a new row* with the connection of the target environment (*Add a new row to selected environment*) |
| SharePoint list | Add step 7 inside the inner loop: *Create item* in the LCOH list with the same fields |
| SQL / other | Add step 7 with the matching connector, or let the LCOH Suite read the CAPEX Dataset table through the Dataverse connector |

Agree a fixed column contract with the LCOH Suite owner: dataset key, product code, version code, region code, size, scope, TIC category, cost in EUR and EUR/kW, published on.
