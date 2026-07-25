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
p["dc90"] = p["defensive_contribution_per_90"].astype(float)
p["dc_matches"] = p["dc_matches"].astype(int)
p["defcon_points"] = p["defcon_points"].astype(int)
p["pts_per_m"] = (p["defcon_points"] / p["cost"]).round(2)

def rows(df, cols):
    return df[cols].to_dict(orient="records")

COLS = ["name", "team_short", "pos", "minutes", "dc", "dc90",
        "dc_matches", "defcon_points", "cost", "pts_per_m"]

# Leaderboards
top_points = p.sort_values(["defcon_points", "dc"], ascending=False).head(15)
top_per90 = p[p["minutes"] >= 900].sort_values("dc90", ascending=False).head(15)
best_value = p[(p["cost"] <= 5.5) & (p["defcon_points"] >= 6)].sort_values(
    "pts_per_m", ascending=False).head(12)
table = p.sort_values("defcon_points", ascending=False).head(30)

# Position summary: how DefCon points split across positions
pos_summary = []
for pos in ["DEF", "MID", "FWD"]:
    sub = p[p["pos"] == pos]
    hitters = sub[sub["defcon_points"] > 0]
    pos_summary.append({
        "pos": pos, "players": int(len(sub)),
        "returning_players": int(len(hitters)),
        "total_points": int(sub["defcon_points"].sum()),
        "avg_points_returning": round(float(hitters["defcon_points"].mean()) if len(hitters) else 0, 1),
    })

# Team DefCon: total points banked by each club's players
team_tot = (p.groupby("team_short")["defcon_points"].sum()
            .sort_values(ascending=False).reset_index())
team_defcon = [{"team": r.team_short, "points": int(r.defcon_points)}
               for r in team_tot.itertuples()]

payload = {
    "meta": {
        "season": "2025/26",
        "source": "vaastav/Fantasy-Premier-League archive (data/2025-26); official FPL API stats, season-end snapshot",
        "note": "DefCon points: +2/match at DEF>=10 or MID/FWD>=12 defensive contributions. GKs excluded.",
        "n_players": int(len(p)),
        "n_returning": int((p["defcon_points"] > 0).sum()),
    },
    "top_points": rows(top_points, COLS),
    "top_per90": rows(top_per90, COLS),
    "best_value": rows(best_value, COLS),
    "table": rows(table, COLS),
    "position_summary": pos_summary,
    "team_defcon": team_defcon,
}
with open(os.path.join(DOCS, "defcon.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

# --- Console summary ---------------------------------------------------------
print(f"Players analysed: {payload['meta']['n_players']} | with DefCon returns: {payload['meta']['n_returning']}")
print("\nTop 10 DefCon points banked (2025/26):")
for r in payload["top_points"][:10]:
    print(f"  {r['name']:<14} {r['team_short']} {r['pos']}  {r['defcon_points']:>3} pts  "
          f"({r['dc_matches']}/{r['minutes']//90 if r['minutes'] else 0} match-hits, {r['dc90']:.1f}/90, £{r['cost']}m)")
print("\nPoints by position:")
for r in pos_summary:
    print(f"  {r['pos']}: {r['total_points']} pts across {r['returning_players']} returning players")
print("\nTop 5 teams by DefCon points banked:")
for r in team_defcon[:5]:
    print(f"  {r['team']}: {r['points']}")
print("\nWrote docs/defcon.json")
