# SupeRR Selector S2 R1 — reproducible pipeline

Requirements: Python 3.10+ with pandas, numpy, scikit-learn (>=1.4), matplotlib, reportlab, Pillow; Node with pptxgenjs (deck only).
Put the data-pack CSVs in a folder and edit the `D`/`W` path constants at the top of each script.

Run in order:
1. `s1_prepare.py`  – audit, field decoding, pre-ball match state, resource curve, win-probability model, Pressure Index
2. `s2_expect.py`   – cross-fitted context expectation models; per-ball RAA / RSAA
3. `s3_score.py`    – hierarchical empirical-Bayes ratings, 18-spec ensemble, match bootstrap (seed 2027), season hold-out
4. `s4_tables.py`   – descriptive splits, confidence levels, T20I-only watchlist
5. `s5_charts.py`   – figures
6. `s6_verify.py`   – independent recomputation from raw CSVs + ID/name checks
7. `s7_report.py`   – PDF report;  `s8_deck.js` – PPTX deck;  `s9_export.py` – ranking dataset CSVs

Runtime: ~5 minutes on 2 CPU cores.
