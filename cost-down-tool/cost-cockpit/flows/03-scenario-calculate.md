# Flow 03: Scenario - calculate

Writes the scenario lines for one scenario: one line per CBS element and cost type of the chosen cost version, plus one line per feature impact. The flow only copies inputs onto the lines. The arithmetic happens in the formula columns *Scale factor*, *Final cost (EUR)* and *Cost per kW (EUR/kW)* of the Scenario Line table, because Power Automate has no power function.

Logic reference: `../engine/cost_engine.py`, function `scenario_lines`. Covers R7 (project size), R8 (region) and R3 (feature effects).

## Prerequisite

The formula columns on Scenario (`cdt_SizeRatio`, `cdt_ModuleRatio`) and Scenario Line (`cdt_ScaleFactor`, `cdt_FinalCostEUR`, `cdt_CostPerKW`) exist with exactly these schema names.

## Trigger

**When a row is added, modified or deleted** (Dataverse): Change type Modified, table Scenarios, scope Organization, Select columns `cdt_calcrequested`, Filter rows `cdt_calcrequested eq true`.

## Actions

1. **Get product**: *Get a row by ID*, Products, `triggerOutputs()?['body/_cdt_product_value']`.

2. **Set sizes**: *Update a row*, Scenarios, Row ID `triggerOutputs()?['body/cdt_scenarioid']`: Reference size (MW) = `outputs('Get_product')?['body/cdt_referencesizemw']`, Module size (MW) = `outputs('Get_product')?['body/cdt_modulesizemw']`.

3. **Get scenario**: *Get a row by ID*, Scenarios, same Row ID. This read returns the formula columns `cdt_sizeratio` and `cdt_moduleratio`.

4. **List old lines**: *List rows*, Scenario Lines, Filter rows `_cdt_scenario_value eq @{triggerOutputs()?['body/cdt_scenarioid']}`, Select columns `cdt_scenariolineid`, pagination on.

5. **Delete old lines**: *Apply to each* over the old lines, concurrency 20: *Delete a row*, Scenario Lines, `items('Delete_old_lines')?['cdt_scenariolineid']`.

6. **List CBS**: *List rows*, CBS Elements, Filter rows `_cdt_product_value eq @{triggerOutputs()?['body/_cdt_product_value']}`, pagination on.

7. **List factors**: *List rows*, Regional Factors, Filter rows `_cdt_region_value eq @{triggerOutputs()?['body/_cdt_region_value']}`.

8. **List base**: *List rows*, Cost Items, with this **Fetch Xml Query** (leave the other fields empty):

```xml
<fetch aggregate="true">
  <entity name="cdt_costitem">
    <attribute name="cdt_amounteur" alias="amount" aggregate="sum" />
    <attribute name="cdt_cbselement" alias="cbs" groupby="true" />
    <attribute name="cdt_costtype" alias="costtype" groupby="true" />
    <filter>
      <condition attribute="cdt_costversion" operator="eq" value="@{triggerOutputs()?['body/_cdt_costversion_value']}" />
    </filter>
  </entity>
</fetch>
```

   Each result row has `amount` (number), `cbs` (GUID of the CBS element) and `costtype` (choice number).

9. **Base lines**: *Apply to each* over `outputs('List_base')?['body/value']`, concurrency 20. Inside:

   a. **Find CBS**: *Filter array*, From `outputs('List_CBS')?['body/value']`, condition `item()?['cdt_cbselementid']` is equal to `items('Base_lines')?['cbs']`.

   b. **Find factor**: *Filter array*, From `outputs('List_factors')?['body/value']`, condition `item()?['cdt_costtype']` is equal to `items('Base_lines')?['costtype']`.

   c. **Add base line**: *Add a new row*, Scenario Lines

| Field | Value |
|---|---|
| Name | `concat(outputs('Get_scenario')?['body/cdt_code'], ' ', first(body('Find_CBS'))?['cdt_code'])` |
| Scenario (Scenarios) | `cdt_scenarios(@{triggerOutputs()?['body/cdt_scenarioid']})` |
| CBS element (CBS Elements) | `cdt_cbselements(@{items('Base_lines')?['cbs']})` |
| Line type | Base cost |
| Cost type | `items('Base_lines')?['costtype']` (custom value) |
| Scope | `first(body('Find_CBS'))?['cdt_scope']` (custom value) |
| TIC category | `first(body('Find_CBS'))?['cdt_ticcategory']` (custom value) |
| Base amount (EUR) | `items('Base_lines')?['amount']` |
| Scaling code | `sub(first(body('Find_CBS'))?['cdt_scalingmethod'], 710000000)` |
| Scaling exponent | `coalesce(first(body('Find_CBS'))?['cdt_scalingexponent'], 0)` |
| Size ratio | `outputs('Get_scenario')?['body/cdt_sizeratio']` |
| Module ratio | `outputs('Get_scenario')?['body/cdt_moduleratio']` |
| Regional factor | `coalesce(first(body('Find_factor'))?['cdt_factor'], 1)` |
| Escalation factor | `coalesce(outputs('Get_scenario')?['body/cdt_escalationfactor'], 1)` |
| Project size (MW) | `outputs('Get_scenario')?['body/cdt_sizemw']` |

   The scaling code is the choice value minus 710000000: Per module = 1, Power law = 2, Fixed = 3.

10. **List scenario features**: *List rows*, Scenario Features, Filter rows `_cdt_scenario_value eq @{triggerOutputs()?['body/cdt_scenarioid']}`.

11. **Features**: *Apply to each* over the scenario features (no concurrency). Inside:

    a. **List impacts**: *List rows*, Feature Impacts, Filter rows `_cdt_feature_value eq @{items('Features')?['_cdt_feature_value']}`.

    b. **Impacts**: *Apply to each* over the impacts. Inside:

       - **Impact CBS**: *Filter array*, From `outputs('List_CBS')?['body/value']`, `item()?['cdt_cbselementid']` is equal to `items('Impacts')?['_cdt_cbselement_value']`.
       - **Element groups**: *Filter array*, From `outputs('List_base')?['body/value']`, `item()?['cbs']` is equal to `items('Impacts')?['_cdt_cbselement_value']`.
       - **Select amounts**: *Select*, From `body('Element_groups')`, Map in text mode: `item()?['amount']`.
       - **Element base**: *Compose*, `if(empty(body('Select_amounts')), 0, xpath(xml(json(concat('{"r":{"v":', string(body('Select_amounts')), '}}'))), 'sum(/r/v)'))`.
       - **Impact factor**: *Filter array*, From `outputs('List_factors')?['body/value']`, `item()?['cdt_costtype']` is equal to `items('Impacts')?['cdt_costtype']`.
       - **Add feature line**: *Add a new row*, Scenario Lines, like 9c with these differences:

| Field | Value |
|---|---|
| Name | `concat(outputs('Get_scenario')?['body/cdt_code'], ' ', items('Impacts')?['cdt_code'])` |
| CBS element | `cdt_cbselements(@{items('Impacts')?['_cdt_cbselement_value']})` |
| Feature (Features) | `cdt_features(@{items('Features')?['_cdt_feature_value']})` |
| Line type | Feature effect |
| Cost type | `items('Impacts')?['cdt_costtype']` |
| Scope, TIC category | from `first(body('Impact_CBS'))` |
| Base amount (EUR) | `if(equals(items('Impacts')?['cdt_impacttype'], 710000001), items('Impacts')?['cdt_value'], if(equals(items('Impacts')?['cdt_impacttype'], 710000002), mul(items('Impacts')?['cdt_value'], outputs('Get_scenario')?['body/cdt_referencesizemw']), div(mul(items('Impacts')?['cdt_value'], outputs('Element_base')), 100)))` |
| Scaling code | `if(equals(items('Impacts')?['cdt_impacttype'], 710000001), 3, if(equals(items('Impacts')?['cdt_impacttype'], 710000002), 2, sub(first(body('Impact_CBS'))?['cdt_scalingmethod'], 710000000)))` |
| Scaling exponent | `if(equals(items('Impacts')?['cdt_impacttype'], 710000002), 1, coalesce(first(body('Impact_CBS'))?['cdt_scalingexponent'], 0))` |
| Regional factor | `coalesce(first(body('Impact_factor'))?['cdt_factor'], 1)` |

       Impact types: 710000001 fixed amount, 710000002 amount per MW, 710000003 percent of element.

12. **List new lines**: *List rows*, Scenario Lines, Filter rows `_cdt_scenario_value eq @{triggerOutputs()?['body/cdt_scenarioid']}`, Select columns `cdt_finalcosteur`, pagination on.

13. **Select totals**: *Select*, From the new lines, Map in text mode: `item()?['cdt_finalcosteur']`.

14. **Total**: *Compose*, `if(empty(body('Select_totals')), 0, xpath(xml(json(concat('{"r":{"v":', string(body('Select_totals')), '}}'))), 'sum(/r/v)'))`.

15. **Finish**: *Update a row*, Scenarios: Total cost (EUR) = `outputs('Total')`, Total cost (EUR/kW) = `div(outputs('Total'), mul(outputs('Get_scenario')?['body/cdt_sizemw'], 1000))`, Status = Calculated, Calculated on = `utcNow()`, Calculation requested = No.

## Notes

- Step 8 relies on the stored Amount (EUR) of the cost items (flow 01 and the import keep it current).
- If a CBS element has cost items but no scaling method, step 9c fails for that line. The view *Leaf elements* in the app shows which elements still need a rule.
- Calculating a scenario on a draft version is allowed; the lines then reflect the draft at that moment.
