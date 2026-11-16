# Flow 02: Cost version - release

Freezes the draft version and opens the next one as a copy. After the run there is a released version that no longer changes and a new draft that carries all cost items forward. This is the versioning of requirement R6.

## Trigger

**When a row is added, modified or deleted** (Dataverse)

| Setting | Value |
|---|---|
| Change type | Modified |
| Table name | Cost Versions |
| Scope | Organization |
| Select columns | `cdt_releaserequested` |
| Filter rows | `cdt_releaserequested eq true and cdt_status eq 710000001` |

## Actions

1. **Get product**: *Get a row by ID*, table Products, Row ID `triggerOutputs()?['body/_cdt_product_value']`.

2. **New number**: *Compose*, input `add(triggerOutputs()?['body/cdt_versionnumber'], 1)`.

3. **New code**: *Compose*, input `concat(outputs('Get_product')?['body/cdt_code'], '-V', formatNumber(outputs('New_number'), '000'))`.

4. **Add new version**: *Add a new row*, table Cost Versions

| Field | Value |
|---|---|
| Name | `concat(outputs('Get_product')?['body/cdt_name'], ' V', formatNumber(outputs('New_number'), '000'))` |
| Code | `outputs('New_code')` |
| Version number | `outputs('New_number')` |
| Status | Draft |
| Product (Products) | `cdt_products(@{triggerOutputs()?['body/_cdt_product_value']})` |
| Based on version (Cost Versions) | `cdt_costversions(@{triggerOutputs()?['body/cdt_costversionid']})` |
| Price year | `triggerOutputs()?['body/cdt_priceyear']` |
| Release requested | No |

5. **List cost items**: *List rows*, table Cost Items, Filter rows `_cdt_costversion_value eq @{triggerOutputs()?['body/cdt_costversionid']}`. Settings: Pagination on, threshold 100000.

6. **Copy items**: *Apply to each* over `outputs('List_cost_items')?['body/value']`, concurrency 20. Inside: **Add cost item**, *Add a new row*, table Cost Items

| Field | Value |
|---|---|
| Description | `items('Copy_items')?['cdt_name']` |
| Import key | `replace(items('Copy_items')?['cdt_importkey'], triggerOutputs()?['body/cdt_code'], outputs('New_code'))` |
| Cost version (Cost Versions) | `cdt_costversions(@{outputs('Add_new_version')?['body/cdt_costversionid']})` |
| CBS element (CBS Elements) | `cdt_cbselements(@{items('Copy_items')?['_cdt_cbselement_value']})` |
| Supplier (Suppliers) | `if(empty(items('Copy_items')?['_cdt_supplier_value']), null, concat('cdt_suppliers(', items('Copy_items')?['_cdt_supplier_value'], ')'))` |
| Cost type | `items('Copy_items')?['cdt_costtype']` (switch the field to *Enter custom value*) |
| Teamcenter item ID | `items('Copy_items')?['cdt_teamcenteritemid']` |
| Teamcenter revision | `items('Copy_items')?['cdt_teamcenterrevision']` |
| Quantity | `items('Copy_items')?['cdt_quantity']` |
| Unit | `items('Copy_items')?['cdt_unit']` |
| Unit price | `items('Copy_items')?['cdt_unitprice']` |
| Currency code | `items('Copy_items')?['cdt_currencycode']` |
| FX rate to EUR | `items('Copy_items')?['cdt_fxrate']` |
| Amount (EUR) | `items('Copy_items')?['cdt_amounteur']` |
| Price source, Confidence, Make or buy | `items('Copy_items')?['cdt_pricesource']`, `...['cdt_confidence']`, `...['cdt_makebuy']` (custom values) |
| Price date | `items('Copy_items')?['cdt_pricedate']` |
| Comment | `items('Copy_items')?['cdt_comment']` |

7. **Mark released**: *Update a row*, table Cost Versions, Row ID `triggerOutputs()?['body/cdt_costversionid']`: Status = Released, Released on = `utcNow()`, Release requested = No.

8. Optional **Notify**: *Post message in a chat or channel* (Teams) with `concat('Cost version ', triggerOutputs()?['body/cdt_code'], ' released. New draft: ', outputs('New_code'))`.

## Notes

- Put steps 4 to 7 into a *Scope* and add a second scope that runs *after failure* and sets Release requested = No with a message, so that a failed run can be repeated.
- Released versions are protected by the business rule and the security set-up in `../app/model-driven-app.md`.
- 2,000 cost items take a few minutes. The user gets the Teams message when it is done.
