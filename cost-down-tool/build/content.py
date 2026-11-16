"""Single source of truth for the cost-down tool make-or-buy research.

Run `python3 content.py` to dump content.json (consumed by build_pptx.js).
build_xlsx.py imports CONTENT directly.

Conventions
- "fact" texts are taken from the sources listed in SOURCES (IDs in brackets).
- Anything called "planning assumption" is the author's estimate, not a vendor quote.
"""
import json
import os

# --------------------------------------------------------------------------
# Requirements (from the task description, first brainstorming)
# --------------------------------------------------------------------------
REQUIREMENTS = [
    # id, block, short, english, german original, proposed priority
    ("R1", "1 Cost transparency", "Detailed cost roll-up",
     "Status-quo cost transparency at detail level (roll-up over the product / cost breakdown structure)",
     "Status quo Kostentransparenz auf Detaillevel", "Must"),
    ("R2", "1 Cost transparency", "Cost type & scope split",
     "Separation of cost types (e.g. material vs. engineering effort) and of NCA scope vs. EPC scope",
     "Trennung zwischen Kostenarten (z.B. Material und ENG-Aufwände, sowie NCA-scope und EPC-scope)", "Must"),
    ("R3", "1 Cost transparency", "Feature-to-TIC mapping",
     "Show the dependency of product features on TIC (total installed cost) topics",
     "Abhängigkeit von Product Features zu TIC Themen aufzeigen", "Must"),
    ("R4", "1 Cost transparency", "Cost-driver analysis",
     "Analysis features such as identification of the largest cost drivers",
     "Analyse Feature wie Identifikation von größten Kostentreibern etc.", "Must"),
    ("R5", "1 Cost transparency", "Teamcenter interface",
     "Teamcenter interface as input for prices and suppliers",
     "Schnittstelle Teamcenter als Input für Preise und Lieferanten", "Must"),
    ("R6", "1 Cost transparency", "Versioning",
     "Versioning to compare cost status over time",
     "Versionierung zum Vergleich über Zeit", "Must"),
    ("R7", "2 Scenario simulation", "Scaling effects",
     "Scaling effects: automatic cost transparency for different project sizes",
     "Skalierungseffekte --> Automatische Kostentransparenz für verschiedene Projektgrößen", "Must"),
    ("R8", "2 Scenario simulation", "Regional differences",
     "Regional cost differences depending on project site, especially for TIC topics",
     "Regionale Kostenunterschiede (je nach Projektstandort), insbesondere für TIC-Themen", "Must"),
    ("R9", "3 Target costs & tracking", "Benchmarking",
     "Cost benchmarking between own products and competitors",
     "Cost benchmarking zwischen eigenen Produkten und Wettbewerbern", "Should"),
    ("R10", "3 Target costs & tracking", "Target per component",
     "Target value definition per cost component",
     "Zielwertbestimmung je Kostenkomponente", "Must"),
    ("R11", "3 Target costs & tracking", "Idea repository",
     "Idea repository fed by colleagues",
     "Ideenspeicher von Kollegen", "Should"),
    ("R12", "3 Target costs & tracking", "Measures & prioritisation",
     "List of measures incl. prioritisation (and tracking against targets)",
     "Maßnahmenliste und Priorisierung", "Must"),
    ("R13", "4 LCOH Suite", "LCOH Suite interface",
     "Interface to the LCOH Suite (Power App) to fill its database; alternatively built as part of the LCOH Suite",
     "Schnittstelle zu LCOH Suite in Powerapp zur Befüllung Datenbank", "Must"),
]

# --------------------------------------------------------------------------
# Solutions compared (5 external + 3 in-house)
# --------------------------------------------------------------------------
SOLUTIONS = [
    # key, short label, long label, type
    ("TCPCM", "Teamcenter PCM", "Siemens Teamcenter Product Cost Management", "External"),
    ("APRIORI", "aPriori", "aPriori Manufacturing Insights Platform", "External"),
    ("FACTON", "FACTON EPC", "FACTON EPC Suite", "External"),
    ("TSET", "Tset", "Tset Cost & Carbon", "External"),
    ("CLEO", "Cleopatra", "Cleopatra Enterprise (Cost Engineering)", "External"),
    ("IHA", "In-house A", "In-house A: Lean (Excel + SharePoint + Power BI)", "In-house"),
    ("IHB", "In-house B", "In-house B: Power Platform app (Dataverse + Power Apps + Power BI)", "In-house"),
    ("IHC", "In-house C", "In-house C: Fabric data platform (+ Power BI / Power Apps)", "In-house"),
]

# Requirement fit, 0-3 per requirement R1..R13, same order as SOLUTIONS.
# 0 = not covered, 1 = workaround / heavy customisation, 2 = largely covered by
# configuration, 3 = native / designed in. In-house scores describe the TARGET
# design (nothing exists today); delivery risk is scored separately.
FIT = {
    "TCPCM":   [3, 2, 1, 2, 3, 3, 1, 2, 1, 3, 0, 1, 1],
    "APRIORI": [2, 1, 0, 3, 3, 2, 1, 2, 1, 2, 0, 1, 1],
    "FACTON":  [3, 2, 1, 2, 2, 3, 1, 2, 1, 3, 0, 1, 1],
    "TSET":    [3, 2, 1, 2, 1, 2, 1, 2, 1, 2, 0, 0, 2],
    "CLEO":    [2, 2, 1, 2, 0, 2, 3, 3, 2, 1, 0, 0, 1],
    "IHA":     [2, 3, 2, 3, 1, 1, 2, 2, 2, 2, 2, 2, 2],
    "IHB":     [3, 3, 3, 3, 2, 3, 3, 3, 2, 3, 3, 3, 3],
    "IHC":     [3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 2, 2, 2],
}

FIT_RATIONALE = {
    "TCPCM": "BOM-based costing with Teamcenter structure import, versions, target costing and a factor-cost knowledge base; built for manufactured products, so plant-size scaling, TIC, ideas/measures and the LCOH link need workarounds.",
    "APRIORI": "Strong on cost drivers of manufactured parts from 3D CAD and on regional manufacturing data; weak on system-level monitoring, engineering hours, TIC and measure tracking.",
    "FACTON": "Enterprise costing with versioning, design-to-cost and target costing; Teamcenter connector not publicly documented; no idea/measure management; TIC scaling by workaround.",
    "TSET": "Modern SaaS, flexible calculators (own Excel logic), open API; no public Teamcenter connector; no idea/measure management; TIC scaling by workaround.",
    "CLEO": "Built for capital-project estimating: location factors, scaling/parametric models, benchmarking of projects; not a BOM/Teamcenter product-costing tool and no idea/measure management.",
    "IHA": "Covers every block at a basic level and is very flexible, but versioning, security, relational structure and the Teamcenter link stay manual and fragile.",
    "IHB": "Data model is designed around exactly these requirements and shares the platform with the LCOH Suite; Teamcenter interface and benchmark data must be built/collected.",
    "IHC": "Same coverage as B with stronger data integration and simulation; idea/measure front end and LCOH link need an additional app layer; highest build effort.",
}

# --------------------------------------------------------------------------
# Weighted scoring (criteria, weights, 1-5 scores). C1 is derived from FIT.
# --------------------------------------------------------------------------
CRITERIA = [
    # id, name, weight, description
    ("C1", "Functional fit to requirements", 0.30, "Derived from the fit matrix (sum of R1-R13 scores / 39 x 5)"),
    ("C2", "Teamcenter integration", 0.10, "How directly prices/suppliers/BOM flow in from Teamcenter"),
    ("C3", "LCOH Suite / Power Platform integration", 0.10, "Effort to feed the LCOH Suite database and reuse the Microsoft stack"),
    ("C4", "5-year cost (TCO)", 0.15, "Licences + implementation + internal effort over 5 years (5 = lowest cost)"),
    ("C5", "Time to first usable release", 0.10, "Incl. selection/procurement for external tools (5 = fastest)"),
    ("C6", "Flexibility / ownership of cost logic", 0.10, "Ability to change structures, formulas and reports without a vendor"),
    ("C7", "Reference data & methods out of the box", 0.05, "Shipped labour, machine, material, location data and costing methods"),
    ("C8", "Sustainability & risk", 0.10, "Vendor viability or key-person / maintenance risk (5 = lowest risk)"),
]

# scores for C2..C8 (C1 computed), order as SOLUTIONS
SCORES = {
    "C2": [5, 4, 3, 2, 1, 2, 3, 4],
    "C3": [2, 2, 2, 3, 2, 4, 5, 4],
    "C4": [2, 1, 2, 2, 3, 5, 4, 3],
    "C5": [2, 2, 2, 3, 3, 5, 4, 2],
    "C6": [2, 2, 3, 3, 3, 4, 5, 5],
    "C7": [5, 5, 4, 4, 4, 1, 1, 1],
    "C8": [5, 4, 4, 3, 4, 2, 3, 3],
}

# --------------------------------------------------------------------------
# External shortlist: KPI rows
# --------------------------------------------------------------------------
EXT_KPI_ROWS = [
    "Vendor / origin",
    "Product focus",
    "Deployment",
    "Licence model",
    "Public price signal",
    "Planning assumption: licence per year",
    "Planning assumption: one-off implementation",
    "Implementation time (after contract)",
    "Reference data shipped",
    "Teamcenter integration",
    "API / Power BI / Microsoft integration",
    "Versioning & scenarios",
    "Target costing",
    "Published customers",
    "Main strengths for this use case",
    "Main gaps vs. requirements",
    "Vendor risk",
    "Sources",
]

EXT_KPIS = {
    "TCPCM": [
        "Siemens Digital Industries Software (DE/US); half-yearly releases (2412, 2506, 2512, 2606)",
        "Product costing, tool costing, profitability calculation, should-cost / purchase price analysis, CO2e footprint",
        "On-premises, or SaaS as Teamcenter X Product Cost Management",
        "Named end-user licences plus add-on modules; quote only",
        "None for PCM. Teamcenter X Essentials is reported at roughly USD 150-200 per user/month by third parties (not PCM-specific); AWS Marketplace lists a 20-named-user minimum for Teamcenter X",
        "EUR 60k-200k (enterprise PCM class; no vendor quote yet)",
        "EUR 60k-300k (services 1-3x first-year licence is a common enterprise-software rule of thumb)",
        "4-9 months (planning assumption; validate with Siemens partner)",
        "Production-site data for 67 countries / 454 regions (release 2406): labour cost (2 skill levels), labour burden (3 shifts), floor space, interest; energy and interest updated twice a year; machine database updated quarterly; about 10,000 materials (v9.3)",
        "Native: direct import of product structures from Teamcenter incl. attribute mapping (make-or-buy, plant, technology); 2606 beta item: roll-up of cost targets and values inside Teamcenter",
        "Own OpenAPI REST interface; 2606 adds an endpoint for aggregated profitability KPIs for Power BI / Tableau / SAP BDC; Excel export of cost breakdowns (2506)",
        "Versions of calculations, technical and business what-if scenarios, best/normal/worst case in profitability",
        "Yes - target costing and cost-target roll-up are core use cases",
        "Not researched per name; positioned by Siemens for automotive, machinery, aerospace and other discrete manufacturing",
        "Teamcenter-native; strongest shipped knowledge base; low vendor risk; same vendor as the PLM",
        "No plant-size/TIC scaling logic, no construction location factors, no idea/measure management, LCOH link only via API",
        "Low (Siemens)",
        "S1 S2 S3 S4 S5 S6 S7 S8 S11 S12 S13 S14",
    ],
    "APRIORI": [
        "aPriori Technologies (US)",
        "Manufacturing cost and manufacturability simulation driven by 3D CAD geometry (should-cost, design-to-cost, sourcing)",
        "Cloud (user tiers 20/50/100/200/500/1,250 in 2022 datasheet) or on-premises",
        "Named user, annual subscription; foundation package sized by deployment plus regional data libraries and modules",
        "Third-party estimates only: about USD 4,000-17,000 per month to start; 'enterprise platforms like aPriori typically start at USD 100k+ per year'; add-on regional data about USD 400-2,000 per month",
        "EUR 100k-250k (upper end of the class per third-party signals)",
        "EUR 35k-175k per third-party estimate (setup 10-50k, integration 10-50k, digital-factory customisation 15-75k USD)",
        "About 6 months (G2 user-review average); ROI after about 18 months (G2)",
        "95 regional data libraries (pricing page; FAQ says 87) and 450+ manufacturing process simulations",
        "Yes - PLM integration with Teamcenter and Windchill is part of the 'Automate' packaging (aP Connect)",
        "Integration layer (aP Connect); API; reporting module",
        "Scenario comparison of regions, processes, materials; saved scenarios",
        "Yes (design-to-cost targets at part/assembly level)",
        "Carrier (case study); Forrester TEI composite of four customers",
        "Deepest automatic cost-driver insight for manufactured parts; Teamcenter integration; large regional library",
        "Needs 3D CAD and manufacturing focus; little value for engineering hours, EPC scope, TIC, benchmarking of whole plants, ideas/measures",
        "Low-medium (established private vendor)",
        "S17 S18 S19 S20 S21 S22 S23",
    ],
    "FACTON": [
        "FACTON GmbH (Germany)",
        "Enterprise product costing across the lifecycle: quotation calculation, should costing, design-to-cost, cost controlling, management reporting, product carbon footprint",
        "On-premises or SaaS in the cloud (Azure-based cloud offer announced 2016)",
        "Editions EPC Standard / EPC Professional plus add-on modules; quote only",
        "None published",
        "EUR 60k-200k (enterprise PCM class; no vendor quote yet)",
        "EUR 60k-300k (planning assumption)",
        "4-9 months (planning assumption; vendor claims 'rapid implementation' for the standard solution without a figure)",
        "Benchmark data for wages, overheads and machines (Should Costing)",
        "Generic ERP/PLM interfaces; PTC Windchill named publicly, Teamcenter connector not publicly documented - to be confirmed",
        "Power BI integration named; listed on Microsoft Marketplace (Should Costing)",
        "Versioning and simulation are core concepts of the platform",
        "Yes - design-to-cost / target costing is a core module",
        "Airbus, Porsche, Ford, Deutz, Brose, MANN+HUMMEL, mtu, Wittenstein, Safran, MAHLE, Hauni, Hettich",
        "German vendor with mechanical- and plant-engineering references; strong versioning and target costing; controlling view",
        "Teamcenter link unclear; no idea/measure management; TIC scaling and regional construction factors by customisation",
        "Low-medium (established mid-size vendor)",
        "S24 S25 S26 S27 S28 S29 S30",
    ],
    "TSET": [
        "Tset Software GmbH (Vienna, founded 2018; Series A of about EUR 12.7-13M)",
        "Cloud software for product cost and CO2e calculation: target costing, design-to-cost, sourcing",
        "SaaS only",
        "Flexible SaaS pricing by company size, usage and features; quote only",
        "None published",
        "EUR 60k-150k (planning assumption; scale-up SaaS)",
        "EUR 40k-200k (planning assumption)",
        "3-6 months (planning assumption; pilot-first approach described in the Brose story)",
        "Validated market data for 79 countries (materials, machine rates, energy, labour); 50+ calculation modules",
        "No public Teamcenter connector; open API (SAP workflow built by Brose IT on Tset Studio API)",
        "API-first architecture (BMW master-data example); integration to be built per customer",
        "Versioned calculators in Tset Studio; scenario comparison",
        "Yes (target costing and target CO2 are named use cases)",
        "AGCO, Brose, Lego, thyssenkrupp, ZF, BMW Group",
        "Most flexible external option: own Excel logic can be migrated into versioned calculators; API-first",
        "Teamcenter interface to be built; no idea/measure management; manufacturing focus; younger vendor",
        "Medium (venture-funded scale-up, 70-100+ staff)",
        "S31 S32 S33 S34 S35 S36 S37 S38",
    ],
    "CLEO": [
        "Cost Engineering Consultancy (Netherlands)",
        "Capital-project cost estimating, cost control and benchmarking for process/energy/EPC projects",
        "Cloud or on-premises; editions Standard / Professional",
        "Quote only",
        "None published (peer product CostOS is listed from USD 2,800 per user by Capterra)",
        "EUR 40k-100k (placeholder - no price signal found)",
        "EUR 30k-120k (placeholder)",
        "3-6 months (planning assumption)",
        "CESK cost-engineering knowledge bases; location-factor tables; smart cost models",
        "None found (integrations named: SAP, Excel, Power BI, Oracle P6)",
        "Power BI and Excel integration named",
        "Estimate versions and comparison; supports AACE estimating methods incl. factor/parametric (vendor statement)",
        "Budget vs. estimate rather than component target costing",
        "ITER Organization (assembly and installation estimates)",
        "Only shortlisted tool built for TIC: location factors, scaling models, project benchmarking, EPC breakdown structures",
        "No BOM/Teamcenter product costing, no feature mapping, no idea/measure management",
        "Low-medium (specialist vendor)",
        "S39 S40 S41 S42 S43 S44 S53",
    ],
}

# Complementary tools (not stand-alone answers)
COMPLEMENTARY = [
    ("Valuedesk", "Valuedesk GmbH (Bielefeld)", "Savings / measure management",
     "Web platform to capture ideas, run and measure savings measures; dashboards, methods explorer, savings tracker",
     "Packages VD-READY (10 full users, 200 measures, 2 value streams, 1-month term), VD-GROW (20 users, 400 measures, 4 value streams, 12 months), VD-ENTERPRISE; prices on request",
     "Covers R11-R12 out of the box; would need a link to the cost model", "S45 S46 S47 S48"),
    ("Falcon", "Nordantech (Hamburg)", "Measure / transformation tracking",
     "Cloud tool for measure programmes with degree-of-implementation (Haertegrad) reporting and effect-driver views",
     "Third-party price info: EUR 1,250 per month incl. 10 users; +EUR 35 per user/month up to 50 users; +EUR 25 for users 51-100",
     "Covers R12 (tracking); no cost model", "S49 S50"),
    ("costdata", "costdata GmbH (Cologne, founded 1997)", "Benchmark data (and calculation software)",
     "Database with 45M+ data points in 18 segments for 130+ countries: wages, machine rates, material prices, location factors, overheads",
     "Sold as complete package (software + data + training) or as data package only; prices on request",
     "Data package could feed an in-house tool (regional factors, R8/R9) - 'buy data, build tool'", "S51"),
    ("Mendix + Teamcenter Connector", "Siemens (Mendix)", "Low-code platform with native Teamcenter access",
     "Teamcenter Connector / Teamcenter Extension generate domain models and microflows on Teamcenter data",
     "Mendix platform licence required; not part of the Microsoft suite",
     "Alternative in-house platform if the Teamcenter link turns out to be the hard part; breaks the Power Platform link to the LCOH Suite", "S16"),
]

# Long list
LONGLIST = [
    # tool, vendor, category, what it is, relevance, shortlisted
    ("Teamcenter Product Cost Management", "Siemens", "Product cost management (PCM)", "PLM-integrated product costing, should-cost, profitability, CO2e", "High - Teamcenter-native", "Yes"),
    ("aPriori", "aPriori Technologies", "PCM / should-cost", "CAD-driven manufacturing cost simulation", "Medium - manufactured parts only", "Yes"),
    ("FACTON EPC", "FACTON", "PCM / enterprise product costing", "Lifecycle product costing, design-to-cost, quotation", "High - plant-engineering references", "Yes"),
    ("Tset", "Tset Software", "PCM (SaaS)", "Cloud cost and CO2e calculation with own calculators", "Medium-high - flexible, API-first", "Yes"),
    ("Cleopatra Enterprise", "Cost Engineering", "Capital-project / TIC estimating", "Estimating, cost control, benchmarking for capital projects", "High for TIC, scaling, regions", "Yes"),
    ("SAP Product Lifecycle Costing", "SAP", "PCM (ERP-side)", "Early cost calculation on SAP HANA, feeds S/4HANA CO-PC", "Only if the SAP landscape is the cost master", "No"),
    ("costdata", "costdata", "Cost data + calculation", "Benchmark database for 130+ countries and calculation software", "Data source for in-house tool", "Complement"),
    ("4cost-aces", "4cost", "Parametric estimating", "Parametric/lifecycle cost estimating (German vendor)", "Not researched in depth", "No"),
    ("SEER (SEER-H, SEER-MFG)", "Galorath", "Parametric estimating", "Parametric hardware/manufacturing estimation, aerospace/defence heritage", "Low - different use case", "No"),
    ("TruePlanning", "Unison", "Parametric estimating", "Parametric cost models, aerospace/defence heritage", "Low - different use case", "No"),
    ("Aspen Capital Cost Estimator", "AspenTech", "Capital-project / TIC estimating", "Design-based installed-cost models, 5-6 regional bases", "Medium - process-plant TIC only", "No"),
    ("CostOS", "Nomitech", "Capital-project / TIC estimating", "Estimating with BIM/GIS; Capterra lists from USD 2,800 per user", "Medium - alternative to Cleopatra", "No"),
    ("EcoSys", "Hexagon", "Project controls", "Enterprise project cost control and portfolio", "Low - project execution focus", "No"),
    ("DFMA Should Costing", "Boothroyd Dewhurst", "Should-cost", "Design for manufacture/assembly, regional data for 22 countries", "Low - part-level design method", "No"),
    ("Costimator", "MTI Systems", "Manufacturing estimating", "Quote estimating for discrete manufacturing", "Low", "No"),
    ("Valuedesk", "Valuedesk", "Savings / measure management", "Idea capture, measure tracking, savings reporting", "High for R11-R12 only", "Complement"),
    ("Falcon", "Nordantech", "Measure / transformation tracking", "Measure programmes with degree-of-implementation tracking", "Medium for R12 only", "Complement"),
    ("Mendix + Teamcenter Connector", "Siemens", "Low-code platform", "Low-code apps directly on Teamcenter data", "Alternative build platform", "Complement"),
]

# --------------------------------------------------------------------------
# In-house options
# --------------------------------------------------------------------------
INHOUSE_ROWS = [
    "Idea in one sentence",
    "Building blocks",
    "Data storage",
    "Calculation engine",
    "User interface",
    "Teamcenter interface",
    "LCOH Suite link",
    "Versioning",
    "Scenario simulation",
    "Ideas & measures",
    "Licences needed (list prices)",
    "Planning assumption: build effort",
    "Planning assumption: run effort",
    "Time to MVP / full scope",
    "Skills needed",
    "Strengths",
    "Limits",
    "Best used as",
]

INHOUSE = {
    "IHA": [
        "Structure today's Excel cost data, store it in SharePoint, analyse it in Power BI",
        "Excel + Power Query, SharePoint lists/library, Power BI, optional canvas Power App and Forms for idea intake",
        "SharePoint lists and Excel files (flat tables)",
        "Excel formulas, Power Query and DAX measures",
        "Excel for editing, Power BI for analysis, Teams tab",
        "Scheduled/manual BOM and price export (Excel/CSV) from Teamcenter into SharePoint",
        "Shared SharePoint lists or export files read by the LCOH Suite",
        "Dated snapshot files/lists; limited audit trail",
        "Parameter tables (scale exponent, regional factor) in Excel; what-if parameters in Power BI",
        "SharePoint list + form, status column, Power BI tracking",
        "Included in Microsoft 365; Power BI Pro USD 14 per user/month where not already licensed (E5 includes it)",
        "60 dev person-days + 25 SME person-days (range 45-90 / 20-35)",
        "About 35 person-days per year (manual refresh and upkeep)",
        "6-8 weeks / about 3 months",
        "Power BI and Excel power user",
        "Fastest and cheapest; no premium licences; ideal to prove the data model and reports",
        "Not relational, 5,000-item list-view threshold and 2,000-row delegation limit, coarse security, spreadsheet error risk, manual Teamcenter step",
        "Prototype / phase-1 MVP and fallback",
    ],
    "IHB": [
        "A dedicated 'Cost Cockpit' app on the same platform as the LCOH Suite, with a relational cost database",
        "Dataverse, model-driven Power App + custom pages, Power Automate, Power BI (embedded), Dev/Test/Prod with pipelines",
        "Dataverse tables (CBS, cost items, versions, features, scenarios, regions, benchmarks, targets, ideas, measures)",
        "Dataverse calculated/roll-up logic and Power Automate for snapshots; DAX for analysis; scenario results materialised per run",
        "Model-driven app for data and workflow, idea-box page for all colleagues (Teams/mobile), Power BI dashboards",
        "Phase 1 file import; phase 4 custom connector to Teamcenter services via on-premises data gateway or Teamcenter 2606 Power BI integration",
        "Same platform: shared Dataverse tables or a versioned 'CAPEX dataset' table the LCOH Suite reads",
        "Explicit version table (freeze flow), Dataverse auditing at table/column level, version-to-version bridge in Power BI",
        "Scaling rules and regional factors as tables per CBS element; scenario builder; side-by-side comparison",
        "Idea-to-measure workflow with approval, degree-of-implementation levels, prioritisation score, tracking against targets",
        "Power Apps Premium USD 20 per user/month (pay-as-you-go USD 10 per active user/app/month as alternative), Power BI Pro USD 14, Power Automate Premium USD 15 for flow owners",
        "190 dev person-days + 60 SME person-days (range 150-260 / 45-80)",
        "About 50 person-days per year (maintenance and small enhancements)",
        "10-12 weeks / 6-7 months",
        "Power Platform developer (Dataverse, model-driven apps, Power Automate), Power BI developer, Teamcenter key user",
        "Fits all 13 requirements by design; native LCOH link; full control of structure and logic; role-based security and audit; low cash-out",
        "Reference data and benchmarks must be collected; Teamcenter connector must be built; needs premium licences and a named owner",
        "Recommended target solution",
    ],
    "IHC": [
        "A cost data hub in Microsoft Fabric with a code-based scenario engine, Power BI on top",
        "Fabric lakehouse / SQL database, pipelines, notebooks (Python), Power BI incl. translytical task flows for write-back, Power App for master data and ideas",
        "OneLake (Delta tables) / Fabric SQL database",
        "Python / SQL in Fabric notebooks (scaling, regional factors, Monte-Carlo ranges), results stored as tables",
        "Power BI reports with write-back buttons; Power App for workflows",
        "Automated ingestion pipelines from Teamcenter services / exports and ERP",
        "Dataverse 'Link to Microsoft Fabric' (shortcuts) to read LCOH data; results written back via flow or API",
        "Delta-table history plus explicit version tables",
        "Most powerful: batch simulation over many sizes/regions, sensitivity and uncertainty ranges",
        "Needs the Power App layer from option B for a good user experience",
        "Fabric capacity (F2 about USD 263 per month pay-as-you-go, about USD 156 reserved), Power BI Pro for all viewers below F64, Power Apps Premium for app users",
        "320 dev person-days + 70 SME person-days (range 260-420 / 55-90)",
        "About 70 person-days per year",
        "About 4 months / 9-10 months",
        "Data engineer (Fabric, Python/SQL), Power BI developer, Power Platform developer",
        "Scales to ERP actuals and large BOM volumes; strongest simulation; clean analytics architecture",
        "Highest effort and skill demand; more IT involvement; over-sized for a first release",
        "Later evolution of B when data volume or simulation depth requires it",
    ],
}

# --------------------------------------------------------------------------
# TCO model inputs (planning assumptions; EUR unless stated)
# --------------------------------------------------------------------------
TCO_GLOBAL = {
    "core_users": 10,
    "contrib_users": 30,
    "years": 5,
    "fx": 0.90,
    "internal_rate": 800,
    "external_rate": 1100,
}
PRICES_USD = {
    "Power Apps Premium (per user/month)": 20,
    "Power BI Pro (per user/month)": 14,
    "Power Automate Premium (per user/month)": 15,
    "Fabric F2 pay-as-you-go (per month)": 263,
    "Fabric F2 reserved (per month)": 156,
    "Dataverse extra database capacity (per GB/month)": 40,
}
TCO_SCENARIOS = [
    # key, label, [low, base, high] each = (dev PD, external share, SME PD, external services EUR, run PD/yr)
    ("IHA", "In-house A: Lean", [(45, 0, 20, 0, 25), (60, 0, 25, 0, 35), (90, 0, 35, 0, 50)]),
    ("IHB", "In-house B: Power Platform", [(150, .5, 45, 0, 35), (190, .5, 60, 0, 50), (260, .5, 80, 0, 70)]),
    ("IHC", "In-house C: Fabric platform", [(260, .6, 55, 0, 50), (320, .6, 70, 0, 70), (420, .6, 90, 0, 95)]),
    ("EXT", "External PCM suite", [(0, 0, 60, 60000, 20), (0, 0, 90, 150000, 30), (0, 0, 140, 300000, 45)]),
    ("EXTC", "External PCM suite + measure tool + LCOH link", [(30, .5, 70, 60000, 30), (40, .5, 100, 150000, 40), (60, .5, 150, 300000, 55)]),
]
EXT_LICENCE = (60000, 110000, 200000)


def tco():
    g = TCO_GLOBAL
    fx, ir, er, yrs = g["fx"], g["internal_rate"], g["external_rate"], g["years"]
    core, contrib = g["core_users"], g["contrib_users"]
    users = core + contrib
    pa, pbi, pau, f2, f2r, dv = 20, 14, 15, 263, 156, 40
    lic = {
        "IHA": (0, users * pbi * 12 * fx, users * pbi * 12 * fx),
        "IHB": (core * pa * 12 * fx, (users * (pa + pbi) * 12 + 2 * pau * 12) * fx,
                (users * (pa + pbi) * 12 + 2 * pau * 12 + 5 * dv * 12) * fx),
        "IHC": ((f2r * 12 + core * pa * 12) * fx, (2 * f2 * 12 + users * pbi * 12 + core * pa * 12) * fx,
                (4 * f2 * 12 + users * pbi * 12 + users * pa * 12) * fx),
        "EXT": EXT_LICENCE,
    }
    mt = (1250 * 12, (1250 + max(0, users - 10) * 35) * 12, (1250 + max(0, users - 10) * 35) * 12)
    lic["EXTC"] = tuple(EXT_LICENCE[i] + mt[i] for i in range(3))
    out = []
    for key, label, cases in TCO_SCENARIOS:
        row = {"key": key, "label": label, "cases": {}}
        for i, case in enumerate(["low", "base", "high"]):
            dev, sh, sme, ext, run = cases[i]
            one_int = (dev * (1 - sh) + sme) * ir
            one_ext = dev * sh * er + ext
            l5 = lic[key][i] * yrs
            r5 = run * ir * yrs
            row["cases"][case] = {
                "licence_per_year": round(lic[key][i]),
                "oneoff_internal": round(one_int),
                "oneoff_external": round(one_ext),
                "licences_5y": round(l5),
                "run_5y": round(r5),
                "total": round(one_int + one_ext + l5 + r5),
                "cash_out": round(one_ext + l5),
                "internal_effort": round(one_int + r5),
            }
        out.append(row)
    return out


# --------------------------------------------------------------------------
# Roadmap for the recommended in-house path (B, starting lean)
# --------------------------------------------------------------------------
ROADMAP = [
    # phase, name, start week, end week, dev PD, SME PD, goal, work packages, deliverable / gate
    ("0", "Mobilise & decide", 1, 4, 15, 12,
     "Make-or-buy confirmed, scope and data sources clear",
     ["Requirements catalogue with Product gH2 and R&D", "Status-quo tool landscape and data inventory (which Teamcenter attributes hold prices/suppliers, where the LCOH Suite stores data)",
      "Define cost breakdown structure, cost types, scope split (NCA/EPC), TIC categories", "Licence and environment check with IT; RFI to 2-3 vendors for hard numbers",
      "Governance: product owner, developer, key users"],
     "Gate G0: decision paper, requirements catalogue v1, solution design, backlog"),
    ("1", "MVP: cost transparency", 5, 12, 45, 15,
     "One trusted cost baseline that can be sliced and versioned",
     ["Dataverse data model (CBS, cost items, versions) and model-driven app", "Import of the baseline from existing Excel and a Teamcenter export",
      "Tagging by cost type, scope and TIC category", "First release freeze (version 1)",
      "Power BI: cost tree, Pareto of cost drivers, NCA vs. EPC split, version bridge"],
     "Gate G1: MVP in use by the core team; continue / adjust / fall back to external"),
    ("2", "Scenario simulation", 13, 18, 35, 10,
     "Cost for any project size and region at the push of a button",
     ["Scaling rule per CBS element (per module, power law, fixed)", "Regional factor tables per cost category and region",
      "Scenario builder (size, region, feature set, price year)", "Scenario comparison report; calibration against known projects"],
     "Release 2: scenario module; calibration note"),
    ("3", "Targets & cost-down", 19, 24, 40, 13,
     "Targets per component and a managed pipeline of measures",
     ["Benchmark table (own products vs. competitors, public studies)", "Target value per CBS element and gap view",
      "Idea box for all colleagues (Teams/mobile)", "Measure list with degree-of-implementation levels, owner, due date, saving, prioritisation score",
      "Tracking dashboard: target vs. current vs. secured measures"],
     "Release 3: target costing and measure tracking"),
    ("4", "Integrate & industrialise", 25, 30, 35, 10,
     "Automated data flows and a supportable product",
     ["Automated Teamcenter interface (custom connector / services, or Teamcenter Power BI integration)", "LCOH Suite link: versioned CAPEX dataset",
      "Security roles, auditing, Dev/Test/Prod pipelines", "Test cases against legacy Excel, user training, documentation, hand-over to run"],
     "Release 4: go-live for all users; run model agreed"),
]
ROADMAP_OVERHEAD = ("PM, testing, training, documentation (across phases)", 20, 0)

ROLES = [
    ("Sponsor", "Head of department", "Decisions at gates, removes blockers", "2 h per month"),
    ("Product owner", "Product gH2", "Owns requirements, backlog, priorities and acceptance", "0.2-0.3 FTE during build"),
    ("Power Platform developer", "Internal or external", "Data model, app, flows, Power BI, ALM", "about 1.0 FTE during build"),
    ("Cost engineering SMEs", "Product / R&D / Sales Development", "Cost structure, scaling rules, regional factors, test cases", "about 0.2 FTE in total"),
    ("Teamcenter key user / PLM IT", "IT / Engineering", "Export definition, API access, attribute mapping", "10-15 person-days"),
    ("IT / Power Platform CoE", "IT", "Environments, licences, security review, gateway", "5-10 person-days"),
    ("Key users", "Product, R&D, Procurement", "Pilot use, feedback, idea-box roll-out", "1-2 days per release"),
]

# --------------------------------------------------------------------------
# Teamcenter interface routes
# --------------------------------------------------------------------------
TC_ROUTES = [
    ("T1", "File export", "Scheduled or manual export of BOM, prices and suppliers (Excel/CSV/PLM XML) to SharePoint; Power Query or dataflow loads it",
     "Low (days)", "None beyond a Teamcenter key user", "Manual step, no live data, export layout must stay stable", "Phase 1 - start here"),
    ("T2", "Teamcenter Power BI integration", "Teamcenter 2606 ships a Power BI integration with templates for BOMs, programme plans, schedules and search results",
     "Low-medium", "Teamcenter release 2606 or later; licensing to be confirmed with Siemens", "Reporting-oriented; whether prices/supplier attributes are exposed must be tested", "Check availability in phase 0"),
    ("T3", "Service interface via custom connector", "Power Automate custom connector (premium) calls Teamcenter services (JSON over the Active Workspace gateway / SOA services) through the on-premises data gateway",
     "Medium (15-30 person-days)", "Teamcenter service account, API documentation generated for the installed release, IT security approval", "No single universal REST API for core Teamcenter data; depends on the installed version and customisations", "Phase 4 target"),
    ("T4", "Middleware / gateway product", "Existing integration middleware (e.g. Teamcenter Gateway products or the ERP interface) also delivers to Dataverse / Fabric",
     "Medium-high", "Middleware already licensed and operated by IT", "Dependency on the IT integration roadmap", "Only if already in place"),
    ("T5", "Via Teamcenter PCM", "If Teamcenter PCM is licensed, its own OpenAPI REST interface exposes calculations and KPIs",
     "Low-medium", "Teamcenter PCM licence", "Only relevant in a hybrid scenario", "Option for a later hybrid"),
]

# --------------------------------------------------------------------------
# Risks
# --------------------------------------------------------------------------
RISKS = [
    # scope, risk, impact, likelihood, mitigation
    ("In-house", "Key-person dependency on the developer", "High", "Medium", "Two trained makers, managed solutions in Dev/Test/Prod, documentation, IT CoE involved from phase 0"),
    ("In-house", "Scope creep - tool becomes as large as the LCOH Suite", "Medium", "High", "Separate app on a shared data backbone, MVP-first, backlog owned by one product owner, gate after each phase"),
    ("In-house", "Teamcenter does not hold clean prices/suppliers", "High", "Medium", "Data inventory in phase 0, price source and confidence flag per cost item, named data owners"),
    ("In-house", "No shipped reference data (regional factors, benchmarks)", "Medium", "High", "Start with public studies and own projects; buy a data package (e.g. costdata) if needed"),
    ("In-house", "Teamcenter API access delayed by IT security", "Medium", "Medium", "Start with file export (T1), clarify API route in parallel, test Teamcenter 2606 Power BI integration"),
    ("In-house", "Premium licences needed for every app user", "Low", "Medium", "Licence check in phase 0; pay-as-you-go for occasional users; Power BI for read-only audiences"),
    ("In-house", "Self-built calculation logic contains errors", "High", "Medium", "Test cases against legacy Excel, peer review of formulas, version-locked scaling rules"),
    ("In-house", "No budget for maintenance after go-live", "Medium", "Medium", "Agree run budget (about 0.25 FTE) at gate G0; quarterly release rhythm"),
    ("External", "Functional mismatch - tools are built for part-level should-costing", "High", "High", "Scripted demo on own data before contract (feature-to-TIC, scaling, EPC scope)"),
    ("External", "Second tool and custom integration still needed for ideas/measures and LCOH", "Medium", "High", "Include integration scope and third-party tools in the vendor comparison"),
    ("External", "High recurring cash-out for a small user group", "Medium", "High", "Negotiate user tiers; check group frame agreements"),
    ("External", "Vendor lock-in for cost logic and data", "Medium", "Medium", "Contractual data export, API access, exit clause"),
    ("External", "Selection and procurement add months before any value", "Medium", "High", "Run RFI in parallel to the in-house MVP"),
]

# --------------------------------------------------------------------------
# Open questions and RFI questions
# --------------------------------------------------------------------------
OPEN_QUESTIONS = [
    ("Internal", "Where exactly are prices and supplier data maintained today - Teamcenter attributes, ERP, Excel?", "PLM IT / Procurement"),
    ("Internal", "Which Teamcenter release is installed, is Active Workspace in use, and is the 2606 Power BI integration available?", "PLM IT"),
    ("Internal", "Where does the LCOH Suite store its data (Dataverse, SharePoint, SQL) and who maintains it?", "LCOH Suite owner"),
    ("Internal", "Which Microsoft licences exist (M365 E3/E5, Power Apps Premium, Fabric capacity)?", "IT licensing"),
    ("Internal", "Do group-level frame agreements exist with a shortlisted vendor (Siemens PCM licences, SAP, others)?", "IT / Procurement"),
    ("Internal", "How many users: editors, contributors of ideas, read-only management?", "Product gH2"),
    ("Internal", "Which cost breakdown structure is the reference (existing TIC structure, LCOH Suite structure)?", "Product gH2 / R&D"),
    ("Internal", "Is developer capacity available internally, or is an external Power Platform partner needed?", "Head of department / IT"),
    ("Internal", "Data classification: may cost data be stored in Dataverse / a vendor cloud?", "IT security"),
    ("Vendor RFI", "Licence price for 10 editors + 30 contributors/viewers, 3- and 5-year terms; price per additional user", "All vendors"),
    ("Vendor RFI", "Fixed-price implementation offer incl. Teamcenter interface; duration in weeks to first productive use", "All vendors"),
    ("Vendor RFI", "Show on our sample data: split by cost type and NCA/EPC scope, engineering hours as cost items", "All vendors"),
    ("Vendor RFI", "How are plant-size scaling and regional construction factors modelled?", "All vendors"),
    ("Vendor RFI", "How are ideas, measures and target tracking supported - natively or via partner tool?", "All vendors"),
    ("Vendor RFI", "API to push results into a Power Apps / Dataverse application; Power BI connector", "All vendors"),
    ("Vendor RFI", "Reference customers in plant engineering / energy / hydrogen; hosting location and certifications", "All vendors"),
    ("Vendor RFI", "Is the Teamcenter connector a standard product (which Teamcenter versions) or a project?", "FACTON, Tset, Cleopatra"),
]

# --------------------------------------------------------------------------
# Public hydrogen cost references (useful for benchmarking / calibration)
# --------------------------------------------------------------------------
H2_BENCHMARKS = [
    ("Installed electrolyser cost outside China, 2024", "USD 2,000-2,600 per kW", "IEA figures as reported by secondary sources - verify in IEA Global Hydrogen Review", "S82"),
    ("Chinese electrolyser built and installed in China, 2024", "USD 600-1,200 per kW", "IEA figures as reported by secondary sources", "S82"),
    ("System cost China-made vs. Europe/US-made", "about USD 600 per kW vs. about USD 2,500 per kW", "BNEF as reported by FuelCellChina", "S80"),
    ("Alkaline full system outside China, 2025", "slightly above USD 2.0M per MW; China 50-60% lower", "CRU", "S75"),
    ("Installed cost, standard European / North American plants", "USD 2,300 per kW (alkaline), USD 2,550 per kW (PEM)", "Electric Hydrogen white paper, Dec 2024", "S76"),
    ("Stack share of direct CAPEX", "20-50% of direct CAPEX in large PEM/ALK projects", "World Bank technical report", "S74"),
    ("1 GW plant total installed cost (2020 baseline design)", "EUR 1,400 per kW alkaline, EUR 1,800 per kW PEM", "ISPT Gigawatt green hydrogen plant (2020)", "S77"),
    ("1 GW advanced design", "EUR 730 per kW", "ISPT advanced design report (2022); technology/year basis to be checked", "S78"),
    ("PEM balance-of-plant scaling", "USD 848 per kW at 1 MW to USD 87 per kW at 1 GW; most of the gain is reached by about 100 MW", "OSTI / journal article on BoP scale-up", "S79"),
]

# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------
SOURCES = [
    ("S1", "Siemens blog - What's new in Teamcenter Product Cost Management 2606", "https://blogs.sw.siemens.com/teamcenter/teamcenter-product-cost-management-whats-new-in-version-2606/", "Vendor"),
    ("S2", "Kaizen PLM - What's new in Teamcenter Product Cost Management 2606", "https://www.kaizenplm.ie/post/what-s-new-in-version-2606-teamcenter-product-cost-management", "Partner"),
    ("S3", "Siemens blog - Teamcenter Product Cost Management 2506", "https://blogs.sw.siemens.com/teamcenter/teamcenter-product-cost-management-whats-new-in-version-2506/", "Vendor"),
    ("S4", "Siemens blog - Teamcenter Product Cost Management 2512", "https://blogs.sw.siemens.com/teamcenter/whats-new-in-teamcenter-product-cost-management-version-2512/", "Vendor"),
    ("S5", "Siemens blog - Teamcenter Product Cost Management what's new series (knowledge base figures for 9.3 and 2406)", "https://blogs.sw.siemens.com/teamcenter/teamcenter-product-cost-management-whats-new/", "Vendor"),
    ("S6", "Siemens fact sheet - Teamcenter product costing", "https://www.plm.automation.siemens.com/en_us/Images/Siemens-PLM-Teamcenter-Product-Costing-fs_tcm1023-204012.pdf", "Vendor"),
    ("S7", "Siemens fact sheet - Teamcenter X Product Cost Management", "https://resources.sw.siemens.com/en-US/fact-sheet-reduce-costs-and-carbon-footprint-with-teamcenter-x-product-cost-management/", "Vendor"),
    ("S8", "Siemens blog - Introducing Teamcenter 2606", "https://blogs.sw.siemens.com/teamcenter/teamcenter-2606/", "Vendor"),
    ("S9", "Siemens blog - Power BI integration for actionable analytics in Teamcenter", "https://blogs.sw.siemens.com/teamcenter/power-bi-integration-teamcenter/", "Vendor"),
    ("S10", "Emixa - Teamcenter 2606 release guide", "https://www.emixa.com/blog/teamcenter-2606-release-guide", "Partner"),
    ("S11", "Siemens blog - 2026 Teamcenter beta testing event", "https://blogs.sw.siemens.com/teamcenter/plm-teamcenter-beta-event/", "Vendor"),
    ("S12", "PROLIM - Identifying and specifying target costs with Teamcenter PCM", "https://www.prolim.com/identifying-and-specifying-target-costs-with-teamcenter/", "Partner"),
    ("S13", "G2 - Teamcenter pricing; AWS Marketplace - Teamcenter X", "https://www.g2.com/products/teamcenter/pricing", "Third party"),
    ("S14", "Leo AI blog - The Teamcenter API: what it gives engineering teams", "https://www.getleo.ai/blog/teamcenter-api-what-you-can-get", "Third party"),
    ("S15", "Siemens community - guides for getting started with the REST API", "https://community.sw.siemens.com/s/question/0D5Vb00000auM4fKAE/are-there-any-guides-for-getting-started-with-the-rest-api", "Community"),
    ("S16", "Mendix docs - Teamcenter Extension / Connector", "https://docs.mendix.com/appstore/modules/siemens-plm/teamcenter-extension", "Vendor"),
    ("S17", "aPriori - Pricing & packaging", "https://www.apriori.com/pricing/", "Vendor"),
    ("S18", "aPriori - FAQs", "https://www.apriori.com/faqs/", "Vendor"),
    ("S19", "G2 - aPriori pricing and implementation statistics", "https://www.g2.com/products/apriori-manufacturing-intelligence-platform/pricing", "Third party"),
    ("S20", "Software Finder - aPriori pricing estimates", "https://softwarefinder.com/manufacturing-software/apriori", "Third party"),
    ("S21", "Emithran - Should-cost analysis software compared (2026)", "https://www.emithran.com/blog/should-cost-analysis-software-comparison", "Third party"),
    ("S22", "Forrester - Total Economic Impact of aPriori (2022, commissioned by aPriori)", "https://www.apriori.com/wp-content/uploads/2022/11/Forrester-Total-Economic-Impact-of-aPriori-Nov-8-2022-FINAL.pdf", "Analyst (commissioned)"),
    ("S23", "aPriori - Product modules overview, cloud solution (2022 datasheet)", "https://www.apriori.com/wp-content/uploads/2022/08/aPriori-Product-Modules-Overview-Cloud-Solution-DS-062922-V14.pdf", "Vendor"),
    ("S24", "FACTON - Cost management software overview", "https://www.facton.com/software", "Vendor"),
    ("S25", "FACTON - Services", "https://www.facton.com/services", "Vendor"),
    ("S26", "FitGap - FACTON EPC Suite profile", "https://us.fitgap.com/products/036767/facton-epc-suite", "Third party"),
    ("S27", "SoftGuide - FACTON EPC", "https://www.softguide.com/program/facton", "Third party"),
    ("S28", "PRWeb - FACTON introduces EPC Should Costing SaaS in the cloud (2016)", "https://www.prweb.com/releases/facton_introduces_epc_should_costing_saas_solution_in_the_cloud/prweb13570922.htm", "Vendor"),
    ("S29", "Microsoft Marketplace - FACTON EPC Should Costing", "https://marketplace.microsoft.com/en-us/product/factongmbh1583248282207.facton_epc_sc?tab=overview", "Marketplace"),
    ("S30", "Capterra - FACTON EPC", "https://www.capterra.com/p/161502/Facton-EPC-Suite/", "Third party"),
    ("S31", "Tset - Product page cost & carbon", "https://tset.com/product/cost-carbon", "Vendor"),
    ("S32", "Tset - About", "https://tset.com/about", "Vendor"),
    ("S33", "Tset - Series A announcement", "https://tset.com/press-and-news/series-a-funding-tset", "Vendor"),
    ("S34", "Vestbee - Tset raises EUR 12.7M", "https://www.vestbee.com/insights/articles/tset-raises-12-7-m", "Press"),
    ("S35", "Tset - Customer story Brose", "https://tset.com/customer-stories/brose", "Vendor"),
    ("S36", "Tset - API-first architecture for cost engineering master data with BMW Group", "https://tset.com/blog/bmw-group-cost-engineering-api-first-approach", "Vendor"),
    ("S37", "Tset - FAQ", "https://tset.com/faq", "Vendor"),
    ("S38", "Tset - Automotive industry page", "https://tset.com/industries/automotive", "Vendor"),
    ("S39", "Cleopatra Enterprise - Cost estimating software", "https://cleopatraenterprise.com/cost-estimating-software-2/", "Vendor"),
    ("S40", "Cleopatra Enterprise - Cost estimating brochure (2025)", "https://cleopatraenterprise.com/wp-content/uploads/2025/04/Cost-estimating-software-brochure.pdf", "Vendor"),
    ("S41", "Cleopatra Enterprise - Cost management software", "https://cleopatraenterprise.com/cost-management-software/", "Vendor"),
    ("S42", "Cleopatra Enterprise - Power industry page", "https://cleopatraenterprise.com/industries/cleopatra-enterprise-for-power/", "Vendor"),
    ("S43", "SaaSrat - Cleopatra Enterprise review 2026", "https://saasrat.com/products/cleopatra-enterprise", "Third party"),
    ("S44", "Cleopatra Enterprise - Managing project costs with metrics and benchmarking", "https://cleopatraenterprise.com/blog/managing-project-costs-with-metrics-and-benchmarking/", "Vendor"),
    ("S45", "Valuedesk - Prices & packages", "https://www.valuedesk.de/en/software/preise/", "Vendor"),
    ("S46", "Valuedesk - Cost cutting solution", "https://www.valuedesk.de/en/loesungen/cost-cutting/", "Vendor"),
    ("S47", "Westfalen-Blatt - Der Kosten-Optimierer (Valuedesk)", "https://www.westfalen-blatt.de/owl/bielefeld/der-kosten-optimierer-1153769", "Press"),
    ("S48", "IHC OWL - Hinter den Kulissen von Valuedesk", "https://www.ihc-owl.de/hinter-den-kulissen-von-valuedesk-gmbh/", "Press"),
    ("S49", "trusted.de - Falcon (Nordantech) review and prices", "https://trusted.de/falcon", "Third party"),
    ("S50", "Capterra - Falcon reviews", "https://www.capterra.com/p/210024/Falcon/reviews/", "Third party"),
    ("S51", "costdata - Market data", "https://www.costdata.de/en/data", "Vendor"),
    ("S52", "AspenTech - Economic evaluation family brochure (ACCE)", "https://www.aspentech.com/-/media/aspentech/home/resources/brochure/pdfs/fy23/q3/at-08059-new-economic-evaluation-family-brochure_0123.pdf", "Vendor"),
    ("S53", "Capterra UK - CostOS Estimating", "https://www.capterra.co.uk/software/52188/costos-estimating", "Third party"),
    ("S54", "SAP Community - Deep dive into SAP Product Lifecycle Costing", "https://community.sap.com/t5/product-lifecycle-management-blog-posts-by-sap/secure-profits-with-early-design-cost-control-a-deep-dive-into-sap-product/ba-p/14451316", "Vendor"),
    ("S55", "TrustRadius - Product cost management category", "https://www.trustradius.com/categories/product-cost-management", "Third party"),
    ("S56", "ERP Research - Implementation cost breakdown (services vs. licence rule of thumb)", "https://www.erpresearch.com/en-us/erp-implementation-cost-breakdown", "Third party"),
    ("S57", "Microsoft Learn - Pipelines in Power Platform", "https://learn.microsoft.com/power-platform/alm/pipelines", "Microsoft"),
    ("S58", "Microsoft Learn - Understand translytical task flows", "https://learn.microsoft.com/en-us/power-bi/create-reports/translytical-task-flow-overview", "Microsoft"),
    ("S59", "Microsoft Learn - Configure Dataverse auditing", "https://learn.microsoft.com/power-apps/developer/data-platform/auditing/configure", "Microsoft"),
    ("S60", "Microsoft Learn - Dataverse long-term data retention", "https://learn.microsoft.com/power-apps/developer/data-platform/long-term-retention", "Microsoft"),
    ("S61", "Microsoft Learn - Link Dataverse to Microsoft Fabric", "https://learn.microsoft.com/en-us/training/modules/link-dataverse-fabric/synchronize-data", "Microsoft"),
    ("S62", "Superblocks - Power Apps pricing 2026", "https://www.superblocks.com/blog/powerapps-pricing", "Third party"),
    ("S63", "SAMexpert - Power Apps per-app plan retired", "https://samexpert.com/power-apps-per-app-plan-retired/", "Third party"),
    ("S64", "Redress Compliance - Power Platform licensing 2026", "https://redresscompliance.com/microsoft-power-platform-licensing-complete", "Third party"),
    ("S65", "EPC Group - Power BI pricing and licensing 2026", "https://www.epcgroup.net/insights/power-bi-pricing-licensing-2026", "Third party"),
    ("S66", "Embeddable - Power BI pricing 2026", "https://embeddable.com/blog/power-bi-pricing", "Third party"),
    ("S67", "Forrester - Total Economic Impact of Microsoft Power Apps (commissioned by Microsoft)", "https://tei.forrester.com/go/microsoft/powerappstei/?lang=en-us", "Analyst (commissioned)"),
    ("S68", "Microsoft Power Platform blog - feature updates April and September 2026", "https://microsoft.com/en-us/power-platform/blog/power-apps/whats-new-in-power-platform-september-2026-feature-update", "Microsoft"),
    ("S69", "Microsoft Learn - Create a custom connector from scratch", "https://learn.microsoft.com/en-us/connectors/custom-connectors/define-blank", "Microsoft"),
    ("S70", "m365.fm - Why SharePoint is not a database for Power Apps", "https://www.m365.fm/blog/why-sharepoint-is-not-a-database-for-power-apps--and-what-to-use-instead/", "Community"),
    ("S71", "Panko - What we know about spreadsheet errors (arXiv 0804.0941)", "https://arxiv.org/pdf/0804.0941.pdf", "Academic"),
    ("S72", "Microsoft - Copilot Studio pricing", "https://www.microsoft.com/copilot/microsoft-copilot-studio", "Microsoft"),
    ("S73", "Atlan - Translytical task flows (2026 status)", "https://atlan.com/know/microsoft-fabric/translytical-task-flows/", "Third party"),
    ("S74", "World Bank - Technical report on electrolyser technical and economic characteristics", "https://documents1.worldbank.org/curated/en/099022326123011297/pdf/P506220-b45b0865-8706-4862-8792-d8cc71f84569.pdf", "Public study"),
    ("S75", "CRU - Chinese green hydrogen has cost benefits but challenges are emerging (2025)", "https://www.crugroup.com/en/communities/thought-leadership/2025/chinese-green-hydrogen-has-cost-benefits-but-challenges-are-emerging/", "Analyst"),
    ("S76", "Electric Hydrogen - PEM vs. alkaline white paper (Dec 2024)", "https://eh2.com/wp-content/uploads/2025/01/Final_PEM_vs_Alkaline_December_2024_Whitepaper.pdf", "Vendor study"),
    ("S77", "ISPT - Gigawatt green hydrogen plant, public report (2020)", "https://ispt.eu/media/ISPT-public-report-gigawatt-green-hydrogen-plant.pdf", "Public study"),
    ("S78", "ISPT - A one-gigawatt green-hydrogen plant, advanced design (2022)", "https://ispt.eu/media/Public-report-gigawatt-advanced-green-electrolyser-design.pdf", "Public study"),
    ("S79", "OSTI - Cost estimation of balance-of-plant equipment scale-up for PEM electrolyser systems", "https://www.osti.gov/pages/biblio/3376750-cost-estimation-balance-plant-equipment-scale-up-proton-exchange-membrane-water-electrolyzer-systems", "Academic"),
    ("S80", "FuelCellChina - BNEF: cost of electrolysers is rising instead of falling", "https://www.fuelcellchina.com/Industry_information_details/3725.html", "Press"),
    ("S81", "Intratec - Plant location factors methodology", "https://methodology.intratec.us/industry-economics/location-factors/", "Data provider"),
    ("S82", "Secondary reporting of IEA Global Hydrogen Review cost figures (verify against the IEA report)", "https://www.hyzenergy.com/blog/chinese-electrolyzer-cost-vs-western", "Secondary"),
]

CONTENT = {
    "requirements": REQUIREMENTS,
    "solutions": SOLUTIONS,
    "fit": FIT,
    "fit_rationale": FIT_RATIONALE,
    "criteria": CRITERIA,
    "scores": SCORES,
    "ext_kpi_rows": EXT_KPI_ROWS,
    "ext_kpis": EXT_KPIS,
    "complementary": COMPLEMENTARY,
    "longlist": LONGLIST,
    "inhouse_rows": INHOUSE_ROWS,
    "inhouse": INHOUSE,
    "tco_global": TCO_GLOBAL,
    "prices_usd": PRICES_USD,
    "tco": tco(),
    "roadmap": ROADMAP,
    "roadmap_overhead": ROADMAP_OVERHEAD,
    "roles": ROLES,
    "tc_routes": TC_ROUTES,
    "risks": RISKS,
    "open_questions": OPEN_QUESTIONS,
    "h2_benchmarks": H2_BENCHMARKS,
    "sources": SOURCES,
}


def weighted_scores():
    """Return {solution_key: (c1, total)} using the same maths as the workbook."""
    out = {}
    for idx, (key, *_rest) in enumerate(SOLUTIONS):
        c1 = sum(FIT[key]) / (3 * len(REQUIREMENTS)) * 5
        total = CRITERIA[0][2] * c1
        for cid, _name, w, _d in CRITERIA[1:]:
            total += w * SCORES[cid][idx]
        out[key] = (round(c1, 2), round(total, 2))
    return out


CONTENT["weighted"] = weighted_scores()

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "content.json"), "w", encoding="utf-8") as fh:
        json.dump(CONTENT, fh, indent=1, ensure_ascii=False)
    for k, v in CONTENT["weighted"].items():
        print(k, v)
    for row in CONTENT["tco"]:
        print(row["label"], row["cases"]["base"]["total"], row["cases"]["low"]["total"], row["cases"]["high"]["total"])
