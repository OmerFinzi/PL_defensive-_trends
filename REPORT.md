# Premier League Defensive Trends — Findings Report

**Window:** 2020/21 → 2025/26 (six completed seasons, 2,280 matches)
**Sources:** [fixturedownload.com](https://fixturedownload.com) EPL results (§1–7) · official FPL stats via the [vaastav archive](https://github.com/vaastav/Fantasy-Premier-League) for 2025/26 DefCon (§8) · [football-data.co.uk](https://www.football-data.co.uk) corners + official FPL set-piece orders (§9)
**Updated:** for the 2025/26 season

---

## 1. The six-season arc: defence is winning ground back

| Season | Goals / game | Clean sheets / game | BTTS rate |
|--------|:---:|:---:|:---:|
| 2020/21 | 2.69 | 0.59 | 49% |
| 2021/22 | 2.82 | 0.56 | 50% |
| 2022/23 | 2.85 | 0.54 | 52% |
| 2023/24 | **3.28** | **0.41** | **62%** |
| 2024/25 | 2.93 | 0.47 | 57% |
| **2025/26** | **2.75** | **0.51** | 56% |

The story is a spike and a reversal. **2023/24 was the peak of an attacking era** — the most goals per game and the fewest clean sheets in the window, with nearly two in three matches seeing both teams score. Since then scoring has fallen for two straight seasons, and **2025/26 is the lowest-scoring season since 2020/21** at 2.75 goals/game, with clean sheets recovering to 0.51 per game.

Across the whole window the clean-sheet trend is still gently **negative** (≈ −0.023 clean sheets/game per season), so this is a *recovery within a longer attacking drift* rather than a return to low-scoring football. For FPL that argues for treating premium defensive assets as more viable in 2025/26 than in the 2023/24 chaos — but with selectivity, not a blanket "load up on defenders."

## 2. How many goals in a match? Poisson, not a bell curve

Averages hide shape. Across all 2,280 matches the mean is **2.89 goals** with an SD of 1.68 — but goals per match are a **count**: discrete, never negative, and skewed right. The distribution most people picture is the normal curve; the correct one is **Poisson**, and the difference is not academic.

The evidence is direct. Poisson's defining property is that variance equals mean, and here the **variance-to-mean ratio is 0.98** against a predicted 1.00. Skewness is **+0.53**, where a normal distribution requires 0. Fitting both by chi-square, pooled over all six seasons:

| Fit | χ² (df) | p | Verdict |
|---|:---:|:---:|---|
| Normal (Gaussian) | 62.6 (6) | <0.001 | decisively rejected |
| **Poisson** | **2.4 (7)** | **0.936** | consistent with the data |

Two visible failures of the bell curve. It puts **2.19% of its probability mass below zero goals** — about 50 impossible matches across the window — which Poisson cannot do by construction. And it misallocates in the middle: it predicts 12.7% of matches finishing with exactly one goal when 15.6% actually do, while over-predicting 3–4 goal games.

**Per season** (each fitted separately; p-values are what make the two models comparable, since tail-pooling leaves them with different degrees of freedom):

| Season | Matches | Mean | SD | Var/mean | Normal χ² (df) | p | Poisson χ² (df) | p | Better |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 2020/21 | 380 | 2.69 | 1.76 | 1.14 | 30.1 (5) | <0.001 | 10.5 (6) | 0.105 | Poisson |
| 2021/22 | 380 | 2.82 | 1.63 | 0.94 | 8.7 (4) | 0.069 | 6.0 (6) | 0.426 | Poisson |
| 2022/23 | 380 | 2.85 | 1.79 | 1.12 | 21.6 (5) | <0.001 | 4.8 (6) | 0.565 | Poisson |
| 2023/24 | 380 | 3.28 | 1.66 | 0.84 | 6.4 (5) | 0.267 | 6.2 (7) | 0.519 | Poisson |
| 2024/25 | 380 | 2.93 | 1.62 | 0.89 | 11.7 (5) | 0.039 | 4.0 (6) | 0.679 | Poisson |
| **2025/26** | 380 | 2.75 | 1.57 | 0.90 | 4.2 (4) | 0.374 | 8.9 (6) | 0.178 | *normal* |

Poisson fits better in five of six seasons, and is never *rejected* in any of them. But note the honest exception: **in 2025/26 alone the normal curve fits slightly better** (p 0.374 vs 0.178). That is not evidence the model changed — a single season is only 380 matches, which has little power to separate two similar-looking distributions, and 2025/26 is the least dispersed season in the window (SD 1.57). It is exactly the kind of result that would be over-read if the pooled fit weren't there to anchor it. The stable reading is the pooled one, where 2,280 matches make the verdict emphatic.

**Why this matters for FPL.** If goals conceded follow a Poisson process with mean λ, then a clean sheet is just P(0) = e^−λ — so a team's clean-sheet rate is predictable from its goals-conceded average alone, with nothing else fitted. Tested against all 120 team-seasons in this window, that predicts clean-sheet rate to within **3.7 percentage points** on average (correlation 0.902, bias −0.6pp). Arsenal conceded 0.71 per game in 2025/26, which implies a 49.1% clean-sheet rate; they actually recorded 50.0%. This is the practical payoff: you do not need a clean-sheet model, only a goals-conceded estimate, and the conversion is one exponential.

### Most common scorelines

46 distinct scorelines were actually recorded. The top of the list, in **home–away** order:

| Scoreline | Matches | Share | | Scoreline | Matches | Share |
|---|:---:|:---:|---|---|:---:|:---:|
| **1–1** | 250 | **10.96%** | | 2–2 | 131 | 5.75% |
| 1–0 | 189 | 8.29% | | 0–0 | 129 | 5.66% |
| 2–1 | 187 | 8.20% | | 0–2 | 126 | 5.53% |
| 0–1 | 167 | 7.32% | | 3–1 | 111 | 4.87% |
| 1–2 | 159 | 6.97% | | 3–0 | 103 | 4.52% |
| 2–0 | 154 | 6.75% | | 1–3 | 71 | 3.11% |

**1–1 is the single most likely result in a Premier League match**, at nearly 11% — and it was the modal scoreline in five of the six seasons (2022/23 was the exception, when 1–0 led on 12.1%). Note that only about one match in eighteen is a 0–0.

Orientation is deliberate: scorelines are kept home–away rather than collapsed by margin, because **the gap between a result and its mirror image *is* home advantage**. Every mirrored pair leans home: 1–0 occurred 189 times against 167 for 0–1, 2–1 187 times against 159 for 1–2, and 2–0 154 times against 126 for 0–2. Collapsing them into "1-goal win" would erase the effect entirely.

## 3. Who to trust at the back in 2025/26

Top defences by clean-sheet rate:

| # | Team | CS rate | Conceded/gm | Home CS | Away CS |
|---|------|:---:|:---:|:---:|:---:|
| 1 | **Arsenal** | 50% | 0.71 | 58% | 42% |
| 2 | **Man City** | 42% | 0.92 | 47% | 37% |
| 3 | Crystal Palace | 32% | 1.34 | 37% | 26% |
| 4 | Bournemouth | 29% | 1.42 | 32% | 26% |
| 5 | Sunderland | 29% | 1.26 | 37% | 21% |
| 6 | Everton | 29% | 1.32 | 32% | 26% |

**Arsenal are in a tier of their own** — a 50% clean-sheet rate and 0.71 goals conceded per game is the best defensive season **since 2021/22**, though not the best of the window: Man City and Liverpool both managed 21 clean sheets (55%) at 0.68 conceded that year, so Arsenal's 2025/26 ranks third of the 120 team-seasons here. Man City are the only other side clearing a 40% clean-sheet rate this season. After the top two there is a **sharp cliff**: the third-best defence (Crystal Palace) is already down at 32% and conceding roughly one-and-a-third per game. The practical FPL read: the two "set-and-forget" defensive sources are Arsenal and City; everyone else is a rotation/fixture play, not a season-long lock.

## 4. The home clean-sheet edge: real, but not a trend

Two different things get called "home advantage" here, and they behave differently — worth separating, because conflating them overstates the case.

Measured in **points per game**, the home-minus-away gap does trend **positive** across the window (≈ +0.05 PPG per season), and 2020/21 — the behind-closed-doors season — is the one year it went *negative* (−0.07). That is a genuine, well-known crowd effect.

Measured in **clean sheets**, which is what this project actually plots, there is no such trend. The home-minus-away clean-sheet gap by season runs +0.005, +0.068, +0.113, +0.055, **−0.011**, +0.058 — a slope of essentially zero (−0.0009 per season). It was near-flat in 2020/21, peaked in 2022/23, and **inverted in 2024/25**, when away sides kept marginally more clean sheets than home sides. Note also that only 2020/21 was played behind closed doors; crowds were back for 2021/22, which had a *larger* home clean-sheet edge than 2025/26 does.

So the honest read: home fixtures are the better clean-sheet bet in 2025/26 (28% vs 23%), and in five of six seasons overall — but this is a modest, noisy edge that reversed as recently as last season, not a durable pattern to lean on hard. Use it as a tiebreak between similar defensive assets, not as a primary signal.

## 5. Momentum: who tightened up, who fell apart

Change in goals conceded per game, **2025/26 vs 2024/25**:

**Biggest improvers** (conceding fewer)
- Brighton −0.34 · Man City −0.24 · Spurs −0.21 · Arsenal −0.18 · Brentford −0.13

**Biggest declines** (leaking more)
- Liverpool +0.32 · Chelsea +0.24 · Newcastle +0.21 · Bournemouth +0.21 · Everton +0.16

Momentum is an FPL edge because it front-runs price and template moves. Brighton's sharp tightening and Spurs' improvement are the kind of under-owned defensive stories worth acting on early; **Liverpool's step back** is the most notable decline among the traditional big sides.

## 6. When clean sheets come

Averaging clean sheets per game by third of the season (Early GW1–12, Mid GW13–26, Late GW27–38) shows only mild variation across the campaign — there is no single "defensive window" that dominates. The bigger lever for timing defensive investment is **fixtures and home/away** (Sections 3–4) rather than the calendar third.

## 7. Promoted sides

| Team | CS rate | Conceded/gm | Clean sheets |
|------|:---:|:---:|:---:|
| Sunderland | 29% | 1.26 | 11 / 38 |
| Leeds | 21% | 1.47 | 8 / 38 |
| Burnley | 11% | 1.97 | 4 / 38 |

**Sunderland were the standout newcomer defensively** — a 29% clean-sheet rate put them level with established mid-table sides and made their cheap defenders genuine early-season value. Leeds were serviceable; Burnley leaked heavily (nearly two per game) and were an FPL defensive avoid.

## 8. DefCon — the new 2025/26 defensive-points metric (player-level)

*Source note: this section is player-level and comes from a **different source** to the sections above — official FPL season-end stats via the vaastav archive, not the results feed. A player banks +2 in a match when defensive contributions reach the threshold (DEF ≥ 10 CBIT; MID/FWD ≥ 12 including recoveries). GKs excluded.*

**Top DefCon points banked (2025/26):**

| # | Player | Team | Pos | DefCon pts | Threshold hits | DC/90 | Price |
|---|--------|------|-----|:---:|:---:|:---:|:---:|
| 1 | Elliot Anderson | NFO | MID | 52 | 26 | 13.9 | £5.7m |
| 1 | Marcos Senesi | BOU | DEF | 52 | 26 | 11.5 | £5.2m |
| 3 | James Tarkowski | EVE | DEF | 44 | 22 | 10.2 | £5.8m |
| 4 | James Garner | EVE | MID | 40 | 20 | 12.1 | £5.2m |
| 4 | Maxence Lacroix | CRY | DEF | 40 | 20 | 10.8 | £5.2m |
| 4 | Joachim Andersen | FUL | DEF | 40 | 20 | 10.3 | £4.4m |

**By position:** defenders banked **1,642** DefCon points (141 returning players) versus midfielders' **1,174** (118 players); forwards were negligible (18 points). DefCon is overwhelmingly a defender-and-holding-midfielder mechanic.

**Hardest-working defensive squads** (total DefCon points across the club): **Everton (206), Bournemouth (190), Burnley (174), Leeds (164), West Ham (162)**. Note the pattern — several are mid/lower-table or promoted sides that defend more and therefore rack up defensive actions. High DefCon volume is *not* the same as an elite defence (Burnley leaked the most goals in the league yet ranked third for DefCon points).

**Best budget value** (DefCon points per £m, enablers ≤ £5.5m): **Maxime Estève (BUR, £3.8m)** and **Senesi** lead at ~10 points/£m, with **Andersen (FUL, £4.4m)** close behind — cheap, nailed defensive-contribution sources.

**FPL takeaway:** DefCon rewards a distinct player profile from clean sheets. The elite-defence pick (Arsenal/City assets) chases clean-sheet points; the DefCon pick chases *volume of defensive actions*, which favours ball-winning defenders and holding midfielders at busy, deeper-defending clubs — often much cheaper. A balanced squad can target both.

## 9. Set pieces — corners & free kicks (penalties excluded)

*Source note: corner counts (for & against) come from [football-data.co.uk](https://www.football-data.co.uk) match data; designated set-piece takers come from the official FPL set-piece orders. **Penalties are excluded** at the user's request. Corners are used as the reliable, open-play set-piece **volume** measure.*

**League-wide corners have been remarkably stable** — around 10 per match across all six seasons (10.2 in 2020/21, a 10.8 peak in 2023/24, back to 10.0 in 2025/26). Set-piece *volume* isn't where the league has changed; the defensive shifts in §1 are about conversion and clean sheets, not corner counts.

**Attacking set-piece volume — most corners won per game (2025/26):**

| Team | Won/gm | Conceded/gm | Net/gm |
|------|:---:|:---:|:---:|
| Man City | 6.5 | 3.8 | **+2.7** |
| Liverpool | 6.1 | 4.4 | +1.7 |
| Chelsea | 6.1 | 4.3 | +1.8 |
| Newcastle | 6.1 | 4.9 | +1.2 |
| Arsenal | 5.7 | 3.4 | **+2.3** |

The corner-winning leaders are the possession/attacking sides. On **net** corners (won − conceded), **Man City (+2.7)** and **Arsenal (+2.3)** dominate — they generate set-piece pressure *and* concede little of it.

**Defensive set-piece exposure — most corners conceded per game:** **West Ham (6.1)**, **Burnley (6.0)**, **Wolves (6.0)** — the sides camped in their own third, defending the most set pieces.

**Notable set-piece takers** (designated for *both* corners and direct free kicks in 2025/26): **Rice (Arsenal)**, **Ward-Prowse (Burnley)**, **Reece James (Chelsea)**, **Wilson (Fulham)**, **Stach (Leeds)**, **Bruno Fernandes (Man Utd)**, **Xhaka (Sunderland)**, **Bowen (West Ham)**. These dual-duty takers are a club's set-piece hubs — useful FPL context, since concentrated set-piece responsibility drives assist potential.

**Set-piece goals scored & conceded, 2025/26 (source: [Understat](https://understat.com)).** Goals from corners + set pieces + direct free kicks (penalties excluded):

| # | Most goals SCORED | GF | SP shots | Shots/goal | | Most goals CONCEDED | GA |
|---|---|:---:|:---:|:---:|---|---|:---:|
| 1 | **Arsenal** | **23** | 158 | **6.9** | | **Bournemouth** | **18** |
| 2 | Man Utd | 20 | 142 | 7.1 | | West Ham | 16 |
| 3 | Spurs | 18 | 135 | 7.5 | | Leeds *(3=)* | 15 |
| 4 | Aston Villa | 17 | 134 | 7.9 | | Crystal Palace *(3=)* | 15 |
| 5= | West Ham | 15 | 111 | 7.4 | | Liverpool *(5=)* | 14 |
| 5= | Liverpool | 15 | 126 | 8.4 | | Nott'm Forest, Newcastle *(5=)* | 14 |

Ranks on both sides carry `=` where clubs are level. Note West Ham appear on both sides — joint-fifth for set-piece goals scored *and* second-most conceded.

League-wide: **243 set-piece goals from 2,481 set-piece shots** (~10.2 shots per goal on average).

**Arsenal are the most prolific set-piece side** — 23 goals, three clear of Man Utd's 20 — and also top the efficiency table at 6.9 shots per goal. But the efficiency lead is not the story the raw ordering suggests: Man Utd are at 7.1, a 3% gap, and the two clubs' 95% confidence intervals ([4.6, 10.8] and [4.6, 11.6]) overlap almost entirely. On a season's worth of set-piece goals, **Arsenal and Man Utd are statistically indistinguishable on efficiency**; the honest claim is volume, not clinical finishing.

The genuinely large gaps are at the bottom. **Brentford and Burnley manage only 4 set-piece goals each**, needing 24–26 shots per goal — roughly **3.5× less efficient** than Arsenal, a difference wide enough to survive the uncertainty. And efficiency clearly diverges from volume: Newcastle and Man City generate plenty of set-piece shots (158 and 141) but convert poorly (12.2 and 12.8 shots/goal), suggesting delivery quality matters more than sheer quantity.

On the defensive side, **Bournemouth's 18 conceded** stands out as a genuine defensive-set-piece weakness — worth cross-referencing against their overall clean-sheet numbers in §3. The fewest conceded is **Brentford with 6**, with Arsenal next on 7. Arsenal's set-piece defence is best understood as **volume suppression rather than resistance**: they face by far the fewest set-piece shots in the league (71), but once a shot comes their per-shot resistance is only mid-table — 10.1 shots needed per goal conceded ranks 10th of 20.

**Efficiency, every team — set-piece shots needed per goal (lower = better):**

Both halves read top-to-bottom in one sequence, ranked best-to-worst attacking efficiency (columns 1–3 are places 1–10, columns 4–6 places 11–20):

| Team | To score | To concede | | Team | To score | To concede |
|---|:---:|:---:|---|---|:---:|:---:|
| Arsenal | **6.9** | 10.1 | | Leeds | 11.1 | 9.6 |
| Man Utd | 7.1 | 9.2 | | Brighton | 11.7 | 12.7 |
| West Ham | 7.4 | 10.1 | | Newcastle | 12.2 | **6.8** |
| Spurs | 7.5 | 15.3 | | Everton | 12.7 | 14.4 |
| Aston Villa | 7.9 | 9.1 | | Man City | 12.8 | 7.7 |
| Liverpool | 8.4 | 8.3 | | Wolves | 14.0 | 12.8 |
| Chelsea | 8.9 | 8.2 | | Crystal Palace | 14.1 | 8.8 |
| Bournemouth | 9.2 | 8.3 | | Sunderland | 14.7 | 10.7 |
| Fulham | 10.6 | 11.6 | | Burnley | 24.5 | 11.5 |
| Nott'm Forest | 10.6 | 10.4 | | Brentford | **26.0** | **18.7** |

Bold marks the league extremes: best and worst "to score" (Arsenal 6.9, Brentford 26.0), and the two ends of "to concede" — Brentford's league-high 18.7 (hardest to breach) and Newcastle's league-low 6.8 (easiest).

Two things worth calling out beyond the volume numbers — remember **higher "to concede" is better** (more shots needed before opponents score). **Brentford have the league's most resistant set-piece defence by this measure**: opponents need **18.7 shots** to score against them, the division's highest, and this is the rare efficiency claim that is corroborated rather than isolated — Brentford also concede the fewest set-piece goals outright (6). Their attack is the opposite story — **worst in the league at 26.0 shots per goal scored** — so Brentford pair a resistant set-piece defence with almost no set-piece threat going forward.

**Newcastle sit at the other extreme**: despite a mid-table set-piece attack (12.2 shots/goal), they concede a set-piece goal every **6.8 shots faced**, the league low. One caveat on how to read that: the ratio is driven as much by Newcastle facing *few* set-piece shots (95, the third-fewest after Arsenal and Man City) as by conceding many — their 14 goals conceded is tied 5th–7th-most in the league (with Liverpool and Nott'm Forest) against a median of 13 — worse than average, but not among the leakiest. With 14 goals the 95% interval is [4.0, 12.4], which overlaps much of the division, so treat this as a soft flag rather than a firm ranking. Directionally it still points the right way: Newcastle's dead-ball defending converts one of the league's *lowest* volumes of chances faced into a slightly *above*-median number of goals, which is the signature of poor per-shot resistance.

*Reliability note: Understat blocks automated/datacenter requests (as do FBref, Sofascore and FotMob), so [`fetch_setpiece_goals.py`](fetch_setpiece_goals.py) has to be run from an ordinary home/office connection — from a flagged IP it silently returns a data-stripped page. That makes this the one input in the project that cannot be re-derived from a file committed to the repo; rerun the script to reproduce `docs/setpieces_goals.json`. The numbers themselves are Understat's; nothing is estimated.*

---

## Scope & honesty

Sections 1–6 are built **only** from match results (`analyze.py`). Section 7 (DefCon) is **player-level** from the official-FPL vaastav archive (`defcon.py`); the live FPL API can't supply a completed season's DefCon (it resets each summer), so the archive is used. Section 8 (set pieces) uses football-data.co.uk corners and official FPL set-piece orders (`setpieces.py`), plus Understat goals-by-situation (`fetch_setpiece_goals.py`, `setpieces_goals_stats.py`), with **penalties excluded** throughout. Every number is computed directly from those files; nothing is estimated or imported from third-party projections.

Known limits, stated plainly:

- **No set-piece scorer attribution.** Set-piece goals are **club totals** from Understat shot data; set-piece *takers* come from FPL's designated-taker orders. The two are never joined, so this report does not claim who scored a given set-piece goal.
- **The Understat pull is the one non-reproducible input** from files committed here — rerun `fetch_setpiece_goals.py` from a normal network connection to regenerate it.
- **Efficiency ratios on single-digit goal counts are noisy.** Every shots-per-goal figure carries a 95% Byar Poisson interval; where intervals overlap, treat the clubs as tied rather than ranked. Several plausible-looking gaps in §9 do not survive this test, and the text says so where that applies.
- **Cross-position defensive-action comparisons need care** — see the DefCon note in §8 and the README method section. The positions differ on both which actions count and what threshold they must clear.
- Out of scope: **player-level** xG/xGA and ownership. Club-level set-piece xG *is* included.

*Analysis by [@omerfin7](https://github.com/OmerFinzi).*
