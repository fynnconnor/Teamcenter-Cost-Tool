# Seed and demo data

**All cost figures in this folder are synthetic.** They are round numbers chosen so that results can be checked by hand. Replace them with real data before anyone draws conclusions.

| File (load order) | Table | Content |
|---|---|---|
| `01_cdt_fxrate.csv` | FX Rate | EUR and USD |
| `02_cdt_product.csv` | Product | One demo product, 100 MW reference size, 20 MW modules |
| `03_cdt_cbselement.csv` | CBS Element | Generic 8-branch cost breakdown structure with scope, TIC category and scaling rule |
| `04_cdt_supplier.csv` | Supplier | Six placeholder suppliers |
| `05_cdt_costversion.csv` | Cost Version | V001 released baseline, V002 draft |
| `06_cdt_costitem.csv` | Cost Item | 14 items per version |
| `07_cdt_region.csv`, `08_cdt_regionalfactor.csv` | Region, Regional Factor | Five regions, illustrative factors per cost type |
| `09_cdt_feature.csv`, `10_cdt_featureimpact.csv` | Feature, Feature Impact | Three features, one impact each |
| `11_cdt_scenario.csv`, `12_cdt_scenariofeature.csv` | Scenario, Scenario Feature | Three scenarios used by the golden test results |
| `13_cdt_target.csv` | Target | Target per level-1 element |
| `14_cdt_benchmark.csv` | Benchmark | Two public study values and the demo product |
| `15_cdt_idea.csv`, `16_cdt_measure.csv` | Idea, Measure | Three ideas, three measures |
| `17_cdt_tcmapping.csv` | Teamcenter Mapping | Item-to-CBS mapping for the demo export |

## Header conventions

- A plain header is the logical column name, for example `cdt_code`.
- `cdt_Product@cdt_code` is a lookup: navigation property `cdt_Product`, resolved through the alternate key column `cdt_code` of the target table.
- Choice columns contain the label, Yes/No columns contain `Yes` or `No`.

Load with `scripts/load_seed_data.py` or, without Python, with `scripts/load_seed_browser_console.js`.
