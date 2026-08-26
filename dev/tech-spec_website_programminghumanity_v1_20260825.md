# Technical Specification — programminghumanity.org Static Site

**Version:** v1
**Date:** 2026-08-25
**Repo:** `/Users/jonc/code/programminghumanity-org`
**Source of content:** migrated from programminghumanity.wordpress.com (WordPress Twenty Nineteen theme)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Structure](#2-structure)
3. [Page Template Anatomy](#3-page-template-anatomy)
4. [Design System](#4-design-system)
5. [Content](#5-content)
6. [Navigation & User Flow](#6-navigation--user-flow)
7. [Testing & Tooling](#7-testing--tooling)
8. [Known Gaps & Limitations](#8-known-gaps--limitations)
9. [Appendix A: Remaining Stub Pages](#appendix-a-remaining-stub-pages-104)

---

## 1. Overview

Fully static HTML/CSS website — **416 HTML pages**, one shared stylesheet (`css/style.css`, 421 lines, 6,954 bytes, human-readable, not minified), **no build system, no JavaScript**. Pages are hand-assembled from a WordPress XML export plus a live-site content dump; WordPress block markup (`wp-block-*` classes and `<!-- wp:* -->` comments) is preserved in the source. Local dev is `python3 -m http.server 8080`. A pytest suite (`tests/`) validates structure, links, and site-wide invariants.

---

## 2. Structure

### 2.1 Directory inventory

| Path | Purpose | HTML files |
|---|---|---|
| `/` (root) | `index.html` (home), `archive.html` (full sitemap), `404.html` | 3 |
| `2018-2019/` | Semester archive: IPHS 200 first year (syllabus, topics, posters, exercises) | 38 (37 + index) |
| `2019-fall/` | Semester archive: IPHS 300 AI course, Fall 2019 lectures | 24 |
| `2020/` | Semester archive: single page (`ap-us-history-2020.html`) + index | 2 |
| `2020-fall/` | Semester archive: topic pages + posters, Fall 2020 | 14 |
| `2020-spring/` | Semester archive: topic pages, posters, projects, Spring 2020 | 17 |
| `2021/` | Semester archive: AI course lectures 2021 | 32 |
| `2022-spring/` | Semester archive: AI course lectures Spring 2022 | 25 |
| `2023/` | Semester archive: syllabus/readings/lectures 2023 | 7 |
| `2025-spring/` | Semester archive: AI course lectures Spring 2025 | 19 |
| `2026-spring/` | Semester archive: AI course lectures Spring 2026 | 16 |
| `blog/` | Blog posts (largest folder) | 128 (127 posts + index) |
| `core/` | Structural/evergreen pages: about, contact, faculty, syllabus, readings, projects, resources, workshops | 41 |
| `labs/` | Hands-on lab pages (lab-algorithms, lab-nlp, nlp-scripts, …) | 16 |
| `research/` | Research reference pages (research-causality, research-datasets, …) | 15 |
| `topics/` | Week-by-week course topic pages (topic-data, topic-networks, …) | 19 |
| `css/` | `style.css` — the single shared stylesheet | 0 |
| `images/` | `images/uploads/` local media (2 files, see §5.4) | 0 |
| `tests/` | pytest suite: `conftest.py`, 3 test files, `requirements.txt` | 0 |
| `dev/` | Dev docs: `audit_bug-fix_20260317.md` (migration audit report) | 0 |
| `tmp/` | Migration tooling: Python scripts + JSON dumps used to populate content (see §7.3) | 0 |
| **Total** | | **416** |

Other root files: `README.md` (directory map + content stats), `CLAUDE.md` (agent guidance), `.gitignore`. Non-content dirs: `.git/`, `.venv/`, `.pytest_cache/`, `.vscode/`, `.gstack/`.

### 2.2 File naming conventions

- **Flat files**: `folder/page-name.html`, never `folder/page-name/index.html`. Slugs are lowercase-kebab-case, carried over from WordPress permalinks (e.g. `blog/best-jupyter-notebooks-for-ml-in-python.html`).
- Semester-suffixed variants distinguish reruns of the same lecture: `machine-learning-introduction-2022.html`, `machine-learning-introduction-spring-2025.html`, `machine-learning-introduction-spring-2026.html`.
- WordPress duplicate-slug artifacts survive: `-2` suffixes (`topic-models-2.html`, `composing-music-with-rnns-2.html`, `readings-2.html`) and `-old`/`-orig`/`dup-` prefixes in `2023/` and `2025-spring/`.
- Every content folder has an `index.html` listing its pages.

### 2.3 Folder index pattern

Each folder `index.html` contains an item-count sentence plus a `ul.item-list` of links, one `<li>` per page. From `2021/index.html:25-28`:

```html
<div class="page-content">
<p>31 items in <strong>2021</strong>.</p>
<ul class="item-list">
<li><a href="0-readings-2021.html">0 Readings 2021</a> <span class="badge badge-placeholder">Placeholder</span></li>
```

Link text is the Title-Cased slug ("Ai Actors And Evolution"), not the page's real `<h1>`. Entries for stub pages carry `<span class="badge badge-placeholder">Placeholder</span>`. The home page (`index.html:36`) lists all ten semester folders with item counts in a `div.section` / `ul.item-list`.

---

## 3. Page Template Anatomy

### 3.1 Shared skeleton

Every one of the 416 pages follows the same structure (representative example, `topics/topic-data.html:1-25`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Topic: Data &ndash; Programming Humanity</title>
<link rel="stylesheet" href="../css/style.css">
</head>
<body>
<header class="site-header">
<div class="header-inner">
<h1 class="site-title"><a href="../index.html">Programming Humanity &mdash; <span class="tagline">Computational Thinking for Humanity</span></a></h1>
<nav class="main-nav"><ul>
<li><a href="../core/syllabus.html">Syllabus</a></li>
<li><a href="../core/readings-2.html">Readings</a></li>
<li><a href="../core/about.html">About</a></li>
</ul></nav>
<div class="social-nav"><a href="https://twitter.com/ai4dhumanities" target="_blank" rel="noopener">Twitter</a></div>
</div>
</header>
<section class="hero"><h1>Topic: Data <span class="badge badge-private">Private</span></h1></section>
<main class="content-wrapper">
<div class="breadcrumbs"><a href="../index.html">Home</a> &raquo; <a href="index.html">Topics</a> &raquo; <span>Topic: Data</span></div>
<div class="page-meta">Created: 2019-01-09 &bull; Modified: 2025-11-17 &bull; Status: private</div>
<div class="page-content"> …content… </div>
</main>
<footer class="site-footer"><p>Programming Humanity</p></footer>
</body>
</html>
```

Sequence: `DOCTYPE` → `head` (charset, viewport, title, one CSS link) → `header.site-header` (`h1.site-title` + `nav.main-nav` + `div.social-nav`) → `section.hero` with the page `<h1>` → `main.content-wrapper` (`div.breadcrumbs`, `div.page-meta`, `div.page-content`) → `footer.site-footer`. All 416 footers are identical: `<p>Programming Humanity</p>`.

- Page `<title>` always ends `&ndash; Programming Humanity` (test-enforced).
- Nav is always exactly the same 3 links (Syllabus, Readings, About — test-enforced) plus the Twitter social link (`https://twitter.com/ai4dhumanities`).

### 3.2 Relative CSS paths by depth

The site is only ever 1 folder deep, so there are exactly two variants (verified by grep across all pages):

| Path | Count | Used by |
|---|---|---|
| `href="css/style.css"` | 3 | root pages (`index.html`, `archive.html`, `404.html`) |
| `href="../css/style.css"` | 413 | every page inside a folder |

All other relative links (nav, breadcrumbs, home link, header background image `../images/uploads/tree-3097419_1920.jpg`) follow the same depth prefix.

### 3.3 Breadcrumbs, page-meta, badges

- **Breadcrumbs** (`div.breadcrumbs`): `Home » <Folder> » <Page>` with relative links; present on 398 pages. The 18 pages without them are the 3 root pages and the 15 folder `index.html` files (folder indexes and root pages intentionally omit them; test suite only requires breadcrumbs on non-index subfolder pages).
- **Page meta** (`div.page-meta`): `Created: YYYY-MM-DD • Modified: YYYY-MM-DD [• Status: draft|private]` — WordPress post dates and status, present on 398 pages. Stub pages carry a reduced `Folder: <name>` meta line instead (`2021/attention-transformers.html:24`).
- **Badges** (`span.badge` inside the hero `<h1>` or index list items):
  - `badge-draft` (orange `#ff9800`) — 145 pages, mostly unfinished blog posts (e.g. `blog/causality.html`).
  - `badge-private` (pink `#e91e63`) — 73 pages, WordPress-private pages (e.g. `topics/topic-data.html`).
  - `badge-placeholder` (gray `#9e9e9e`) — appears only in 8 folder index files, 115 occurrences total.

### 3.4 Placeholder state (important nuance)

The migration originally created 115 placeholder pages with `.placeholder-notice` boxes. **Today zero pages contain `.placeholder-notice`** — a content-population pass replaced the notice boxes. However:

- **104 pages are still generic stubs**: their entire `page-content` is boilerplate ("This lecture is part of the [semester] of Programming Humanity. For the complete course outline… see the Readings page." — see `2021/attention-transformers.html:25-28`). Full list in Appendix A. Distribution: 2018-2019 (8), 2019-fall (22), 2021 (24), 2022-spring (14), 2023 (6), 2025-spring (16), 2026-spring (14).
- **115 `badge-placeholder` badges remain** in 8 index files (`2018-2019/index.html` ×10, `2019-fall/index.html` ×22, `2021/index.html` ×26, `2022-spring/index.html` ×14, `2023/index.html` ×6, `2025-spring/index.html` ×16, `2026-spring/index.html` ×15, `core/index.html` ×6). The badge count (115) exceeds the stub count (104): ~11 pages were populated with real content (e.g. `2021/0-readings-2021.html`, 97 lines with images and topic links) but their index badges were never removed. The badges are stale metadata, not ground truth.

---

## 4. Design System

`css/style.css` (421 lines, readable, commented "Twenty Nineteen-inspired theme"). Note: project CLAUDE.md calls it minified; it is not.

### 4.1 CSS custom properties (`:root`, style.css:3-17)

| Token | Value | Role |
|---|---|---|
| `--bg` | `#fff` | Page background |
| `--text` | `#111` | Body text |
| `--text-lt` | `#767676` | Muted text (breadcrumbs, meta, captions, footer) |
| `--accent` | `#0073aa` | Links (classic WordPress blue) |
| `--accent-dk` | `#005177` | Link hover |
| `--border` | `#e0e0e0` | Rules, table borders, footer top border |
| `--code-bg` | `#f5f5f5` | Code/pre background (also table `th`) |
| `--draft` | `#ff9800` | Draft badge, placeholder-notice border |
| `--priv` | `#e91e63` | Private badge |
| `--fh` | `"NonBreakingSpaceOverride", "Hoefler Text", Garamond, "Times New Roman", serif` | Heading font stack |
| `--fb` | `"NonBreakingSpaceOverride", -apple-system, "Segoe UI", Roboto, "Helvetica Neue", sans-serif` | Body font stack |
| `--mw` | `700px` | Content max-width |
| `--mww` | `1168px` | Wide max-width (header inner) |

Non-token colors used directly: header fallback `#111` with `rgba(0,0,0,0.5)` overlay; hero `#1a1a2e` (dark navy); placeholder badge `#9e9e9e`; placeholder-notice background `#fff3e0`; item-list row divider `#f0f0f0`.

### 4.2 Typography

- **Base**: body 22px / line-height 1.8, sans-serif stack `--fb` (drops to 18px below 768px). This mirrors Twenty Nineteen's large body type.
- **Headings**: serif stack `--fh`, weight 700, line-height 1.2–1.3. Sizes: `.site-title` 2.4rem (1.6rem mobile), `.hero h1` 2.25rem (1.8rem mobile), content `h2` 1.8rem, `h3` 1.4rem, `h4` 1.125rem, `.section h2` 1.6rem.
- **Small text**: the distinctive Twenty Nineteen value `0.72727rem` is used for nav links, breadcrumbs, page-meta, figcaptions, and footer. Nav links are additionally 700 weight, uppercase, `letter-spacing: 0.05em`.
- **Badges**: 0.6rem, 700, uppercase, `letter-spacing: 0.5px`.
- Links are underlined by default (`text-decoration: underline`, style.css:31-34).

### 4.3 Layout

- **Header** (`.site-header`, style.css:48-62): full-bleed background photo `../images/uploads/tree-3097419_1920.jpg` (center/cover) over `#111`, darkened by a `::before` overlay at 50% black; white text, centered; padding `66px 2rem` (40px 1rem mobile). Inner wrapper capped at `--mww` 1168px.
- **Hero** (`.hero`, style.css:146-161): solid `#1a1a2e` band, white serif `<h1>`, padding `3rem 2rem`; the h1 itself is capped at `--mw` 700px and centered.
- **Content** (`.content-wrapper`): single centered column, `max-width: 700px`, padding `3rem 2rem 4rem` (2rem 1rem mobile). No sidebar, no grid.
- **Footer** (`.site-footer`): centered, muted, 1px top border, `2rem` padding.
- **Responsive**: exactly one media query, `@media (max-width: 768px)` (style.css:394-421) — shrinks base font, header/hero padding, title sizes, and collapses `.columns` (2-column `column-count`) to 1.

### 4.4 Component classes

- `.item-list` — unstyled list, rows separated by 1px `#f0f0f0` rules; the core listing device on index pages, home, and archive.
- `.section` — content grouping with serif 1.6rem `h2` (home page and archive semester groups).
- `.badge` + `.badge-draft` / `.badge-private` / `.badge-placeholder` — rounded (3px) uppercase pills.
- `.placeholder-notice` — orange dashed callout box (`#fff3e0` bg, 2px dashed `--draft`, 8px radius); styled but currently unused (0 pages).
- `.breadcrumbs`, `.page-meta` — muted small-text metadata rows.
- Content typography: styled `blockquote` (4px left accent border, italic, 1.125em), `pre`/`code` (`--code-bg`, 3px radius, 0.85em, pre scrolls with `overflow-x: auto`), full-width bordered `table` (th on `#f5f5f5`), `figure`/`figcaption`, `hr` (2px `--border`), `.columns` (2-col).
- WordPress compatibility: `.wp-block-image` (1.5rem vertical margin) and `.wp-block-separator` (styled like `hr`) are the only `wp-block-*` classes with CSS rules; all other `wp-block-*` classes in the markup (paragraph, heading, list, embed, quote, jetpack-slideshow) inherit element styling and are effectively inert.
- Global `img { max-width: 100%; height: auto }` keeps hotlinked CDN images responsive.

---

## 5. Content

### 5.1 Categories

- **Semester archives** (10 folders, 205 non-index pages): 2018-2019 (37), 2019-fall (23), 2020 (1), 2020-fall (13), 2020-spring (16), 2021 (31), 2022-spring (24), 2023 (6), 2025-spring (18), 2026-spring (15). Earlier semesters (2018–2020) are richly populated topic/poster pages; 2019-fall and 2021→2026 lecture pages are mostly stubs (§3.4).
- **Core** (40 pages): syllabus, readings-2 (current readings), about, contact, faculty, projects, resources, laptop-setup, workshops (Python, NLP), essays (nerdification-of-society, in-perpetual-ignorance).
- **Blog** (127 posts): short essays and link-collections on AI/DH pedagogy (`ai-matures-beyond-computer-science.html`, `can-you-be-self-taught.html`); many are drafts (badge-draft).
- **Labs** (15), **Topics** (18), **Research** (14): non-semester-specific course material.

### 5.2 Representative page patterns (sampled)

- **Topic page** — `topics/topic-data.html` (12KB, Private badge): long-form prose essay in `p.wp-block-paragraph` runs, meta `Created: 2019-01-09 • Modified: 2025-11-17 • Status: private`. Pattern: framing essay → readings/questions → links.
- **Syllabus** — `core/syllabus.html`: `h2/h3/h4.wp-block-heading` hierarchy (course number, meeting times, office hours), `ul.wp-block-list` of learning outcomes, grade breakdown paragraphs. Preserves WordPress editor artifacts like `class="has-dark-gray-color has-text-color has-link-color … wp-elements-682bd6629311d038dde7c45ef32989df"`.
- **Blog post** — `blog/causality.html` (Draft badge): short link-dump; retains raw `<!-- wp:paragraph -->` / `<!-- /wp:paragraph -->` and `<!-- wp:list -->` serialization comments around each block, including bare unlinked URLs typical of drafts.
- **Lab page** — `labs/lab-programming.html` (15.8KB): dense `<strong>`-headed sections of external-resource `ul`s (hundreds of outbound links); markup carries live-editor debris — `data-is-drop-zone="true"`, `wp-block wp-block-list-item` wrappers, an empty trailing paragraph with a `data--placeholder="Type / to choose a block"` span — evidence this content was scraped from the rendered block editor DOM rather than clean post HTML.
- **Poster/project page** — `2020-fall/posters-fall-2020.html` (17.7KB): `wp-block-heading` course headings followed by student poster entries with `figure.wp-block-image` images hotlinked to the WordPress CDN. `core/projects.html` cross-links the poster pages across semesters via relative links.
- **Folder index** — `2021/index.html`: count sentence + `ul.item-list` with placeholder badges (§2.3).
- **Populated stub-sibling** — `2021/0-readings-2021.html` (97 lines): CDN hero image inside a `figure` that still contains a WordPress drop-zone `<svg>` ("Drop files to upload"), followed by a numbered list of topic links into `../topics/` and `../core/`.

### 5.3 Embedded media & WordPress remnants

- **Images hotlink to WordPress**: 98 pages reference `programminghumanity.wordpress.com/wp-content/uploads/...`, 15 pages reference the older `programminghumanity.files.wordpress.com` CDN host. Only 2 images are local (§5.4).
- **Block serialization comments**: 105 pages retain `<!-- wp:* -->` comments.
- **wp-block class census** (all pages): `wp-block-paragraph` ×968, `wp-block-image` ×331, `wp-block-embed` ×156, `wp-block-list` ×129, `wp-block-heading` ×118, `wp-block-jetpack-slideshow` ×81, `wp-block-embed-youtube` ×74, `wp-block-quote` ×15, `wp-block-separator` ×11, `wp-block-gallery` ×1, `wp-block-embed-twitter` ×1.
- **Embeds**: 84 `<iframe>`s (mostly YouTube; 129 pages mention youtube). Jetpack slideshow markup is preserved but non-functional without Jetpack's JS.

### 5.4 `images/uploads/` (local media)

Only two files:
- `tree-3097419_1920.jpg` (1.3MB) — the site-wide header background photo.
- `datacamp-50px.png` (5.6KB) — DataCamp sponsor logo (though `index.html:32` still hotlinks the CDN copy of this same image rather than the local file).

---

## 6. Navigation & User Flow

- **Global header nav** (identical on all 416 pages): Syllabus → `core/syllabus.html`, Readings → `core/readings-2.html`, About → `core/about.html`. Site title links home. Social nav: single Twitter link to `https://twitter.com/ai4dhumanities` (opens new tab, `rel="noopener"`).
- **Footer**: the single line `Programming Humanity` on every page — no footer nav, no copyright year.
- **Primary flows**:
  1. Home → "Course Archives by Semester" `item-list` → semester `index.html` → lecture/topic page; return via breadcrumbs (`Home » 2021 » Page`) or the hero-header home link.
  2. Home → "Quick Links" (Syllabus, Readings, About, Full Archive).
  3. Home → `archive.html` — the full sitemap.
  4. Cross-links: `core/readings-2.html` and stub pages link into `topics/`; `core/projects.html` fans out to poster pages across semester folders.
- **archive.html** (34.9KB): "Complete archive of all content organized by semester" — 15 `div.section` groups with counts in the `h2` (`2026 Spring (15)`, … `2018 2019 (37)`, `Core (40)`, `Labs (15)`, `Topics (18)`, `Research (14)`, `Blog (127)`), each a `ul.item-list`; 401 links total = every non-index page on the site. It is the only page linking to blog posts globally (there is no blog nav entry; `core/blog.html` exists as a page but is not in the nav).
- **404.html**: standard skeleton, hero "404 – Not Found", links back to Home and Archive. Note a double-escaping bug: the `<title>` and hero render the literal text `&ndash;` because the source has `&amp;ndash;` (`404.html:6,21`). Being a static host artifact, it only works if the host is configured to serve it for missing paths.

---

## 7. Testing & Tooling

### 7.1 pytest suite (`tests/`, deps: pytest, beautifulsoup4, lxml)

Shared fixtures in `tests/conftest.py` (session-scoped): `all_html_files`, `parsed_pages` (BeautifulSoup-parsed), `subfolder_html_files`, `folder_index_files`, `css_file`.

- **`test_unit_html_structure.py`** — per-page invariants: DOCTYPE present; non-empty `<title>` ending in "Programming Humanity"; exactly one `style.css` link; header and footer present; `meta charset` + `viewport`; CSS file exists, is non-empty, has `:root` variables, key selectors, and font families; no empty `img src`; no empty iframes; **no `.placeholder-notice` elements** (regression gate for the content-population pass); no leftover `data-wp-block-attribute-key` editor attributes.
- **`test_integration_links.py`** — link resolution: home nav links resolve; every subfolder page has exactly 3 nav links and they resolve; social link points to Twitter; every `archive.html` link resolves; folder-index `item-list` links resolve; **all internal links on all pages resolve to existing files**; no page references a non-existent CSS file; no internal links still point at `programminghumanity.wordpress.com`; readings page links to topic pages.
- **`test_e2e_site.py`** — site-level: required root files (`index.html`, `archive.html`, `404.html`) and directories exist; each semester folder exists and has content; minimum 200 total pages; a hard-coded `TARGET_FILES` manifest of key stems per folder all exist; all subfolder pages share identical nav labels; every page has a footer with text, a hero with `<h1>`, breadcrumbs on non-index subfolder pages; no page has empty content.

Run: `cd tests && pip install -r requirements.txt && pytest -v` (single test: `pytest tests/test_unit_html_structure.py::TestHTMLStructure::test_all_pages_have_title -v`).

### 7.2 `dev/`

`dev/audit_bug-fix_20260317.md` — the 2026-03-17/18 migration audit & bug-fix report (scope: migration audit, content population, structural fixes, test-suite creation).

### 7.3 `tmp/` migration tooling

One-off Python scripts + JSON data used to populate stub pages from the live site (not part of the served site): `update_content.py` ("Update static HTML files with WordPress content from the content dump", includes ad-widget stripping), `update_pages.py`, `match_drafts.py`, `scan_issues.py`; data files `wp-content-dump.json`, `wp-combined-urls.json`, `pw-pages-content.json`, `content-mapping.json`, `draft-mapping.json`, `placeholder-mapping.json`.

---

## 8. Known Gaps & Limitations

1. **104 stub pages** (Appendix A) still contain only two boilerplate sentences — concentrated in the AI-course semesters (2019-fall, 2021, 2022-spring, 2023, 2025-spring, 2026-spring) plus 8 pages in 2018-2019. `README.md` and `CLAUDE.md` still cite the original "115 placeholders"; the true remaining count is 104.
2. **Stale placeholder badges**: 115 `badge-placeholder` spans across 8 index files no longer match reality — ~11 badged pages were populated but their badges were never removed (e.g. `2021/0-readings-2021.html`). `core/index.html` has 6 badges yet 0 core pages are stubs.
3. **Hotlinked images**: ~113 pages depend on WordPress CDN hosts (`programminghumanity.wordpress.com` ×98, `programminghumanity.files.wordpress.com` ×15). If the WordPress site is ever deleted, nearly all imagery breaks. Only 2 assets are local; even the home page hotlinks the CDN copy of `datacamp-50px.png` instead of the local one.
4. **Dead dynamic embeds**: 81 Jetpack slideshow blocks and the drop-zone/editor debris (`data-is-drop-zone`, "Drop files to upload" SVGs, `data--placeholder` spans) render inert or as visual noise without WordPress JS.
5. **Missing vs. a typical WordPress site**: no search, no comments, no RSS/Atom feed, no tag/category taxonomy pages, no per-post author/date archives, no pagination, no `sitemap.xml` or `robots.txt`, no favicon, no Open Graph/meta description tags, no analytics.
6. **Documentation drift**: CLAUDE.md describes `css/style.css` as minified — it is a readable 421-line file.
7. **Small bugs**: `404.html` double-escapes `&ndash;` in its title/hero (§6); index link text is Title-Cased slugs rather than real page titles ("Ai Actors And Evolution", "Xai And Ethics").
8. **Accessibility/perf**: many CDN `<img>` tags have empty or auto-generated `alt` text; the 1.3MB header JPEG loads on every page uncompressed; body text at 22px/1.8 is faithful to Twenty Nineteen but heavy.
9. **External link rot risk**: lab/research pages are dense outbound link collections (hundreds of links, some already dated: repl.it, Anaconda installers, O'Reilly Safari deep links); nothing tests external links.

---

## Appendix A: Remaining Stub Pages (104)

Pages whose entire content is the boilerplate "…is part of the &lt;semester&gt; of Programming Humanity…" paragraph pair.

**2018-2019 (8):** assignments, course-schedule, exercises, nlp-tools, posters-fall-2019, posters, quantitative-reasoning, sample-exercises

**2019-fall (22):** ai-evolution-and-neuroscience, ai-topics-fall-2019, building-brains-ai-2019, composing-ai-2019, consolidation-ai-2019, data-patterns-ai-2019, data-visualization-ai-2019, data-wrangling-ai-2019, future-trends-ai-2019, gofai-ai-2019, learning-ai-2019, machine-learning-ai-2019, machine-learning-part-b-ai-2019, nlp-a-ai-2019, nlp-ai-2019, nlp-b-ai-2019, probability-ai-2019, programming-ai-2019, reading-ai-2019, seeing-ai-2019, syllabus-ai-2019, w2-lab-data-wrangling

**2021 (24):** 3-measuring-models-2021, 4-xai-and-ethics-2021, ai-actors-and-evolution, attention-transformers, building-brains-with-artificial-neurons, classifying-text-and-language, composing-music-with-rnns, composing-music-with-rnns-2, creating-new-realities-with-gans, creating-reality-with-gans, future-directions, introduction-to-ai-2021, keras-a-framework-for-dnn, machine-learning-and-training-a-model, machine-learning-introduction, machines-learning-emotions-2021, maching-reading, programming, recap-and-future, seeing-the-world-with-cnns, seeing-the-world-with-cnns-2, the-map-of-machine-learning, transforming-intelligence, xai-ai-and-ethics

**2022-spring (14):** a-deeper-dive-into-neural-nets-2022, building-brains-with-artificial-neurons-2022, classifying-art-and-emotion-2022, classifying-text-and-language-2022, composing-music-with-rnns-2022, creating-reality-with-gans-and-vits-2022, introduction-to-ai-spr-2022, machine-learning-continued-2022, machine-learning-introduction-2022, machine-reading-2022, reinforcement-learning-and-the-future-of-ai-2022, seeing-the-world-with-cnns-2022, transforming-intelligence-2022, xai-and-ethics-2022

**2023 (6):** creating-reality-with-gans-and-vits-2023-old, introduction-to-ai-2023fall, readings-2023, reinforcement-learning-and-the-future-of-ai-orig-2023, syllabus-3, transforming-intelligence-2023-old

**2025-spring (16):** agi-spring-2025, ai-engineering-spring-2025, building-brains-with-artificial-neurons-spring-2025, classifying-art-and-emotion-spring-2025, classifying-text-and-language-spring-2025, classifying-text-art-emotion-spring-2025, creating-reality-with-gans-vae-diffusion-and-vit-models-spring-2025, dup-future-trends-ai-2019, machine-learning-continued-spring-2025, machine-learning-introduction-2022-2, machine-learning-introduction-spring-2025, reinforcement-learning-and-the-future-of-ai-orig-spring-2025, seeing-the-world-with-cnns-spring-2025, temporal-ai-rnn-spring-2025, transforming-intelligence-spring-2025, xai-and-ethics-spring-2025

**2026-spring (14):** a-deeper-dive-and-sequential-anns-spring-2026, a-deeper-dive-into-neural-nets-2026, ap-comparative-gov-2026-constitutional-terms, building-brains-with-artificial-neurons-2, building-brains-with-artificial-neurons-spring-2026, classifying-art-emotion-spring-2026, machine-learning-continued-spring-2026, machine-learning-introduction-spring-2026, syllabus-2, temporal-ai-spring-2026, test-1, test-14-16, their-eyes-were-watching-ch17-20, xai-and-ethics-spring-2026
