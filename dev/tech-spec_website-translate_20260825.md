# Plan — Replicating the WordPress Look/Feel/Flow in the Static Repo

**Date:** 2026-08-25
**Inputs:**
- `tech-spec_website_programminghumanity_v1_20260825.md` (current static site)
- `tech-spec_website-programminghumanity-wordpress_v1_20260825.md` (desired live site)
- `report_diff-websites_20260825.md` (gap analysis)

---

## 1. Overview

The repo already has full **content** parity with programminghumanity.wordpress.com
(all 78 live URLs mirrored, plus a better information architecture: semester
folders, indexes, archive). What it lacks is **design** parity: the current CSS
approximates the live site but inverts the typography, replaces the signature
full-viewport blue-duotone hero with a generic banner + navy title band, and
centers a layout Twenty Nineteen left-weights.

This plan re-themes the static site to be visually indistinguishable from the
Twenty Nineteen live site (minus WordPress.com platform chrome), using batch HTML
transforms + one shared stylesheet, verified with automated screenshot comparison
against the live site.

## 2. Goals

**G1 — Typography fidelity:** serif body (Hoefler Text stack, 22px/1.8), bold sans
headings/nav/titles, matching the measured computed styles in the WP spec.
**G2 — Hero fidelity:** full-viewport per-page featured-image header with
grayscale + `#0073a8` blend duotone, white branding top-left ("Title — Tagline"
one line), bold sans nav below, H1 overlaid bottom-left with white dash; plain
white header variant for pages without a featured image.
**G3 — Layout fidelity:** wide left-weighted content column, `alignwide/alignfull`
support, minimal footer.
**G4 — Flow fidelity:** blog posts get meta row (author/date), category footer,
prev/next navigation; `/blog` index styled like the live paginated list; nav stays
the 3-item menu (Syllabus/Readings/About) + Twitter.
**G5 — Self-sufficiency (hardening):** mirror hero/featured images locally so
look survives WP.com deletion (body images can follow later).
**G6 — Verification:** automated pixel/style comparison live-vs-local per page
class, plus extended pytest suite.

**Non-goals:** WP.com marketing bar, Jetpack subscribe/reblog bar, cookie bar,
comments (link back to WP.com post instead or omit), ads, Gravatar hovercards.
Keep repo-only IA improvements (breadcrumbs, archive, semester indexes) but
restyle them to sit quietly inside the theme.

## 3. Current Situation (from diff report)

- Content: ✅ complete superset; images hotlink to WP.com CDN.
- Typography: ❌ serif/sans roles inverted (fix is role reassignment — both
  stacks already exist as `--fh`/`--fb` in `css/style.css`).
- Hero: ❌ same tree image everywhere, no duotone, ~300px banner, separate navy
  title band (an invention not on the live site).
- Layout: ❌ centered 700px column vs live wide left-weighted column.
- Blog: ❌ no post meta, categories, or prev/next; index is a plain item list.
- Furniture: repo-only breadcrumbs/date-lines (keep, restyle); missing share
  links (add static share-intent links).

## 4. Sequenced Task List

### Phase 0 — Asset & data capture (prerequisite for hero work)
0.1 Scrape a **page→featured-image map** from the live site: for each of the 78
    live URLs, record the `.site-featured-image img` src (many pages share
    images; some have none). Output `dev/data/featured-images.json`.
0.2 Download those featured images (and the poster-grid thumbnails) into
    `images/uploads/YYYY/MM/…` preserving WP paths.
0.3 Capture reference screenshots of the live site (home, syllabus, readings,
    about, one topic, one lab, one poster page, blog index, one post; desktop +
    mobile) into `dev/reference/` as the visual acceptance targets.

### Phase 1 — CSS re-theme (one file, site-wide effect)
1.1 Swap font roles in `css/style.css`: body/paragraphs → `--fh` serif 22px/1.8;
    headings, site title, nav, meta → `--fb` sans (sizes per WP spec §3.1).
1.2 Rebuild header/hero styles: `~100vh` featured-image header, `filter:
    grayscale(1)` + blue blend (`mix-blend-mode: multiply/screen` overlay of
    `#0073a8`, matching Twenty Nineteen), white left-aligned branding, H1
    bottom-left with `::before` white dash; and the plain-white header variant.
1.3 Layout: content column to live measure (wide, left-weighted margins),
    `alignwide/alignfull`, caption styling, link underline 2px, dark form buttons.
1.4 Restyle repo-only furniture (breadcrumbs, date lines, item lists, badges) in
    quiet gray sans so they don't fight the theme.

### Phase 2 — Batch HTML transforms (scripted, all ~416 pages)
2.1 Write `dev/scripts/retheme.py` (Python + BeautifulSoup — same stack as the
    test suite; run with `uv`). Transforms, idempotent per page:
    a. Header rewrite: branding to "Title — Tagline" single line; move H1 into
       the hero; inject per-page featured image (from featured-images.json;
       fall back by page-type: semester pages inherit their live counterpart's
       image, placeholders get the white-header variant).
    b. Blog posts: add meta row (author `jonchun`, date — parse from existing
       content or the WP sitemap timestamps), category footer, prev/next links
       (chronological order from the blog index).
    c. Add static share links (X/Facebook share-intent URLs).
    d. Keep breadcrumbs/date-lines but wrapped in a `.page-meta` class for quiet styling.
2.2 Regenerate `blog/index.html` in live style (title + excerpt list, 11/page
    pagination or a single long list — recommend single list for a static site).
2.3 Point hero `<img>` srcs at the locally mirrored copies from Phase 0.2.

### Phase 3 — Responsive & polish
3.1 Mobile: hero collapses to solid `#0073a8` block with white text (live
    behavior), fluid type scale (live uses ~1.125 rem scaling below 768px).
3.2 Print stylesheet parity (Twenty Nineteen ships print.css) — optional.

### Phase 4 — Verification & regression safety
4.1 Extend pytest: every page has exactly one hero (image or white variant);
    blog posts have meta/prev-next; fonts assigned per role (parse CSS);
    featured-image map coverage.
4.2 Visual QA loop with the headless browser: screenshot local vs live for the
    9 reference pages at 1280px + 375px; compare side-by-side; iterate CSS until
    match. Automatable as a fan-out workflow (below).
4.3 Run full test suite; commit checkpoints per phase (ask before merging to main
    per house rules — work is on `main` trunk, commit when approved).

### Phase 5 — Content completion (parallel/ongoing)
5.1 Populate remaining placeholder pages from the live site (scrape
    `.entry-content` per matching URL).
5.2 Optionally mirror **all** body images locally (harden against CDN loss) and
    rewrite `wp-content/uploads` URLs to `images/uploads/`.

**Sequencing rationale:** Phase 0 unblocks the hero (the one thing that needs
live-site data). Phase 1 is high-leverage (one file). Phase 2 is mechanical and
scriptable. Verification (4) runs after each of 1-3, not only at the end.

## 5. Recommended Methods

- **Batch transforms over hand-edits:** 416 pages, no build system → a single
  idempotent Python/BeautifulSoup script (checked into `dev/scripts/`) is the
  reliable way; re-runnable as pages get added. Use `uv run`.
- **Keep the no-build architecture.** Do not introduce a static-site generator;
  the flat-file + one-CSS model is working and tested. All look/feel changes
  concentrate in `css/style.css` + a scripted markup normalization.
- **Duotone via CSS, not image editing:** grayscale filter + blend overlay
  reproduces Twenty Nineteen exactly and works with any future hero image.
- **Live site as oracle:** every styling decision traces to a measured computed
  style or reference screenshot, not memory of the theme. (Optionally crib from
  the actual Twenty Nineteen `style.css` — it's GPL — rather than re-deriving.)
- **Scrape while you can:** the WP.com site is the source of truth for featured
  images, post dates, and placeholder content. Capture `featured-images.json`,
  post metadata, and remaining content early (Phase 0) so later phases don't
  depend on the live site staying up.

## 6. Skills & Automated Workflows to Use

| Task | Tool/Skill |
|---|---|
| All live-site scraping, screenshots, computed styles | `/browse` (gstack headless browser) — already used for the specs |
| Visual QA screenshots (mobile/tablet/desktop) | `/browse` `responsive` + `screenshot` commands |
| Spec refinement before Phase 1/2 implementation | `/spec` (gstack) if requirements need tightening |
| Commit messages at phase checkpoints | `commit-helper` |
| Parallel page-transform + verification at scale | **Claude Code Workflow**: fan out one agent per content folder (disjoint files → clean merges), then a verify stage that screenshots each folder's sample page against its live reference; loop until visual diffs pass |
| Test-first on the retheme script | `/tdd` (only if desired) |
| Structure/regression checks | existing pytest suite + Phase 4.1 additions |

Suggested workflow shape for Phase 2/4 (run when you say go):
`pipeline(folders, transform-agent, screenshot-verify-agent)` with worktree
isolation unnecessary (file ownership is disjoint by folder).

## 7. Recommendation

Execute Phases 0-1 first as a single session (asset capture + CSS re-theme) —
that alone closes the two High-severity gaps (typography, hero) and will make the
site read as "the same site" at a glance. Then run Phase 2 as a scripted batch
with the test suite as a safety net, and Phase 4's screenshot loop as acceptance.
Phase 5 (placeholder content, local image mirroring) is independent and can run
any time — but do the Phase 0 scraping now while the live site is up.

Estimated effort: Phases 0-1 ≈ one focused session; Phase 2 ≈ one session
(script + run + fix); Phases 3-4 ≈ one session. Content completion (5) is
open-ended and parallelizable.
