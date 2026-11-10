// Stage 8 — PPTX version of the methodology report (pptxgenjs, structured deck)
const pptxgen = require('pptxgenjs');
const fs = require('fs');
const SKILL = fs.readdirSync('/root/.claude/skills/synced').map(d => `/root/.claude/skills/synced/${d}/pptx`).find(p => fs.existsSync(p));
const { applyTheme } = require(SKILL + '/scripts/apply_theme.js');
const D = JSON.parse(fs.readFileSync('/home/claude/work/deck_data.json'));
const CH = '/home/claude/work/charts/';
const THEME = { name: 'SupeRR Royal', headFontFace: 'Arial', bodyFontFace: 'Calibri',
  colors: { dk1: '1B1B1B', lt1: 'FFFFFF', dk2: '1D2F6F', lt2: 'F3F4F8', accent1: '1D2F6F', accent2: 'E2307C', accent3: '5D9BE6',
            accent4: 'B9D4F4', accent5: '1D5BA6', accent6: '8A8984', hlink: '1D5BA6', folHlink: '6D2E46' } };
const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'SupeRR Selector S2 R1 — Most Reliable Players Under Pressure';
const C = pres.SchemeColor;
const foot = { text: { text: 'SupeRR Selector S2 · R1 · rankings computed from supplied IPL & T20I data 2022–2026', options: { x: 0.5, y: 7.05, w: 9, h: 0.3, fontSize: 9, color: C.accent6 } } };
pres.defineSlideMaster({ title: 'DARK', background: { color: THEME.colors.dk2 },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.7, y: 2.2, w: 11.9, h: 1.6, fontSize: 40, bold: true, color: C.background1, fontFace: 'Arial' }, text: '' } },
            { placeholder: { options: { name: 'body', type: 'body', x: 0.7, y: 3.9, w: 11.9, h: 2.4, fontSize: 18, color: C.background1, valign: 'top' }, text: '' } }] });
pres.defineSlideMaster({ title: 'CONTENT', background: { color: 'FFFFFF' },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 12.3, h: 0.85, fontSize: 30, bold: true, color: C.text2, fontFace: 'Arial', valign: 'middle' }, text: '' } }, foot],
  slideNumber: { x: 12.3, y: 7.05, w: 0.6, h: 0.3, fontSize: 9, color: THEME.colors.accent6 } });

const txt = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, fontSize: 14, color: C.text1, valign: 'top', margin: 0.05 }, o));
const card = (s, x, y, w, h, name) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: C.background2 }, line: { color: C.background2 }, rectRadius: 0.08, objectName: name });
const stat = (s, x, y, w, big, small, name) => { card(s, x, y, w, 1.55, name); txt(s, big, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.8, fontSize: 36, bold: true, color: C.accent2, fontFace: 'Arial' }); txt(s, small, { x: x + 0.2, y: y + 0.92, w: w - 0.4, h: 0.55, fontSize: 12, color: C.text2 }); };
const bul = (items, fs = 14) => items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 6, fontSize: fs } }));
const confColor = { High: '1D5BA6', Medium: '5D9BE6', Low: 'B9D4F4' };

// 1 Title
pres.addSection({ title: 'Opening' });
let s = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Opening' });
s.addText('SupeRR Selector Season 2 — Round 1', { placeholder: 'title' });
s.addText([{ text: 'Identifying the most reliable players under pressure', options: { breakLine: true, color: 'FFB3D3', fontSize: 22, bold: true } },
           { text: 'Context-aware Pressure Index · hierarchical empirical-Bayes ratings · match bootstrap · 18-spec robustness ensemble', options: { breakLine: true } },
           { text: '837 IPL & T20I matches · 193,988 deliveries · 2022–2026 · prepared for Rajasthan Royals, 11 Nov 2026' }], { placeholder: 'body' });
s.addNotes('Title. The whole study is computed from the supplied data; external facts are used only in the RR strategy section.');

// 2 Answer first
pres.addSection({ title: 'Answer' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Answer' });
s.addText('The final top 10s under pressure', { placeholder: 'title' });
const mkTable = (arr, head) => [[head, 'Score', 'Conf.'].map(h => ({ text: h, options: { bold: true, color: 'FFFFFF', fill: { color: THEME.colors.dk2 } } }))]
  .concat(arr.map(p => [{ text: `${p.rank}. ${p.name}` }, { text: p.score.toFixed(1) }, { text: p.conf, options: { color: p.conf === 'Low' ? '8A8984' : '1D5BA6', bold: p.conf === 'High' } }]));
s.addTable(mkTable(D.bat, 'Batters'), { x: 0.5, y: 1.35, w: 5.9, colW: [3.6, 1.0, 1.3], fontSize: 13, rowH: 0.42, border: { type: 'solid', color: 'D9DBE3', pt: 0.5 }, fontFace: 'Calibri', objectName: 'bat-table' });
s.addTable(mkTable(D.bowl, 'Bowlers'), { x: 6.9, y: 1.35, w: 5.9, colW: [3.6, 1.0, 1.3], fontSize: 13, rowH: 0.42, border: { type: 'solid', color: 'D9DBE3', pt: 0.5 }, fontFace: 'Calibri', objectName: 'bowl-table' });
txt(s, 'Score = mean 0–100 Pressure Performance Score across 18 model specifications. Confidence combines bootstrap P(top 10), spec robustness and sample size.', { x: 0.5, y: 6.3, w: 12.3, h: 0.5, fontSize: 11, color: C.accent6, italic: true });
s.addNotes('Answer first. 7 High, 10 Medium, 3 Low confidence finalists. Russell and Karthik are retired from IPL: ranking findings, not auction options.');

// 3 Data
pres.addSection({ title: 'Data & pressure' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Data & pressure' });
s.addText('Clean data first: every field validated, nothing imputed', { placeholder: 'title' });
stat(s, 0.5, 1.35, 2.9, '837', 'IPL (367) + T20I (470) matches analysed', 'st1');
stat(s, 3.6, 1.35, 2.9, '16', 'missing matches — all abandoned, no data lost', 'st2');
stat(s, 6.7, 1.35, 2.9, '75%', 'rebuilt totals within ±3 runs of official margins', 'st3');
stat(s, 9.8, 1.35, 3.0, '30', 'non-IPL T20 matches excluded from the core', 'st4');
txt(s, bul(['extras1_runs is a category code (6 = none, 2 = wide, 3 = leg-bye …): never summed as runs',
            '"runs" = off the bat only; bowler conceded = bat runs + 1 per wide/no-ball; byes & leg-byes excluded',
            'Legal balls counted from flags (over_ball_num reaches 13); super overs (38 rows) excluded',
            'Bowler wickets = caught, bowled, LBW, stumped, hit-wicket; run-outs and retirements never credited',
            'All joins on player_id; 7 duplicate display names flagged (e.g. Rashid Khan 4722 vs 20172)']), { x: 0.5, y: 3.15, w: 12.3, h: 3.6, fontSize: 15 });
s.addNotes('Extra-run amounts (e.g. 4 byes) are not recorded, so chase targets carry about ±3 runs of noise; player batting runs are exact.');

// 4 Pressure definition
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Data & pressure' });
s.addText('Pressure Index: pre-ball state only, 0–100', { placeholder: 'title' });
const comp = [['Component', '2nd inns', '1st inns'], ['Chase difficulty  σ(4·ln D), D = need / E_rem(balls, wkts)', '0.25', '—'], ['Required rate vs competition par', '0.10', '—'],
  ['Closeness 4·WP·(1−WP) (win-prob model, AUC 0.90)', '0.20', '—'], ['Projected-total shortfall vs par', '—', '0.30'], ['Wickets above expected for the stage', '—', '0.15'],
  ['Wickets lost', '0.15', '0.10'], ['Stage (final five overs boosted)', '0.15', '0.20'], ['Recent collapse (wkts, last 18 balls)', '0.10', '0.15'], ['Scoring squeeze (dots, last 12 balls)', '0.05', '0.10']];
s.addTable(comp.map((r, i) => r.map(c => ({ text: c, options: i === 0 ? { bold: true, color: 'FFFFFF', fill: { color: THEME.colors.dk2 } } : {} }))),
  { x: 0.5, y: 1.35, w: 7.6, colW: [5.4, 1.1, 1.1], fontSize: 12, rowH: 0.4, border: { type: 'solid', color: 'D9DBE3', pt: 0.5 }, objectName: 'pi-table' });
card(s, 8.5, 1.35, 4.3, 5.3, 'pi-card');
txt(s, [{ text: 'From score to index', options: { bold: true, fontSize: 16, color: C.text2, breakLine: true } },
        { text: 'PI = percentile rank of the weighted composite within competition × innings', options: { breakLine: true, paraSpaceAfter: 8 } },
        { text: 'Low < 50 · Medium 50–75 · High 75–90 · Extreme ≥ 90', options: { bold: true, color: C.accent2, breakLine: true, paraSpaceAfter: 8 } },
        { text: 'Primary pressure set: PI ≥ 75. Tested at 65 and 85.', options: { breakLine: true, paraSpaceAfter: 8 } },
        { text: 'Dead chases (WP < 10% or > 90%) are down-weighted by a contest-alive factor.', options: { breakLine: true, paraSpaceAfter: 8 } },
        { text: 'Equal-weight alternative index: Spearman 0.85 with the main index.' }], { x: 8.75, y: 1.55, w: 3.85, h: 5.0, fontSize: 14 });
s.addNotes('E_rem is a monotone gradient-boosted resource curve (DLS-style) learned from full first innings by competition and season.');

// 5 PI validation
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Data & pressure' });
s.addText('The index finds genuine danger', { placeholder: 'title' });
s.addImage({ path: CH + 'pi_distribution.png', x: 0.5, y: 1.3, w: 12.3, h: 3.69, altText: 'Chase win %, dismissal rate and scoring rate by pressure category' });
stat(s, 0.5, 5.2, 4.0, '+38%', 'dismissal rate: Extreme vs Low pressure (7.2 vs 5.2 per 100 balls)', 'v1');
stat(s, 4.65, 5.2, 4.0, '62% → 30%', 'chase win rate: Low vs High pressure states', 'v2');
stat(s, 8.8, 5.2, 4.0, '144 → 130', 'bat runs per 100 balls, despite pressure clustering at the death', 'v3');

// 6 Model
pres.addSection({ title: 'Model' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Model' });
s.addText('Four steps from ball to rating', { placeholder: 'title' });
const steps = [['1  Expect', 'Cross-fitted gradient boosting predicts runs, dismissal, dot, boundary for an average player in the same context: competition, season, over, wickets, batting position, pace/spin, opposition, pressure'],
  ['2  Value', 'RAA = (runs − E[runs]) − λ·(out − P(out)); bowlers mirror it as RSAA. λ = run value of a wicket in that state (11.7 powerplay → 3.5 death)'],
  ['3  Shrink', 'θ = r·x_pressure + (1 − r)·(a + b·x_normal), r = n/(n+k). Shrinks toward the player\'s OWN baseline; k ≈ 390 (bat) / 460 (bowl) IPL balls'],
  ['4  Combine', 'Weighted z-score composite + 10th-pct lower bound + pressure-vs-normal delta (+ death-over value for bowlers); IPL:T20I 70:30; averaged over 18 specs']];
steps.forEach((st, i) => { const x = 0.5 + i * 3.12; card(s, x, 1.45, 2.95, 4.9, 'step' + i);
  txt(s, st[0], { x: x + 0.2, y: 1.6, w: 2.55, h: 0.6, fontSize: 22, bold: true, color: C.accent2, fontFace: 'Arial' });
  txt(s, st[1], { x: x + 0.2, y: 2.3, w: 2.55, h: 3.9, fontSize: 14 }); });
txt(s, 'Eligibility (fixed before ranking): batters ≥ 100 pressure balls, bowlers ≥ 120; ≥ 10 matches; ≥ 30 IPL pressure balls; ≥ 200 normal balls → 72 batters, 90 bowlers.', { x: 0.5, y: 6.45, w: 12.3, h: 0.5, fontSize: 12, color: C.accent6, italic: true });

// 7 Insight
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Model' });
s.addText('Raw "clutch" numbers are mostly noise, so shrink smartly', { placeholder: 'title' });
stat(s, 0.5, 1.35, 3.0, '≈ 0', 'split-half reliability of raw pressure batting value', 'i1');
stat(s, 0.5, 3.05, 3.0, '0.47', 'correlation of normal vs pressure batting scoring', 'i2');
stat(s, 0.5, 4.75, 3.0, '0.34', 'split-half reliability of pressure bowling value', 'i3');
s.addChart(pres.charts.BAR, [{ name: 'Raw pressure average', labels: ['Batting', 'Bowling'], values: [101.0, 78.1] }, { name: 'League average', labels: ['Batting', 'Bowling'], values: [54.9, 53.8] },
  { name: 'Hierarchical EB (this model)', labels: ['Batting', 'Bowling'], values: [52.2, 51.2] }],
  { x: 3.9, y: 1.35, w: 8.9, h: 5.0, barDir: 'col', chartColors: ['B9D4F4', '8A8984', 'E2307C'], showValue: true, dataLabelPosition: 'outEnd', dataLabelFontSize: 11, dataLabelColor: '1B1B1B',
    showLegend: true, legendPos: 'b', legendFontSize: 12, showTitle: true, title: 'Season hold-out: predict 2025–26 pressure value from 2022–24 (weighted MSE ×10⁻³, lower is better)', titleFontSize: 13, titleColor: '1D2F6F',
    catAxisLabelColor: '5D5C58', valAxisLabelColor: '5D5C58', valGridLine: { color: 'E6E5E0', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', legendFontFace: '+mn-lt', titleFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt', objectName: 'holdout-chart' });
txt(s, 'Honest caveat: for batting, the normal baseline alone predicts slightly better (47.9). Batting ranks describe evidence, not strong forecasts.', { x: 3.9, y: 6.4, w: 8.9, h: 0.5, fontSize: 11, color: C.accent6, italic: true });

// 8/9 Batters, 10/11 Bowlers
function topSlide(key, label, valLabel, scatter, boot, sect) {
  pres.addSection({ title: sect });
  let s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: sect });
  s.addText(`Top 10 ${label}: score, sample and confidence`, { placeholder: 'title' });
  const arr = D[key];
  s.addChart(pres.charts.BAR, [{ name: 'Pressure score', labels: arr.map(p => `${p.rank}. ${p.name}`).reverse(), values: arr.map(p => p.score).reverse() }],
    { x: 0.4, y: 1.3, w: 5.6, h: 5.5, barDir: 'bar', chartColors: arr.map(p => confColor[p.conf]).reverse(), invertedColors: arr.map(p => confColor[p.conf]).reverse(), showValue: true, dataLabelPosition: 'outEnd', dataLabelFontSize: 11,
      dataLabelColor: '1B1B1B', showLegend: false, valAxisMaxVal: 110, valAxisHidden: true, catAxisLabelFontSize: 12, catAxisLabelColor: '1B1B1B', valGridLine: { style: 'none' }, catGridLine: { style: 'none' },
      showTitle: true, title: 'Ensemble Pressure Score (bar shade = confidence)', titleFontSize: 12, titleColor: '1D2F6F', catAxisLabelFontFace: '+mn-lt', titleFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt', objectName: key + '-bar' });
  const head = ['Player', 'IPL/T20I balls', valLabel, 'Normal', 'Δ', key === 'bat' ? 'SR (exp.)' : 'Econ (exp.)', 'P(top10)', 'Conf.'];
  const rows = [head.map(h => ({ text: h, options: { bold: true, color: 'FFFFFF', fill: { color: THEME.colors.dk2 } } }))].concat(arr.map(p => [p.name, `${p.nI}/${p.nT}`, p.pv.toFixed(1), p.nv.toFixed(1), (p.d > 0 ? '+' : '') + p.d.toFixed(1),
    key === 'bat' ? `${p.sr.toFixed(0)} (${p.exp.toFixed(0)})` : `${p.sr.toFixed(2)} (${p.exp.toFixed(2)})`, `${p.boot}%`, p.conf].map(t => ({ text: String(t) }))));
  s.addTable(rows, { x: 6.2, y: 1.35, w: 6.7, colW: [1.6, 0.85, 0.65, 0.65, 0.55, 0.95, 0.65, 0.8], fontSize: 10.5, rowH: 0.43, border: { type: 'solid', color: 'D9DBE3', pt: 0.5 }, objectName: key + '-table' });
  txt(s, `${valLabel} = ${key === 'bat' ? 'runs added' : 'runs saved'} above context expectation per 100 pressure balls (shrunk). Δ = pressure − own normal. P(top10) from 300 match bootstraps.`, { x: 6.2, y: 6.25, w: 6.7, h: 0.6, fontSize: 10, color: C.accent6, italic: true });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: sect });
  s.addText(`${label[0].toUpperCase() + label.slice(1)}: own baseline and uncertainty`, { placeholder: 'title' });
  s.addImage({ path: CH + scatter, x: 0.5, y: 1.3, w: 6.0, h: 4.48, altText: `${label} pressure vs normal scatter` });
  s.addImage({ path: CH + boot, x: 6.75, y: 1.3, w: 6.1, h: 3.58, altText: `${label} bootstrap rank intervals` });
  txt(s, bul(key === 'bat' ? ['Tim David, Klaasen, Suryakumar: High confidence, top 10 in all 18 specs', 'Shashank Singh: biggest lift over his own baseline (+11.8)', 'Abhishek Sharma & Naman Dhir: Low confidence; small pressure samples']
    : ['Narine: rank 1 in 15 of 18 specs, P(top 10) = 99%', 'Bumrah & Pathirana: High-confidence death specialists', 'Mustafizur: Low confidence (P(top 10) = 32%)'], 13), { x: 6.75, y: 5.05, w: 6.1, h: 1.8 });
}
topSlide('bat', 'batters', 'Press. RAA', 'bat_press_vs_normal.png', 'bat_bootstrap.png', 'Batters');
topSlide('bowl', 'bowlers', 'Press. RSAA', 'bowl_press_vs_normal.png', 'bowl_bootstrap.png', 'Bowlers');

// 12 Robustness
pres.addSection({ title: 'Robustness' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Robustness' });
s.addText('Ranks hold across 18 model specifications', { placeholder: 'title' });
s.addImage({ path: CH + 'bat_sensitivity.png', x: 0.5, y: 1.25, w: 12.3, h: 2.85, altText: 'Batting rank sensitivity heatmap' });
s.addImage({ path: CH + 'bowl_sensitivity.png', x: 0.5, y: 4.15, w: 12.3, h: 2.85, altText: 'Bowling rank sensitivity heatmap' });
s.addNotes('Specs: pressure definition (main / equal-weight) x threshold (65/75/85th pct) x IPL:T20I (60:40/70:30/80:20). Overlap with final top 10: batting 7-9, bowling 8-10.');

// 13 RR
pres.addSection({ title: 'RR strategy' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'RR strategy' });
s.addText('For RR: buy pressure death bowling first, then a finisher', { placeholder: 'title' });
card(s, 0.5, 1.35, 6.0, 5.4, 'rr-finding');
txt(s, [{ text: 'Data finding', options: { bold: true, fontSize: 17, color: C.text2, breakLine: true } },
        ...bul(['No IPL 2026 RR player reaches either top 20', 'Best RR pressure bowler: Archer, 24th of 90; Deshpande 62nd, Bishnoi 80th, Curran 84th, Sandeep Sharma 85th',
                'Best RR pressure batters: Jurel 26th, Parag 27th of 72', 'Jaiswal & Sooryavanshi: openers, too few pressure balls to judge'], 14)], { x: 0.75, y: 1.55, w: 5.5, h: 5.0 });
card(s, 6.8, 1.35, 6.0, 5.4, 'rr-opinion');
txt(s, [{ text: 'Opinion (role fit)', options: { bold: true, fontSize: 17, color: C.accent2, breakLine: true } },
        ...bul(['Death: Pathirana, Bumrah (High); Indian-slot options Mohsin Khan, Bhuvneshwar', 'Middle-overs spin: Narine; Indian-slot Kuldeep, Varun Chakravarthy',
                'Finisher No. 5–7: Tim David, Klaasen; Indian-slot Shashank Singh', 'Russell & Karthik retired: next eligible are Tilak Varma, Rajat Patidar, Tristan Stubbs',
                'IPL 2027 retentions not yet official (11 Nov 2026): no availability assumed'], 14)], { x: 7.05, y: 1.55, w: 5.5, h: 5.0 });
s.addNotes('Squad source: rajasthanroyals.com (15-16 Dec 2025) cross-checked with the IPL 2026 mapping in the data.');

// 14 Close
pres.addSection({ title: 'Close' });
s = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Close' });
s.addText('Limits we report, not hide', { placeholder: 'title' });
s.addText(bul(['Multi-run extras not recorded: chase targets carry ±3 runs of noise', 'Batting pressure skill has weak out-of-sample signal; bowling is stronger',
               'Index weights are judgement-based: mitigated by an equal-weight alternative and the 18-spec ensemble', 'Full methodology, code and the all-player ranking dataset accompany this deck'], 17), { placeholder: 'body' });

(async () => {
  const f = '/home/claude/work/out/SupeRR_Selector_S2_R1_Deck.pptx';
  await pres.writeFile({ fileName: f }); await applyTheme(f, THEME); console.log('written');
})();
