# Legacy Viewer

A single-page, **database-free** archive of the collected writing of Luke Labern
(289 works, 2010–2020) — extracted from the [Legacy](https://github.com/Labern/Legacy)
Rails app and packaged as one self-contained HTML file you can open in any browser.

## What it does

- **Everything is in `index.html`.** All 289 pieces — poems, sonnets, short
  stories, essays, novels, songs, album reviews, blog posts — are embedded
  directly in the page. No server, no database, no build step required to read it.
- **Thematic search.** Type a theme like `sonnet death`, `love`, `nihilism`,
  `god`, or `music` and it ranks the most relevant pieces. A built-in lexicon
  expands themes (e.g. *death* also matches *mortality, grief, oblivion, grave*…)
  so a search surfaces work *about* an idea, not just word-for-word matches.
- **Form-aware.** Words like `sonnet`, `essay`, `story`, `novel` steer results
  toward that form — so `sonnet death` finds sonnets that touch on death.
- **Browse** by form (Poem, Sonnet, Short Story, Essay, …) or by collection/tag.
- **Read in place.** Click any result to read the full piece, beautifully
  typeset, with related writing suggested at the bottom.
- Light / dark reading themes.

## Usage

Just open `index.html` in a browser. That's it.

## Rebuilding from source

The page is generated from the original WordPress export.

```bash
cd build
python3 build_records.py   # extracted_posts.json -> cleaned, deduped records
python3 build_site.py      # records -> ../index.html (the single-page app)
```

- `build/extracted_posts.json` — the raw extracted posts (from the Legacy DB seed
  data, deduped later in the pipeline).
- `build/build_records.py` — cleans HTML, removes duplicates (the same piece was
  tagged under several WordPress categories), detects each piece's form, parses
  dates, and writes canonical records.
- `build/build_site.py` — embeds the records and the client-side search engine
  into a single `index.html`.

## Design

Typography uses **Libre Baskerville**, the serif from the original
lukelabern.com, to keep the literary feel of the source site.
