"""
Recompute set-piece efficiency ratios in docs/setpieces_goals.json to 2dp and
add 95% confidence intervals on them.

Why: shots_per_goal_for/against = shots / goals, and goals is the small,
noisy term (single digits to teens over a season) — the ratio's precision is
bounded by the goal COUNT, not by the (much larger, more stable) shot count.
A team with 6 set-piece goals conceded could easily have had 4 or 9 given
normal match-to-match variance, and that swings the ratio a lot.

Uses Byar's approximation for the 95% Poisson confidence interval on a count
(no scipy dependency — this project only requires pandas/numpy). Verified
against exact chi-squared Poisson CIs to ~0.1 agreement.

Idempotent — safe to re-run after refreshing docs/setpieces_goals.json from
a fresh Understat pull (see .claude/skills/fpl-def-data).
"""
import json, math, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(ROOT, "docs", "setpieces_goals.json")


def byar_ci(k, z=1.96):
    if k <= 0:
        return 0.0, (1 - 1 / 9 + z / 3) ** 3
    lo = k * (1 - 1 / (9 * k) - z / (3 * math.sqrt(k))) ** 3
    hi = (k + 1) * (1 - 1 / (9 * (k + 1)) + z / (3 * math.sqrt(k + 1))) ** 3
    return max(0.0, lo), hi


d = json.load(open(PATH, encoding="utf-8"))
for r in d["teams"]:
    r["shots_per_goal_for"] = round(r["sf"] / r["gf"], 2)
    lo, hi = byar_ci(r["gf"])
    r["sp_for_ci_lo"] = round(r["sf"] / hi, 2)
    r["sp_for_ci_hi"] = round(r["sf"] / lo, 2) if lo > 0 else None

    r["shots_per_goal_against"] = round(r["sa"] / r["ga"], 2)
    lo, hi = byar_ci(r["ga"])
    r["sp_against_ci_lo"] = round(r["sa"] / hi, 2)
    r["sp_against_ci_hi"] = round(r["sa"] / lo, 2) if lo > 0 else None

note = ("Set-piece goals = corners + set pieces + direct free kicks (penalties excluded). "
        "Efficiency = set-piece shots per set-piece goal. 95% CIs (Byar's Poisson "
        "approximation on the goal count) show how much a ranking could shift by "
        "chance alone -- treat overlapping intervals as statistically indistinguishable.")
d["meta"]["note"] = note

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2)

print(f"Wrote {PATH}")
print("\nDefensive efficiency ranked, with 95% CI (wide CIs = don't over-read small gaps):")
for r in sorted(d["teams"], key=lambda r: r["shots_per_goal_against"], reverse=True):
    print(f"  {r['team']:<15} to-concede {r['shots_per_goal_against']:>5.2f}  "
          f"95% CI [{r['sp_against_ci_lo']:.2f}, {r['sp_against_ci_hi']:.2f}]  (from {r['ga']} goals)")
