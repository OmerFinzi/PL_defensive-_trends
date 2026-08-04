"""Build docs/index.html — a self-contained dashboard with data.json embedded inline.
Run after analyze.py. Output has zero external requests (GitHub Pages + offline safe)."""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
data = json.load(open(os.path.join(DOCS, "data.json"), encoding="utf-8"))
defcon_path = os.path.join(DOCS, "defcon.json")
defcon = json.load(open(defcon_path, encoding="utf-8")) if os.path.exists(defcon_path) else None
sp_path = os.path.join(DOCS, "setpieces.json")
setpieces = json.load(open(sp_path, encoding="utf-8")) if os.path.exists(sp_path) else None
spg_path = os.path.join(DOCS, "setpieces_goals.json")
spgoals = json.load(open(spg_path, encoding="utf-8")) if os.path.exists(spg_path) else None
if spgoals is not None:
    n = len(spgoals["teams"])
    assert n == 20, f"setpieces_goals.json has {n} teams, expected 20 — check for a dropped/misspelled team from the manual Understat entry"

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Premier League Defensive Trends 2020/21 - 2025/26</title>
<style>
:root{
  color-scheme:light;
  --plane:#f9f9f7; --surface:#fcfcfb; --surface-2:#ffffff;
  --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,.10);
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#e87ba4;
  --good:#0ca30c; --crit:#d03b3b; --accent:#1baf7a;
  --shadow:0 1px 2px rgba(11,11,11,.04),0 8px 24px rgba(11,11,11,.06);
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --plane:#0d0d0d; --surface:#1a1a19; --surface-2:#222220;
  --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181;
  --good:#0ca30c; --crit:#d03b3b; --accent:#199e70;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.5);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --plane:#0d0d0d; --surface:#1a1a19; --surface-2:#222220;
    --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
    --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181;
    --accent:#199e70;
  }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--plane);color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.5;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:20;backdrop-filter:blur(10px);
  background:color-mix(in srgb,var(--plane) 82%,transparent);
  border-bottom:1px solid var(--border)}
.top .wrap{display:flex;align-items:center;gap:14px;padding-top:14px;padding-bottom:14px}
.badge{width:38px;height:38px;border-radius:11px;flex:none;display:grid;place-items:center;
  background:linear-gradient(135deg,var(--accent),var(--s1));color:#fff;font-size:20px;
  box-shadow:var(--shadow)}
.top h1{font-size:16px;margin:0;font-weight:650;letter-spacing:-.01em}
.top p{margin:0;font-size:12.5px;color:var(--ink-2)}
.grow{flex:1}
.toggle{border:1px solid var(--border);background:var(--surface);color:var(--ink-2);
  border-radius:10px;padding:8px 12px;font-size:13px;cursor:pointer;font-weight:550}
.toggle:hover{color:var(--ink)}
.hero{padding:52px 0 26px}
.eyebrow{font-size:12px;font-weight:650;letter-spacing:.08em;text-transform:uppercase;
  color:var(--accent);margin:0 0 12px}
.hero h2{font-size:clamp(26px,4.4vw,44px);line-height:1.08;margin:0 0 14px;
  font-weight:720;letter-spacing:-.02em;max-width:20ch}
.hero .lede{font-size:16.5px;color:var(--ink-2);max-width:64ch;margin:0}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:30px 0 8px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:15px;
  padding:18px 18px 16px;box-shadow:var(--shadow)}
.kpi .v{font-size:30px;font-weight:720;letter-spacing:-.02em}
.kpi .l{font-size:12.5px;color:var(--ink-2);margin-top:3px}
.kpi .d{font-size:12px;font-weight:600;margin-top:9px;display:inline-flex;align-items:center;gap:5px}
.up{color:var(--good)} .down{color:var(--crit)}
section{padding:34px 0}
.sec-h{margin:0 0 4px;font-size:21px;font-weight:670;letter-spacing:-.01em}
.sec-sub{margin:0 0 20px;color:var(--ink-2);font-size:14.5px;max-width:76ch}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;
  padding:22px 22px 16px;box-shadow:var(--shadow)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.ctitle{font-size:14.5px;font-weight:620;margin:0 0 2px}
.csub{font-size:12.5px;color:var(--muted);margin:0 0 14px}
.legend{display:flex;flex-wrap:wrap;gap:14px;margin:12px 2px 0;font-size:12.5px;color:var(--ink-2)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:10px;height:10px;border-radius:3px;flex:none}
svg{width:100%;height:auto;display:block;overflow:visible}
.chart-h{fill:var(--ink);font-size:15.5px;font-weight:720;letter-spacing:-.01em}
.chart-sub{fill:var(--muted);font-size:11.5px}
.lgnd{fill:var(--ink-2);font-size:11.5px;font-weight:550}
.wm{fill:var(--muted);font-size:11.5px;font-weight:750;opacity:.5;letter-spacing:.02em}
.axis-lbl{fill:var(--muted);font-size:11px}
.val-lbl{fill:var(--ink);font-size:11px;font-weight:600}
.chart-card{position:relative}
.chart-actions{position:absolute;top:12px;right:12px;display:flex;gap:6px;opacity:.55;transition:opacity .15s}
.chart-card:hover .chart-actions,.chart-actions:focus-within{opacity:1}
.icon-btn{width:29px;height:29px;border-radius:9px;border:1px solid var(--border);background:var(--surface-2);
  color:var(--ink-2);display:grid;place-items:center;cursor:pointer;box-shadow:var(--shadow);padding:0}
.icon-btn:hover{color:var(--ink)}
.icon-btn:disabled{cursor:default;color:var(--good)}
.icon-btn svg{width:14px;height:14px;display:block}
.tip{position:fixed;pointer-events:none;z-index:50;background:var(--surface-2);
  border:1px solid var(--border);border-radius:10px;padding:8px 11px;font-size:12.5px;
  box-shadow:var(--shadow);opacity:0;transition:opacity .1s;max-width:240px}
.tip b{font-weight:650}
.tip .row{display:flex;justify-content:space-between;gap:14px;color:var(--ink-2)}
.tip .row b{color:var(--ink)}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:9px 10px;text-align:right;border-bottom:1px solid var(--border);
  font-variant-numeric:tabular-nums}
th:first-child,td:first-child{text-align:left}
th{font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);
  font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}
th:hover{color:var(--ink)}
tbody tr:hover{background:color-mix(in srgb,var(--accent) 7%,transparent)}
.rk{color:var(--muted);width:26px}
.bar-cell{position:relative}
.mini{height:7px;border-radius:4px;background:var(--s1);display:inline-block;vertical-align:middle}
.chip{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:600;
  background:color-mix(in srgb,var(--accent) 15%,transparent);color:var(--accent)}
.notes{font-size:13px;color:var(--ink-2)}
.notes li{margin:6px 0}
footer{padding:34px 0 56px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--border);margin-top:20px}
footer a{color:var(--accent)}
.pill-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.promo{background:var(--surface);border:1px solid var(--border);border-radius:13px;padding:14px 16px;
  box-shadow:var(--shadow);flex:1;min-width:150px}
.promo .n{font-weight:650;font-size:15px}
.promo .s{font-size:12.5px;color:var(--ink-2);margin-top:4px}
@media(max-width:860px){.grid2,.grid3{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){
  .card{padding:16px 0 12px}
  .card>[id^="c_"]{overflow-x:auto;-webkit-overflow-scrolling:touch;padding:0 14px}
  .card>[id^="c_"] svg{min-width:480px}
  .chart-actions{right:20px}
}
</style>
</head>
<body>
<header class="top"><div class="wrap">
  <div class="badge">&#128737;</div>
  <div><h1>Premier League Defensive Trends</h1><p>Six seasons of clean sheets &amp; goals conceded &middot; 2020/21 &rarr; 2025/26</p></div>
  <div class="grow"></div>
  <button class="toggle" id="themeBtn">&#9789; Theme</button>
</div></header>

<main class="wrap">
  <div class="hero">
    <p class="eyebrow">FPL Defensive Analysis &middot; Updated for 2025/26</p>
    <h2 id="heroHead"></h2>
    <p class="lede" id="heroLede"></p>
    <div class="kpis" id="kpis"></div>
  </div>

  <section>
    <h3 class="sec-h">The six-season story</h3>
    <p class="sec-sub">Clean sheets per game, goals per game, and "both teams to score" rate across every completed season. The attacking spike of 2023/24 has unwound &mdash; 2025/26 is the meanest season for goals since the pandemic-era 2020/21.</p>
    <div class="grid3">
      <div class="card"><div id="c_cs"></div></div>
      <div class="card"><div id="c_goals"></div></div>
      <div class="card"><div id="c_btts"></div></div>
    </div>
  </section>

  <section>
    <div class="grid2">
      <div>
        <h3 class="sec-h">Who to trust at the back &mdash; 2025/26</h3>
        <p class="sec-sub">Clean-sheet rate per team this season, split home vs away. The gap between the elite two and the rest is stark.</p>
        <div class="card"><div id="c_teams"></div></div>
      </div>
      <div>
        <h3 class="sec-h">The home clean-sheet edge</h3>
        <p class="sec-sub">Home and away clean-sheet rates by season. Home sides shut opponents out more often in five of the six seasons &mdash; but the edge is noisy rather than trending: it was near zero in 2020/21, peaked in 2022/23, and actually inverted in 2024/25. (Home advantage measured in <i>points</i> per game shows a cleaner recovery; that is a different metric from the one plotted here.)</p>
        <div class="card"><div id="c_ha"></div></div>
        <h3 class="sec-h" style="margin-top:26px">When clean sheets come</h3>
        <p class="sec-sub">Average clean sheets per game by third of the season.</p>
        <div class="card"><div id="c_thirds"></div></div>
      </div>
    </div>
  </section>

  <section>
    <h3 class="sec-h">Momentum: who tightened up, who fell apart</h3>
    <p class="sec-sub">Change in goals conceded per game, 2025/26 vs 2024/25. Green = conceding fewer (defence improving); red = leaking more. Only teams present in both seasons.</p>
    <div class="grid2">
      <div class="card"><div id="c_risers"></div></div>
      <div class="card"><div id="c_fallers"></div></div>
    </div>
  </section>

  <section>
    <h3 class="sec-h">Promoted sides &mdash; 2025/26 defensive record</h3>
    <p class="sec-sub">How the three newcomers held up defensively in their season back in the top flight.</p>
    <div class="pill-row" id="promo"></div>
  </section>

  <section>
    <h3 class="sec-h">Full 2025/26 defensive table</h3>
    <p class="sec-sub">Every team, sortable. Click a column header to re-sort.</p>
    <div class="card" style="padding:6px 10px"><div style="overflow-x:auto"><table id="tbl"></table></div></div>
  </section>
</main>

<section id="defconSec" style="display:none">
    <p class="eyebrow" style="color:var(--s2)">New for 2025/26 &middot; Player-level data</p>
    <h3 class="sec-h">Defensive Contribution (DefCon) points</h3>
    <p class="sec-sub" id="defconIntro"></p>
    <div class="kpis" id="defconKpis" style="margin-top:22px"></div>

    <div class="grid2" style="margin-top:20px">
      <div>
        <div class="card"><div id="c_dcpts"></div></div>
      </div>
      <div>
        <div class="card"><div id="c_dcpos"></div></div>
        <div class="card" style="margin-top:18px"><div id="c_dcteam"></div></div>
        <p class="csub" style="margin-top:8px">Note: this ranks defensive <i>workload</i> banked into FPL points, not defensive <i>quality</i> &mdash; a busy, deep-defending side racks up DefCon points the same way a leaky one does. For a quality read, see clean sheets &amp; goals conceded above.</p>
      </div>
    </div>

    <h3 class="sec-h" style="margin-top:34px">Best budget DefCon value</h3>
    <p class="sec-sub">DefCon points per &pound;m of season-end price, for enablers priced &pound;5.5m or under. These are the cheap defenders and midfielders who quietly banked points all season.</p>
    <div class="card" style="max-width:620px"><div id="c_dcvalue"></div></div>

    <h3 class="sec-h" style="margin-top:34px">Total defensive actions</h3>
    <p class="sec-sub">The action counts behind DefCon. The two position groups are scored on <b>different actions</b> &mdash; defenders on CBIT alone (clearances + blocks + interceptions + tackles), midfielders and forwards on CBIT <b>plus ball recoveries</b> &mdash; and against <b>different bars</b> (10 vs 12). So neither raw totals nor raw per-90 rates compare fairly across positions: counting everyone on CBIT hides high-volume midfielders, whose recoveries do count, while ranking on actions per 90 ignores that midfielders need more of them. The season leaderboard therefore counts each position on the actions that score for it, and the rate chart shows each player's per-90 as a <b>share of their own threshold</b>, where 100% is an average match landing exactly on the +2 boundary. The team table is deliberately different: raw CBIT for every player including goalkeepers, so all 20 squads sit on one uniform stat.</p>
    <div class="grid2" style="margin-top:20px">
      <div><div class="card"><div id="c_cbittop"></div></div></div>
      <div>
        <div class="card"><div id="c_cbitteam"></div></div>
        <div class="card" style="margin-top:18px"><div id="c_cbit90"></div></div>
      </div>
    </div>

    <h3 class="sec-h" style="margin-top:34px">Top 30 DefCon earners &mdash; full table</h3>
    <p class="sec-sub">Sortable. DC = total defensive contributions; DC/90 = per 90 minutes; Hits = matches reaching the DefCon threshold.</p>
    <div class="card" style="padding:6px 10px"><div style="overflow-x:auto"><table id="dctbl"></table></div></div>
  </section>

  <section id="spSec" style="display:none">
    <p class="eyebrow" style="color:var(--s3)">Set pieces &middot; Corners &amp; free kicks (penalties excluded)</p>
    <h3 class="sec-h">Set-piece volume &amp; who takes them</h3>
    <p class="sec-sub" id="spIntro"></p>
    <div class="kpis" id="spKpis" style="margin-top:22px"></div>

    <div class="grid2" style="margin-top:20px">
      <div>
        <div class="card"><div id="c_spteams"></div></div>
      </div>
      <div>
        <div class="card"><div id="c_sptrend"></div></div>
        <h3 class="sec-h" style="margin-top:26px">Notable set-piece takers</h3>
        <p class="sec-sub">Players who are their club's designated taker for <b>both</b> corners and direct free kicks in 2025/26.</p>
        <div class="pill-row" id="sp_notable"></div>
      </div>
    </div>

    <h3 class="sec-h" style="margin-top:34px">Designated takers by club &mdash; 2025/26</h3>
    <p class="sec-sub">Primary corner and direct-free-kick takers per club (official FPL set-piece orders). Penalty takers are excluded. These are designated takers, not confirmed scorers.</p>
    <div class="card" style="padding:6px 10px"><div style="overflow-x:auto"><table id="sp_takers"></table></div></div>

    <div id="spgBlock" style="display:none">
      <h3 class="sec-h" style="margin-top:34px">Set-piece goals &mdash; who scores &amp; concedes most</h3>
      <p class="sec-sub" id="spgIntro"></p>
      <div class="kpis" id="spgKpis" style="margin-top:18px"></div>
      <div class="grid2" style="margin-top:20px">
        <div class="card"><div id="c_spgfor"></div></div>
        <div class="card"><div id="c_spgagainst"></div></div>
      </div>

      <h3 class="sec-h" style="margin-top:34px">Set-piece efficiency &mdash; shots needed per goal</h3>
      <p class="sec-sub">How many set-piece shots, on average, each team needs to score once &mdash; and how many their opponents need to score against them. Lower "to score" = more clinical; lower "to concede" = more porous defensively. <b>The gray whiskers are 95% confidence intervals</b> on the goal count behind each ratio (a handful of goals either way from a small sample) &mdash; hover a bar for the exact range. Where two teams' whiskers overlap heavily, treat them as statistically indistinguishable rather than reading the ranking literally; an arrow means the interval runs past the edge of the chart.</p>
      <div class="card" style="max-width:620px"><div id="c_spgeff"></div></div>
    </div>
  </section>

  <footer><div class="wrap">
  <p><b>Data</b> &middot; League &amp; team trends from <span id="fsrc"></span> (match results). DefCon section from the community FPL archive (official FPL season-end stats). Set-piece corners from football-data.co.uk; set-piece takers from official FPL orders (penalties excluded). Each source is clearly labelled. Goal-level set-piece breakdown and xGA/ownership need event data and are out of scope &mdash; not shown, not estimated.<br>
  <b>Method</b> &middot; A clean sheet is credited to a team that concedes zero in a match. "CS rate" = clean sheets &divide; matches. Built with a reproducible Python pipeline; this page embeds its output and makes no external requests.<br>
  Analysis by <b>@omerfin7</b> &middot; refreshed for the 2025/26 season.</p>
</div></footer>

<div class="tip" id="tip"></div>
<script>
const DATA = __DATA_JSON__;
const DEFCON = __DEFCON_JSON__;
const SP = __SP_JSON__;
const SPG = __SPG_JSON__;
const $=(s,r=document)=>r.querySelector(s);
const tip=$("#tip");
const cv=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
function showTip(html,e){tip.innerHTML=html;tip.style.opacity=1;
  const p=12,w=tip.offsetWidth,h=tip.offsetHeight;
  let x=e.clientX+p,y=e.clientY+p;
  if(x+w>innerWidth)x=e.clientX-w-p; if(y+h>innerHeight)y=e.clientY-h-p;
  tip.style.left=x+"px";tip.style.top=y+"px";}
function hideTip(){tip.style.opacity=0;}
const NS="http://www.w3.org/2000/svg";
function el(t,a={}){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);return e;}
const fmt1=v=>v.toFixed(2), pct=v=>Math.round(v*100)+"%";

// ---------- hero + KPIs ----------
const L=DATA.league, last=L[L.length-1], prev=L[L.length-2];
const topTeam=DATA.latest_table[0];
// The record is looked up, not assumed: the latest leader is not automatically the
// best of the window (Arsenal's 2025/26 is third behind two 2021/22 seasons).
const BD=DATA.best_defensive_seasons, rec=BD[0];
const recHolders=BD.filter(r=>r.cs_rate===rec.cs_rate&&r.conceded_pg===rec.conceded_pg);
const recIsLatest=recHolders.some(r=>r.team===topTeam.team&&r.season===DATA.meta.latest);
const heroTail=recIsLatest
  ? `the single best defensive return across the six seasons studied`
  : `the league's best this season, though short of the ${pct(rec.cs_rate)} `+
    `${recHolders.map(r=>r.team).join(" and ")} managed in ${rec.season}`;
$("#heroHead").textContent=`Defences are winning back the Premier League in ${DATA.meta.latest}.`;
$("#heroLede").innerHTML=`After the goal glut of 2023/24 &mdash; the highest-scoring of the six seasons studied &mdash; scoring has fallen for two straight seasons. In ${DATA.meta.latest} clubs are conceding less, keeping more clean sheets, and <b>${topTeam.team}</b> lead the way with a ${pct(topTeam.cs_rate)} clean-sheet rate &mdash; ${heroTail}.`;
$("#fsrc").textContent=DATA.meta.source;
function kpi(v,l,d,dir){return `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div>`+
  (d?`<div class="d ${dir}">${dir==='up'?'&#9650;':'&#9660;'} ${d}</div>`:``)+`</div>`;}
const csD=(last.cs_per_game-prev.cs_per_game), gD=(last.goals_per_game-prev.goals_per_game);
$("#kpis").innerHTML=
  kpi(fmt1(last.cs_per_game),`Clean sheets / game (${DATA.meta.latest})`,`${csD>=0?'+':''}${csD.toFixed(2)} vs ${prev.season}`,csD>=0?'up':'down')+
  kpi(fmt1(last.goals_per_game),`Goals / game (${DATA.meta.latest})`,`${gD>=0?'+':''}${gD.toFixed(2)} vs ${prev.season}`,gD<=0?'up':'down')+
  kpi(pct(last.btts_rate),`Both teams to score`,`lowest since ${DATA.meta.latest==='2025/26'?'2022/23':''}`,'up')+
  kpi(topTeam.team,`Meanest defence`,`${pct(topTeam.cs_rate)} CS &middot; ${fmt1(topTeam.conceded_pg)} conceded/gm`,'up');

// ---------- shared chart chrome: headline + watermark (+ optional legend) ----------
function banner(svg,W,H,title,sub,legend){
  if(title){const t=el("text",{x:14,y:22,class:"chart-h"});t.textContent=title;svg.appendChild(t);}
  if(sub){const s=el("text",{x:14,y:39,class:"chart-sub"});s.textContent=sub;svg.appendChild(s);}
  const wm=el("text",{x:W-8,y:H-8,"text-anchor":"end",class:"wm"});wm.textContent="@omerfin7";svg.appendChild(wm);
  if(legend){
    // own row, left-aligned below the subtitle — keeps the top-right corner
    // clear for the HTML save/copy button overlay (see addChartActions)
    const ly=sub?57:40; let x=14;
    legend.forEach(it=>{
      svg.appendChild(el("rect",{x,y:ly-9,width:9,height:9,rx:2,fill:it.color}));
      const tt=el("text",{x:x+14,y:ly,class:"lgnd"});tt.textContent=it.label;svg.appendChild(tt);
      x+=14+it.label.length*6.4+18;
    });
  }
}
// ---------- line chart ----------
function lineChart(sel,pts,{color,fmt=fmt1,pad=0.14,title,sub,sdCapLo=0,sdCapHi=Infinity}){
  const W=440,H=250,mL=44,mR=18,mT=58,mB=40;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,role:"img"});
  const hasSd=pts.some(p=>p.sd!=null);
  const ys=pts.map(p=>p.y);
  // a rate/count can't physically go below 0 (or, for a share, above 1) —
  // clamp the band so it never implies an impossible value
  const sdLo=pts.map(p=>Math.max(sdCapLo,p.y-(p.sd||0))), sdHi=pts.map(p=>Math.min(sdCapHi,p.y+(p.sd||0)));
  let lo=Math.min(...ys,...sdLo),hi=Math.max(...ys,...sdHi);const sp=(hi-lo)||1;
  lo=Math.max(sdCapLo,lo-sp*pad);hi=Math.min(sdCapHi,hi+sp*pad);
  const X=i=>mL+(W-mL-mR)*i/(pts.length-1);
  const Y=v=>mT+(H-mT-mB)*(1-(v-lo)/(hi-lo));
  for(let g=0;g<=3;g++){const v=lo+(hi-lo)*g/3;const y=Y(v);
    svg.appendChild(el("line",{x1:mL,x2:W-mR,y1:y,y2:y,stroke:cv('--grid'),"stroke-width":1}));
    const t=el("text",{x:mL-6,y:y+3,"text-anchor":"end",class:"axis-lbl"});t.textContent=fmt(v);svg.appendChild(t);}
  pts.forEach((p,i)=>{const t=el("text",{x:X(i),y:H-22,"text-anchor":"middle",class:"axis-lbl"});
    t.textContent=p.lab;svg.appendChild(t);});
  if(hasSd){
    // ±1 SD across that season's matches — how much spread sits behind the average
    let bd=`M ${X(0)} ${Y(sdHi[0])}`; pts.forEach((p,i)=>{if(i)bd+=` L ${X(i)} ${Y(sdHi[i])}`;});
    for(let i=pts.length-1;i>=0;i--)bd+=` L ${X(i)} ${Y(sdLo[i])}`;
    bd+=' Z';
    svg.appendChild(el("path",{d:bd,fill:color,"fill-opacity":0.12}));
  }
  let d=`M ${X(0)} ${Y(ys[0])}`; pts.forEach((p,i)=>d+=` L ${X(i)} ${Y(p.y)}`);
  const area=d+` L ${X(pts.length-1)} ${Y(lo)} L ${X(0)} ${Y(lo)} Z`;
  const gid="g"+sel.replace(/\W/g,'');
  const defs=el("defs");const lg=el("linearGradient",{id:gid,x1:0,y1:0,x2:0,y2:1});
  lg.appendChild(el("stop",{offset:"0%","stop-color":color,"stop-opacity":.20}));
  lg.appendChild(el("stop",{offset:"100%","stop-color":color,"stop-opacity":0}));
  defs.appendChild(lg);svg.appendChild(defs);
  if(!hasSd)svg.appendChild(el("path",{d:area,fill:`url(#${gid})`}));
  svg.appendChild(el("path",{d,fill:"none",stroke:color,"stroke-width":2.4,"stroke-linejoin":"round","stroke-linecap":"round"}));
  pts.forEach((p,i)=>{
    svg.appendChild(el("circle",{cx:X(i),cy:Y(p.y),r:3.6,fill:cv('--surface'),stroke:color,"stroke-width":2}));
    const vt=el("text",{x:X(i),y:Y(p.y)-9,"text-anchor":"middle",class:"val-lbl"});vt.textContent=fmt(p.y);svg.appendChild(vt);
    const hit=el("rect",{x:X(i)-18,y:mT,width:36,height:H-mT-mB,fill:"transparent"});
    hit.addEventListener("mousemove",e=>{
      const sdRow=p.sd!=null?`<div class="row"><span>±1 SD (across matches)</span><b>${fmt(p.sd)}</b></div>`:'';
      showTip(`<b>${p.full}</b><div class="row"><span>${p.name}</span><b>${fmt(p.y)}</b></div>${sdRow}`,e);});
    hit.addEventListener("mouseleave",hideTip);svg.appendChild(hit);});
  banner(svg,W,H,title,sub);
  $(sel).appendChild(svg);
}
const seasons=L.map(r=>r.season);
function mk(key,name,f=fmt1){return L.map(r=>({x:r.season,y:r[key],sd:r[key+'_sd'],lab:r.season.slice(2),full:r.season,name}));}

// ---------- horizontal team bars (home/away CS) ----------
function teamBars(sel,rows,title,sub){
  const W=560,rowH=24,mT=74,mL=104,mR=44,H=mT+rows.length*rowH+22;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
  const max=Math.max(...rows.map(r=>Math.max(r.home_cs_rate,r.away_cs_rate)))*1.08;
  const X=v=>mL+(W-mL-mR)*v/max;
  rows.forEach((r,i)=>{
    const y=mT+i*rowH;
    const t=el("text",{x:mL-8,y:y+rowH/2+1,"text-anchor":"end",class:"val-lbl"});t.textContent=r.team;svg.appendChild(t);
    const mkbar=(val,col,off,h)=>{
      const w=Math.max(2,X(val)-mL);
      const rect=el("rect",{x:mL,y:y+off,width:w,height:h,rx:3,fill:col});
      rect.addEventListener("mousemove",e=>showTip(`<b>${r.team}</b><div class="row"><span>Overall CS</span><b>${pct(r.cs_rate)}</b></div><div class="row"><span>Home CS</span><b>${pct(r.home_cs_rate)}</b></div><div class="row"><span>Away CS</span><b>${pct(r.away_cs_rate)}</b></div><div class="row"><span>Conceded/gm</span><b>${fmt1(r.conceded_pg)}</b></div>`,e));
      rect.addEventListener("mouseleave",hideTip);svg.appendChild(rect);};
    mkbar(r.home_cs_rate,cv('--s1'),3,7);
    mkbar(r.away_cs_rate,cv('--s3'),13,7);
    // Label the bar the number actually sits at. It used to print the overall CS
    // rate at the tip of the longer home/away bar, so it described neither.
    const mx=Math.max(r.home_cs_rate,r.away_cs_rate);
    const vl=el("text",{x:X(mx)+6,y:y+rowH/2+1,class:"axis-lbl"});
    vl.textContent=pct(mx);svg.appendChild(vl);
  });
  banner(svg,W,H,title,sub,[{label:'Home',color:cv('--s1')},{label:'Away',color:cv('--s3')}]);
  $(sel).appendChild(svg);
}

// ---------- home advantage: two lines same scale ----------
function multiLine(sel,series,fmt=pct,title,sub,legend){
  const W=520,H=298,mL=44,mR=18,mT=76,mB=40;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
  const all=series.flatMap(s=>s.data.map(d=>d.y));
  let lo=Math.min(...all),hi=Math.max(...all);const sp=(hi-lo)||1;lo-=sp*.18;hi+=sp*.18;
  const n=series[0].data.length;
  const X=i=>mL+(W-mL-mR)*i/(n-1), Y=v=>mT+(H-mT-mB)*(1-(v-lo)/(hi-lo));
  for(let g=0;g<=3;g++){const v=lo+(hi-lo)*g/3,y=Y(v);
    svg.appendChild(el("line",{x1:mL,x2:W-mR,y1:y,y2:y,stroke:cv('--grid')}));
    const t=el("text",{x:mL-6,y:y+3,"text-anchor":"end",class:"axis-lbl"});t.textContent=fmt(v);svg.appendChild(t);}
  series[0].data.forEach((d,i)=>{const t=el("text",{x:X(i),y:H-22,"text-anchor":"middle",class:"axis-lbl"});t.textContent=d.lab;svg.appendChild(t);});
  series.forEach(s=>{let d=`M ${X(0)} ${Y(s.data[0].y)}`;s.data.forEach((p,i)=>d+=` L ${X(i)} ${Y(p.y)}`);
    svg.appendChild(el("path",{d,fill:"none",stroke:s.color,"stroke-width":2.4,"stroke-linejoin":"round"}));
    s.data.forEach((p,i)=>svg.appendChild(el("circle",{cx:X(i),cy:Y(p.y),r:3.4,fill:cv('--surface'),stroke:s.color,"stroke-width":2})));});
  series[0].data.forEach((_,i)=>{const hit=el("rect",{x:X(i)-16,y:mT,width:32,height:H-mT-mB,fill:"transparent"});
    hit.addEventListener("mousemove",e=>{const rows=series.map(s=>`<div class="row"><span>${s.name}</span><b>${fmt(s.data[i].y)}</b></div>`).join('');
      showTip(`<b>${series[0].data[i].full}</b>${rows}`,e);});
    hit.addEventListener("mouseleave",hideTip);svg.appendChild(hit);});
  banner(svg,W,H,title,sub,legend);
  $(sel).appendChild(svg);
}

// ---------- season thirds grouped bars ----------
function thirdsChart(sel,title,sub,legend){
  const keys=Object.keys(DATA.thirds.all_seasons);
  const W=520,H=298,mL=44,mR=18,mT=76,mB=54,gw=(W-mL-mR)/keys.length;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
  const vals=keys.flatMap(k=>[DATA.thirds.all_seasons[k],DATA.thirds[DATA.meta.latest][k]]);
  const hi=Math.max(...vals)*1.15;const Y=v=>mT+(H-mT-mB)*(1-v/hi);
  for(let g=0;g<=3;g++){const v=hi*g/3,y=Y(v);
    svg.appendChild(el("line",{x1:mL,x2:W-mR,y1:y,y2:y,stroke:cv('--grid')}));
    const t=el("text",{x:mL-6,y:y+3,"text-anchor":"end",class:"axis-lbl"});t.textContent=v.toFixed(2);svg.appendChild(t);}
  keys.forEach((k,i)=>{
    const cx=mL+gw*i+gw/2, bw=gw*0.26;
    const a=DATA.thirds.all_seasons[k], b=DATA.thirds[DATA.meta.latest][k];
    const mkbar=(v,col,dx,lbl)=>{const h=(H-mT-mB)-(Y(v)-mT);
      const rc=el("rect",{x:cx+dx,y:Y(v),width:bw,height:Math.max(1,h),rx:3,fill:col});
      rc.addEventListener("mousemove",e=>showTip(`<b>${k}</b><div class="row"><span>${lbl}</span><b>${v.toFixed(2)} CS/gm</b></div>`,e));
      rc.addEventListener("mouseleave",hideTip);svg.appendChild(rc);
      const vt=el("text",{x:cx+dx+bw/2,y:Y(v)-5,"text-anchor":"middle",class:"val-lbl"});vt.textContent=v.toFixed(2);svg.appendChild(vt);};
    mkbar(a,cv('--s4'),-bw-2,"All seasons");
    mkbar(b,cv('--s1'),2,DATA.meta.latest);
    const t=el("text",{x:cx,y:H-32,"text-anchor":"middle",class:"axis-lbl"});t.textContent=k.split(' ')[0];svg.appendChild(t);
    const t2=el("text",{x:cx,y:H-20,"text-anchor":"middle",class:"axis-lbl"});t2.textContent=k.match(/\((.*)\)/)[1];svg.appendChild(t2);
  });
  banner(svg,W,H,title,sub,legend);
  $(sel).appendChild(svg);
}

// ---------- diverging movers ----------
function movers(sel,rows,improving,title,sub){
  const W=520,rowH=30,mT=56,mL=104,mR=58,H=mT+rows.length*rowH+22;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
  const max=Math.max(...rows.map(r=>Math.abs(r.delta)))*1.12;
  const X=v=>mL+(W-mL-mR)*Math.abs(v)/max;
  const col=improving?cv('--good'):cv('--crit');
  rows.forEach((r,i)=>{
    const y=mT+i*rowH;
    const t=el("text",{x:mL-8,y:y+rowH/2+1,"text-anchor":"end",class:"val-lbl"});t.textContent=r.team;svg.appendChild(t);
    const w=Math.max(2,X(r.delta)-mL);
    const rc=el("rect",{x:mL,y:y+8,width:w,height:12,rx:3,fill:col});
    rc.addEventListener("mousemove",e=>showTip(`<b>${r.team}</b><div class="row"><span>${DATA.league[DATA.league.length-2].season}</span><b>${fmt1(r.prev)}</b></div><div class="row"><span>${DATA.meta.latest}</span><b>${fmt1(r.cur)}</b></div><div class="row"><span>Change</span><b>${r.delta>0?'+':''}${fmt1(r.delta)}/gm</b></div>`,e));
    rc.addEventListener("mouseleave",hideTip);svg.appendChild(rc);
    const vl=el("text",{x:mL+w+6,y:y+rowH/2+1,class:"axis-lbl"});vl.textContent=`${r.delta>0?'+':''}${r.delta.toFixed(2)}`;svg.appendChild(vl);
  });
  banner(svg,W,H,title,sub);
  $(sel).appendChild(svg);
}

// ---------- promoted ----------
$("#promo").innerHTML=DATA.promoted.map(r=>
  `<div class="promo"><div class="n">${r.team} <span class="chip">promoted</span></div>
   <div class="s">${pct(r.cs_rate)} clean-sheet rate &middot; ${fmt1(r.conceded_pg)} conceded/game<br>${r.clean_sheets} clean sheets in ${r.games} games</div></div>`).join('');

// ---------- table ----------
const cols=[["team","Team"],["games","P"],["clean_sheets","CS"],["cs_rate","CS %"],
  ["conceded","GC"],["conceded_pg","GC/gm"],["home_cs_rate","Home CS%"],["away_cs_rate","Away CS%"]];
let sortKey="cs_rate",sortDir=-1;
function renderTable(){
  const rows=[...DATA.latest_table].sort((a,b)=>(a[sortKey]>b[sortKey]?1:-1)*sortDir);
  const maxCS=Math.max(...rows.map(r=>r.cs_rate));
  let h="<thead><tr><th class='rk'>#</th>"+cols.map(c=>`<th data-k="${c[0]}">${c[1]}</th>`).join('')+"</tr></thead><tbody>";
  rows.forEach((r,i)=>{
    h+=`<tr><td class="rk">${i+1}</td>`+cols.map(c=>{
      const v=r[c[0]];
      if(c[0]==="team")return `<td><b>${v}</b></td>`;
      if(c[0]==="cs_rate")return `<td class="bar-cell">${pct(v)} <span class="mini" style="width:${28*v/maxCS+4}px"></span></td>`;
      if(c[0].includes("rate"))return `<td>${pct(v)}</td>`;
      if(c[0]==="conceded_pg")return `<td>${fmt1(v)}</td>`;
      return `<td>${v}</td>`;
    }).join('')+"</tr>";
  });
  $("#tbl").innerHTML=h+"</tbody>";
  $("#tbl").querySelectorAll("th[data-k]").forEach(th=>th.onclick=()=>{
    const k=th.dataset.k; if(k===sortKey)sortDir*=-1;else{sortKey=k;sortDir=(k==="team")?1:-1;}renderTable();});
}
renderTable();

// ---------- DefCon (player-level, 2025/26) ----------
const POSCOL={DEF:'--s1',MID:'--s2',FWD:'--s3'};
function hbars(sel,rows,{value,label,color,valfmt=(v)=>v,rowH=26,mL=118,mR=48,tip,title,sub,legend}){
  const W=560,mT=legend?74:56,H=mT+rows.length*rowH+22;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
  const max=Math.max(...rows.map(r=>value(r)))*1.06||1;
  const X=v=>mL+(W-mL-mR)*v/max;
  rows.forEach((r,i)=>{
    const y=mT+i*rowH, v=value(r);
    const t=el("text",{x:mL-8,y:y+rowH/2+1,"text-anchor":"end",class:"val-lbl"});t.textContent=label(r);svg.appendChild(t);
    const w=Math.max(2,X(v)-mL), col=typeof color==='function'?color(r):color;
    const rc=el("rect",{x:mL,y:y+rowH/2-5,width:w,height:10,rx:3,fill:col});
    if(tip){rc.addEventListener("mousemove",e=>showTip(tip(r),e));rc.addEventListener("mouseleave",hideTip);}
    svg.appendChild(rc);
    const vl=el("text",{x:mL+w+6,y:y+rowH/2+1,class:"axis-lbl"});vl.textContent=valfmt(v);svg.appendChild(vl);
  });
  banner(svg,W,H,title,sub,legend);
  $(sel).appendChild(svg);
}
function dcTip(r){return `<b>${r.name}</b> &middot; ${r.team_short} ${r.pos}<div class="row"><span>DefCon points</span><b>${r.defcon_points}</b></div><div class="row"><span>Threshold hits</span><b>${r.dc_matches}/${r.apps} matches</b></div><div class="row"><span>Hit rate</span><b>${(r.hit_rate*100).toFixed(0)}% <span style="opacity:.6">(95% CI ${(r.hit_rate_ci_lo*100).toFixed(0)}&ndash;${(r.hit_rate_ci_hi*100).toFixed(0)}%)</span></b></div><div class="row"><span>Per 90</span><b>${r.dc90.toFixed(2)}</b></div><div class="row"><span>Price</span><b>&pound;${r.cost}m</b></div>`;}
function renderDefcon(){
  if(!DEFCON)return;
  $("#defconSec").style.display="";
  $("#defconIntro").innerHTML=`New this season, players bank <b>+2 points</b> in a match when their defensive work hits a threshold &mdash; <b>10+</b> clearances/blocks/interceptions/tackles for defenders, <b>12+</b> (also counting recoveries) for midfielders and forwards. Across ${DEFCON.meta.season}, <b>${DEFCON.meta.n_returning}</b> of the ${DEFCON.meta.n_played} outfielders who actually played banked at least one DefCon return (${DEFCON.meta.n_players} were registered, but ${DEFCON.meta.n_players-DEFCON.meta.n_played} never played a minute). ${DEFCON.meta.note} Hover a player for their <b>threshold-hit rate</b> with a 95% confidence interval &mdash; with 30+ matches to draw on, the leaders' hit-rates are a real, repeatable role/floor, not a hot streak.`;
  const tp=DEFCON.top_points, lead=tp[0], ps=DEFCON.position_summary;
  const defP=ps.find(p=>p.pos==='DEF'), midP=ps.find(p=>p.pos==='MID');
  $("#defconKpis").innerHTML=
    `<div class="kpi"><div class="v">${lead.defcon_points}</div><div class="l">Most DefCon points &middot; ${lead.name} (${lead.team_short})</div><div class="d up">${lead.dc_matches} threshold hits</div></div>`+
    `<div class="kpi"><div class="v">${DEFCON.meta.n_returning}</div><div class="l">Players with DefCon returns</div><div class="d up">of ${DEFCON.meta.n_played} who played</div></div>`+
    `<div class="kpi"><div class="v">${defP.total_points}</div><div class="l">Points banked by defenders</div><div class="d up">${defP.returning_players} returning</div></div>`+
    `<div class="kpi"><div class="v">${midP.total_points}</div><div class="l">Points banked by midfielders</div><div class="d up">${midP.returning_players} returning</div></div>`;
  hbars("#c_dcpts",tp,{value:r=>r.defcon_points,label:r=>`${r.name} (${r.team_short})`,
    color:r=>cv(POSCOL[r.pos]),tip:dcTip,
    title:"DefCon points banked — top 15",sub:"2025/26 · threshold hits × 2 pts",
    legend:[{label:'DEF',color:cv('--s1')},{label:'MID',color:cv('--s2')},{label:'FWD',color:cv('--s3')}]});
  hbars("#c_dcpos",ps,{value:r=>r.total_points,label:r=>r.pos,
    color:r=>cv(POSCOL[r.pos]),rowH:38,mL:56,
    title:"Where DefCon points come from",sub:"Total points banked by position, 2025/26",
    tip:r=>`<b>${r.pos}</b><div class="row"><span>Total points</span><b>${r.total_points}</b></div><div class="row"><span>Returning players</span><b>${r.returning_players}</b></div><div class="row"><span>Avg / returner</span><b>${r.avg_points_returning}</b></div>`});
  hbars("#c_dcteam",DEFCON.team_defcon.slice(0,12),{value:r=>r.points,label:r=>r.team,
    color:cv('--s1'),rowH:22,mL:56,title:"Hardest-working defensive clubs",sub:"Total DefCon points across each squad",
    tip:r=>`<b>${r.team}</b><div class="row"><span>DefCon points</span><b>${r.points}</b></div>`});
  hbars("#c_dcvalue",DEFCON.best_value,{value:r=>r.pts_per_m,label:r=>`${r.name} (${r.team_short})`,
    color:cv('--s3'),valfmt:v=>v.toFixed(2),
    title:"Best budget DefCon value",sub:"DefCon points per £m · enablers ≤ £5.5m",
    tip:r=>`<b>${r.name}</b> &middot; ${r.team_short} ${r.pos}<div class="row"><span>Points / &pound;m</span><b>${r.pts_per_m.toFixed(2)}</b></div><div class="row"><span>DefCon points</span><b>${r.defcon_points}</b></div><div class="row"><span>Price</span><b>&pound;${r.cost}m</b></div>`});
  const cbitTip=r=>`<b>${r.name}</b> &middot; ${r.team_short} ${r.pos}<div class="row"><span>Defensive actions</span><b>${r.dc}</b></div><div class="row"><span>CBIT</span><b>${r.cbit}</b></div><div class="row"><span>Recoveries</span><b>${r.pos==='DEF'?`${r.rec} &middot; not counted for DEF`:r.rec}</b></div><div class="row"><span>Actions / 90</span><b>${r.dc90.toFixed(2)} <span style="opacity:.6">vs ${r.thr} needed</span></b></div><div class="row"><span>Share of threshold</span><b>${r.thr_pct.toFixed(0)}%</b></div><div class="row"><span>Minutes</span><b>${r.minutes}</b></div>`;
  hbars("#c_cbittop",DEFCON.top_cbit,{value:r=>r.dc,label:r=>`${r.name} (${r.team_short})`,
    color:r=>cv(POSCOL[r.pos]),tip:cbitTip,
    title:"Most defensive actions — top 15",sub:"Counted per position · DEF: CBIT · MID/FWD: CBIT + recoveries",
    legend:[{label:'DEF',color:cv('--s1')},{label:'MID',color:cv('--s2')},{label:'FWD',color:cv('--s3')}]});
  hbars("#c_cbitteam",DEFCON.team_cbit.slice(0,12),{value:r=>r.cbit,label:r=>r.team,
    color:cv('--s1'),rowH:22,mL:56,title:"Team CBIT totals",sub:"Raw CBIT across the whole squad incl. GKs, recoveries excluded — 2025/26",
    tip:r=>`<b>${r.team}</b><div class="row"><span>CBIT (season)</span><b>${r.cbit}</b></div>`});
  hbars("#c_cbit90",DEFCON.top_cbit90,{value:r=>r.thr_pct,label:r=>`${r.name} (${r.team_short})`,
    color:r=>cv(POSCOL[r.pos]),valfmt:v=>v.toFixed(0)+"%",tip:cbitTip,
    title:"Closest to their threshold, per 90 — top 10",sub:"Actions per 90 as a share of that position's bar (DEF 10, MID/FWD 12) · 1,500+ minutes",
    legend:[{label:'DEF',color:cv('--s1')},{label:'MID',color:cv('--s2')},{label:'FWD',color:cv('--s3')}]});
  // table
  const dcols=[["name","Player"],["team_short","Team"],["pos","Pos"],["minutes","Min"],
    ["dc","DC"],["dc90","DC/90"],["dc_matches","Hits"],["defcon_points","DefCon pts"],["cost","&pound;m"]];
  let sk="defcon_points",sd=-1;
  function draw(){
    const rows=[...DEFCON.table].sort((a,b)=>(a[sk]>b[sk]?1:-1)*sd);
    let h="<thead><tr><th class='rk'>#</th>"+dcols.map(c=>`<th data-k="${c[0]}">${c[1]}</th>`).join('')+"</tr></thead><tbody>";
    rows.forEach((r,i)=>{h+=`<tr><td class="rk">${i+1}</td>`+dcols.map(c=>{
      const v=r[c[0]];
      if(c[0]==="name")return `<td><b>${v}</b></td>`;
      if(c[0]==="pos")return `<td><span class="dot" style="display:inline-block;background:${cv(POSCOL[v])}"></span> ${v}</td>`;
      if(c[0]==="dc90")return `<td>${v.toFixed(2)}</td>`;
      if(c[0]==="cost")return `<td>${v.toFixed(2)}</td>`;
      if(c[0]==="defcon_points")return `<td><b>${v}</b></td>`;
      return `<td>${v}</td>`;}).join('')+"</tr>";});
    $("#dctbl").innerHTML=h+"</tbody>";
    $("#dctbl").querySelectorAll("th[data-k]").forEach(th=>th.onclick=()=>{
      const k=th.dataset.k;if(k===sk)sd*=-1;else{sk=k;sd=(k==="name"||k==="team_short"||k==="pos")?1:-1;}draw();});
  }
  draw();
}

// ---------- draw everything (also used to re-theme) ----------
function renderMain(){
  lineChart("#c_cs",mk('cs_per_game','Clean sheets / game'),{color:cv('--s1'),title:"Clean sheets per game",sub:"2020/21–2025/26 · shaded = ±1 SD across matches",sdCapHi:2});
  lineChart("#c_goals",mk('goals_per_game','Goals / game'),{color:cv('--s2'),title:"Goals per game",sub:"Total goals ÷ matches · shaded = ±1 SD across matches"});
  lineChart("#c_btts",L.map(r=>({y:r.btts_rate,sd:r.btts_rate_sd,lab:r.season.slice(2),full:r.season,name:'BTTS'})),{color:cv('--s3'),fmt:pct,title:"Both teams to score",sub:"Share of matches · shaded = ±1 SD across matches",sdCapHi:1});
  teamBars("#c_teams",DATA.latest_table,"Who to trust at the back — 2025/26","Clean-sheet rate per team, home vs away");
  multiLine("#c_ha",[{name:"Home CS rate",color:cv('--s1'),data:L.map(r=>({y:r.home_cs_rate,lab:r.season.slice(2),full:r.season}))},{name:"Away CS rate",color:cv('--s2'),data:L.map(r=>({y:r.away_cs_rate,lab:r.season.slice(2),full:r.season}))}],pct,"The home clean-sheet edge","Clean-sheet rate by season · home ahead in 5 of 6",[{label:'Home',color:cv('--s1')},{label:'Away',color:cv('--s2')}]);
  thirdsChart("#c_thirds","When clean sheets come","Avg clean sheets/game by third of season",[{label:'All seasons',color:cv('--s4')},{label:'2025/26',color:cv('--s1')}]);
  movers("#c_risers",DATA.risers,true,"Biggest improvers — 2025/26","Fewer goals conceded/gm vs 2024/25");
  movers("#c_fallers",DATA.fallers,false,"Biggest declines — 2025/26","More goals conceded/gm vs 2024/25");
}
// ---------- Set pieces (corners + free kicks, penalties excluded) ----------
function spBars(sel,rows,title,sub){
  const W=560,rowH=25,mT=74,mL=104,mR=52,H=mT+rows.length*rowH+22;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
  const max=Math.max(...rows.map(r=>Math.max(r.for_pg,r.against_pg)))*1.08;
  const X=v=>mL+(W-mL-mR)*v/max;
  rows.forEach((r,i)=>{
    const y=mT+i*rowH;
    const t=el("text",{x:mL-8,y:y+rowH/2+1,"text-anchor":"end",class:"val-lbl"});t.textContent=r.team;svg.appendChild(t);
    const mkbar=(val,col,off)=>{const w=Math.max(2,X(val)-mL);
      const rc=el("rect",{x:mL,y:y+off,width:w,height:7,rx:3,fill:col});
      rc.addEventListener("mousemove",e=>showTip(`<b>${r.team}</b><div class="row"><span>Corners won/gm</span><b>${r.for_pg}</b></div><div class="row"><span>Corners conceded/gm</span><b>${r.against_pg}</b></div><div class="row"><span>Net/gm</span><b>${r.net_pg>0?'+':''}${r.net_pg}</b></div>`,e));
      rc.addEventListener("mouseleave",hideTip);svg.appendChild(rc);};
    mkbar(r.for_pg,cv('--s3'),3);
    mkbar(r.against_pg,cv('--s2'),13);
    // Label the bar the number actually sits at — for 10 of 20 clubs the conceded
    // bar is the longer one, so printing corners *won* there described the wrong bar.
    const mx=Math.max(r.for_pg,r.against_pg);
    const vl=el("text",{x:X(mx)+6,y:y+rowH/2+1,class:"axis-lbl"});
    vl.textContent=mx.toFixed(2);svg.appendChild(vl);
  });
  banner(svg,W,H,title,sub,[{label:'Won',color:cv('--s3')},{label:'Conceded',color:cv('--s2')}]);
  $(sel).appendChild(svg);
}
function renderSP(){
  if(!SP)return;
  $("#spSec").style.display="";
  const T=SP.teams_latest, sl=SP.league;
  const topWin=T[0], mostExposed=[...T].sort((a,b)=>b.against_pg-a.against_pg)[0];
  $("#spIntro").innerHTML=`Corners are open-play set pieces (penalties excluded). "Won" = your attacking corners; "conceded" = defensive set-piece exposure. In ${SP.meta.latest}, <b>${topWin.team}</b> won the most corners (${topWin.for_pg}/game) and <b>${mostExposed.team}</b> faced the most (${mostExposed.against_pg}/game). ${SP.meta.note}`;
  $("#spKpis").innerHTML=
    `<div class="kpi"><div class="v">${sl[sl.length-1].corners_pg}</div><div class="l">Corners per match (${SP.meta.latest})</div><div class="d up">league-wide, both teams</div></div>`+
    `<div class="kpi"><div class="v">${topWin.for_pg}</div><div class="l">Most corners won &middot; ${topWin.team}</div><div class="d up">per game</div></div>`+
    `<div class="kpi"><div class="v">${mostExposed.against_pg}</div><div class="l">Most exposed &middot; ${mostExposed.team}</div><div class="d down">corners conceded/game</div></div>`+
    `<div class="kpi"><div class="v">${SP.notable_takers.length}</div><div class="l">Dual set-piece takers</div><div class="d up">corners + free kicks</div></div>`;
  spBars("#c_spteams",T,"Corners won vs conceded per game — "+SP.meta.latest,"Attacking vs defensive set-piece volume, by team");
  lineChart("#c_sptrend",sl.map(r=>({y:r.corners_pg,lab:r.season.slice(2),full:r.season,name:'Corners/match'})),
    {color:cv('--s1'),fmt:v=>v.toFixed(2),title:"Corners per match — league trend",sub:"Both teams combined, 2020/21 to "+SP.meta.latest});
  $("#sp_notable").innerHTML=SP.notable_takers.map(r=>
    `<div class="promo"><div class="n">${r.name}</div><div class="s">${r.team}<br>${r.roles}</div></div>`).join('');
  // takers table
  const rows=[...SP.takers];
  let h="<thead><tr><th>Club</th><th style='text-align:left'>Corners</th><th style='text-align:left'>Direct free kicks</th></tr></thead><tbody>";
  rows.forEach(r=>{h+=`<tr><td><b>${r.team}</b></td><td style='text-align:left'>${r.corner_taker||'&mdash;'}</td><td style='text-align:left'>${r.fk_taker||'&mdash;'}</td></tr>`;});
  $("#sp_takers").innerHTML=h+"</tbody>";
}

function renderSPG(){
  if(!SPG){ $("#spgBlock").style.display="none"; return; }
  $("#spgBlock").style.display="";
  const T=SPG.teams;
  const topFor=[...T].sort((a,b)=>b.gf-a.gf)[0];
  const topAg=[...T].sort((a,b)=>b.ga-a.ga)[0];
  const eff=T.filter(r=>r.gf>=5&&r.shots_per_goal_for!=null).sort((a,b)=>a.shots_per_goal_for-b.shots_per_goal_for)[0];
  $("#spgIntro").innerHTML=`Goals scored and conceded from set pieces (<b>corners + set pieces + direct free kicks</b>; penalties excluded), ${SPG.meta.season}. Source: ${SPG.meta.source}. "Per goal" = set-piece shots taken per set-piece goal &mdash; a lower number means more clinical. ${SPG.meta.note}`;
  $("#spgKpis").innerHTML=
    `<div class="kpi"><div class="v">${topFor.gf}</div><div class="l">Most set-piece goals &middot; ${topFor.team}</div><div class="d up">${topFor.shots_per_goal_for.toFixed(2)} SP shots per goal</div></div>`+
    `<div class="kpi"><div class="v">${topAg.ga}</div><div class="l">Most conceded &middot; ${topAg.team}</div><div class="d down">from set pieces</div></div>`+
    (eff?`<div class="kpi"><div class="v">${eff.shots_per_goal_for.toFixed(2)}</div><div class="l">Most clinical &middot; ${eff.team}</div><div class="d up">SP shots per goal &middot; 5+ goals only</div></div>`:``)+
    `<div class="kpi"><div class="v">${SPG.league.sp_goals}</div><div class="l">Set-piece goals, league-wide</div><div class="d up">from ${SPG.league.sp_shots} SP shots</div></div>`;
  const forRows=[...T].sort((a,b)=>b.gf-a.gf);
  const agRows=[...T].sort((a,b)=>b.ga-a.ga);
  hbars("#c_spgfor",forRows,{value:r=>r.gf,label:r=>r.team,color:cv('--s3'),
    title:"Set-piece goals SCORED — "+SPG.meta.season,sub:"Corners + set pieces + direct free kicks (no penalties)",
    tip:r=>`<b>${r.team}</b><div class="row"><span>Set-piece goals</span><b>${r.gf}</b></div><div class="row"><span>Set-piece shots</span><b>${r.sf}</b></div><div class="row"><span>Shots per goal</span><b>${r.shots_per_goal_for!=null?r.shots_per_goal_for.toFixed(2):'&mdash;'}</b></div><div class="row"><span>Set-piece xG</span><b>${r.xgf}</b></div>`});
  hbars("#c_spgagainst",agRows,{value:r=>r.ga,label:r=>r.team,color:cv('--s2'),
    title:"Set-piece goals CONCEDED — "+SPG.meta.season,sub:"Defensive set-piece exposure (no penalties)",
    tip:r=>`<b>${r.team}</b><div class="row"><span>Conceded (set pieces)</span><b>${r.ga}</b></div><div class="row"><span>Set-piece shots faced</span><b>${r.sa}</b></div><div class="row"><span>Shots per goal conceded</span><b>${r.shots_per_goal_against!=null?r.shots_per_goal_against.toFixed(2):'&mdash;'}</b></div><div class="row"><span>Set-piece xG against</span><b>${r.xga}</b></div>`});
  const effRows=[...T].filter(r=>r.shots_per_goal_for!=null).sort((a,b)=>a.shots_per_goal_for-b.shots_per_goal_for);
  effBars("#c_spgeff",effRows,"Set-piece shots needed per goal — "+SPG.meta.season,"Most clinical first · all 20 clubs · whiskers = 95% CI — overlapping intervals are indistinguishable");
}
function whisker(svg,X,lo,hi,max,y,color){
  const capH=4.4, x1=X(Math.max(0,lo)), clipped=hi>max, x2=clipped?X(max)-2:X(hi);
  svg.appendChild(el("line",{x1,x2,y1:y,y2:y,stroke:color,"stroke-width":1.3,"stroke-linecap":"round",opacity:.75}));
  svg.appendChild(el("line",{x1,x2:x1,y1:y-capH/2,y2:y+capH/2,stroke:color,"stroke-width":1.3,opacity:.75}));
  if(clipped){
    svg.appendChild(el("path",{d:`M ${x2-3} ${y-3.2} L ${x2+2} ${y} L ${x2-3} ${y+3.2}`,fill:"none",stroke:color,"stroke-width":1.3,"stroke-linecap":"round","stroke-linejoin":"round",opacity:.75}));
  }else{
    svg.appendChild(el("line",{x1:x2,x2,y1:y-capH/2,y2:y+capH/2,stroke:color,"stroke-width":1.3,opacity:.75}));
  }
}
function effBars(sel,rows,title,sub){
  const W=560,rowH=24,mT=74,mL=104,mR=54,H=mT+rows.length*rowH+22;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
  const max=Math.max(...rows.map(r=>Math.max(r.shots_per_goal_for,r.shots_per_goal_against)))*1.1;
  const X=v=>mL+(W-mL-mR)*v/max;
  rows.forEach((r,i)=>{
    const y=mT+i*rowH;
    const t=el("text",{x:mL-8,y:y+rowH/2+1,"text-anchor":"end",class:"val-lbl"});t.textContent=r.team;svg.appendChild(t);
    const tipHtml=`<b>${r.team}</b><div class="row"><span>Shots per goal &mdash; to score</span><b>${r.shots_per_goal_for.toFixed(2)} <span style="opacity:.6">${r.sp_for_ci_lo!=null&&r.sp_for_ci_hi!=null?`(95% CI ${r.sp_for_ci_lo.toFixed(1)}&ndash;${r.sp_for_ci_hi.toFixed(1)}, n=${r.gf} goals)`:`(n=${r.gf} goals)`}</span></b></div><div class="row"><span>Shots per goal &mdash; to concede</span><b>${r.shots_per_goal_against!=null?`${r.shots_per_goal_against.toFixed(2)} <span style="opacity:.6">(95% CI ${r.sp_against_ci_lo.toFixed(1)}&ndash;${r.sp_against_ci_hi.toFixed(1)}, n=${r.ga} goals)</span>`:'&mdash;'}</b></div>`;
    const w1=Math.max(2,X(r.shots_per_goal_for)-mL);
    const rc1=el("rect",{x:mL,y:y+3,width:w1,height:7,rx:3,fill:cv('--s3')});
    rc1.addEventListener("mousemove",e=>showTip(tipHtml,e));rc1.addEventListener("mouseleave",hideTip);svg.appendChild(rc1);
    const vl1=el("text",{x:mL+w1+6,y:y+3+6,class:"axis-lbl"});vl1.textContent=r.shots_per_goal_for.toFixed(2);svg.appendChild(vl1);
    if(r.sp_for_ci_lo!=null)whisker(svg,X,r.sp_for_ci_lo,r.sp_for_ci_hi,max,y+6.5,cv('--ink-2'));
    if(r.shots_per_goal_against!=null){
      const w2=Math.max(2,X(r.shots_per_goal_against)-mL);
      const rc2=el("rect",{x:mL,y:y+13,width:w2,height:7,rx:3,fill:cv('--s2')});
      rc2.addEventListener("mousemove",e=>showTip(tipHtml,e));rc2.addEventListener("mouseleave",hideTip);svg.appendChild(rc2);
      const vl2=el("text",{x:mL+w2+6,y:y+13+6,class:"axis-lbl"});vl2.textContent=r.shots_per_goal_against.toFixed(2);svg.appendChild(vl2);
      if(r.sp_against_ci_lo!=null)whisker(svg,X,r.sp_against_ci_lo,r.sp_against_ci_hi,max,y+16.5,cv('--ink-2'));
    }
  });
  banner(svg,W,H,title,sub,[{label:'To score',color:cv('--s3')},{label:'To concede',color:cv('--s2')},{label:'95% CI',color:cv('--ink-2')}]);
  $(sel).appendChild(svg);
}

// ---------- per-chart save / copy ----------
const ICON_DL="<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M12 3v12'/><path d='M7 10l5 5 5-5'/><path d='M5 21h14'/></svg>";
const ICON_COPY="<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='9' y='9' width='11' height='11' rx='2'/><path d='M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1'/></svg>";
const ICON_CHECK="<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'><path d='M4 12l5 5L20 6'/></svg>";
function chartName(svg){
  const t=svg.querySelector('.chart-h')?.textContent||'chart';
  return t.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,'')+'.png';
}
function svgToCanvas(svg,scale=3){
  return new Promise((resolve,reject)=>{
    const vb=svg.viewBox.baseVal;
    const w=(vb&&vb.width)||svg.clientWidth||600, h=(vb&&vb.height)||svg.clientHeight||300;
    const clone=svg.cloneNode(true);
    clone.setAttribute('xmlns','http://www.w3.org/2000/svg');
    clone.setAttribute('width',w); clone.setAttribute('height',h);
    // exported SVG is serialized standalone — it has no access to the page's
    // <style> rules or CSS custom properties, so bake the current theme's
    // resolved colors/fonts in directly (otherwise text falls back to black serif).
    const FONT='system-ui,-apple-system,"Segoe UI",sans-serif';
    const style=document.createElementNS(NS,'style');
    style.textContent=`
      text{font-family:${FONT}}
      .chart-h{fill:${cv('--ink')};font-size:15.5px;font-weight:720;letter-spacing:-.01em}
      .chart-sub{fill:${cv('--muted')};font-size:11.5px}
      .lgnd{fill:${cv('--ink-2')};font-size:11.5px;font-weight:550}
      .wm{fill:${cv('--muted')};font-size:11.5px;font-weight:750;opacity:.5;letter-spacing:.02em}
      .axis-lbl{fill:${cv('--muted')};font-size:11px}
      .val-lbl{fill:${cv('--ink')};font-size:11px;font-weight:600}
    `;
    clone.insertBefore(style,clone.firstChild);
    const xml=new XMLSerializer().serializeToString(clone);
    const img=new Image();
    img.onload=()=>{
      const canvas=document.createElement('canvas');
      canvas.width=w*scale; canvas.height=h*scale;
      const ctx=canvas.getContext('2d');
      ctx.fillStyle=cv('--surface'); ctx.fillRect(0,0,canvas.width,canvas.height);
      ctx.scale(scale,scale); ctx.drawImage(img,0,0,w,h);
      resolve(canvas);
    };
    img.onerror=reject;
    img.src='data:image/svg+xml;base64,'+btoa(unescape(encodeURIComponent(xml)));
  });
}
function flashBtn(btn,html){
  const orig=btn.innerHTML; btn.innerHTML=html; btn.disabled=true;
  setTimeout(()=>{btn.innerHTML=orig; btn.disabled=false;},1300);
}
async function downloadSVG(svg){
  const canvas=await svgToCanvas(svg);
  canvas.toBlob(blob=>{
    const a=document.createElement('a');
    a.href=URL.createObjectURL(blob); a.download=chartName(svg); a.click();
  });
}
async function copySVG(svg,btn){
  try{
    if(!navigator.clipboard||!window.ClipboardItem) throw new Error('no clipboard api');
    const canvas=await svgToCanvas(svg);
    await new Promise((res,rej)=>canvas.toBlob(async blob=>{
      try{ await navigator.clipboard.write([new ClipboardItem({'image/png':blob})]); res(); }
      catch(e){ rej(e); }
    },'image/png'));
    flashBtn(btn,ICON_CHECK);
  }catch(e){ await downloadSVG(svg); flashBtn(btn,ICON_DL); }
}
function addChartActions(){
  document.querySelectorAll('[id^="c_"]').forEach(div=>{
    const card=div.closest('.card');
    if(!card||card.querySelector('.chart-actions'))return;
    card.classList.add('chart-card');
    const bar=document.createElement('div');
    bar.className='chart-actions';
    bar.innerHTML=`<button class="icon-btn" type="button" title="Copy image" aria-label="Copy chart image">${ICON_COPY}</button>`+
                  `<button class="icon-btn" type="button" title="Download PNG" aria-label="Download chart as PNG">${ICON_DL}</button>`;
    card.insertBefore(bar,card.firstChild);
    const [copyBtn,dlBtn]=bar.querySelectorAll('button');
    copyBtn.addEventListener('click',()=>{const svg=div.querySelector('svg'); if(svg)copySVG(svg,copyBtn);});
    dlBtn.addEventListener('click',()=>{const svg=div.querySelector('svg'); if(svg)downloadSVG(svg);});
  });
}

renderMain();
renderDefcon();
renderSP();
renderSPG();
addChartActions();

// ---------- theme toggle ----------
$("#themeBtn").onclick=()=>{
  const cur=document.documentElement.getAttribute("data-theme");
  const dark=cur?cur==="dark":matchMedia("(prefers-color-scheme:dark)").matches;
  document.documentElement.setAttribute("data-theme",dark?"light":"dark");
  document.querySelectorAll("[id^=c_]").forEach(n=>n.innerHTML="");
  renderMain();
  renderDefcon();
  renderSP();
  renderSPG();
  addChartActions();
};
</script>
</body>
</html>
"""

out = HTML.replace("__DATA_JSON__", json.dumps(data))
out = out.replace("__DEFCON_JSON__", json.dumps(defcon))
out = out.replace("__SP_JSON__", json.dumps(setpieces))
out = out.replace("__SPG_JSON__", json.dumps(spgoals))
with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
    f.write(out)
print("Wrote docs/index.html (", len(out), "bytes )")
