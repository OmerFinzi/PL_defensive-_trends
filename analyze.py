"""
PL Defensive Trends — analysis pipeline (2020/21 -> 2025/26).

Reads match-results CSVs (fixturedownload.com schema) from data/epl-*.csv,
computes league- and team-level defensive metrics plus multi-season trends,
and writes docs/data.json (consumed by the dashboard) and
outputs/team_season_defence.csv.

Data is match-results only. Player-level FPL stats are intentionally out of
scope (see .claude/skills/fpl-def-data). No numbers are invented.
"""
import glob, json, math, os
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(ROOT, "outputs")
os.makedirs(DOCS, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

def season_label(start_year: int) -> str:
    return f"{start_year}/{str(start_year + 1)[-2:]}"

# ---- Load & combine every season -------------------------------------------
frames = []
for path in sorted(glob.glob(os.path.join(DATA, "epl-*.csv"))):
    start_year = int(os.path.basename(path).split("-")[1].split(".")[0])
    df = pd.read_csv(path)
    df = df[df["Result"].notna()].copy()
    df["start_year"] = start_year
    df["season"] = season_label(start_year)
    goals = df["Result"].str.split(" - ", expand=True).astype(int)
    df["HG"], df["AG"] = goals[0], goals[1]
    frames.append(df)

m = pd.concat(frames, ignore_index=True)
m["total_goals"] = m["HG"] + m["AG"]
m["home_cs"] = (m["AG"] == 0).astype(int)     # home team kept a clean sheet
m["away_cs"] = (m["HG"] == 0).astype(int)     # away team kept a clean sheet
m["btts"] = ((m["HG"] > 0) & (m["AG"] > 0)).astype(int)
m["home_win"] = (m["HG"] > m["AG"]).astype(int)
m["away_win"] = (m["AG"] > m["HG"]).astype(int)
m["draw"] = (m["HG"] == m["AG"]).astype(int)
third = pd.cut(m["Round Number"], bins=[0, 12, 26, 38],
               labels=["Early (GW1-12)", "Mid (GW13-26)", "Late (GW27-38)"])
m["third"] = third

seasons = sorted(m["start_year"].unique())
latest = seasons[-1]
latest_label = season_label(latest)

# ---- League-wide per-season aggregates -------------------------------------
league = []
for y in seasons:
    s = m[m["start_year"] == y]
    n = len(s)
    league.append({
        "season": season_label(y),
        "start_year": int(y),
        "matches": int(n),
        "goals_per_game": round(s["total_goals"].mean(), 3),
        "home_goals_pg": round(s["HG"].mean(), 3),
        "away_goals_pg": round(s["AG"].mean(), 3),
        "clean_sheets": int(s["home_cs"].sum() + s["away_cs"].sum()),
        "cs_per_game": round((s["home_cs"].sum() + s["away_cs"].sum()) / n, 3),
        "home_cs_rate": round(s["home_cs"].mean(), 3),
        "away_cs_rate": round(s["away_cs"].mean(), 3),
        "btts_rate": round(s["btts"].mean(), 3),
        "home_win_rate": round(s["home_win"].mean(), 3),
        "away_win_rate": round(s["away_win"].mean(), 3),
        "draw_rate": round(s["draw"].mean(), 3),
        "home_ppg": round((s["home_win"] * 3 + s["draw"]).mean(), 3),
        "away_ppg": round((s["away_win"] * 3 + s["draw"]).mean(), 3),
        # match-level standard deviation behind each season average (these are
        # means over ~380 per-match observations, so that's the natural spread)
        "cs_per_game_sd": round((s["home_cs"] + s["away_cs"]).std(), 2),
        "goals_per_game_sd": round(s["total_goals"].std(), 2),
        "btts_rate_sd": round(s["btts"].std(), 2),
    })
league_df = pd.DataFrame(league)

# ---- Per-team per-season defensive table -----------------------------------
def team_defence(sdf):
    home = sdf.groupby("Home Team").agg(
        home_games=("home_cs", "size"), home_cs=("home_cs", "sum"),
        home_conceded=("AG", "sum")).rename_axis("team")
    away = sdf.groupby("Away Team").agg(
        away_games=("away_cs", "size"), away_cs=("away_cs", "sum"),
        away_conceded=("HG", "sum")).rename_axis("team")
    t = home.join(away, how="outer").fillna(0)
    t["games"] = t.home_games + t.away_games
    t["clean_sheets"] = t.home_cs + t.away_cs
    t["conceded"] = t.home_conceded + t.away_conceded
    t["cs_rate"] = t.clean_sheets / t.games
    t["home_cs_rate"] = t.home_cs / t.home_games.replace(0, np.nan)
    t["away_cs_rate"] = t.away_cs / t.away_games.replace(0, np.nan)
    t["conceded_pg"] = t.conceded / t.games
    return t

team_rows = []
for y in seasons:
    t = team_defence(m[m["start_year"] == y]).reset_index()
    t["season"] = season_label(y)
    t["start_year"] = y
    team_rows.append(t)
team_all = pd.concat(team_rows, ignore_index=True)
team_all.to_csv(os.path.join(OUT, "team_season_defence.csv"), index=False)

def team_table(y):
    t = team_defence(m[m["start_year"] == y]).reset_index()
    assert len(t) == 20, f"{season_label(y)} team table has {len(t)} teams, expected 20 — check Home/Away Team naming in data/epl-{y}.csv"
    t = t.sort_values("cs_rate", ascending=False)
    return [{
        "team": r.team, "games": int(r.games), "clean_sheets": int(r.clean_sheets),
        "cs_rate": round(r.cs_rate, 3), "conceded": int(r.conceded),
        "conceded_pg": round(r.conceded_pg, 3),
        "home_cs_rate": round(float(r.home_cs_rate), 3),
        "away_cs_rate": round(float(r.away_cs_rate), 3),
    } for r in t.itertuples()]

latest_table = team_table(latest)

# Best defensive team-seasons across the whole window. The dashboard hero used to
# call the latest season's leader "the best of the six seasons studied" without
# anything ever computing that — it was third, behind Man City and Liverpool, who
# both managed 21 clean sheets at 0.68 conceded in 2021/22. Ranked on clean-sheet
# rate, then goals conceded per game as the tiebreak.
best_defensive_seasons = [{
    "team": r.team, "season": r.season, "clean_sheets": int(r.clean_sheets),
    "cs_rate": round(r.cs_rate, 3), "conceded_pg": round(r.conceded_pg, 3),
} for r in team_all.sort_values(["cs_rate", "conceded_pg"],
                                ascending=[False, True]).head(5).itertuples()]

# ---- Trends: linear slope of key league metrics over 6 seasons -------------
def slope(series):
    x = np.arange(len(series))
    return float(np.polyfit(x, series.values, 1)[0])

trends = {
    "cs_per_game_slope": round(slope(league_df["cs_per_game"]), 4),
    "goals_per_game_slope": round(slope(league_df["goals_per_game"]), 4),
    "btts_slope": round(slope(league_df["btts_rate"]), 4),
    "home_advantage_ppg": [round(a - b, 3) for a, b in
                           zip(league_df["home_ppg"], league_df["away_ppg"])],
    "home_advantage_slope": round(
        slope(league_df["home_ppg"] - league_df["away_ppg"]), 4),
}

# ---- Season-third clean-sheet pattern (when to load defenders) --------------
def third_cs(sdf):
    g = sdf.groupby("third", observed=True)
    return {str(k): round(v, 3) for k, v in
            ((k, (grp["home_cs"].sum() + grp["away_cs"].sum()) / len(grp))
             for k, grp in g)}

thirds = {"all_seasons": third_cs(m), latest_label: third_cs(m[m["start_year"] == latest])}

# ---- Distribution of total goals per match: Gaussian vs Poisson -------------
# Goals per match is a COUNT — discrete, non-negative, right-skewed — so the
# textbook model is Poisson, not a normal curve. Both are fitted here so the
# chart can show the comparison instead of asserting it: the bell curve is what
# people reach for by habit, and seeing exactly where it fails is the point.
# erf/lgamma by hand — this project deliberately has no scipy dependency.
def norm_mass(k, mu, sd):
    """Normal probability over [k-0.5, k+0.5] — the fair way to compare a
    continuous density against integer counts (same width as a histogram bin)."""
    cdf = lambda x: 0.5 * (1 + math.erf((x - mu) / (sd * math.sqrt(2))))
    return cdf(k + 0.5) - cdf(k - 0.5)

def norm_pdf(x, mu, sd):
    return math.exp(-((x - mu) ** 2) / (2 * sd ** 2)) / (sd * math.sqrt(2 * math.pi))

def pois_pmf(k, lam):
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))

# Regularized upper incomplete gamma Q(a,x), for chi-square p-values. Raw
# chi-square statistics are NOT comparable between the two models because tail
# pooling leaves them with different degrees of freedom (the normal fits two
# parameters, Poisson one) — the p-value is what makes it a fair comparison.
def _gser(a, x):
    ap, s, d = a, 1.0 / a, 1.0 / a
    for _ in range(500):
        ap += 1; d *= x / ap; s += d
        if abs(d) < abs(s) * 1e-14:
            break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))

def _gcf(a, x):
    tiny = 1e-300
    b, c = x + 1 - a, 1 / tiny
    d = 1 / b if b != 0 else 1 / tiny
    h = d
    for i in range(1, 500):
        an = -i * (i - a); b += 2; d = an * d + b
        if abs(d) < tiny: d = tiny
        c = b + an / c
        if abs(c) < tiny: c = tiny
        d = 1 / d; de = d * c; h *= de
        if abs(de - 1) < 1e-14:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h

def chi2_p(stat, df):
    """Upper-tail p-value. High p = the model is consistent with the data."""
    if df <= 0 or stat <= 0:
        return None
    a, x = df / 2.0, stat / 2.0
    return 1 - _gser(a, x) if x < a + 1 else _gcf(a, x)

def chi2_gof(obs, prob_fn, n, n_params):
    """Pearson chi-square, pooling the right tail until every expected count
    reaches 5 so the approximation stays valid."""
    exp = [prob_fn(k) * n for k in range(len(obs))]
    o = [int(v) for v in obs]
    while len(exp) > 2 and exp[-1] < 5:
        exp[-2] += exp[-1]; o[-2] += o[-1]; exp.pop(); o.pop()
    stat = sum((oi - ei) ** 2 / ei for oi, ei in zip(o, exp))
    df = len(exp) - 1 - n_params
    p = chi2_p(stat, df)
    return round(stat, 1), df, (round(p, 4) if p is not None else None)

def fit_goals(vals, label, kmax):
    """Observed goals-per-match distribution plus both fitted models."""
    v = np.asarray(vals)
    n, mu, sd = len(v), float(v.mean()), float(v.std(ddof=1))
    obs = np.bincount(v, minlength=kmax + 1)
    gchi, gdf, gp = chi2_gof(obs, lambda k: norm_mass(k, mu, sd), n, 2)
    pchi, pdf, pp = chi2_gof(obs, lambda k: pois_pmf(k, mu), n, 1)
    return {
        "season": label, "n": n,
        "mean": round(mu, 3), "sd": round(sd, 3),
        "var_mean_ratio": round(sd ** 2 / mu, 3),        # Poisson predicts 1.0
        "skew": round(float(pd.Series(v).skew()), 3),    # normal predicts 0
        "bins": [{"k": k, "obs": int(obs[k]),
                  "obs_pct": round(obs[k] / n * 100, 2),
                  "gauss_pct": round(norm_mass(k, mu, sd) * 100, 2),
                  "pois_pct": round(pois_pmf(k, mu) * 100, 2)}
                 for k in range(kmax + 1)],
        # Smooth normal density as percent-per-goal, so it sits on the same scale
        # as the bars. Sampled below zero too, to show the mass the bell curve
        # puts on impossible negative scorelines.
        "gauss_curve": [{"x": round(x, 2), "y": round(norm_pdf(x, mu, sd) * 100, 3)}
                        for x in np.arange(-1.0, kmax + 1.01, 0.2)],
        "gauss_negative_pct": round(
            0.5 * (1 + math.erf((-0.5 - mu) / (sd * math.sqrt(2)))) * 100, 2),
        "gauss_chi2": gchi, "gauss_df": gdf, "gauss_p": gp,
        "pois_chi2": pchi, "pois_df": pdf, "pois_p": pp,
        "better": "poisson" if (pp or 0) >= (gp or 0) else "gauss",
    }

KMAX = int(m["total_goals"].max())
goal_dist = fit_goals(m["total_goals"].values, "All seasons", KMAX)
goal_dist["max_goals"] = KMAX
goal_dist["per_season"] = [fit_goals(m[m["start_year"] == y]["total_goals"].values,
                                     season_label(y), KMAX) for y in seasons]

# Does the Poisson finding actually pay off? If goals conceded are Poisson with
# mean lambda, a clean sheet is just P(0) = exp(-lambda) — so a team's clean-sheet
# rate should be predictable from its goals-conceded average alone, with no extra
# fitting. Checking that against all 120 team-seasons turns the distributional
# claim into something usable rather than academic.
_pred = np.exp(-team_all["conceded_pg"])
_err = _pred - team_all["cs_rate"]
_lt = team_all[team_all["season"] == latest_label]
_best = _lt.sort_values("conceded_pg").iloc[0]
goal_dist["poisson_cs_check"] = {
    "n_team_seasons": int(len(team_all)),
    "mae_pp": round(float(_err.abs().mean()) * 100, 1),
    "bias_pp": round(float(_err.mean()) * 100, 1),
    "corr": round(float(_pred.corr(team_all["cs_rate"])), 3),
    "example": {"team": _best["team"], "season": _best["season"],
                "conceded_pg": round(float(_best["conceded_pg"]), 3),
                "predicted_cs": round(float(math.exp(-_best["conceded_pg"])), 3),
                "actual_cs": round(float(_best["cs_rate"]), 3)},
}

# Pooled over 2,280 matches the verdict is emphatic, and the dashboard says so in
# words — so fail loudly if a data refresh ever inverts it rather than shipping a
# subtitle that lies. Deliberately NOT asserted per season: at n=380 a single
# season has little power to separate the two, and 2025/26 currently favours the
# normal curve. That nuance is reported, not hidden.
assert goal_dist["better"] == "poisson", (
    "Pooled goals-per-match no longer favours Poisson — the distribution "
    "commentary in build_dashboard.py and REPORT.md needs rewriting")

# ---- Most common exact scorelines -------------------------------------------
# Kept in home-away orientation on purpose: 1-0 outnumbering 0-1 IS the home
# advantage, and collapsing them would throw that away.
def scoreline_table(sdf, top=12):
    c = sdf.groupby(["HG", "AG"]).size().sort_values(ascending=False)
    n = len(sdf)
    return [{"score": f"{h}-{a}", "n": int(v), "pct": round(v / n * 100, 2)}
            for (h, a), v in c.head(top).items()]

_sc = m.groupby(["HG", "AG"]).size()
def _pair(h, a):
    return {"home": f"{h}-{a}", "away": f"{a}-{h}",
            "home_n": int(_sc.get((h, a), 0)), "away_n": int(_sc.get((a, h), 0))}

scorelines = {
    "overall": scoreline_table(m),
    "distinct": int(len(_sc)),
    "per_season": [{"season": season_label(y),
                    "top": scoreline_table(m[m["start_year"] == y], 3)}
                   for y in seasons],
    # Same margin, mirrored — the gap between each pair is home advantage.
    "mirrored": [_pair(1, 0), _pair(2, 1), _pair(2, 0), _pair(3, 1), _pair(3, 0)],
}

# ---- Defensive risers / fallers: 25/26 vs previous season -------------------
def conceded_pg_by_year(y):
    t = team_defence(m[m["start_year"] == y])
    return t["conceded_pg"]

cur = conceded_pg_by_year(latest)
prev = conceded_pg_by_year(latest - 1)
movers = []
for team in cur.index:
    if team in prev.index:
        d = cur[team] - prev[team]   # negative = conceding fewer = improving
        movers.append({"team": team, "cur": round(cur[team], 3),
                       "prev": round(prev[team], 3), "delta": round(d, 3)})
# Tiebreak on name so equal deltas get a stable published order rather than one
# that depends on pandas sort stability — Newcastle and Bournemouth both moved
# +0.211 in 2025/26, and which one appeared "third-worst" was previously arbitrary.
movers.sort(key=lambda r: (r["delta"], r["team"]))
risers = movers[:5]                    # improved most (delta most negative)
fallers = movers[-5:][::-1]            # worsened most

# ---- Promoted teams' defensive record in 25/26 -----------------------------
prev_teams = set(m[m["start_year"] == latest - 1]["Home Team"])
cur_teams = set(m[m["start_year"] == latest]["Home Team"])
promoted = sorted(cur_teams - prev_teams)
promoted_rows = [r for r in latest_table if r["team"] in promoted]

payload = {
    "meta": {
        "seasons": [season_label(y) for y in seasons],
        "latest": latest_label,
        "source": "fixturedownload.com (English Premier League results)",
        "generated_seasons": len(seasons),
        "total_matches": int(len(m)),
    },
    "league": league,
    "latest_table": latest_table,
    "best_defensive_seasons": best_defensive_seasons,
    "trends": trends,
    "goal_dist": goal_dist,
    "scorelines": scorelines,
    "thirds": thirds,
    "risers": risers,
    "fallers": fallers,
    "promoted": promoted_rows,
}

with open(os.path.join(DOCS, "data.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

# ---- Console summary --------------------------------------------------------
print(f"Seasons: {payload['meta']['seasons']}  | matches: {payload['meta']['total_matches']}")
print(f"\nLeague clean sheets per game:")
for r in league:
    print(f"  {r['season']}: {r['cs_per_game']:.2f} CS/game | {r['goals_per_game']:.2f} goals/game | BTTS {r['btts_rate']:.0%}")
print(f"\nCS/game trend slope: {trends['cs_per_game_slope']:+.4f} per season")
print(f"Home-advantage (PPG) trend slope: {trends['home_advantage_slope']:+.4f} per season")
print(f"\n{latest_label} top-6 defences (CS rate):")
for r in latest_table[:6]:
    print(f"  {r['team']:<15} CS {r['cs_rate']:.0%} | conceded/gm {r['conceded_pg']:.2f} | home CS {r['home_cs_rate']:.0%} away CS {r['away_cs_rate']:.0%}")
print(f"\nBiggest defensive improvers ({latest_label} vs {season_label(latest-1)}):")
for r in risers:
    print(f"  {r['team']:<15} {r['prev']:.2f} -> {r['cur']:.2f} conceded/gm ({r['delta']:+.2f})")
print(f"\nPromoted {latest_label}: {promoted}")

print("\nGoals per match — distribution fit (higher p = model consistent with data):")
print(f"  {'season':<12}{'n':>5}{'mean':>7}{'sd':>6}{'var/mean':>10}"
      f"{'Gauss chi2':>12}{'p':>8}{'Pois chi2':>11}{'p':>8}   better")
for r in [goal_dist] + goal_dist["per_season"]:
    gp = f"{r['gauss_p']:.3f}" if r["gauss_p"] is not None else "  n/a"
    pp = f"{r['pois_p']:.3f}" if r["pois_p"] is not None else "  n/a"
    print(f"  {r['season']:<12}{r['n']:>5}{r['mean']:>7.2f}{r['sd']:>6.2f}"
          f"{r['var_mean_ratio']:>10.2f}{r['gauss_chi2']:>12.1f}({r['gauss_df']}){gp:>8}"
          f"{r['pois_chi2']:>9.1f}({r['pois_df']}){pp:>8}   {r['better']}")
print(f"  The bell curve puts {goal_dist['gauss_negative_pct']:.2f}% of its mass on "
      f"negative scorelines (~{goal_dist['gauss_negative_pct']/100*goal_dist['n']:.0f} "
      f"impossible matches); Poisson cannot.")

print(f"\nMost common scorelines (home-away), all seasons "
      f"({scorelines['distinct']} distinct):")
for r in scorelines["overall"][:8]:
    print(f"  {r['score']}  {r['n']:>4}  {r['pct']:>5.2f}%")
print("  same margin mirrored (the gap is home advantage): " + " | ".join(
    f"{p['home']} {p['home_n']} vs {p['away']} {p['away_n']}" for p in scorelines["mirrored"][:3]))

print("\nWrote docs/data.json and outputs/team_season_defence.csv")
