# Model-driven app "Cost Cockpit"

The model-driven app is the workplace for everyone who maintains cost data. It needs no code: Dataverse generates forms and views from the tables, and you arrange them. This file is the specification; the build manual (chapter 6) walks through the clicks.

## 1. App and navigation

Create the app inside the solution **Cost Cockpit**: *New > App > Model-driven app*, name `Cost Cockpit`.

Site map (left navigation):

| Area | Group | Tables / pages |
|---|---|---|
| Cost | Structure | Products, CBS Elements |
| Cost | Baseline | Cost Versions, Cost Items |
| Scenarios | Simulation | Scenarios, Scenario Lines |
| Scenarios | Parameters | Regions, Regional Factors, Features, Feature Impacts |
| Cost-down | Targets | Targets, Benchmarks |
| Cost-down | Pipeline | Ideas, Measures |
| Integration | Teamcenter | Teamcenter Import Rows, Teamcenter Mappings, Suppliers |
| Integration | LCOH Suite | CAPEX Datasets |
| Integration | Settings | FX Rates |
| Analysis | Reports | Power BI report (embedded dashboard, added in phase 1) |

## 2. Views

Edit the view *Active <table>* of each table and add the columns below, in this order. Sort as stated.

| Table | Columns | Sort | Extra views |
|---|---|---|---|
| Products | Code, Name, Reference size (MW), Module size (MW), Active | Code | |
| CBS Elements | Code, Name, Product, Parent element, Level, Scope, TIC category, Scaling method, Scaling exponent, Is leaf | Sort order | *Leaf elements* (Is leaf = Yes) |
| Cost Versions | Code, Name, Product, Version number, Status, Released on, Is baseline | Version number, descending | *Draft versions*, *Released versions* |
| Cost Items | Description, Cost version, CBS element, Cost type, Quantity, Unit, Unit price, Currency code, Amount (EUR), Supplier, Price source, Confidence | Amount (EUR), descending | *Items without price* (Unit price = 0), *Low confidence* |
| Scenarios | Code, Name, Cost version, Region, Project size (MW), Status, Total cost (EUR), Total cost (EUR/kW), Calculated on | Calculated on, descending | |
| Scenario Lines | Scenario, CBS element, Cost type, Line type, Base amount (EUR), Scale factor, Regional factor, Final cost (EUR), Cost per kW (EUR/kW) | Final cost (EUR), descending | |
| Regional Factors | Region, Cost type, Factor, Source, Valid from | Region | |
| Feature Impacts | Feature, CBS element, Impact type, Value, Cost type | Feature | |
| Targets | CBS element, Target (EUR/kW), Target year, Basis | CBS element | |
| Benchmarks | Subject, Own product, TIC category, Scope, Value (EUR/kW), Plant size (MW), Year, Source, Confidence | Year, descending | |
| Ideas | Title, Submitter, Product, CBS element, Estimated saving (EUR), Effort, Category, Status, Created on | Created on, descending | *New ideas* (Status = New), *My ideas* (Created by = current user) |
| Measures | Code, Title, CBS element, Owner, Saving (EUR), Probability (%), Weighted saving (EUR), Priority score, Degree of implementation, Due date, Status | Priority score, descending | *Open measures*, *Overdue* (Due date < today, Status = Open) |
| Teamcenter Import Rows | Import run, Item ID, Item name, Quantity, Unit price, Currency code, Supplier name, CBS code, Cost type, Status, Message | Import run, descending | *Not mapped* (Status = New) |
| CAPEX Datasets | Dataset key, Scenario, Scope, TIC category, Cost (EUR), Cost (EUR/kW), Published on | Published on, descending | |

Turn on the **editable grid** (Power Apps grid control, *Enable editing = Yes*) for Cost Items, Regional Factors, Targets and Teamcenter Import Rows. These are edited in bulk.

## 3. Forms

Main form per table: one tab *General* with two columns. Put the fields in the order of the data dictionary. Additions:

| Table | Sub-grids and special controls |
|---|---|
| Product | Sub-grids: CBS Elements, Cost Versions, Features |
| CBS Element | Sub-grids: child elements (Parent element = this), Cost Items, Targets, Measures. Turn on the hierarchy view (table settings > *Hierarchy*, relationship Parent element) to get the tree view |
| Cost Version | Sub-grid: Cost Items (editable grid). Sub-grid: Scenarios |
| Scenario | Section *Result*: Total cost (EUR), Total cost (EUR/kW), Calculated on, Size ratio, Module ratio (all read-only). Sub-grids: Scenario Features, Scenario Lines, CAPEX Datasets |
| Feature | Sub-grid: Feature Impacts |
| Region | Sub-grid: Regional Factors (editable grid) |
| Idea | Sub-grid: Measures |
| Measure | Section *Score*: Weighted saving (EUR), Priority score (read-only) |

Create a **quick create form** for Idea (Title, Description, Product, CBS element, Estimated saving, Effort, Category) and enable *quick create* on the table. This is the zero-code idea box; the canvas page in `idea-box.md` is the friendlier alternative.

## 4. Business rules

Create these as business rules with scope **Entity** so that they also apply to imports and flows.

| Table | Rule | Condition | Action |
|---|---|---|---|
| Cost Version | Lock released version | Status equals Released or Archived | Lock all fields except Comment |
| Cost Item | Default FX rate | FX rate to EUR does not contain data | Set FX rate to EUR = 1 |
| Cost Item | Default currency | Currency code does not contain data | Set Currency code = "EUR" |
| CBS Element | Exponent only for power law | Scaling method does not equal Power law | Clear and lock Scaling exponent |
| CBS Element | Exponent required | Scaling method equals Power law | Set Scaling exponent as Business Required |
| Measure | Default day rate | Day rate (EUR) does not contain data | Set Day rate (EUR) = 800 |
| Scenario | Default escalation | Escalation factor does not contain data | Set Escalation factor = 1 |

A business rule locks fields on the form only. To really protect released versions, add the security set-up of chapter 5.

## 5. Security roles

Copy the standard role *Basic User* three times inside the solution and set the table privileges:

| Role | For | Privileges on Cost Cockpit tables |
|---|---|---|
| Cost Cockpit Reader | Management, R&D | Read on all tables, organization level. No access to Supplier and to Unit price / Amount if supplier prices are confidential (use column security on Unit price) |
| Cost Cockpit Contributor | All colleagues | Reader, plus Create and Write (user level) on Idea |
| Cost Cockpit Editor | Cost engineers, product managers | Create, Read, Write, Append, Append To on all tables (organization level); Delete on Cost Item, Scenario, Scenario Line, Idea, Measure |
| Cost Cockpit Admin | Product owner, developer | All privileges on all tables |

Released versions: assign released Cost Versions to a team *Cost Cockpit Archive* in the release flow (optional step) and give Editors only user-level Write on Cost Version and Cost Item. Then a released version can no longer be changed by editors.

Turn on **auditing** for the environment and for the tables Cost Item, Cost Version, CBS Element, Target and Measure (table settings > *Audit changes to its data*).

## 6. Command bar buttons

Four buttons call the flows or create rows. Formulas are in `command-bar.fx`.

| Table | Button | Location | Effect |
|---|---|---|---|
| Cost Version | Release version | Main form | Sets *Release requested* = Yes. The flow `02 Cost version - release` freezes the version and opens the next draft |
| Scenario | Calculate | Main form and main grid | Sets *Calculation requested* = Yes. The flow `03 Scenario - calculate` writes the scenario lines |
| Scenario | Publish to LCOH Suite | Main form | Sets *Publication requested* = Yes. The flow `04 Scenario - publish CAPEX dataset` writes the CAPEX dataset rows |
| Idea | Convert to measure | Main form and main grid | Creates a measure from the idea and sets the idea to *Converted to measure* |

How to add a button: open the app in the app designer, select the table > *Edit command bar* > choose *Main form* or *Main grid* > *New > Command* > set *Action* to *Run formula* and paste the formula; set *Visibility* to *Show on condition from formula* and paste the visibility formula. The first time, the designer creates a command component library; add the tables named in the formula as data sources there (*Add data*).

If your environment does not offer formula commands, the fallback needs no button: put the Yes/No field (*Release requested*, *Calculation requested*, *Publication requested*) on the form. Setting it to Yes and saving triggers the same flow.

## 7. Embedded Power BI report

After the report is published (build manual chapter 9): in the solution, *New > Dashboard > Power BI embedded*, pick workspace and report, then add the dashboard to the site map under *Analysis*.
