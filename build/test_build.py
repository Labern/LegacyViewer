#!/usr/bin/env python3
"""
Test suite for LegacyViewer index.html.
Run: python3 build/test_build.py
Builds the site fresh, then checks the output for correctness.
"""
import subprocess, sys, re, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build", "build_site.py")
OUT   = "/Users/labern/Desktop/Clean/LegacyArchive/index.html"

# ── build ────────────────────────────────────────────────────────────────────
print("Building…")
result = subprocess.run(["python3", BUILD], capture_output=True, text=True)
if result.returncode != 0:
    print("BUILD FAILED:\n", result.stderr)
    sys.exit(1)

content = open(OUT).read()
errors = []

def check(name, condition, detail=""):
    if not condition:
        errors.append(f"FAIL  {name}" + (f": {detail}" if detail else ""))
    else:
        print(f"  ok  {name}")

# ── JS syntax ────────────────────────────────────────────────────────────────
print("\n[JS]")
js_block = re.search(r"<script>(.*?)</script>", content, re.S)
check("JS block exists", js_block)
if js_block:
    js = js_block.group(1)
    r = subprocess.run(["node", "--check", "/dev/stdin"],
                       input=js, capture_output=True, text=True)
    check("JS parses without error", r.returncode == 0, r.stderr.strip()[:200])

    # curly-quote guard: only check code outside the WORKS literal
    works_m = re.search(r"const WORKS\s*=\s*\[.*?\];", js, re.S)
    js_code = js.replace(works_m.group(0), "") if works_m else js
    CURLY = {chr(0x2018), chr(0x2019), chr(0x201C), chr(0x201D)}
    bad_quotes = [c for c in js_code if c in CURLY]
    check("No curly quotes in JS code", len(bad_quotes) == 0,
          f"{len(bad_quotes)} curly quotes outside WORKS data — will break parsing")

# ── works data ───────────────────────────────────────────────────────────────
print("\n[Data]")
m = re.search(r"const WORKS\s*=\s*(\[.*?\]);", content, re.S)
check("WORKS array present", m)
if m:
    try:
        works = json.loads(m.group(1))
        check("289 works embedded", len(works) == 289, f"got {len(works)}")
        slugs = [w.get("s") or w.get("slug","") for w in works]
        check("All works have slugs", all(slugs))
        types = {w.get("y") or w.get("type","") for w in works}
        check("Poem type present", "Poem" in types)
        check("Short Story type present", "Short Story" in types)
        check("Sonnet type present", "Sonnet" in types)
    except json.JSONDecodeError as e:
        errors.append(f"FAIL  WORKS JSON invalid: {e}")

# ── themes ───────────────────────────────────────────────────────────────────
print("\n[Themes]")
check("Zesty theme CSS exists",      '[data-theme="zesty"]' in content)
check("Dark theme CSS exists",       '[data-theme="dark"]' in content)
check("CSS accent variable defined", "--accent:" in content)
check("Zesty bg gradient present",   "0f0c29" in content)

# ── mobile media query ───────────────────────────────────────────────────────
print("\n[Mobile]")
mobile = re.search(r"@media \(max-width:600px\)\{([^}](?:[^{}]|\{[^}]*\})*)\}", content)
check("Mobile media query exists", mobile)
if mobile:
    mq = mobile.group(0)
    check("Mobile body font ≥ 18px",
          bool(re.search(r"body\{font-size:([2-9]\d|1[89])px", mq)),
          "body font-size under 18px on mobile")
    check("Mobile .reader padding overridden",
          ".reader{padding:" in mq)
    check("Mobile .prose font overridden",
          ".prose{font-size:" in mq)

# ── key UI elements ──────────────────────────────────────────────────────────
print("\n[UI]")
check("Reader element present",      'id="reader"' in content)
check("bgStars canvas present",      'id="bgStars"' in content)
check("Zesty toggle button present", 'id="zestyToggle"' in content)
check("Theme toggle button present", 'id="themeToggle"' in content)
check("Scroll-to-top button",        'id="scrollTop"' in content)
check("Instagram toast present",     "igToast" in content)
check("Browse switch present",       'class="browse-switch"' in content)
check("Shooting star JS present",    "shootStar" in content)

# ── zesty default init ───────────────────────────────────────────────────────
print("\n[Zesty default]")
check("setTheme called on first load (no saved theme)",
      "else setTheme(" in content,
      "first-load fallback missing — Zesty button won't highlight on fresh visit")
check("zesty-on class toggled in setTheme",
      "zesty-on" in content)
check("data-theme=zesty on <html>",
      'data-theme="zesty"' in content)

# ── CSS grid / cards ─────────────────────────────────────────────────────────
print("\n[Cards]")
check("Grid auto-fill columns",      "auto-fill" in content)
check("Card aspect-ratio set",       "aspect-ratio" in content)

# ── reader layout ────────────────────────────────────────────────────────────
print("\n[Reader]")
check("Story reader class",          ".reader.story{" in content)
check("Left-heavy poem padding",     "120px" in content)
check("Zesty reader equal padding",  re.search(r'\[data-theme="zesty"\] \.reader\{[^}]*padding', content) is not None)

# ── summary ──────────────────────────────────────────────────────────────────
print()
if errors:
    print(f"{'─'*50}")
    for e in errors:
        print(e)
    print(f"{'─'*50}")
    print(f"{len(errors)} test(s) failed.")
    sys.exit(1)
else:
    print(f"All tests passed.")
