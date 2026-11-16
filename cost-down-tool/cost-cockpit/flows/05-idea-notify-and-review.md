# Flow 05: Idea - notify and review

Tells the product owner about each new idea and reminds measure owners of overdue measures. Two small flows; both are optional comfort functions for R11 and R12.

## 05a New idea

Trigger: **When a row is added, modified or deleted**: Change type Added, table Ideas, scope Organization.

1. **Post card**: *Post message in a chat or channel* (Microsoft Teams), Post as Flow bot, Post in Channel (the cost-down channel). Message:

```
New cost-down idea: @{triggerOutputs()?['body/cdt_name']}
Submitted by: @{triggerOutputs()?['body/cdt_submittername']}
Estimated saving: @{coalesce(triggerOutputs()?['body/cdt_estimatedsavingeur'], 'not stated')} EUR
```

2. Optional **Ask for decision**: *Start and wait for an approval* (type Approve/Reject - First to respond), assigned to the product owner, title `concat('Evaluate idea: ', triggerOutputs()?['body/cdt_name'])`. Then *Update a row* on the idea: Status = Accepted (710000003) or Rejected (710000004), Evaluation note = approver comment.

## 05b Overdue measures (weekly)

Trigger: **Recurrence**, every week on Monday 08:00.

1. **List overdue**: *List rows*, Measures, Filter rows `cdt_status eq 710000001 and cdt_duedate lt @{formatDateTime(utcNow(), 'yyyy-MM-dd')}`, Expand query `owninguser($select=internalemailaddress,fullname)`.
2. **Condition**: `length(outputs('List_overdue')?['body/value'])` greater than 0.
3. **Per measure**: *Apply to each*: *Send an email (V2)* to `items('Per_measure')?['owninguser']?['internalemailaddress']` with code, title, due date and degree of implementation.
