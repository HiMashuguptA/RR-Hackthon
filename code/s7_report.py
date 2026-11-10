"""Stage 7 — methodology report PDF (reportlab)."""
import pandas as pd, numpy as np, json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image,
                                PageBreak, KeepTogether, NextPageTemplate, CondPageBreak)
W = '/home/claude/work/'; CH = W + 'charts/'; OUT = '/home/claude/work/out/'
import os; os.makedirs(OUT, exist_ok=True)
NAVY = colors.HexColor('#1d2f6f'); PINK = colors.HexColor('#e2307c'); INK = colors.HexColor('#1b1b1b'); MUTED = colors.HexColor('#5d5c58')
LIGHT = colors.HexColor('#f3f4f8'); LINE = colors.HexColor('#d9dbe3')
A = json.load(open(W + 'audit_stage1.json')); S3 = json.load(open(W + 'stage3.json')); CAL = json.load(open(W + 'calib.json'))
S4 = json.load(open(W + 'stage4.json')); V = json.load(open(W + 'verify.json'))
BT = pd.read_pickle(W + 'bat_table.pkl'); BW = pd.read_pickle(W + 'bowl_table.pkl')
tb = BT[BT.final_rank <= 10].sort_values('final_rank'); tw = BW[BW.final_rank <= 10].sort_values('final_rank')

ss = getSampleStyleSheet()
H1 = ParagraphStyle('H1', parent=ss['Heading1'], fontName='Helvetica-Bold', fontSize=17, textColor=NAVY, spaceBefore=4, spaceAfter=8)
H2 = ParagraphStyle('H2', parent=ss['Heading2'], fontName='Helvetica-Bold', fontSize=12.5, textColor=NAVY, spaceBefore=10, spaceAfter=5)
H3 = ParagraphStyle('H3', parent=ss['Heading3'], fontName='Helvetica-Bold', fontSize=10.5, textColor=PINK, spaceBefore=6, spaceAfter=3)
B = ParagraphStyle('B', parent=ss['BodyText'], fontName='Helvetica', fontSize=9.4, leading=13.2, textColor=INK, spaceAfter=5)
SM = ParagraphStyle('SM', parent=B, fontSize=8, leading=10.5, textColor=MUTED)
TC = ParagraphStyle('TC', parent=B, fontSize=7.6, leading=9.6, spaceAfter=0)
TCB = ParagraphStyle('TCB', parent=TC, fontName='Helvetica-Bold', textColor=colors.white)
BUL = ParagraphStyle('BUL', parent=B, leftIndent=12, bulletIndent=2, spaceAfter=2)
CALL = ParagraphStyle('CALL', parent=B, backColor=LIGHT, borderColor=LINE, borderWidth=.6, borderPadding=7, spaceBefore=6, spaceAfter=10)
MONO = ParagraphStyle('MONO', parent=B, fontName='Courier', fontSize=8.2, leading=11, backColor=LIGHT, borderPadding=6, spaceBefore=4, spaceAfter=8)

def P(t, s=B): return Paragraph(t, s)
def bullets(items): return [Paragraph(i, BUL, bulletText='•') for i in items]
def img(name, w=170):
    from PIL import Image as PI
    im = PI.open(CH + name); r = im.height / im.width
    return Image(CH + name, width=w * mm, height=w * mm * r)
def table(rows, widths, head=True, zebra=True, fs=None):
    data = [[Paragraph(str(c), TCB if (head and i == 0) else TC) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    st = [('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LINEBELOW', (0, 0), (-1, -1), .3, LINE),
          ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3), ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4)]
    if head: st += [('BACKGROUND', (0, 0), (-1, 0), NAVY)]
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0: st.append(('BACKGROUND', (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(st)); return t
f1 = lambda x: f'{x:.1f}'; f2 = lambda x: f'{x:.2f}'; pct = lambda x: f'{100*x:.0f}%'

def on_page(c, doc):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, A4[1] - 9 * mm, A4[0], 9 * mm, fill=1, stroke=0)
    c.setFillColor(PINK); c.rect(0, A4[1] - 10 * mm, A4[0], 1 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 8)
    c.drawString(15 * mm, A4[1] - 6 * mm, 'SupeRR Selector Season 2  |  Round 1: Most Reliable Players Under Pressure')
    c.setFont('Helvetica', 8); c.drawRightString(A4[0] - 15 * mm, A4[1] - 6 * mm, 'Methodology Report')
    c.setFillColor(MUTED); c.setFont('Helvetica', 7.5)
    c.drawString(15 * mm, 8 * mm, 'All rankings computed from the supplied IPL & T20I data (2022–2026). Reproducible code supplied with this report.')
    c.drawRightString(A4[0] - 15 * mm, 8 * mm, f'Page {doc.page}')
    c.restoreState()
def on_cover(c, doc):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    c.setFillColor(PINK); c.rect(0, A4[1] * .38, A4[0], 2.2 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont('Helvetica', 12); c.drawString(20 * mm, A4[1] - 40 * mm, 'RAJASTHAN ROYALS  ×  UNSTOP')
    c.setFont('Helvetica-Bold', 34); c.drawString(20 * mm, A4[1] - 75 * mm, 'SupeRR Selector')
    c.drawString(20 * mm, A4[1] - 90 * mm, 'Season 2')
    c.setFont('Helvetica-Bold', 17); c.setFillColor(colors.HexColor('#ffb3d3'))
    c.drawString(20 * mm, A4[1] - 110 * mm, 'Round 1 — Identifying the Most Reliable Players Under Pressure')
    c.setFillColor(colors.white); c.setFont('Helvetica', 11.5)
    y = A4[1] - 128 * mm
    for line in ['Methodology report: a context-aware Pressure Index, hierarchical (empirical-Bayes)',
                 'player ratings, match-level bootstrap and an 18-specification robustness ensemble.',
                 '', 'Data: 837 IPL & T20I matches · 193,988 deliveries · 2022–2026']:
        c.drawString(20 * mm, y, line); y -= 6.5 * mm
    c.setFont('Helvetica', 9.5); c.drawString(20 * mm, 25 * mm, 'Prepared for the Rajasthan Royals analytics & recruitment team  ·  11 November 2026')
    c.restoreState()

doc = BaseDocTemplate(OUT + 'SupeRR_Selector_S2_R1_Methodology_Report.pdf', pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                      topMargin=17 * mm, bottomMargin=15 * mm, title='SupeRR Selector S2 R1 — Most Reliable Players Under Pressure',
                      author='SupeRR Selector submission')
fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')
doc.addPageTemplates([PageTemplate('cover', [fr], onPage=on_cover), PageTemplate('body', [fr], onPage=on_page)])
s = [NextPageTemplate('body'), PageBreak()]

# ---------------- Contents
s += [P('Contents', H1)]
toc = ['Executive summary', 'Problem understanding', 'Dataset overview', 'Data cleaning & validation', 'Mathematical definition of pressure',
       'Pressure Index methodology & validation', 'Batting reliability model', 'Bowling reliability model', 'IPL and T20I comparison',
       'Statistical reliability & validation', 'Top 10 batters — detailed evidence', 'Top 10 bowlers — detailed evidence',
       'Rajasthan Royals IPL 2027 strategic implications', 'Key findings & recommendations', 'Limitations & future improvements',
       'Technical appendix — formulas, metrics, assumptions']
s += [P(f'{i+2}. {t}') for i, t in enumerate(toc)]
s += [Spacer(1, 6), P('Reading guide: <b>proven statistical findings</b> are reported with sample sizes and uncertainty. <b>Strategic opinion</b> (Section 14) is labelled as such and kept separate from the data.', CALL), PageBreak()]

# ---------------- 2 Executive summary
s += [P('2. Executive summary', H1)]
s += [P(f'We built a pressure-aware rating system for every batter and bowler in the supplied IPL and T20I data (2022–2026). The system has four steps. '
        f'(1) A <b>Pressure Index (0–100)</b> for every delivery, calculated only from the match state <i>before</i> that ball. '
        f'(2) Context <b>expectation models</b> that say what an average player would produce on that exact ball. '
        f'(3) <b>Hierarchical empirical-Bayes ratings</b> that shrink small samples toward each player\'s own normal-pressure baseline. '
        f'(4) An <b>18-specification ensemble</b> with a 300-resample match-level bootstrap, to measure how robust each rank is.')]
s += [P('Headline results', H3)]
rows = [['Rank', 'Top-10 batters', 'Score', 'Conf.', 'Top-10 bowlers', 'Score', 'Conf.']]
for i in range(10):
    a, b_ = tb.iloc[i], tw.iloc[i]
    rows.append([i + 1, a['name'], f1(a.pressure_score), a.confidence, b_['name'], f1(b_.pressure_score), b_.confidence])
s += [table(rows, [12, 42, 16, 18, 44, 16, 18])]
s += [Spacer(1, 6), P('Key findings', H3)]
hb, hw = S3['bat']['holdout'], S3['bowl']['holdout']
s += bullets([
    'Pressure is real and measurable. Batter dismissal rates rise from 5.2 to 7.2 per 100 balls between Low- and Extreme-pressure states, and scoring falls from 144 to 130 runs per 100 balls. The chase win-probability model built inside the index has an AUC of 0.90.',
    'Pressure-specific "clutch" ability is <b>small and noisy</b>. Split-half reliability of raw pressure batting value is close to zero. In contrast, a batter\'s normal-pressure ability predicts their pressure output well (r = 0.47 for run-scoring). This is why the model shrinks each player toward their <i>own</i> baseline rather than the league average.',
    f'In a 2022–24 → 2025–26 hold-out, the hierarchical estimate cut prediction error by about half (batting) and a third (bowling) relative to raw pressure averages. Weighted MSE fell from {hb["weighted_mse_x1000"]["raw_pressure_mean"]} to {hb["weighted_mse_x1000"]["EB_hierarchical"]} for batting and from {hw["weighted_mse_x1000"]["raw_pressure_mean"]} to {hw["weighted_mse_x1000"]["EB_hierarchical"]} for bowling (×10<super>-3</super>). Bowling pressure ratings carry more repeatable signal than batting ratings.',
    'Both top-10 lists are robust. Across all 18 specifications, 7–10 of the 10 batters and 8–10 of the 10 bowlers stay in the top 10. Seven of the 20 finalists are High confidence, ten Medium and three Low (labelled throughout).',
    'Availability note for the auction (verified externally, not used in ranking): Andre Russell retired from the IPL in Nov 2025 and Dinesh Karthik after IPL 2024. Both remain in the data-driven Unstop ranking, but Section 14 names actionable alternates.',
])
s += [PageBreak()]

# ---------------- 3 Problem understanding
s += [P('3. Problem understanding', H1)]
s += [P('The brief asks for the 10 batters and 10 bowlers who deliver <b>most reliably</b> when the match is on the line, relative to their usual level. We translated it into four measurable requirements:')]
s += bullets(['<b>Context, not totals.</b> Raw runs and wickets reward opportunity. Every outcome is judged against what an average player would produce in the identical pre-ball situation (competition, season, innings, over, wickets, batting position, pace/spin, opposition and pressure state).',
              '<b>Pressure must be defined before the ball is bowled.</b> The index uses only information available at the moment of delivery, so a ball is never labelled "pressure" because of what happened next.',
              '<b>Reliability over peaks.</b> Short hot streaks are shrunk. Uncertainty is measured at match level (balls within a match are not independent). Ranks are stress-tested against alternative definitions.',
              '<b>IPL first.</b> The decision context is the IPL 2027 auction, so IPL evidence carries the primary weight (70:30 blend) and T20I evidence is supplementary.'])
s += [P('What "best under pressure" means in this report', H3),
      P('A player ranks highly if, in high-pressure states, they add more runs (batters) or save more runs (bowlers) than the context expects. Wickets are converted to runs using the run value of a wicket in that state. The ranking also rewards doing this consistently (high lower confidence bound) and doing at least as well as their own normal standard.', CALL)]

# ---------------- 4 Dataset overview
s += [P('4. Dataset overview', H1)]
r = A['rows']
s += [table([['File', 'Records', 'Use'],
             ['ball_by_ball.csv', f"{r['ball_by_ball.csv']:,}", 'Delivery-level events; striker_id / bowler_id for players; match_id join'],
             ['matches.csv', f"{r['matches.csv']:,}", 'Match metadata, revised (DLS) overs/targets, winner'],
             ['competitions.csv', f"{r['competitions.csv']:,}", 'comp_id → name, format (T20 / T20I), season'],
             ['teams.csv', f"{r['teams.csv']:,}", 'Team names per competition'],
             ['playing_eleven.csv', f"{r['playing_eleven.csv']:,}", 'Appearances (audit only)'],
             ['competition_team_player_mapping.csv', f"{r['competition_team_player_mapping.csv']:,}", 'Exact display names (dropdown) per player_id']],
            [52, 22, 100])]
s += [Spacer(1, 6), table([['Population', 'Matches with ball-by-ball', 'Deliveries (inns 1–2)', 'Treatment'],
                           ['IPL 2022–2026 (5 seasons)', A['matches_by_group']['IPL'], f"{A['rows_by_group']['IPL']:,}", 'Primary evidence (70%)'],
                           ['T20 Internationals', A['matches_by_group']['T20I'], f"{A['rows_by_group']['T20I']:,}", 'Supplementary evidence (30%)'],
                           ['Other T20 (Emerging Teams Asia Cup 2024, Asia Cup Rising Stars 2025)', A['matches_by_group']['OtherT20'], f"{A['rows_by_group']['OtherT20']:,}", 'Excluded: A-team/emerging events, not comparable']],
                          [70, 30, 32, 42])]
s += [Spacer(1, 6), P('Competition scoring environments differ a lot. The model estimates a par first-innings total for each competition-season and uses it to normalise required rates:')]
par = A['par_first_innings_total']
s += [table([['Competition'] + [k.split()[1] for k in par if k.startswith('IPL')],
             ['IPL par 1st-inns total'] + [f1(v) for k, v in par.items() if k.startswith('IPL')],
             ['T20I par 1st-inns total'] + [f1(v) for k, v in par.items() if k.startswith('T20I')]], [45, 25, 25, 25, 25, 25])]
s += [P('IPL scoring rose by about 23 runs per innings from 2022 to 2026, consistent with the Impact Player era. This is why season-level normalisation is essential.', SM), PageBreak()]

# ---------------- 5 Data cleaning
s += [P('5. Data cleaning & validation', H1)]
s += [P('Every field was checked against the others before use. The table records each decision; nothing was imputed or manufactured.')]
s += [table([['Issue found', 'Evidence', 'Decision'],
             ['883 matches vs 867 with ball-by-ball', 'All 16 missing matches have result = "Match Abandoned"', 'No deliveries lost; no distortion of rankings'],
             ['Super overs', '38 rows in innings 3–4 (6 matches)', 'Excluded from all regular-innings metrics'],
             ['extras1_runs is a category code, not runs', 'Perfect 1:1 map: 6=none, 2=wide, 3=leg-bye, 4=bye, 1=Overstep (no-ball), 5=other (no-ball), 7=penalty', 'Never summed. Used extras_type instead'],
             ['"runs" = runs off the bat only', 'runs = 0 on every wide (7,714), bye (529) and leg-bye row', 'Batting runs = runs; bowler conceded = runs + 1 per wide/no-ball; byes & leg-byes excluded'],
             ['Extra amounts not recorded', 'A wide or bye that goes for 4 is stored as one extras event', 'Team totals approximated at +1 per extra (see validation below). Bowler conceded slightly understates multi-run wides'],
             ['"other" extras behave as no-balls', 'With wides, Overstep and "other" illegal, 98.2% of all overs contain exactly 6 legal balls and only one contains 7', 'Legal ball = not wide / Overstep / other'],
             ['over_ball_num > 6', 'Up to 13 (re-bowled deliveries)', 'Legal balls counted by cumulative legal flags, never from over numbers'],
             ['Boundary-flag inconsistencies', '20 rows of 4 and 3 rows of 6 off the bat without a flag; flags never set for other values', 'Boundary = is_four or is_six (all-run 4s and overthrows are not boundaries)'],
             ['is_wicket includes non-bowler dismissals', 'RunOut 600, Retire Out 6, Obstructing 3', 'Bowler wickets = Caught, Bowled, LBW, Stumped, Hit Wicket only. Retired-out is not a batter failure'],
             ['Duplicate display names', '7 names map to 2 IDs (e.g. Rashid Khan 4722 = Afghanistan/GT; 20172 = Nepal)', 'All joins on player_id. Finalist IDs listed for dropdown use'],
             ['DLS / reduced matches', 'Revised overs stored in balls (e.g. 114 = 19 overs)', 'Balls available and target taken from revised fields']],
            [44, 66, 64])]
s += [P('Validation of scoring against independent results', H3),
      P('No external scorecards are bundled with the data, so we validated reconstructed innings totals against the run margins in matches.csv (391 non-DLS matches won by runs). With +1 run per extra event, 32% reproduce the margin exactly, 75% are within ±3 runs and 92% within ±5 runs. The errors are symmetric, consistent with unrecorded multi-run extras in both innings. Implication: chase targets carry ±3 runs of noise. This affects the Pressure Index only marginally, because it enters through a log-ratio, and it does not affect player batting runs or bowler-conceded runs, which are fully recorded apart from multi-run wides.', CALL)]
s += [P('Every top-10 player\'s raw career totals (runs, balls, dismissals; legal balls, conceded, bowler wickets) were recomputed by separate code directly from the CSVs and match the pipeline exactly (Section 11).', SM), PageBreak()]

# ---------------- 6 Pressure definition
s += [P('6. Mathematical definition of pressure', H1)]
s += [P('For each delivery we know the pre-ball state: runs R, wickets lost W, legal balls bowled L, balls available N (revised for DLS), recent wickets (last 18 legal balls) and recent team dot balls (last 12 legal balls). Two learned functions turn this state into resource and danger measures.')]
s += [P('<b>Resource curve E<sub>rem</sub>(b, w).</b> The expected runs still to come with b balls left and w wickets down, by competition and season. It is a monotone gradient-boosted model fitted on full first innings (DLS-style resources, learned from the data). It gives two quantities used throughout: the projected total and the <b>run value of a wicket</b> λ = E<sub>rem</sub>(b, w) − E<sub>rem</sub>(b, w+1). λ averages 11.7 runs in the powerplay, 6.5 in the middle overs and 3.5 at the death.'),
      P('<b>Chase difficulty</b> D = runs needed / E<sub>rem</sub>(b, w). This single ratio combines runs remaining, balls remaining and wickets in hand: D = 1 is a par chase, D = 1.5 needs 50% more than the resources usually yield.'),
      P(f'<b>Chase win probability</b> WP: logistic regression on ln D, fraction of balls left, wickets lost and ln(RRR / par RR). Fitted on {A["wp_model"]["n"]:,} second-innings deliveries; AUC {A["wp_model"]["auc"]}, Brier {A["wp_model"]["brier"]}. It uses only pre-ball state.')]
s += [P('Component scores (each mapped to 0–1)', H3)]
s += [table([['Component', 'Formula', 'Innings', 'Weight'],
             ['Chase difficulty', 'σ(4·ln D)', '2nd', '0.25'],
             ['Required rate vs norm', 'σ(4·ln(RRR / par RR<sub>comp,season</sub>))', '2nd', '0.10'],
             ['Match situation (closeness)', '4·WP·(1−WP)', '2nd', '0.20'],
             ['Projected-total shortfall', 'σ(8·(par − (R + E<sub>rem</sub>)) / par)', '1st', '0.30'],
             ['Wickets above expected', 'σ((W − E[W | L]) / 1.5)', '1st', '0.15'],
             ['Wickets lost', 'W / 10', 'both', '0.15 (2nd) / 0.10 (1st)'],
             ['Innings stage', '0.5·L/N + 0.5·[balls left ≤ 30]', 'both', '0.15 (2nd) / 0.20 (1st)'],
             ['Recent collapse', 'min(wkts in last 18 legal, 3) / 3', 'both', '0.10 (2nd) / 0.15 (1st)'],
             ['Scoring squeeze', 'min(team dots in last 12 legal / 8, 1)', 'both', '0.05 (2nd) / 0.10 (1st)']],
            [42, 72, 18, 42])]
s += [P('σ is the logistic function. Second-innings raw scores are multiplied by a <b>contest-alive factor</b> 0.5 + 0.5·min(1, closeness / 0.36), which halves pressure in decided chases (WP &lt; 10% or &gt; 90%). Needing 80 off 12 balls is a lost cause, not pressure.', SM)]
s += [P('From raw score to a 0–100 index', H3),
      P('PI = 100 × percentile rank of the raw composite <b>within each competition group and innings</b>. Calibrating separately for IPL and T20I stops the more mismatched T20I fixtures from distorting the scale, and gives each innings its own failure mode (building a total vs chasing one). Categories: <b>Low</b> &lt; 50, <b>Medium</b> 50–75, <b>High</b> 75–90, <b>Extreme</b> ≥ 90. The primary "pressure" set is PI ≥ 75 (High + Extreme, the top quarter of match states). The 65th and 85th percentiles are tested as alternatives.', CALL)]
s += [P('Why these weights? Each innings gives its largest weight to the most direct statement of the failure risk (chase difficulty plus closeness in a chase; projected shortfall when setting a total). Stage, collapse and squeeze terms capture the escalation the brief describes. Because weights are a judgement, we also built an <b>equal-weight alternative index</b> (all components weighted equally, no alive factor). Its Spearman correlation with the main index is ' + f'{A["pi_spec_corr"]}' + ', and every final ranking was re-run under both.', B), PageBreak()]

# ---------------- 7 PI methodology & validation
s += [P('7. Pressure Index methodology & validation', H1)]
s += [img('pi_distribution.png', 174)]
s += [P('The index separates pressure from ordinary play on outcomes it was never trained on. Batter dismissal rates rise 38% from Low to Extreme pressure, and scoring per ball falls even though pressure clusters in the high-scoring death overs. Chase win rates fall from 62% (Low) to 30–34% (High/Extreme). Extreme is slightly above High because the closeness term deliberately concentrates Extreme on genuinely live contests.', B)]
s += [img('pi_by_over.png', 130)]
s += [P('Pressure builds through each innings and peaks in the last five overs, with a visible bump when early wickets fall in the powerplay. Chases carry higher pressure than first innings in the closing overs.', SM), PageBreak()]

# ---------------- 8 Batting model
s += [P('8. Batting reliability model', H1)]
s += [P('Step 1 — context expectations', H3),
      P('For every ball faced (wides excluded), five-fold cross-fitted gradient-boosting models, split by match so a ball is never predicted by a model that saw its own match, estimate E[runs], P(dismissal), P(dot) and P(boundary). Features: competition, season, innings, over, legal balls bowled, wickets lost, <b>batting position</b>, pace/spin, Pressure Index, chase difficulty, RRR/par, recent wickets and <b>opposition</b>. Calibration is tight: predicted runs per ball 1.397 vs observed 1.400; dismissals 5.52% vs 5.46%. Batting position, phase and competition are normalised here, so a No. 7 finisher is compared with what an average batter would do in No. 7 finisher situations.'),
      P('Step 2 — per-ball value', H3),
      P('<b>Runs Added Above Expectation (RAA)</b> = (runs − E[runs]) − λ·(out − P(out)). This converts a dismissal into its true run cost in that state. Also tracked: runs above expectation, dismissal avoidance, dot avoidance, boundary rate above expectation.'),
      P('Step 3 — hierarchical shrinkage toward the player\'s own baseline', H3),
      P('θ<sub>pressure</sub> = r·x<sub>pressure</sub> + (1 − r)·(a + b·x<sub>normal</sub>),  r = n / (n + k),  k = σ²/τ²<sub>resid</sub>', MONO),
      P('Here x<sub>normal</sub> is the player\'s normal-pressure rate (itself shrunk), a and b are fitted across players, and k is estimated by match-clustered method of moments for each metric and competition. For IPL RAA, k ≈ 387 balls: a batter with 387 IPL pressure balls is weighted half on what they did under pressure and half on what their normal game predicts. This is the reliability adjustment the brief asks for. It stops a 40-ball purple patch from topping the table, and it judges pressure performance <i>relative to the player\'s ordinary level</i>.'),
      P('Step 4 — Pressure Batting Performance Score', H3)]
s += [table([['Component (pressure, shrunk, per ball)', 'Weight', 'Captures'],
             ['RAA (runs + wicket cost vs expectation)', '0.30', 'Context-adjusted runs above expectation'],
             ['Runs above expectation', '0.15', 'Scoring efficiency'],
             ['Dismissal avoidance', '0.10', 'Ability to avoid dismissals'],
             ['Dot-ball avoidance', '0.10', 'Rotating strike under squeeze'],
             ['Boundary rate above expectation', '0.05', 'Release shots'],
             ['Pressure − normal RAA', '0.10', 'Improvement over own baseline'],
             ['10th-percentile lower bound of RAA', '0.20', 'Reliability / sample size']], [70, 18, 86])]
s += [P('Components are z-scored across eligible players, combined, and min-max scaled to 0–100. The final score is the <b>mean over the 18-specification ensemble</b> (Section 11).', SM)]
s += [P('Eligibility (batting)', H3), P('≥ 100 pressure balls faced, ≥ 10 distinct matches with pressure balls, ≥ 30 <b>IPL</b> pressure balls (IPL relevance), ≥ 200 normal-pressure balls (to define a baseline). ' + f'{S3["bat"]["n_eligible"]} of {S3["bat"]["n_players_any"]} batters qualify. These thresholds were fixed before ranking and held constant across all sensitivity runs.'), PageBreak()]

# ---------------- 9 Bowling model
s += [P('9. Bowling reliability model', H1)]
s += [P('The same three steps apply, from the bowler\'s side, over every delivery bowled (wides and no-balls included):')]
s += bullets(['<b>Bowler-conceded runs</b> = runs off the bat + 1 per wide / no-ball. Byes and leg-byes are excluded. Legal deliveries exclude wides and no-balls.',
              '<b>Bowler wickets</b> = Caught, Bowled, LBW, Stumped, Hit Wicket only. Run-outs (600 events, including 49 off the 10 finalists\' bowling) are never credited.',
              '<b>Runs Saved Above Expectation (RSAA)</b> = (E[conceded] − conceded) + λ·(wicket − P(wicket)). Expectations come from cross-fitted models with the same context features, using the <b>batting side</b> and the striker\'s batting position as opposition-quality controls. Calibration: 1.388 predicted vs 1.389 observed runs per ball.',
              '<b>Phase demands.</b> Over, phase and pressure are all in the expectation model, so a death bowler is compared with the death-over norm, not with powerplay economy rates. Specialist death work is <b>explicitly rewarded</b> through a separate shrunk death-over pressure RSAA component.'])
s += [table([['Component (pressure, shrunk, per ball)', 'Weight', 'Captures'],
             ['RSAA (runs + wickets vs expectation)', '0.25', 'Runs prevented incl. wicket value'],
             ['Runs conceded below expectation', '0.15', 'Economy vs context'],
             ['Bowler wickets above expectation', '0.10', 'Wicket-taking vs expected'],
             ['Dot-ball generation above expectation', '0.10', 'Squeeze'],
             ['Boundary suppression', '0.05', 'Boundary prevention'],
             ['Pressure − normal RSAA', '0.10', 'Improvement over own baseline'],
             ['10th-percentile lower bound of RSAA', '0.15', 'Reliability / sample size'],
             ['Death-over pressure RSAA', '0.10', 'Specialist death skill']], [70, 18, 86])]
s += [P('Eligibility (bowling)', H3), P('≥ 120 pressure deliveries, ≥ 10 matches, ≥ 30 IPL pressure deliveries, ≥ 200 normal deliveries. ' + f'{S3["bowl"]["n_eligible"]} of {S3["bowl"]["n_players_any"]} bowlers qualify. For IPL RSAA, k ≈ 457 balls.'), PageBreak()]

# ---------------- 10 IPL vs T20I
s += [P('10. IPL and T20I comparison', H1)]
s += [P('Each metric is estimated separately within IPL and within T20I, each against its own context expectation (so T20I mismatches against weaker associate sides are already priced in through the opposition feature). The two estimates are then blended:'),
      P('w<sub>IPL</sub> = 0.7·e<sub>IPL</sub> / (0.7·e<sub>IPL</sub> + 0.3·e<sub>T20I</sub>),   e = n / (n + 300)', MONO),
      P('With adequate samples in both, the blend is 70:30. A player with no T20I evidence is <b>not penalised</b>: their IPL estimate stands on its own, already shrunk by its own reliability. T20I volume can never dominate automatically, because each competition\'s weight saturates at its base share. Alternative blends of 80:20 and 60:40 are part of the sensitivity grid. At a fixed threshold, changing the blend keeps 7–9 of the 10 batters and 8–10 of the 10 bowlers in the top 10.')]
s += [img('bat_ipl_t20i.png', 150), img('bowl_ipl_t20i.png', 150)]
s += [CondPageBreak(75 * mm), P('T20I-only watchlist (fails only the IPL-evidence rule; not ranked)', H3)]
wl = [['Batters', 'T20I pressure balls', 'Pressure RAA/100', 'Bowlers', 'T20I pressure balls', 'Pressure RSAA/100']]
for x, y in zip(S4['bat']['watchlist'][:6], S4['bowl']['watchlist'][:6]):
    wl.append([x['name'], int(x['n_p_T']), f1(x['v']), y['name'], int(y['n_p_T']), f1(y['v'])])
s += [table(wl, [36, 22, 24, 36, 22, 24])]
s += [P('These players have strong T20I pressure evidence but little or no IPL pressure exposure, so their transfer to IPL conditions is unproven within this dataset. They are useful scouting leads for an auction with overseas slots, not ranked selections.', SM), PageBreak()]

# ---------------- 11 Reliability & validation
s += [P('11. Statistical reliability & validation', H1)]
s += [P('11.1 Is pressure performance a repeatable skill?', H3),
      P('Splitting each player\'s matches into odd and even match IDs: raw pressure batting RAA has essentially zero split-half reliability, while normal-pressure batting RAA has 0.56 (Spearman-Brown). Pressure bowling RSAA does better (0.34), and its run-conceding component reaches 0.56. Players\' normal and pressure scoring correlate at 0.47. Conclusion: <b>most of the apparent "clutch" spread in raw batting numbers is noise</b>. A responsible ranking must borrow strength from the player\'s overall ability and only reward pressure-specific deviations that are supported by sample size. The hierarchical model does exactly that.', B)]
s += [P('11.2 Season hold-out (time-based validation)', H3)]
s += [table([['Predict 2025–26 pressure value from 2022–24 data', 'Batting wMSE ×10<super>-3</super>', 'Bowling wMSE ×10<super>-3</super>'],
             ['Raw 2022–24 pressure average', hb['weighted_mse_x1000']['raw_pressure_mean'], hw['weighted_mse_x1000']['raw_pressure_mean']],
             ['League average (predict 0)', hb['weighted_mse_x1000']['league_average(0)'], hw['weighted_mse_x1000']['league_average(0)']],
             ['Normal-pressure baseline only', hb['weighted_mse_x1000']['normal_baseline_only'], hw['weighted_mse_x1000']['normal_baseline_only']],
             ['<b>Hierarchical EB estimate (this model)</b>', hb['weighted_mse_x1000']['EB_hierarchical'], hw['weighted_mse_x1000']['EB_hierarchical']]], [90, 42, 42])]
s += [P(f'Players: {hb["n_players"]} batters, {hw["n_players"]} bowlers with ≥ 60 pressure balls in both periods. The model halves the batting error and cuts the bowling error by a third relative to raw pressure averages, and beats the league average in both disciplines. For bowling it is the best predictor tested (Spearman {hw["spearman"]["v"]}). For batting, the normal baseline alone predicts slightly better. This is reported honestly: batting pressure ratings should be read as <b>evidence of what happened</b>, appropriately regularised, rather than a strong forecast. This is why batting confidence labels are more conservative.', SM)]
s += [P('11.3 Match-level bootstrap', H3),
      P('Matches, not balls, are the unit of resampling. We drew 300 Poisson bootstrap replicates with one weight per match, shared across all players in that match. Each replicate recomputes every player\'s rating and the full ranking with the hyper-parameters held fixed. The outputs are each finalist\'s 5th–95th percentile rank interval and P(top 10).')]
s += [img('bat_bootstrap.png', 140), img('bowl_bootstrap.png', 140)]
s += [P('11.4 Robustness to model specification', H3),
      P('Eighteen specifications were run: pressure definition {main, equal-weight} × threshold {65th, 75th, 85th percentile} × IPL:T20I {60:40, 70:30, 80:20}, with the eligible set held fixed. The <b>final score is the mean score across all 18</b>, so no single arbitrary choice drives the ranking. Overlap of each specification\'s top 10 with the final top 10: batting 7–9 / 10, bowling 8–10 / 10.')]
s += [img('bat_sensitivity.png', 174), img('bowl_sensitivity.png', 174)]
s += [CondPageBreak(60 * mm), P('11.5 Confidence levels', H3),
      P('<b>High</b>: P(top 10) ≥ 60% in bootstrap, top 10 in ≥ 75% of specifications, ≥ 250 pressure balls and ≥ 25 pressure matches. <b>Medium</b>: P(top 10) ≥ 35%, top 10 in ≥ 50% of specifications, ≥ 120 pressure balls. <b>Low</b>: anything else. Low-confidence finalists are ranked because the ensemble placed them there, but they should not be read as equally proven.')]
s += [CondPageBreak(70 * mm), P('11.6 Independent verification', H3)]
chk = V['checks']
s += [table([['Check', 'Result'],
             ['Player IDs present in mapping; display names exact', 'Pass (20/20)' if chk['bat_names_exact'] and chk['bowl_names_exact'] else 'FAIL'],
             ['No duplicate player within either list', 'Pass' if chk['bat_no_duplicates'] and chk['bowl_no_duplicates'] else 'FAIL'],
             ['All finalists meet eligibility thresholds', 'Pass' if chk['bat_all_eligible'] and chk['bowl_all_eligible'] else 'FAIL'],
             ['Raw totals recomputed from CSVs by separate code = pipeline', 'Pass' if chk['bat_raw_stats_match_pipeline'] and chk['bowl_raw_stats_match_pipeline'] else 'FAIL'],
             ['Primary-spec scores reproduce on re-run', 'Pass' if chk['bat_primary_score_reproduces'] and chk['bowl_primary_score_reproduces'] else 'FAIL'],
             ['Missing matches are all abandoned (no distortion)', 'Pass' if chk['missing_matches_all_abandoned'] else 'FAIL'],
             ['Extras: byes/leg-byes excluded from bowler runs; run-outs not credited', 'Pass (recomputed independently)']], [130, 44])]
s += [PageBreak()]

# ---------------- 12 Top 10 batters
def bat_rows(t):
    rows = [['#', 'Player (ID)', 'IPL / T20I press. balls', 'Press. matches', 'Score', 'Press. RAA/100', 'Normal RAA/100', 'Δ vs normal', 'Press. SR (exp.)', 'Balls/dis.', '% matches > exp.', 'Conf.']]
    for _, r in t.iterrows():
        rows.append([int(r.final_rank), f"{r['name']} ({r.name})", f'{int(r.n_p_I)} / {int(r.n_p_T)}', int(r.m_p), f1(r.pressure_score), f1(r.press_value_per100),
                     f1(r.normal_value_per100), f'{r.delta_per100:+.1f}', f'{r.P_SR:.0f} ({r.P_exp_SR:.0f})', f1(r.P_balls_per_dis), pct(r.pct_matches_pos), r.confidence])
    return rows
s += [P('12. Top 10 batters — detailed evidence', H1)]
s += [table(bat_rows(tb), [6, 30, 17, 12, 11, 13, 13, 12, 17, 12, 13, 13])]
s += [P('RAA/100 = runs added above context expectation per 100 pressure balls, including the run cost of dismissals (posterior, shrunk). Δ = pressure minus own normal baseline. Press. SR in brackets = strike rate an average batter would be expected to achieve on the same balls.', SM)]
s += [img('bat_top10.png', 140), img('bat_press_vs_normal.png', 130), img('bat_consistency.png', 160)]
BATNOTE = {
 6396: 'The clearest finisher signal in the data. 341 IPL + 205 T20I pressure balls; strike rate 168 against 136 expected; 50% of his pressure balls come at the death. Rank 1 in 13 of 18 specifications (never worse than 4th) and P(top 10) = 92%.',
 4260: 'Middle-overs pressure specialist (61% of pressure balls in overs 7–15). Strike rate 168 vs spin under pressure, 190 in the last five overs. Positive pressure value in all 5 seasons, the most season-consistent batter in the list.',
 1699: 'Largest pressure sample in the top 3 (619 balls, 57 matches). Elite normal baseline carried into pressure states; 69% of his pressure balls come while chasing; SR 163 in difficult chases (D > 1.2).',
 2756: 'Biggest pressure-over-normal improvement in the top 10 (+11.8 RAA/100). SR 215 in the last five overs under pressure. IPL-only evidence (237 balls) keeps confidence at Medium.',
 6281: 'Ranked by the ensemble mainly because his normal-pressure baseline is the highest in the dataset (21.6 RAA/100). His own pressure record is below that baseline (Δ −9.8) and the sample is small (152 balls). Low confidence. The model is backing ability, not proven pressure output.',
 1318: 'Death-overs hitter (49% of pressure balls at the death; SR 189 in last five overs). Pressure value well above his normal baseline. <b>Retired from IPL (Nov 2025)</b>, so a ranking finding only, not an auction option.',
 143: '71% of his pressure balls came at the death; Δ +5.7 over his normal baseline. Data covers IPL 2022–24 and T20I 2022. <b>Retired after IPL 2024</b>, so a ranking finding only.',
 3125: 'Largest pressure sample in the batting top 10 (622 balls, 51 matches). Survives pressure longest of the top 10 (27 balls per dismissal). Strong in difficult chases (220 balls, SR 166) and in the last five overs (SR 183). Pressure value consistently above his normal baseline (+8.9).',
 3647: 'Middle-order anchor who keeps the rate moving: pressure SR 150 vs 142 expected, SR 181 in the last five overs, and 54% of his pressure balls while chasing. Inside the top 10 in 13 of 18 specifications.',
 37052: 'Highest pressure strike rate in the top 10 (178 vs 141 expected) and positive in 68% of his pressure matches. But only 166 pressure balls across 2 seasons, so Low confidence.',
}
for _, r in tb.iterrows():
    s += [KeepTogether([P(f"{int(r.final_rank)}. {r['name']}  <font color='#5d5c58' size=8>(ID {r.name} · {r.confidence} confidence · score {f1(r.pressure_score)} · bootstrap P(top 10) {pct(r.boot_top10)} · top 10 in {pct(r.grid_top10)} of specs)</font>", H3),
                        P(BATNOTE[r.name], B)])]
s += [PageBreak()]

# ---------------- 13 Top 10 bowlers
def bowl_rows(t):
    rows = [['#', 'Player (ID)', 'IPL / T20I press. balls', 'Press. matches', 'Score', 'Press. RSAA/100', 'Normal RSAA/100', 'Δ vs normal', 'Press. econ (exp.)', 'Press. wkts', 'Death press. balls / econ', 'Conf.']]
    for _, r in t.iterrows():
        rows.append([int(r.final_rank), f"{r['name']} ({r.name})", f'{int(r.n_p_I)} / {int(r.n_p_T)}', int(r.m_p), f1(r.pressure_score), f1(r.press_value_per100),
                     f1(r.normal_value_per100), f'{r.delta_per100:+.1f}', f'{r.P_econ:.2f} ({r.P_exp_econ:.2f})', int(r.P_wkts), f'{int(r.DEATH_legal)} / {r.DEATH_econ:.2f}', r.confidence])
    return rows
s += [P('13. Top 10 bowlers — detailed evidence', H1)]
s += [table(bowl_rows(tw), [6, 31, 17, 12, 11, 13, 13, 12, 18, 11, 17, 13])]
s += [P('RSAA/100 = runs saved above context expectation per 100 pressure deliveries, including the run value of bowler-credited wickets (posterior, shrunk). Economy in brackets = expected economy for an average bowler on the same deliveries.', SM)]
s += [img('bowl_top10.png', 140), img('bowl_press_vs_normal.png', 130), img('bowl_consistency.png', 160)]
BOWLNOTE = {
 781: 'The most robust selection in the study: rank 1 in 15 of 18 specifications (never worse than 3rd) and P(top 10) = 99%. Pressure economy 5.31 against 7.28 expected; boundary rate under pressure halves (6.2% vs 13.4% normal). Saves more runs above expectation in all 5 seasons.',
 6669: 'Biggest pressure-over-normal lift among bowlers (+19.7 RSAA/100). Defending in second innings at 4.97 economy (76 balls), and positive in 78% of pressure matches. IPL-only evidence (169 balls) keeps confidence at Medium.',
 8661: 'Specialist death bowler: 65% of pressure deliveries at the death, 259 death pressure balls at 7.92; overall pressure economy 7.64 against 9.99 expected for the same deliveries. 30 pressure wickets. High confidence.',
 2933: 'Elite in every phase. 508 pressure deliveries with economy 7.12 vs 8.58 expected and 33 wickets; 284 death pressure balls at 7.35. Top 10 in all 18 specifications.',
 830: 'New-ball and death pressure bowler (47% death, 28% powerplay). 25 wickets at 15.2 balls per wicket under pressure; defending economy 7.32. Wide bootstrap interval, so Medium confidence.',
 3644: 'Wrist-spin wicket-taker under pressure: 39 wickets, boundary rate 9.7%. First-innings pressure economy 5.95. Top 10 in 17 of 18 specifications.',
 6256: 'Mystery spin that is strongest when the game tightens: 46 pressure wickets, economy 6.94 vs 7.44 expected, and only 6.54 an over on 157 death pressure balls.',
 4722: 'Largest pressure sample in either list (872 deliveries, 82 matches) and 58 wickets. Concedes boundaries on just 10.1% of pressure balls. Dropdown note: select ID 4722 (Gujarat Titans / Afghanistan), not the Nepal player of the same name (20172).',
 360: 'Death-overs reliability (70% of pressure balls at the death, 311 balls). 35 wickets; P(top 10) = 64% in bootstrap. Medium confidence because rank varies with the pressure threshold.',
 4373: 'Left-arm cutters at the death: 347 death pressure balls at 7.85 and the highest pressure dot-ball share in the list (45.6%). Ranked 10th with Low confidence (P(top 10) = 32%).',
}
for _, r in tw.iterrows():
    s += [KeepTogether([P(f"{int(r.final_rank)}. {r['name']}  <font color='#5d5c58' size=8>(ID {r.name} · {r.confidence} confidence · score {f1(r.pressure_score)} · bootstrap P(top 10) {pct(r.boot_top10)} · top 10 in {pct(r.grid_top10)} of specs)</font>", H3),
                        P(BOWLNOTE[r.name], B)])]
s += [PageBreak()]

# ---------------- 14 RR strategy
s += [P('14. Rajasthan Royals IPL 2027 strategic implications', H1)]
s += [P('<b>Status of facts.</b> RR\'s IPL 2026 squad below is taken from rajasthanroyals.com (retained and traded players, 15 Dec 2025; auction buys, 16 Dec 2025) and cross-checked against the IPL 2026 team mapping in the supplied data. IPL 2027 retentions and auction availability had <b>not been officially published</b> as of 11 November 2026, so no retention, release or price is assumed here. Everything marked "Opinion" is strategic judgement, not a statistical finding.', CALL)]
s += [P('14.1 Data finding — where RR\'s current squad sits on the pressure scale', H3)]
rrb = BT[BT.ipl26_team.eq('Rajasthan Royals') & BT.eligible].sort_values('final_rank')
rrw = BW[BW.ipl26_team.eq('Rajasthan Royals') & BW.eligible].sort_values('final_rank')
rows = [['RR batter (IPL 2026)', 'Rank / eligible', 'Press. RAA/100', 'RR bowler (IPL 2026)', 'Rank / eligible', 'Press. RSAA/100']]
for i in range(max(len(rrb), len(rrw))):
    a = rrb.iloc[i] if i < len(rrb) else None; b_ = rrw.iloc[i] if i < len(rrw) else None
    rows.append([a['name'] if a is not None else '', f"{int(a.final_rank)} / {S3['bat']['n_eligible']}" if a is not None else '', f1(a.press_value_per100) if a is not None else '',
                 b_['name'] if b_ is not None else '', f"{int(b_.final_rank)} / {S3['bowl']['n_eligible']}" if b_ is not None else '', f1(b_.press_value_per100) if b_ is not None else ''])
s += [table(rows, [38, 22, 22, 38, 22, 22])]
s += [P('No current RR player reaches either top 20. RR\'s best eligible pressure bowler (Jofra Archer) ranks 24th of 90, and four frontline bowlers rank in the bottom third (Tushar Deshpande 62nd, Ravi Bishnoi 80th, Sam Curran 84th, Sandeep Sharma 85th). Batting pressure ratings for Dhruv Jurel and Riyan Parag sit mid-table (26th–27th of 72). Yashasvi Jaiswal and Vaibhav Sooryavanshi are ineligible: as openers they rarely bat in high-pressure states (62 and 34 pressure balls), so no pressure judgement is possible for them, positive or negative. <b>Finding:</b> the clearest data-supported gap is <b>pressure bowling, especially at the death</b>, followed by a <b>proven pressure finisher at No. 5–7</b>.', B)]
s += [P('14.2 Role fit for each finalist (Opinion, grounded in the data attributes shown)', H3)]
RRB = {
 6396: ('No. 6 finisher; pace-hitting at the death', 'Defending-score inflation in overs 16–20; chases needing 12+ an over'),
 4260: ('No. 4–5 middle-overs enforcer vs spin', 'Breaking spin squeezes in overs 7–15 when wickets have fallen'),
 1699: ('No. 3–4 chase controller', 'Difficult chases where the asking rate climbs mid-innings'),
 2756: ('No. 6–7 finisher; Indian, so no overseas slot used', 'Last-five-over acceleration when the innings is behind par'),
 6281: ('Opener; aggressive powerplay intent', 'Low-pressure tempo-setting; pressure role unproven (Low confidence)'),
 1318: ('Not available: retired from IPL (Nov 2025)', 'Shown for ranking completeness only'),
 143: ('Not available: retired after IPL 2024', 'Shown for ranking completeness only'),
 3125: ('No. 4–5 overseas wicketkeeper-finisher', 'Run chases above par; death-over hitting after a collapse'),
 3647: ('No. 3–4 Indian anchor-captain profile', 'Rebuilding after early wickets without stalling the rate'),
 37052: ('No. 6–7 Indian finisher (developing)', 'High-tempo death hitting; sample still small'),
}
RRW = {
 781: ('Overseas middle-overs spinner', 'Strangling chases in overs 7–15; boundary denial'),
 6669: ('Indian left-arm seamer, death and defending', 'Defending small totals in the final overs'),
 8661: ('Overseas death specialist', 'Closing out chases in overs 17–20'),
 2933: ('Indian all-phase spearhead', 'Any phase; death overs of tight chases'),
 830: ('Overseas new-ball and death seamer', 'Early wickets plus defending at the death'),
 3644: ('Indian wrist-spinner, middle overs', 'Taking wickets when the opposition must accelerate'),
 6256: ('Indian mystery spinner, middle and death', 'Middle-over control in chases; death-over spin option'),
 4722: ('Overseas leg-spinner and lower-order bat', 'Boundary denial plus wickets in overs 7–20'),
 360: ('Indian death and swing seamer', 'Death-over defence; new-ball swing'),
 4373: ('Overseas left-arm cutter specialist', 'Death overs on slower surfaces; dot-ball squeeze'),
}
rows = [['#', 'Batter', 'IPL 2026 team (data)', 'Ideal RR role', 'Match situations he helps win']]
for _, r in tb.iterrows():
    rows.append([int(r.final_rank), r['name'], r.ipl26_team if isinstance(r.ipl26_team, str) else '— (no IPL 2026 record)', *RRB[r.name]])
s += [table(rows, [6, 30, 34, 50, 54])]
s += [Spacer(1, 6)]
rows = [['#', 'Bowler', 'IPL 2026 team (data)', 'Ideal RR role', 'Match situations he helps win']]
for _, r in tw.iterrows():
    rows.append([int(r.final_rank), r['name'], r.ipl26_team, *RRW[r.name]])
s += [table(rows, [6, 30, 34, 50, 54])]
s += [P('14.3 Auction priorities (Opinion)', H3)]
s += bullets(['<b>Priority 1 — a High-confidence death bowler.</b> Pathirana and Bumrah are the two High-confidence death specialists. Mohsin Khan (Indian, Medium) and Bhuvneshwar Kumar (Indian, Medium) are the Indian-slot alternatives with strong death and defending numbers. This addresses RR\'s largest measured gap.',
              '<b>Priority 2 — a middle-overs pressure spinner.</b> Narine is the single most robust finding in the study. Kuldeep Yadav and Varun Chakravarthy offer Indian-slot equivalents with 39 and 46 pressure wickets.',
              '<b>Priority 3 — a pressure finisher at No. 5–7.</b> Tim David and Klaasen are High confidence. Shashank Singh is the strongest Indian finisher option and costs no overseas slot.',
              '<b>Actionable alternates for unavailable finalists</b> (next eligible by ensemble score): batting #11 Namboori Tilak Varma (High-volume: 776 pressure balls), #12 Rajat Patidar, #13 Tristan Stubbs. Bowling depth: #11 Noor Ahmad, #12 Kagiso Rabada.',
              '<b>Availability gate.</b> Every name above is currently contracted to another franchise per the data\'s IPL 2026 mapping. Bids depend on the official retention lists, which were not available at the time of writing.'])
s += [PageBreak()]

# ---------------- 15 Findings
s += [P('15. Key findings & recommendations', H1)]
s += bullets(['<b>Define pressure from the pre-ball state, calibrated by competition.</b> A composite of chase difficulty, closeness, resources, stage, collapse and squeeze separates real danger states (dismissal rates +38%) from ordinary play.',
              '<b>Judge players against context, and shrink toward their own baseline.</b> Raw pressure numbers are mostly noise for batters. The hierarchical model cuts out-of-sample error by a third to a half.',
              '<b>The bowling list is more trustworthy than the batting list.</b> Bowling pressure ratings show repeatable signal (split-half 0.34; hold-out Spearman 0.21). Batting pressure ratings mostly reflect overall ability plus a modest, shrunk pressure adjustment.',
              '<b>Most robust selections:</b> Sunil Narine, Jasprit Bumrah, Matheesha Pathirana (bowling); Tim David, Heinrich Klaasen, Suryakumar Yadav (batting). All are High confidence and top 10 in every specification.',
              '<b>Treat with caution:</b> Abhishek Sharma, Naman Dhir and Mustafizur Rahman (Low confidence). Mohsin Khan and Shashank Singh rest on IPL-only samples under 250 balls.',
              '<b>For RR:</b> the data points first to pressure death bowling, then to a pressure finisher.'])

# ---------------- 16 Limitations
s += [P('16. Limitations & future improvements', H1)]
s += bullets(['Extra-run amounts (multi-run wides, byes) are not recorded. Team totals and chase targets carry ±3 runs of noise (75% of matches), and bowler-conceded runs slightly understate multi-run wides.',
              'Openers rarely face high-pressure balls by construction, so pressure ratings are not available for many top-order players. This is a property of the definition, not a judgement on them.',
              'Pressure Index weights are judgement-based. Mitigated by an equal-weight alternative and the 18-spec ensemble, but not learned from outcomes.',
              'Batting pressure skill has weak out-of-sample predictability. Rankings describe 2022–26 evidence and should be combined with scouting.',
              'Ball-tracking fields (speed, line, length) are sparse or zero-filled and were not used. Fielding, wicket-keeping and captaincy are out of scope.',
              'Non-IPL T20 events (30 matches) are excluded; franchise leagues outside the dataset (SA20, ILT20, CPL, BBL) are not available.',
              'Future work: learn component weights by maximising leverage (win-probability swing per ball); add bowler–batter matchup models; a full Bayesian hierarchical fit (Stan) with season-level random effects.'])
s += [PageBreak()]

# ---------------- 17 Appendix
s += [P('17. Technical appendix — formulas, metrics, assumptions', H1)]
s += [P('A. Notation & core definitions', H3)]
s += [table([['Term', 'Definition'],
             ['Legal ball', 'extras_type not in {wide, Overstep, other}'],
             ['Ball faced (batter)', 'All deliveries except wides'],
             ['Team runs (state only)', 'runs + 1·[wide/no-ball/bye/leg-bye/penalty] + extras_2_runs'],
             ['Bowler conceded', 'runs + 1·[wide or no-ball]'],
             ['Batter dismissal', 'is_wicket ∧ dismissed_player_id = striker_id ∧ type ≠ Retire Out'],
             ['Bowler wicket', 'is_wicket ∧ type ∈ {Caught, Bowled, LBW, Stump, Hit Wicket}'],
             ['Balls available N', 'Revised overs field (stored in balls) else 120'],
             ['Target', 'revised_target if present, else 1st-innings total + 1'],
             ['Pre-ball state', 'Cumulative sums excluding the current delivery'],
             ['λ (wicket run value)', 'E<sub>rem</sub>(b, w) − E<sub>rem</sub>(b, w+1); 0 at 10 wickets'],
             ['RAA (batting)', '(runs − E[runs]) − λ·(out − P(out))'],
             ['RSAA (bowling)', '(E[conc] − conc) + λ·(wkt − P(wkt))']], [45, 129])]
s += [P('B. Empirical-Bayes estimation', H3),
      P('For metric m, competition c, player i: x<sub>p</sub> = pressure mean, n<sub>p</sub> balls; x<sub>n</sub> = normal mean shrunk toward the regulars\' mean with k<sub>n</sub> = σ²<sub>n</sub>/τ²<sub>n</sub> (moments over players with ≥ 300 normal balls). Prior: a + b·x<sub>n</sub> by weighted least squares (weights min(n<sub>p</sub>, 400), players with n<sub>p</sub> ≥ 30). τ²<sub>resid</sub> = weighted residual variance − mean sampling variance. Sampling variance uses a match-clustered estimator Σ<sub>m</sub>(s<sub>m</sub> − n<sub>m</sub>x̄)² / n². Posterior SD = (n/σ² + 1/τ²)<super>−1/2</super>. Lower bound = θ − 1.2816·SD (blended across competitions).', B)]
hp = S3['bat']['hyper']; hq = S3['bowl']['hyper']
s += [table([['Hyper-parameter (RAA / RSAA)', 'Bat IPL', 'Bat T20I', 'Bowl IPL', 'Bowl T20I'],
             ['k (balls; shrinkage strength)', f1(hp['IPL|v']['k']), f1(hp['T20I|v']['k']), f1(hq['IPL|v']['k']), f1(hq['T20I|v']['k'])],
             ['b (slope on own normal baseline)', f2(hp['IPL|v']['b']), f2(hp['T20I|v']['b']), f2(hq['IPL|v']['b']), f2(hq['T20I|v']['b'])],
             ['k<sub>n</sub> (normal baseline shrinkage)', f1(hp['IPL|v']['k_n']), f1(hp['T20I|v']['k_n']), f1(hq['IPL|v']['k_n']), f1(hq['T20I|v']['k_n'])]], [70, 26, 26, 26, 26])]
s += [P('C. Expectation models', H3),
      P('sklearn HistGradientBoosting (250 iterations, learning rate 0.06, 31 leaves, min 200 samples per leaf), 5-fold GroupKFold by match_id (out-of-fold predictions only). Opposition team as a native categorical. Resource model: monotone constraints (+ balls left, − wickets).', B)]
s += [P('D. Reproducibility', H3),
      P('Run in order: s1_prepare.py → s2_expect.py → s3_score.py → s4_tables.py → s5_charts.py → s6_verify.py → s7_report.py. Random seeds are fixed (bootstrap seed 2027; model seeds 0/1). The supporting dataset (all players, IDs, scores, samples, confidence, eligibility, ranks and metrics) is supplied as CSV with a data dictionary.', B)]
s += [P('E. Final dropdown selections (exact names from competition_team_player_mapping.csv)', H3)]
rows = [['Rank', 'Batter', 'ID', 'Bowler', 'ID']]
for i in range(10): rows.append([i + 1, tb.iloc[i]['name'], tb.index[i], tw.iloc[i]['name'], tw.index[i]])
s += [table(rows, [14, 52, 20, 58, 20])]
doc.build(s)
print('ok')
