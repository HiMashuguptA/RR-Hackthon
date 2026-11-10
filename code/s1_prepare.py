"""Stage 1 — load, clean, build pre-delivery match state and the Pressure Index.
SupeRR Selector S2 R1. Reproducible: python s1_prepare.py  (reads ../data, writes deliveries.parquet)
"""
import pandas as pd, numpy as np, json
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression

D = '/home/claude/data/'; W = '/home/claude/work/'
b = pd.read_csv(D+'ball_by_ball.csv', low_memory=False)
m = pd.read_csv(D+'matches.csv'); c = pd.read_csv(D+'competitions.csv')
audit = {}
audit['rows'] = {f: int(len(pd.read_csv(D+f, low_memory=False))) for f in
                 ['ball_by_ball.csv','matches.csv','competitions.csv','teams.csv','playing_eleven.csv','competition_team_player_mapping.csv']}

m = m.merge(c, on='comp_id', how='left')
m['comp_group'] = np.where(m.comp_name.str.startswith('IPL'), 'IPL',
                   np.where(m.match_format.eq('T20I'), 'T20I', 'OtherT20'))
m['season'] = pd.to_datetime(m.match_date).dt.year
audit['matches_without_bbb'] = m.loc[~m.match_id.isin(b.match_id), ['match_id','comp_name','match_date','result']].to_dict('records')
audit['super_over_rows'] = int((b.innings > 2).sum()); audit['super_over_matches'] = sorted(b.loc[b.innings>2,'match_id'].unique().tolist())

b = b[b.innings.isin([1, 2])].merge(m[['match_id','comp_id','comp_name','comp_group','season','first_inn_revised_overs',
                                        'second_inn_revised_overs','revised_target','win_team_id','result']], on='match_id', how='left')
audit['rows_by_group'] = b.groupby('comp_group').size().to_dict()
audit['matches_by_group'] = b.groupby('comp_group').match_id.nunique().to_dict()
b = b[b.comp_group.isin(['IPL','T20I'])].copy()   # non-IPL T20 (Emerging/Rising Stars) excluded from core

# ---- field decoding (validated in audit) ----
b['et'] = b.extras_type.fillna('none')
b['is_wide'] = b.et.eq('wide'); b['is_nb'] = b.et.isin(['Overstep','other'])
b['is_bye'] = b.et.isin(['byes','legbyes'])
b['legal'] = ~(b.is_wide | b.is_nb)
b['bat_runs'] = b.runs                               # 'runs' = runs off the bat only (0 on every wide/bye/leg-bye row)
b['boundary'] = b.is_four | b.is_six                 # flags trusted; 23 rows of 4/6 off the bat w/o flag = all-run/overthrow
# Team-run approximation: extra amounts are not recorded -> 1 run per wide/no-ball/bye/leg-bye (+extras_2_runs)
b['team_runs'] = b.bat_runs + (b.is_wide|b.is_nb|b.is_bye|b.et.eq('Penalty')).astype(int) + b.extras_2_runs
# bowler-conceded: bat runs + 1 per wide/no-ball penalty; byes & leg-byes excluded
b['bowl_conc'] = b.bat_runs + (b.is_wide|b.is_nb).astype(int)
BOWLER_WKTS = {'Caught','Bowled','LBW','Stump','Hit Wicket'}
b['bowler_wkt'] = b.is_wicket & b.dismissal_type.isin(BOWLER_WKTS)
b['team_wkt'] = b.is_wicket & ~b.dismissal_type.eq('Retire Out')
b['striker_out'] = b.is_wicket & (b.dismissed_player_id == b.striker_id) & ~b.dismissal_type.eq('Retire Out')
b['faced'] = ~b.is_wide                               # balls faced by striker (no-balls count)

b = b.sort_values(['match_id','innings','innings_ball_num']).reset_index(drop=True)
g = b.groupby(['match_id','innings'], sort=False)
b['R_pre'] = g.team_runs.cumsum() - b.team_runs
b['W_pre'] = g.team_wkt.cumsum() - b.team_wkt.astype(int)
b['L_pre'] = g.legal.cumsum() - b.legal.astype(int)
# balls available (revised overs are stored in balls)
b['N'] = np.where(b.innings.eq(1), b.first_inn_revised_overs, b.second_inn_revised_overs)
b['N'] = b.N.fillna(120).clip(upper=120)
b['b_left'] = (b.N - b.L_pre).clip(lower=1)

# recent wickets (last 18 legal balls) and team dots (last 12 legal balls), strictly pre-delivery
rw = np.zeros(len(b)); rd = np.zeros(len(b))
for _, idx in g.indices.items():
    L = b.L_pre.values[idx]; wk = b.team_wkt.values[idx].astype(int)
    dot = ((b.team_runs.values[idx] == 0) & b.legal.values[idx]).astype(int)
    cw = np.concatenate([[0], np.cumsum(wk)]); cd = np.concatenate([[0], np.cumsum(dot)])
    # position of first delivery with L_pre >= L-18
    pos18 = np.searchsorted(L, L - 18, side='left'); pos12 = np.searchsorted(L, L - 12, side='left')
    ar = np.arange(len(idx))
    rw[idx] = cw[ar] - cw[pos18]; rd[idx] = cd[ar] - cd[pos12]
b['recent_wk'] = rw; b['recent_dots'] = rd

# innings totals (approx) and targets
tot = b.groupby(['match_id','innings']).team_runs.sum().unstack()
b['inn1_total'] = b.match_id.map(tot[1])
b['target'] = np.where(b.revised_target.notna(), b.revised_target, b.inn1_total + 1)
b['need'] = (b.target - b.R_pre).clip(lower=1)

# ---- resource model E_rem(b_left, wickets, group, season), monotone GBM on full 1st innings ----
fi = b[(b.innings == 1) & (b.N == 120)].copy()
fi['rem'] = fi.match_id.map(tot[1]) - fi.R_pre
fi['ipl'] = fi.comp_group.eq('IPL').astype(int)
X = fi[['b_left','W_pre','ipl','season']].values
res_model = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, monotonic_cst=[1,-1,0,0], random_state=0).fit(X, fi.rem)
def E_rem(bl, w, ipl, season):
    out = res_model.predict(np.c_[bl, np.minimum(w, 9), ipl, season]); return np.where(w >= 10, 0, np.maximum(out, 0))
b['ipl'] = b.comp_group.eq('IPL').astype(int)
b['E_rem'] = E_rem(b.b_left, b.W_pre, b.ipl, b.season)
b['E_rem_w1'] = E_rem(b.b_left, b.W_pre + 1, b.ipl, b.season)
b['wkt_cost'] = (b.E_rem - b.E_rem_w1).clip(lower=0)     # context run value of a wicket
par = fi.groupby(['comp_group','season']).apply(lambda d: d.groupby('match_id').rem.first().mean()).rename('par_total')
b = b.merge(par.reset_index(), on=['comp_group','season'], how='left')
b['par_rr'] = b.par_total / 20
audit['par_first_innings_total'] = {f'{k[0]} {k[1]}': round(v, 1) for k, v in par.items()}
expW = fi.groupby(['comp_group','L_pre']).W_pre.mean().rename('E_W').reset_index()
b = b.merge(expW, on=['comp_group','L_pre'], how='left'); b['E_W'] = b.E_W.fillna(b.W_pre)

# ---- win-probability model for chases (pre-delivery state only) ----
sig = lambda x: 1 / (1 + np.exp(-x))
inn2 = b.innings.eq(2)
b['D'] = b.need / np.maximum(b.E_rem, 1)
b['RRR'] = 6 * b.need / b.b_left
feat = lambda d: np.c_[np.log(d.D.clip(0.05, 20)), d.b_left / d.N, d.W_pre, np.log(d.RRR.clip(0.5, 72) / d.par_rr)]
s2 = b[inn2 & b.win_team_id.notna()].copy()
s2 = s2[~s2.result.str.contains('Tie|tie|No Result|Abandon', na=False)]
y = (s2.win_team_id == s2.batting_team_id).astype(int)
wp = LogisticRegression(C=10, max_iter=2000).fit(feat(s2), y)
b['WP'] = np.nan
b.loc[inn2, 'WP'] = wp.predict_proba(feat(b[inn2]))[:, 1]
from sklearn.metrics import roc_auc_score, brier_score_loss
pp = wp.predict_proba(feat(s2))[:, 1]
audit['wp_model'] = {'auc': round(roc_auc_score(y, pp), 3), 'brier': round(brier_score_loss(y, pp), 3), 'n': int(len(s2)),
                     'coef': dict(zip(['ln D','frac balls left','wickets lost','ln RRR/par'], np.round(wp.coef_[0], 3).tolist()))}

# ---- Pressure Index components (all in [0,1]) ----
b['s_stage'] = 0.5 * (b.L_pre / b.N) + 0.5 * (b.b_left <= 30)
b['s_recent'] = np.minimum(b.recent_wk, 3) / 3
b['s_squeeze'] = np.minimum(b.recent_dots / 8, 1)
b['s_wkt'] = b.W_pre / 10
# second innings
b['s_diff'] = sig(4 * np.log(b.D.clip(0.05, 20)))
b['s_rrr'] = sig(4 * np.log((b.RRR / b.par_rr).clip(0.05, 20)))
b['s_close'] = 4 * b.WP * (1 - b.WP)
# first innings
b['proj'] = b.R_pre + b.E_rem
b['s_short'] = sig(8 * (b.par_total - b.proj) / b.par_total)
b['s_wex'] = sig((b.W_pre - b.E_W) / 1.5)

WEIGHTS = {
 'main': {1: dict(s_short=.30, s_wex=.15, s_wkt=.10, s_stage=.20, s_recent=.15, s_squeeze=.10),
          2: dict(s_diff=.25, s_rrr=.10, s_wkt=.15, s_stage=.15, s_recent=.10, s_squeeze=.05, s_close=.20)},
 'alt':  {1: dict(s_short=1/6, s_wex=1/6, s_wkt=1/6, s_stage=1/6, s_recent=1/6, s_squeeze=1/6),
          2: dict(s_diff=1/7, s_rrr=1/7, s_wkt=1/7, s_stage=1/7, s_recent=1/7, s_squeeze=1/7, s_close=1/7)},
}
for spec, wt in WEIGHTS.items():
    raw = np.zeros(len(b))
    for inn in (1, 2):
        mask = b.innings.eq(inn).values
        r = sum(b.loc[mask, k].values * v for k, v in wt[inn].items())
        if inn == 2 and spec == 'main':      # 'contest alive' factor: dead chases are not pressure
            r = r * (0.5 + 0.5 * np.minimum(1, b.loc[mask, 's_close'].values / 0.36))
        raw[mask] = r
    b[f'raw_{spec}'] = raw
    b[f'PI_{spec}'] = b.groupby(['comp_group','innings'])[f'raw_{spec}'].rank(pct=True) * 100
b['PI'] = b.PI_main
b['pcat'] = pd.cut(b.PI, [-1, 50, 75, 90, 101], labels=['Low','Medium','High','Extreme'])
b['phase'] = pd.cut(b.overid, [0, 6, 15, 20], labels=['Powerplay','Middle','Death'])
b['last5'] = b.b_left <= 30

# validation of the index: outcome rates by category
val = b[b.faced].groupby('pcat', observed=True).agg(balls=('faced','size'), dismissal_pct=('striker_out','mean'),
                                     dot_pct=('bat_runs', lambda s: (s == 0).mean()), rpb=('bat_runs','mean'))
audit['pi_validation'] = val.round(4).reset_index().to_dict('records')
ov = b[inn2 & b.legal & (b.L_pre % 6 == 0) & b.win_team_id.notna()].copy()
ov['chase_won'] = ov.win_team_id == ov.batting_team_id
audit['chase_win_by_cat'] = ov.groupby('pcat', observed=True).chase_won.mean().round(3).to_dict()
audit['pi_spec_corr'] = round(b[['PI_main','PI_alt']].corr(method='spearman').iloc[0,1], 3)

keep = ['match_id','comp_id','comp_name','comp_group','season','innings','overid','over_ball_num','innings_ball_num','batting_team_id',
 'bowling_team_id','striker_id','striker_name','bowler_id','bowler_name','batting_order','pace_or_spin','bowling_type','bat_runs','boundary',
 'is_four','is_six','is_wide','is_nb','is_bye','legal','faced','bowl_conc','bowler_wkt','striker_out','team_wkt','R_pre','W_pre','L_pre','N','b_left',
 'need','D','RRR','WP','E_rem','wkt_cost','par_rr','recent_wk','recent_dots','PI_main','PI_alt','PI','pcat','phase','last5','win_team_id',
 's_diff','s_rrr','s_close','s_short','s_wex','s_wkt','s_stage','s_recent','s_squeeze']
b[keep].to_pickle(W+'deliveries.pkl')
json.dump(audit, open(W+'audit_stage1.json','w'), indent=1, default=str)
print(json.dumps(audit, indent=1, default=str)[:6000])
