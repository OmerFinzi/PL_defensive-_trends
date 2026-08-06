"""
DefCon (Defensive Contribution) analysis for 2025/26 — the new FPL scoring metric.

Source: the community FPL data archive (vaastav/Fantasy-Premier-League),
data/2025-26 snapshot. The LIVE FPL API cannot be used for this: by the time of
writing it had already reset to the 2026/27 pre-season (0 gameweeks played), so
it no longer holds 2025/26 per-player DefCon totals. The archive preserves them.

DefCon points rule (2025/26): a player banks +2 in a match if their defensive
contribution reaches the position threshold — DEF: >= 10 (clearances + blocks +
interceptions + tackles); MID/FWD: >= 12 (that CBIT total plus ball recoveries).
Goalkeepers are not eligible. The `defensive_contribution` field is already
position-correct (verified: DEF excludes recoveries, MID/FWD includes them).

Writes docs/defcon.json for the dashboard. This is PLAYER-level data from a
separate source to the match-results analysis in analyze.py — kept distinct.
"""
import os, json
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "data", "fpl_2025_26")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(DOCS, exist_ok=True)

POS = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
THRESH = {"DEF": 10, "MID": 12, "FWD": 12}

players = pd.read_csv(os.path.join(SRC, "players_raw.csv"))
teams = pd.read_csv(os.path.join(SRC, "teams.csv")).set_index("id")
gw = pd.read_csv(os.path.join(SRC, "merged_gw.csv"))

# --- DefCon points banked + threshold-hit matches, from per-gameweek data -----
# The archive ships a few exactly-duplicated (element, GW, fixture) rows; left in
# they double-count appearances and threshold hits. Genuine double-gameweeks have
# distinct fixture ids and must survive, so dedupe on the fixture, not the GW.
gw = gw.drop_duplicates(subset=["element", "GW", "fixture"])
gw = gw[gw["minutes"] > 0].copy()
thr = gw["position"].map(THRESH)
gw["hit"] = (thr.notna()) & (gw["defensive_contribution"] >= thr)
banked = gw.groupby("element").agg(
    dc_matches=("hit", "sum"),                  # matches reaching the threshold
    apps=("minutes", "size"),
).reset_index()
banked["defcon_points"] = banked["dc_matches"] * 2

# --- Merge with season-total player table ------------------------------------
p = players[players["element_type"].isin([2, 3, 4])].copy()   # outfield only
p = p.merge(banked, left_on="id", right_on="element", how="left").fillna(
    {"dc_matches": 0, "apps": 0, "defcon_points": 0})
p["pos"] = p["element_type"].map(POS)
p["team_name"] = p["team"].map(teams["name"])
p["team_short"] = p["team"].map(teams["short_name"])
p["cost"] = p["now_cost"] / 10.0
p["name"] = p["web_name"]
p["dc"] = p["defensive_contribution"].astype(int)
p["dc90"] = p["defensive_contribution_per_90"].astype(float).round(2)
p["dc_matches"] = p["dc_matches"].astype(int)
p["defcon_points"] = p["defcon_points"].astype(int)
p["pts_per_m"] = (p["defcon_points"] / p["cost"]).round(2)
p["apps"] = p["apps"].astype(int)

def wilson_ci(hits, n, z=1.96):
    """95% Wilson score interval on a hit-rate — how consistently a player
    reaches the DefCon threshold, not just their raw point total."""
    if n == 0:
        return 0.0, 0.0
    phat = hits / n
    denom = 1 + z * z / n
    center = phat + z * z / (2 * n)
    adj = z * np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))
    return round(max(0, (center - adj) / denom), 2), round(min(1, (center + adj) / denom), 2)

p["hit_rate"] = np.where(p["apps"] > 0, (p["dc_matches"] / p["apps"]).round(2), 0.0)
_ci = [wilson_ci(h, n) for h, n in zip(p["dc_matches"], p["apps"])]
p["hit_rate_ci_lo"] = [c[0] for c in _ci]
p["hit_rate_ci_hi"] = [c[1] for c in _ci]

# Raw CBIT (clearances + blocks + interceptions + tackles) and ball recoveries.
# These are the breakdown behind `dc`, not a ranking metric in their own right:
# DEF are scored on CBIT alone, MID/FWD on CBIT + recoveries, so ranking every
# position on raw CBIT buries midfielders whose recoveries genuinely do count.
# Player leaderboards below therefore rank on `dc`, which is position-correct.
p["cbit"] = (p["clearances_blocks_interceptions"] + p["tackles"]).astype(int)
p["rec"] = p["recoveries"].astype(int)

# Per-90 rates are NOT comparable across positions either, for a second reason:
# the thresholds differ (DEF 10, MID/FWD 12). Ranking on dc90 alone puts 10
# midfielders in a top 10 that advertises a DEF/MID/FWD legend. Expressing the
# rate as a share of the player's own threshold is the cross-position-fair form:
# 100% means an average match lands exactly on the +2 boundary.
p["thr"] = p["pos"].map(THRESH)
p["thr_pct"] = (p["dc90"] / p["thr"] * 100).round(1)

def rows(df, cols):
    return df[cols].to_dict(orient="records")

COLS = ["name", "team_short", "pos", "minutes", "dc", "dc90",
        "dc_matches", "defcon_points", "cost", "pts_per_m", "apps",
        "hit_rate", "hit_rate_ci_lo", "hit_rate_ci_hi"]
CBIT_COLS = ["name", "team_short", "pos", "minutes", "cbit", "rec", "dc", "dc90",
             "thr", "thr_pct"]

# Leaderboards
top_points = p.sort_values(["defcon_points", "dc"], ascending=False).head(15)
# NB: there is deliberately no raw dc90 leaderboard. Sorting every position on
# actions per 90 ignores that MID/FWD need 12 and DEF only 10, so it returns 15
# midfielders and reads as a cross-position ranking it isn't. The rate chart uses
# thr_pct instead (see top_cbit90 below).
best_value = p[(p["cost"] <= 5.5) & (p["defcon_points"] >= 6)].sort_values(
    "pts_per_m", ascending=False).head(12)
table = p.sort_values(["defcon_points", "dc"], ascending=False).head(30)

# Position summary: how DefCon points split across positions
pos_summary = []
for pos in ["DEF", "MID", "FWD"]:
    sub = p[p["pos"] == pos]
    hitters = sub[sub["defcon_points"] > 0]
    pos_summary.append({
        "pos": pos, "players": int(len(sub)),
        "returning_players": int(len(hitters)),
        "total_points": int(sub["defcon_points"].sum()),
        "avg_points_returning": round(float(hitters["defcon_points"].mean()) if len(hitters) else 0, 2),
    })

# Team DefCon: total points banked by each club's players
team_tot = (p.groupby("team_short")["defcon_points"].sum()
            .sort_values(ascending=False).reset_index())
team_defcon = [{"team": r.team_short, "points": int(r.defcon_points)}
               for r in team_tot.itertuples()]

# Defensive-action leaderboards. Players rank on the position-correct count (`dc`);
# the team table stays on raw CBIT so all 20 squads are compared like-for-like on
# one uniform stat rather than a DEF/MID hybrid.
top_cbit = p.sort_values("dc", ascending=False).head(15)
top_cbit90 = p[p["minutes"] >= 1500].sort_values("thr_pct", ascending=False).head(10)

# Team totals use `players` (all four positions), not the outfield-only `p`:
# goalkeepers make real clearances and blocks, and dropping their 958 league-wide
# CBIT reshuffles the table (Leeds 2nd -> 4th). GKs are excluded from the DefCon
# points table above because they are ineligible to score it — different question.
gk_cbit = (players[players["element_type"] == 1]
           .assign(cbit=lambda d: d["clearances_blocks_interceptions"] + d["tackles"],
                   team_short=lambda d: d["team"].map(teams["short_name"])))
team_cbit_tot = (pd.concat([p[["team_short", "cbit"]], gk_cbit[["team_short", "cbit"]]])
                 .groupby("team_short")["cbit"].sum()
                 .sort_values(ascending=False).reset_index())
team_cbit = [{"team": r.team_short, "cbit": int(r.cbit)}
             for r in team_cbit_tot.itertuples()]

# --- Who is it easiest to bank DefCon AGAINST? -------------------------------
# For every club, the average number of OPPOSING players who reached their
# threshold in a match against them. High = facing this club drags opponents into
# a lot of defensive work, so their fixtures are the ones to target when picking a
# cheap DefCon source. Note this is a property of the club being FACED, and the
# schedule is balanced (everyone plays everyone home and away), so no opponent
# adjustment is needed.
opp = gw.copy()
opp["opp_name"] = opp["opponent_team"].map(teams["name"])
_o = opp.groupby("opp_name").agg(hits=("hit", "sum"),
                                 matches=("fixture", "nunique")).reset_index()

def byar_ci(k, z=1.96):
    """95% Poisson interval on a count — same approximation used for set-piece
    ratios. With ~45-90 hits per club these intervals are wide, and saying so is
    the point: neighbouring clubs here are tied, not ranked."""
    if k <= 0:
        return 0.0, (1 - 1 / 9 + z / 3) ** 3
    lo = k * (1 - 1 / (9 * k) - z / (3 * np.sqrt(k))) ** 3
    hi = (k + 1) * (1 - 1 / (9 * (k + 1)) + z / (3 * np.sqrt(k + 1))) ** 3
    return max(0.0, lo), hi

# "Teams that stayed in the league" = everyone bar the bottom three. That has to
# come from the results feed, since the FPL snapshot's points/played columns are
# zeroed out (the API had already rolled over to the next pre-season).
_res = pd.read_csv(os.path.join(ROOT, "data", "epl-2025.csv"))
_res = _res[_res["Result"].notna()]
_g = _res["Result"].str.split(" - ", expand=True).astype(int)
_pts = []
for h, a, hg, ag in zip(_res["Home Team"], _res["Away Team"], _g[0], _g[1]):
    _pts.append((h, 3 if hg > ag else (1 if hg == ag else 0), hg - ag))
    _pts.append((a, 3 if ag > hg else (1 if hg == ag else 0), ag - hg))
_tbl = (pd.DataFrame(_pts, columns=["team", "pts", "gd"]).groupby("team").sum()
        .sort_values(["pts", "gd"], ascending=False).reset_index())
assert set(_tbl["team"]) == set(teams["name"]), (
    "club names differ between data/epl-2025.csv and fpl_2025_26/teams.csv — "
    "the relegation split below would silently drop or keep the wrong clubs")
relegated = set(_tbl.tail(3)["team"])

_o["per_match"] = _o["hits"] / _o["matches"]
_o["stays_up"] = ~_o["opp_name"].isin(relegated)
_o = _o.sort_values("per_match", ascending=False)
opp_defcon = []
for r in _o.itertuples():
    lo, hi = byar_ci(int(r.hits))
    opp_defcon.append({
        "team": r.opp_name,
        "team_short": str(teams.set_index("name").loc[r.opp_name, "short_name"]),
        "hits": int(r.hits), "matches": int(r.matches),
        "per_match": round(float(r.per_match), 2),
        "ci_lo": round(lo / r.matches, 2), "ci_hi": round(hi / r.matches, 2),
        "stays_up": bool(r.stays_up),
    })

# Pipeline safety net: a silent team-name mismatch in a merge/groupby would
# quietly shrink a "per club" table instead of erroring. The Premier League
# always has exactly 20 clubs, so fail loudly if any per-team table doesn't.
for _name, _tbl2 in [("team_defcon", team_defcon), ("team_cbit", team_cbit),
                     ("opp_defcon", opp_defcon)]:
    assert len(_tbl2) == 20, f"{_name} has {len(_tbl2)} teams, expected 20 — check team_short mapping"
assert sum(r["stays_up"] for r in opp_defcon) == 17, (
    f"expected 17 clubs staying up, got {sum(r['stays_up'] for r in opp_defcon)}")
assert all(r["matches"] == 38 for r in opp_defcon), "a club has != 38 fixtures in merged_gw"

payload = {
    "meta": {
        "season": "2025/26",
        "source": "vaastav/Fantasy-Premier-League archive (data/2025-26); official FPL API stats, season-end snapshot",
        "note": "DefCon points: +2/match at DEF>=10 or MID/FWD>=12 defensive contributions. GKs excluded.",
        "n_players": int(len(p)),
        # n_played is the honest denominator for the "how many returned" rate:
        # 247 of the 744 registered outfielders never played a minute all season.
        "n_played": int((p["minutes"] > 0).sum()),
        "n_returning": int((p["defcon_points"] > 0).sum()),
    },
    "top_points": rows(top_points, COLS),
    "best_value": rows(best_value, COLS),
    "table": rows(table, COLS),
    "position_summary": pos_summary,
    "team_defcon": team_defcon,
    "top_cbit": rows(top_cbit, CBIT_COLS),
    "top_cbit90": rows(top_cbit90, CBIT_COLS),
    "team_cbit": team_cbit,
    "opp_defcon": opp_defcon,
    "relegated": sorted(relegated),
}
with open(os.path.join(DOCS, "defcon.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

# --- Console summary ---------------------------------------------------------
print(f"Outfielders registered: {payload['meta']['n_players']} | played: {payload['meta']['n_played']} "
      f"| with DefCon returns: {payload['meta']['n_returning']}")
print("\nTop 10 DefCon points banked (2025/26):")
for r in payload["top_points"][:10]:
    print(f"  {r['name']:<14} {r['team_short']} {r['pos']}  {r['defcon_points']:>3} pts  "
          f"({r['dc_matches']}/{r['apps']} match-hits, {r['dc90']:.1f}/90, £{r['cost']}m)")
print("\nPoints by position:")
for r in pos_summary:
    print(f"  {r['pos']}: {r['total_points']} pts across {r['returning_players']} returning players")
print("\nTop 5 teams by DefCon points banked:")
for r in team_defcon[:5]:
    print(f"  {r['team']}: {r['points']}")
print("\nTop 5 players by defensive actions (position-correct season total):")
for r in payload["top_cbit"][:5]:
    print(f"  {r['name']:<14} {r['team_short']} {r['pos']}  {r['dc']} actions "
          f"({r['cbit']} CBIT + {r['rec']} rec, {r['dc90']}/90, {r['minutes']} min)")
print("\nTop 5 closest to their own threshold per 90 (min 1500 minutes):")
for r in payload["top_cbit90"][:5]:
    print(f"  {r['name']:<14} {r['team_short']} {r['pos']}  {r['thr_pct']}% of threshold "
          f"({r['dc90']}/90 vs {r['thr']} needed)")
_up = [r for r in opp_defcon if r["stays_up"]]
print(f"\nEasiest to bank DefCon against (opposing players hitting the threshold per match)")
print(f"  {len(_up)} clubs staying up; relegated and excluded: {', '.join(sorted(relegated))}")
for r in _up[:5]:
    print(f"  {r['team']:<16}{r['per_match']:.2f}/match  95% CI [{r['ci_lo']}, {r['ci_hi']}]  ({r['hits']} in 38)")
print("  ...")
for r in _up[-3:]:
    print(f"  {r['team']:<16}{r['per_match']:.2f}/match  95% CI [{r['ci_lo']}, {r['ci_hi']}]  ({r['hits']} in 38)")

print("\nWrote docs/defcon.json")
