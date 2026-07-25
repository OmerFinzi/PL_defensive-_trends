"""
Set-piece GOALS from Understat (reliable, current) — 2025/26.

WHY THIS IS A SEPARATE, RUN-IT-YOURSELF SCRIPT
Understat is the reliable free source for goals-by-situation (from corner /
set piece / direct free kick). It refuses automated requests from datacenter /
flagged IPs (it serves a data-stripped page). The machine this repo was built
on is on such an IP, and every proxy/reader tried was Cloudflare-blocked too.
Run this from a NORMAL network (a home/office connection) and it works — it
only makes ~20 requests (one per club).

WHAT IT PRODUCES
docs/setpieces_goals.json with, per team, set-piece goals scored & conceded
(corners + set pieces + direct free kicks; PENALTIES EXCLUDED), the set-piece
shots behind them, and efficiency = set-piece shots per goal (attacking and
defensive). Then run `python build_dashboard.py` to show it on the dashboard.

Usage:
    python fetch_setpiece_goals.py            # season 2025/26 (default)
    python fetch_setpiece_goals.py 2024       # a different season start year
"""
import sys, os, re, json, codecs, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
SEASON = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
SET_PIECE = ["FromCorner", "SetPiece", "DirectFreekick"]   # penalties excluded

# Understat URL slug -> the team names used elsewhere in this project
TEAMS = {
    "Arsenal": "Arsenal", "Aston_Villa": "Aston Villa", "Bournemouth": "Bournemouth",
    "Brentford": "Brentford", "Brighton": "Brighton", "Burnley": "Burnley",
    "Chelsea": "Chelsea", "Crystal_Palace": "Crystal Palace", "Everton": "Everton",
    "Fulham": "Fulham", "Leeds": "Leeds", "Liverpool": "Liverpool",
    "Manchester_City": "Man City", "Manchester_United": "Man Utd",
    "Newcastle_United": "Newcastle", "Nottingham_Forest": "Nott'm Forest",
    "Sunderland": "Sunderland", "Tottenham": "Spurs", "West_Ham": "West Ham",
    "Wolverhampton_Wanderers": "Wolves",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
           "Accept": "text/html", "Accept-Language": "en-US,en;q=0.9"}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

def parse_var(html, name):
    """Extract a `var name = JSON.parse('...')` block from an Understat page."""
    m = re.search(name + r"\s*=\s*JSON\.parse\('([^']+)'\)", html)
    if not m:
        return None
    return json.loads(codecs.decode(m.group(1), "unicode_escape"))

def team_setpieces(slug):
    html = fetch(f"https://understat.com/team/{slug}/{SEASON}")
    stats = parse_var(html, "statisticsData")
    if stats is None or "situation" not in stats:
        raise RuntimeError("no statisticsData — likely an IP-blocked/stripped page")
    sit = stats["situation"]
    gf = sf = ga = sa = 0
    xgf = xga = 0.0
    for k in SET_PIECE:
        s = sit.get(k, {})
        gf += int(s.get("goals", 0)); sf += int(s.get("shots", 0)); xgf += float(s.get("xG", 0) or 0)
        ag = s.get("against", {})
        ga += int(ag.get("goals", 0)); sa += int(ag.get("shots", 0)); xga += float(ag.get("xG", 0) or 0)
    return gf, sf, round(xgf, 1), ga, sa, round(xga, 1)

def label(y):  return f"{y}/{str(y + 1)[-2:]}"

def main():
    rows, failed = [], []
    for slug, name in TEAMS.items():
        try:
            gf, sf, xgf, ga, sa, xga = team_setpieces(slug)
            rows.append({
                "team": name, "gf": gf, "ga": ga, "sf": sf, "sa": sa, "xgf": xgf, "xga": xga,
                "shots_per_goal_for": round(sf / gf, 1) if gf else None,
                "shots_per_goal_against": round(sa / ga, 1) if ga else None,
            })
            print(f"  {name:<15} scored {gf} (x{xgf}) from {sf} SP shots | conceded {ga} from {sa}")
            time.sleep(0.6)
        except Exception as e:
            failed.append(name); print(f"  {name:<15} FAILED: {e}")

    if not rows:
        print("\nNo data retrieved. Understat is blocking this network. Run this from a\n"
              "normal (home/office) connection — it is not a code problem.")
        sys.exit(1)
    if failed:
        print(f"\nWARNING: {len(failed)} club(s) failed: {failed}. Re-run to retry them.")

    rows.sort(key=lambda r: r["gf"], reverse=True)
    payload = {
        "meta": {
            "season": label(SEASON),
            "source": "Understat (goals by situation)",
            "situations": SET_PIECE,
            "penalties_excluded": True,
            "note": "Set-piece goals = from corners + set pieces + direct free kicks (penalties excluded). "
                    "Efficiency = set-piece shots per set-piece goal.",
        },
        "teams": rows,
        "league": {
            "sp_goals": sum(r["gf"] for r in rows),
            "sp_shots": sum(r["sf"] for r in rows),
        },
    }
    with open(os.path.join(DOCS, "setpieces_goals.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nWrote docs/setpieces_goals.json for {label(SEASON)} ({len(rows)} clubs).")
    print("Now run:  python build_dashboard.py")

if __name__ == "__main__":
    main()
