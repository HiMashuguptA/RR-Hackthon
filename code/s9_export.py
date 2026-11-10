"""Stage 9 — export the supporting ranking dataset (all analysed players) + data dictionary."""
import pandas as pd
W='/home/claude/work/'; O=W+'out/'
cols_common = {'name':'player_name','eligible':'eligible','confidence':'confidence','final_rank':'final_rank','pressure_score':'pressure_score_ensemble',
 'primary_spec_score':'pressure_score_primary_spec','press_value_per100':'pressure_value_per100','normal_value_per100':'normal_value_per100',
 'delta_per100':'pressure_minus_normal_per100','lb':'lower_bound_per_ball','n_p_I':'ipl_pressure_balls','n_p_T':'t20i_pressure_balls','n_p':'total_pressure_balls',
 'm_p_I':'ipl_pressure_matches','m_p_T':'t20i_pressure_matches','m_p':'pressure_matches','n_n':'normal_balls','wI':'ipl_blend_weight',
 'boot_top10':'bootstrap_p_top10','boot_rank_lo':'bootstrap_rank_p05','boot_rank_hi':'bootstrap_rank_p95','grid_top10':'share_of_18_specs_in_top10',
 'grid_best':'best_rank_18_specs','grid_worst':'worst_rank_18_specs','rank_main_65_70':'rank_thr65','rank_main_85_70':'rank_thr85','rank_main_75_60':'rank_blend60_40',
 'rank_main_75_80':'rank_blend80_20','rank_alt_75_70':'rank_alt_pressure_index','pct_matches_pos':'pct_pressure_matches_above_exp','match_sd_per100':'match_sd_per100',
 'seasons_20b':'seasons_with_20plus_pressure_balls','seasons_pos':'seasons_positive','ipl26_team':'ipl2026_team_in_data','name_is_duplicated_in_mapping':'name_duplicated_in_mapping'}
bat = {'runs_ae':'pressure_runs_ae_per_ball','out_ae':'pressure_dismissal_avoid_per_ball','dot_ae':'pressure_dot_avoid_per_ball','bd_ae':'pressure_boundary_ae_per_ball',
 'P_runs':'pressure_runs','P_balls':'pressure_balls_faced_raw','P_SR':'pressure_SR','P_exp_SR':'pressure_expected_SR','P_dot_pct':'pressure_dot_pct','P_bdry_pct':'pressure_boundary_pct',
 'P_outs':'pressure_dismissals','P_balls_per_dis':'pressure_balls_per_dismissal','N_SR':'normal_SR','N_dot_pct':'normal_dot_pct','N_balls_per_dis':'normal_balls_per_dismissal',
 'L5P_balls':'last5_pressure_balls','L5P_SR':'last5_pressure_SR','CHASE_balls':'difficult_chase_balls','CHASE_SR':'difficult_chase_SR','WKF_balls':'wickets_falling_balls','WKF_SR':'wickets_falling_SR',
 'IPLP_SR':'ipl_pressure_SR','T20IP_SR':'t20i_pressure_SR'}
bowl = {'conc_ae':'pressure_runs_saved_ae_per_ball','wk_ae':'pressure_wkts_ae_per_ball','dot_ae':'pressure_dot_ae_per_ball','bd_ae':'pressure_boundary_supp_per_ball','death_v':'death_pressure_value_per_ball',
 'P_legal':'pressure_legal_balls','P_conc':'pressure_runs_conceded','P_econ':'pressure_economy','P_exp_econ':'pressure_expected_economy','P_wkts':'pressure_bowler_wkts','P_dot_pct':'pressure_dot_pct',
 'P_bdry_pct':'pressure_boundary_pct','P_balls_per_wkt':'pressure_balls_per_wkt','P_opps':'pressure_distinct_opponents','N_econ':'normal_economy','N_dot_pct':'normal_dot_pct',
 'DEATH_legal':'death_pressure_balls','DEATH_econ':'death_pressure_economy','DEF_legal':'defending_pressure_balls','DEF_econ':'defending_pressure_economy','FI_legal':'first_inns_pressure_balls','FI_econ':'first_inns_pressure_economy',
 'IPLP_econ':'ipl_pressure_economy','T20IP_econ':'t20i_pressure_economy'}
for role, extra in (('bat',bat),('bowl',bowl)):
    T = pd.read_pickle(W+f'{role}_table.pkl')
    m = {**cols_common, **extra}
    out = T[[c for c in m if c in T]].rename(columns=m); out.index.name='player_id'
    out = out.sort_values(['eligible','final_rank','total_pressure_balls'], ascending=[False,True,False]).round(4)
    out.to_csv(O+f'ranking_dataset_{"batters" if role=="bat" else "bowlers"}.csv')
    print(role, out.shape)
dd = """Data dictionary — ranking_dataset_batters.csv / ranking_dataset_bowlers.csv
One row per player with any IPL/T20I batting (or bowling) in the supplied data (innings 1-2, IPL + T20I only).
player_id / player_name ........ IDs and exact display names from competition_team_player_mapping.csv
eligible ....................... meets fixed eligibility thresholds (see report s.8/9)
final_rank ..................... rank by pressure_score_ensemble among eligible players (1 = best)
pressure_score_ensemble ........ mean 0-100 composite score over 18 model specifications (THE ranking score)
pressure_score_primary_spec .... 0-100 score under the primary spec (PI_main, 75th pct, 70:30)
pressure_value_per100 .......... shrunk posterior RAA (bat) / RSAA (bowl) per 100 pressure balls
normal_value_per100 ............ shrunk value per 100 normal-pressure balls (own baseline)
pressure_minus_normal_per100 ... difference of the two
lower_bound_per_ball ........... posterior 10th percentile of pressure value (per ball)
*_pressure_balls / *_matches ... sample sizes (pressure = Pressure Index >= 75)
bootstrap_* .................... 300 match-level Poisson bootstrap replicates (eligible only)
share_of_18_specs_in_top10 ..... robustness across pressure spec x threshold x IPL:T20I weight
rank_thr65 / rank_thr85 / rank_blend60_40 / rank_blend80_20 / rank_alt_pressure_index ... ranks under alternative specs
*_ae_per_ball .................. per-ball value above context expectation (shrunk)
pressure_SR / pressure_economy etc. ... raw descriptive statistics on pressure balls; expected_* = average-player expectation on the same balls
last5 / difficult_chase (D>1.2) / wickets_falling (wicket in last 18 legal balls) / death / defending (2nd inns) splits are raw, pressure balls only
ipl2026_team_in_data ........... team in the IPL 2026 competition mapping (blank = no IPL 2026 record)
"""
open(O+'data_dictionary.txt','w').write(dd)
