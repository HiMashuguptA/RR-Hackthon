"""Stage 6 — independent verification of the final selections (separate code path from raw CSVs)."""
import pandas as pd, numpy as np, json
import s3_score as S
D = '/home/claude/data/'; W = '/home/claude/work/'
raw = pd.read_csv(D + 'ball_by_ball.csv', low_memory=False)
m = pd.read_csv(D + 'matches.csv'); c = pd.read_csv(D + 'competitions.csv'); mp = pd.read_csv(D + 'competition_team_player_mapping.csv')
m = m.merge(c, on='comp_id')
keep = m[(m.comp_name.str.startswith('IPL')) | (m.match_format == 'T20I')].match_id
r = raw[raw.match_id.isin(keep) & raw.innings.isin([1, 2])]
checks = {}
res = {}
for role in ('bat', 'bowl'):
    T = pd.read_pickle(W + f'{role}_table.pkl'); top = T[T.final_rank <= 10].sort_values('final_rank')
    ids = top.index.tolist()
    names_map = mp.drop_duplicates('player_id').set_index('player_id').player_name
    checks[f'{role}_ids_in_mapping'] = all(i in names_map.index for i in ids)
    checks[f'{role}_names_exact'] = all(names_map[i] == n for i, n in zip(ids, top.name))
    checks[f'{role}_no_duplicates'] = len(set(ids)) == 10 and top.name.nunique() == 10
    checks[f'{role}_all_eligible'] = bool(top.eligible.all())
    rows = []
    for pid in ids:
        if role == 'bat':
            d = r[(r.striker_id == pid) & (r.extras_type.fillna('') != 'wide')]
            runs = d.runs.sum(); balls = len(d)
            outs = (d.is_wicket & (d.dismissed_player_id == pid) & (d.dismissal_type != 'Retire Out')).sum()
            pipe_runs = top.loc[pid, 'P_runs'] + top.loc[pid, 'N_runs']; pipe_balls = top.loc[pid, 'P_balls'] + top.loc[pid, 'N_balls']
            pipe_outs = top.loc[pid, 'P_outs'] + top.loc[pid, 'N_outs']
            rows.append(dict(pid=pid, name=names_map[pid], runs=runs, balls=balls, SR=round(100 * runs / balls, 2), outs=outs,
                             match=(runs == pipe_runs) and (balls == pipe_balls) and (outs == pipe_outs)))
        else:
            d = r[r.bowler_id == pid]; et = d.extras_type.fillna('')
            legal = (~et.isin(['wide', 'Overstep', 'other'])).sum()
            conc = d.runs.sum() + et.isin(['wide', 'Overstep', 'other']).sum()   # byes/leg-byes excluded
            wk = (d.is_wicket & d.dismissal_type.isin(['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket'])).sum()
            ro = (d.is_wicket & d.dismissal_type.eq('RunOut')).sum()
            pl = top.loc[pid, 'P_legal'] + top.loc[pid, 'N_legal']; pc = top.loc[pid, 'P_conc'] + top.loc[pid, 'N_conc']; pw = top.loc[pid, 'P_wkts'] + top.loc[pid, 'N_wkts']
            rows.append(dict(pid=pid, name=names_map[pid], legal=legal, conceded=conc, econ=round(6 * conc / legal, 2), bowler_wkts=wk,
                             runouts_not_credited=ro, match=(legal == pl) and (conc == pc) and (wk == pw)))
    res[role] = pd.DataFrame(rows)
    checks[f'{role}_raw_stats_match_pipeline'] = bool(res[role].match.all())
    # re-run primary-spec scoring from scratch and compare
    o, _ = S.score(role, S.build_pm(role))
    checks[f'{role}_primary_score_reproduces'] = bool(np.allclose(o.score.reindex(ids).values, top.score.values, atol=1e-6))
checks['missing_matches_all_abandoned'] = bool(m[~m.match_id.isin(raw.match_id)].result.eq('Match Abandoned').all())
checks['no_overlap_bat_bowl_required'] = 'n/a (separate lists)'
json.dump({'checks': checks, 'bat': res['bat'].to_dict('records'), 'bowl': res['bowl'].to_dict('records')}, open(W + 'verify.json', 'w'), indent=1, default=lambda x: x.item() if hasattr(x, 'item') else str(x))
print(json.dumps(checks, indent=1)); print(res['bat'].to_string()); print(res['bowl'].to_string())
