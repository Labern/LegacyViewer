#!/usr/bin/env python3
"""Build a static, database-free, searchable archive of Luke Labern's writing
from extracted_posts.json. Output: /Users/labern/Desktop/Clean/LegacyArchive/
"""
import json, re, os, html, unicodedata
from collections import defaultdict

ROOT = "/Users/labern/Desktop/Clean"
SRC = f"{ROOT}/extracted_posts.json"
OUT = f"{ROOT}/LegacyArchive"
WORKS_DIR = f"{OUT}/works"
ASSETS_DIR = f"{OUT}/assets"

os.makedirs(WORKS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# ---------------------------------------------------------------- load
posts = json.load(open(SRC))

JUNK_GENRES = {
    "enter your zip code here", "we're live!", "blogroll",
    "a work in process", "work in progress", "uncategorized", "none", "",
}
YEAR_GENRES = {str(y) for y in range(2000, 2031)}

def strip_tags(c):
    t = re.sub(r"<[^>]+>", " ", c or "")
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()

def textlen(c):
    return len(strip_tags(c))

# ---------------------------------------------------------------- dedupe
groups = defaultdict(list)
for p in posts:
    key = strip_tags(p["title"]).lower()
    groups[key].append(p)

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"['\"]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"^-+|-+$", "", s) or "untitled"

# ---------------------------------------------------------------- type detection
def detect_type(title, genres):
    t = title.lower()
    g = {x.lower() for x in genres}
    m = re.search(r"\(([^)]*)\)\s*$", t)
    paren = m.group(1) if m else ""
    def has(*words): return any(w in paren for w in words)
    if "sonnet" in t: return "Sonnet"
    if has("ode"): return "Ode"
    if has("song", "lyrics", "ep", "music"): return "Song"
    if has("short story", "short, short story", "story"): return "Short Story"
    if has("novel"): return "Novel"
    if has("extract"): return "Extract"
    if has("essay"): return "Essay"
    if has("treatise"): return "Essay"
    if has("monologue", "play"): return "Play"
    if has("travel writing", "journalism"): return "Journalism"
    if has("poem"): return "Poem"
    if "essential albums" in g or "essential album" in t: return "Album Review"
    if "philosophy" in g: return "Essay"
    if "journalism" in g: return "Journalism"
    if "play" in g: return "Play"
    if "novel" in g: return "Novel"
    if "stories" in g: return "Short Story"
    if "essay" in g: return "Essay"
    if "music" in g or "song" in g: return "Song"
    if "poetry" in g: return "Poem"
    if "extract" in g: return "Extract"
    if "criticism" in g: return "Album Review"
    if "blog" in g: return "Blog"
    if "prose" in g: return "Prose"
    return "Prose"

# ---------------------------------------------------------------- content cleaning
slug_set = {}

def clean_content(c, slug_by_oldslug):
    if not c:
        return ""
    # remove base64 images entirely
    c = re.sub(r"<img[^>]*data:image[^>]*>", "", c, flags=re.I)
    # drop script/style/button/iframe blocks
    c = re.sub(r"<(script|style|button|iframe)[^>]*>.*?</\1>", "", c, flags=re.I | re.S)
    c = re.sub(r"<(script|style|button|iframe)[^>]*/?>", "", c, flags=re.I)
    # neutralise event handlers
    c = re.sub(r'\son\w+="[^"]*"', "", c, flags=re.I)
    c = re.sub(r"\son\w+='[^']*'", "", c, flags=re.I)
    return c.strip()

def rewrite_links(c, oldslug_to_slug):
    # internal links -> local work pages where we can map them
    def repl(m):
        quote, url = m.group(1), m.group(2)
        target = None
        mm = re.search(r"/posts/([^/\"'#?]+)", url)
        if mm:
            target = oldslug_to_slug.get(mm.group(1))
        if target:
            return f'href={quote}{target}.html{quote}'
        # external -> open in new tab
        if url.startswith("http"):
            return f'href={quote}{url}{quote} target="_blank" rel="noopener"'
        return m.group(0)
    return re.sub(r'href=(["\'])(.*?)\1', repl, c)

# ---------------------------------------------------------------- build records
records = []
for key, items in groups.items():
    best = max(items, key=lambda p: textlen(p["content"]))
    if textlen(best["content"]) < 20:
        continue
    title = strip_tags(best["title"]).strip()
    if not title:
        continue
    genres = []
    for it in items:
        g = (it.get("genre") or "").strip()
        if g and g.lower() not in JUNK_GENRES:
            genres.append(g)
    # tags = genres minus year-only and junk, deduped, title-cased-ish
    tags = []
    seen = set()
    for g in genres:
        gl = g.lower()
        if gl in YEAR_GENRES or gl in JUNK_GENRES or gl == "the nihilist":
            continue
        if gl not in seen:
            seen.add(gl)
            tags.append(g)
    typ = detect_type(title, genres)
    # date
    raw = (best.get("created_at") or "")
    year = None
    date_iso = None
    md = re.match(r"(\d{4})-(\d{2})-(\d{2})", raw)
    if md and md.group(1) != "0000":
        year = int(md.group(1))
        date_iso = f"{md.group(1)}-{md.group(2)}-{md.group(3)}"
    # slug
    base = best.get("slug") or slugify(title)
    base = slugify(base)
    slug = base
    n = 2
    while slug in slug_set:
        slug = f"{base}-{n}"; n += 1
    slug_set[slug] = True
    records.append({
        "title": title,
        "raw_content": best["content"],
        "type": typ,
        "tags": tags,
        "year": year,
        "date": date_iso,
        "slug": slug,
        "oldslug": (best.get("slug") or slugify(title)),
    })

# map oldslug -> new slug for internal link rewriting
oldslug_to_slug = {r["oldslug"]: r["slug"] for r in records}

# finalise content + plaintext + excerpt
for r in records:
    cc = clean_content(r["raw_content"], oldslug_to_slug)
    cc = rewrite_links(cc, oldslug_to_slug)
    r["content"] = cc
    txt = strip_tags(cc)
    r["text"] = txt
    excerpt = txt[:240]
    if len(txt) > 240:
        excerpt = excerpt.rsplit(" ", 1)[0] + "…"
    r["excerpt"] = excerpt
    r["words"] = len(txt.split())
    del r["raw_content"]

# sort: dated newest first, then undated alpha
records.sort(key=lambda r: (r["date"] or "0000", r["title"]), reverse=True)

print(f"Final works: {len(records)}")
from collections import Counter
print("Types:", dict(Counter(r["type"] for r in records)))

# stash for the next stage
json.dump(records, open(f"{OUT}/_records.json", "w"), ensure_ascii=False)
print("Wrote _records.json")
