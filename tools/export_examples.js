/**
 * Regenerate the README preview images in docs/examples/.
 *
 *   node tools/export_examples.js            # after running build_dashboard.py
 *
 * Why this exists: those PNGs are screenshots, so they go stale silently whenever
 * a chart title, label or number changes — and they did. This runs the dashboard's
 * OWN chart code out of docs/index.html under a minimal DOM shim, serializes each
 * chart to a standalone styled SVG, then screenshots it with headless Chrome/Edge.
 * Because the drawing code is the real one, the images cannot drift from the
 * dashboard; only this file's chart list can go out of date.
 *
 * Requires: Node, and Chrome or Edge installed (override with CHROME_PATH).
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'docs', 'examples');
const TMP = fs.mkdtempSync(path.join(require('os').tmpdir(), 'pl-charts-'));

// Which dashboard charts become README images. Selector -> output basename.
const CHARTS = [
  { sel: '#c_cs',      name: 'clean-sheets-per-game' },
  { sel: '#c_btts',    name: 'both-teams-to-score' },
  { sel: '#c_dist',    name: 'goals-per-match-poisson' },
  { sel: '#c_teams',   name: 'who-to-trust-2025-26' },
  { sel: '#c_ha',      name: 'home-advantage' },
  { sel: '#c_dcpts',   name: 'defcon-top15' },
  { sel: '#c_cbittop', name: 'defensive-actions-top15' },
  { sel: '#c_spteams', name: 'set-pieces-corners' },
  { sel: '#c_spgfor',  name: 'set-piece-goals-scored' },
  { sel: '#c_spgeff',  name: 'set-piece-efficiency' },
];

const html = fs.readFileSync(path.join(ROOT, 'docs', 'index.html'), 'utf8');
const css = html.match(/<style>([\s\S]*?)<\/style>/)[1];
const script = html.match(/<script[^>]*>([\s\S]*?)<\/script>/)[1];

// Resolve the light-theme CSS custom properties so cv() returns the real palette.
const VARS = {};
for (const m of css.match(/:root\s*\{([\s\S]*?)\}/)[1].matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)) {
  VARS[m[1]] = m[2].trim();
}

const SVG_NS = 'http://www.w3.org/2000/svg';
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const escAttr = s => esc(s).replace(/"/g, '&quot;');

class Node {
  constructor(tag) {
    this.tag = tag; this.attrs = {}; this.kids = []; this._text = ''; this._html = '';
    this.style = { setProperty() {} };
    this.classList = { add() {}, remove() {}, toggle() {} };
    this.dataset = {};
  }
  setAttribute(k, v) { this.attrs[k] = v; }
  getAttribute(k) { return this.attrs[k] ?? null; }
  appendChild(c) { this.kids.push(c); return c; }
  removeChild(c) { this.kids = this.kids.filter(x => x !== c); }
  insertBefore(c) { this.kids.unshift(c); return c; }
  addEventListener() {} removeEventListener() {}
  set textContent(v) { this._text = v; } get textContent() { return this._text; }
  set innerHTML(v) { this._html = v; if (v === '') this.kids = []; } get innerHTML() { return this._html; }
  querySelector() { return null; } querySelectorAll() { return []; }
  closest() { return null; } contains() { return false; }
  getBoundingClientRect() { return { width: 640, height: 360, left: 0, top: 0 }; }
  cloneNode() { return this; } remove() {} focus() {} insertAdjacentHTML() {}
  get firstChild() { return this.kids[0] || null; }
  serialize() {
    const a = Object.entries(this.attrs).map(([k, v]) => ` ${k}="${escAttr(v)}"`).join('');
    // Deliberately not a truthiness test: textContent is legitimately the number 0
    // on the goal-distribution x-axis, and a falsy check silently drops that label.
    const has = this._text !== '' && this._text !== null && this._text !== undefined;
    return `<${this.tag}${a}>${(has ? esc(this._text) : '') + this.kids.map(k => k.serialize()).join('')}</${this.tag}>`;
  }
}

const hosts = {};
global.window = global;
global.document = {
  createElementNS: (ns, t) => new Node(t),
  createElement: t => new Node(t),
  createTextNode: t => { const n = new Node('#text'); n._text = t; n.serialize = () => esc(t); return n; },
  querySelector: sel => (hosts[sel] ||= new Node('div')),
  querySelectorAll: () => [],
  getElementById: () => new Node('div'),
  addEventListener() {},
  documentElement: {
    style: { setProperty() {} }, getAttribute: () => 'light', setAttribute() {},
    classList: { add() {}, remove() {} },
  },
  body: new Node('body'), head: new Node('head'),
};
global.getComputedStyle = () => ({ getPropertyValue: n => VARS[n.trim()] || '#000000' });
global.matchMedia = () => ({ matches: false, addEventListener() {}, addListener() {} });
global.localStorage = { getItem: () => null, setItem() {} };
global.requestAnimationFrame = f => { f(0); return 1; };
global.ResizeObserver = class { observe() {} disconnect() {} };
global.navigator = { clipboard: { writeText: () => Promise.resolve() }, userAgent: 'node' };
global.Blob = class {};
global.URL = { createObjectURL: () => 'blob:x', revokeObjectURL() {} };

eval(script);

// Only the classes the SVGs reference, so an exported file stands alone.
const SVG_CSS = `
  .chart-h{fill:${VARS['--ink']};font-size:16px;font-weight:700}
  .chart-sub{fill:${VARS['--muted']};font-size:11px}
  .lgnd{fill:${VARS['--ink-2']};font-size:11px}
  .wm{fill:${VARS['--muted']};font-size:11px;font-weight:700;opacity:.5}
  .axis-lbl{fill:${VARS['--muted']};font-size:11px}
  .val-lbl{fill:${VARS['--ink']};font-size:11px;font-weight:600}
  text{font-family:'Segoe UI',system-ui,-apple-system,sans-serif}
`;

function findBrowser() {
  const cands = [process.env.CHROME_PATH,
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    '/usr/bin/google-chrome', '/usr/bin/chromium',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ].filter(Boolean);
  const hit = cands.find(p => { try { return fs.statSync(p).isFile(); } catch { return false; } });
  if (!hit) throw new Error('No Chrome/Edge found — set CHROME_PATH to the executable');
  return hit;
}

const browser = findBrowser();
let missing = 0;
for (const { sel, name } of CHARTS) {
  const svg = (hosts[sel]?.kids || []).find(k => k.tag === 'svg');
  if (!svg) { console.error(`  MISSING ${sel} — chart list out of date?`); missing++; continue; }
  const [, , w, h] = (svg.attrs.viewBox || '0 0 600 400').split(/\s+/).map(Number);
  const body = svg.serialize()
    .replace(/^<svg/, `<svg xmlns="${SVG_NS}" width="${w}" height="${h}"`)
    .replace(/>/, `><style>${SVG_CSS}</style>`);
  const page = path.join(TMP, name + '.html');
  fs.writeFileSync(page, `<!doctype html><meta charset="utf-8"><style>
    html,body{margin:0;padding:0;background:transparent}
    .card{background:${VARS['--surface']};border:1px solid ${VARS['--border']};border-radius:14px;
          padding:6px 10px 4px;width:${w + 20}px;box-sizing:border-box}
    svg{display:block;width:100%;height:auto}
    </style><div class="card">${body}</div>`);
  execFileSync(browser, ['--headless=new', '--disable-gpu', '--hide-scrollbars',
    '--force-device-scale-factor=2', '--default-background-color=00000000',
    `--window-size=${w + 20},${h + 14}`,
    `--screenshot=${path.join(OUT, name + '.png')}`, 'file:///' + page.replace(/\\/g, '/'),
  ], { stdio: 'ignore' });
  console.log(`  ${name}.png  ${(w + 20) * 2}x${(h + 14) * 2}`);
}
fs.rmSync(TMP, { recursive: true, force: true });
console.log(missing ? `\n${missing} chart(s) missing — fix CHARTS in this file` : '\nAll example images regenerated.');
process.exitCode = missing ? 1 : 0;
