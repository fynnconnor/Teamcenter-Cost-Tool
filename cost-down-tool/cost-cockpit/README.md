# Cost Cockpit: code basis and build manual

The cost-down tool as a Power App on Dataverse, next to the LCOH Suite, with a Teamcenter interface and a Power BI report. This folder holds everything needed to build it: data model, provisioning scripts, demo data, calculation reference, app and flow specifications, Teamcenter import, report definition and the manual.

Status: 16 November 2026, version 0.1. Built for the 13 requirements of the make-or-buy research (`../cost-down-tool_research-dossier.md`).

## Start here

1. Read `docs/01-build-manual.md`, chapters 1 and 2.
2. Send the three requests in chapter 2.2 (IT, PLM IT, LCOH Suite owner).
3. Follow chapters 3 to 6: environment, data model, demo data, app. That is day 1.

## What is in the folder

| Path | Content |
|---|---|
| `docs/01-build-manual.md` (`.docx`) | Step-by-step manual from empty environment to production |
| `docs/02-requirements-specification.md` (`.docx`) | The 13 requirements with acceptance checks, 16 further requirements to decide, add-ins and features |
| `docs/03-data-dictionary.md` | All 20 tables, columns, keys, formula columns and 18 choices (generated) |
| `schema/cost_cockpit.schema.json` | Source of truth for the data model |
| `scripts/` | `provision_dataverse.py` and `provision_browser_console.js` create the data model; `load_seed_data.py` and `load_seed_browser_console.js` load the demo data; `build_artifacts.py` regenerates derived files; `tests/` |
| `seed/` | Synthetic demo data (one product, two versions, three scenarios) |
| `engine/` | `cost_engine.py`: reference calculation; `golden/`: expected results for every test in the manual |
| `app/` | Model-driven app specification, command-bar formulas (Power Fx), idea box page |
| `flows/` | Five Power Automate flow specifications with every expression |
| `teamcenter/` | Export template, two dataflow queries (Power Query M), custom connector definition (OpenAPI 2.0) |
| `powerbi/` | Queries (M), measures (DAX), model and page specification |

## What was tested

| Part | Status |
|---|---|
| Data model provisioning (Python and browser script) | Tested against a simulated Dataverse Web API: complete, in the right order, repeatable |
| Demo data loaders (Python and browser script) | Tested against the same simulation: 132 rows, no duplicates on re-run |
| Calculation engine | 16 unit tests with hand-calculated expectations |
| Idea box YAML | Valid against Microsoft's published schema for canvas source files; not pasted into Power Apps Studio |
| Flows, Power Fx formulas, DAX, Power Query, Teamcenter connector | Not run: they need a tenant, Power BI Desktop and a Teamcenter system. Written against current Microsoft documentation, each with expected results on the demo data |

Run the tests: `python -m unittest discover -s tests` in `scripts/` and `python -m unittest` in `engine/` (Python 3.9 or later, no packages needed; Node.js is used for the browser-script tests if installed).

## Assumptions

- Dataverse is available (Power Apps Premium). Without it, the same structure can be built on SharePoint lists with reduced function; see option A in the research.
- All demo figures are synthetic and must not be read as real costs.
- Regional factors, scaling exponents and benchmarks in the demo data are placeholders.
