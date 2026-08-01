"""
Set-piece analysis (penalties EXCLUDED) for the PL defensive-trends project.

Two reliable, distinct sources:
  1. football-data.co.uk (data/football_data/E0_*.csv) -> corners for/against
     per team and league-wide, 2020/21..2025/26. Corners are open-play set
     pieces (no penalties), giving attacking (corners won) and defensive
     (corners conceded) set-piece VOLUME.
  2. Official FPL set-piece taker orders (data/fpl_2025_26/players_raw.csv)
     -> designated corner and direct-free-kick takers per club, 2025/26.
     Penalty takers are intentionally excluded.

Honesty note: goal-level "goals scored/conceded from set pieces" and a verified
set-piece SCORER list need event data (Opta/StatsBomb via FBref/Understat), which
was not reliably accessible when this was built (FBref 403; Understat served
stripped pages). Those are NOT fabricated here. Direct-free-kick *takers* are
reported as designated takers, not as confirmed scorers.

Writes docs/setpieces.json.
"""
import os, glob, json
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(ROOT, "data", "football_data")
FPL = os.path.join(ROOT, "data", "fpl_2025_26")
DOCS = os.path.join(ROOT, "docs")

# football-data team names -> the names used elsewhere in this project
CANON = {"Man United": "Man Utd", "Tottenham": "Spurs"}
def canon(t): return CANON.get(t, t)

def season_label(y): return f"{y}/{str(y + 1)[-2:]}"

# ---- Corners: league trend + per-team (attacking = won, defensive = conceded)
league, team_latest_rows = [], None
latest_year = None
for path in sorted(glob.glob(os.path.join(FD, "E0_*.csv"))):
    year = int(os.path.basename(path).split("_")[1].split(".")[0])
    df = pd.read_csv(path)
    df = df[df["HC"].notna() & df["AC"].notna()].copy()
    n = len(df)
    league.append({
        "season": season_label(year),
        "matches": int(n),
        "corners_pg": round((df["HC"].sum() + df["AC"].sum()) / n, 2),  # both teams / match
    })
    # per-team for this season
    home = df.groupby("HomeTeam").agg(hg=("HC", "size"), hf=("HC", "sum"), ha=("AC", "sum"))
    away = df.groupby("AwayTeam").agg(ag=("AC", "size"), af=("AC", "sum"), aa=("HC", "sum"))
    t = home.join(away, how="outer").fillna(0)
    t.index = [canon(x) for x in t.index]
    assert len(t) == 20, f"{season_label(year)} corners table has {len(t)} teams, expected 20 — check the CANON name mapping"
    t["games"] = t.hg + t.ag
    t["cf"] = t.hf + t.af            # corners won (attacking)
    t["ca"] = t.ha + t.aa            # corners conceded (defensive)
    if year == max(int(os.path.basename(p).split("_")[1].split(".")[0])
                   for p in glob.glob(os.path.join(FD, "E0_*.csv"))):
        latest_year = year
        rows = []
        for team, r in t.iterrows():
            rows.append({
                "team": team, "games": int(r.games),
                "for": int(r.cf), "against": int(r.ca),
                "for_pg": round(r.cf / r.games, 2),
                "against_pg": round(r.ca / r.games, 2),
                "net_pg": round((r.cf - r.ca) / r.games, 2),
                "for_home_pg": round(r.hf / r.hg, 2) if r.hg else 0,
                "for_away_pg": round(r.af / r.ag, 2) if r.ag else 0,
            })
        team_latest_rows = sorted(rows, key=lambda x: x["for_pg"], reverse=True)

latest_label = season_label(latest_year)

# ---- Set-piece takers (corners + direct free kicks; penalties excluded) ------
players = pd.read_csv(os.path.join(FPL, "players_raw.csv"))
teams = pd.read_csv(os.path.join(FPL, "teams.csv")).set_index("id")["name"].to_dict()

def first_taker(team_id, col):
    sub = players[(players["team"] == team_id) & (players[col] == 1)]
    if len(sub):
        return sub.iloc[0]["web_name"]
    return None

taker_rows = []
for tid, tname in teams.items():
    taker_rows.append({
        "team": tname,
        "corner_taker": first_taker(tid, "corners_and_indirect_freekicks_order"),
        "fk_taker": first_taker(tid, "direct_freekicks_order"),
    })
taker_rows.sort(key=lambda r: r["team"])
assert len(taker_rows) == 20, f"taker_rows has {len(taker_rows)} teams, expected 20 — check data/fpl_2025_26/teams.csv"

# Notable takers: players who are the #1 taker for BOTH corners and direct FKs
notable = []
dual = players[(players["corners_and_indirect_freekicks_order"] == 1) &
               (players["direct_freekicks_order"] == 1)]
for _, r in dual.iterrows():
    notable.append({"name": r["web_name"], "team": teams.get(r["team"], "?"),
                    "roles": "corners + direct free kicks"})
notable.sort(key=lambda x: x["team"])

payload = {
    "meta": {
        "latest": latest_label,
        "penalties_excluded": True,
        "corners_source": "football-data.co.uk (English Premier League match data)",
        "takers_source": "Official Fantasy Premier League set-piece taker orders (2025/26)",
        "note": "Corners are open-play set pieces (no penalties). Set-piece TAKERS are designated corner / direct-free-kick takers, not confirmed scorers. Player-level goals-from-set-pieces was not available from a reliable free source and is not shown.",
    },
    "league": league,
    "teams_latest": team_latest_rows,
    "takers": taker_rows,
    "notable_takers": notable,
}
with open(os.path.join(DOCS, "setpieces.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

# ---- Console summary --------------------------------------------------------
print(f"League corners per match (both teams):")
for r in league:
    print(f"  {r['season']}: {r['corners_pg']}")
print(f"\n{latest_label} — most corners WON per game (attacking set-piece volume):")
for r in team_latest_rows[:6]:
    print(f"  {r['team']:<15} {r['for_pg']} won/gm | {r['against_pg']} conceded/gm | net {r['net_pg']:+}")
print(f"\n{latest_label} — most corners CONCEDED per game (defensive set-piece exposure):")
for r in sorted(team_latest_rows, key=lambda x: x['against_pg'], reverse=True)[:5]:
    print(f"  {r['team']:<15} {r['against_pg']} conceded/gm")
print(f"\nNotable dual set-piece takers (corners + direct FKs):")
for r in notable:
    print(f"  {r['name']:<14} {r['team']}")
print(f"\nSample taker rows:")
for r in taker_rows[:5]:
    print(f"  {r['team']:<15} corners: {r['corner_taker']}  | FK: {r['fk_taker']}")
print("\nWrote docs/setpieces.json")
