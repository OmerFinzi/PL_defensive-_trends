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
Match-results-derived defensive metrics: clean sheets (home/away/total), goals conceded per game, goals per game, home-advantage splits, BTTS rate, season-third (early/mid/late) patterns, per-team defensive tables and multi-season trends.

## What it CANNOT support (be honest — do not fabricate)
Player-level FPL stats: individual defensive contributions (tackles/CBIT), the new 25/26 defensive-contribution points, minutes, prices, ownership, xG/xGA. Those need the official FPL API or an xG provider — out of scope for this results-only dataset. Say so rather than inventing numbers.

## Adding a season
1. Download `epl-<YEAR>.csv` into `data/`.
2. It concatenates automatically — the pipeline globs `data/epl-*.csv`. No code change needed.
