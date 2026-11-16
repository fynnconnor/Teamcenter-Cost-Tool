// Cost Cockpit - Dataflow A: Teamcenter export file -> staging table "Teamcenter Import Rows"
// ----------------------------------------------------------------------------------------------
// Power Query (M). Create a Dataverse dataflow (make.powerapps.com > Dataflows > New dataflow),
// choose "Blank query", open the Advanced editor and paste this query. Adjust the four parameters.
//
// Load settings (step "Map tables"):
//   Destination table : Teamcenter Import Rows (cdt_tcimportrow), "Load to existing table"
//   Key               : Import row key (cdt_name)       -> rows are upserted, re-running is safe
//   Column mapping    : automatic, the output columns carry the logical column names
//   Do NOT tick "Delete rows that no longer exist in the query output".
//
// Expected file: CSV with the header of export-template.csv. One row per priced item.
// Quantity must be the TOTAL quantity of the item in the product at reference size
// (a flattened BOM). If Teamcenter exports quantity per parent, flatten it before or in Teamcenter.
let
    // ---- parameters -------------------------------------------------------------------------
    SiteUrl      = "https://<tenant>.sharepoint.com/sites/<site>",
    FolderPart   = "/CostCockpit/TeamcenterExport/",     // part of the folder path that identifies the drop folder
    VersionCode  = "DEMO-V002",                          // draft cost version the import goes into
    Delimiter    = ",",                                  // ";" for German Excel exports
    Culture      = "en-US",                              // "de-DE" if numbers use a decimal comma
    // ---- newest file in the drop folder -------------------------------------------------------
    Files        = SharePoint.Files(SiteUrl, [ApiVersion = 15]),
    InFolder     = Table.SelectRows(Files, each Text.Contains([Folder Path], FolderPart) and Text.EndsWith(Text.Lower([Name]), ".csv")),
    Newest       = Table.FirstN(Table.Sort(InFolder, {{"Date modified", Order.Descending}}), 1),
    FileName     = Newest{0}[Name],
    ImportRun    = Text.BeforeDelimiter(FileName, ".", {0, RelativePosition.FromEnd}),
    // ---- parse --------------------------------------------------------------------------------
    Csv          = Csv.Document(Newest{0}[Content], [Delimiter = Delimiter, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted     = Table.PromoteHeaders(Csv, [PromoteAllScalars = true]),
    Typed        = Table.TransformColumnTypes(Promoted, {
                       {"ItemID", type text}, {"Revision", type text}, {"ItemName", type text}, {"ParentItemID", type text},
                       {"Level", Int64.Type}, {"Quantity", type number}, {"Unit", type text}, {"UnitPrice", type number},
                       {"Currency", type text}, {"SupplierID", type text}, {"SupplierName", type text}, {"PriceDate", type date}}, Culture),
    NonEmpty     = Table.SelectRows(Typed, each [ItemID] <> null and Text.Trim([ItemID]) <> ""),
    // ---- shape to the staging table -----------------------------------------------------------
    Shaped       = Table.FromRecords(Table.TransformRows(NonEmpty, (r) => [
                       cdt_name          = ImportRun & "~" & r[ItemID] & "~" & (r[ParentItemID] ?? ""),
                       cdt_importrun     = ImportRun,
                       cdt_versioncode   = VersionCode,
                       cdt_itemid        = Text.Trim(r[ItemID]),
                       cdt_revision      = r[Revision],
                       cdt_itemname      = r[ItemName],
                       cdt_parentitemid  = r[ParentItemID],
                       cdt_bomlevel      = r[Level],
                       cdt_quantity      = r[Quantity],
                       cdt_unit          = r[Unit],
                       cdt_unitprice     = r[UnitPrice],
                       cdt_currencycode  = Text.Upper(r[Currency] ?? "EUR"),
                       cdt_supplierid    = r[SupplierID],
                       cdt_suppliername  = r[SupplierName],
                       cdt_pricedate     = r[PriceDate],
                       cdt_status        = 710000001      // New
                   ])),
    Result       = Table.TransformColumnTypes(Shaped, {
                       {"cdt_name", type text}, {"cdt_importrun", type text}, {"cdt_versioncode", type text}, {"cdt_itemid", type text},
                       {"cdt_revision", type text}, {"cdt_itemname", type text}, {"cdt_parentitemid", type text}, {"cdt_bomlevel", Int64.Type},
                       {"cdt_quantity", type number}, {"cdt_unit", type text}, {"cdt_unitprice", type number}, {"cdt_currencycode", type text},
                       {"cdt_supplierid", type text}, {"cdt_suppliername", type text}, {"cdt_pricedate", type date}, {"cdt_status", Int64.Type}})
in
    Result
