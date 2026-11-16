// Cost Cockpit - Power BI queries (Power Query M)
// ----------------------------------------------------------------------------------------------
// Power BI Desktop: Transform data > New source > Blank query > Advanced editor.
// 1. Create the parameter EnvironmentHost (Manage parameters, type Text), e.g. yourorg.crm4.dynamics.com
// 2. Create the query fnPick from the first block.
// 3. Create one query per table from the blocks below; the query name is printed above each block.
// The Dataverse connector (TDS endpoint) must be enabled in the environment (default: on).
// Choice columns come twice: "<column>" is the number, "<column>name" is the label.


// ============================== fnPick ==========================================================
// Selects and renames columns of one Dataverse table. map = list of {logical name, friendly name}.
(item as text, map as list) as table =>
let
    Source   = CommonDataService.Database(EnvironmentHost),
    Data     = Source{[Schema = "dbo", Item = item]}[Data],
    Selected = Table.SelectColumns(Data, List.Transform(map, each _{0})),
    Renamed  = Table.RenameColumns(Selected, map)
in
    Renamed


// ============================== Product =========================================================
fnPick("cdt_product", {{"cdt_productid", "Product Id"}, {"cdt_code", "Product Code"}, {"cdt_name", "Product"},
    {"cdt_referencesizemw", "Reference Size MW"}, {"cdt_modulesizemw", "Module Size MW"}})

// ============================== CBS Element =====================================================
fnPick("cdt_cbselement", {{"cdt_cbselementid", "CBS Element Id"}, {"cdt_code", "CBS Code"}, {"cdt_name", "CBS Element"},
    {"cdt_product", "Product Id"}, {"cdt_parent", "Parent Id"}, {"cdt_level", "Level"},
    {"cdt_scope", "Scope Value"}, {"cdt_scopename", "Scope"}, {"cdt_ticcategory", "TIC Category Value"}, {"cdt_ticcategoryname", "TIC Category"},
    {"cdt_scalingmethod", "Scaling Method Value"}, {"cdt_scalingmethodname", "Scaling Method"}, {"cdt_scalingexponent", "Scaling Exponent"},
    {"cdt_isleaf", "Is Leaf"}, {"cdt_sortorder", "Sort Order"}})

// ============================== Cost Version ====================================================
fnPick("cdt_costversion", {{"cdt_costversionid", "Cost Version Id"}, {"cdt_code", "Version Code"}, {"cdt_name", "Cost Version"},
    {"cdt_product", "Product Id"}, {"cdt_versionnumber", "Version Number"}, {"cdt_statusname", "Version Status"},
    {"cdt_releasedon", "Released On"}, {"cdt_isbaseline", "Is Baseline"}})

// ============================== Compare Version =================================================
// Same content as Cost Version, NOT related to any table. Used as slicer "compare with".
fnPick("cdt_costversion", {{"cdt_costversionid", "Cost Version Id"}, {"cdt_code", "Compare Version Code"}, {"cdt_name", "Compare Version"}})

// ============================== Cost Item =======================================================
fnPick("cdt_costitem", {{"cdt_costitemid", "Cost Item Id"}, {"cdt_name", "Cost Item"}, {"cdt_costversion", "Cost Version Id"},
    {"cdt_cbselement", "CBS Element Id"}, {"cdt_supplier", "Supplier Id"}, {"cdt_costtype", "Cost Type Value"}, {"cdt_costtypename", "Cost Type"},
    {"cdt_teamcenteritemid", "Teamcenter Item ID"}, {"cdt_quantity", "Quantity"}, {"cdt_unit", "Unit"}, {"cdt_unitprice", "Unit Price"},
    {"cdt_currencycode", "Currency"}, {"cdt_fxrate", "FX Rate"}, {"cdt_amounteur", "Amount EUR"},
    {"cdt_pricesourcename", "Price Source"}, {"cdt_pricedate", "Price Date"}, {"cdt_confidencename", "Confidence"}, {"cdt_makebuyname", "Make or Buy"}})

// ============================== Supplier ========================================================
fnPick("cdt_supplier", {{"cdt_supplierid", "Supplier Id"}, {"cdt_name", "Supplier"}, {"cdt_teamcenterid", "Supplier Teamcenter ID"}, {"cdt_country", "Supplier Country"}})

// ============================== Region ==========================================================
fnPick("cdt_region", {{"cdt_regionid", "Region Id"}, {"cdt_code", "Region Code"}, {"cdt_name", "Region"}})

// ============================== Regional Factor =================================================
fnPick("cdt_regionalfactor", {{"cdt_regionalfactorid", "Regional Factor Id"}, {"cdt_region", "Region Id"},
    {"cdt_costtype", "Cost Type Value"}, {"cdt_costtypename", "Cost Type"}, {"cdt_factor", "Factor"}})

// ============================== Feature =========================================================
fnPick("cdt_feature", {{"cdt_featureid", "Feature Id"}, {"cdt_code", "Feature Code"}, {"cdt_name", "Feature"}, {"cdt_product", "Product Id"}})

// ============================== Feature Impact ==================================================
fnPick("cdt_featureimpact", {{"cdt_featureimpactid", "Feature Impact Id"}, {"cdt_feature", "Feature Id"}, {"cdt_cbselement", "CBS Element Id"},
    {"cdt_impacttype", "Impact Type Value"}, {"cdt_impacttypename", "Impact Type"}, {"cdt_value", "Value"},
    {"cdt_costtype", "Cost Type Value"}, {"cdt_costtypename", "Cost Type"}})

// ============================== Scenario ========================================================
fnPick("cdt_scenario", {{"cdt_scenarioid", "Scenario Id"}, {"cdt_code", "Scenario Code"}, {"cdt_name", "Scenario"},
    {"cdt_costversion", "Cost Version Id"}, {"cdt_region", "Region Id"}, {"cdt_sizemw", "Size MW"},
    {"cdt_statusname", "Scenario Status"}, {"cdt_totaleur", "Total EUR"}, {"cdt_totalperkw", "Total EUR per kW"}, {"cdt_calculatedon", "Calculated On"}})

// ============================== Scenario Line ===================================================
fnPick("cdt_scenarioline", {{"cdt_scenariolineid", "Scenario Line Id"}, {"cdt_scenario", "Scenario Id"}, {"cdt_cbselement", "CBS Element Id"},
    {"cdt_feature", "Feature Id"}, {"cdt_linetypename", "Line Type"}, {"cdt_costtypename", "Cost Type"}, {"cdt_scopename", "Scope"},
    {"cdt_ticcategoryname", "TIC Category"}, {"cdt_baseamounteur", "Base Amount EUR"}, {"cdt_scalefactor", "Scale Factor"},
    {"cdt_regionalfactor", "Regional Factor"}, {"cdt_finalcosteur", "Final Cost EUR"}, {"cdt_costperkw", "Cost per kW"}})

// ============================== Target ==========================================================
fnPick("cdt_target", {{"cdt_targetid", "Target Id"}, {"cdt_cbselement", "CBS Element Id"}, {"cdt_targeteurperkw", "Target EUR per kW"},
    {"cdt_targetyear", "Target Year"}, {"cdt_basisname", "Target Basis"}})

// ============================== Benchmark =======================================================
fnPick("cdt_benchmark", {{"cdt_benchmarkid", "Benchmark Id"}, {"cdt_name", "Benchmark"}, {"cdt_subject", "Subject"}, {"cdt_isown", "Own Product"},
    {"cdt_scopename", "Scope"}, {"cdt_ticcategoryname", "TIC Category"}, {"cdt_valueeurperkw", "Value EUR per kW"},
    {"cdt_plantsizemw", "Plant Size MW"}, {"cdt_year", "Year"}, {"cdt_source", "Source"}, {"cdt_confidencename", "Confidence"}})

// ============================== Idea ============================================================
fnPick("cdt_idea", {{"cdt_ideaid", "Idea Id"}, {"cdt_name", "Idea"}, {"cdt_cbselement", "CBS Element Id"}, {"cdt_estimatedsavingeur", "Estimated Saving EUR"},
    {"cdt_statusname", "Idea Status"}, {"cdt_categoryname", "Idea Category"}, {"cdt_submittername", "Submitter"}, {"createdon", "Created On"}})

// ============================== Measure =========================================================
fnPick("cdt_measure", {{"cdt_measureid", "Measure Id"}, {"cdt_code", "Measure Code"}, {"cdt_name", "Measure"}, {"cdt_cbselement", "CBS Element Id"},
    {"cdt_savingeur", "Saving EUR"}, {"cdt_oneoffcosteur", "One-off Cost EUR"}, {"cdt_effortpd", "Effort PD"}, {"cdt_probability", "Probability"},
    {"cdt_dilevel", "DI Level Value"}, {"cdt_dilevelname", "DI Level"}, {"cdt_statusname", "Measure Status"}, {"cdt_duedate", "Due Date"},
    {"cdt_priorityscore", "Priority Score"}, {"cdt_realisedsavingeur", "Realised Saving EUR"}})

// ============================== Size MW =========================================================
// What-if parameter table for the project size slicer (not related to any table).
// Alternative: Modeling > New parameter > Numeric range, name "Size MW", 10 to 2000, increment 10.
Table.FromColumns({List.Numbers(10, 200, 10)}, type table [#"Size MW" = number])
