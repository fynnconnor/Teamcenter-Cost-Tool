# Data dictionary

Generated from `schema/cost_cockpit.schema.json` by `scripts/build_artifacts.py`. Do not edit by hand.

Publisher prefix `cdt` · solution `CostCockpit` · 20 tables · 18 global choices.

Use this file in two ways: as reference while building apps, flows and reports, and as the specification if you create the tables by hand in the maker portal instead of running the provisioning script.

## Tables at a glance

| Table | Logical name | Purpose | Serves |
|---|---|---|---|
| Product | `cdt_product` | Product or plant configuration whose cost is monitored. | R1 |
| CBS Element | `cdt_cbselement` | Node of the cost breakdown structure. Carries scope, TIC category and the scaling rule. | R1 R2 R7 |
| Supplier | `cdt_supplier` | Supplier master, fed from Teamcenter. | R5 |
| FX Rate | `cdt_fxrate` | Exchange rate to EUR per currency; copied onto cost items at import. | R1 |
| Cost Version | `cdt_costversion` | Version of the cost baseline of a product. Draft versions are edited, released versions are frozen. | R6 |
| Cost Item | `cdt_costitem` | Lowest cost level: one priced item, hour block or lump sum within a cost version. | R1 R2 R4 R5 |
| Feature | `cdt_feature` | Product feature or design option whose cost effect is tracked. | R3 |
| Feature Impact | `cdt_featureimpact` | Effect of a feature on one CBS element: the feature-to-TIC dependency. | R3 |
| Region | `cdt_region` | Project location for regional cost factors. | R8 |
| Regional Factor | `cdt_regionalfactor` | Cost factor of a region for one cost type, relative to the base region (1.0). | R8 |
| Scenario | `cdt_scenario` | What-if case: a cost version calculated for a project size, a region and a set of features. | R7 R8 R13 |
| Scenario Feature | `cdt_scenariofeature` | Feature selected in a scenario. | R3 R7 |
| Scenario Line | `cdt_scenarioline` | Result line of a scenario per CBS element and cost type. Inputs are written by the flow, results are formula columns. | R7 R8 |
| CAPEX Dataset | `cdt_capexdataset` | Published scenario result per scope and TIC category. This is the interface table the LCOH Suite reads. | R13 |
| Benchmark | `cdt_benchmark` | Cost data point of an own product, a competitor or a public study. | R9 |
| Target | `cdt_target` | Target value per CBS element. | R10 |
| Idea | `cdt_idea` | Cost-down idea submitted by a colleague. | R11 |
| Measure | `cdt_measure` | Cost-down measure with owner, saving, effort and degree of implementation. | R12 |
| Teamcenter Mapping | `cdt_tcmapping` | Remembers which CBS element and cost type a Teamcenter item belongs to, so that re-imports are mapped automatically. | R5 |
| Teamcenter Import Row | `cdt_tcimportrow` | Staging table for rows exported from Teamcenter before they become cost items. | R5 |

## Product

Logical name `cdt_product` · plural *Products* · ownership UserOwned.

Product or plant configuration whose cost is monitored.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (30) | Yes | Short unique code, e.g. DEMO. Used as key for imports. |
| Description | `cdt_description` | Multiline text | No |  |
| Reference size (MW) | `cdt_referencesizemw` | Decimal (2 decimals) | Yes | Project size the cost baseline refers to. |
| Module size (MW) | `cdt_modulesizemw` | Decimal (2 decimals) | Yes | Size of one product module; used by the per-module scaling rule. |
| Technology | `cdt_technology` | Text (100) | No |  |
| Active | `cdt_active` | Yes/No | No |  |

Alternate keys: **Product code** on `cdt_code`.

## CBS Element

Logical name `cdt_cbselement` · plural *CBS Elements* · ownership UserOwned.

Node of the cost breakdown structure. Carries scope, TIC category and the scaling rule.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (50) | Yes | Unique code incl. product prefix, e.g. DEMO-2.1. No / : ? & characters. |
| Level | `cdt_level` | Whole number | Yes | 1 = top level. |
| Scope | `cdt_scope` | Choice: Scope | No | NCA scope, EPC scope or owner. Set on leaf elements. |
| TIC category | `cdt_ticcategory` | Choice: TIC category | No | Category for total-installed-cost reporting. |
| Scaling method | `cdt_scalingmethod` | Choice: Scaling method | No | How the cost of this element changes with project size. |
| Scaling exponent | `cdt_scalingexponent` | Decimal (3 decimals) | No | Exponent n of the power law; only used with scaling method 'Power law'. |
| Is leaf | `cdt_isleaf` | Yes/No | No | Cost items may only be booked on leaf elements. |
| Sort order | `cdt_sortorder` | Whole number | No |  |
| Responsible | `cdt_responsible` | Text (100) | No | Name of the person responsible for this cost element. |
| Comment | `cdt_comment` | Multiline text | No |  |
| Product | `cdt_product` | Lookup to `cdt_product` | Yes | On delete of the parent: Restrict. Navigation property `cdt_Product`. |
| Parent element | `cdt_parent` | Lookup to `cdt_cbselement` | No | On delete of the parent: Restrict. Navigation property `cdt_Parent`. |

Alternate keys: **CBS code** on `cdt_code`.

## Supplier

Logical name `cdt_supplier` · plural *Suppliers* · ownership UserOwned.

Supplier master, fed from Teamcenter.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Teamcenter ID | `cdt_teamcenterid` | Text (60) | Yes | Vendor ID in Teamcenter. |
| Country | `cdt_country` | Text (60) | No |  |

Alternate keys: **Supplier Teamcenter ID** on `cdt_teamcenterid`.

## FX Rate

Logical name `cdt_fxrate` · plural *FX Rates* · ownership OrganizationOwned.

Exchange rate to EUR per currency; copied onto cost items at import.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Currency code | `cdt_name` | Text (10), primary name | Yes | |
| Rate to EUR | `cdt_ratetoeur` | Decimal (6 decimals) | Yes | 1 unit of the currency = x EUR. |
| Valid from | `cdt_validfrom` | Date only | No |  |

Alternate keys: **Currency code** on `cdt_name`.

## Cost Version

Logical name `cdt_costversion` · plural *Cost Versions* · ownership UserOwned.

Version of the cost baseline of a product. Draft versions are edited, released versions are frozen.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (50) | Yes | Unique code, e.g. DEMO-V001. |
| Version number | `cdt_versionnumber` | Whole number | Yes |  |
| Status | `cdt_status` | Choice: Version status | Yes |  |
| Released on | `cdt_releasedon` | Date only | No |  |
| Is baseline | `cdt_isbaseline` | Yes/No | No | Marks the version that targets and measures refer to. |
| Price year | `cdt_priceyear` | Whole number | No |  |
| Release requested | `cdt_releaserequested` | Yes/No | No | Set to Yes to start the release flow. |
| Comment | `cdt_comment` | Multiline text | No |  |
| Product | `cdt_product` | Lookup to `cdt_product` | Yes | On delete of the parent: Restrict. Navigation property `cdt_Product`. |
| Based on version | `cdt_basedon` | Lookup to `cdt_costversion` | No | On delete of the parent: RemoveLink. Navigation property `cdt_BasedOn`. |

Alternate keys: **Version code** on `cdt_code`.

## Cost Item

Logical name `cdt_costitem` · plural *Cost Items* · ownership UserOwned.

Lowest cost level: one priced item, hour block or lump sum within a cost version.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Description | `cdt_name` | Text (300), primary name | Yes | |
| Import key | `cdt_importkey` | Text (200) | Yes | Unique key: version code + '~' + CBS code + '~' + item id. Used for upsert. |
| Cost type | `cdt_costtype` | Choice: Cost type | Yes |  |
| Teamcenter item ID | `cdt_teamcenteritemid` | Text (100) | No |  |
| Teamcenter revision | `cdt_teamcenterrevision` | Text (20) | No |  |
| Quantity | `cdt_quantity` | Decimal (4 decimals) | Yes | Pieces, hours, lots ... |
| Unit | `cdt_unit` | Text (20) | No |  |
| Unit price | `cdt_unitprice` | Decimal (4 decimals) | Yes | In the currency given by currency code. |
| Currency code | `cdt_currencycode` | Text (3) | No | ISO code, e.g. EUR. |
| FX rate to EUR | `cdt_fxrate` | Decimal (6 decimals) | No | Copied from the FX rate table at import. Blank is treated as 1. |
| Amount (EUR) | `cdt_amounteur` | Decimal (2 decimals) | No | Quantity x unit price x FX rate. Written by import and by the flow 'Cost item - set amount'. |
| Price source | `cdt_pricesource` | Choice: Price source | No |  |
| Price date | `cdt_pricedate` | Date only | No |  |
| Confidence | `cdt_confidence` | Choice: Confidence | No |  |
| Make or buy | `cdt_makebuy` | Choice: Make or buy | No |  |
| Comment | `cdt_comment` | Multiline text | No |  |
| Cost version | `cdt_costversion` | Lookup to `cdt_costversion` | Yes | On delete of the parent: Cascade. Navigation property `cdt_CostVersion`. |
| CBS element | `cdt_cbselement` | Lookup to `cdt_cbselement` | Yes | On delete of the parent: Restrict. Navigation property `cdt_CBSElement`. |
| Supplier | `cdt_supplier` | Lookup to `cdt_supplier` | No | On delete of the parent: RemoveLink. Navigation property `cdt_Supplier`. |

Alternate keys: **Cost item import key** on `cdt_importkey`.

## Feature

Logical name `cdt_feature` · plural *Features* · ownership UserOwned.

Product feature or design option whose cost effect is tracked.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (50) | Yes |  |
| Description | `cdt_description` | Multiline text | No |  |
| Category | `cdt_category` | Text (100) | No |  |
| Is standard | `cdt_isstandard` | Yes/No | No | Standard features are part of the baseline. |
| Product | `cdt_product` | Lookup to `cdt_product` | Yes | On delete of the parent: Restrict. Navigation property `cdt_Product`. |

Alternate keys: **Feature code** on `cdt_code`.

## Feature Impact

Logical name `cdt_featureimpact` · plural *Feature Impacts* · ownership UserOwned.

Effect of a feature on one CBS element: the feature-to-TIC dependency.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (100) | Yes |  |
| Impact type | `cdt_impacttype` | Choice: Impact type | Yes |  |
| Value | `cdt_value` | Decimal (4 decimals) | Yes | EUR, EUR per MW or percent, depending on impact type. Negative values are savings. |
| Cost type | `cdt_costtype` | Choice: Cost type | Yes | Cost type of the effect; decides which regional factor applies. |
| Comment | `cdt_comment` | Multiline text | No |  |
| Feature | `cdt_feature` | Lookup to `cdt_feature` | Yes | On delete of the parent: Cascade. Navigation property `cdt_Feature`. |
| CBS element | `cdt_cbselement` | Lookup to `cdt_cbselement` | Yes | On delete of the parent: Restrict. Navigation property `cdt_CBSElement`. |

Alternate keys: **Feature impact code** on `cdt_code`.

## Region

Logical name `cdt_region` · plural *Regions* · ownership UserOwned.

Project location for regional cost factors.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (30) | Yes |  |
| Country | `cdt_country` | Text (60) | No |  |
| Comment | `cdt_comment` | Multiline text | No |  |

Alternate keys: **Region code** on `cdt_code`.

## Regional Factor

Logical name `cdt_regionalfactor` · plural *Regional Factors* · ownership UserOwned.

Cost factor of a region for one cost type, relative to the base region (1.0).

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (60) | Yes | Region code + '~' + cost type number. |
| Cost type | `cdt_costtype` | Choice: Cost type | Yes |  |
| Factor | `cdt_factor` | Decimal (3 decimals) | Yes | 1.000 = same cost as base region. |
| Source | `cdt_source` | Text (300) | No |  |
| Valid from | `cdt_validfrom` | Date only | No |  |
| Region | `cdt_region` | Lookup to `cdt_region` | Yes | On delete of the parent: Cascade. Navigation property `cdt_Region`. |

Alternate keys: **Regional factor code** on `cdt_code`.

## Scenario

Logical name `cdt_scenario` · plural *Scenarios* · ownership UserOwned.

What-if case: a cost version calculated for a project size, a region and a set of features.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (50) | Yes |  |
| Project size (MW) | `cdt_sizemw` | Decimal (2 decimals) | Yes |  |
| Reference size (MW) | `cdt_referencesizemw` | Decimal (2 decimals) | No | Copied from the product by the calculation flow. |
| Module size (MW) | `cdt_modulesizemw` | Decimal (2 decimals) | No | Copied from the product by the calculation flow. |
| Escalation factor | `cdt_escalationfactor` | Decimal (4 decimals) | No | Price-year adjustment; blank is treated as 1. |
| Status | `cdt_status` | Choice: Scenario status | No |  |
| Calculation requested | `cdt_calcrequested` | Yes/No | No | Set to Yes to start the calculation flow. |
| Publication requested | `cdt_publishrequested` | Yes/No | No | Set to Yes to publish the CAPEX dataset for the LCOH Suite. |
| Calculated on | `cdt_calculatedon` | Date and time | No |  |
| Total cost (EUR) | `cdt_totaleur` | Decimal (2 decimals) | No | Written by the calculation flow. |
| Total cost (EUR/kW) | `cdt_totalperkw` | Decimal (2 decimals) | No | Written by the calculation flow. |
| Comment | `cdt_comment` | Multiline text | No |  |
| Product | `cdt_product` | Lookup to `cdt_product` | Yes | On delete of the parent: Restrict. Navigation property `cdt_Product`. |
| Cost version | `cdt_costversion` | Lookup to `cdt_costversion` | Yes | On delete of the parent: Restrict. Navigation property `cdt_CostVersion`. |
| Region | `cdt_region` | Lookup to `cdt_region` | Yes | On delete of the parent: Restrict. Navigation property `cdt_Region`. |

Alternate keys: **Scenario code** on `cdt_code`.

Formula columns (create by hand, data type *fx Formula*; set the schema name under *Advanced options* before saving):

| Column | Schema name | Result type | Decimals | Formula |
|---|---|---|---|---|
| Size ratio | `cdt_SizeRatio` | Decimal | 6 | `If('Reference size (MW)' > 0, 'Project size (MW)' / 'Reference size (MW)', 0)` |
| Module ratio | `cdt_ModuleRatio` | Decimal | 6 | `If('Module size (MW)' > 0 && 'Reference size (MW)' > 0, RoundUp('Project size (MW)' / 'Module size (MW)', 0) / RoundUp('Reference size (MW)' / 'Module size (MW)', 0), 0)` |

## Scenario Feature

Logical name `cdt_scenariofeature` · plural *Scenario Features* · ownership UserOwned.

Feature selected in a scenario.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (120) | Yes | Scenario code + '~' + feature code. |
| Scenario | `cdt_scenario` | Lookup to `cdt_scenario` | Yes | On delete of the parent: Cascade. Navigation property `cdt_Scenario`. |
| Feature | `cdt_feature` | Lookup to `cdt_feature` | Yes | On delete of the parent: Restrict. Navigation property `cdt_Feature`. |

Alternate keys: **Scenario feature code** on `cdt_code`.

## Scenario Line

Logical name `cdt_scenarioline` · plural *Scenario Lines* · ownership UserOwned.

Result line of a scenario per CBS element and cost type. Inputs are written by the flow, results are formula columns.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Line type | `cdt_linetype` | Choice: Line type | Yes |  |
| Cost type | `cdt_costtype` | Choice: Cost type | Yes |  |
| Scope | `cdt_scope` | Choice: Scope | No |  |
| TIC category | `cdt_ticcategory` | Choice: TIC category | No |  |
| Base amount (EUR) | `cdt_baseamounteur` | Decimal (2 decimals) | Yes | Cost at reference size in the base region. |
| Scaling code | `cdt_scalingcode` | Whole number | Yes | 1 = per module, 2 = power law, 3 = fixed. |
| Scaling exponent | `cdt_scalingexponent` | Decimal (3 decimals) | No |  |
| Size ratio | `cdt_sizeratio` | Decimal (6 decimals) | Yes |  |
| Module ratio | `cdt_moduleratio` | Decimal (6 decimals) | Yes |  |
| Regional factor | `cdt_regionalfactor` | Decimal (3 decimals) | Yes |  |
| Escalation factor | `cdt_escalationfactor` | Decimal (4 decimals) | Yes |  |
| Project size (MW) | `cdt_sizemw` | Decimal (2 decimals) | Yes |  |
| Scenario | `cdt_scenario` | Lookup to `cdt_scenario` | Yes | On delete of the parent: Cascade. Navigation property `cdt_Scenario`. |
| CBS element | `cdt_cbselement` | Lookup to `cdt_cbselement` | Yes | On delete of the parent: Restrict. Navigation property `cdt_CBSElement`. |
| Feature | `cdt_feature` | Lookup to `cdt_feature` | No | On delete of the parent: RemoveLink. Navigation property `cdt_Feature`. |

Formula columns (create by hand, data type *fx Formula*; set the schema name under *Advanced options* before saving):

| Column | Schema name | Result type | Decimals | Formula |
|---|---|---|---|---|
| Scale factor | `cdt_ScaleFactor` | Float | 6 | `If('Scaling code' = 1, Float('Module ratio'), If('Scaling code' = 2, Power(Float('Size ratio'), Float('Scaling exponent')), Float(1)))` |
| Final cost (EUR) | `cdt_FinalCostEUR` | Float | 2 | `Float('Base amount (EUR)') * 'Scale factor' * Float('Regional factor') * Float('Escalation factor')` |
| Cost per kW (EUR/kW) | `cdt_CostPerKW` | Float | 2 | `If('Project size (MW)' > 0, 'Final cost (EUR)' / (Float('Project size (MW)') * 1000), Float(0))` |

## CAPEX Dataset

Logical name `cdt_capexdataset` · plural *CAPEX Datasets* · ownership UserOwned.

Published scenario result per scope and TIC category. This is the interface table the LCOH Suite reads.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Dataset key | `cdt_datasetkey` | Text (200) | Yes | Scenario code + '~' + scope number + '~' + TIC category number. |
| Product code | `cdt_productcode` | Text (30) | No |  |
| Version code | `cdt_versioncode` | Text (50) | No |  |
| Region code | `cdt_regioncode` | Text (30) | No |  |
| Project size (MW) | `cdt_sizemw` | Decimal (2 decimals) | No |  |
| Scope | `cdt_scope` | Choice: Scope | No |  |
| TIC category | `cdt_ticcategory` | Choice: TIC category | No |  |
| Cost (EUR) | `cdt_costeur` | Decimal (2 decimals) | No |  |
| Cost (EUR/kW) | `cdt_costperkw` | Decimal (2 decimals) | No |  |
| Published on | `cdt_publishedon` | Date and time | No |  |
| Scenario | `cdt_scenario` | Lookup to `cdt_scenario` | Yes | On delete of the parent: Cascade. Navigation property `cdt_Scenario`. |

Alternate keys: **CAPEX dataset key** on `cdt_datasetkey`.

## Benchmark

Logical name `cdt_benchmark` · plural *Benchmarks* · ownership UserOwned.

Cost data point of an own product, a competitor or a public study.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (60) | Yes |  |
| Subject | `cdt_subject` | Text (200) | Yes | Product, competitor or study the value belongs to. |
| Own product | `cdt_isown` | Yes/No | No |  |
| Scope | `cdt_scope` | Choice: Scope | No | Scope the value covers, if known. |
| TIC category | `cdt_ticcategory` | Choice: TIC category | No | Leave blank for a total-plant value. |
| Value (EUR/kW) | `cdt_valueeurperkw` | Decimal (2 decimals) | Yes |  |
| Plant size (MW) | `cdt_plantsizemw` | Decimal (2 decimals) | No |  |
| Year | `cdt_year` | Whole number | No |  |
| Source | `cdt_source` | Text (300) | No |  |
| Source URL | `cdt_sourceurl` | Text (500) | No |  |
| Confidence | `cdt_confidence` | Choice: Confidence | No |  |
| Comment | `cdt_comment` | Multiline text | No | State what is included and excluded. |
| Region | `cdt_region` | Lookup to `cdt_region` | No | On delete of the parent: RemoveLink. Navigation property `cdt_Region`. |

Alternate keys: **Benchmark code** on `cdt_code`.

## Target

Logical name `cdt_target` · plural *Targets* · ownership UserOwned.

Target value per CBS element.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Name | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (80) | Yes |  |
| Target (EUR/kW) | `cdt_targeteurperkw` | Decimal (2 decimals) | Yes | Target at reference size. |
| Target year | `cdt_targetyear` | Whole number | No |  |
| Basis | `cdt_basis` | Choice: Target basis | No |  |
| Comment | `cdt_comment` | Multiline text | No |  |
| CBS element | `cdt_cbselement` | Lookup to `cdt_cbselement` | Yes | On delete of the parent: Cascade. Navigation property `cdt_CBSElement`. |

Alternate keys: **Target code** on `cdt_code`.

## Idea

Logical name `cdt_idea` · plural *Ideas* · ownership UserOwned.

Cost-down idea submitted by a colleague.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Title | `cdt_name` | Text (200), primary name | Yes | |
| Description | `cdt_description` | Multiline text | No |  |
| Estimated saving (EUR) | `cdt_estimatedsavingeur` | Decimal (2 decimals) | No | Per plant at reference size. |
| Effort | `cdt_effort` | Choice: Idea effort | No |  |
| Category | `cdt_category` | Choice: Idea category | No |  |
| Status | `cdt_status` | Choice: Idea status | Yes |  |
| Submitter | `cdt_submittername` | Text (100) | No |  |
| Evaluation note | `cdt_evaluationnote` | Multiline text | No |  |
| Product | `cdt_product` | Lookup to `cdt_product` | No | On delete of the parent: RemoveLink. Navigation property `cdt_Product`. |
| CBS element | `cdt_cbselement` | Lookup to `cdt_cbselement` | No | On delete of the parent: RemoveLink. Navigation property `cdt_CBSElement`. |

## Measure

Logical name `cdt_measure` · plural *Measures* · ownership UserOwned.

Cost-down measure with owner, saving, effort and degree of implementation.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Title | `cdt_name` | Text (200), primary name | Yes | |
| Code | `cdt_code` | Text (60) | Yes |  |
| Saving (EUR) | `cdt_savingeur` | Decimal (2 decimals) | Yes | Per plant at reference size. |
| One-off cost (EUR) | `cdt_oneoffcosteur` | Decimal (2 decimals) | No |  |
| Effort (person-days) | `cdt_effortpd` | Decimal (1 decimals) | No |  |
| Day rate (EUR) | `cdt_dayrateeur` | Decimal (2 decimals) | No | Cost per person-day used for the score; blank is treated as 800. |
| Probability (%) | `cdt_probability` | Whole number | Yes |  |
| Degree of implementation | `cdt_dilevel` | Choice: Degree of implementation | Yes |  |
| Due date | `cdt_duedate` | Date only | No |  |
| Status | `cdt_status` | Choice: Measure status | Yes |  |
| Realised saving (EUR) | `cdt_realisedsavingeur` | Decimal (2 decimals) | No |  |
| Comment | `cdt_comment` | Multiline text | No |  |
| Idea | `cdt_idea` | Lookup to `cdt_idea` | No | On delete of the parent: RemoveLink. Navigation property `cdt_Idea`. |
| Product | `cdt_product` | Lookup to `cdt_product` | No | On delete of the parent: RemoveLink. Navigation property `cdt_Product`. |
| CBS element | `cdt_cbselement` | Lookup to `cdt_cbselement` | Yes | On delete of the parent: Restrict. Navigation property `cdt_CBSElement`. |
| Target version | `cdt_targetversion` | Lookup to `cdt_costversion` | No | On delete of the parent: RemoveLink. Navigation property `cdt_TargetVersion`. |

Alternate keys: **Measure code** on `cdt_code`.

Formula columns (create by hand, data type *fx Formula*; set the schema name under *Advanced options* before saving):

| Column | Schema name | Result type | Decimals | Formula |
|---|---|---|---|---|
| Weighted saving (EUR) | `cdt_WeightedSavingEUR` | Decimal | 2 | `'Saving (EUR)' * 'Probability (%)' / 100` |
| Priority score | `cdt_PriorityScore` | Decimal | 2 | `If(('One-off cost (EUR)' + 'Effort (person-days)' * If(IsBlank('Day rate (EUR)'), 800, 'Day rate (EUR)')) > 0, 'Saving (EUR)' * 'Probability (%)' / 100 / ('One-off cost (EUR)' + 'Effort (person-days)' * If(IsBlank('Day rate (EUR)'), 800, 'Day rate (EUR)')), 0)` |

## Teamcenter Mapping

Logical name `cdt_tcmapping` · plural *Teamcenter Mappings* · ownership UserOwned.

Remembers which CBS element and cost type a Teamcenter item belongs to, so that re-imports are mapped automatically.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Teamcenter item ID | `cdt_name` | Text (100), primary name | Yes | |
| Cost type | `cdt_costtype` | Choice: Cost type | Yes |  |
| Comment | `cdt_comment` | Multiline text | No |  |
| CBS element | `cdt_cbselement` | Lookup to `cdt_cbselement` | Yes | On delete of the parent: Restrict. Navigation property `cdt_CBSElement`. |

Alternate keys: **Teamcenter item ID** on `cdt_name`.

## Teamcenter Import Row

Logical name `cdt_tcimportrow` · plural *Teamcenter Import Rows* · ownership UserOwned.

Staging table for rows exported from Teamcenter before they become cost items.

| Column | Logical name | Type | Required | Notes |
|---|---|---|---|---|
| Row key | `cdt_name` | Text (250), primary name | Yes | |
| Import run | `cdt_importrun` | Text (60) | Yes | Identifier of the import, e.g. 2026-11-16 or the export file name. |
| Target version code | `cdt_versioncode` | Text (50) | Yes |  |
| Item ID | `cdt_itemid` | Text (100) | Yes |  |
| Revision | `cdt_revision` | Text (20) | No |  |
| Item name | `cdt_itemname` | Text (300) | No |  |
| Parent item ID | `cdt_parentitemid` | Text (100) | No |  |
| BOM level | `cdt_bomlevel` | Whole number | No |  |
| Quantity | `cdt_quantity` | Decimal (4 decimals) | No |  |
| Unit | `cdt_unit` | Text (20) | No |  |
| Unit price | `cdt_unitprice` | Decimal (4 decimals) | No |  |
| Currency code | `cdt_currencycode` | Text (3) | No |  |
| Supplier ID | `cdt_supplierid` | Text (60) | No |  |
| Supplier name | `cdt_suppliername` | Text (200) | No |  |
| Price date | `cdt_pricedate` | Date only | No |  |
| CBS code | `cdt_cbscode` | Text (50) | No | Filled from the mapping table or by hand. |
| Cost type | `cdt_costtype` | Choice: Cost type | No |  |
| Status | `cdt_status` | Choice: Import status | No |  |
| Message | `cdt_message` | Text (500) | No |  |

Alternate keys: **Import row key** on `cdt_name`.

## Global choices

Flows and the Web API use the numeric values; apps and reports show the labels.

### Scope (`cdt_scope`)

| Value | Label |
|---|---|
| 710000001 | NCA scope |
| 710000002 | EPC scope |
| 710000003 | Owner / other |

### Cost type (`cdt_costtype`)

| Value | Label |
|---|---|
| 710000001 | Material |
| 710000002 | Engineering hours |
| 710000003 | Manufacturing & assembly |
| 710000004 | Logistics |
| 710000005 | Construction & installation |
| 710000006 | Services & commissioning |
| 710000007 | Indirects & contingency |

### TIC category (`cdt_ticcategory`)

| Value | Label |
|---|---|
| 710000001 | Electrolyser modules |
| 710000002 | Process balance of plant |
| 710000003 | Power supply & electrical |
| 710000004 | Utilities |
| 710000005 | Civil & buildings |
| 710000006 | Installation & construction |
| 710000007 | Engineering & project management |
| 710000008 | Indirects, commissioning & contingency |

### Scaling method (`cdt_scalingmethod`)

| Value | Label |
|---|---|
| 710000001 | Per module |
| 710000002 | Power law |
| 710000003 | Fixed |

### Version status (`cdt_versionstatus`)

| Value | Label |
|---|---|
| 710000001 | Draft |
| 710000002 | Released |
| 710000003 | Archived |

### Price source (`cdt_pricesource`)

| Value | Label |
|---|---|
| 710000001 | Teamcenter |
| 710000002 | ERP |
| 710000003 | Supplier quote |
| 710000004 | Estimate |
| 710000005 | Benchmark |

### Confidence (`cdt_confidence`)

| Value | Label |
|---|---|
| 710000001 | High |
| 710000002 | Medium |
| 710000003 | Low |

### Make or buy (`cdt_makebuy`)

| Value | Label |
|---|---|
| 710000001 | Make |
| 710000002 | Buy |

### Impact type (`cdt_impacttype`)

| Value | Label |
|---|---|
| 710000001 | Fixed amount (EUR) |
| 710000002 | Amount per MW (EUR/MW) |
| 710000003 | Percent of element (%) |

### Scenario status (`cdt_scenariostatus`)

| Value | Label |
|---|---|
| 710000001 | Draft |
| 710000002 | Calculated |
| 710000003 | Published |

### Line type (`cdt_linetype`)

| Value | Label |
|---|---|
| 710000001 | Base cost |
| 710000002 | Feature effect |

### Target basis (`cdt_targetbasis`)

| Value | Label |
|---|---|
| 710000001 | Benchmark |
| 710000002 | Top-down from LCOH |
| 710000003 | Bottom-up estimate |
| 710000004 | Management target |

### Idea status (`cdt_ideastatus`)

| Value | Label |
|---|---|
| 710000001 | New |
| 710000002 | In evaluation |
| 710000003 | Accepted |
| 710000004 | Rejected |
| 710000005 | Converted to measure |

### Idea effort (`cdt_ideaeffort`)

| Value | Label |
|---|---|
| 710000001 | Small |
| 710000002 | Medium |
| 710000003 | Large |

### Idea category (`cdt_ideacategory`)

| Value | Label |
|---|---|
| 710000001 | Design |
| 710000002 | Procurement |
| 710000003 | Manufacturing |
| 710000004 | Scope / EPC interface |
| 710000005 | Standardisation |
| 710000006 | Other |

### Degree of implementation (`cdt_dilevel`)

| Value | Label |
|---|---|
| 710000001 | DI1 Idea |
| 710000002 | DI2 Evaluated |
| 710000003 | DI3 Decided |
| 710000004 | DI4 Implemented |
| 710000005 | DI5 Effective in cost version |

### Measure status (`cdt_measurestatus`)

| Value | Label |
|---|---|
| 710000001 | Open |
| 710000002 | On hold |
| 710000003 | Done |
| 710000004 | Cancelled |

### Import status (`cdt_importstatus`)

| Value | Label |
|---|---|
| 710000001 | New |
| 710000002 | Mapped |
| 710000003 | Loaded |
| 710000004 | Error |
