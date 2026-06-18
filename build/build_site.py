#!/usr/bin/env python3
"""Generate a single self-contained index.html (a 'oner') — database-free,
fully client-side searchable archive of Luke Labern's writing."""
import json, re
from collections import Counter

ROOT = "/Users/labern/Desktop/Clean"
OUT = f"{ROOT}/LegacyArchive"
records = json.load(open(f"{OUT}/_records.json"))

PROSE_TYPES = {"Short Story", "Novel", "Extract"}

def normalize_prose(html):
    # Collapse runs of 2+ <br> into paragraph breaks
    html = re.sub(r'(\s*<br\s*/?>\s*){2,}', '</p><p>', html, flags=re.I)
    # Remove stray single <br> between block elements (redundant whitespace)
    html = re.sub(r'(</p>)\s*(<br\s*/?>\s*)+(<p)', r'\1\3', html, flags=re.I)
    # Remove leading <br> at start of content
    html = re.sub(r'^(\s*<br\s*/?>\s*)+', '', html, flags=re.I)
    # Clean up empty <p> tags
    html = re.sub(r'<p[^>]*>\s*</p>', '', html, flags=re.I)
    return html.strip()

# trim payload to what the page needs
works = []
for r in records:
    content = r["content"]
    if r["type"] in PROSE_TYPES:
        content = normalize_prose(content)
    works.append({
        "t": r["title"],
        "y": r["type"],
        "g": r["tags"],
        "yr": r["year"],
        "d": r["date"],
        "s": r["slug"],
        "x": r["excerpt"],
        "w": r["words"],
        "txt": r["text"],
        "c": content,
    })

types = [t for t, _ in Counter(w["y"] for w in works).most_common()]
years = sorted({w["yr"] for w in works if w["yr"]})
yr_lo, yr_hi = (years[0], years[-1]) if years else ("", "")

data_json = json.dumps(works, ensure_ascii=False)
data_json = data_json.replace("</", "<\\/").replace(" ", "\\u2028").replace(" ", "\\u2029")

HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="zesty">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Legacy — The Writing of Luke Labern</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Afacad+Flux:wght@100..1000&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#ffffff; --bg2:#f6f5f2; --ink:#1c1a17; --ink2:#56504a; --ink3:#8a8278;
  --line:#e7e3dc; --line2:#d8d2c8; --accent:#d23c77; --accent-ink:#a51f57;
  --mark:#ffd9e8; --card:#ffffff; --shadow:0 1px 2px rgba(20,15,10,.05),0 10px 30px rgba(20,15,10,.05);
  --serif:"Libre Baskerville",Georgia,"Times New Roman",serif;
  --ui:"Afacad Flux",ui-sans-serif,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
  --maxw:1080px;
}
[data-theme="dark"]{
  --bg:#141210; --bg2:#1b1813; --ink:#efe9df; --ink2:#c4bbac; --ink3:#8d8474;
  --line:#2c281f; --line2:#3a3429; --accent:#f06aa0; --accent-ink:#f48cb6;
  --mark:#5a2740; --card:#1c1813; --shadow:0 1px 2px rgba(0,0,0,.3),0 12px 34px rgba(0,0,0,.4);
}
[data-theme="zesty"]{
  --bg:#0c0a1f; --bg2:rgba(48,43,99,0.45); --ink:#e8e8f0; --ink2:#b6b6c9; --ink3:#7070a0;
  --line:rgba(94,234,212,0.18); --line2:rgba(94,234,212,0.08); --accent:#5eead4; --accent-ink:#2dd4bf;
  --mark:rgba(94,234,212,0.22); --card:rgba(255,255,255,0.04); --shadow:0 4px 32px rgba(94,234,212,0.08),0 0 0 1px rgba(94,234,212,0.05);
}
@keyframes zesty-drift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
@keyframes zesty-shimmer{to{background-position:300% center}}
[data-theme="zesty"] body{background:linear-gradient(-45deg,#0f0c29,#302b63,#24243e,#1a1a2e);background-size:400% 400%;animation:zesty-drift 18s ease infinite}
[data-theme="zesty"] .topbar{background:rgba(12,10,31,0.82);border-bottom-color:rgba(94,234,212,0.12)}
[data-theme="zesty"] .brand{background:linear-gradient(90deg,#5eead4,#a78bfa,#f472b6,#5eead4);background-size:300% auto;-webkit-background-clip:text;background-clip:text;color:transparent;animation:zesty-shimmer 6s linear infinite;padding:0 0.05em}
[data-theme="zesty"] .hero h1{background:linear-gradient(90deg,#f472b6,#a78bfa,#5eead4,#f472b6);background-size:300% auto;-webkit-background-clip:text;background-clip:text;color:transparent;animation:zesty-shimmer 8s linear infinite;padding:0 0.06em 0.18em;display:inline-block;line-height:1.1}
[data-theme="zesty"] .card{backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}
[data-theme="zesty"] .card:hover{box-shadow:0 0 28px rgba(94,234,212,0.14),0 0 0 1px rgba(94,234,212,0.3)}
[data-theme="zesty"] .searchbox input{background:rgba(255,255,255,0.05);border-color:rgba(94,234,212,0.2)}
[data-theme="zesty"] .searchbox input:focus{border-color:#5eead4;box-shadow:0 0 0 3px rgba(94,234,212,0.1)}
[data-theme="zesty"] .cloud button{background:rgba(255,255,255,0.04);backdrop-filter:blur(4px)}
[data-theme="zesty"] .cloud button:hover{box-shadow:0 0 14px rgba(94,234,212,0.12)}
[data-theme="zesty"] .browse-switch{background:rgba(255,255,255,0.06);backdrop-filter:blur(6px)}
[data-theme="zesty"] mark{background:rgba(94,234,212,0.25);color:#e8e8f0}
[data-theme="zesty"] .reader{background:rgba(12,10,31,0.6);backdrop-filter:blur(12px);border-radius:16px;margin-top:24px;padding-left:60px;padding-right:60px}
[data-theme="zesty"] .reader.story{padding-left:60px;padding-right:60px}
.iconbtn.zesty-on{background:linear-gradient(90deg,#5eead4,#a78bfa);color:#0c0a1f;border-color:transparent;font-weight:600}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--serif);font-size:18px;line-height:1.6;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:var(--accent-ink);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:2px}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.ui{font-family:var(--ui)}

/* topbar */
.topbar{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:saturate(140%) blur(8px);border-bottom:1px solid var(--line)}
.topbar .wrap{display:flex;align-items:center;gap:16px;height:58px}
.brand{font-weight:700;letter-spacing:.04em;cursor:pointer;font-size:1rem}
.brand .dot{color:var(--accent)}
.topbar .spacer{flex:1}
.iconbtn{font-family:var(--ui);font-size:.82rem;cursor:pointer;background:transparent;border:1px solid var(--line2);color:var(--ink2);padding:6px 13px;border-radius:999px;transition:.15s}
.iconbtn:hover{border-color:var(--accent);color:var(--accent)}

/* hero */
.hero{padding:76px 0 30px;text-align:center}
.hero h1{font-size:clamp(3.2rem,10vw,6.4rem);margin:0;line-height:1.04;letter-spacing:-.01em;font-weight:700}
.hero .tag{font-family:var(--ui);text-transform:uppercase;letter-spacing:.3em;font-size:.88rem;color:var(--ink3);margin:34px 0 0}
.hero .stats{margin-top:18px;color:var(--ink3);font-style:italic;font-size:1rem}

/* search */
.searchbox{position:relative;max-width:680px;margin:42px auto 4px}
.searchbox input{width:100%;font-family:var(--serif);font-size:0.9rem;padding:17px 50px 17px 22px;border-radius:14px;border:1px solid var(--line2);background:var(--card);color:var(--ink);box-shadow:var(--shadow);outline:none;transition:border-color .15s}
.searchbox input:focus{border-color:var(--accent)}
.searchbox .clear{position:absolute;right:14px;top:50%;transform:translateY(-50%);cursor:pointer;color:var(--ink3);font-size:1.4rem;line-height:1;background:none;border:none;display:none}
.searchbox.has-text .clear{display:block}
.chip-suggest{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:14px}
.chip-suggest button{font-family:var(--ui);font-size:.8rem;cursor:pointer;background:var(--bg2);border:1px solid var(--line);color:var(--ink2);padding:5px 13px;border-radius:999px;transition:.15s}
.chip-suggest button:hover{border-color:var(--accent);color:var(--accent)}

/* meta + filters */
.resultmeta{font-family:var(--ui);font-size:.78rem;letter-spacing:.05em;text-transform:uppercase;color:var(--ink3);margin:40px 0 12px;display:flex;align-items:center;gap:12px;border-bottom:1px solid var(--line);padding-bottom:10px}
.resultmeta .count{color:var(--accent);font-weight:600}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 4px}
.filters button{font-family:var(--ui);font-size:.8rem;cursor:pointer;background:transparent;border:1px solid var(--line2);color:var(--ink2);padding:6px 13px;border-radius:999px;transition:.15s}
.filters button:hover{border-color:var(--accent);color:var(--accent)}
.filters button.active{background:var(--accent);border-color:var(--accent);color:#fff}

/* grid */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px;margin:18px 0 60px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:26px 28px;box-shadow:var(--shadow);cursor:pointer;display:flex;flex-direction:column;gap:9px;transition:transform .12s,border-color .12s;min-width:0;overflow-wrap:anywhere;aspect-ratio:1/1;overflow:hidden}
.card:hover{transform:translateY(-3px);border-color:var(--accent)}
.card .ribbon{font-family:var(--ui);font-size:.66rem;letter-spacing:.13em;text-transform:uppercase;color:var(--accent);font-weight:600}
.card h3{margin:0;font-size:1.14rem;line-height:1.2;font-weight:700}
.card .snippet{color:var(--ink2);font-size:.84rem;line-height:1.5}
.card .foot{font-family:var(--ui);font-size:.74rem;color:var(--ink3);display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:auto}
.card .why{color:var(--accent-ink)}
mark{background:var(--mark);color:inherit;padding:0 2px;border-radius:3px}
.empty{text-align:center;padding:60px 20px;color:var(--ink3);font-style:italic}

/* browse */
.section-title{font-family:var(--ui);font-size:.78rem;letter-spacing:.15em;text-transform:uppercase;color:var(--ink3);margin:44px 0 14px}
.browse-header{font-family:var(--ui);font-size:.96rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink3);margin:44px 0 14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.browse-switch{display:inline-flex;background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:3px;gap:2px}
.browse-tab{font-family:var(--ui);font-size:.96rem;letter-spacing:.06em;text-transform:uppercase;background:none;border:none;border-radius:5px;padding:5px 14px;cursor:pointer;color:var(--ink2);transition:.15s;line-height:1}
.browse-tab:hover{color:var(--accent)}
.browse-tab.active{color:#fff}
.browse-tab.active[data-mode="form"]{background:var(--accent)}
.browse-tab.active[data-mode="year"]{background:#a78bfa}
.browse-tab.active[data-mode="theme"]{background:#5eead4;color:#1a4a44}
/* instagram toast */
#igToast{position:fixed;bottom:28px;left:28px;max-width:320px;background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:14px 44px 14px 18px;font-family:var(--ui);font-size:.82rem;color:var(--ink2);line-height:1.5;box-shadow:0 8px 32px rgba(0,0,0,.35),0 0 0 1px rgba(0,0,0,.08);opacity:0;transform:translateY(10px);pointer-events:none;transition:opacity .4s,transform .4s;z-index:99999;isolation:isolate}
#igToast.visible{opacity:1;transform:translateY(0);pointer-events:auto}
#igToast a{color:var(--accent);text-decoration:underline;text-underline-offset:2px}
#igToast .toast-x{position:absolute;top:10px;right:12px;background:none;border:none;cursor:pointer;color:var(--ink3);font-size:1.1rem;line-height:1;padding:2px 4px;border-radius:4px;transition:color .15s}
#igToast .toast-x:hover{color:var(--ink)}
.cloud{display:flex;flex-wrap:wrap;gap:10px}
.cloud button{font-family:var(--serif);cursor:pointer;background:var(--bg2);border:1px solid var(--line);color:var(--ink2);border-radius:10px;padding:7px 14px;transition:.15s;font-size:.96rem}
.cloud button:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-2px)}
.cloud button.active{background:var(--accent);border-color:var(--accent);color:#fff}
.cloud button.active .n{color:rgba(255,255,255,.75)}
.cloud button .n{color:var(--ink3);font-size:.8rem;margin-left:6px}

/* reader */
.reader{max-width:880px;margin:0 auto;padding:46px 24px 90px 120px}
.reader.story{max-width:890px;padding:46px 48px 90px 48px}
.reader.story .prose{font-size:clamp(0.80rem,0.60rem + 0.75vw,1.02rem);line-height:1.8}
.reader .back{font-family:var(--ui);font-size:.82rem;color:var(--ink3);display:inline-block;margin-bottom:32px;cursor:pointer}
.reader .ribbon{font-family:var(--ui);font-size:.72rem;letter-spacing:.15em;text-transform:uppercase;color:var(--accent);font-weight:600;margin-bottom:10px}
.reader h1{font-size:clamp(2rem,5vw,3rem);line-height:1.12;margin:0 0 14px;font-weight:700}
.reader .meta{font-family:var(--ui);font-size:.82rem;color:var(--ink3);display:flex;flex-wrap:wrap;gap:8px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:20px;margin-bottom:34px}
.reader .meta .sep{opacity:.35;user-select:none}
.reader .meta .tg{cursor:pointer}
.reader .meta .tg:hover{color:var(--accent)}
.prose{font-size:clamp(0.84rem, 0.64rem + 0.81vw, 1.10rem);line-height:1.85}
.prose p{margin:0 0 1.3em}
.prose em,.prose i{font-style:italic}
.prose strong,.prose b{font-weight:700}
.prose h1,.prose h2,.prose h3{font-weight:700;line-height:1.2;margin:1.6em 0 .5em}
.prose h1{font-size:1.7rem}.prose h2{font-size:1.4rem}.prose h3{font-size:1.2rem}
.prose blockquote{margin:1.4em 0;padding:.2em 0 .2em 1.2em;border-left:3px solid var(--accent);color:var(--ink2);font-style:italic}
.prose img{max-width:100%;height:auto;border-radius:6px}
.prose pre{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.85rem;background:var(--bg2);padding:16px;border-radius:10px;overflow:auto;border:1px solid var(--line)}
.prose a{text-decoration:underline;text-underline-offset:2px}
.prose hr{border:none;border-top:1px solid var(--line);margin:2em 0}
.related{border-top:1px solid var(--line);margin-top:56px;padding-top:26px}
.related .grid{grid-template-columns:repeat(auto-fill,minmax(230px,1fr));margin-bottom:0}
footer.site{border-top:1px solid var(--line);padding:30px 0;margin-top:30px;font-family:var(--ui);font-size:.8rem;color:var(--ink3);text-align:center;line-height:1.7}
#scrollTop{position:fixed;bottom:28px;right:28px;width:44px;height:44px;border-radius:50%;background:var(--accent);border:none;color:#fff;font-size:.85rem;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .2s,transform .2s;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 12px rgba(0,0,0,.25);z-index:900}
#scrollTop.visible{opacity:1;pointer-events:auto}
#scrollTop:hover{transform:translateY(-3px)}
.scan-btn{font-family:var(--ui);font-size:.78rem;cursor:pointer;background:var(--bg2);border:1px solid var(--line2);color:var(--ink2);padding:5px 13px;border-radius:999px;transition:.15s}
.scan-btn:hover{border-color:var(--accent);color:var(--accent)}
.scan-btn.on{background:var(--accent);border-color:var(--accent);color:#fff}
.scan-view{font-size:clamp(0.84rem, 0.64rem + 0.81vw, 1.10rem);line-height:1.85;font-family:var(--serif)}
.scan-view b{font-weight:700;font-style:normal}
.scan-meta{margin-top:2.2rem;padding:1.1rem 1.3rem;background:var(--bg2);border:1px solid var(--line);border-radius:12px;font-family:var(--ui);font-size:.84rem;color:var(--ink2);line-height:1.7}
.scan-meta strong{color:var(--ink)}
.hidden{display:none!important}
@media (max-width:600px){body{font-size:17px}.hero{padding:40px 0 16px}.grid{grid-template-columns:1fr}.reader{padding-left:24px}}
#bgStars{position:fixed;inset:0;pointer-events:none;z-index:0;opacity:0;transition:opacity 1.2s}
[data-stars="1"] #bgStars{opacity:1}
</style>
</head>
<body>
<canvas id="bgStars"></canvas>
<div class="topbar"><div class="wrap">
  <span class="brand" id="brand">Legacy<span class="dot">.</span> / Labern</span>
  <span class="spacer"></span>
  <button class="iconbtn" id="zestyToggle">Zesty</button>
  <button class="iconbtn" id="themeToggle">Dark</button>
</div></div>

<!-- HOME -->
<main id="home">
  <div class="hero wrap">
    <h1>Legacy</h1>
    <p class="tag">The collected writing of Luke Labern</p>
    <p class="stats" id="heroStats"></p>
    <div class="searchbox" id="sbox">
      <input id="q" type="text" autocomplete="off" spellcheck="false"
        placeholder="Search by theme / form — e.g. sonnet death, love">
      <button class="clear" id="clear" title="Clear">&times;</button>
    </div>
    <div class="chip-suggest" id="suggest"></div>
  </div>
  <div class="wrap">
    <div id="resultsArea"></div>
    <div id="browseArea"></div>
  </div>
  <button id="scrollTop" aria-label="Back to top">↑</button>
  <footer class="site"><div class="wrap">
    &copy; Luke Labern, 2008&ndash;2026 &middot; __N__ works &middot; A static, database-free archive &middot; everything here is searchable and clickable.
  </div></footer>
</main>

<!-- READER -->
<article id="reader" class="reader hidden"></article>

<script>
const WORKS = __DATA__;
const TYPES = __TYPES__;
// Only literary forms get their own browse-by-form chip. Everything else
// (Blog, Album Review, Journalism, Song, …) is still reachable via "All".
const LITERARY = ["Poem","Sonnet","Ode","Short Story","Novel","Essay","Play","Extract"];
WORKS.forEach((w,i)=>{w.i=i; w._t=(w.t||'').toLowerCase(); w._txt=(w.txt||'').toLowerCase(); w._g=(w.g||[]).map(s=>s.toLowerCase());});

/* ---------- theme lexicon: query word -> related words ---------- */
const THEMES = {
  death:["death","dead","dying","die","died","mortality","mortal","grave","graves","grief","mourning","mourn","funeral","corpse","oblivion","decay","perish","perished","tomb","ashes","dust","departed","afterlife","eulogy","suicide","kill","killed","loss"],
  love:["love","loved","loving","lover","beloved","romance","romantic","heart","hearts","desire","passion","affection","longing","yearning","tender","kiss","embrace","devotion","intimacy","adore"],
  time:["time","times","temporal","clock","hours","days","years","eternity","eternal","moment","moments","past","future","memory","memories","fleeting","ephemeral","transient","ageing","aging","nostalgia"],
  god:["god","gods","religion","religious","faith","divine","heaven","hell","prayer","pray","soul","spirit","sacred","holy","worship","sin","salvation","christ","jesus","atheism","atheist","belief","biblical","scripture","church"],
  meaning:["meaning","meaningless","meaninglessness","nihilism","nihilist","nihilistic","purpose","purposeless","void","absurd","absurdity","existence","existential","existentialism","nothingness","nothing","emptiness","futility","futile"],
  freedom:["freedom","free","liberty","liberation","choice","choices","will","autonomy","escape","bound","chains","prison","captive","cage"],
  nature:["nature","sky","sea","ocean","earth","tree","trees","forest","flower","flowers","rain","sun","moon","stars","star","wind","storm","river","mountain","mountains","garden","seasons","autumn","winter","spring","summer","snow","leaves"],
  mind:["mind","madness","mad","insanity","insane","sanity","thought","thoughts","consciousness","reason","logic","dream","dreams","sleep","nightmare","obsession","ocd","anxiety","depression","despair","melancholy"],
  music:["music","song","songs","sound","sounds","melody","rhythm","silence","note","notes","album","albums","guitar","voice","singing","sing","harmony"],
  drugs:["drug","drugs","marijuana","weed","cannabis","high","codeine","opiate","opiates","intoxication","addiction","sober","sobriety","pill","pills"],
  self:["self","identity","ego","authenticity","authentic","individual","loneliness","lonely","alone","alienation","solitude","isolation","mirror","reflection"],
  suffering:["suffering","suffer","pain","painful","agony","torment","torture","misery","miserable","anguish","hurt","wound","scar","struggle","sorrow"],
  beauty:["beauty","beautiful","sublime","grace","graceful","elegance","wonder","awe","radiant","light","glow"],
  war:["war","battle","fight","soldier","blood","violence","violent","conflict","weapon","enemy","death"],
  hope:["hope","hopeful","redemption","redeem","salvation","rebirth","renewal","dawn","light","faith","optimism"],
  fear:["fear","afraid","terror","dread","horror","panic","fright","scared","phobia"],
  body:["body","flesh","skin","blood","bone","bones","breath","heartbeat","veins","mortal"],
  sex:["sex","sexual","lust","desire","naked","erotic","seduction","flesh"],
  money:["money","wealth","rich","poor","poverty","greed","capitalism","possessions","success","ambition"],
  writing:["writing","words","language","poem","poetry","poet","story","novel","prose","book","page","pen","author","literature","literary"],
};
const WORD2THEME = {};
for(const k in THEMES){ for(const w of THEMES[k]){ (WORD2THEME[w]=WORD2THEME[w]||[]).push(k); } }

const TYPEWORDS = {
  sonnet:"Sonnet", sonnets:"Sonnet", poem:"Poem", poems:"Poem", poetry:"Poem",
  ode:"Ode", odes:"Ode", song:"Song", songs:"Song", lyric:"Song", lyrics:"Song",
  story:"Short Story", stories:"Short Story", "short story":"Short Story", fiction:"Short Story",
  essay:"Essay", essays:"Essay", philosophy:"Essay", philosophical:"Essay",
  novel:"Novel", novels:"Novel", album:"Album Review", albums:"Album Review", review:"Album Review",
  play:"Play", blog:"Blog", prose:"Prose", journalism:"Journalism", extract:"Extract",
};

function tokenize(s){ return (s.toLowerCase().match(/[a-z']+/g)||[]); }

function parseQuery(q){
  let lower = q.toLowerCase();
  let typeFilters = new Set();
  // multi-word type phrases first
  if(/short\s+stor/.test(lower)){ typeFilters.add("Short Story"); lower=lower.replace(/short\s+stor\w*/g,' '); }
  let toks = tokenize(lower);
  let themeToks = [];
  for(const tk of toks){
    if(TYPEWORDS[tk]){ typeFilters.add(TYPEWORDS[tk]); }
    else themeToks.push(tk);
  }
  // build expanded term weights
  let terms = {}; // term -> weight
  for(const tk of themeToks){
    terms[tk] = Math.max(terms[tk]||0, 1.0);
    const th = WORD2THEME[tk];
    if(th){ for(const theme of th){ for(const w of THEMES[theme]){ terms[w] = Math.max(terms[w]||0, 0.45); } } }
  }
  return {typeFilters, themeToks, terms, raw:q.trim()};
}

function scoreWork(w, pq){
  const {typeFilters, terms, themeToks} = pq;
  let score = 0, matched = new Set();
  const title = w._t, txt = w._txt;
  for(const term in terms){
    const weight = terms[term];
    const re = new RegExp("\\b"+term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'), "g");
    if(title.search(re)>=0){ score += 7*weight; matched.add(term); }
    for(const tg of w._g){ if(tg.indexOf(term)>=0){ score += 4*weight; matched.add(term); } }
    let m, c=0; const re2=new RegExp("\\b"+term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),"g");
    while((m=re2.exec(txt))!==null && c<12){ c++; }
    if(c>0){ score += weight*(1.4 + Math.min(c,12)*0.5); matched.add(term); }
  }
  // require at least one *direct* theme token to match if themeToks present
  if(themeToks.length){
    let directHit=false;
    for(const tk of themeToks){ if(matched.has(tk) || title.indexOf(tk)>=0 || txt.indexOf(tk)>=0) {directHit=true;break;} }
    if(!directHit && score>0) score *= 0.12; // expanded-only match: keep but rank low
  }
  // type handling: a named form (e.g. "sonnet") should dominate, then rank
  // those by theme. Off-form pieces are pushed far down but not removed.
  if(typeFilters.size){
    if(typeFilters.has(w.y)){ score = score*1.7 + 2; }
    else { score *= 0.05; }
  }
  return {score, matched:[...matched]};
}

function search(q){
  const pq = parseQuery(q);
  if(!pq.themeToks.length && !pq.typeFilters.size) return null;
  let res = [];
  for(const w of WORKS){
    const {score, matched} = scoreWork(w, pq);
    if(score>0.0001) res.push({w, score, matched, pq});
  }
  res.sort((a,b)=> b.score-a.score || (b.w.w-a.w.w));
  return res;
}

/* ---------- rendering ---------- */
const el = s=>document.querySelector(s);
const heroStats = el('#heroStats');
heroStats.textContent = WORKS.length+" works · "+__YRLO__+"–"+__YRHI__;

function esc(s){return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}

function snippetFor(w, matched){
  if(!matched || !matched.length) return esc(w.x);
  // find first matched term in text, show window around it
  const txt = w.txt;
  let pos=-1, term=null;
  for(const m of matched){ const p=w._txt.indexOf(m); if(p>=0 && (pos<0||p<pos)){pos=p;term=m;} }
  if(pos<0) return esc(w.x);
  let start = Math.max(0, pos-90);
  let end = Math.min(txt.length, pos+150);
  let s = (start>0?'…':'')+txt.slice(start,end)+(end<txt.length?'…':'');
  s = esc(s);
  for(const m of matched){
    s = s.replace(new RegExp("("+m.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+")","ig"),'<mark>$1</mark>');
  }
  return s;
}

function linesPreview(w, maxLines){
  const raw = w.c
    .replace(/<br\s*\/?>\s*/gi,'\n').replace(/<p[^>]*>/gi,'\n').replace(/<[^>]+>/g,'')
    .replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&[^;]+;/g,'');
  const lines = raw.split('\n').map(l=>l.trim()).filter(l=>l.length>0);
  const CHAR_CAP=320;
  let out='', chars=0, clipped=false;
  for(let i=0;i<Math.min(lines.length,maxLines);i++){
    const l=lines[i];
    if(chars+l.length>CHAR_CAP){ out+=esc(l.slice(0,CHAR_CAP-chars))+'…'; clipped=true; break; }
    out+=(i>0?'<br>':'')+esc(l); chars+=l.length;
  }
  const more=clipped||lines.length>maxLines;
  return out+(more?'<br><span style="color:var(--ink3)">…</span>':'');
}

function cardHTML(w, matched){
  const yr = w.yr?('· '+w.yr):'';
  const why = (matched&&matched.length)?('<span class="why">'+matched.slice(0,3).map(esc).join(', ')+'</span>'):'';
  const snippet = (matched&&matched.length) ? snippetFor(w,matched) : linesPreview(w,5);
  return '<div class="card" data-s="'+w.s+'">'
    + '<div class="ribbon">'+esc(w.y)+'</div>'
    + '<h3>'+esc(w.t)+'</h3>'
    + '<div class="snippet">'+snippet+'</div>'
    + '<div class="foot"><span>'+w.w+' words '+yr+'</span>'+why+'</div></div>';
}

function renderResults(q){
  const area = el('#resultsArea'), browse = el('#browseArea');
  const res = search(q);
  if(res===null){ area.innerHTML=''; browse.classList.remove('hidden'); renderBrowse(); return; }
  browse.classList.add('hidden');
  if(!res.length){
    area.innerHTML='<div class="resultmeta"><span class="count">0</span> results for &ldquo;'+esc(q)+'&rdquo;</div>'
      +'<div class="empty">Nothing matched that theme. Try a single word like <b>death</b>, <b>love</b>, <b>god</b>, or <b>music</b>.</div>';
    return;
  }
  const top = res.slice(0,60);
  area.innerHTML='<div class="resultmeta"><span class="count">'+res.length+'</span> '
    +(res.length===1?'work':'works')+' for &ldquo;'+esc(q)+'&rdquo;'
    +(res.length>60?' <span>(showing 60)</span>':'')+'</div>'
    +'<div class="grid">'+top.map(r=>cardHTML(r.w, r.matched)).join('')+'</div>';
}

let browseMode='form', activeType=null, activeYear=null, activeTheme=null;

function renderBrowse(){
  const browse = el('#browseArea');
  const modes=['form','year','theme'];
  let html='<div class="browse-header"><span>Browse by</span><div class="browse-switch">'
    +modes.map(m=>'<button class="browse-tab'+(browseMode===m?' active':'')+'" data-mode="'+m+'">'+m+'</button>').join('')
    +'</div></div>';

  if(browseMode==='form'){
    const typeCounts={};
    WORKS.forEach(w=>typeCounts[w.y]=(typeCounts[w.y]||0)+1);
    const list=activeType?WORKS.filter(w=>w.y===activeType):WORKS.slice();
    html+='<div class="cloud">';
    html+='<button class="'+(activeType?'':'active')+'" data-type="">All<span class="n">'+WORKS.length+'</span></button>';
    for(const t of LITERARY){ if(!typeCounts[t]) continue; html+='<button class="'+(activeType===t?'active':'')+'" data-type="'+esc(t)+'">'+esc(t)+'<span class="n">'+typeCounts[t]+'</span></button>'; }
    html+='</div>';
    const label=activeType?activeType:'All works';
    html+='<div class="section-title">'+esc(label)+' · '+list.length+'</div>';
    html+='<div class="grid">'+list.map(w=>cardHTML(w,null)).join('')+'</div>';

  } else if(browseMode==='year'){
    const yearCounts={};
    WORKS.forEach(w=>{ if(w.yr) yearCounts[w.yr]=(yearCounts[w.yr]||0)+1; });
    const years=Object.keys(yearCounts).map(Number).sort((a,b)=>b-a);
    const dated=WORKS.filter(w=>w.yr);
    const list=activeYear?dated.filter(w=>w.yr===activeYear):dated.slice().sort((a,b)=>b.yr-a.yr||b.d.localeCompare(a.d));
    html+='<div class="cloud">';
    html+='<button class="'+(activeYear?'':'active')+'" data-year="">All<span class="n">'+dated.length+'</span></button>';
    for(const y of years){ html+='<button class="'+(activeYear===y?'active':'')+'" data-year="'+y+'">'+y+'<span class="n">'+yearCounts[y]+'</span></button>'; }
    html+='</div>';
    const label=activeYear?String(activeYear):'All years';
    html+='<div class="section-title">'+esc(label)+' · '+list.length+'</div>';
    html+='<div class="grid">'+list.map(w=>cardHTML(w,null)).join('')+'</div>';

  } else {
    const themeKeys=Object.keys(THEMES);
    const themeCounts={};
    for(const tk of themeKeys){
      const words=THEMES[tk];
      themeCounts[tk]=WORKS.filter(w=>words.some(wd=>w._txt.includes(wd)||w._t.includes(wd))).length;
    }
    const list=activeTheme
      ? WORKS.filter(w=>THEMES[activeTheme].some(wd=>w._txt.includes(wd)||w._t.includes(wd)))
      : WORKS.slice();
    html+='<div class="cloud">';
    html+='<button class="'+(activeTheme?'':'active')+'" data-theme="">All<span class="n">'+WORKS.length+'</span></button>';
    for(const tk of themeKeys){
      if(!themeCounts[tk]) continue;
      const lbl=tk.charAt(0).toUpperCase()+tk.slice(1);
      html+='<button class="'+(activeTheme===tk?'active':'')+'" data-theme="'+esc(tk)+'">'+esc(lbl)+'<span class="n">'+themeCounts[tk]+'</span></button>';
    }
    html+='</div>';
    const label=activeTheme?(activeTheme.charAt(0).toUpperCase()+activeTheme.slice(1)):'All works';
    html+='<div class="section-title">'+esc(label)+' · '+list.length+'</div>';
    html+='<div class="grid">'+list.map(w=>cardHTML(w,null)).join('')+'</div>';
  }
  browse.innerHTML=html;
}

/* ---------- scansion engine ---------- */
const POETIC = new Set(['Poem','Sonnet','Ode']);

const FW = new Set(['the','a','an','and','but','or','nor','in','on','at','to','of','by','from','with',
  'as','if','when','while','where','though','that','this','these','those','which','who','what',
  'my','his','her','thy','thine','their','our','its','your','i','am','is','are','was','were',
  'be','been','have','has','had','do','does','did','not','so','for','yet','than','then','o','ah','oh','it']);

function syllabify(word){
  // Split a word into its graphical syllable chunks.
  // Returns array of strings that concatenate back to the original word.
  const w=word.toLowerCase();
  if(w.length<=1) return [word];
  const isV=c=>'aeiouy'.includes(c);
  // 1. Find vowel cluster positions [start, end)
  let clusters=[];
  for(let i=0;i<w.length;){
    if(isV(w[i])){let j=i;while(j<w.length&&isV(w[j]))j++;clusters.push([i,j]);i=j;}else i++;
  }
  if(clusters.length<=1) return [word]; // monosyllabic
  // 2. Build split points using Maximal Onset Principle:
  //    single consonant → goes with next syllable; multiple → last one goes with next
  let splits=[0];
  for(let k=0;k<clusters.length-1;k++){
    const end1=clusters[k][1],start2=clusters[k+1][0],cons=start2-end1;
    if(cons===0) splits.push(end1);         // adjacent vowels
    else if(cons===1) splits.push(start2);  // one consonant: open syllable preferred
    else splits.push(start2-1);             // cluster: keep one onset for next syllable
  }
  splits.push(w.length);
  let syls=[];
  for(let k=0;k<splits.length-1;k++) syls.push(word.slice(splits[k],splits[k+1]));
  // 3. Merge terminal silent 'e': "more" → ["mor","e"] → ["more"]
  if(syls.length>=2 && syls[syls.length-1].toLowerCase()==='e')
    syls=[...syls.slice(0,-2),syls[syls.length-2]+syls[syls.length-1]];
  // 4. Merge sonorant+"-ed"/"-es" endings: "mattered" → ["mat","ter","ed"] → ["mat","tered"]
  if(syls.length>=3){
    const last=syls[syls.length-1].toLowerCase(),prev=syls[syls.length-2].toLowerCase();
    if((last==='ed'||last==='es')&&/[rlmn]$/.test(prev))
      syls=[...syls.slice(0,-2),syls[syls.length-2]+syls[syls.length-1]];
  }
  return syls;
}

function scanPoem(htmlContent){
  const lines=htmlContent
    .replace(/<br\s*\/?>/gi,'\n').replace(/<[^>]+>/g,'')
    .replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&[^;]+;/g,' ')
    .split('\n').map(l=>l.trim()).filter(l=>l.length>0&&l.length<200);

  const scannedLines=lines.map(line=>{
    const tokens=(line.match(/[a-zA-Z'']+|[^a-zA-Z'']+/g)||[]);
    let pos=0;
    return tokens.map(tok=>{
      if(!/[a-zA-Z]/.test(tok)) return esc(tok);
      const lower=tok.toLowerCase().replace(/[^a-z']/g,'');
      const lsyls=syllabify(lower);  // syllable splits computed from lowercase
      const n=lsyls.length;
      if(FW.has(lower)){pos+=n;return esc(tok);}
      // Map syllable lengths back onto original-cased token
      let idx=0,html='',boldDone=false;
      for(let si=0;si<n;si++){
        const chunk=tok.slice(idx,idx+lsyls[si].length);idx+=lsyls[si].length;
        // Bold the first syllable that falls on a metrically stressed (odd, 0-based) beat
        if(!boldDone&&(pos+si)%2===1){html+='<b>'+esc(chunk)+'</b>';boldDone=true;}
        else html+=esc(chunk);
      }
      pos+=n;return html;
    }).join('');
  });

  const sylCounts=lines.map(line=>
    (line.match(/[a-zA-Z'']+/g)||[]).reduce((s,w)=>s+syllabify(w.toLowerCase().replace(/[^a-z']/g,'')).length,0)
  );
  const sorted=[...sylCounts].sort((a,b)=>a-b);
  const median=sorted[Math.floor(sorted.length/2)];
  const pct=Math.round(100*sylCounts.filter(c=>Math.abs(c-median)<=1).length/Math.max(1,sylCounts.length));
  let meter='Free verse';
  if(median>=9&&median<=11) meter='Iambic pentameter';
  else if(median>=7&&median<=8) meter='Iambic tetrameter';
  else if(median>=5&&median<=6) meter='Iambic trimeter';
  else if(median>=12&&median<=14) meter='Alexandrine (iambic hexameter)';
  return {html:scannedLines.join('<br>'),meter,median,pct,lineCount:lines.length};
}

/* ---------- reader ---------- */
function renderReader(slug){
  const w = WORKS.find(x=>x.s===slug);
  const r = el('#reader');
  if(!w){ r.className='reader'; r.innerHTML='<a class="back" id="backLink">← Back</a><p>Not found.</p>'; }
  else{
    r.className='reader'+(w.y==='Short Story'||w.y==='Novel'||w.y==='Extract'?' story':'');
    const yr = w.d?new Date(w.d).toLocaleDateString('en-GB',{year:'numeric',month:'long',day:'numeric'}):(w.yr||'Undated');
    const tags=(w.g||[]).map(g=>'<span class="tg" data-tag="'+esc(g)+'">'+esc(g)+'</span>').join(' · ');
    const rel = WORKS.filter(x=>x.s!==w.s && (x.y===w.y || (x.g||[]).some(g=>(w.g||[]).includes(g))))
      .sort((a,b)=>(b.w-a.w)).slice(0,4);
    const scanBtn = POETIC.has(w.y) ? '<button class="scan-btn" id="scanBtn">Scansion mode (Beta)</button>' : '';
    r.innerHTML='<a class="back" id="backLink">← Back to the library</a>'
      +'<div class="ribbon">'+esc(w.y)+'</div>'
      +'<h1>'+esc(w.t)+'</h1>'
      +'<div class="meta"><span>By Luke Labern</span><span class="sep">·</span><span>'+yr+'</span><span class="sep">·</span><span>'+w.w+' words</span>'+(tags?'<span class="sep">·</span><span>'+tags+'</span>':'')+(scanBtn?'<span class="sep">·</span><span>'+scanBtn+'</span>':'')+'</div>'
      +'<div id="proseView" class="prose">'+w.c+'</div>'
      +'<div id="scanView" class="scan-view hidden"></div>'
      +(rel.length?'<div class="related"><div class="section-title">Related writing</div><div class="grid">'+rel.map(x=>cardHTML(x,null)).join('')+'</div></div>':'');

    // wire scansion toggle
    const btn=el('#scanBtn');
    if(btn){
      btn.addEventListener('click',()=>{
        const pv=el('#proseView'), sv=el('#scanView');
        const on=btn.classList.toggle('on');
        if(on){
          if(!sv.dataset.built){
            const result=scanPoem(w.c);
            sv.innerHTML=result.html
              +'<div class="scan-meta">'
              +'<strong>'+result.meter+'</strong>'
              +' &middot; median '+result.median+' syllables/line'
              +' &middot; '+result.pct+'% of lines within 1 syllable of median'
              +'<br><em>Bold = word\'s first syllable falls on a metrically stressed beat (iambic da-DUM pattern assumed). '
              +'Function words are never bolded. Multi-syllable words are treated as a unit.</em>'
              +'</div>';
            sv.dataset.built='1';
          }
          pv.classList.add('hidden'); sv.classList.remove('hidden');
          btn.textContent='Reading mode';
        } else {
          sv.classList.add('hidden'); pv.classList.remove('hidden');
          btn.textContent='Scansion mode (Beta)';
        }
      });
    }
  }
  el('#home').classList.add('hidden');
  r.classList.remove('hidden');
  window.scrollTo(0,0);
}

function showHome(){
  el('#reader').classList.add('hidden');
  el('#home').classList.remove('hidden');
}

/* ---------- routing ---------- */
function route(){
  const h=location.hash;
  const m=h.match(/^#\/w\/(.+)$/);
  if(m){ renderReader(decodeURIComponent(m[1])); }
  else{ showHome(); }
}
window.addEventListener('hashchange', route);

/* ---------- events ---------- */
const qInput=el('#q'), sbox=el('#sbox');
let debTimer=null;
function onQuery(){
  const v=qInput.value;
  sbox.classList.toggle('has-text', v.length>0);
  clearTimeout(debTimer);
  debTimer=setTimeout(()=>renderResults(v), 80);
}
qInput.addEventListener('input', onQuery);
el('#clear').addEventListener('click', ()=>{qInput.value='';onQuery();qInput.focus();});

document.body.addEventListener('click', e=>{
  const card=e.target.closest('.card[data-s]');
  if(card){ location.hash='#/w/'+encodeURIComponent(card.dataset.s); return; }
  const mBtn=e.target.closest('button[data-mode]');
  if(mBtn){ browseMode=mBtn.dataset.mode; activeType=null; activeYear=null; activeTheme=null; renderBrowse(); return; }
  const tBtn=e.target.closest('button[data-type]');
  if(tBtn){ activeType=tBtn.dataset.type||null; renderBrowse(); return; }
  const yBtn=e.target.closest('button[data-year]');
  if(yBtn){ activeYear=yBtn.dataset.year?Number(yBtn.dataset.year):null; renderBrowse(); return; }
  const thBtn=e.target.closest('button[data-theme]');
  if(thBtn){ activeTheme=thBtn.dataset.theme||null; renderBrowse(); return; }
  const tag=e.target.closest('[data-tag]');
  if(tag){ qInput.value=tag.dataset.tag; if(location.hash) location.hash=''; sbox.classList.add('has-text'); renderResults(qInput.value); window.scrollTo({top:0,behavior:'smooth'}); return; }
  if(e.target.id==='backLink'){ location.hash=''; return; }
  if(e.target.id==='brand'){ location.hash=''; qInput.value=''; onQuery(); window.scrollTo({top:0,behavior:'smooth'}); return; }
});

// suggested theme chips
const SUGGEST=["sonnet death","love","nihilism","god","music","time","madness","freedom","nature"];
el('#suggest').innerHTML=SUGGEST.map(s=>'<button>'+s+'</button>').join('');
el('#suggest').addEventListener('click',e=>{ if(e.target.tagName==='BUTTON'){ qInput.value=e.target.textContent; onQuery(); } });

// theme toggle
const tt=el('#themeToggle'), tz=el('#zestyToggle');
function setTheme(t){
  document.documentElement.dataset.theme=t;
  if(t!=='zesty'){ delete document.documentElement.dataset.stars; tz.textContent='Zesty'; }
  tt.textContent=t==='light'?'Dark':'Light';
  tz.classList.toggle('zesty-on', t==='zesty');
  try{localStorage.setItem('legacy-theme',t)}catch(e){}
}
tt.addEventListener('click',()=>setTheme(document.documentElement.dataset.theme==='light'?'dark':'light'));
tz.addEventListener('click',()=>{
  if(document.documentElement.dataset.theme!=='zesty'){ setTheme('zesty'); return; }
  const starsOn=document.documentElement.dataset.stars==='1';
  document.documentElement.dataset.stars=starsOn?'0':'1';
  tz.textContent=starsOn?'Zesty':'Zesty ✦';
});
try{ const saved=localStorage.getItem('legacy-theme'); if(saved) setTheme(saved); }catch(e){}

// scroll-to-top button
const scrollTopBtn=el('#scrollTop');
window.addEventListener('scroll',()=>scrollTopBtn.classList.toggle('visible',window.scrollY>300),{passive:true});
scrollTopBtn.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));

// idle shooting star — curves from bottom-left to top-right
(function(){
  const cvs=document.createElement('canvas');
  cvs.style.cssText='position:fixed;inset:0;pointer-events:none;z-index:999;width:100%;height:100%';
  document.body.appendChild(cvs);
  const ctx=cvs.getContext('2d');
  let W,H;
  function resize(){W=cvs.width=innerWidth;H=cvs.height=innerHeight;}
  resize();
  window.addEventListener('resize',resize,{passive:true});
  let idleTimer=null,raf=null,gen=0;
  // sample a quadratic bezier at t
  function bez(p0,p1,p2,t){return (1-t)*(1-t)*p0+2*(1-t)*t*p1+t*t*p2;}
  function shootStar(myGen){
    if(myGen!==gen) return;
    const th=document.documentElement.dataset.theme;
    const col=th==='zesty'?'#a78bfa':th==='dark'?'#f06aa0':'#d23c77';
    // always start from very close to the bottom-left corner
    const x0=Math.random()*W*.08, y0=H*.88+Math.random()*H*.12;
    const x2=W*.5+Math.random()*W*.5, y2=Math.random()*H*.4;
    // control point arcs the path outward
    const cx=(x0+x2)/2-W*.1, cy=(y0+y2)/2-H*.25;
    const TRAIL=180; // trail length in bezier t-units (points sampled)
    const dur=1100+Math.random()*400;
    const t0=performance.now();
    function frame(now){
      if(myGen!==gen){ctx.clearRect(0,0,W,H);return;}
      const p=Math.min((now-t0)/dur,1);
      const ease=p<.5?2*p*p:-1+(4-2*p)*p;
      const alpha=Math.sin(p*Math.PI);
      ctx.clearRect(0,0,W,H);
      // draw trail: sample N points behind the head along the bezier
      const N=60;
      ctx.save();
      ctx.globalAlpha=alpha;
      ctx.shadowColor=col;ctx.shadowBlur=28;
      for(let i=0;i<N;i++){
        const ti=Math.max(0,ease-(N-i)/N*0.28);
        const ti1=Math.max(0,ease-(N-i-1)/N*0.28);
        const ax=bez(x0,cx,x2,ti), ay=bez(y0,cy,y2,ti);
        const bx=bez(x0,cx,x2,ti1), by=bez(y0,cy,y2,ti1);
        const frac=i/N;
        ctx.beginPath();
        ctx.moveTo(ax,ay);ctx.lineTo(bx,by);
        ctx.strokeStyle=`rgba(255,255,255,${frac*.7})`;
        ctx.lineWidth=4+frac*10; // thick at head, thin at tail
        ctx.stroke();
      }
      // glowing head
      const hx=bez(x0,cx,x2,ease), hy=bez(y0,cy,y2,ease);
      const grd=ctx.createRadialGradient(hx,hy,0,hx,hy,22);
      grd.addColorStop(0,'rgba(255,255,255,1)');
      grd.addColorStop(.35,col);
      grd.addColorStop(1,'rgba(255,255,255,0)');
      ctx.beginPath();ctx.arc(hx,hy,22,0,Math.PI*2);
      ctx.fillStyle=grd;ctx.shadowBlur=40;ctx.shadowColor=col;
      ctx.fill();
      // bright core
      ctx.beginPath();ctx.arc(hx,hy,6,0,Math.PI*2);
      ctx.fillStyle='#fff';ctx.shadowBlur=20;ctx.fill();
      ctx.restore();
      if(p<1) raf=requestAnimationFrame(frame);
      else{ ctx.clearRect(0,0,W,H); setTimeout(()=>shootStar(myGen),10000); }
    }
    raf=requestAnimationFrame(frame);
  }
  function resetIdle(){
    gen++;cancelAnimationFrame(raf);clearTimeout(idleTimer);
    ctx.clearRect(0,0,W,H);
    idleTimer=setTimeout(()=>shootStar(gen),5000);
  }
  ['mousemove','keydown','scroll','click','touchstart'].forEach(e=>
    window.addEventListener(e,resetIdle,{passive:true})
  );
  resetIdle();
})();

// idle instagram toast (10s on home page)
(function(){
  const toast=document.createElement('div');
  toast.id='igToast';
  toast.innerHTML='If this material offended and/or inspired you, message me: <a href="https://instagram.com/labern" target="_blank" rel="noopener">@Labern</a> on Instagram'
    +'<button class="toast-x" aria-label="Dismiss">&times;</button>';
  document.body.appendChild(toast);
  let shown=false, showTimer=null, hideTimer=null;
  function dismiss(){ toast.classList.remove('visible'); clearTimeout(hideTimer); }
  function show(){
    if(!location.hash && !shown){ shown=true; toast.classList.add('visible'); hideTimer=setTimeout(dismiss,5000); }
  }
  function scheduleToast(){ clearTimeout(showTimer); if(shown) return; showTimer=setTimeout(show,10000); }
  toast.querySelector('.toast-x').addEventListener('click',e=>{ e.stopPropagation(); dismiss(); });
  toast.querySelector('a').addEventListener('click',e=>e.stopPropagation());
  window.addEventListener('hashchange',()=>{ dismiss(); shown=false; if(!location.hash) scheduleToast(); });
  scheduleToast();
})();

// background twinkling stars (visible in zesty mode)
(function(){
  const cvs=el('#bgStars');
  const ctx=cvs.getContext('2d');
  function resize(){cvs.width=innerWidth;cvs.height=innerHeight;}
  resize();
  window.addEventListener('resize',resize,{passive:true});
  const stars=Array.from({length:140},()=>({
    x:Math.random()*innerWidth, y:Math.random()*innerHeight,
    r:Math.random()*1.4+0.2, d:Math.random()*.5+0.2, t:Math.random()*Math.PI*2
  }));
  function draw(){
    ctx.clearRect(0,0,cvs.width,cvs.height);
    ctx.fillStyle='#cbd5ff';
    for(const s of stars){
      s.t+=0.018*s.d;
      ctx.globalAlpha=Math.max(0.05, 0.4+Math.sin(s.t)*0.4);
      ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fill();
    }
    requestAnimationFrame(draw);
  }
  draw();
})();

// init
renderBrowse();
route();
</script>
</body>
</html>
"""

HTML = (HTML
        .replace("__DATA__", data_json)
        .replace("__TYPES__", json.dumps(types))
        .replace("__YRLO__", str(yr_lo))
        .replace("__YRHI__", str(yr_hi))
        .replace("__N__", str(len(works))))

open(f"{OUT}/index.html", "w", encoding="utf-8").write(HTML)
print(f"Wrote {OUT}/index.html  ({len(HTML)/1e6:.2f} MB, {len(works)} works)")
