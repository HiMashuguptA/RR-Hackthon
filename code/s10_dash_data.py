import pandas as pd, numpy as np, json
W='/home/claude/work/'
out={}
for role in ('bat','bowl'):
    T=pd.read_pickle(W+f'{role}_table.pkl'); E=T[T.eligible].sort_values('final_rank')
    df=pd.read_pickle(W+('bat_balls.pkl' if role=='bat' else 'bowl_balls.pkl'))
    pid='striker_id' if role=='bat' else 'bowler_id'
    P=df[df.PI>=75]
    if role=='bat':
        g=P.groupby([pid,'comp_group','season']).agg(b=('v','size'),v=('v','sum'),r=('bat_runs','sum'),er=('E_runs','sum'),o=('out','sum'),m=('match_id','nunique'))
    else:
        g=P.groupby([pid,'comp_group','season']).agg(b=('v','size'),v=('v','sum'),r=('bowl_conc','sum'),er=('E_conc','sum'),o=('wk','sum'),l=('legal','sum'),m=('match_id','nunique'))
    g=g.reset_index(); g=g[g[pid].isin(E.index)]
    splits={}
    for _,x in g.iterrows():
        rec=[x.comp_group,int(x.season),int(x.b),round(float(x.v),2),int(x.r),round(float(x.er),1),int(x.o),int(x.m)]+([int(x.l)] if role=='bowl' else [])
        splits.setdefault(int(x[pid]),[]).append(rec)
    players=[]
    for i,r in E.iterrows():
        d=dict(id=int(i),name=r['name'],rank=int(r.final_rank),score=round(r.pressure_score,1),conf=r.confidence,pv=round(r.press_value_per100,1),nv=round(r.normal_value_per100,1),
               d=round(r.delta_per100,1),nI=int(r.n_p_I),nT=int(r.n_p_T),m=int(r.m_p),boot=round(float(r.boot_top10)*100),grid=round(float(r.grid_top10)*100),
               lo=int(r.boot_rank_lo),hi=int(r.boot_rank_hi),team=r.ipl26_team if isinstance(r.ipl26_team,str) else '',pos=round(float(r.pct_matches_pos)*100),
               seas=f"{int(r.seasons_pos)}/{int(r.seasons_20b)}" if not np.isnan(r.seasons_20b) else '-')
        if role=='bat':
            d.update(psr=round(r.P_SR,1),esr=round(r.P_exp_SR,1),nsr=round(r.N_SR,1),pdot=round(r.P_dot_pct,1),ndot=round(r.N_dot_pct,1),pbd=round(r.P_bdry_pct,1),nbd=round(r.N_bdry_pct,1),
                     pbpd=None if np.isnan(r.P_balls_per_dis) else round(r.P_balls_per_dis,1),nbpd=None if np.isnan(r.N_balls_per_dis) else round(r.N_balls_per_dis,1),
                     l5=round(r.L5P_SR,1) if r.L5P_balls>0 else None,l5b=int(r.L5P_balls) if r.L5P_balls==r.L5P_balls else 0,
                     ch=round(r.CHASE_SR,1) if r.CHASE_balls==r.CHASE_balls and r.CHASE_balls>0 else None,chb=int(r.CHASE_balls) if r.CHASE_balls==r.CHASE_balls else 0)
        else:
            d.update(pec=round(r.P_econ,2),eec=round(r.P_exp_econ,2),nec=round(r.N_econ,2),pw=int(r.P_wkts),pdot=round(r.P_dot_pct,1),ndot=round(r.N_dot_pct,1),pbd=round(r.P_bdry_pct,1),nbd=round(r.N_bdry_pct,1),
                     dth=round(r.DEATH_econ,2) if r.DEATH_legal==r.DEATH_legal and r.DEATH_legal>0 else None,dthb=int(r.DEATH_legal) if r.DEATH_legal==r.DEATH_legal else 0,
                     dfe=round(r.DEF_econ,2) if r.DEF_legal==r.DEF_legal and r.DEF_legal>0 else None,dfb=int(r.DEF_legal) if r.DEF_legal==r.DEF_legal else 0)
        d['sp']=splits.get(int(i),[])
        players.append(d)
    out[role]=players
a=json.load(open(W+'audit_stage1.json')); s3=json.load(open(W+'stage3.json'))
out['meta']=dict(pi=a['pi_validation'],chase=a['chase_win_by_cat'],hold={k:s3[k]['holdout'] for k in ('bat','bowl')},nel={k:s3[k]['n_eligible'] for k in ('bat','bowl')})
s=json.dumps(out,separators=(',',':')); open(W+'dash_data.json','w').write(s); print(len(s))
