# Idea box (canvas page)

A single screen where any colleague submits a cost-down idea in under a minute and sees the status of their own ideas. It covers requirement R11. Build it as a **custom page** inside the model-driven app, or as a stand-alone canvas app pinned in Teams; the screen is the same.

Every user of this page needs a licence that covers Dataverse (Power Apps Premium or pay-as-you-go). If that is a hurdle for occasional users, start with the quick create form of the Idea table (see `model-driven-app.md`) and add this page later.

## Build it in 20 minutes

1. In the solution: *New > App > Page* (custom page) or *Canvas app*, tablet format, name `Idea Box`.
2. *Data > Add data*: **Ideas**, **Products**, **CBS Elements**.
3. Try the fast way first: right-click the screen in the tree view > *Paste code* and paste the content of `idea-box.pa.yaml` (only the part below `Children:` if you paste into an existing screen). Power Apps validates the code; if it rejects a control, build the controls by hand from the table below. The formulas are the same.
4. Save, publish, and add the page to the app navigation (model-driven app designer > *Add page > Custom page*).

The YAML could not be validated in Power Apps Studio from here. The control table is the reliable reference.

## Controls and formulas

| Control (type) | Name | Property | Formula |
|---|---|---|---|
| Label | `lblHeader` | Text | `"Submit a cost-down idea"` |
| Text input | `txtTitle` | HintText | `"Short title (required)"` |
| Text input | `txtDescription` | Mode | `TextMode.MultiLine` |
| | | HintText | `"What should change, and why does it save cost?"` |
| Combo box | `cmbProduct` | Items | `Products` |
| | | DisplayFields / SearchFields | `["cdt_name"]` |
| | | SelectMultiple | `false` |
| Combo box | `cmbCBS` | Items | `Filter('CBS Elements', Product.Product = cmbProduct.Selected.Product)` |
| | | DisplayFields / SearchFields | `["cdt_name"]` |
| | | SelectMultiple | `false` |
| Text input | `txtSaving` | Format | `TextFormat.Number` |
| | | HintText | `"Estimated saving per plant in EUR (optional)"` |
| Drop down | `drpEffort` | Items | `Choices('Idea effort')` |
| Drop down | `drpCategory` | Items | `Choices('Idea category')` |
| Button | `btnSubmit` | Text | `"Submit idea"` |
| | | OnSelect | see below |
| Gallery (vertical) | `galMyIdeas` | Items | `SortByColumns(Filter(Ideas, Submitter = User().FullName), "createdon", SortOrder.Descending)` |
| Label in gallery | `lblIdeaTitle` | Text | `ThisItem.Title` |
| Label in gallery | `lblIdeaStatus` | Text | `Text(ThisItem.Status)` |

`btnSubmit.OnSelect`:

```powerfx
If(
    IsBlank(Trim(txtTitle.Text)),
    Notify("Please enter a title.", NotificationType.Error),
    Patch(
        Ideas,
        Defaults(Ideas),
        {
            Title: Trim(txtTitle.Text),
            Description: txtDescription.Text,
            Product: cmbProduct.Selected,
            'CBS element': cmbCBS.Selected,
            'Estimated saving (EUR)': If(IsBlank(txtSaving.Text), Blank(), Value(txtSaving.Text)),
            Effort: drpEffort.Selected.Value,
            Category: drpCategory.Selected.Value,
            Status: 'Idea status'.New,
            Submitter: User().FullName
        }
    );
    Reset(txtTitle); Reset(txtDescription); Reset(txtSaving); Reset(cmbProduct); Reset(cmbCBS);
    Notify("Thank you. Your idea was saved.", NotificationType.Success)
)
```

## Optional extras

- **Teams notification to the product owner** on every new idea: flow `05 Idea - notify and review` in `flows/`.
- **Attachment** (photo, sketch): enable attachments on the Idea table and add an *Attachments* control to the page.
- **Anonymous counter** on the page: `CountRows(Filter(Ideas, Status <> 'Idea status'.Rejected))` as a label "ideas submitted so far".
