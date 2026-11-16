# Teamcenter interface (requirement R5)

Goal: prices, quantities and suppliers flow from Teamcenter into the cost items of a draft cost version, without retyping.

## What to clarify with PLM IT first

1. **Where do prices and suppliers live?** In Teamcenter attributes (which ones, on item, revision or vendor part?), in the ERP system, or in Excel? If prices are not in Teamcenter, the import below takes structure and suppliers from Teamcenter and prices from the other source.
2. Which **Teamcenter release** is installed, and is Active Workspace in use?
3. Can a **saved query or report** export the columns of `export-template.csv`? Who can schedule it?
4. Is the JSON service endpoint reachable (`https://<host>/tc/JsonRestServices`), and may a **service account** be used?
5. Is an **on-premises data gateway** available for Power Platform?

## Routes

| Route | When | What you build | Files |
|---|---|---|---|
| T1 File export | Phase 1, start here | Export file dropped in SharePoint; dataflow A loads it into the staging table; dataflow B turns staging rows into cost items | `export-template.csv`, `dataflow_A_export_to_staging.pq`, `dataflow_B_staging_to_costitems.pq` |
| T2 Teamcenter Power BI integration | If release 2606 or later is installed | Use the Siemens templates to bring BOM data into Power BI; export from there to the drop folder, then T1 | none |
| T3 Service connector | Phase 4 | Custom connector calls the Teamcenter services; a flow writes the same staging rows; dataflow B stays unchanged | `teamcenter-connector.swagger.json` |

All routes end in the same staging table, so the mapping and the cost-item logic are built once.

## How the import works

```
Teamcenter export (CSV)  --dataflow A-->  Teamcenter Import Rows (staging)
                                                  |
        Teamcenter Mappings (item -> CBS element, cost type)   FX Rates
                                                  |
                                           --dataflow B-->  Suppliers, Cost Items (upsert by import key)
                                                            staging rows marked Loaded / New / Error
```

1. Export from Teamcenter with the columns of `export-template.csv` and save the file in the SharePoint drop folder. The file name becomes the *import run*.
2. Refresh dataflow A. The rows appear under *Teamcenter Import Rows* with status New.
3. Refresh dataflow B. Rows whose item ID is in *Teamcenter Mappings* become cost items of the draft version; they are marked Loaded.
4. Open the view *Not mapped*. For each row, either add the item to *Teamcenter Mappings* (CBS element and cost type) or type a CBS code into the row. Refresh dataflow B again. The mapping is remembered, so the next import of the same item needs no manual step.
5. Check the total of the draft version in the app or in Power BI.

Rules built into the queries:

- A cost item is identified by **version code ~ CBS code ~ item ID**. Re-importing updates quantity, price, supplier and FX rate of the same item and does not create duplicates.
- Amount (EUR) = quantity × unit price × FX rate, written by the dataflow. Items in EUR get FX rate 1; other currencies need a row in *FX Rates*.
- Quantity must be the **total quantity in the product at reference size**. If the export contains quantities per parent line, flatten the BOM in the Teamcenter report or multiply along the structure before the import.
- Cost items that are not in Teamcenter (engineering hours, lump sums, estimates) are entered in the app and are never touched by the import, because their import key has no Teamcenter item ID.
- Items that disappear from Teamcenter are not deleted automatically. The view *Cost Items* sorted by price date shows items that were not refreshed.

Test with the demo data: copy `export-template.csv` to the drop folder, set `VersionCode = "DEMO-V002"` in dataflow A and `ImportRun = "export-template"` in dataflow B. Expected: six cost items of DEMO-V002 updated (total of DEMO-V002 unchanged at 90,380,000 EUR), one staging row *Not mapped* (item 100099).

## Route T3: custom connector

`teamcenter-connector.swagger.json` is an OpenAPI 2.0 definition with eight operations of the Teamcenter JSON services: login, session info, get item by ID, get properties, find saved queries, create BOM window, expand one level, close BOM windows.

It is a **starting template**. Request shapes for login, properties, item lookup and BOM windows follow publicly available client code; *Expand BOM one level* was not verified. Service names and payloads differ between Teamcenter releases and customisations, so check each operation against the service documentation of your installation before relying on it. Newer Teamcenter REST endpoints may use OAuth client credentials instead of a session cookie; ask PLM IT which applies.

Steps:

1. *make.powerapps.com > Custom connectors > New > Import an OpenAPI file*. Set the host to your Teamcenter web tier. Tick *Connect via on-premises data gateway* if Teamcenter is not reachable from the internet.
2. Security: *No authentication* at connector level. The session is handled by the Login operation.
3. Test *Log in* with the service account. Read the header `Set-Cookie` of the response and copy the `JSESSIONID=...` part.
4. Test *Get session info* with that value in the parameter *Session cookie*.
5. Build the flow: Log in > extract cookie with `first(split(outputs('Log_in')?['headers']?['Set-Cookie'], ';'))` > Get item by ID or run a saved query > Get properties (price, vendor, quantity attributes) > for each result *Add a new row* to **Teamcenter Import Rows** with the same columns dataflow A writes > refresh dataflow B (*Refresh a dataflow* action).
6. Store the service-account password in an environment variable of type secret (Azure Key Vault), not in the flow.

If the response does not expose `Set-Cookie` through the connector, call the services with the *HTTP* action through the gateway instead, or ask PLM IT for a token-based endpoint.

## Sources

- Siemens community and third-party documentation on `/tc/JsonRestServices` and the login service: see dossier sources S14, S15.
- Request shapes: open-source client `Krusty84/TCSwiftBridge` on GitHub (login, getProperties, getItemFromId, createBOMWindows, closeBOMWindows).
