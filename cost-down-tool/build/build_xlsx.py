"""Build the decision workbook from content.py.

Usage: python3 build_xlsx.py [output.xlsx]
"""
import os
import sys

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L

import content as c

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "cost-down-tool_decision-workbook.xlsx")

FONT = "Arial"
PETROL = "0E4D5B"
TEAL = "0E7C7B"
MINT = "E6F0EE"
AMBER = "F4A259"
GREY = "F2F4F4"

f_title = Font(name=FONT, size=16, bold=True, color=PETROL)
f_sub = Font(name=FONT, size=10, italic=True, color="555555")
f_head = Font(name=FONT, size=10, bold=True, color="FFFFFF")
f_body = Font(name=FONT, size=10)
f_bold = Font(name=FONT, size=10, bold=True)
f_input = Font(name=FONT, size=10, color="0000FF")
f_link = Font(name=FONT, size=10, color="008000")
f_section = Font(name=FONT, size=11, bold=True, color=PETROL)
fill_head = PatternFill("solid", start_color=PETROL)
fill_sub = PatternFill("solid", start_color=MINT)
fill_grey = PatternFill("solid", start_color=GREY)
fill_yellow = PatternFill("solid", start_color="FFFF00")
fill_amber = PatternFill("solid", start_color="FCE3C5")
thin = Side(style="thin", color="C9D3D2")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap_top = Alignment(wrap_text=True, vertical="top")
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
EUR = '#,##0;(#,##0);"-"'
NUM1 = "0.0"
NUM2 = "0.00"
PCT = "0%"

wb = Workbook()


def sheet(title, tab=None):
    ws = wb.create_sheet(title)
    if tab:
        ws.sheet_properties.tabColor = tab
    ws.sheet_view.showGridLines = False
    return ws


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = f_title
    ws.row_dimensions[1].height = 26
    if sub:
        ws["A2"] = sub
        ws["A2"].font = f_sub


def header(ws, row, labels, start_col=1, height=30):
    for i, lab in enumerate(labels):
        cell = ws.cell(row=row, column=start_col + i, value=lab)
        cell.font = f_head
        cell.fill = fill_head
        cell.alignment = center
        cell.border = border
    ws.row_dimensions[row].height = height


def body(ws, row, values, start_col=1, fonts=None, fmt=None, fill=None, align=None):
    for i, val in enumerate(values):
        cell = ws.cell(row=row, column=start_col + i, value=val)
        cell.font = (fonts[i] if fonts and fonts[i] else f_body)
        cell.alignment = align or wrap_top
        cell.border = border
        if fmt and fmt[i]:
            cell.number_format = fmt[i]
        if fill:
            cell.fill = fill
    return row + 1


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, start=1):
        ws.column_dimensions[L(i)].width = w


SOL_KEYS = [s[0] for s in c.SOLUTIONS]
SOL_SHORT = [s[1] for s in c.SOLUTIONS]
N_REQ = len(c.REQUIREMENTS)

# ---------------------------------------------------------------- Read me
ws = wb.active
ws.title = "Read me"
ws.sheet_view.showGridLines = False
ws.sheet_properties.tabColor = PETROL
title(ws, "Cost-down tool: in-house or external? - Decision workbook",
      "Research status 13 Nov 2026. Desk research; no vendor has been contacted yet.")
rows = [
    ("Purpose", "Working file for the make-or-buy decision. It holds every matrix behind the slides and lets you change weights, scores and cost assumptions."),
    ("Legend: blue text", "Input or assumption that you can overwrite (scores, weights, prices, effort)."),
    ("Legend: black text", "Formula. Do not overwrite."),
    ("Legend: green text", "Value linked from another sheet."),
    ("Legend: yellow fill", "Planning assumption that should be replaced by a vendor quote or internal figure before the decision."),
    ("Important caveat", "No product cost management vendor publishes prices. All external cost figures are planning assumptions by the author, built from the public signals named next to them."),
    ("Fit scores", "0 = not covered, 1 = workaround / heavy customisation, 2 = largely covered by configuration, 3 = native / designed in. In-house scores describe the target design; nothing exists today."),
    ("Source IDs", "S1...S82 refer to the sheet 'Sources'. The dossier (markdown file) explains the reasoning."),
]
r = 4
for k, v in rows:
    ws.cell(row=r, column=1, value=k).font = f_bold
    cell = ws.cell(row=r, column=2, value=v)
    cell.font = f_body
    cell.alignment = wrap_top
    if "blue" in k:
        cell.font = f_input
    if "green" in k:
        cell.font = f_link
    if "yellow" in k:
        cell.fill = fill_yellow
    ws.row_dimensions[r].height = 30
    r += 1
r += 1
ws.cell(row=r, column=1, value="Sheets").font = f_section
r += 1
index = [
    ("Requirements", "13 requirements derived from the task description, with German original and proposed priority"),
    ("Long list", "18 screened products by category"),
    ("External KPIs", "18 KPI rows for the five shortlisted external products"),
    ("Complementary tools", "Products that cover a part (measures, data, low-code)"),
    ("In-house options", "Three Microsoft-suite options A, B, C"),
    ("Fit matrix", "Requirement fit 0-3 for all eight solutions (editable)"),
    ("Scoring", "Weighted scoring with editable weights and scores"),
    ("TCO model", "5-year cost model with low / base / high cases (editable)"),
    ("Roadmap", "Phases, work packages, effort and a week plan for the in-house path"),
    ("Teamcenter interface", "Five routes to get prices and suppliers out of Teamcenter"),
    ("Risks", "Risk register for in-house and external"),
    ("RFI and open questions", "Questions for vendors and internal clarifications, with space for answers"),
    ("H2 cost references", "Public cost figures for benchmarking and calibration"),
    ("Sources", "All sources with links"),
]
header(ws, r, ["Sheet", "Content"])
r += 1
for name, desc in index:
    body(ws, r, [name, desc], fonts=[f_bold, None])
    r += 1
widths(ws, [26, 120])

# ---------------------------------------------------------------- Requirements
ws = sheet("Requirements", TEAL)
title(ws, "Requirements catalogue (first version)",
      "Split of the brainstormed requirements into 13 scoreable items. Priority and comment columns are for the alignment with Product gH2 and R&D.")
header(ws, 4, ["ID", "Block", "Short name", "Requirement (English)", "Original wording (German)", "Proposed priority", "Agreed priority", "Comment / acceptance criterion"])
r = 5
for rid, block, short, en, de, prio in c.REQUIREMENTS:
    body(ws, r, [rid, block, short, en, de, prio, None, None], fonts=[f_bold, None, None, None, None, f_input, f_input, f_input])
    ws.cell(row=r, column=7).fill = fill_yellow
    r += 1
ws.cell(row=r + 1, column=1, value="Example for the yellow columns: Agreed priority = 'Must'; Comment = 'Version comparison must show the delta per cost element between two releases'.").font = f_sub
widths(ws, [6, 24, 26, 60, 60, 12, 12, 50])
ws.freeze_panes = "D5"

# ---------------------------------------------------------------- Long list
ws = sheet("Long list", TEAL)
title(ws, "Market long list", "Products screened in the desk research. 'Complement' = covers only a part of the requirements.")
header(ws, 4, ["#", "Product", "Vendor", "Category", "What it is", "Relevance for this use case", "Shortlisted"])
r = 5
for i, row in enumerate(c.LONGLIST, start=1):
    body(ws, r, [i, *row], fonts=[None, f_bold, None, None, None, None, None])
    r += 1
widths(ws, [4, 34, 22, 30, 60, 40, 12])
ws.freeze_panes = "C5"
ws.conditional_formatting.add(f"G5:G{r-1}", CellIsRule(operator="equal", formula=['"Yes"'], fill=PatternFill("solid", start_color="CDE8DC")))
ws.conditional_formatting.add(f"G5:G{r-1}", CellIsRule(operator="equal", formula=['"Complement"'], fill=fill_amber))

# ---------------------------------------------------------------- External KPIs
ws = sheet("External KPIs", TEAL)
title(ws, "KPI matrix for the five shortlisted external products",
      "Facts come from the sources in the last row. Yellow rows are planning assumptions by the author - replace with quotes.")
ext_keys = SOL_KEYS[:5]
header(ws, 4, ["KPI", *[s[2] for s in c.SOLUTIONS[:5]]])
r = 5
for i, kpi in enumerate(c.EXT_KPI_ROWS):
    vals = [kpi] + [c.EXT_KPIS[k][i] for k in ext_keys]
    is_assumption = kpi.startswith("Planning assumption") or kpi.startswith("Implementation time")
    body(ws, r, vals, fonts=[f_bold] + [f_input if is_assumption else None] * 5, fill=fill_yellow if is_assumption else None)
    ws.cell(row=r, column=1).fill = fill_sub
    r += 1
# fit score row linked from the fit matrix
vals = ["Requirement fit (of 39) - from 'Fit matrix'"] + [f"='Fit matrix'!{L(3+i)}{5+N_REQ}" for i in range(5)]
body(ws, r, vals, fonts=[f_bold] + [f_link] * 5)
ws.cell(row=r, column=1).fill = fill_sub
r += 1
vals = ["Weighted score (1-5) - from 'Scoring'"] + [f"=Scoring!{L(4+i)}14" for i in range(5)]
body(ws, r, vals, fonts=[f_bold] + [f_link] * 5, fmt=[None] + [NUM2] * 5)
ws.cell(row=r, column=1).fill = fill_sub
widths(ws, [34, 46, 46, 46, 46, 46])
ws.freeze_panes = "B5"

# ---------------------------------------------------------------- Complementary
ws = sheet("Complementary tools", TEAL)
title(ws, "Complementary products", "These do not answer the whole question but can fill a gap or supply data.")
header(ws, 4, ["Product", "Vendor", "Category", "What it adds", "Commercial information", "Possible role", "Sources"])
r = 5
for row in c.COMPLEMENTARY:
    body(ws, r, list(row), fonts=[f_bold] + [None] * 6)
    r += 1
widths(ws, [28, 30, 28, 60, 60, 50, 14])

# ---------------------------------------------------------------- In-house options
ws = sheet("In-house options", AMBER)
title(ws, "In-house options on the Microsoft suite",
      "A can serve as the MVP of B; C is a possible later evolution of B. Yellow rows are planning assumptions.")
ih_keys = SOL_KEYS[5:]
header(ws, 4, ["Aspect", *[s[2] for s in c.SOLUTIONS[5:]]])
r = 5
for i, aspect in enumerate(c.INHOUSE_ROWS):
    is_assumption = aspect.startswith("Planning assumption") or aspect.startswith("Time to MVP")
    body(ws, r, [aspect] + [c.INHOUSE[k][i] for k in ih_keys], fonts=[f_bold] + [f_input if is_assumption else None] * 3,
         fill=fill_yellow if is_assumption else None)
    ws.cell(row=r, column=1).fill = fill_sub
    r += 1
vals = ["Requirement fit (of 39) - from 'Fit matrix'"] + [f"='Fit matrix'!{L(8+i)}{5+N_REQ}" for i in range(3)]
body(ws, r, vals, fonts=[f_bold] + [f_link] * 3)
ws.cell(row=r, column=1).fill = fill_sub
r += 1
vals = ["Weighted score (1-5) - from 'Scoring'"] + [f"=Scoring!{L(9+i)}14" for i in range(3)]
body(ws, r, vals, fonts=[f_bold] + [f_link] * 3, fmt=[None] + [NUM2] * 3)
ws.cell(row=r, column=1).fill = fill_sub
r += 1
vals = ["5-year cost, selected case (EUR) - from 'TCO model'"] + [f"='TCO model'!G{55+i}" for i in range(3)]
body(ws, r, vals, fonts=[f_bold] + [f_link] * 3, fmt=[None] + [EUR] * 3)
ws.cell(row=r, column=1).fill = fill_sub
widths(ws, [34, 62, 62, 62])
ws.freeze_panes = "B5"

# ---------------------------------------------------------------- Fit matrix
ws = sheet("Fit matrix", PETROL)
title(ws, "Requirement fit matrix",
      "Scale 0-3: 0 not covered, 1 workaround / heavy customisation, 2 largely covered by configuration, 3 native / designed in. Blue cells are editable.")
ws["A3"] = "Preliminary desk assessment. External scores need confirmation in demos; in-house scores describe the target design, not something that exists today."
ws["A3"].font = f_sub
header(ws, 4, ["ID", "Requirement", *SOL_SHORT], height=34)
r = 5
for i, req in enumerate(c.REQUIREMENTS):
    vals = [req[0], f"{req[2]}: {req[3]}"] + [c.FIT[k][i] for k in SOL_KEYS]
    body(ws, r, vals, fonts=[f_bold, None] + [f_input] * 8)
    for col in range(3, 11):
        ws.cell(row=r, column=col).alignment = center
    r += 1
first, last = 5, r - 1
sum_row = r
body(ws, r, [None, "Sum (max. 39)"] + [f"=SUM({L(col)}{first}:{L(col)}{last})" for col in range(3, 11)],
     fonts=[None, f_bold] + [f_bold] * 8, fill=fill_sub, align=center)
r += 1
body(ws, r, [None, "Share of maximum"] + [f"={L(col)}{sum_row}/(3*COUNTA($A${first}:$A${last}))" for col in range(3, 11)],
     fonts=[None, f_bold] + [None] * 8, fmt=[None, None] + [PCT] * 8, fill=fill_sub, align=center)
r += 1
body(ws, r, [None, "Rank"] + [f"=RANK({L(col)}{sum_row},$C${sum_row}:$J${sum_row})" for col in range(3, 11)],
     fonts=[None, f_bold] + [None] * 8, fill=fill_sub, align=center)
r += 1
body(ws, r, [None, "Requirements not covered at all (score 0)"] + [f"=COUNTIF({L(col)}{first}:{L(col)}{last},0)" for col in range(3, 11)],
     fonts=[None, f_bold] + [None] * 8, fill=fill_sub, align=center)
ws.conditional_formatting.add(
    f"C{first}:J{last}",
    ColorScaleRule(start_type="num", start_value=0, start_color="F4B6A6", mid_type="num", mid_value=1.5, mid_color="FBF3D0",
                   end_type="num", end_value=3, end_color="8FCFB4"))
r += 2
ws.cell(row=r, column=1, value="Rationale per solution").font = f_section
r += 1
for key, short in zip(SOL_KEYS, SOL_SHORT):
    ws.cell(row=r, column=1, value=short).font = f_bold
    ws.cell(row=r, column=1).alignment = wrap_top
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=10)
    cell = ws.cell(row=r, column=2, value=c.FIT_RATIONALE[key])
    cell.font = f_body
    cell.alignment = wrap_top
    ws.row_dimensions[r].height = 30
    r += 1
widths(ws, [16, 70, 13, 13, 13, 13, 13, 13, 13, 13])
ws.freeze_panes = "C5"
assert sum_row == 5 + N_REQ

# ---------------------------------------------------------------- Scoring
ws = sheet("Scoring", PETROL)
title(ws, "Weighted scoring",
      "Scores 1-5 (5 = best). Weights (column B) and scores (blue) are editable; criterion C1 is derived from the fit matrix.")
header(ws, 4, ["Criterion", "Weight", "What is assessed", *SOL_SHORT], height=34)
r = 5
for idx, (cid, name, w, desc) in enumerate(c.CRITERIA):
    if cid == "C1":
        vals = [f"{cid} {name}", w, desc] + [f"='Fit matrix'!{L(3+i)}{sum_row}/(3*{N_REQ})*5" for i in range(8)]
        fonts = [f_bold, f_input, None] + [f_link] * 8
    else:
        vals = [f"{cid} {name}", w, desc] + list(c.SCORES[cid])
        fonts = [f_bold, f_input, None] + [f_input] * 8
    body(ws, r, vals, fonts=fonts, fmt=[None, PCT, None] + [NUM1] * 8)
    for col in range(4, 12):
        ws.cell(row=r, column=col).alignment = center
    ws.cell(row=r, column=2).alignment = center
    r += 1
crit_first, crit_last = 5, r - 1
body(ws, r, ["Sum of weights (must be 100%)", f"=SUM(B{crit_first}:B{crit_last})", None] + [None] * 8,
     fonts=[f_bold, f_bold, None] + [None] * 8, fmt=[None, PCT, None] + [None] * 8, fill=fill_grey, align=center)
r += 1
total_row = r
assert total_row == 14
body(ws, r, ["Weighted total (1-5)", None, None] + [f"=SUMPRODUCT($B${crit_first}:$B${crit_last},{L(col)}{crit_first}:{L(col)}{crit_last})" for col in range(4, 12)],
     fonts=[f_bold, None, None] + [f_bold] * 8, fmt=[None, None, None] + [NUM2] * 8, fill=fill_sub, align=center)
r += 1
body(ws, r, ["Rank", None, None] + [f"=RANK({L(col)}{total_row},$D${total_row}:$K${total_row})" for col in range(4, 12)],
     fonts=[f_bold, None, None] + [f_bold] * 8, fill=fill_sub, align=center)
ws.conditional_formatting.add(
    f"D{crit_first}:K{crit_last}",
    ColorScaleRule(start_type="num", start_value=1, start_color="F4B6A6", mid_type="num", mid_value=3, mid_color="FBF3D0",
                   end_type="num", end_value=5, end_color="8FCFB4"))
ws.conditional_formatting.add(f"B{crit_last+1}", FormulaRule(formula=[f"ABS(B{crit_last+1}-1)>0.0001"], fill=PatternFill("solid", start_color="F4B6A6")))
r += 2
notes = [
    "C4 and C5 for external products rest on planning assumptions (no quotes yet). Update after the RFI.",
    "C8 combines vendor viability (external) and key-person / maintenance risk (in-house).",
    "Sensitivity: raise the weight of C7 to see the effect of shipped reference data; raise C2 if the Teamcenter link is the dominant concern.",
]
for n in notes:
    ws.cell(row=r, column=1, value=n).font = f_sub
    r += 1
chart = BarChart()
chart.type = "bar"
chart.style = 10
chart.title = "Weighted total (1-5)"
chart.roundedCorners = False
data = Reference(ws, min_col=4, max_col=11, min_row=total_row, max_row=total_row)
cats = Reference(ws, min_col=4, max_col=11, min_row=4, max_row=4)
chart.add_data(data, from_rows=True, titles_from_data=False)
chart.set_categories(cats)
chart.legend = None
chart.title.overlay = False
chart.x_axis.delete = False
chart.y_axis.delete = False
chart.y_axis.scaling.min = 0
chart.y_axis.scaling.max = 5
chart.height = 8
chart.width = 18
ws.add_chart(chart, "M4")
widths(ws, [40, 9, 52, 13, 13, 13, 13, 13, 13, 13, 13])
ws.freeze_panes = "D5"

# ---------------------------------------------------------------- TCO model
ws = sheet("TCO model", PETROL)
title(ws, "5-year cost model (EUR)",
      "All blue cells are assumptions you can change. Yellow cells have no public basis and should be replaced by vendor quotes. Data stewardship effort is the same in every option and not included.")
g = c.TCO_GLOBAL
ws["A4"] = "Global inputs"
ws["A4"].font = f_section
glob = [
    ("Editing users (cost engineers, product managers)", g["core_users"], None, "Assumption - confirm with Product gH2"),
    ("Contributors / viewers (idea submitters, management, R&D)", g["contrib_users"], None, "Assumption - confirm with Product gH2"),
    ("Horizon in years", g["years"], None, "Assumption"),
    ("Exchange rate EUR per USD", g["fx"], "0.00", "Assumption for converting USD list prices - replace with treasury rate"),
    ("Internal day rate (EUR per person-day)", g["internal_rate"], EUR, "Assumption - replace with internal cost rate"),
    ("External day rate (EUR per person-day)", g["external_rate"], EUR, "Assumption - replace with partner offer"),
    ("Case selector: 1 = low, 2 = base, 3 = high", 2, None, "Drives the 'Selected case' and 'Results' blocks"),
]
r = 5
nowrap = Alignment(vertical="top")
for lab, val, fmt, note in glob:
    body(ws, r, [lab, val, note], fonts=[None, f_input, f_sub], fmt=[None, fmt, None], align=nowrap)
    r += 1
# rows 5..11 -> B5 core, B6 contrib, B7 years, B8 fx, B9 internal, B10 external, B11 selector
ws["A13"] = "Microsoft list prices (USD)"
ws["A13"].font = f_section
prices = [
    ("Power Apps Premium (per user/month)", 20, "S62, S64 - third-party guides citing Microsoft's price list"),
    ("Power BI Pro (per user/month)", 14, "S65, S66 - set to 0 if covered by Microsoft 365 E5"),
    ("Power Automate Premium (per user/month)", 15, "S64"),
    ("Fabric F2 capacity, pay-as-you-go (per month)", 263, "S65, S66; F4 and F8 are taken as 2x and 4x (linear capacity pricing)"),
    ("Fabric F2 capacity, reserved (per month)", 156, "S66"),
    ("Dataverse extra database capacity (per GB/month)", 40, "S62"),
]
r = 14
for lab, val, note in prices:
    body(ws, r, [lab, val, note], fonts=[None, f_input, f_sub], fmt=[None, EUR, None], align=nowrap)
    r += 1
# rows 14..19 -> B14 PA, B15 PBI, B16 PAu, B17 F2, B18 F2r, B19 DV
ws["A21"] = "Other inputs"
ws["A21"].font = f_section
other = [
    ("Measure-tracking tool: base fee per month incl. 10 users (EUR)", 1250, EUR, "S49 - third-party price information for Falcon"),
    ("Measure-tracking tool: fee per additional user/month (EUR)", 35, EUR, "S49"),
    ("Extra Dataverse capacity in the high case (GB)", 5, None, "Assumption"),
    ("Power Automate Premium licences for flow owners", 2, None, "Assumption"),
]
r = 22
for lab, val, fmt, note in other:
    body(ws, r, [lab, val, note], fonts=[None, f_input, f_sub], fmt=[None, fmt, None], align=nowrap)
    r += 1
# rows 22..25 -> B22 base fee, B23 per user, B24 GB, B25 flow owners

ws["A27"] = "Scenario inputs"
ws["A27"].font = f_section
header(ws, 28, ["Scenario", "Case", "Developer person-days", "Share built externally", "SME / internal project person-days",
                "External services, one-off (EUR)", "Licences per year (EUR)", "Run effort (person-days per year)", "Basis"], height=44)
U = "($B$5+$B$6)"
lic_formulas = {
    "IHA": ["=0", f"={U}*$B$15*12*$B$8", f"={U}*$B$15*12*$B$8"],
    "IHB": ["=$B$5*$B$14*12*$B$8",
            f"=({U}*($B$14+$B$15)*12+$B$25*$B$16*12)*$B$8",
            f"=({U}*($B$14+$B$15)*12+$B$25*$B$16*12+$B$24*$B$19*12)*$B$8"],
    "IHC": ["=($B$18*12+$B$5*$B$14*12)*$B$8",
            f"=(2*$B$17*12+{U}*$B$15*12+$B$5*$B$14*12)*$B$8",
            f"=(4*$B$17*12+{U}*$B$15*12+{U}*$B$14*12)*$B$8"],
}
basis = {
    "IHA": ["Power BI Pro already covered by Microsoft 365 E5", "Power BI Pro for all users", "As base"],
    "IHB": ["Power Apps Premium for editors only; others read in Power BI already licensed",
            "Power Apps Premium + Power BI Pro for all users, Power Automate Premium for flow owners", "Base + extra Dataverse capacity"],
    "IHC": ["F2 reserved + Power Apps Premium for editors", "F4 pay-as-you-go + Power BI Pro for all + Power Apps Premium for editors",
            "F8 pay-as-you-go + Power BI Pro and Power Apps Premium for all"],
    "EXT": ["No public price: low planning assumption", "No public price: base planning assumption", "No public price: high planning assumption (third-party signals for aPriori reach this level, S20/S21)"],
    "EXTC": ["PCM suite + measure tool for 10 users + small integration", "PCM suite + measure tool for all users + LCOH integration", "As base with high PCM licence"],
}
r = 29
row_of = {}
for key, label, cases in c.TCO_SCENARIOS:
    row_of[key] = r
    for i, case in enumerate(["Low", "Base", "High"]):
        dev, share, sme, ext, run = cases[i]
        if key in lic_formulas:
            lic = lic_formulas[key][i]
            lic_font, lic_fill = None, None
        elif key == "EXT":
            lic = c.EXT_LICENCE[i]
            lic_font, lic_fill = f_input, fill_yellow
        else:  # EXTC = EXT licence + measure tool
            ext_row = row_of["EXT"] + i
            if i == 0:
                lic = f"=G{ext_row}+$B$22*12"
            else:
                lic = f"=G{ext_row}+($B$22+MAX(0,{U}-10)*$B$23)*12"
            lic_font, lic_fill = None, None
        body(ws, r, [label, case, dev, share, sme, ext, lic, run, basis[key][i]],
             fonts=[f_bold if i == 0 else None, None, f_input, f_input, f_input, f_input, lic_font, f_input, f_sub],
             fmt=[None, None, EUR, PCT, EUR, EUR, EUR, EUR, None])
        if lic_fill:
            ws.cell(row=r, column=7).fill = lic_fill
        if key in ("EXT", "EXTC") :
            ws.cell(row=r, column=6).fill = fill_yellow
        if i == 1:
            for col in range(1, 9):
                if ws.cell(row=r, column=col).fill.start_color.rgb in (None, "00000000"):
                    ws.cell(row=r, column=col).fill = fill_grey
        r += 1
assert r == 44, r

ws["A45"] = "Selected case (set by the case selector in B11)"
ws["A45"].font = f_section
header(ws, 46, ["Scenario", "Case", "Developer person-days", "Share built externally", "SME / internal project person-days",
                "External services, one-off (EUR)", "Licences per year (EUR)", "Run effort (person-days per year)"], height=44)
r = 47
for key, label, _cases in c.TCO_SCENARIOS:
    a = row_of[key]
    vals = [label, '=CHOOSE($B$11,"Low","Base","High")'] + [f"=INDEX({L(col)}{a}:{L(col)}{a+2},$B$11)" for col in range(3, 9)]
    body(ws, r, vals, fonts=[f_bold] + [None] * 7, fmt=[None, None, EUR, PCT, EUR, EUR, EUR, EUR])
    r += 1
assert r == 52

ws["A53"] = "Results for the selected case (EUR over the horizon)"
ws["A53"].font = f_section
header(ws, 54, ["Scenario", "One-off internal effort", "One-off external (services, external developers)", "Licences over the horizon",
                "Run effort over the horizon", "Internal effort total", "Total cost", "of which cash-out", "Cost per user and year"], height=44)
r = 55
for i, (key, label, _cases) in enumerate(c.TCO_SCENARIOS):
    s = 47 + i
    vals = [
        label,
        f"=(C{s}*(1-D{s})+E{s})*$B$9",
        f"=C{s}*D{s}*$B$10+F{s}",
        f"=G{s}*$B$7",
        f"=H{s}*$B$9*$B$7",
        f"=B{r}+E{r}",
        f"=B{r}+C{r}+D{r}+E{r}",
        f"=C{r}+D{r}",
        f"=IF({U}*$B$7=0,0,G{r}/({U}*$B$7))",
    ]
    body(ws, r, vals, fonts=[f_bold, None, None, None, None, None, f_bold, None, None], fmt=[None] + [EUR] * 8)
    r += 1
assert r == 60

ws["A61"] = "All three cases side by side (total cost over the horizon, EUR)"
ws["A61"].font = f_section
header(ws, 62, ["Scenario", "Low", "Base", "High", "Cash-out, base"], height=30)
r = 63
for key, label, _cases in c.TCO_SCENARIOS:
    a = row_of[key]
    tot = lambda rr: f"=(C{rr}*(1-D{rr})+E{rr})*$B$9+C{rr}*D{rr}*$B$10+F{rr}+G{rr}*$B$7+H{rr}*$B$9*$B$7"
    cash = f"=C{a+1}*D{a+1}*$B$10+F{a+1}+G{a+1}*$B$7"
    body(ws, r, [label, tot(a), tot(a + 1), tot(a + 2), cash], fonts=[f_bold, None, f_bold, None, None], fmt=[None] + [EUR] * 4)
    r += 1

chart = BarChart()
chart.type = "bar"
chart.grouping = "stacked"
chart.overlap = 100
chart.style = 10
chart.title = "Cost over the horizon, selected case (EUR)"
chart.roundedCorners = False
data = Reference(ws, min_col=2, max_col=5, min_row=54, max_row=59)
cats = Reference(ws, min_col=1, min_row=55, max_row=59)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.title.overlay = False
chart.legend.overlay = False
chart.legend.position = "b"
chart.x_axis.delete = False
chart.y_axis.delete = False
chart.y_axis.number_format = "#,##0"
chart.height = 10
chart.width = 26
ws.add_chart(chart, "K28")
widths(ws, [52, 16, 24, 20, 20, 20, 18, 18, 60])
ws.freeze_panes = "B5"

# ---------------------------------------------------------------- Roadmap
ws = sheet("Roadmap", AMBER)
title(ws, "Roadmap for the in-house path (option B with a lean start)",
      "Start and end weeks are editable; the week plan on the right follows them. Effort figures are planning assumptions.")
header(ws, 4, ["Phase", "Name", "Start week", "End week", "Developer person-days", "SME person-days", "Goal", "Work packages", "Result / gate"]
       + [str(w) for w in range(1, 31)], height=44)
r = 5
for ph, name, s, e, dev, sme, goal, wps, gate in c.ROADMAP:
    body(ws, r, [ph, name, s, e, dev, sme, goal, "\n".join("- " + w for w in wps), gate],
         fonts=[f_bold, f_bold, f_input, f_input, f_input, f_input, None, None, None])
    for w in range(1, 31):
        cell = ws.cell(row=r, column=9 + w, value=None)
        cell.border = border
    ws.row_dimensions[r].height = 105
    r += 1
rm_first, rm_last = 5, r - 1
name, dev, sme = c.ROADMAP_OVERHEAD
body(ws, r, ["-", name, None, None, dev, sme, None, None, None], fonts=[f_bold, None, None, None, f_input, f_input, None, None, None])
r += 1
body(ws, r, [None, "Total", None, None, f"=SUM(E{rm_first}:E{r-1})", f"=SUM(F{rm_first}:F{r-1})", None, None, None],
     fonts=[None, f_bold, None, None, f_bold, f_bold, None, None, None], fill=fill_sub)
r += 1
body(ws, r, [None, "Duration in weeks", None, f"=MAX(D{rm_first}:D{rm_last})", None, None, None, None, None],
     fonts=[None, f_bold, None, f_bold, None, None, None, None, None], fill=fill_sub)
ws.conditional_formatting.add(
    f"J{rm_first}:AM{rm_last}",
    FormulaRule(formula=[f"AND(VALUE(J$4)>=$C{rm_first},VALUE(J$4)<=$D{rm_first})"], fill=PatternFill("solid", start_color=TEAL)))
r += 2
ws.cell(row=r, column=1, value="Team").font = f_section
r += 1
header(ws, r, ["Role", None, "Who", None, None, None, "Responsibility", "Load", None])
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)
r += 1
for role, who, resp, load in c.ROLES:
    body(ws, r, [role, None, who, None, None, None, resp, load, None], fonts=[f_bold] + [None] * 8)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)
    ws.row_dimensions[r].height = 28
    r += 1
widths(ws, [8, 26, 8, 8, 11, 9, 34, 60, 40] + [3.2] * 30)
ws.freeze_panes = "C5"

# ---------------------------------------------------------------- Teamcenter interface
ws = sheet("Teamcenter interface", AMBER)
title(ws, "Routes for the Teamcenter interface (requirement R5)",
      "To be validated with PLM IT. First clarify where prices and suppliers are really maintained.")
header(ws, 4, ["ID", "Route", "How it works", "Effort", "Precondition", "Limit", "When", "Finding from PLM IT"])
r = 5
for row in c.TC_ROUTES:
    body(ws, r, [*row, None], fonts=[f_bold, f_bold, None, None, None, None, None, f_input])
    ws.cell(row=r, column=8).fill = fill_yellow
    r += 1
widths(ws, [6, 30, 60, 22, 44, 50, 24, 40])

# ---------------------------------------------------------------- Risks
ws = sheet("Risks", AMBER)
title(ws, "Risk register", "Impact and likelihood: High / Medium / Low. Owner and status are for the project team.")
header(ws, 4, ["#", "Applies to", "Risk", "Impact", "Likelihood", "Mitigation", "Owner", "Status"])
r = 5
for i, row in enumerate(c.RISKS, start=1):
    body(ws, r, [i, *row, None, None], fonts=[None, f_bold, None, None, None, None, f_input, f_input])
    r += 1
for col in ("D", "E"):
    ws.conditional_formatting.add(f"{col}5:{col}{r-1}", CellIsRule(operator="equal", formula=['"High"'], fill=PatternFill("solid", start_color="F4B6A6")))
    ws.conditional_formatting.add(f"{col}5:{col}{r-1}", CellIsRule(operator="equal", formula=['"Medium"'], fill=PatternFill("solid", start_color="FBF3D0")))
    ws.conditional_formatting.add(f"{col}5:{col}{r-1}", CellIsRule(operator="equal", formula=['"Low"'], fill=PatternFill("solid", start_color="CDE8DC")))
widths(ws, [4, 12, 56, 10, 11, 70, 16, 14])
ws.freeze_panes = "C5"

# ---------------------------------------------------------------- RFI and open questions
ws = sheet("RFI and open questions", AMBER)
title(ws, "Open questions and RFI checklist", "Fill the yellow column as answers come in.")
header(ws, 4, ["#", "Type", "Question", "Addressee", "Answer / finding", "Date"])
r = 5
for i, (typ, q, who) in enumerate(c.OPEN_QUESTIONS, start=1):
    body(ws, r, [i, typ, q, who, None, None], fonts=[None, f_bold, None, None, f_input, f_input])
    ws.cell(row=r, column=5).fill = fill_yellow
    r += 1
ws.cell(row=r + 1, column=1, value="Example answer: 'Teamcenter 2412 with Active Workspace; prices are maintained in ERP, supplier in Teamcenter vendor part' - 20 Nov 2026.").font = f_sub
widths(ws, [4, 14, 80, 28, 60, 12])
ws.freeze_panes = "C5"

# ---------------------------------------------------------------- H2 cost references
ws = sheet("H2 cost references", TEAL)
title(ws, "Public cost references for benchmarking and calibration",
      "Seed data for the benchmark table (R9) and sanity checks for scaling and regional logic (R7, R8). Check scope and year before use.")
header(ws, 4, ["Metric", "Value", "Origin", "Source ID"])
r = 5
for row in c.H2_BENCHMARKS:
    body(ws, r, list(row), fonts=[f_bold, None, None, None])
    r += 1
widths(ws, [56, 56, 70, 10])

# ---------------------------------------------------------------- Sources
ws = sheet("Sources", "888888")
title(ws, "Sources", "Collected by web search on 13 Nov 2026. Vendor pages could not be opened directly from the research environment; facts come from search extracts of these pages.")
header(ws, 4, ["ID", "Source", "Link", "Type"])
r = 5
for sid, name, url, typ in c.SOURCES:
    body(ws, r, [sid, name, url, typ], fonts=[f_bold, None, None, None])
    cell = ws.cell(row=r, column=3)
    cell.hyperlink = url
    cell.font = Font(name=FONT, size=10, color="0563C1", underline="single")
    r += 1
widths(ws, [6, 80, 90, 22])
ws.freeze_panes = "B5"

wb.save(OUT)
print("saved", os.path.abspath(OUT))
