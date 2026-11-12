// Layout helpers for the guide (docx-js 9.x). One consistent style everywhere.
const fs = require("fs");
const path = require("path");
const d = require("docx");
const {
  Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, HeadingLevel, ImageRun, PageBreak, TableLayoutType, VerticalAlign,
} = d;

const W = 9360; // content width in DXA (US Letter, 1" margins)
const FONT = "Calibri";
const MONO = "Consolas";
const C = {
  ink: "1A1A1A", ink2: "52514E", head: "1F3864", band: "1F3864", grid: "BFBFBF",
  code: "F3F2EF", codeBorder: "D0CFCA",
  tip: ["1BAF7A", "E8F7F1"], warn: ["EB6834", "FDEEE7"], check: ["2A78D6", "EAF2FC"],
  why: ["6B5CA5", "F0EEF8"], tested: "137A55", user: "1F5FAD", notwin: "B4501F", verify: "C00000",
};
const MAX_CODE = 88;
const warnings = [];
let listInstance = 0;

// ---- inline markup: **bold**, `code`, {T} tested tag, {W} not-tested tag, {V} TO-VERIFY
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`|\{T\}|\{W\}|\{V\}|\{U\})/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else if (t.startsWith("`")) out.push(new TextRun({ text: t.slice(1, -1), font: MONO, size: 19, ...base, color: "7A2E0E" }));
    else if (t === "{T}") out.push(new TextRun({ text: "[Tested by Claude on Linux]", bold: true, color: C.tested, size: 18 }));
    else if (t === "{W}") out.push(new TextRun({ text: "[Not tested on Windows]", bold: true, color: C.notwin, size: 18 }));
    else if (t === "{U}") out.push(new TextRun({ text: "[Verified by the user on Windows 10 Pro (build 19045) with WSL2]", bold: true, color: C.user, size: 18 }));
    else if (t === "{V}") out.push(new TextRun({ text: "TO-VERIFY", bold: true, color: C.verify, size: 18 }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

const P = (text, opt = {}) => new Paragraph({ children: runs(text, opt.run || {}), spacing: { after: 100, ...(opt.spacing || {}) }, alignment: opt.align, keepNext: opt.keepNext, indent: opt.indent });
const H1 = (t, pageBreak = true) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)], pageBreakBefore: pageBreak });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

function bullets(items, level = 0) {
  return items.map((t) => new Paragraph({ children: runs(t), numbering: { reference: "bullets", level }, spacing: { after: 60 } }));
}
function numbered(items) {
  listInstance += 1;
  const inst = listInstance;
  const out = [];
  items.forEach((it, k) => {
    const nextIsCode = k + 1 < items.length && typeof items[k + 1] === "object" && items[k + 1].code;
    if (typeof it === "string") {
      out.push(new Paragraph({ children: runs(it), keepNext: nextIsCode, keepLines: true, numbering: { reference: "steps", level: 0, instance: inst }, spacing: { after: 60 } }));
    } else if (it.code) {
      out.push(...code(it.code, { indent: 360 }));
    } else if (it.note) {
      out.push(P(it.note, { indent: { left: 360 } }));
    }
  });
  return out;
}
function checklist(items) {
  return items.map((t) => new Paragraph({ children: [new TextRun({ text: "☐  ", size: 22 }), ...runs(t)], indent: { left: 360, hanging: 300 }, spacing: { after: 50 } }));
}

const noBorders = { top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }, bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }, left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }, right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" } };

function code(text, opt = {}) {
  const lines = text.replace(/\s+$/, "").split("\n");
  const lim = MAX_CODE - Math.round((opt.indent || 0) / 70);
  lines.forEach((l) => { if (l.length > lim) warnings.push(`code line > ${lim} chars: ${l}`); });
  const width = W - (opt.indent || 0);
  const paras = lines.map((l) => new Paragraph({ children: [new TextRun({ text: l.length ? l : " ", font: MONO, size: 17, color: C.ink })], spacing: { after: 0, line: 240 } }));
  const b = { style: BorderStyle.SINGLE, size: 4, color: C.codeBorder };
  return [new Table({
    width: { size: width, type: WidthType.DXA }, columnWidths: [width], indent: { size: opt.indent || 0, type: WidthType.DXA },
    rows: [new TableRow({ cantSplit: lines.length < 25, children: [new TableCell({ width: { size: width, type: WidthType.DXA }, shading: { fill: C.code, type: ShadingType.CLEAR, color: "auto" }, borders: { top: b, bottom: b, left: b, right: b }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: paras })] })],
  }), new Paragraph({ children: [], spacing: { after: 80 } })];
}

function callout(kind, text) {
  const map = { Tip: C.tip, Warning: C.warn, Check: C.check, "Why this matters": C.why };
  const [edge, fill] = map[kind];
  const items = Array.isArray(text) ? text : [text];
  const children = [new Paragraph({ children: [new TextRun({ text: kind.toUpperCase(), bold: true, color: edge, size: 18 })], spacing: { after: 40 } }),
    ...items.map((t) => new Paragraph({ children: runs(t), spacing: { after: 40 } }))];
  return [new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: [W],
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({ width: { size: W, type: WidthType.DXA }, shading: { fill, type: ShadingType.CLEAR, color: "auto" }, margins: { top: 80, bottom: 80, left: 160, right: 120 }, borders: { ...noBorders, left: { style: BorderStyle.SINGLE, size: 24, color: edge } }, children })] })],
  }), new Paragraph({ children: [], spacing: { after: 80 } })];
}

// generic table: header row + body rows; widths as fractions or DXA
function table(header, rows, widths, opt = {}) {
  const sum = widths.reduce((a, b) => a + b, 0);
  const cw = widths.map((w) => Math.round((w / sum) * W));
  cw[cw.length - 1] += W - cw.reduce((a, b) => a + b, 0);
  const b = { style: BorderStyle.SINGLE, size: 4, color: C.grid };
  const borders = { top: b, bottom: b, left: b, right: b };
  const fs = opt.size || 19;
  const keepAll = opt.keep !== undefined ? opt.keep : rows.length <= 10;   // small tables never split
  const cell = (t, i, hdr, shade, last) => new TableCell({
    width: { size: cw[i], type: WidthType.DXA }, borders, margins: { top: 50, bottom: 50, left: 90, right: 90 },
    shading: hdr ? { fill: "DCE3EE", type: ShadingType.CLEAR, color: "auto" } : (shade ? { fill: "F7F7F5", type: ShadingType.CLEAR, color: "auto" } : undefined),
    children: String(t).split("\n").map((line) => new Paragraph({ keepNext: keepAll && !last, children: runs(line, { size: fs, bold: hdr || undefined }), spacing: { after: 20 } })),
  });
  const trs = [];
  if (header) trs.push(new TableRow({ tableHeader: true, cantSplit: true, children: header.map((h, i) => cell(h, i, true)) }));
  rows.forEach((r, k) => trs.push(new TableRow({ cantSplit: true, children: r.map((t, i) => cell(t, i, false, k % 2 === 1, k === rows.length - 1)) })));
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: cw, rows: trs }), new Paragraph({ children: [], spacing: { after: 100 } })];
}

function pngSize(file) {
  const b = fs.readFileSync(file);
  return [b.readUInt32BE(16), b.readUInt32BE(20)];
}
function image(file, widthIn, caption) {
  const [w, h] = pngSize(file);
  const wpx = Math.round(widthIn * 96);
  const hpx = Math.round((wpx * h) / w);
  const out = [new Paragraph({ alignment: AlignmentType.CENTER, keepNext: !!caption, spacing: { after: 60 }, children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width: wpx, height: hpx }, altText: { title: path.basename(file), description: caption || path.basename(file), name: path.basename(file) } })] })];
  if (caption) out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: runs(caption, { italics: true, size: 18, color: C.ink2 }) }));
  return out;
}

// ---- day page --------------------------------------------------------------
function dayPage(day) {
  const out = [];
  const week = Math.ceil(day.n / 7);
  const label = day.n > 28 ? "Final days \u00B7 6 h" : (day.milestone ? `Week ${week} \u00B7 MILESTONE` : `Week ${week} \u00B7 6 h`);
  const band = new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: [7300, 2060],
    rows: [new TableRow({ cantSplit: true, children: [
      new TableCell({ width: { size: 7300, type: WidthType.DXA }, shading: { fill: C.band, type: ShadingType.CLEAR, color: "auto" }, borders: noBorders, margins: { top: 100, bottom: 100, left: 160, right: 80 }, verticalAlign: VerticalAlign.CENTER,
        // the band text is itself a Heading 2, so each day appears in the table of contents
        children: [new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 0, after: 0 }, children: [new TextRun({ text: `Day ${day.n} \u2013 ${day.title}`, bold: true, color: "FFFFFF", size: 28 })] })] }),
      new TableCell({ width: { size: 2060, type: WidthType.DXA }, shading: { fill: day.milestone ? "EB6834" : "2A78D6", type: ShadingType.CLEAR, color: "auto" }, borders: noBorders, margins: { top: 100, bottom: 100, left: 80, right: 160 }, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: label, bold: true, color: "FFFFFF", size: 20 })] })] }),
    ] })],
  });
  out.push(new Paragraph({ children: [new PageBreak()], spacing: { after: 0 } }));
  out.push(band, new Paragraph({ children: [], spacing: { after: 80 } }));
  out.push(P(`**Goal.** ${day.goal}`));
  const total = day.budget.reduce((a, b) => a + b[1], 0);
  if (Math.abs(total - 6) > 1e-9) warnings.push(`Day ${day.n}: budget sums to ${total}`);
  out.push(...table(["Block", "Hours", "What you do"], [...day.budget.map((b) => [b[0], b[1].toFixed(1), b[2]]), ["**Total**", "**6.0**", ""]], [1.5, 0.7, 6.3]));
  if (day.why) out.push(...callout("Why this matters", day.why));
  out.push(H3("Steps"));
  out.push(...numbered(day.steps));
  if (day.output) { out.push(H3("What correct output looks like")); out.push(...(Array.isArray(day.output) ? bullets(day.output) : [P(day.output)])); }
  if (day.mistakes) { out.push(H3("Common mistakes and fixes")); out.push(...table(["Mistake / symptom", "Fix"], day.mistakes, [1, 1.3])); }
  if (day.extra) out.push(...day.extra);
  out.push(H3("Done when"));
  out.push(...checklist(day.done));
  out.push(P(`**Save:** ${day.save}`));
  out.push(...callout("Tip", `**If you only have 3 hours:** ${day.fallback}`));
  return out;
}

module.exports = { d, W, C, FONT, MONO, runs, P, H1, H2, H3, pageBreak, bullets, numbered, checklist, code, callout, table, image, dayPage, warnings };
