# SupeRR Selector Season 2 — Round 1: Most Reliable Players Under Pressure

**Live dashboard:** https://rr-superr-selector-dashboard.vercel.app

Rajasthan Royals × Unstop. Rankings of the 10 most reliable batters and bowlers under pressure, computed from the supplied IPL & T20I ball-by-ball data (2022–2026; 837 matches, 193,988 deliveries).

| Rank | Batter | Bowler |
|---|---|---|
| 1 | Tim David | Sunil Narine |
| 2 | Heinrich Klaasen | Mohsin Khan |
| 3 | Suryakumar Yadav | Matheesha Pathirana |
| 4 | Shashank Singh | Jasprit Bumrah |
| 5 | Abhishek Sharma | Josh Hazlewood |
| 6 | Andre Russell | Kuldeep Yadav |
| 7 | Dinesh Karthik | Varun Chakravarthy |
| 8 | Nicholas Pooran | Rashid Khan |
| 9 | Shreyas Iyer | Bhuvneshwar Kumar |
| 10 | Naman Dhir | Mustafizur Rahman |

## Method in one paragraph
Every delivery gets a **Pressure Index (0–100)** from the pre-ball match state only: chase difficulty against expected remaining resources, required rate vs competition par, win-probability closeness, wickets, stage, recent collapse and dot-ball squeeze. Context models give the expected outcome of an average player on each ball. Players are rated on runs added or saved above that expectation, including the run cost of wickets. Ratings use **hierarchical empirical-Bayes shrinkage toward each player's own normal baseline**, a 70:30 IPL:T20I blend, an **18-specification robustness ensemble** and a **300-replicate match-level bootstrap** for confidence levels.

## Contents
- `index.html` — interactive dashboard (self-contained, no external dependencies)
- `report/` — methodology report (PDF) and slide deck (PPTX)
- `data/` — full ranking dataset for every analysed player, plus a data dictionary
- `code/` — reproducible pipeline (`s1_prepare.py` … `s10_dash_data.py`), see `code/README.md`
- `charts/` — figures used in the report

The original competition data pack is not redistributed here.
