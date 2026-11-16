/* Build the research deck from content.json.
 *
 * Usage: node build_pptx.js [output.pptx]
 * Needs: pptxgenjs, react, react-dom, react-icons, sharp and the pptx skill's apply_theme.js
 * (set PPTX_SKILL_DIR to the skill directory).
 */
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const D = require("./content.json");

const SKILL = process.env.PPTX_SKILL_DIR;
const { applyTheme } = require(path.join(SKILL, "scripts", "apply_theme.js"));
const OUT = process.argv[2] || path.join(__dirname, "..", "cost-down-tool_make-or-buy-research.pptx");

const THEME = {
  name: "Cost-down research",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "12262B", lt1: "FFFFFF", dk2: "0E4D5B", lt2: "EDF3F2",
    accent1: "0E7C7B", accent2: "F4A259", accent3: "5B8E7D", accent4: "BC4B51",
    accent5: "7FA650", accent6: "66757A", hlink: "0E7C7B", folHlink: "5B8E7D",
  },
};
const H = THEME.colors;
const LINE = "C9D6D4";
const HEAT = ["F2B5A7", "FAE3B4", "D5E8C4", "86C9A8"];
const FOOT = "Cost-down tool · in-house or external? · research status November 2026";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Cost-down tool: in-house or external?";
pres.subject = "Research basis for the make-or-buy decision";
pres.author = "Product cost research";
const C = pres.SchemeColor;

const W = 13.333, MX = 0.6, CW = W - 2 * MX;

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: H.dk2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.2, w: 8.6, h: 1.9, fontSize: 44, bold: true, color: C.background1, align: "left", valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.3, w: 8.6, h: 1.2, fontSize: 20, color: C.background2, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "SECTION_DARK",
  background: { color: H.dk2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.5, w: 9.0, h: 1.4, fontSize: 40, bold: true, color: C.background1, align: "left", valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.1, w: 9.0, h: 1.2, fontSize: 18, color: C.background2, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: H.lt1 },
  margin: [0.6, 0.6, 0.7, 0.6],
  objects: [
    { text: { text: FOOT, options: { x: MX, y: 7.03, w: 9, h: 0.3, fontSize: 10, color: C.accent6, margin: 0 } } },
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.35, w: CW, h: 0.85, fontSize: 32, bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.13, y: 7.03, w: 0.6, h: 0.3, fontSize: 10, color: C.accent6, align: "right" },
});

// ---------------------------------------------------------------- helpers
const iconCache = {};
async function icon(name, hex = "FFFFFF") {
  const key = name + hex;
  if (!iconCache[key]) {
    const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fa[name], { color: "#" + hex, size: 256 }));
    const buf = await sharp(Buffer.from(svg)).resize(256, 256, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toBuffer();
    iconCache[key] = "image/png;base64," + buf.toString("base64");
  }
  return iconCache[key];
}

let objN = 0;
const nm = (p) => `${p} ${++objN}`;

function txt(slide, text, o) {
  slide.addText(text, Object.assign({ isTextBox: true, margin: 0, fontSize: 14, color: C.text1, valign: "top", align: "left", objectName: nm("Text") }, o));
}
function card(slide, x, y, w, h, o = {}) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({
    x, y, w, h, rectRadius: 0.08, fill: { color: o.fill || C.background2 }, line: { color: o.line || o.fill || C.background2, width: 0.75 }, objectName: nm("Card"),
  }, o.extra || {}));
}
async function iconCircle(slide, name, x, y, d, color) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: color || C.accent1 }, line: { color: color || C.accent1, width: 0 }, objectName: nm("Icon circle") });
  const pad = d * 0.25;
  slide.addImage({ data: await icon(name), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, altText: name.replace(/^Fa/, "") + " icon", objectName: nm("Icon") });
}
function numCircle(slide, n, x, y, d, color) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: color || C.accent1 }, line: { color: color || C.accent1, width: 0 }, objectName: nm("Number circle") });
  txt(slide, String(n), { x, y, w: d, h: d, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle" });
}
function bullets(items, o = {}) {
  return items.map((t, i) => ({ text: t, options: Object.assign({ bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: o.space == null ? 5 : o.space }, o.run || {}) }));
}
function sourceNote(slide, text) {
  txt(slide, text, { x: MX, y: 6.68, w: CW, h: 0.28, fontSize: 10, color: C.accent6, valign: "middle" });
}
function headCell(t, o = {}) {
  return { text: t, options: Object.assign({ bold: true, color: C.background1, fill: { color: H.dk2 }, fontSize: 11, valign: "middle", align: "left" }, o) };
}
function cell(t, o = {}) {
  return { text: t, options: Object.assign({ color: C.text1, fontSize: 11, valign: "top", align: "left" }, o) };
}
function table(slide, rows, o) {
  slide.addTable(rows, Object.assign({
    border: { type: "solid", pt: 0.5, color: LINE }, fontSize: 11, margin: [0.05, 0.08, 0.05, 0.08], color: C.text1, objectName: nm("Table"),
  }, o));
}
function stat(slide, x, y, w, big, small, color) {
  txt(slide, big, { x, y, w, h: 0.62, fontSize: 28, bold: true, color: color || C.accent1, valign: "middle" });
  txt(slide, small, { x, y: y + 0.62, w, h: 0.5, fontSize: 11, color: C.accent6 });
}
function content(sectionTitle, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle });
  s.addText(title, { placeholder: "title" });
  return s;
}
function decor(slide) {
  // large translucent circles, the same motif as the icon circles
  slide.addShape(pres.shapes.OVAL, { x: 9.4, y: -1.2, w: 5.6, h: 5.6, fill: { color: H.accent1, transparency: 55 }, line: { color: H.accent1, width: 0, transparency: 100 }, objectName: nm("Decor") });
  slide.addShape(pres.shapes.OVAL, { x: 10.9, y: 3.6, w: 3.6, h: 3.6, fill: { color: H.accent2, transparency: 25 }, line: { color: H.accent2, width: 0, transparency: 100 }, objectName: nm("Decor") });
  slide.addShape(pres.shapes.OVAL, { x: 8.7, y: 5.3, w: 1.5, h: 1.5, fill: { color: H.lt1, transparency: 85 }, line: { color: H.lt1, width: 0, transparency: 100 }, objectName: nm("Decor") });
}
const k = (n) => Math.round(n / 1000);
const cap = (t) => t.charAt(0).toUpperCase() + t.slice(1);
const fmtM = (n) => (n / 1e6).toFixed(2);
const sol = (key) => D.solutions.find((s) => s[0] === key);
const fitSum = (key) => D.fit[key].reduce((a, b) => a + b, 0);
const tco = (key) => D.tco.find((t) => t.key === key).cases;

// ================================================================= build
(async () => {
  let S;

  // ------------------------------------------------------------- 1 title
  S = "Summary";
  pres.addSection({ title: S });
  let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: S });
  decor(s);
  s.addText("Cost-down tool: in-house or external?", { placeholder: "title" });
  s.addText("Research basis for the make-or-buy decision on a product-cost monitoring tool", { placeholder: "body" });
  txt(s, "Status 13 November 2026 · desk research · no vendor contacted yet", { x: 0.8, y: 6.5, w: 8.6, h: 0.35, fontSize: 12, color: C.background2 });
  s.addNotes("Compiled research for the make-or-buy decision. Companion files: research dossier (full reasoning and sources) and decision workbook (editable matrices and cost model). All external prices are planning assumptions, not quotes.");

  // ------------------------------------------------------------- 2 executive summary
  s = content(S, "In-house on the Power Platform fits best");
  const findings = [
    ["No external product covers all requirements", "The list spans product costing, TIC estimating and measure management. Best external fit: 23 of 39 points."],
    ["External tools solve a different problem", "They calculate what a manufactured part should cost. Needed here: transparency by scope, engineering hours and TIC."],
    ["The Microsoft platform is already in use", "The LCOH Suite is a Power App. A second app on the same data platform delivers the required interface."],
    ["In-house costs less and needs little cash", "Five years: about EUR 0.5M vs. 0.9M in total, EUR 0.18M vs. 0.7M cash-out (planning assumptions)."],
    ["Buying still has real advantages", "Shipped reference data, lower key-person risk, available today. Teamcenter PCM is the fallback."],
  ];
  findings.forEach((f, i) => {
    const y = 1.5 + i * 1.0;
    numCircle(s, i + 1, MX, y + 0.03, 0.42);
    txt(s, f[0], { x: MX + 0.6, y, w: 6.7, h: 0.34, fontSize: 16, bold: true, color: C.text2 });
    txt(s, f[1], { x: MX + 0.6, y: y + 0.36, w: 6.7, h: 0.56, fontSize: 13 });
  });
  card(s, 8.3, 1.5, 4.43, 5.0, { fill: H.dk2 });
  txt(s, "Recommendation", { x: 8.6, y: 1.7, w: 3.9, h: 0.35, fontSize: 12, bold: true, color: C.accent2, charSpacing: 1 });
  txt(s, "Build option B, start lean, keep two exit gates, and run an RFI in parallel.", { x: 8.6, y: 2.05, w: 3.9, h: 1.15, fontSize: 18, bold: true, color: C.background1 });
  const st = [["37 / 39", "requirement fit of in-house B; best external product reaches 23"], ["10-12 weeks", "to a usable MVP after the go decision"], ["EUR 0.18M", "cash-out over five years; EUR 0.5M including internal effort"]];
  st.forEach((v, i) => {
    const y = 3.35 + i * 1.03;
    txt(s, v[0], { x: 8.6, y, w: 3.9, h: 0.5, fontSize: 26, bold: true, color: C.accent2, valign: "middle" });
    txt(s, v[1], { x: 8.6, y: y + 0.5, w: 3.9, h: 0.45, fontSize: 11, color: C.background2 });
  });
  sourceNote(s, "Fit and cost figures are a preliminary desk assessment; external prices are not published and must be confirmed by RFI.");
  s.addNotes("Key message: the requirement list is broader than any single product category. In-house option B scores 37 of 39 fit points and 4.07 of 5 in the weighted scoring; Teamcenter PCM is the best external product with 23 points and 3.03. Cost: in-house B EUR 503,560 over five years (range 329k-677k), external PCM suite EUR 892,000 (range 488k-1,592k). See dossier chapters 1 and 9.");

  // ------------------------------------------------------------- 3 requirements
  s = content(S, "Thirteen requirements in four blocks");
  const blocks = [
    ["1 Cost transparency", "FaSearchDollar", "Status quo at detail level"],
    ["2 Scenario simulation", "FaProjectDiagram", "Cost for any project size and site"],
    ["3 Target costs & tracking", "FaBullseye", "From benchmark to tracked measure"],
    ["4 LCOH Suite", "FaLink", "Feed the existing Power App"],
  ];
  const bw = 2.86, bg = 0.23;
  for (let i = 0; i < blocks.length; i++) {
    const [name, ic, tag] = blocks[i];
    const x = MX + i * (bw + bg);
    card(s, x, 1.5, bw, 3.3);
    await iconCircle(s, ic, x + 0.25, 1.68, 0.6, i === 3 ? C.accent2 : C.accent1);
    txt(s, name, { x: x + 1.0, y: 1.68, w: bw - 1.15, h: 0.6, fontSize: 15, bold: true, color: C.text2, valign: "middle" });
    txt(s, tag, { x: x + 0.25, y: 2.38, w: bw - 0.5, h: 0.3, fontSize: 11, italic: true, color: C.accent6 });
    const reqs = D.requirements.filter((r) => r[1] === name);
    const runs = [];
    reqs.forEach((r, j) => {
      runs.push({ text: r[0] + "  ", options: { bold: true, color: C.accent1 } });
      runs.push({ text: r[2], options: { breakLine: j < reqs.length - 1, paraSpaceAfter: 5 } });
    });
    txt(s, runs, { x: x + 0.25, y: 2.78, w: bw - 0.5, h: 1.95, fontSize: 13 });
  }
  const impl = [
    ["R7 and R8 are plant topics", "Costing tools scale with production volume and manufacturing site. Needed here: plant size and construction site."],
    ["R3 exists in no standard product", "The feature-to-TIC mapping has to be configured or built in every option, bought or made."],
    ["R9 depends on data, not software", "No tool ships competitor cost data for green-hydrogen plants. Public studies can seed the table."],
  ];
  const iw = (CW - 2 * bg) / 3;
  impl.forEach((v, i) => {
    const x = MX + i * (iw + bg);
    card(s, x, 5.0, iw, 1.5, { fill: H.dk2 });
    txt(s, v[0], { x: x + 0.25, y: 5.1, w: iw - 0.5, h: 0.4, fontSize: 14, bold: true, color: C.accent2, valign: "middle" });
    txt(s, v[1], { x: x + 0.25, y: 5.52, w: iw - 0.5, h: 0.9, fontSize: 12, color: C.background1 });
  });
  sourceNote(s, "Derived from the first brainstorming in the task description. Priorities are still to be confirmed in the requirements catalogue with Product gH2 and R&D.");
  s.addNotes(D.requirements.map((r) => `${r[0]} ${r[3]} (original: ${r[4]}; proposed priority: ${r[5]})`).join("\n"));

  // ------------------------------------------------------------- 4 three categories
  s = content(S, "The requirements span three software categories");
  const cats = [
    ["Product cost management", "FaCubes", "R1 R2 R4 R6 R10", "Roll-up over product structures, versions, target costing, should-cost", "Teamcenter PCM, aPriori, FACTON, Tset", C.accent1],
    ["TIC / capital-project estimating", "FaIndustry", "R7 R8 (R9)", "Plant-size scaling, construction location factors, project benchmarks", "Cleopatra, Aspen ACCE, CostOS", C.accent1],
    ["Savings / measure management", "FaLightbulb", "R11 R12", "Idea capture, measure list, degree of implementation, tracking", "Valuedesk, Falcon", C.accent1],
    ["Specific to this organisation", "FaPuzzlePiece", "R3 R5 R9 R13", "Feature-to-TIC mapping, Teamcenter prices, competitor data, LCOH Suite link", "No standard product", C.accent2],
  ];
  for (let i = 0; i < cats.length; i++) {
    const [name, ic, rs, what, prod, col] = cats[i];
    const x = MX + i * (bw + bg);
    card(s, x, 1.5, bw, 3.75);
    await iconCircle(s, ic, x + 0.25, 1.72, 0.6, col);
    txt(s, name, { x: x + 1.0, y: 1.72, w: bw - 1.15, h: 0.6, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    txt(s, rs, { x: x + 0.25, y: 2.5, w: bw - 0.5, h: 0.32, fontSize: 13, bold: true, color: i === 3 ? C.accent4 : C.accent1 });
    txt(s, what, { x: x + 0.25, y: 2.9, w: bw - 0.5, h: 1.15, fontSize: 12 });
    txt(s, "Products", { x: x + 0.25, y: 4.15, w: bw - 0.5, h: 0.25, fontSize: 10, bold: true, color: C.accent6 });
    txt(s, prod, { x: x + 0.25, y: 4.4, w: bw - 0.5, h: 0.7, fontSize: 12 });
  }
  card(s, MX, 5.5, CW, 1.0, { fill: H.dk2 });
  txt(s, [
    { text: "Consequence: ", options: { bold: true, color: C.accent2 } },
    { text: "buying means at least two products plus custom integration. The best single product, Teamcenter PCM, reaches 23 of 39 fit points; an in-house design reaches 37.", options: { color: C.background1 } },
  ], { x: MX + 0.3, y: 5.5, w: CW - 0.6, h: 1.0, fontSize: 15, valign: "middle" });
  s.addNotes("R1, R2, R4, R6 and R10 are classic product-cost-management functions. R7 and R8 concern total installed cost of a plant: PCM tools model production volume and manufacturing site, capital-project estimating tools model plant size and construction site. R11 and R12 are savings-management functions. R3, R13 and competitor data for R9 are specific to the organisation. Dossier chapter 2.");

  // ------------------------------------------------------------- 5 section external
  S = "External solutions";
  pres.addSection({ title: S });
  s = pres.addSlide({ masterName: "SECTION_DARK", sectionTitle: S });
  decor(s);
  s.addText("External solutions", { placeholder: "title" });
  s.addText("Market landscape, a shortlist of five and the KPIs for the decision", { placeholder: "body" });

  // ------------------------------------------------------------- 6 landscape
  s = content(S, "Eighteen products screened in five categories");
  const land = [
    ["Product cost management", ["Teamcenter PCM*", "aPriori*", "FACTON EPC*", "Tset*", "SAP Product Lifecycle Costing", "DFMA Should Costing", "Costimator"], "Covers R1 R2 R4 R6 R10"],
    ["TIC / capital-project estimating", ["Cleopatra Enterprise*", "Aspen Capital Cost Estimator", "CostOS", "EcoSys"], "Covers R7 R8 and project benchmarks"],
    ["Parametric estimating", ["SEER", "TruePlanning", "4cost-aces"], "Early estimates; aerospace and defence heritage"],
    ["Savings / measure management", ["Valuedesk+", "Falcon+"], "Covers R11 R12"],
    ["Data and platforms", ["costdata+", "Mendix with Teamcenter Connector+"], "Inputs for an own tool"],
  ];
  const lw = 2.26, lg = 0.2;
  land.forEach((col, i) => {
    const x = MX + i * (lw + lg);
    card(s, x, 1.5, lw, 4.6);
    txt(s, col[0], { x: x + 0.2, y: 1.65, w: lw - 0.4, h: 0.62, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    const runs = col[1].map((p, j) => {
      const short = p.endsWith("*"), comp = p.endsWith("+");
      return { text: p.replace(/[*+]$/, ""), options: { bold: short, italic: comp, color: short ? C.accent1 : C.text1, breakLine: j < col[1].length - 1, paraSpaceAfter: 7 } };
    });
    txt(s, runs, { x: x + 0.2, y: 2.4, w: lw - 0.4, h: 2.75, fontSize: 12 });
    txt(s, col[2], { x: x + 0.2, y: 5.25, w: lw - 0.4, h: 0.7, fontSize: 10, color: C.accent6, valign: "bottom" });
  });
  txt(s, [
    { text: "Bold teal", options: { bold: true, color: C.accent1 } }, { text: " = shortlisted      " },
    { text: "Italic", options: { italic: true } }, { text: " = complement that covers one part only" },
  ], { x: MX, y: 6.25, w: CW, h: 0.3, fontSize: 11, color: C.accent6 });
  sourceNote(s, "Sources: vendor sites and review platforms (S1-S56). Full list with relevance rating in the workbook, sheet 'Long list'.");
  s.addNotes("SAP Product Lifecycle Costing is only relevant if the SAP landscape is the cost master; SAP describes a continuing roadmap (S54). Aspen ACCE uses design-based installation models with five to six regional bases (S52). CostOS is listed from USD 2,800 per user on Capterra (S53). 4cost was not researched in depth.");

  // ------------------------------------------------------------- 7 shortlist
  s = content(S, "Five products shortlisted, one per way of buying");
  const sl = [
    ["Teamcenter PCM", "PLM-native costing", "Same vendor as the PLM; imports product structures from Teamcenter directly", "TCPCM", "No plant-size scaling, no ideas or measures"],
    ["aPriori", "CAD-driven should-cost", "Market reference for automatic cost-driver analysis of manufactured parts", "APRIORI", "Needs 3D CAD; part level only"],
    ["FACTON EPC", "Enterprise costing suite", "German vendor; versioning and target costing; plant-engineering references", "FACTON", "Teamcenter link not confirmed"],
    ["Tset", "SaaS, API-first", "Own Excel logic can be migrated into versioned calculators", "TSET", "Teamcenter interface is a project"],
    ["Cleopatra Enterprise", "TIC estimating", "Only tool built for location factors, scaling and project benchmarks", "CLEO", "No BOM or Teamcenter costing"],
  ];
  const rows7 = [[headCell("Product"), headCell("Type"), headCell("Why it is on the list"), headCell("Fit (of 39)", { align: "center" }), headCell("Biggest gap")]];
  sl.forEach((r) => rows7.push([
    cell(r[0], { bold: true, color: C.text2, fontSize: 13 }), cell(r[1], { fontSize: 12 }), cell(r[2], { fontSize: 12 }),
    cell(String(fitSum(r[3])), { bold: true, fontSize: 16, align: "center", valign: "middle", color: C.accent1 }), cell(r[4], { fontSize: 12 }),
  ]));
  table(s, rows7, { x: MX, y: 1.5, w: CW, colW: [2.3, 2.2, 4.33, 1.1, 2.2], rowH: [0.45, 0.84, 0.84, 0.84, 0.84, 0.84] });
  txt(s, "For comparison: the in-house target design reaches 37 points (option B). Scores are a desk assessment and need confirmation in scripted demos.", { x: MX, y: 6.3, w: CW, h: 0.4, fontSize: 13, italic: true, color: C.accent6, valign: "middle" });
  s.addNotes("Fit scale per requirement: 0 not covered, 1 workaround, 2 largely covered by configuration, 3 native. Rationale per product is in the workbook sheet 'Fit matrix' and dossier chapter 4.");

  // ------------------------------------------------------------- 8-12 profiles
  const profiles = [
    { key: "TCPCM", title: "Teamcenter PCM: the Teamcenter-native option",
      what: "Siemens' costing application for product and tool costing, profitability, should-cost and CO2e. Two releases per year; the current one is 2606.",
      facts: ["Imports product structures directly from Teamcenter, including make-or-buy, plant and technology attributes",
        "Knowledge base for 67 countries and 454 regions: labour, floor space, interest, energy, machines, about 10,000 materials",
        "Own REST interface; release 2606 adds a KPI endpoint for Power BI",
        "Versions and what-if scenarios; target costing is a documented use case",
        "On-premises or SaaS (Teamcenter X); named-user licences plus modules"],
      tiles: [["Teamcenter link", "Native"], ["Implementation", "4-9 months*"], ["Reference data", "67 countries"], ["Price signal", "None published"]],
      plus: "Teamcenter-native, strongest shipped data, lowest vendor risk",
      minus: "No plant-size scaling or construction factors, no ideas or measures, LCOH link only through the API",
      src: "Sources: S1, S5, S6, S7, S11, S12, S14   * planning assumption" },
    { key: "APRIORI", title: "aPriori: automatic should-cost from 3D CAD",
      what: "US platform that simulates manufacturing cost and manufacturability from 3D CAD geometry for design, sourcing and quoting.",
      facts: ["More than 450 manufacturing process simulations and 95 regional data libraries",
        "Standard PLM integration with Teamcenter and Windchill",
        "Named users on annual subscription; package sized by deployment",
        "Third parties estimate USD 4,000-17,000 per month to start and USD 35,000-175,000 one-off",
        "G2 reviews: about 6 months to implement, 18 months to return on investment"],
      tiles: [["Teamcenter link", "Standard"], ["Implementation", "about 6 months"], ["Reference data", "95 regions"], ["Price signal", "USD 48-204k / yr"]],
      plus: "Deepest automatic cost-driver insight for manufactured parts",
      minus: "Needs 3D CAD; little value for engineering hours, EPC scope, TIC and measures; expensive end of the market",
      src: "Sources: S17, S18, S19, S20, S21, S22   Price signal is a third-party estimate" },
    { key: "FACTON", title: "FACTON EPC: enterprise costing suite from Germany",
      what: "Enterprise costing suite for quotation calculation, should costing, design-to-cost, cost controlling, reporting and product carbon footprint.",
      facts: ["Versioning, simulation and target costing are core concepts",
        "Editions Standard and Professional plus add-on modules; on-premises or SaaS",
        "ERP and PLM interfaces; Windchill and Power BI are named publicly, Teamcenter is not",
        "Benchmark data for wages, overheads and machines",
        "Customers include Airbus, Porsche, Deutz, mtu, Wittenstein, MAHLE and Hauni"],
      tiles: [["Teamcenter link", "To be confirmed"], ["Implementation", "4-9 months*"], ["Reference data", "Wages, machines"], ["Price signal", "None published"]],
      plus: "Strong versioning and target costing; references in mechanical and plant engineering",
      minus: "Teamcenter link unclear; TIC scaling and regions only by customisation; no ideas or measures",
      src: "Sources: S24, S25, S26, S27, S28, S29, S30   * planning assumption" },
    { key: "TSET", title: "Tset: flexible SaaS with an open API",
      what: "Vienna-based SaaS for product cost and CO2e calculation. Founded 2018, Series A of about EUR 13M, 70 to 100+ employees.",
      facts: ["More than 50 calculation modules and market data for 79 countries",
        "Tset Studio: build calculators or migrate own Excel logic; calculators are versioned",
        "API-first: Brose IT built a SAP workflow on the open API",
        "Customers: AGCO, Brose, Lego, thyssenkrupp, ZF and BMW Group",
        "SaaS pricing by company size, usage and features; no figures published"],
      tiles: [["Teamcenter link", "Project via API"], ["Implementation", "3-6 months*"], ["Reference data", "79 countries"], ["Price signal", "None published"]],
      plus: "Most adaptable external tool: own logic instead of a fixed method",
      minus: "Teamcenter interface must be built; automotive heritage; younger vendor; no ideas or measures",
      src: "Sources: S31, S32, S33, S35, S36, S37, S38   * planning assumption" },
    { key: "CLEO", title: "Cleopatra Enterprise: built for TIC estimating",
      what: "Dutch software for capital-project cost estimating, cost control and benchmarking in process industries, energy and EPC.",
      facts: ["Location-factor tables, smart cost models and flexible breakdown structures",
        "Vendor states support for all AACE estimating methods",
        "Benchmarking of own projects, normalised for location and time",
        "Integrates with SAP, Excel, Power BI and Oracle P6; no Teamcenter link found",
        "Standard and Professional editions, cloud or on-premises; ITER is a published user"],
      tiles: [["Teamcenter link", "None found"], ["Implementation", "3-6 months*"], ["Reference data", "CESK cost data"], ["Price signal", "None published"]],
      plus: "Only shortlisted tool that models plant size, region and EPC scope natively",
      minus: "Not a product-costing tool: no BOM logic, no Teamcenter, no feature mapping, no measures",
      src: "Sources: S39, S40, S41, S42, S43, S44   * planning assumption" },
  ];
  for (const p of profiles) {
    s = content(S, p.title);
    txt(s, p.what, { x: MX, y: 1.5, w: 6.5, h: 0.8, fontSize: 15, color: C.text2 });
    txt(s, bullets(p.facts, { space: 7 }), { x: MX, y: 2.42, w: 6.5, h: 2.75, fontSize: 14 });
    txt(s, "Fit by requirement block", { x: MX, y: 5.22, w: 6.5, h: 0.26, fontSize: 11, bold: true, color: C.accent6 });
    const blk = [["Cost transparency", 0, 6], ["Scenarios", 6, 8], ["Targets & tracking", 8, 12], ["LCOH link", 12, 13]];
    const bkw = (6.5 - 3 * 0.14) / 4;
    blk.forEach((b, i) => {
      const got = D.fit[p.key].slice(b[1], b[2]).reduce((a, v) => a + v, 0), max = 3 * (b[2] - b[1]);
      const x = MX + i * (bkw + 0.14), y = 5.52;
      card(s, x, y, bkw, 0.98);
      txt(s, b[0], { x: x + 0.12, y: y + 0.07, w: bkw - 0.24, h: 0.24, fontSize: 10, color: C.accent6 });
      txt(s, `${got} of ${max}`, { x: x + 0.12, y: y + 0.31, w: bkw - 0.24, h: 0.32, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
      s.addShape(pres.shapes.RECTANGLE, { x: x + 0.12, y: y + 0.72, w: bkw - 0.24, h: 0.1, fill: { color: C.background1 }, line: { color: C.background1, width: 0 }, objectName: nm("Bar track") });
      if (got > 0) s.addShape(pres.shapes.RECTANGLE, { x: x + 0.12, y: y + 0.72, w: (bkw - 0.24) * got / max, h: 0.1, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 }, objectName: nm("Bar value") });
    });
    // fit badge
    const rx = 7.55, rw = W - MX - rx;
    card(s, rx, 1.5, 1.6, 1.55, { fill: H.dk2 });
    txt(s, `${fitSum(p.key)}`, { x: rx, y: 1.58, w: 1.6, h: 0.75, fontSize: 36, bold: true, color: C.accent2, align: "center", valign: "middle" });
    txt(s, "of 39 fit points", { x: rx, y: 2.35, w: 1.6, h: 0.5, fontSize: 11, color: C.background1, align: "center" });
    const tw = (rw - 1.6 - 0.15 - 0.15) / 2;
    p.tiles.forEach((t, i) => {
      const x = rx + 1.75 + (i % 2) * (tw + 0.15), y = 1.5 + Math.floor(i / 2) * 0.82;
      card(s, x, y, tw, 0.73);
      txt(s, t[0], { x: x + 0.12, y: y + 0.06, w: tw - 0.24, h: 0.24, fontSize: 10, color: C.accent6 });
      txt(s, t[1], { x: x + 0.12, y: y + 0.3, w: tw - 0.24, h: 0.38, fontSize: 13, bold: true, color: C.text2, valign: "middle" });
    });
    card(s, rx, 3.3, rw, 1.45);
    await iconCircle(s, "FaCheck", rx + 0.2, 3.5, 0.5, C.accent5);
    txt(s, "Strength for this use case", { x: rx + 0.9, y: 3.42, w: rw - 1.1, h: 0.3, fontSize: 11, bold: true, color: C.accent6 });
    txt(s, p.plus, { x: rx + 0.9, y: 3.72, w: rw - 1.1, h: 0.95, fontSize: 13 });
    card(s, rx, 4.95, rw, 1.55);
    await iconCircle(s, "FaTimes", rx + 0.2, 5.15, 0.5, C.accent4);
    txt(s, "Gap against the requirements", { x: rx + 0.9, y: 5.07, w: rw - 1.1, h: 0.3, fontSize: 11, bold: true, color: C.accent6 });
    txt(s, p.minus, { x: rx + 0.9, y: 5.37, w: rw - 1.1, h: 1.05, fontSize: 13 });
    sourceNote(s, p.src);
    const kp = D.ext_kpis[p.key];
    s.addNotes(D.ext_kpi_rows.map((r, i) => `${r}: ${kp[i]}`).join("\n") + `\nFit rationale: ${D.fit_rationale[p.key]}`);
  }

  // ------------------------------------------------------------- 13 complementary
  s = content(S, "Four products can fill a gap, none solves the task");
  const comp = [
    ["Valuedesk", "FaLightbulb", "Savings / measure management", "Captures ideas, runs and measures savings measures; dashboards and a catalogue of methods", "Packages from 10 users and 200 measures; prices on request", "Covers R11 and R12, has no cost model"],
    ["Falcon", "FaTasks", "Measure tracking", "Tracks measure programmes with degree-of-implementation reporting", "Third-party information: EUR 1,250 per month incl. 10 users, EUR 35 per further user", "Covers R12"],
    ["costdata", "FaDatabase", "Benchmark data", "Database for 130+ countries: wages, machine rates, material prices, location factors", "Sold as data package alone; prices on request", "Buy the data, build the tool"],
    ["Mendix + Teamcenter Connector", "FaCode", "Low-code platform by Siemens", "Low-code apps directly on Teamcenter data; integration blocks are generated", "Mendix platform licence; outside the Microsoft suite", "Alternative build platform"],
  ];
  for (let i = 0; i < comp.length; i++) {
    const [name, ic, catg, what, com, role] = comp[i];
    const x = MX + i * (bw + bg);
    card(s, x, 1.5, bw, 4.95);
    await iconCircle(s, ic, x + 0.25, 1.72, 0.6, C.accent1);
    txt(s, name, { x: x + 1.0, y: 1.72, w: bw - 1.15, h: 0.6, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    txt(s, catg, { x: x + 0.25, y: 2.45, w: bw - 0.5, h: 0.3, fontSize: 11, italic: true, color: C.accent6 });
    txt(s, what, { x: x + 0.25, y: 2.85, w: bw - 0.5, h: 1.2, fontSize: 12 });
    txt(s, "Commercial", { x: x + 0.25, y: 4.1, w: bw - 0.5, h: 0.25, fontSize: 10, bold: true, color: C.accent6 });
    txt(s, com, { x: x + 0.25, y: 4.35, w: bw - 0.5, h: 0.95, fontSize: 12 });
    txt(s, "Role", { x: x + 0.25, y: 5.4, w: bw - 0.5, h: 0.25, fontSize: 10, bold: true, color: C.accent6 });
    txt(s, role, { x: x + 0.25, y: 5.65, w: bw - 0.5, h: 0.65, fontSize: 12, bold: true, color: C.accent1 });
  }
  sourceNote(s, "Sources: S16, S45, S46, S47, S49, S50, S51");
  s.addNotes(D.complementary.map((c) => `${c[0]} (${c[1]}): ${c[3]} Commercial: ${c[4]}. Role: ${c[5]}. Sources: ${c[6]}`).join("\n"));

  // ------------------------------------------------------------- 14 external cost & time
  s = content(S, "No vendor publishes prices, so an RFI is needed");
  const rows14 = [[headCell("Product"), headCell("Public price signal"), headCell("Planning assumption, licence per year"), headCell("Implementation after contract")]];
  const k14 = [["TCPCM", "Teamcenter PCM"], ["APRIORI", "aPriori"], ["FACTON", "FACTON EPC"], ["TSET", "Tset"], ["CLEO", "Cleopatra"]];
  const sig = { TCPCM: "None for cost management. Teamcenter X Essentials reported at USD 150-200 per user and month (not PCM-specific)", APRIORI: "Third party: USD 4,000-17,000 per month to start; 'typically USD 100k+ per year'", FACTON: "None", TSET: "None", CLEO: "None; peer product CostOS listed from USD 2,800 per user" };
  const ass = { TCPCM: "EUR 60k-200k", APRIORI: "EUR 100k-250k", FACTON: "EUR 60k-200k", TSET: "EUR 60k-150k", CLEO: "EUR 40k-100k (placeholder)" };
  const imp = { TCPCM: "4-9 months*", APRIORI: "about 6 months (G2 reviews)", FACTON: "4-9 months*", TSET: "3-6 months*", CLEO: "3-6 months*" };
  k14.forEach(([key, name]) => rows14.push([cell(name, { bold: true, color: C.text2, fontSize: 13 }), cell(sig[key], { fontSize: 12 }), cell(ass[key], { bold: true, fontSize: 12 }), cell(imp[key], { fontSize: 12 })]));
  table(s, rows14, { x: MX, y: 1.5, w: 7.9, colW: [1.5, 3.2, 1.7, 1.5], rowH: [0.6, 1.05, 0.9, 0.75, 0.75, 0.9], fontSize: 12 });
  const cx = 8.8, cw2 = W - MX - cx;
  card(s, cx, 1.5, cw2, 4.95, { fill: H.dk2 });
  txt(s, "Planning case: external PCM suite", { x: cx + 0.25, y: 1.68, w: cw2 - 0.5, h: 0.35, fontSize: 14, bold: true, color: C.accent2 });
  const pc = [["EUR 110k", "licence per year (range 60k-200k)"], ["EUR 150k", "implementation services (range 60k-300k)"], ["6-12 months", "from start of selection to productive use"]];
  pc.forEach((v, i) => {
    const y = 2.2 + i * 1.05;
    txt(s, v[0], { x: cx + 0.25, y, w: cw2 - 0.5, h: 0.5, fontSize: 26, bold: true, color: C.background1, valign: "middle" });
    txt(s, v[1], { x: cx + 0.25, y: y + 0.5, w: cw2 - 0.5, h: 0.4, fontSize: 11, color: C.background2 });
  });
  txt(s, "About 10 editing users plus viewers. Rule of thumb for enterprise software: services cost one to three times the first-year licence.", { x: cx + 0.25, y: 5.4, w: cw2 - 0.5, h: 0.95, fontSize: 11, color: C.background2 });
  sourceNote(s, "Sources: S13, S19, S20, S21, S53, S56   * planning assumption by the author, not a quote");
  s.addNotes("These are the weakest numbers in the material. No product cost management vendor publishes prices; the only numeric signals concern aPriori and come from third-party sites. Selection, negotiation and IT security review are assumed to take two to four months before implementation starts. The RFI questions are in the workbook sheet 'RFI and open questions'.");

  // ------------------------------------------------------------- 15 section in-house
  S = "In-house on the Microsoft suite";
  pres.addSection({ title: S });
  s = pres.addSlide({ masterName: "SECTION_DARK", sectionTitle: S });
  decor(s);
  s.addText("In-house on the Microsoft suite", { placeholder: "title" });
  s.addText("Three options, how the solution works, roadmap, team and risks", { placeholder: "body" });

  // ------------------------------------------------------------- 16 three options
  s = content(S, "Three in-house options that build on each other");
  const opts = [
    { key: "IHA", tk: "IHA", name: "A  Lean", ic: "FaFileExcel", idea: "Structure today's Excel cost data, store it in SharePoint, analyse it in Power BI.", mvp: "6-8 weeks", eff: "60 + 25", use: "Prototype and phase-1 MVP" },
    { key: "IHB", tk: "IHB", name: "B  Power Platform app", ic: "FaLayerGroup", idea: "A dedicated Cost Cockpit app with a relational database on the platform of the LCOH Suite.", mvp: "10-12 weeks", eff: "190 + 60", use: "Recommended target solution" },
    { key: "IHC", tk: "IHC", name: "C  Fabric data platform", ic: "FaServer", idea: "A cost data hub in Microsoft Fabric with a code-based scenario engine and Power BI on top.", mvp: "about 4 months", eff: "320 + 70", use: "Later evolution of B" },
  ];
  const ow = 3.7, og = 0.515;
  for (let i = 0; i < opts.length; i++) {
    const o = opts[i], x = MX + i * (ow + og), rec = o.key === "IHB";
    card(s, x, 1.5, ow, 4.95, rec ? { fill: H.dk2 } : {});
    const tc = rec ? C.background1 : C.text1, hc = rec ? C.background1 : C.text2, mc = rec ? C.background2 : C.accent6;
    await iconCircle(s, o.ic, x + 0.25, 1.72, 0.6, rec ? C.accent2 : C.accent1);
    txt(s, o.name, { x: x + 1.0, y: 1.72, w: ow - 1.2, h: 0.6, fontSize: 17, bold: true, color: hc, valign: "middle" });
    txt(s, o.idea, { x: x + 0.25, y: 2.5, w: ow - 0.5, h: 1.0, fontSize: 13, color: tc });
    const facts = [["Fit", `${fitSum(o.key)} of 39`], ["MVP", o.mvp], ["Build effort (dev + SME)", `${o.eff} days`], ["5-year cost, base", `EUR ${fmtM(tco(o.tk).base.total)}M`]];
    facts.forEach((f, j) => {
      const y = 3.6 + j * 0.47;
      txt(s, f[0], { x: x + 0.25, y, w: 1.85, h: 0.4, fontSize: 11, color: mc, valign: "middle" });
      txt(s, f[1], { x: x + 2.1, y, w: ow - 2.35, h: 0.4, fontSize: 13, bold: true, color: rec ? C.accent2 : C.text2, valign: "middle" });
    });
    txt(s, o.use, { x: x + 0.25, y: 5.7, w: ow - 0.5, h: 0.55, fontSize: 13, bold: true, italic: true, color: rec ? C.accent2 : C.accent1, valign: "middle" });
    if (i < 2) await (async () => { s.addImage({ data: await icon("FaArrowRight", H.accent6), x: x + ow + 0.1, y: 3.8, w: 0.32, h: 0.32, altText: "leads to", objectName: nm("Arrow") }); })();
  }
  sourceNote(s, "Effort and cost are planning assumptions. A can be the MVP of B; C is a possible later evolution when data volume or simulation depth requires it.");
  s.addNotes("Option A needs no premium licences. Option B needs Power Apps Premium (USD 20 per user and month, or pay-as-you-go USD 10 per active user per app and month), Power BI Pro (USD 14) and Power Automate Premium (USD 15) for flow owners. Option C needs a Fabric capacity (F2 about USD 263 per month pay-as-you-go). Sources S62, S64, S65, S66.");

  // ------------------------------------------------------------- 17 option A
  const optionDetail = async (title, key, rowsIdx, stats, note, src) => {
    s = content(S, title);
    const ih = D.inhouse[key];
    const rws = [[headCell("Aspect"), headCell("Design")]];
    rowsIdx.forEach((i) => rws.push([cell(D.inhouse_rows[i], { bold: true, color: C.text2, fontSize: 12, valign: "middle" }), cell(ih[i], { fontSize: 12, valign: "middle" })]));
    table(s, rws, { x: MX, y: 1.5, w: 6.9, colW: [1.75, 5.15], rowH: [0.42].concat(rowsIdx.map(() => 0.64)) });
    const rx = 7.8, rw = W - MX - rx;
    card(s, rx, 1.5, rw, 1.55);
    await iconCircle(s, "FaCheck", rx + 0.2, 1.7, 0.5, C.accent5);
    txt(s, "Strengths", { x: rx + 0.9, y: 1.6, w: rw - 1.1, h: 0.3, fontSize: 11, bold: true, color: C.accent6 });
    txt(s, ih[15], { x: rx + 0.9, y: 1.9, w: rw - 1.1, h: 1.1, fontSize: 12 });
    card(s, rx, 3.2, rw, 1.75);
    await iconCircle(s, "FaTimes", rx + 0.2, 3.4, 0.5, C.accent4);
    txt(s, "Limits", { x: rx + 0.9, y: 3.3, w: rw - 1.1, h: 0.3, fontSize: 11, bold: true, color: C.accent6 });
    txt(s, ih[16], { x: rx + 0.9, y: 3.6, w: rw - 1.1, h: 1.3, fontSize: 12 });
    const sw = rw / 3;
    stats.forEach((v, i) => stat(s, rx + i * sw, 5.2, sw - 0.1, v[0], v[1]));
    sourceNote(s, src);
    s.addNotes(D.inhouse_rows.map((r, i) => `${r}: ${ih[i]}`).join("\n") + (note ? "\n" + note : ""));
  };
  await optionDetail("Option A: lean start with Excel, SharePoint, Power BI", "IHA", [2, 3, 4, 5, 7, 8, 9],
    [["6-8 wks", "to MVP"], ["85", "person-days to build"], [`${fmtM(tco("IHA").base.total)}M`, "EUR over five years"]],
    "SharePoint lists are flat, have a 5,000-item list-view threshold and Power Apps delegation limits (S70). Field audits found errors in 0.38% to 2.5% of spreadsheet cells (S71).",
    "Sources: S65, S70, S71. Effort and cost are planning assumptions.");

  // ------------------------------------------------------------- 18 option B architecture
  s = content(S, "Option B: a Cost Cockpit app next to the LCOH Suite");
  const layers = [
    ["Sources", ["Teamcenter", "Excel cost sheets", "ERP actuals", "Benchmark data"], false],
    ["Integration", ["Power Query dataflows", "Power Automate flows", "Custom connector + gateway"], false],
    ["Data backbone", ["Dataverse, shared with the LCOH Suite: cost structure · cost items · versions · scenarios · targets · measures"], true],
    ["Apps and reports", ["Cost Cockpit app", "Idea box in Teams", "Power BI dashboards", "LCOH Suite (existing)"], false],
    ["Governance", ["Dev / Test / Prod", "Security roles", "Auditing", "Deployment pipelines"], false],
  ];
  const lx = MX, lwid = 8.9, lh = 0.84, lgap = 0.16;
  layers.forEach((l, i) => {
    const y = 1.5 + i * (lh + lgap);
    card(s, lx, y, lwid, lh, l[2] ? { fill: H.dk2 } : {});
    txt(s, l[0], { x: lx + 0.2, y, w: 1.6, h: lh, fontSize: 13, bold: true, color: l[2] ? C.accent2 : C.text2, valign: "middle" });
    const bx0 = lx + 1.9, bwid = lwid - 2.1, n = l[1].length, g = 0.12, w1 = (bwid - (n - 1) * g) / n;
    l[1].forEach((b, j) => {
      const x = bx0 + j * (w1 + g);
      if (!l[2]) card(s, x, y + 0.14, w1, lh - 0.28, { fill: H.lt1, line: LINE });
      txt(s, b, { x: x + 0.08, y: y + 0.14, w: w1 - 0.16, h: lh - 0.28, fontSize: 12, align: "center", valign: "middle", color: l[2] ? C.background1 : C.text1, bold: l[2] });
    });
  });
  const sx = 9.85, sw18 = W - MX - sx;
  stat(s, sx, 1.5, sw18, "37 of 39", "requirement fit of the target design");
  stat(s, sx, 2.75, sw18, "10-12 weeks", "to MVP; full scope in 6-7 months");
  stat(s, sx, 4.0, sw18, "190 + 60", "developer and SME person-days");
  stat(s, sx, 5.25, sw18, "EUR 15k", "licences per year at list price, 40 users");
  sourceNote(s, "Sources: S57, S59, S62, S64, S65, S69. Effort is a planning assumption.");
  s.addNotes(D.inhouse_rows.map((r, i) => `${r}: ${D.inhouse.IHB[i]}`).join("\n") + "\nPlatform facts: Power Apps Premium includes 250 MB Dataverse database and 2 GB file capacity per user (S62). Deployment pipelines require Managed Environments and premium licences (S57). Dataverse auditing works at environment, table and column level (S59).");

  // ------------------------------------------------------------- 19 data model
  s = content(S, "The data model mirrors the requirements");
  const dm = [
    ["Cost breakdown structure", "Hierarchy with scope (NCA / EPC), TIC category and owner", "R1 R2"],
    ["Cost item", "Teamcenter item, supplier, quantity, unit price, cost type, price source and date", "R1 R2 R5"],
    ["Cost version", "Frozen snapshot of all cost values with status and date", "R6"],
    ["Feature and feature link", "Effect of a product feature on cost elements: amount, amount per MW or factor", "R3"],
    ["Scaling rule", "Per element: per module, power law with exponent, or fixed", "R7"],
    ["Region and regional factor", "Factor per region and cost category, with source and date", "R8"],
    ["Scenario and result", "Project size, region, feature set, price year; computed cost per element", "R7 R8"],
    ["Benchmark", "Own product or competitor, source, year, size, cost per element, confidence", "R9"],
    ["Target", "Target value per element and date, with its basis", "R10"],
    ["Idea", "Title, submitter, affected element, estimated saving, status", "R11"],
    ["Measure and tracking", "Owner, saving, probability, degree of implementation, planned vs. realised", "R12"],
  ];
  const rows19 = [[headCell("Table"), headCell("Content"), headCell("Serves")]];
  dm.forEach((r) => rows19.push([cell(r[0], { bold: true, color: C.text2 }), cell(r[1]), cell(r[2], { bold: true, color: C.accent1 })]));
  table(s, rows19, { x: MX, y: 1.5, w: 8.6, colW: [2.4, 5.1, 1.1], rowH: 0.4 });
  const dx = 9.5, dw = W - MX - dx;
  card(s, dx, 1.5, dw, 4.95);
  await iconCircle(s, "FaSitemap", dx + 0.25, 1.72, 0.6, C.accent1);
  txt(s, "How a number is built", { x: dx + 1.0, y: 1.72, w: dw - 1.2, h: 0.6, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
  txt(s, bullets([
    "Leaf cost = quantity × unit price × exchange rate",
    "Each element sums its children",
    "Every value carries cost type, scope and TIC category, so any split is one click",
    "R13: a released scenario is handed to the LCOH Suite as a version-stamped CAPEX dataset",
  ], { space: 9 }), { x: dx + 0.25, y: 2.55, w: dw - 0.5, h: 3.75, fontSize: 12 });
  sourceNote(s, "Design proposal for option B; the same structure applies to option A (lists) and option C (Fabric tables).");
  s.addNotes("The cost breakdown structure is the backbone. It should be agreed with Product gH2 and R&D in phase 0 and aligned with the structure the LCOH Suite uses. Exchange-rate and escalation-index tables complete the model. Dossier chapter 7.2.");

  // ------------------------------------------------------------- 20 option C
  await optionDetail("Option C: Fabric data platform for heavy simulation", "IHC", [2, 3, 4, 5, 6, 8, 9],
    [["16 wks", "to MVP"], ["390", "person-days to build"], [`${fmtM(tco("IHC").base.total)}M`, "EUR over five years"]],
    "Translytical task flows let Power BI report buttons write data back through Fabric user data functions; several sources report general availability since March 2026 (S58, S73). 'Link to Microsoft Fabric' exposes Dataverse tables as shortcuts without copying (S61).",
    "Sources: S58, S61, S65, S66, S73. Effort and cost are planning assumptions.");

  // ------------------------------------------------------------- 21 scenario logic
  s = content(S, "Scenarios: one scaling rule per cost element");
  const rules = [
    ["Per module", "cost = cost per module × number of modules", "Modular product scope"],
    ["Power law", "cost(S) = cost(ref) × (S / S ref)^n", "Shared balance of plant and site scope; calibrate n per element"],
    ["Fixed", "cost independent of size", "One-time engineering"],
  ];
  rules.forEach((r, i) => {
    const y = 1.5 + i * 1.08;
    card(s, MX, y, 5.9, 0.95);
    numCircle(s, i + 1, MX + 0.2, y + 0.26, 0.42);
    txt(s, r[0], { x: MX + 0.8, y: y + 0.08, w: 1.5, h: 0.8, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    txt(s, r[1], { x: MX + 2.3, y: y + 0.08, w: 3.5, h: 0.4, fontSize: 12, bold: true, color: C.accent1, valign: "middle" });
    txt(s, r[2], { x: MX + 2.3, y: y + 0.48, w: 3.5, h: 0.42, fontSize: 11, color: C.accent6 });
  });
  card(s, MX, 4.78, 5.9, 1.72, { fill: H.dk2 });
  await iconCircle(s, "FaGlobeEurope", MX + 0.2, 4.98, 0.5, C.accent2);
  txt(s, "Regional adjustment", { x: MX + 0.9, y: 4.9, w: 4.8, h: 0.32, fontSize: 14, bold: true, color: C.accent2 });
  txt(s, "cost(region) = Σ cost(category) × factor(region, category)", { x: MX + 0.9, y: 5.24, w: 4.85, h: 0.36, fontSize: 12, bold: true, color: C.background1 });
  txt(s, "Separate factors for labour, materials, equipment and indirects, because construction labour varies far more than equipment prices.", { x: MX + 0.9, y: 5.62, w: 4.85, h: 0.8, fontSize: 11, color: C.background2 });
  const sizes = ["10", "20", "50", "100", "200", "500", "1,000"];
  const sv = [10, 20, 50, 100, 200, 500, 1000];
  s.addChart(pres.charts.LINE, [
    { name: "Per module", labels: sizes, values: sv.map(() => 100) },
    { name: "Power law, n = 0.6", labels: sizes, values: sv.map((v) => Math.round(100 * Math.pow(v / 10, -0.4) * 10) / 10) },
    { name: "Fixed", labels: sizes, values: sv.map((v) => Math.round(1000 / v * 10) / 10) },
  ], {
    x: 6.8, y: 1.5, w: W - MX - 6.8, h: 4.95, objectName: nm("Chart"),
    showTitle: true, title: "Cost per kW by project size (index, 10 MW = 100)", titleFontSize: 12, titleFontFace: "+mn-lt", titleColor: H.dk2,
    chartColors: [H.accent1, H.accent2, H.accent4], lineSize: 2.5, lineDataSymbolSize: 6,
    catAxisTitle: "Project size in MW", showCatAxisTitle: true, catAxisTitleFontSize: 10, catAxisTitleFontFace: "+mn-lt", catAxisTitleColor: H.accent6,
    catAxisLabelColor: H.accent6, valAxisLabelColor: H.accent6, catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E3E9E8", size: 0.5 }, catGridLine: { style: "none" }, valAxisMinVal: 0, valAxisMaxVal: 100,
    showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: "+mn-lt", legendColor: H.dk1,
  });
  sourceNote(s, "Illustration of the three rule types, not product data. Public reference: PEM balance-of-plant cost falls from USD 848 to USD 87 per kW between 1 MW and 1 GW (S79).");
  s.addNotes("The six-tenths rule (n about 0.6) is the conventional starting value in process-plant estimating; exponents must be calibrated per element from own projects and quotes. Regional factors can come from own projects, EPC partner feedback, public indices and purchasable data sets such as costdata or Intratec (S51, S81). A feature switches cost effects on or off through the feature link, so any scenario can be calculated with any feature set.");

  // ------------------------------------------------------------- 22 cost-down loop
  s = content(S, "Cost-down loop: from benchmark to tracked measure");
  const flow = [
    ["FaBalanceScale", "Benchmark", "Own products vs. competitors and public studies"],
    ["FaBullseye", "Target", "Value per cost element with its basis"],
    ["FaChartBar", "Gap", "Current cost minus target, per element"],
    ["FaLightbulb", "Idea box", "Any colleague submits in Teams"],
    ["FaTasks", "Measure", "Owner, saving, effort, due date"],
    ["FaCheckCircle", "Effect", "Saving shows in the next released version"],
  ];
  const fw = 1.78, fg = 0.29;
  for (let i = 0; i < flow.length; i++) {
    const x = MX + i * (fw + fg);
    card(s, x, 1.5, fw, 2.3);
    await iconCircle(s, flow[i][0], x + (fw - 0.6) / 2, 1.68, 0.6, i >= 3 ? C.accent2 : C.accent1);
    txt(s, flow[i][1], { x: x + 0.1, y: 2.38, w: fw - 0.2, h: 0.35, fontSize: 14, bold: true, color: C.text2, align: "center" });
    txt(s, flow[i][2], { x: x + 0.12, y: 2.75, w: fw - 0.24, h: 0.95, fontSize: 11, align: "center" });
    if (i < flow.length - 1) s.addImage({ data: await icon("FaChevronRight", H.accent6), x: x + fw + 0.045, y: 2.55, w: 0.2, h: 0.2, altText: "next step", objectName: nm("Arrow") });
  }
  txt(s, "Degree of implementation", { x: MX, y: 4.1, w: 6, h: 0.32, fontSize: 14, bold: true, color: C.text2 });
  const di = ["1  Idea", "2  Evaluated", "3  Decided", "4  Implemented", "5  Effective in cost version"];
  const diw = [1.25, 1.55, 1.45, 1.75, 2.6];
  let dxx = MX;
  di.forEach((d, i) => {
    card(s, dxx, 4.5, diw[i], 0.5, { fill: i === 4 ? H.dk2 : H.lt2 });
    txt(s, d, { x: dxx, y: 4.5, w: diw[i], h: 0.5, fontSize: 12, bold: true, align: "center", valign: "middle", color: i === 4 ? C.background1 : C.text2 });
    dxx += diw[i] + 0.12;
  });
  txt(s, "The dashboard shows how much of each target gap is covered by measures at each level.", { x: MX, y: 5.12, w: 9.0, h: 0.3, fontSize: 12, color: C.accent6 });
  card(s, MX, 5.6, CW, 0.85);
  txt(s, [
    { text: "Prioritisation score  ", options: { bold: true, color: C.text2 } },
    { text: "= saving × probability ÷ (implementation effort + one-off cost)", options: { bold: true, color: C.accent1 } },
    { text: "   shown together with an impact / effort matrix" },
  ], { x: MX + 0.3, y: 5.6, w: CW - 0.6, h: 0.85, fontSize: 14, valign: "middle" });
  s.addNotes("Covers requirements R9 to R12. A five-level degree-of-implementation scale is common in cost-reduction programmes. Competitor data must be collected in every option; no product ships it. Public seed data: see workbook sheet 'H2 cost references' (for example installed cost outside China USD 2,000-2,600 per kW versus USD 600-1,200 in China, as reported for the IEA; ISPT 1 GW studies).");

  // ------------------------------------------------------------- 23 Teamcenter routes
  s = content(S, "Teamcenter interface: start with export, automate later");
  const rows23 = [[headCell("Route"), headCell("How it works"), headCell("Effort"), headCell("Precondition"), headCell("When")]];
  D.tc_routes.forEach((r) => rows23.push([
    cell(`${r[0]}  ${r[1]}`, { bold: true, color: C.text2 }), cell(r[2]), cell(r[3]), cell(r[4]), cell(r[6], { bold: true, color: C.accent1 }),
  ]));
  table(s, rows23, { x: MX, y: 1.5, w: CW, colW: [2.2, 4.63, 1.4, 2.3, 1.6] });
  card(s, MX, 5.55, CW, 0.9, { fill: H.dk2 });
  txt(s, [
    { text: "Clarify first: ", options: { bold: true, color: C.accent2 } },
    { text: "are prices and supplier assignments really maintained in Teamcenter, or does Teamcenter hold the structure while prices sit in the ERP system or in Excel?", options: { color: C.background1 } },
  ], { x: MX + 0.3, y: 5.55, w: CW - 0.6, h: 0.9, fontSize: 14, valign: "middle" });
  sourceNote(s, "Sources: S1, S8, S9, S10, S14, S15, S69. Effort figures are planning assumptions to be validated with PLM IT.");
  s.addNotes(D.tc_routes.map((r) => `${r[0]} ${r[1]}: ${r[2]} Effort: ${r[3]}. Precondition: ${r[4]}. Limit: ${r[5]}. ${r[6]}.`).join("\n") + "\nThere is no single universal REST API for core Teamcenter data; integrations usually use the services layer with JSON (S14, S15). Teamcenter 2606 ships a Power BI integration with templates for BOMs, programme plans, schedules and search results (S8, S9, S10).");

  // ------------------------------------------------------------- 24 LCOH link
  s = content(S, "LCOH Suite link: two apps on one data backbone");
  const by = 1.5, bh = 1.9;
  card(s, MX, by, 3.4, bh);
  await iconCircle(s, "FaCoins", MX + 0.25, by + 0.25, 0.6, C.accent1);
  txt(s, "Cost Cockpit", { x: MX + 1.0, y: by + 0.25, w: 2.3, h: 0.6, fontSize: 16, bold: true, color: C.text2, valign: "middle" });
  txt(s, "Cost structure, scenarios, targets, measures", { x: MX + 0.25, y: by + 1.0, w: 2.9, h: 0.65, fontSize: 12 });
  card(s, 4.65, by, 4.03, bh, { fill: H.dk2 });
  txt(s, "Released CAPEX dataset", { x: 4.85, y: by + 0.2, w: 3.63, h: 0.4, fontSize: 16, bold: true, color: C.accent2, align: "center" });
  txt(s, "TIC in EUR per kW by scope, project size and region, stamped with the cost version", { x: 4.85, y: by + 0.68, w: 3.63, h: 0.9, fontSize: 12, color: C.background1, align: "center" });
  card(s, 9.33, by, 3.4, bh);
  await iconCircle(s, "FaBolt", 9.58, by + 0.25, 0.6, C.accent2);
  txt(s, "LCOH Suite", { x: 10.33, y: by + 0.25, w: 2.3, h: 0.6, fontSize: 16, bold: true, color: C.text2, valign: "middle" });
  txt(s, "Existing Power App; reads CAPEX as an input", { x: 9.58, y: by + 1.0, w: 2.9, h: 0.65, fontSize: 12 });
  s.addImage({ data: await icon("FaArrowRight", H.accent1), x: 4.15, y: by + 0.7, w: 0.35, h: 0.35, altText: "writes", objectName: nm("Arrow") });
  s.addImage({ data: await icon("FaArrowRight", H.accent1), x: 8.83, y: by + 0.7, w: 0.35, h: 0.35, altText: "is read by", objectName: nm("Arrow") });
  txt(s, "How the link is built depends on where the LCOH Suite stores its data", { x: MX, y: 3.72, w: CW, h: 0.35, fontSize: 14, bold: true, color: C.text2 });
  const lk = [
    ["Dataverse", "Both apps use the same tables in one environment. No interface to build."],
    ["SharePoint or SQL", "A Power Automate flow writes each released dataset to the LCOH data store."],
    ["Unknown or locked", "Versioned export file as a first step; automate once the store is clear."],
  ];
  lk.forEach((v, i) => {
    const x = MX + i * (3.85 + 0.29);
    card(s, x, 4.2, 3.85, 1.3);
    txt(s, v[0], { x: x + 0.2, y: 4.3, w: 3.45, h: 0.32, fontSize: 14, bold: true, color: C.accent1 });
    txt(s, v[1], { x: x + 0.2, y: 4.66, w: 3.45, h: 0.78, fontSize: 12 });
  });
  card(s, MX, 5.7, CW, 0.8);
  txt(s, [
    { text: "Why a separate app: ", options: { bold: true, color: C.text2 } },
    { text: "each app stays small, has its own release rhythm and its own owner, while master data such as the cost structure exists only once." },
  ], { x: MX + 0.3, y: 5.7, w: CW - 0.6, h: 0.8, fontSize: 13, valign: "middle" });
  s.addNotes("Answers requirement R13 and the concern in the task description that building everything into the LCOH Suite would make it too extensive. The storage of the LCOH Suite is an open question for its owner. With Fabric, 'Link to Microsoft Fabric' can also expose Dataverse tables for reporting without copying (S61).");

  // ------------------------------------------------------------- 25 roadmap gantt
  s = content(S, "Roadmap: full scope about 30 weeks after the go");
  const gx = 3.2, gw = W - MX - gx - 0.45, wk = gw / 30;
  txt(s, "Week", { x: MX, y: 1.5, w: 2.5, h: 0.3, fontSize: 11, bold: true, color: C.accent6 });
  [1, 5, 10, 15, 20, 25, 30].forEach((n) => txt(s, String(n), { x: gx + (n - 1) * wk - 0.1, y: 1.5, w: wk + 0.2, h: 0.3, fontSize: 11, color: C.accent6, align: "center" }));
  s.addShape(pres.shapes.LINE, { x: gx, y: 1.85, w: gw, h: 0, line: { color: LINE, width: 1 }, objectName: nm("Axis") });
  const gates = { 0: "G0", 1: "G1", 2: "R2", 3: "R3", 4: "R4" };
  D.roadmap.forEach((p, i) => {
    const y = 2.0 + i * 0.86;
    txt(s, `${p[0]}  ${p[1]}`, { x: MX, y, w: gx - MX - 0.15, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
    txt(s, p[6], { x: MX, y: y + 0.3, w: gx - MX - 0.15, h: 0.45, fontSize: 10, color: C.accent6 });
    const bx = gx + (p[2] - 1) * wk, bwd = (p[3] - p[2] + 1) * wk;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx, y: y + 0.08, w: bwd, h: 0.5, rectRadius: 0.06, fill: { color: i === 0 ? C.accent6 : C.accent1 }, line: { color: i === 0 ? C.accent6 : C.accent1, width: 0 }, objectName: nm("Phase bar") });
    txt(s, `Weeks ${p[2]}-${p[3]}`, { x: bx, y: y + 0.08, w: bwd, h: 0.5, fontSize: 11, bold: true, color: C.background1, align: "center", valign: "middle" });
    s.addShape(pres.shapes.DIAMOND, { x: bx + bwd - 0.02, y: y + 0.13, w: 0.4, h: 0.4, fill: { color: C.accent2 }, line: { color: C.background1, width: 1 }, objectName: nm("Gate") });
    if (i < 4) txt(s, gates[i], { x: bx + bwd + 0.42, y: y + 0.13, w: 0.5, h: 0.4, fontSize: 11, bold: true, color: C.text2, valign: "middle" });
    else txt(s, gates[i], { x: bx + bwd - 0.55, y: y + 0.6, w: 0.9, h: 0.25, fontSize: 11, bold: true, color: C.text2, align: "right" });
  });
  const ly = 6.33;
  s.addShape(pres.shapes.DIAMOND, { x: MX, y: ly + 0.02, w: 0.24, h: 0.24, fill: { color: C.accent2 }, line: { color: C.accent2, width: 0 }, objectName: nm("Legend") });
  txt(s, "G0 make-or-buy confirmed with RFI answers · G1 MVP in use: continue, adjust or fall back to external · R2-R4 releases", { x: MX + 0.35, y: ly, w: CW - 0.35, h: 0.3, fontSize: 11, color: C.text1, valign: "middle" });
  sourceNote(s, "Planning assumption for option B with a lean start: one developer, a part-time product owner and SME input.");
  s.addNotes(D.roadmap.map((p) => `Phase ${p[0]} ${p[1]} (weeks ${p[2]}-${p[3]}; ${p[4]} developer and ${p[5]} SME person-days): ${p[6]}. Work packages: ${p[7].join("; ")}. ${p[8]}`).join("\n"));

  // ------------------------------------------------------------- 26 phase details
  s = content(S, "Each phase ends with a usable result");
  const short = [
    "Requirements catalogue, data inventory, cost structure, licence check, vendor RFI",
    "Data model and app, baseline import from Excel and Teamcenter export, first version freeze, cost-driver dashboards",
    "Scaling rules, regional factor tables, scenario builder, calibration against known projects",
    "Benchmark table, targets and gap view, idea box, measure list with prioritisation, tracking dashboard",
    "Automated Teamcenter interface, LCOH Suite link, security roles, pipelines, tests, training",
  ];
  const rows26 = [[headCell("Phase"), headCell("Weeks", { align: "center" }), headCell("Main work packages"), headCell("Result / gate"), headCell("Person-days dev + SME", { align: "center" })]];
  D.roadmap.forEach((p, i) => rows26.push([
    cell(`${p[0]}  ${p[1]}`, { bold: true, color: C.text2, fontSize: 13 }), cell(`${p[2]}-${p[3]}`, { align: "center", fontSize: 12 }), cell(short[i], { fontSize: 12 }),
    cell(cap(p[8].replace(/^Gate /, "").replace(/^Release \d: /, "")), { fontSize: 12 }), cell(`${p[4]} + ${p[5]}`, { align: "center", bold: true, fontSize: 12 }),
  ]));
  rows26.push([cell("Across phases", { bold: true, color: C.text2, fontSize: 12 }), cell(""), cell("Project management, testing, training, documentation"), cell(""), cell(`${D.roadmap_overhead[1]} + 0`, { align: "center", bold: true })]);
  rows26.push([cell("Total", { bold: true, color: C.background1, fill: { color: H.dk2 }, fontSize: 12 }), cell("30", { align: "center", bold: true, color: C.background1, fill: { color: H.dk2 } }),
    cell("", { fill: { color: H.dk2 } }), cell("", { fill: { color: H.dk2 } }), cell("190 + 60", { align: "center", bold: true, color: C.accent2, fill: { color: H.dk2 } })]);
  table(s, rows26, { x: MX, y: 1.5, w: CW, colW: [2.5, 0.9, 4.6, 2.83, 1.3], rowH: [0.5, 0.7, 0.7, 0.7, 0.7, 0.7, 0.45, 0.45] });
  sourceNote(s, "Effort figures are planning assumptions. Detailed work packages and an editable week plan: workbook sheet 'Roadmap'.");
  s.addNotes("Until gate G1 about 60 developer person-days are spent. The cost breakdown structure, the cleaned baseline and the requirements catalogue produced by then are needed for an external tool as well, so the early work is not lost if the decision is reversed.");

  // ------------------------------------------------------------- 27 team & effort
  s = content(S, "A small team can deliver it");
  const rows27 = [[headCell("Role"), headCell("Who"), headCell("Responsibility"), headCell("Load")]];
  D.roles.forEach((r) => rows27.push([cell(r[0], { bold: true, color: C.text2, fontSize: 12 }), cell(r[1], { fontSize: 12 }), cell(r[2], { fontSize: 12 }), cell(r[3], { fontSize: 12 })]));
  table(s, rows27, { x: MX, y: 1.5, w: 8.5, colW: [2.2, 1.8, 2.8, 1.7], rowH: [0.45].concat(D.roles.map(() => 0.64)) });
  const tx = 9.5, tw27 = W - MX - tx;
  card(s, tx, 1.5, tw27, 4.95, { fill: H.dk2 });
  const st27 = [["190", "developer person-days to full scope"], ["60", "SME person-days"], ["about 50", "person-days per year to run and improve"], ["EUR 15k", "licences per year at list price"]];
  st27.forEach((v, i) => {
    const y = 1.7 + i * 1.17;
    txt(s, v[0], { x: tx + 0.25, y, w: tw27 - 0.5, h: 0.55, fontSize: 28, bold: true, color: C.accent2, valign: "middle" });
    txt(s, v[1], { x: tx + 0.25, y: y + 0.55, w: tw27 - 0.5, h: 0.45, fontSize: 11, color: C.background2 });
  });
  sourceNote(s, "Planning assumptions; licences for 40 users: Power Apps Premium USD 20, Power BI Pro USD 14 per user and month (S62, S65).");
  s.addNotes("Key-person risk is the main organisational risk: plan a trained deputy for the developer and involve the IT Power Platform centre of excellence from phase 0. A Forrester study commissioned by Microsoft reports a 50% reduction in app development time for professional developers using Power Apps (S67).");

  // ------------------------------------------------------------- 28 risks
  s = content(S, "In-house risks are known and can be managed");
  const lvl = (v) => ({ High: HEAT[0], Medium: HEAT[1], Low: HEAT[2] }[v]);
  const rows28 = [[headCell("Risk"), headCell("Impact", { align: "center" }), headCell("Likelihood", { align: "center" }), headCell("Mitigation")]];
  D.risks.filter((r) => r[0] === "In-house").forEach((r) => rows28.push([
    cell(r[1], { bold: true, color: C.text2 }), cell(r[2], { align: "center", fill: { color: lvl(r[2]) } }), cell(r[3], { align: "center", fill: { color: lvl(r[3]) } }), cell(r[4]),
  ]));
  table(s, rows28, { x: MX, y: 1.5, w: CW, colW: [4.0, 1.0, 1.1, 6.03], rowH: 0.52 });
  sourceNote(s, "Risks of the external route (functional mismatch, second tool, cash-out, lock-in, lead time) are listed in the workbook sheet 'Risks'.");
  s.addNotes(D.risks.map((r) => `${r[0]}: ${r[1]} (impact ${r[2]}, likelihood ${r[3]}). Mitigation: ${r[4]}`).join("\n"));

  // ------------------------------------------------------------- 29 section comparison
  S = "Comparison and decision";
  pres.addSection({ title: S });
  s = pres.addSlide({ masterName: "SECTION_DARK", sectionTitle: S });
  decor(s);
  s.addText("Comparison and decision", { placeholder: "title" });
  s.addText("Requirement fit, five-year cost, weighted scoring, recommendation and next steps", { placeholder: "body" });

  // ------------------------------------------------------------- 30 fit heat map
  s = content(S, "Requirement fit: in-house B covers 37 of 39 points");
  const keys = D.solutions.map((x) => x[0]);
  const rows30 = [[headCell("Requirement")].concat(D.solutions.map((x) => headCell(x[1], { align: "center", fill: { color: x[3] === "In-house" ? H.accent1 : H.dk2 } })))];
  D.requirements.forEach((r, i) => rows30.push([cell(`${r[0]}  ${r[2]}`, { bold: true, color: C.text2, valign: "middle" })].concat(
    keys.map((kk) => cell(String(D.fit[kk][i]), { align: "center", valign: "middle", fill: { color: HEAT[D.fit[kk][i]] } })))));
  rows30.push([cell("Sum (of 39)", { bold: true, color: C.background1, fill: { color: H.dk2 }, valign: "middle" })].concat(
    keys.map((kk) => cell(String(fitSum(kk)), { bold: true, align: "center", valign: "middle", color: C.background1, fill: { color: H.dk2 }, fontSize: 12 }))));
  table(s, rows30, { x: MX, y: 1.4, w: CW, colW: [3.17].concat(keys.map(() => 1.12)), rowH: 0.325, margin: [0.02, 0.08, 0.02, 0.08] });
  const lgx = MX;
  ["0  not covered", "1  workaround", "2  configuration", "3  native / designed in"].forEach((t, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: lgx + i * 2.2, y: 6.47, w: 0.22, h: 0.18, fill: { color: HEAT[i] }, line: { color: HEAT[i], width: 0 }, objectName: nm("Legend") });
    txt(s, t, { x: lgx + i * 2.2 + 0.3, y: 6.42, w: 1.85, h: 0.28, fontSize: 10, color: C.accent6, valign: "middle" });
  });
  sourceNote(s, "Desk assessment. In-house scores describe the target design; nothing exists today. External scores need confirmation in demos.");
  s.addNotes(keys.map((kk) => `${sol(kk)[2]}: ${fitSum(kk)} of 39. ${D.fit_rationale[kk]}`).join("\n"));

  // ------------------------------------------------------------- 31 TCO
  s = content(S, "Five-year cost: in-house needs far less cash");
  const tl = ["In-house A", "In-house B", "In-house C", "External suite", "External + add-ons"];
  const tk = ["IHA", "IHB", "IHC", "EXT", "EXTC"];
  const ser = [["Internal effort, one-off", "oneoff_internal"], ["External services, one-off", "oneoff_external"], ["Licences, 5 years", "licences_5y"], ["Internal run effort, 5 years", "run_5y"]];
  s.addChart(pres.charts.BAR, ser.map(([name, f]) => ({ name, labels: tl, values: tk.map((kk) => k(tco(kk).base[f])) })), {
    x: MX, y: 1.45, w: 7.4, h: 5.1, objectName: nm("Chart"), barDir: "col", barGrouping: "stacked", barGapWidthPct: 55,
    chartColors: [H.accent3, "C4701F", H.accent4, H.accent6],
    showTitle: true, title: "Base case, EUR thousand", titleFontSize: 12, titleFontFace: "+mn-lt", titleColor: H.dk2,
    catAxisLabelColor: H.accent6, valAxisLabelColor: H.accent6, catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E3E9E8", size: 0.5 }, catGridLine: { style: "none" }, valAxisNumFmt: "#,##0",
    showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: "+mn-lt", legendColor: H.dk1,
    showValue: true, dataLabelPosition: "ctr", dataLabelFontSize: 9, dataLabelColor: "FFFFFF", dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "#,##0;;",
  });
  const rows31 = [[headCell("EUR thousand"), headCell("Total", { align: "right" }), headCell("Range", { align: "right" }), headCell("Cash-out", { align: "right" })]];
  tk.forEach((kk, i) => {
    const t = tco(kk);
    rows31.push([cell(tl[i], { bold: true, color: C.text2 }), cell(k(t.base.total).toLocaleString("en-US"), { align: "right", bold: true }),
      cell(`${k(t.low.total).toLocaleString("en-US")}-${k(t.high.total).toLocaleString("en-US")}`, { align: "right" }), cell(k(t.base.cash_out).toLocaleString("en-US"), { align: "right", bold: true, color: C.accent4 })]);
  });
  table(s, rows31, { x: 8.3, y: 1.5, w: W - MX - 8.3, colW: [1.63, 0.8, 1.2, 0.8], rowH: 0.42 });
  txt(s, bullets([
    "In-house cost is mostly internal effort; cash-out of option B is about a quarter of an external suite",
    "External ranges are wide because prices are unknown; at its low end a suite costs about as much as option B",
    "A suite still needs a measure tool and an LCOH link (last bar)",
  ], { space: 6 }), { x: 8.3, y: 4.2, w: W - MX - 8.3, h: 2.35, fontSize: 12 });
  sourceNote(s, "Planning assumptions: 10 editors + 30 contributors, EUR 800 internal and EUR 1,100 external day rate, USD list prices at 0.90. Editable in the workbook, sheet 'TCO model'.");
  s.addNotes(D.tco.map((t) => `${t.label}: base EUR ${t.cases.base.total.toLocaleString("en-US")} (low ${t.cases.low.total.toLocaleString("en-US")}, high ${t.cases.high.total.toLocaleString("en-US")}); cash-out base ${t.cases.base.cash_out.toLocaleString("en-US")}; licences per year base ${t.cases.base.licence_per_year.toLocaleString("en-US")}.`).join("\n") + "\nData stewardship is needed in every option and is not included. External + add-ons = PCM suite plus a measure-tracking tool (third-party price information for Falcon, S49) plus a custom link to the LCOH Suite.");

  // ------------------------------------------------------------- 32 scoring
  s = content(S, "Weighted scoring ranks in-house B first");
  const order = keys.map((kk) => ({ kk, v: D.weighted[kk][1] })).sort((a, b) => b.v - a.v);
  s.addChart(pres.charts.BAR, [{ name: "Weighted total", labels: order.map((o) => sol(o.kk)[1]), values: order.map((o) => o.v) }], {
    x: MX, y: 1.45, w: 6.6, h: 5.1, objectName: nm("Chart"), barDir: "bar", barGapWidthPct: 45,
    chartColors: order.map((o) => (sol(o.kk)[3] === "In-house" ? H.accent2 : H.accent1)),
    showTitle: true, title: "Weighted total (1-5); amber = in-house, teal = external", titleFontSize: 12, titleFontFace: "+mn-lt", titleColor: H.dk2,
    catAxisLabelColor: H.dk1, valAxisLabelColor: H.accent6, catAxisLabelFontSize: 11, valAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E3E9E8", size: 0.5 }, catGridLine: { style: "none" }, valAxisMinVal: 0, valAxisMaxVal: 5, valAxisMajorUnit: 1, catAxisOrientation: "maxMin",
    showLegend: false, showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: H.dk1, dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "0.00",
  });
  const rows32 = [[headCell("Criterion"), headCell("Weight", { align: "center" }), headCell("Best", { align: "center" })]];
  const best = { C1: "In-house B", C2: "Teamcenter PCM", C3: "In-house B", C4: "In-house A", C5: "In-house A", C6: "In-house B / C", C7: "TC PCM, aPriori", C8: "Teamcenter PCM" };
  D.criteria.forEach((cr) => rows32.push([cell(cr[1], { bold: true, color: C.text2 }), cell(`${Math.round(cr[2] * 100)}%`, { align: "center" }), cell(best[cr[0]], { align: "center" })]));
  table(s, rows32, { x: 7.6, y: 1.5, w: W - MX - 7.6, colW: [2.83, 0.7, 1.6], rowH: 0.4 });
  txt(s, "In-house B leads on fit, LCOH integration and flexibility at once, so it stays first under any plausible weighting. The order among external products is sensitive to the weights.", { x: 7.6, y: 5.3, w: W - MX - 7.6, h: 1.2, fontSize: 12 });
  sourceNote(s, "Scores 1-5 per criterion are a desk assessment. Weights and scores are editable in the workbook, sheet 'Scoring'.");
  s.addNotes(keys.map((kk, i) => `${sol(kk)[1]}: total ${D.weighted[kk][1]} (fit ${D.weighted[kk][0]}; ` + D.criteria.slice(1).map((cr) => `${cr[0]} ${D.scores[cr[0]][i]}`).join(", ") + ")").join("\n") + "\nWith more weight on reference data and vendor stability, Teamcenter PCM extends its lead among external products; with more weight on TIC scenarios, Cleopatra overtakes it.");

  // ------------------------------------------------------------- 33 build vs buy
  s = content(S, "When to build and when to buy");
  const half = (CW - 0.4) / 2;
  card(s, MX, 1.5, half, 3.75, { fill: H.dk2 });
  await iconCircle(s, "FaTools", MX + 0.25, 1.72, 0.6, C.accent2);
  txt(s, "Build in-house when", { x: MX + 1.0, y: 1.72, w: half - 1.2, h: 0.6, fontSize: 18, bold: true, color: C.background1, valign: "middle" });
  txt(s, bullets([
    "Transparency and tracking at product and TIC level are the main goal",
    "The link to the LCOH Suite matters",
    "Cost structure and logic will keep changing",
    "Developer capacity can be secured, internally or through a partner",
    "Cash budget is limited",
  ], { space: 10 }), { x: MX + 0.3, y: 2.5, w: half - 0.6, h: 2.65, fontSize: 14, color: C.background1 });
  const x2 = MX + half + 0.4;
  card(s, x2, 1.5, half, 3.75);
  await iconCircle(s, "FaShoppingCart", x2 + 0.25, 1.72, 0.6, C.accent1);
  txt(s, "Buy external when", { x: x2 + 1.0, y: 1.72, w: half - 1.2, h: 0.6, fontSize: 18, bold: true, color: C.text2, valign: "middle" });
  txt(s, bullets([
    "Supplier should-cost negotiation on manufactured parts is the main value",
    "No developer capacity can be secured",
    "Licences or frame agreements already exist in the group",
    "IT rules out Dataverse for cost data",
    "An audited standard costing method is required",
  ], { space: 10 }), { x: x2 + 0.3, y: 2.5, w: half - 0.6, h: 2.65, fontSize: 14 });
  card(s, MX, 5.45, CW, 1.0);
  txt(s, [
    { text: "Two hybrids keep options open: ", options: { bold: true, color: C.text2 } },
    { text: "buy reference data and build the tool; or add Teamcenter PCM later for should-costing and feed its results into the Cost Cockpit." },
  ], { x: MX + 0.3, y: 5.45, w: CW - 0.6, h: 1.0, fontSize: 14, valign: "middle" });
  s.addNotes("The evidence in this research points to the left column for the requirement list as given. The right column lists the conditions under which the recommendation should be reversed. The costdata data package (S51) and the Teamcenter PCM REST interface (S1, S14) make both hybrids technically feasible.");

  // ------------------------------------------------------------- 34 recommendation & next steps
  s = content(S, "Recommendation and next steps");
  const rec = [
    ["Decide for in-house option B", "with a lean start"],
    ["Keep two exit gates", "G0 with RFI answers, G1 with the MVP"],
    ["Send an RFI to three vendors", "Teamcenter PCM, FACTON or Tset, Cleopatra"],
    ["Treat reference data separately", "buying data is compatible with building"],
  ];
  rec.forEach((r, i) => {
    const y = 1.5 + i * 1.22;
    card(s, MX, y, 4.6, 1.05);
    numCircle(s, i + 1, MX + 0.2, y + 0.31, 0.42, C.accent2);
    txt(s, r[0], { x: MX + 0.8, y: y + 0.12, w: 3.65, h: 0.4, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    txt(s, r[1], { x: MX + 0.8, y: y + 0.54, w: 3.65, h: 0.4, fontSize: 12, color: C.accent6 });
  });
  const ns = [
    ["1.1", "External best practice incl. cost and time", "Send RFI, book two scripted demos", "Quoted prices and durations"],
    ["1.2", "Internal development possibility", "Clarify open questions; design workshop with IT and the LCOH Suite owner", "Confirmed architecture and licences"],
    ["1.3", "Alignment and decision", "Decision meeting with this material and the RFI answers", "Gate G0 decision"],
    ["2", "Requirements catalogue", "Review the 13 requirements, confirm priorities, map today's tools", "Catalogue v1"],
    ["3", "Implementation", "Start phase 1", "MVP after 10-12 weeks"],
  ];
  const rows34 = [[headCell("Step"), headCell("In the task description"), headCell("Action"), headCell("Output")]];
  ns.forEach((r) => rows34.push([cell(r[0], { bold: true, color: C.accent1, align: "center" }), cell(r[1], { bold: true, color: C.text2 }), cell(r[2]), cell(r[3])]));
  table(s, rows34, { x: 5.6, y: 1.5, w: W - MX - 5.6, colW: [0.6, 2.2, 2.73, 1.6], rowH: [0.42, 0.85, 0.95, 0.85, 0.85, 0.75] });
  s.addNotes("Reverse the recommendation if: the main expected value shifts to supplier should-cost negotiation on manufactured parts; no developer capacity can be secured; the RFI shows that Teamcenter PCM licences already exist in the group or can be had at the low end of the range; or IT security rules out Dataverse for cost data.");

  // ------------------------------------------------------------- 35 open questions
  s = content(S, "Nine internal questions decide the details");
  const oq = D.open_questions.filter((q) => q[0] === "Internal");
  const qw = (CW - 0.3) / 3, qh = 1.5;
  oq.forEach((q, i) => {
    const x = MX + (i % 3) * (qw + 0.15), y = 1.5 + Math.floor(i / 3) * (qh + 0.17);
    card(s, x, y, qw, qh);
    numCircle(s, i + 1, x + 0.18, y + 0.18, 0.4);
    txt(s, q[1], { x: x + 0.72, y: y + 0.12, w: qw - 0.87, h: 0.98, fontSize: 12 });
    txt(s, q[2], { x: x + 0.72, y: y + 1.12, w: qw - 0.87, h: 0.28, fontSize: 10, bold: true, color: C.accent1 });
  });
  sourceNote(s, "The vendor questions for the RFI are in the workbook, sheet 'RFI and open questions', with space for answers.");
  s.addNotes(D.open_questions.map((q) => `${q[0]}: ${q[1]} (${q[2]})`).join("\n"));

  // ------------------------------------------------------------- 36 method & sources
  s = content(S, "Method, limits and sources");
  card(s, MX, 1.5, 5.6, 4.95);
  await iconCircle(s, "FaSearch", MX + 0.25, 1.72, 0.6, C.accent1);
  txt(s, "Method and limits", { x: MX + 1.0, y: 1.72, w: 4.3, h: 0.6, fontSize: 16, bold: true, color: C.text2, valign: "middle" });
  txt(s, bullets([
    "Desk research on 13 November 2026 in English and German; 82 sources",
    "Vendor pages could not be opened directly; facts come from search extracts and should be confirmed with the vendors",
    "No vendor publishes prices: external cost figures are planning assumptions",
    "Microsoft list prices come from third-party licensing guides",
    "Fit and scoring are a first assessment by one person",
    "Not covered: product tests, reference calls, legal and data-protection review",
  ], { space: 11 }), { x: MX + 0.3, y: 2.5, w: 5.0, h: 3.85, fontSize: 13 });
  const rows36 = [[headCell("Topic"), headCell("Source IDs"), headCell("Main origin")]];
  [["Teamcenter PCM and Teamcenter", "S1-S16", "Siemens blogs and fact sheets, partners"],
    ["aPriori", "S17-S23", "Vendor, G2, Software Finder, Forrester"],
    ["FACTON EPC", "S24-S30", "Vendor, FitGap, SoftGuide, Capterra"],
    ["Tset", "S31-S38", "Vendor, press"],
    ["Cleopatra and TIC tools", "S39-S44, S52, S53", "Vendor, SaaSrat, Capterra"],
    ["Measure tools and data", "S45-S51", "Vendors, trusted.de, press"],
    ["Microsoft platform", "S57-S73", "Microsoft Learn, licensing guides"],
    ["Hydrogen cost references", "S74-S82", "World Bank, ISPT, CRU, OSTI"],
  ].forEach((r) => rows36.push([cell(r[0], { bold: true, color: C.text2 }), cell(r[1], { color: C.accent1, bold: true }), cell(r[2])]));
  table(s, rows36, { x: 6.5, y: 1.5, w: W - MX - 6.5, colW: [2.3, 1.45, 2.48], rowH: 0.46 });
  txt(s, "Full list with links: dossier chapter 15 and workbook sheet 'Sources'.", { x: 6.5, y: 5.85, w: W - MX - 6.5, h: 0.5, fontSize: 12, italic: true, color: C.accent6 });
  s.addNotes(D.sources.map((x) => `${x[0]} ${x[1]} - ${x[2]}`).join("\n"));

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("saved", OUT);
})().catch((e) => { console.error(e); process.exit(1); });
