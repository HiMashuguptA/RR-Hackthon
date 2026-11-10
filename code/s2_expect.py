"""Stage 2 — context expectation models (5-fold cross-fitted by match) for batting and bowling outcomes.
Expected values = what an average player would produce in the identical pre-delivery context
(competition, season, innings, over, wickets, batting position, pace/spin, opponent, pressure state)."""
import pandas as pd, numpy as np, json
from sklearn.ensemble import HistGradientBoostingRegressor as HGR, HistGradientBoostingClassifier as HGC
from sklearn.model_selection import GroupKFold
W = '/home/claude/work/'
b = pd.read_pickle(W+'deliveries.pkl')
b['spin'] = b.pace_or_spin.eq('Spin').astype(int)
teams = pd.Index(sorted(set(b.batting_team_id) | set(b.bowling_team_id)))
b['opp_bowl'] = teams.get_indexer(b.bowling_team_id); b['opp_bat'] = teams.get_indexer(b.batting_team_id)
b['Dx'] = np.where(b.innings.eq(2), np.log(b.D.clip(.05, 20)), np.nan)
b['RRx'] = np.where(b.innings.eq(2), np.log((b.RRR / b.par_rr).clip(.05, 20)), np.nan)
base = ['ipl','season','innings','overid','L_pre','W_pre','batting_order','spin','PI','Dx','RRx','recent_wk']
b['ipl'] = b.comp_group.eq('IPL').astype(int)
print('teams', len(teams))

def crossfit(df, feats, cat, target, clf):
    pred = np.zeros(len(df)); X = df[feats].values; y = df[target].values
    catmask = [f in cat for f in feats]
    for tr, te in GroupKFold(5).split(X, y, df.match_id.values):
        mdl = (HGC if clf else HGR)(max_iter=250, learning_rate=0.06, max_leaf_nodes=31, min_samples_leaf=200,
                                     categorical_features=catmask, random_state=1)
        mdl.fit(X[tr], y[tr])
        pred[te] = mdl.predict_proba(X[te])[:, 1] if clf else mdl.predict(X[te])
    return pred

# ---- batting (balls faced) ----
bt = b[b.faced].copy()
bt['isdot'] = (bt.bat_runs == 0).astype(int); bt['out'] = bt.striker_out.astype(int); bt['bd'] = bt.boundary.astype(int)
fb = base + ['opp_bowl']
bt['E_runs'] = crossfit(bt, fb, ['opp_bowl'], 'bat_runs', False)
bt['P_out'] = crossfit(bt, fb, ['opp_bowl'], 'out', True)
bt['P_dot'] = crossfit(bt, fb, ['opp_bowl'], 'isdot', True)
bt['P_bd'] = crossfit(bt, fb, ['opp_bowl'], 'bd', True)
bt['v'] = (bt.bat_runs - bt.E_runs) - bt.wkt_cost * (bt.out - bt.P_out)   # runs added above expectation (RAA)
bt['dot_ae'] = bt.P_dot - bt.isdot; bt['out_ae'] = bt.P_out - bt.out; bt['bd_ae'] = bt.bd - bt.P_bd
bt.to_pickle(W+'bat_balls.pkl')

# ---- bowling (all deliveries) ----
bw = b.copy()
bw['isdot'] = (bw.legal & (bw.bowl_conc == 0)).astype(int); bw['wk'] = bw.bowler_wkt.astype(int); bw['bd'] = bw.boundary.astype(int)
fw = base + ['opp_bat']
bw['E_conc'] = crossfit(bw, fw, ['opp_bat'], 'bowl_conc', False)
bw['P_wk'] = crossfit(bw, fw, ['opp_bat'], 'wk', True)
bw['P_dot'] = crossfit(bw, fw, ['opp_bat'], 'isdot', True)
bw['P_bd'] = crossfit(bw, fw, ['opp_bat'], 'bd', True)
bw['v'] = (bw.E_conc - bw.bowl_conc) + bw.wkt_cost * (bw.wk - bw.P_wk)    # runs saved above expectation (RSAA)
bw['dot_ae'] = bw.isdot - bw.P_dot; bw['bd_ae'] = bw.P_bd - bw.bd; bw['wk_ae'] = bw.wk - bw.P_wk
bw.to_pickle(W+'bowl_balls.pkl')

cal = {'bat': {'runs_obs': bt.bat_runs.mean(), 'runs_exp': bt.E_runs.mean(), 'out_obs': bt.out.mean(), 'out_exp': bt.P_out.mean()},
       'bowl': {'conc_obs': bw.bowl_conc.mean(), 'conc_exp': bw.E_conc.mean(), 'wk_obs': bw.wk.mean(), 'wk_exp': bw.P_wk.mean()},
       'mean_wkt_cost_by_phase': bt.groupby('phase', observed=True).wkt_cost.mean().round(2).to_dict()}
json.dump(cal, open(W+'calib.json','w'), indent=1, default=float); print(cal)
