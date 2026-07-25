---
name: fpl-def-data
description: How to source and load the Premier League match-results data for the PL defensive-trends project. Use whenever adding a new season, refreshing data, or reasoning about what the dataset can/can't support.
---

# FPL Defensive-Trends — Data Source

## Source of truth
All season data comes from **fixturedownload.com** — one CSV per season, identical schema every year. This is the project's single reliable, reproducible source. Do not mix in other providers (keeps seasons comparable).

Download URL pattern (needs a browser User-Agent header; the site 403s bare bots):
```
https://fixturedownload.com/download/epl-<YEAR>-GMTStandardTime.csv
```
`<YEAR>` is the season's starting year: `epl-2025` = the 2025/26 season.

PowerShell fetch:
```powershell
Invoke-WebRequest -Uri "https://fixturedownload.com/download/epl-2025-GMTStandardTime.csv" `
  -OutFile "data/epl-2025.csv" `
  -Headers @{ "User-Agent"="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36" }
```

## Schema (every season)
`Match Number, Round Number, Date, Location, Home Team, Away Team, Result`
- `Result` is `"H - A"` (e.g. `"4 - 2"`); split on `" - "` into Home/Away goals.
- `Round Number` 1–38; a full season = 380 rows.
- `season` is derived = the starting year (2025 → labelled "2025/26" for display).

## What this data CAN support
Match-results-derived defensive metrics: clean sheets (home/away/total), goals conceded per game, goals per game, home-advantage splits, BTTS rate, season-third (early/mid/late) patterns, per-team defensive tables and multi-season trends. Pipeline: `analyze.py`.

## Player-level DefCon data — a SECOND, separate source
The 2025/26 **Defensive Contribution (DefCon)** section is player-level and does NOT come from the results CSVs. It comes from the **official FPL stats**, via the community archive **vaastav/Fantasy-Premier-League** (`data/2025-26/`): `players_raw.csv`, `teams.csv`, `merged_gw.csv`, staged under `data/fpl_2025_26/`. Pipeline: `defcon.py` -> `docs/defcon.json`.

Important gotcha: the **live FPL API cannot supply last season's DefCon** — after the season it resets to the new campaign (0 gameweeks played, all stats zeroed). Use the archive for a completed season; the live API (`bootstrap-static`) only works mid-season.

DefCon points rule (2025/26): +2 in a match when defensive contributions reach the threshold — **DEF: >= 10** (clearances+blocks+interceptions+tackles); **MID/FWD: >= 12** (that total plus recoveries). GKs excluded. The `defensive_contribution` field is already position-correct (DEF excludes recoveries; MID/FWD includes them).

## Set-piece data — a THIRD source (corners) + FPL takers
The Set Pieces section (`setpieces.py` -> `docs/setpieces.json`) uses two things, **penalties excluded**:
- **Corners for/against** per team and league (attacking vs defensive set-piece volume) from **football-data.co.uk** — `https://www.football-data.co.uk/mmz4281/<code>/E0.csv` (season code: `2526` = 2025/26, `2021` = 2020/21, etc.; needs a browser UA). Columns `HC`/`AC` are home/away corners. Staged under `data/football_data/E0_<startyear>.csv`. Team names differ slightly — map `Man United`->`Man Utd`, `Tottenham`->`Spurs`.
- **Set-piece takers** (corners + direct free kicks, NOT penalties) from the official FPL orders already in `players_raw.csv` (`corners_and_indirect_freekicks_order`, `direct_freekicks_order`; order==1 is the primary taker).

### Set-piece GOALS (scored/conceded) — `fetch_setpiece_goals.py`
Goals-by-situation (from corner / set piece / direct free kick) come from **Understat**, the reliable free source. `fetch_setpiece_goals.py` scrapes the 20 club pages, sums the three set-piece situations (penalties excluded) for & against, and writes `docs/setpieces_goals.json` (goals, set-piece shots, xG, and efficiency = SP shots per goal). The dashboard shows a "Set-piece goals" block **only when that JSON exists**.

**Hard gotcha — the build environment is IP-blocked.** Understat serves a data-stripped page (no `statisticsData`) to datacenter/flagged IPs, and FBref (403), Sofascore (403), FotMob, and every public proxy/reader tried (jina, allorigins, codetabs, corsproxy) are blocked too. The worldfootballR GitHub mirror is stale (Understat complete only to 2023/24). So this script **must be run from a normal home/office network** — then it works (it detects the stripped page and errors clearly otherwise). Do NOT fabricate set-piece goals when it can't fetch; the data is simply pending a run from an unblocked network.

## Still out of scope (be honest — do not fabricate)
Other player metrics not in any source here: xG/xGA, ownership %, expected defensive stats, and goal-level set-piece breakdowns. Don't invent them.

## Adding a season
1. Download `epl-<YEAR>.csv` into `data/`.
2. It concatenates automatically — the pipeline globs `data/epl-*.csv`. No code change needed.
