"""Stage 5 — charts (all values computed from pipeline outputs)."""
import pandas as pd, numpy as np, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W = '/home/claude/work/'; C = W + 'charts/'
import os; os.makedirs(C, exist_ok=True)
INK, INK2, MUTE, GRID, SURF = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0', '#fcfcfb'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
CONF = {'High': '#1d5ba6', 'Medium': '#5d9be6', 'Low': '#b9d4f4'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': MUTE, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlesize': 12, 'axes.titleweight': 'bold',
                     'axes.titlecolor': INK, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': .8, 'axes.axisbelow': True})
def save(f, n): f.tight_layout(); f.savefig(C + n, dpi=200); plt.close(f)

b = pd.read_pickle(W + 'deliveries.pkl'); a1 = json.load(open(W + 'audit_stage1.json'))
# 1 pressure category distribution and validation
f, ax = plt.subplots(1, 3, figsize=(13, 3.8))
cats = ['Low', 'Medium', 'High', 'Extreme']
fc = b[b.faced]
cw = pd.Series(a1['chase_win_by_cat']).reindex(cats)
ax[0].bar(cats, 100 * cw, color=ORANGE, width=.6); ax[0].set_ylabel('Chasing team win % (state at start of over)')
ax[0].set_title('Chases won, by pressure category')
for i, val in enumerate(100 * cw): ax[0].text(i, val + 1, f'{val:.0f}%', ha='center', color=INK2, fontsize=9)
ax[0].set_ylim(0, 75)
v = pd.DataFrame(a1['pi_validation']).set_index('pcat').reindex(cats)
ax[1].bar(cats, 100 * v.dismissal_pct, color=BLUE, width=.6); ax[1].set_ylabel('Batter dismissals per 100 balls'); ax[1].set_title('Dismissal rate rises with pressure')
for i, val in enumerate(100 * v.dismissal_pct): ax[1].text(i, val + .1, f'{val:.2f}', ha='center', color=INK2, fontsize=9)
ax[1].set_ylim(0, 8.5)
ax[2].bar(cats, 100 * v.rpb, color=BLUE, width=.6); ax[2].set_ylabel('Bat runs per 100 balls'); ax[2].set_title('Scoring rate falls with pressure')
for i, val in enumerate(100 * v.rpb): ax[2].text(i, val + 1.5, f'{val:.0f}', ha='center', color=INK2, fontsize=9)
ax[2].set_ylim(0, 160)
save(f, 'pi_distribution.png')

# 1b PI by over (mean) per innings
f, ax = plt.subplots(figsize=(7.5, 3.6))
for inn, col in ((1, BLUE), (2, ORANGE)):
    s = b[b.innings == inn].groupby('overid').PI.mean(); ax.plot(s.index, s.values, color=col, lw=2, label=f'Innings {inn}', marker='o', ms=4)
ax.set_xlabel('Over'); ax.set_ylabel('Mean Pressure Index (0–100)'); ax.set_title('Average Pressure Index by over'); ax.legend(frameon=False); ax.set_xticks(range(1, 21))
save(f, 'pi_by_over.png')

for role, unit in (('bat', 'Runs added above expectation per 100 balls'), ('bowl', 'Runs saved above expectation per 100 balls')):
    T = pd.read_pickle(W + f'{role}_table.pkl'); E = T[T.eligible]; top = E[E.final_rank <= 10].sort_values('final_rank')
    lab = 'batters' if role == 'bat' else 'bowlers'
    # 2 ranking bar
    f, ax = plt.subplots(figsize=(8, 4.6))
    y = np.arange(10)[::-1]
    ax.barh(y, top.pressure_score, color=[CONF[c] for c in top.confidence], height=.62)
    for yi, (_, r) in zip(y, top.iterrows()):
        ax.text(r.pressure_score + 1, yi, f'{r.pressure_score:.1f}  ({r.confidence})', va='center', fontsize=9, color=INK2)
    ax.set_yticks(y, [f'{int(r)}. {n}' for r, n in zip(top.final_rank, top.name)]); ax.set_xlim(0, 118); ax.grid(axis='y', visible=False)
    ax.set_xlabel('Pressure Performance Score (ensemble, 0–100 among eligible players)')
    ax.set_title(f'Top 10 {lab} under pressure')
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=CONF[k], label=f'{k} confidence') for k in CONF], frameon=False, loc='lower right', fontsize=8)
    save(f, f'{role}_top10.png')
    # 3 pressure vs normal scatter
    f, ax = plt.subplots(figsize=(7.5, 5.6))
    rest = E[E.final_rank > 10]
    ax.scatter(rest.normal_value_per100, rest.press_value_per100, s=26, color='#c8c7c2', edgecolor='white', lw=.6, label='Other eligible players')
    ax.scatter(top.normal_value_per100, top.press_value_per100, s=60, color=BLUE, edgecolor='white', lw=1.2, label='Top 10', zorder=3)
    lim = [min(E.normal_value_per100.min(), E.press_value_per100.min()) - 2, max(E.normal_value_per100.max(), E.press_value_per100.max()) + 3]
    ax.plot(lim, lim, ls='--', color=MUTE, lw=1); ax.text(lim[1] - 1, lim[1] - 3, 'pressure = normal', color=MUTE, fontsize=8, ha='right')
    for _, r in top.iterrows():
        ax.annotate(str(int(r.final_rank)), (r.normal_value_per100, r.press_value_per100), xytext=(5, -3), textcoords='offset points', fontsize=8, color=INK, fontweight='bold')
    key = '\n'.join(f'{int(r.final_rank)}. {r["name"]}' for _, r in top.iterrows())
    ax.text(0.02, 0.98, key, transform=ax.transAxes, va='top', fontsize=7.5, color=INK2, bbox=dict(facecolor='white', edgecolor=GRID))
    ax.set_xlabel('Normal-pressure baseline (' + unit.split(' per')[0].lower() + ' / 100 balls)')
    ax.set_ylabel('Pressure estimate (same units)'); ax.set_title(f'{lab.capitalize()}: pressure vs normal performance (shrunk estimates)')
    ax.legend(frameon=False, loc='lower right', fontsize=8)
    save(f, f'{role}_press_vs_normal.png')
    # 4 bootstrap rank intervals
    f, ax = plt.subplots(figsize=(7.5, 4.4))
    for yi, (_, r) in zip(y, top.iterrows()):
        ax.plot([r.boot_rank_lo, r.boot_rank_hi], [yi, yi], color=CONF[r.confidence], lw=3, solid_capstyle='round')
        ax.scatter(r.boot_rank_med, yi, color=INK, s=22, zorder=3)
        ax.text(r.boot_rank_hi + 1, yi, f'P(top 10) = {r.boot_top10:.0%}', va='center', fontsize=8, color=INK2)
    ax.set_yticks(y, top.name); ax.grid(axis='y', visible=False); ax.set_xlim(0, 85)
    ax.set_xlabel('Rank in 300 match bootstrap resamples (dot = median; bar = 5th–95th pct)')
    ax.set_title(f'Ranking uncertainty — top 10 {lab}'); ax.axvline(10.5, color=MUTE, ls=':', lw=1)
    save(f, f'{role}_bootstrap.png')
    # 5 sensitivity heatmap
    R = pd.read_pickle(W + f'{role}_gridR.pkl').loc[top.index]
    f, ax = plt.subplots(figsize=(11, 4.4))
    im = ax.imshow(R.values.astype(float), cmap='Blues_r', vmin=1, vmax=30, aspect='auto')
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            val = R.values[i, j]; ax.text(j, i, f'{int(val)}', ha='center', va='center', fontsize=7.5, color='white' if val <= 12 else INK)
    ax.set_yticks(range(10), top.name); ax.grid(False)
    ax.set_xticks(range(R.shape[1]), [f"{'Main' if a == 'PI_main' else 'Alt'} P{b_}\n{int(c*100)}:{int(100-c*100)}" for a, b_, c in R.columns], fontsize=7)
    ax.set_title(f'Rank of each top-10 {lab[:-1]} under 18 model specifications (pressure spec, percentile threshold, IPL:T20I weight)')
    cb = f.colorbar(im, ax=ax, fraction=.02); cb.set_label('Rank (darker = better)')
    save(f, f'{role}_sensitivity.png')
    # 6 IPL vs T20I
    f, ax = plt.subplots(figsize=(8, 4.2))
    k = 'SR' if role == 'bat' else 'econ'
    I = top[f'IPLP_{k}']; Tt = top[f'T20IP_{k}']; xx = np.arange(10)
    ax.bar(xx - .2, I, .38, color=BLUE, label='IPL'); ax.bar(xx + .2, Tt.where(top[f"T20IP_{'balls' if role=='bat' else 'legal'}"] >= 30), .38, color=ORANGE, label='T20I (≥30 balls)')
    ax.set_xticks(xx, top.name, rotation=35, ha='right', fontsize=8)
    ax.set_ylabel('Strike rate under pressure' if role == 'bat' else 'Economy under pressure (runs/over)')
    ax.set_title(f'IPL vs T20I pressure {"strike rate" if role=="bat" else "economy"} — top 10 {lab}'); ax.legend(frameon=False)
    save(f, f'{role}_ipl_t20i.png')

# 7 match-level consistency boxplots
import s3_score as S
for role, lab in (('bat', 'batters'), ('bowl', 'bowlers')):
    T = pd.read_pickle(W + f'{role}_table.pkl'); top = T[T.final_rank <= 10].sort_values('final_rank')
    pm = S.build_pm(role); pm = pm[(pm.n_p >= 6) & pm.pid.isin(top.index)]; pm['mv'] = 100 * pm.v_p / pm.n_p
    data = [pm[pm.pid == p].mv.values for p in top.index]
    f, ax = plt.subplots(figsize=(9, 4.2))
    bp = ax.boxplot(data, patch_artist=True, widths=.55, showfliers=False, medianprops=dict(color=INK, lw=1.5))
    for p in bp['boxes']: p.set(facecolor='#cfe0f5', edgecolor=BLUE)
    for i, d in enumerate(data): ax.scatter(np.random.default_rng(i).normal(i + 1, .06, len(d)), d, s=6, color=BLUE, alpha=.45, zorder=3)
    ax.axhline(0, color=MUTE, lw=1, ls='--'); ax.set_xticks(range(1, 11), top.name, rotation=35, ha='right', fontsize=8)
    ax.set_ylabel('Per-match pressure value per 100 balls'); ax.set_ylim(-150, 150)
    ax.set_title(f'Match-to-match consistency — top 10 {lab}'); ax.set_xlabel('Each dot = one match with ≥6 pressure balls (y clipped to ±150)', fontsize=8)
    save(f, f'{role}_consistency.png')
print(os.listdir(C))
