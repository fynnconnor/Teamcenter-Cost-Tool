# Flow 01: Cost item - set amount

Keeps the stored column **Amount (EUR)** equal to quantity × unit price × FX rate, whoever changes a cost item (form, editable grid, import, flow). The amount is stored, not calculated on the fly, so that views, aggregate queries and Power BI can sum it.

## Trigger

**When a row is added, modified or deleted** (Dataverse)

| Setting | Value |
|---|---|
| Change type | Added or Modified |
| Table name | Cost Items |
| Scope | Organization |
| Select columns | `cdt_quantity,cdt_unitprice,cdt_fxrate` |

Trigger condition (trigger *Settings > Trigger conditions*), so that the flow only runs when the stored amount is wrong by more than half a cent:

```
@or(greater(sub(coalesce(triggerOutputs()?['body/cdt_amounteur'], -1), mul(mul(coalesce(triggerOutputs()?['body/cdt_quantity'], 0), coalesce(triggerOutputs()?['body/cdt_unitprice'], 0)), coalesce(triggerOutputs()?['body/cdt_fxrate'], 1))), 0.005), less(sub(coalesce(triggerOutputs()?['body/cdt_amounteur'], -1), mul(mul(coalesce(triggerOutputs()?['body/cdt_quantity'], 0), coalesce(triggerOutputs()?['body/cdt_unitprice'], 0)), coalesce(triggerOutputs()?['body/cdt_fxrate'], 1))), -0.005))
```

## Actions

1. **Update amount**: *Update a row*

| Field | Value |
|---|---|
| Table name | Cost Items |
| Row ID | `triggerOutputs()?['body/cdt_costitemid']` |
| Amount (EUR) | `mul(mul(coalesce(triggerOutputs()?['body/cdt_quantity'], 0), coalesce(triggerOutputs()?['body/cdt_unitprice'], 0)), coalesce(triggerOutputs()?['body/cdt_fxrate'], 1))` |

The update changes only Amount (EUR), which is not in *Select columns*, so the flow does not trigger itself.

## Notes

- Dataverse rounds the stored value to two decimals.
- During a large import the flow runs once per row whose amount is not yet right. The dataflow in `../teamcenter/` writes the amount itself, so normally nothing runs.
