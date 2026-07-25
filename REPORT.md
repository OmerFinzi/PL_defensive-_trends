# Premier League Defensive Trends — Findings Report

**Window:** 2020/21 → 2025/26 (six completed seasons, 2,280 matches)
**Source:** [fixturedownload.com](https://fixturedownload.com) EPL results · match-results only
**Updated:** for the 2025/26 season

---

## 1. The six-season arc: defence is winning ground back

| Season | Goals / game | Clean sheets / game | BTTS rate |
|--------|:---:|:---:|:---:|
| 2020/21 | 2.69 | 0.59 | 49% |
| 2021/22 | 2.82 | 0.56 | 50% |
| 2022/23 | 2.85 | 0.55 | 52% |
| 2023/24 | **3.28** | **0.41** | **62%** |
| 2024/25 | 2.93 | 0.47 | 57% |
| **2025/26** | **2.75** | **0.51** | 56% |

The story is a spike and a reversal. **2023/24 was the peak of an attacking era** — the most goals per game and the fewest clean sheets in the window, with nearly two in three matches seeing both teams score. Since then scoring has fallen for two straight seasons, and **2025/26 is the lowest-scoring season since 2020/21** at 2.75 goals/game, with clean sheets recovering to 0.51 per game.

Across the whole window the clean-sheet trend is still gently **negative** (≈ −0.023 clean sheets/game per season), so this is a *recovery within a longer attacking drift* rather than a return to low-scoring football. For FPL that argues for treating premium defensive assets as more viable in 2025/26 than in the 2023/24 chaos — but with selectivity, not a blanket "load up on defenders."

## 2. Who to trust at the back in 2025/26

Top defences by clean-sheet rate:

| # | Team | CS rate | Conceded/gm | Home CS | Away CS |
|---|------|:---:|:---:|:---:|:---:|
| 1 | **Arsenal** | 50% | 0.71 | 58% | 42% |
| 2 | **Man City** | 42% | 0.92 | 47% | 37% |
| 3 | Crystal Palace | 32% | 1.34 | 37% | 26% |
| 4 | Bournemouth | 29% | 1.42 | 32% | 26% |
| 5 | Sunderland | 29% | 1.26 | 37% | 21% |
| 6 | Everton | 29% | 1.32 | 32% | 26% |

**Arsenal are in a tier of their own** — a 50% clean-sheet rate and 0.71 goals conceded per game is the single best defensive season in the six-year window. Man City are the only other side clearing a 40% clean-sheet rate. After the top two there is a **sharp cliff**: the third-best defence (Crystal Palace) is already down at 32% and conceding roughly one-and-a-third per game. The practical FPL read: the two "set-and-forget" defensive sources are Arsenal and City; everyone else is a rotation/fixture play, not a season-long lock.

## 3. Home advantage is back

Home clean-sheet rate versus away clean-sheet rate, by season, shows the **behind-closed-doors dip and recovery** clearly. In 2020/21–2021/22 (crowds absent or reduced) the home defensive edge was muted; it has since widened again, and the home-minus-away points-per-game gap trends **positive** over the window (≈ +0.05 PPG per season). Home fixtures remain the higher-probability clean-sheet bet — a durable, exploitable pattern for timing defensive picks.

## 4. Momentum: who tightened up, who fell apart

Change in goals conceded per game, **2025/26 vs 2024/25**:

**Biggest improvers** (conceding fewer)
- Brighton −0.34 · Man City −0.24 · Spurs −0.21 · Arsenal −0.18 · Brentford −0.13

**Biggest declines** (leaking more)
- Liverpool +0.32 · Chelsea +0.24 · Newcastle +0.21 · Bournemouth +0.21 · Everton +0.16

Momentum is an FPL edge because it front-runs price and template moves. Brighton's sharp tightening and Spurs' improvement are the kind of under-owned defensive stories worth acting on early; **Liverpool's step back** is the most notable decline among the traditional big sides.

## 5. When clean sheets come

Averaging clean sheets per game by third of the season (Early GW1–12, Mid GW13–26, Late GW27–38) shows only mild variation across the campaign — there is no single "defensive window" that dominates. The bigger lever for timing defensive investment is **fixtures and home/away** (Sections 2–3) rather than the calendar third.

## 6. Promoted sides

| Team | CS rate | Conceded/gm | Clean sheets |
|------|:---:|:---:|:---:|
| Sunderland | 29% | 1.26 | 11 / 38 |
| Leeds | 21% | 1.47 | 8 / 38 |
| Burnley | 11% | 1.97 | 4 / 38 |

**Sunderland were the standout newcomer defensively** — a 29% clean-sheet rate put them level with established mid-table sides and made their cheap defenders genuine early-season value. Leeds were serviceable; Burnley leaked heavily (nearly two per game) and were an FPL defensive avoid.

---

## Scope & honesty

This report is built **only** from match results. It deliberately does **not** cover player-level FPL metrics — the 2025/26 defensive-contribution points, tackles/CBIT, minutes, prices, ownership, or xG/xGA — because those are not in the results feed. Every number above is computed directly from the six season CSVs by [`analyze.py`](analyze.py); nothing is estimated or imported from third-party projections.

*Analysis by [@omerfin7](https://github.com/OmerFinzi).*
