// Cost Cockpit - Power Fx formulas for command bar buttons (modern commanding)
// ---------------------------------------------------------------------------------------------
// Paste each block into the command designer of the model-driven app (see model-driven-app.md, chapter 6).
// Names in single quotes are the DISPLAY names of tables and columns from the data dictionary.
// If you renamed something, adjust the formula; the designer underlines unknown names in red.
// Not tested in a tenant: check each button once with the demo data.
//
// Yes/No columns: the formulas write true. If the designer rejects true for a column, use the option
// instead, for example 'Release requested (Cost Versions)'.Yes


// ============================================================================================
// 1. Cost Version > main form > "Release version"
// ============================================================================================
// Action (Run formula):
If(
    Confirm(
        "Release " & Self.Selected.Item.Code & "? The version is frozen and a new draft version is created.",
        {Title: "Release version", ConfirmButton: "Release", CancelButton: "Cancel"}
    ),
    Patch('Cost Versions', Self.Selected.Item, {'Release requested': true});
    Notify("Release started. The new draft version appears in a few minutes.", NotificationType.Success)
)

// Visibility (Show on condition from formula):
Self.Selected.Item.Status = 'Version status'.Draft


// ============================================================================================
// 2. Scenario > main form and main grid > "Calculate"
// ============================================================================================
// Action:
Patch(Scenarios, Self.Selected.Item, {'Calculation requested': true});
Notify("Calculation started. Refresh the form in about a minute.", NotificationType.Information)

// Visibility:
CountRows(Self.Selected.AllItems) = 1


// ============================================================================================
// 3. Scenario > main form > "Publish to LCOH Suite"
// ============================================================================================
// Action:
If(
    Confirm(
        "Publish scenario " & Self.Selected.Item.Code & " as CAPEX dataset for the LCOH Suite?",
        {Title: "Publish", ConfirmButton: "Publish", CancelButton: "Cancel"}
    ),
    Patch(Scenarios, Self.Selected.Item, {'Publication requested': true});
    Notify("Publication started.", NotificationType.Success)
)

// Visibility: only calculated or already published scenarios
Self.Selected.Item.Status = 'Scenario status'.Calculated || Self.Selected.Item.Status = 'Scenario status'.Published


// ============================================================================================
// 4. Idea > main form and main grid > "Convert to measure"
// ============================================================================================
// Action:
With(
    {idea: Self.Selected.Item},
    Patch(
        Measures,
        Defaults(Measures),
        {
            Title: idea.Title,
            Code: "M-" & Text(Now(), "yyyymmdd-hhmmss"),
            Idea: idea,
            Product: idea.Product,
            'CBS element': idea.'CBS element',
            'Saving (EUR)': Coalesce(idea.'Estimated saving (EUR)', 0),
            'Probability (%)': 50,
            'Degree of implementation': 'Degree of implementation'.'DI1 Idea',
            Status: 'Measure status'.Open
        }
    );
    Patch(Ideas, idea, {Status: 'Idea status'.'Converted to measure'})
);
Notify("Measure created. Open it to set owner, effort and due date.", NotificationType.Success)

// Visibility: one idea selected, it has a CBS element (required on the measure) and is not converted yet
CountRows(Self.Selected.AllItems) = 1 &&
!IsBlank(Self.Selected.Item.'CBS element') &&
Self.Selected.Item.Status <> 'Idea status'.'Converted to measure' &&
Self.Selected.Item.Status <> 'Idea status'.Rejected
