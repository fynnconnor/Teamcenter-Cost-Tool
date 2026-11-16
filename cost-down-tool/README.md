# Cost-down tool: in-house or external?

Research basis for the make-or-buy decision on a product-cost monitoring tool.
Status: 13 November 2026, desk research, no vendor contacted yet.

| File | What it is |
|---|---|
| `cost-down-tool_make-or-buy-research.pptx` | 36 slides: summary, external market and shortlist, in-house options with architecture and roadmap, comparison, recommendation. Speaker notes carry the detail and source IDs. |
| `cost-down-tool_decision-workbook.xlsx` | 15 sheets: requirements, long list, KPI matrix, in-house options, fit matrix, weighted scoring, 5-year cost model, roadmap, Teamcenter interface routes, risks, RFI and open questions, public hydrogen cost references, sources. Weights, scores and cost assumptions are editable. |
| `cost-down-tool_research-dossier.md` / `.docx` | Full reasoning behind every slide, with all 82 sources linked. |
| `cost-cockpit/` | Code basis and build manual for the in-house Power App (data model, scripts, demo data, flows, Teamcenter import, Power BI). Start with `cost-cockpit/README.md`. |

## Read this before quoting numbers

- No product cost management vendor publishes prices. All external cost figures are planning assumptions by the author and should be replaced by RFI answers.
- Fit and weighted scores are a preliminary desk assessment by one person.
- Vendor pages could not be opened directly from the research environment; facts were taken from search extracts of those pages.

## Regenerating the files

The workbook and the deck are generated from `build/content.py`.

```bash
cd build
python3 content.py            # writes content.json
python3 build_xlsx.py         # writes ../cost-down-tool_decision-workbook.xlsx
node build_pptx.js            # writes ../cost-down-tool_make-or-buy-research.pptx
```

`build_pptx.js` needs the npm packages `pptxgenjs`, `react`, `react-dom`, `react-icons` and `sharp`, and the environment variable `PPTX_SKILL_DIR` pointing to a folder that contains `scripts/apply_theme.js` (used to write the colour theme into the deck). The workbook stores formulas without cached values until it is opened in Excel or recalculated.
