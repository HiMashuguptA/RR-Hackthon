"""Stage 4 — descriptive evidence, confidence levels, final ranking dataset, T20I-only watchlist."""
import pandas as pd, numpy as np, json
import s3_score as S
W = '/home/claude/work/'
mp = pd.read_csv('/home/claude/data/competition_team_player_mapping.csv')
teams_of = mp.groupby('player_id').team_name.apply(lambda s: ', '.join(sorted(set(s))))
dup = set(mp.groupby('player_name').player_id.nunique().loc[lambda s: s > 1].index)
bt, bw = S.bt, S.bw

def bat_desc(d):
    g = d.groupby('pid')
    o = pd.DataFrame({'balls': g.size(), 'runs': g.bat_runs.sum(), 'outs': g.out.sum(),
                      'dots': g.isdot.sum(), 'bdry': g.bd.sum(), 'matches': g.match_id.nunique(), 'exp_runs': g.E_runs.sum()})
    o['SR'] = 100 * o.runs / o.balls; o['exp_SR'] = 100 * o.exp_runs / o.balls
    o['dot_pct'] = 100 * o.dots / o.balls; o['bdry_pct'] = 100 * o.bdry / o.balls
    o['balls_per_dis'] = o.balls / o.outs.replace(0, np.nan); o['avg'] = o.runs / o.outs.replace(0, np.nan)
    return o

def bowl_desc(d):
    g = d.groupby('pid')
    o = pd.DataFrame({'deliv': g.size(), 'legal': g.legal.sum(), 'conc': g.bowl_conc.sum(), 'wkts': g.wk.sum(),
                      'dots': g.isdot.sum(), 'bdry': g.bd.sum(), 'matches': g.match_id.nunique(), 'exp_conc': g.E_conc.sum(),
                      'opps': g.batting_team_id.nunique()})
    o['econ'] = 6 * o.conc / o.legal; o['exp_econ'] = 6 * o.exp_conc / o.legal
    o['dot_pct'] = 100 * o.dots / o.legal; o['bdry_pct'] = 100 * o.bdry / o.legal
    o['balls_per_wkt'] = o.legal / o.wkts.replace(0, np.nan)
    return o

def conf(r):
    if r.boot_top10 >= 0.6 and r.grid_top10 >= 0.75 and r.n_p >= 250 and r.m_p >= 25: return 'High'
    if r.boot_top10 >= 0.35 and r.grid_top10 >= 0.5 and r.n_p >= 120: return 'Medium'
    return 'Low'

summary = {}
for role in ('bat', 'bowl'):
    F = pd.read_pickle(W + f'{role}_final.pkl')
    df = bt if role == 'bat' else bw
    P = df[df.PI >= 75]; N = df[df.PI < 75]
    desc = bat_desc if role == 'bat' else bowl_desc
    Dp = desc(P).add_prefix('P_'); Dn = desc(N).add_prefix('N_')
    extra = {
        'IPLP_': desc(P[P.comp_group == 'IPL']), 'T20IP_': desc(P[P.comp_group == 'T20I']),
        'L5P_': desc(P[P.last5]), 'EXT_': desc(df[df.PI >= 90]),
    }
    if role == 'bat':
        extra['CHASE_'] = desc(P[(P.innings == 2) & (P.D > 1.2)]); extra['WKF_'] = desc(P[P.recent_wk >= 1])
    else:
        extra['DEF_'] = desc(P[P.innings == 2]); extra['FI_'] = desc(P[P.innings == 1]); extra['DEATH_'] = desc(P[P.phase == 'Death'])
    T = F.join(Dp).join(Dn)
    for k, v in extra.items():
        keep = ['balls', 'SR', 'runs', 'outs'] if role == 'bat' else ['legal', 'econ', 'wkts', 'dot_pct']
        T = T.join(v[keep].add_prefix(k))
    T['confidence'] = [conf(r) if e else 'Not eligible' for e, (_, r) in zip(T.eligible, T.iterrows())]
    T['teams_in_data'] = teams_of.reindex(T.index).values
    T['name_is_duplicated_in_mapping'] = T.name.isin(dup)
    T['pressure_score'] = T.ens_score.round(1); T['primary_spec_score'] = T.score.round(1)
    T['press_value_per100'] = 100 * T.v; T['normal_value_per100'] = 100 * T.v_norm; T['delta_per100'] = 100 * T.delta
    T = T.sort_values(['eligible', 'final_rank'], ascending=[False, True])
    T.to_pickle(W + f'{role}_table.pkl')
    # T20I-only watchlist (meets all criteria except IPL minimum)
    e = S.ROLE[role]['elig']
    wl_ids = T.index[(T.n_p >= e['p_balls']) & (T.m_p >= e['p_matches']) & (T.n_n >= e['n_balls'])]
    o, _ = S.score(role, S.build_pm(role), elig_ids=wl_ids)
    wl = o[o.eligible & ~o.index.isin(T.index[T.eligible])].sort_values('rank').head(8)
    wl['name'] = S.names.reindex(wl.index).values
    summary[role] = {'watchlist': wl[['name', 'v', 'n_p_I', 'n_p_T', 'm_p']].assign(v=lambda x: (100 * x.v).round(1)).reset_index().to_dict('records'),
                     'conf_counts_top10': T[T.final_rank <= 10].confidence.value_counts().to_dict()}
    print(role, summary[role])
json.dump(summary, open(W + 'stage4.json', 'w'), indent=1, default=float)
