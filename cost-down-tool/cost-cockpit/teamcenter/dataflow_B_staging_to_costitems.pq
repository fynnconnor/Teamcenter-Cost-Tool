// Cost Cockpit - Dataflow B: staging rows + mapping + FX rates -> Suppliers, Cost Items, staging status
// ----------------------------------------------------------------------------------------------
// Power Query (M). Create a second Dataverse dataflow with FOUR queries. Paste each block into its
// own blank query and give it the name printed above the block. The first query is shared.
// Works for both import routes: rows written to the staging table by dataflow A (file export)
// or by a flow that calls the Teamcenter connector.
//
// Load settings:
//   Staged         : no load (untick "Enable load")
//   SuppliersOut   : table Suppliers (cdt_supplier),               key "Supplier Teamcenter ID"
//   CostItemsOut   : table Cost Items (cdt_costitem),              key "Cost item import key"
//                    map  CostVersionCode -> Cost version . Code (cdt_CostVersion.cdt_code)
//                         CBSCode         -> CBS element . Code  (cdt_CBSElement.cdt_code)
//                         SupplierTcId    -> Supplier . Teamcenter ID (cdt_Supplier.cdt_teamcenterid)
//   StagingStatusOut : table Teamcenter Import Rows (cdt_tcimportrow), key "Import row key"
//   Never tick "Delete rows that no longer exist in the query output".
//   Order: refresh SuppliersOut before CostItemsOut (same dataflow refreshes them in dependency order
//   when CostItemsOut references SuppliersOut; otherwise run the dataflow twice on the first import).


// ============================== query: Staged ================================================
let
    // ---- parameters -------------------------------------------------------------------------
    EnvironmentHost = "<org>.crm4.dynamics.com",          // without https://
    ImportRun       = "export-template",                  // value of "Import run" to process
    // ---- sources ------------------------------------------------------------------------------
    Source   = CommonDataService.Database(EnvironmentHost),
    Staging  = Source{[Schema = "dbo", Item = "cdt_tcimportrow"]}[Data],
    Mapping  = Source{[Schema = "dbo", Item = "cdt_tcmapping"]}[Data],
    CBS      = Source{[Schema = "dbo", Item = "cdt_cbselement"]}[Data],
    FX       = Source{[Schema = "dbo", Item = "cdt_fxrate"]}[Data],
    Run      = Table.SelectRows(Staging, each [cdt_importrun] = ImportRun),
    Slim     = Table.SelectColumns(Run, {"cdt_name", "cdt_versioncode", "cdt_itemid", "cdt_revision", "cdt_itemname", "cdt_quantity",
                   "cdt_unit", "cdt_unitprice", "cdt_currencycode", "cdt_supplierid", "cdt_suppliername", "cdt_pricedate", "cdt_cbscode", "cdt_costtype"}),
    // mapping table: Teamcenter item ID -> CBS element + cost type
    MapSlim  = Table.RenameColumns(Table.SelectColumns(Mapping, {"cdt_name", "cdt_cbselement", "cdt_costtype"}),
                   {{"cdt_name", "map_item"}, {"cdt_cbselement", "map_cbsid"}, {"cdt_costtype", "map_costtype"}}),
    J1       = Table.Join(Slim, "cdt_itemid", MapSlim, "map_item", JoinKind.LeftOuter),
    CbsSlim  = Table.RenameColumns(Table.SelectColumns(CBS, {"cdt_cbselementid", "cdt_code"}), {{"cdt_cbselementid", "cbs_id"}, {"cdt_code", "cbs_code_map"}}),
    J2       = Table.Join(J1, "map_cbsid", CbsSlim, "cbs_id", JoinKind.LeftOuter),
    FxSlim   = Table.RenameColumns(Table.SelectColumns(FX, {"cdt_name", "cdt_ratetoeur"}), {{"cdt_name", "fx_code"}, {"cdt_ratetoeur", "fx_rate"}}),
    J3       = Table.Join(J2, "cdt_currencycode", FxSlim, "fx_code", JoinKind.LeftOuter),
    // a CBS code typed by hand into the staging row wins over the mapping table
    WithCbs  = Table.AddColumn(J3, "CBSCode", each if [cdt_cbscode] <> null and [cdt_cbscode] <> "" then [cdt_cbscode] else [cbs_code_map], type text),
    WithType = Table.AddColumn(WithCbs, "CostTypeValue", each [cdt_costtype] ?? [map_costtype] ?? 710000001, Int64.Type),   // default Material
    WithFx   = Table.AddColumn(WithType, "FxRate", each if [cdt_currencycode] = null or [cdt_currencycode] = "EUR" then 1 else [fx_rate], type number),
    WithOk   = Table.AddColumn(WithFx, "Problem", each
                   if [CBSCode] = null then "No mapping for this item: add it to Teamcenter Mappings or type a CBS code"
                   else if [cdt_unitprice] = null then "No price in the export"
                   else if [FxRate] = null then "No FX rate for " & [cdt_currencycode]
                   else null, type text)
in
    WithOk


// ============================== query: SuppliersOut ==========================================
let
    Source   = Staged,
    WithId   = Table.SelectRows(Source, each [cdt_supplierid] <> null and [cdt_supplierid] <> ""),
    Slim     = Table.SelectColumns(WithId, {"cdt_supplierid", "cdt_suppliername"}),
    Distinct = Table.Distinct(Slim, {"cdt_supplierid"}),
    Result   = Table.RenameColumns(Distinct, {{"cdt_supplierid", "cdt_teamcenterid"}, {"cdt_suppliername", "cdt_name"}})
in
    Result


// ============================== query: CostItemsOut ==========================================
let
    Source   = Table.SelectRows(Staged, each [Problem] = null),
    Shaped   = Table.FromRecords(Table.TransformRows(Source, (r) => [
                   cdt_importkey          = r[cdt_versioncode] & "~" & r[CBSCode] & "~" & r[cdt_itemid],
                   cdt_name               = r[cdt_itemname] ?? r[cdt_itemid],
                   CostVersionCode        = r[cdt_versioncode],
                   CBSCode                = r[CBSCode],
                   SupplierTcId           = r[cdt_supplierid],
                   cdt_costtype           = r[CostTypeValue],
                   cdt_teamcenteritemid   = r[cdt_itemid],
                   cdt_teamcenterrevision = r[cdt_revision],
                   cdt_quantity           = r[cdt_quantity] ?? 0,
                   cdt_unit               = r[cdt_unit],
                   cdt_unitprice          = r[cdt_unitprice],
                   cdt_currencycode       = r[cdt_currencycode] ?? "EUR",
                   cdt_fxrate             = r[FxRate],
                   cdt_amounteur          = Number.Round((r[cdt_quantity] ?? 0) * r[cdt_unitprice] * r[FxRate], 2),
                   cdt_pricesource        = 710000001,      // Teamcenter
                   cdt_pricedate          = r[cdt_pricedate]
               ])),
    Result   = Table.TransformColumnTypes(Shaped, {
                   {"cdt_importkey", type text}, {"cdt_name", type text}, {"CostVersionCode", type text}, {"CBSCode", type text},
                   {"SupplierTcId", type text}, {"cdt_costtype", Int64.Type}, {"cdt_teamcenteritemid", type text},
                   {"cdt_teamcenterrevision", type text}, {"cdt_quantity", type number}, {"cdt_unit", type text},
                   {"cdt_unitprice", type number}, {"cdt_currencycode", type text}, {"cdt_fxrate", type number},
                   {"cdt_amounteur", type number}, {"cdt_pricesource", Int64.Type}, {"cdt_pricedate", type date}})
in
    Result


// ============================== query: StagingStatusOut ======================================
let
    Source   = Staged,
    Shaped   = Table.FromRecords(Table.TransformRows(Source, (r) => [
                   cdt_name    = r[cdt_name],
                   cdt_cbscode = r[CBSCode],
                   cdt_status  = if r[Problem] = null then 710000003 else if r[CBSCode] = null then 710000001 else 710000004,   // Loaded / New / Error
                   cdt_message = r[Problem] ?? "Loaded into cost items"
               ])),
    Result   = Table.TransformColumnTypes(Shaped, {{"cdt_name", type text}, {"cdt_cbscode", type text}, {"cdt_status", Int64.Type}, {"cdt_message", type text}})
in
    Result
