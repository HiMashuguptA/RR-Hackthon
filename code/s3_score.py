"""Stage 3 — hierarchical empirical-Bayes player scoring.
For each player, competition group (IPL/T20I) and metric m (per-ball value above context expectation):
   x_p = observed pressure rate, x_n = normal-pressure rate (shrunk to league average)
   prior_i = a + b * x_n_i            (fitted across players: pressure ability predicted by own baseline)
   theta_i = r_i * x_p + (1 - r_i) * prior_i,   r_i = n_p / (n_p + k),  k = sigma2 / tau2_resid
IPL/T20I blend: weights w and (1-w) scaled by evidence e = n/(n+300); single-competition players are not penalised.
Composite = weighted z-scores of the component posteriors; final score = mean over an 18-spec ensemble
(pressure spec {main, alt} x threshold {65,75,85} x IPL weight {0.6,0.7,0.8}); eligibility fixed by primary spec.
Reliability: match-level Poisson bootstrap (shared match weights), season hold-out, grid robustness."""
import pandas as pd, numpy as np, json, itertools
W = '/home/claude/work/'
rng = np.random.default_rng(2027)
bt = pd.read_pickle(W+'bat_balls.pkl'); bw = pd.read_pickle(W+'bowl_balls.pkl')
mp = pd.read_csv('/home/claude/data/competition_team_player_mapping.csv')
names = mp.drop_duplicates('player_id').set_index('player_id').player_name
bt['pid'] = bt.striker_id; bw['pid'] = bw.bowler_id
bt['runs_ae'] = bt.bat_runs - bt.E_runs
bw['conc_ae'] = bw.E_conc - bw.bowl_conc
bw['death'] = bw.phase.eq('Death')

ROLE = {
 'bat': dict(df=bt, metrics=['v', 'runs_ae', 'out_ae', 'dot_ae', 'bd_ae'],
             comps={'v': .30, 'runs_ae': .15, 'out_ae': .10, 'dot_ae': .10, 'bd_ae': .05, 'delta': .10, 'lb': .20},
             elig=dict(p_balls=100, p_matches=10, ipl_p_balls=30, n_balls=200)),
 'bowl': dict(df=bw, metrics=['v', 'conc_ae', 'wk_ae', 'dot_ae', 'bd_ae'],
              comps={'v': .25, 'conc_ae': .15, 'wk_ae': .10, 'dot_ae': .10, 'bd_ae': .05, 'delta': .10, 'lb': .15, 'death_v': .10},
              elig=dict(p_balls=120, p_matches=10, ipl_p_balls=30, n_balls=200)),
}
EVID_K = 300.0

def build_pm(role, pi='PI_main', thr=75, seasons=None):
    cfg = ROLE[role]; df = cfg['df']
    if seasons is not None: df = df[df.season.isin(seasons)]
    d = df[['pid', 'comp_group', 'match_id', 'season'] + cfg['metrics']].copy()
    d['pr'] = (df[pi] >= thr).values
    if role == 'bowl': d['dp'] = (d.pr & df.death).values
    agg = {}
    for flag, tag in ((True, 'p'), (False, 'n')):
        s = d[d.pr == flag].groupby(['pid', 'comp_group', 'match_id', 'season'])
        a = s[cfg['metrics']].sum().add_suffix('_' + tag); a['n_' + tag] = s.size(); agg[tag] = a
    pm = agg['p'].join(agg['n'], how='outer')
    if role == 'bowl':
        s = d[d.dp].groupby(['pid', 'comp_group', 'match_id', 'season']).v
        pm = pm.join(s.sum().rename('dv_p')).join(s.size().rename('n_dp'))
    return pm.fillna(0).reset_index()

def clustered_var(pm, col, ncol, wt):
    """per-player clustered variance-of-mean pieces; returns per-ball sigma2_eff (median) and x."""
    g = pm.assign(s=pm[col] * wt, n=pm[ncol] * wt).groupby('pid')[['s', 'n']].sum()
    g = g[g.n > 0]; x = g.s / g.n
    t = pm[pm.pid.isin(g.index)]
    e2 = ((t[col] - t[ncol] * t.pid.map(x)) ** 2 * wt[t.index]).groupby(t.pid).sum()
    return x, g.n, e2 / g.n ** 2

def eb_group(pm, col, wt, hp=None):
    """EB for one competition group and one metric. hp = fixed hyper-parameters (for bootstrap)."""
    xn, nn, _ = clustered_var(pm, col + '_n', 'n_n', wt)
    xp, np_, vm = clustered_var(pm, col + '_p', 'n_p', wt)
    if hp is None:
        # normal-baseline shrinkage (to 0 = league-average context expectation)
        ok = nn >= 300; vn = clustered_var(pm, col + '_n', 'n_n', wt)[2]
        mu_n = np.average(xn[ok], weights=nn[ok])
        tau_n = max(np.average((xn[ok] - mu_n) ** 2, weights=nn[ok]) - np.average(vn[ok], weights=nn[ok]), 1e-8)
        sig_n = (vn[ok] * nn[ok]).median(); k_n = sig_n / tau_n
        xns = mu_n + (xn - mu_n) * nn / (nn + k_n)
        J = pd.DataFrame({'xp': xp, 'np': np_}).join(xns.rename('xns'), how='inner'); J = J[J.np >= 30]
        wls = np.minimum(J.np, 400)
        X = np.c_[np.ones(len(J)), J.xns]; beta = np.linalg.lstsq(X * np.sqrt(wls.values)[:, None], J.xp * np.sqrt(wls), rcond=None)[0]
        res = J.xp - X @ beta
        sig2 = (vm.reindex(J.index) * J.np).median()
        tau2 = max(np.average(res ** 2, weights=wls) - np.average(sig2 / J.np, weights=wls), sig2 / 5000)
        hp = dict(mu_n=mu_n, k_n=k_n, a=beta[0], b=beta[1], sig2=sig2, tau2=tau2, k=sig2 / tau2)
    xns = hp['mu_n'] + (xn - hp['mu_n']) * nn / (nn + hp['k_n'])
    idx = xns.index.union(xp.index)
    out = pd.DataFrame(index=idx)
    out['xn'] = xns.reindex(idx).fillna(0); out['nn'] = nn.reindex(idx).fillna(0)
    out['xp'] = xp.reindex(idx).fillna(0); out['np'] = np_.reindex(idx).fillna(0)
    out['prior'] = hp['a'] + hp['b'] * out.xn
    out['r'] = out.np / (out.np + hp['k'])
    out['theta'] = out.r * out.xp + (1 - out.r) * out.prior
    out['psd'] = np.sqrt(1 / (out.np / hp['sig2'] + 1 / hp['tau2']))
    return out, hp

def shrink0(pm, col, ncol, wt, hp=None):
    x, n, vm = clustered_var(pm, col, ncol, wt)
    if hp is None:
        ok = n >= 60
        tau = max(np.average((x[ok] - np.average(x[ok], weights=n[ok])) ** 2, weights=n[ok]) - np.average(vm[ok], weights=n[ok]), 1e-8); sig = (vm[ok] * n[ok]).median(); hp = dict(k=sig / tau)
    return (x * n / (n + hp['k'])), n, hp

def score(role, pm, w_ipl=0.7, wt=None, hps=None, elig_ids=None):
    cfg = ROLE[role]
    wt = pd.Series(1.0, index=pm.index) if wt is None else wt
    new_hps = {}; res = {}
    ev = {}
    for cg in ('IPL', 'T20I'):
        sub = pm[pm.comp_group == cg]; wsub = wt[sub.index]
        for col in cfg['metrics']:
            o, hp = eb_group(sub, col, wsub, None if hps is None else hps[(cg, col)]); new_hps[(cg, col)] = hp
            res[(cg, col)] = o
        if role == 'bowl':
            x, n, hp = shrink0(sub, 'dv_p', 'n_dp', wsub, None if hps is None else hps[(cg, 'death')]); new_hps[(cg, 'death')] = hp
            res[(cg, 'death')] = pd.DataFrame({'theta': x, 'n': n})
        ev[cg] = (res[(cg, 'v')].np + res[(cg, 'v')].nn)
    pids = res[('IPL', 'v')].index.union(res[('T20I', 'v')].index)
    eI = ev['IPL'].reindex(pids).fillna(0); eT = ev['T20I'].reindex(pids).fillna(0)
    aI = w_ipl * eI / (eI + EVID_K); aT = (1 - w_ipl) * eT / (eT + EVID_K)
    wI = aI / (aI + aT); out = pd.DataFrame(index=pids); out['wI'] = wI
    def bl(key, field):
        I = res[('IPL', key)][field].reindex(pids); T = res[('T20I', key)][field].reindex(pids)
        return (wI * I.fillna(0) + (1 - wI) * T.fillna(0))
    for col in cfg['metrics']:
        out[col] = bl(col, 'theta')
    out['v_norm'] = bl('v', 'xn')
    out['v_psd'] = np.sqrt((wI * res[('IPL', 'v')].psd.reindex(pids).fillna(0)) ** 2 + ((1 - wI) * res[('T20I', 'v')].psd.reindex(pids).fillna(0)) ** 2)
    out['delta'] = out.v - out.v_norm
    out['lb'] = out.v - 1.2816 * out.v_psd
    if role == 'bowl':
        I = res[('IPL', 'death')].theta.reindex(pids).fillna(0); T = res[('T20I', 'death')].theta.reindex(pids).fillna(0)
        out['death_v'] = wI * I + (1 - wI) * T
    for cg, t in (('IPL', 'I'), ('T20I', 'T')):
        o = res[(cg, 'v')].reindex(pids)
        out['n_p_' + t] = o.np.fillna(0); out['n_n_' + t] = o.nn.fillna(0); out['raw_p_' + t] = o.xp; out['r_' + t] = o.r
    out['n_p'] = out.n_p_I + out.n_p_T; out['n_n'] = out.n_n_I + out.n_n_T
    m = pm[pm.n_p > 0].groupby(['pid', 'comp_group']).match_id.nunique().unstack().reindex(pids).fillna(0)
    out['m_p_I'] = m.get('IPL', 0); out['m_p_T'] = m.get('T20I', 0); out['m_p'] = out.m_p_I + out.m_p_T
    if role == 'bowl': out['n_death_p'] = sum(res[(cg, 'death')].n.reindex(pids).fillna(0) for cg in ('IPL', 'T20I'))
    e = cfg['elig']
    if elig_ids is None:
        out['eligible'] = (out.n_p >= e['p_balls']) & (out.m_p >= e['p_matches']) & (out.n_p_I >= e['ipl_p_balls']) & (out.n_n >= e['n_balls'])
    else:
        out['eligible'] = out.index.isin(elig_ids)
    el = out[out.eligible]
    comp = sum(wgt * (el[c] - el[c].mean()) / el[c].std() for c, wgt in cfg['comps'].items())
    out['composite'] = comp
    out['score'] = 100 * (comp - comp.min()) / (comp.max() - comp.min())
    out['rank'] = out.score.rank(ascending=False, method='first')
    return out, new_hps

SPECS = list(itertools.product(['PI_main', 'PI_alt'], [65, 75, 85], [0.6, 0.7, 0.8]))

def run_role(role, B=300):
    pm0 = build_pm(role)
    prim, hps = score(role, pm0)
    elig = prim.index[prim.eligible]
    # ensemble across 18 specs (eligibility fixed)
    pms = {}; S = {}; R = {}
    for pi, thr, w in SPECS:
        if (pi, thr) not in pms: pms[(pi, thr)] = build_pm(role, pi, thr)
        o, _ = score(role, pms[(pi, thr)], w, elig_ids=elig)
        S[(pi, thr, w)] = o.score; R[(pi, thr, w)] = o['rank']
    S = pd.DataFrame(S).reindex(prim.index); R = pd.DataFrame(R).reindex(prim.index)
    prim['ens_score'] = S.mean(axis=1); prim['ens_sd'] = S.std(axis=1)
    prim['final_rank'] = prim.ens_score.where(prim.eligible).rank(ascending=False, method='first')
    prim['grid_top10'] = (R <= 10).mean(axis=1); prim['grid_best'] = R.min(axis=1); prim['grid_worst'] = R.max(axis=1)
    for k in [('PI_main', 65, 0.7), ('PI_main', 85, 0.7), ('PI_main', 75, 0.6), ('PI_main', 75, 0.8), ('PI_alt', 75, 0.7)]:
        prim[f'rank_{k[0][3:]}_{k[1]}_{int(k[2]*100)}'] = R[k]
    # match-level Poisson bootstrap at primary spec (hyper-parameters fixed), shared weights per match
    matches = pm0.match_id.unique(); boot_rank = []; boot_v = []
    for _ in range(B):
        mw = pd.Series(rng.poisson(1.0, len(matches)).astype(float), index=matches)
        wt = pd.Series(pm0.match_id.map(mw).values, index=pm0.index)
        o, _ = score(role, pm0, 0.7, wt=wt, hps=hps, elig_ids=elig)
        boot_rank.append(o['rank'].reindex(elig)); boot_v.append(o.v.reindex(elig))
    BR = pd.DataFrame(boot_rank).T; BV = pd.DataFrame(boot_v).T
    prim.loc[elig, 'boot_top10'] = (BR <= 10).mean(axis=1); prim.loc[elig, 'boot_rank_med'] = BR.median(axis=1)
    prim.loc[elig, 'boot_rank_lo'] = BR.quantile(.05, axis=1); prim.loc[elig, 'boot_rank_hi'] = BR.quantile(.95, axis=1)
    prim.loc[elig, 'v_ci_lo'] = BV.quantile(.05, axis=1); prim.loc[elig, 'v_ci_hi'] = BV.quantile(.95, axis=1)
    # consistency: match-level SD and % of pressure matches above expectation (raw), seasons positive
    d = pm0[pm0.n_p > 0].copy(); d['mv'] = d.v_p / d.n_p
    prim['pct_matches_pos'] = d.groupby('pid').mv.apply(lambda s: (s > 0).mean())
    prim['match_sd_per100'] = 100 * d.groupby('pid').mv.std()
    sea = d.groupby(['pid', 'season'])[['v_p', 'n_p']].sum(); sea = sea[sea.n_p >= 20]; sea['x'] = sea.v_p / sea.n_p
    prim['seasons_20b'] = sea.groupby('pid').size(); prim['seasons_pos'] = sea.groupby('pid').x.apply(lambda s: (s > 0).sum())
    prim['name'] = names.reindex(prim.index).values
    return prim, hps, R, S

def holdout(role):
    A, _ = score(role, build_pm(role, seasons=[2022, 2023, 2024]))
    Bpm = build_pm(role, seasons=[2025, 2026])
    fut = Bpm.groupby('pid')[['v_p', 'n_p']].sum(); fut = fut[fut.n_p >= 60]; fut['y'] = fut.v_p / fut.n_p; fut = fut.rename(columns={'n_p': 'yn'})[['y', 'yn']]
    j = A[['v', 'raw_p_I', 'raw_p_T', 'v_norm', 'n_p_I', 'n_p_T', 'composite']].join(fut, how='inner')
    j['raw_pressure'] = ((j.raw_p_I.fillna(0) * j.n_p_I + j.raw_p_T.fillna(0) * j.n_p_T) / (j.n_p_I + j.n_p_T))
    j = j[(j.n_p_I + j.n_p_T) >= 60]
    wmse = lambda p: float(np.average((j.y - p) ** 2, weights=j.yn))
    return {'n_players': int(len(j)),
            'spearman': {k: round(float(j[k].corr(j.y, method='spearman')), 3) for k in ['v', 'raw_pressure', 'v_norm']},
            'weighted_mse_x1000': {'EB_hierarchical': round(1000 * wmse(j.v), 2), 'raw_pressure_mean': round(1000 * wmse(j.raw_pressure), 2),
                                   'league_average(0)': round(1000 * wmse(0 * j.v), 2), 'normal_baseline_only': round(1000 * wmse(j.v_norm), 2)}}

if __name__ == '__main__':
    out = {}
    for role in ('bat', 'bowl'):
        prim, hps, R, S = run_role(role)
        prim.to_pickle(W + f'{role}_final.pkl'); R.to_pickle(W + f'{role}_gridR.pkl'); S.to_pickle(W + f'{role}_gridS.pkl')
        el = prim[prim.eligible]
        top10 = set(el.nsmallest(10, 'final_rank').index)
        out[role] = {'hyper': {f'{k[0]}|{k[1]}': {kk: float(vv) for kk, vv in v.items()} for k, v in hps.items()},
                     'n_eligible': int(prim.eligible.sum()), 'n_players_any': int(len(prim)),
                     'grid_top10_overlap_with_final': {str(k): len(top10 & set(R[k].nsmallest(10).index)) for k in R.columns},
                     'grid_spearman_with_final': {str(k): round(float(R[k].reindex(el.index).corr(el.final_rank, method='spearman')), 3) for k in R.columns},
                     'holdout': holdout(role)}
        print(role, out[role]['n_eligible'], out[role]['holdout'])
        print({k: (round(v['b'], 3), round(v['k'], 1)) for k, v in hps.items() if 'b' in v})
        cols = ['name', 'ens_score', 'score', 'v', 'v_norm', 'delta', 'n_p_I', 'n_p_T', 'm_p', 'grid_top10', 'boot_top10', 'boot_rank_lo', 'boot_rank_hi']
        print(el.sort_values('final_rank')[cols].head(22).round(3).to_string())
    json.dump(out, open(W + 'stage3.json', 'w'), indent=1, default=float)
