# Premier League Defensive Trends — 2020/21 → 2025/26

A six-season study of **defensive performance in the English Premier League**, built for Fantasy Premier League (FPL) decision-making: clean sheets, goals conceded, home/away splits, and where the best defensive value sits going into and through **2025/26**.

> **Now updated for the 2025/26 season.** All 380 matches of 2025/26 are included.

**➡️ [Open the interactive dashboard](https://omerfinzi.github.io/PL_defensive-_trends/)** &nbsp;·&nbsp; [Read the findings report](REPORT.md)

![Dashboard preview](docs/preview.png)

---

## Headline findings (2025/26)

- **Defences are recovering.** After the record goal-glut of 2023/24 (3.28 goals/game, 62% both-teams-to-score), scoring has fallen two seasons running. **2025/26 is the meanest season for goals since 2020/21** — 2.75 goals/game and clean sheets back up to 0.51 per game.
- **Arsenal are the defence to own** — a **50% clean-sheet rate** and just **0.71 goals conceded per game**, the best single-season defensive return in the six-year window. Man City are second (42% CS, 0.92 conceded/gm); after that there's a steep drop-off.
- **Home advantage is back.** The behind-closed-doors era of 2020/21–2021/22 flattened the home edge; it has since recovered — home clean-sheet rate is again clearly above away.
- **Momentum matters.** Biggest defensive *improvers* vs 2024/25: **Brighton (−0.34 conceded/gm)**, Man City, Spurs, Arsenal. Biggest *declines*: **Liverpool (+0.32)**, Chelsea, Newcastle.
- **Promoted-side watch.** **Sunderland** were a genuine defensive surprise (29% CS, 1.26 conceded/gm); Leeds (21%) held up moderately; Burnley struggled (11% CS, 1.97 conceded/gm).

Full numbers and charts are in the [dashboard](https://omerfinzi.github.io/PL_defensive-_trends/) and [REPORT.md](REPORT.md).

---

## What's in the repo

```
data/                 six season CSVs (epl-2020.csv … epl-2025.csv)
analyze.py            analysis pipeline → docs/data.json + outputs/
build_dashboard.py    builds the self-contained docs/index.html
docs/index.html       the interactive dashboard (GitHub Pages entry point)
docs/data.json        computed metrics consumed by the dashboard
outputs/              team_season_defence.csv (tidy per-team-per-season table)
REPORT.md             written findings report
.claude/skills/       project skill describing the data source
```

## Reproduce it

Requires Python 3 with `pandas` and `numpy`.

```bash
pip install pandas numpy
python analyze.py          # rebuilds docs/data.json and outputs/
python build_dashboard.py  # rebuilds docs/index.html from data.json
```

Open `docs/index.html` in any browser — it is fully self-contained (data embedded inline, **zero external requests**, works offline and on GitHub Pages).

## Data source

All season data comes from **[fixturedownload.com](https://fixturedownload.com)** — one results CSV per season, identical schema every year, so seasons stay directly comparable. To add a future season, drop `epl-<startyear>.csv` into `data/` and re-run the two scripts (the pipeline globs `data/epl-*.csv`). See [`.claude/skills/fpl-def-data`](.claude/skills/fpl-def-data/SKILL.md).

## Method & scope

- A **clean sheet** is credited to a team that concedes zero goals in a match. `CS rate` = clean sheets ÷ matches played.
- League metrics count **both teams per match**; team tables split home and away.
- Season "thirds": Early = GW1–12, Mid = GW13–26, Late = GW27–38.

**Honest scope note:** this project uses **match results only**. Player-level FPL data — the new 2025/26 *defensive-contribution* points, tackles/CBIT, minutes, prices, ownership, xG/xGA — is **not** included, because it isn't in the results feed. Those need the official FPL API or an xG provider and are out of scope here. No such numbers are estimated or invented anywhere in this project.

---

*Analysis by [@omerfin7](https://github.com/OmerFinzi). Refreshed for 2025/26.*
