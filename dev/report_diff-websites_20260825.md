# Diff Report — Live WordPress Site (desired) vs. Static Repo Site (current)

**Date:** 2026-08-25
**Desired state:** programminghumanity.wordpress.com (WordPress.com, Twenty Nineteen theme) — see `tech-spec_website-programminghumanity-wordpress_v1_20260825.md`
**Current state:** this repo's static site — see `tech-spec_website_programminghumanity_v1_20260825.md`
**Method:** side-by-side headless-browser screenshots (home, syllabus, blog post; desktop 1280px + mobile 375px), computed-style extraction on both sites, sitemap-vs-filesystem inventory diff.

---

## 1. Verdict Summary

Content parity is **excellent** — all 78 live sitemap slugs exist locally, body text
matches verbatim, and the repo is a superset (semester folders, archive page,
indexes). Look-and-feel parity is **poor**: the current CSS is a loose
approximation that inverts the theme's typography, drops the signature duotone
hero, and centers a layout that Twenty Nineteen deliberately left-aligns.

| Dimension | Parity | Severity of gap |
|---|---|---|
| Content (text, pages) | ✅ complete + superset | — |
| Information architecture | ✅ better than live (folders, indexes, archive) | — |
| Typography | ❌ inverted | **High** |
| Hero / header design | ❌ wrong image treatment, wrong structure | **High** |
| Layout / measure | ❌ centered vs left-weighted | Medium |
| Page furniture (meta, share, comments) | ❌ absent or different | Medium/Low |
| Blog presentation | ❌ no post meta/nav | Medium |
| Colors | ✅ accent matches (#0073aa) | Low |
| Responsive | ⚠️ untested parity | Low |

## 2. Typography — INVERTED (High)

The single biggest visual divergence. Twenty Nineteen's identity is
**serif reading text + bold sans headings**. The repo does the opposite.

| Element | Live (desired) | Repo (current) |
|---|---|---|
| Body text | **Serif** (Hoefler Text/Garamond) 22px / 1.8 | **Sans** (`--fb` system stack) ~21px |
| H1 page title | **Sans** bold 49.5px, letter-spacing −0.02em | **Serif** (`--fh`) |
| H2/H3 | Sans bold | Serif |
| Site title | Sans 24.75px regular | Serif bold, centered |
| Nav links | Sans **700**, 24.75px, sentence case | Small caps/uppercase, letter-spaced, ~13px |

Note: the repo's stylesheet already defines both stacks correctly
(`--fh`: serif, `--fb`: sans — identical strings to the live site's computed
fonts). They are simply **assigned to the wrong roles**. Fix = swap usage, not
add fonts.

## 3. Hero / Header — Wrong treatment (High)

| Aspect | Live (desired) | Repo (current) |
|---|---|---|
| Featured image | **Per-page** (home=tree, syllabus=train tracks, …) | Same tree image on every page |
| Image treatment | `grayscale(1)` + primary-blue blend → **blue duotone** | Natural color (sepia/brown), no filter |
| Header height | Full viewport (~100vh) on image pages | Fixed ~300px banner |
| Page title (H1) | Overlaid **bottom-left of the image**, white, sans bold, small white dash above | In a separate solid navy band *below* the image, serif |
| Branding position | Top-**left**: "Site Title — Tagline" on one line | **Centered**, title with dangling em dash, tagline on second line |
| No-featured-image pages | Plain **white** header, black title, blue nav | Same navy-band treatment everywhere |
| Nav placement | Left, under branding | Centered |

## 4. Layout & Measure (Medium)

| Aspect | Live | Repo |
|---|---|---|
| Content column | Wide (80% max-width), **left-of-center** with asymmetric margins | Centered, `--mw: 700px` |
| Sidebar | None | None ✅ |
| Wide images | `alignwide`/`alignfull` break out of column | Constrained to column |
| Footer | One-liner: site name + WP.com credit | Similar one-liner ✅ (minus WP.com credit) |

## 5. Page Furniture (Medium/Low)

Present locally but **not on the live site** (decide: keep as improvements or drop for fidelity):

- Breadcrumbs (`Home » Core » Syllabus`)
- "Created / Modified" date lines on pages
- Folder index pages (`ul.item-list`), `archive.html`, semester hub on home
- Placeholder badges

Present on live but **missing locally**:

- Post meta row on blog posts (👤 author · 🕐 date · 💬 comment link)
- Category footer ("Posted in …") and **previous/next post navigation**
- Share buttons (X, Facebook) — static equivalents possible via share-intent URLs
- Comments (WP.com-hosted — not replicable statically; omit or link back)
- Jetpack subscribe/reblog bar, WP.com marketing bar, cookie bar — *platform
  chrome, recommend NOT replicating*
- `/blog/` paginated post index in live style (repo has a flat item-list index)

## 6. Content Inventory Diff

- **Live → Repo:** 78/78 sitemap slugs present locally (verified 2026-08-25). No missing pages.
- **Repo → Live:** repo adds ~330 files with no live URL: per-semester duplicates
  (organized into `2018-2019/` … `2026-spring/` folders), folder indexes,
  `archive.html`, `404.html`, placeholder pages. These reorganize the same
  content — an IA improvement over the live site's flat, menu-less sprawl.
- **Images:** both sides reference the same WP.com CDN URLs. Repo has a small
  `images/uploads/` local set. Risk: CDN links break if the WP.com site is ever
  deleted — mirroring uploads locally is a migration-hardening task.
- **Blog:** live sitemap lists 19 posts; repo `blog/` holds 127 pages (includes
  posts not in the sitemap plus placeholders) — repo is the superset.

## 7. Colors (Low)

Accent `#0073aa` matches live link blue; text `#111` and white background match.
Missing: the **duotone primary** `#0073a8` applied as image blend, and the live
hero's white-on-image palette. Repo's navy title band (`~#1a1d33`) has no
equivalent on the live site — it's an invention.

## 8. Behavior / Interactivity

| Feature | Live | Repo | Note |
|---|---|---|---|
| Comments | WP.com comment form | none | can't replicate statically; link to WP.com or omit |
| Search | none visible | none | parity ✅ |
| Subscribe/Reblog | Jetpack bar | none | recommend omit |
| Share buttons | X/Facebook | none | static share-intent links possible |
| Image lazy-load / srcset | WP.com CDN `?w=` params | plain `<img>` | optional `?w=` params work cross-origin |
| Mobile hero | solid primary-blue block, white text | untested/likely banner crop | needs responsive pass |

## 9. Prioritized Gap List

1. **Swap typography roles** (serif body ↔ sans headings) — one CSS change, biggest fidelity win.
2. **Hero redesign**: full-viewport, per-page featured image, grayscale+blue-blend duotone, overlaid bottom-left H1 with white dash, left-aligned branding "Title — Tagline".
3. **Plain-white header variant** for pages without featured images.
4. **Layout**: widen content column, left-weight it; support wide images.
5. **Blog furniture**: post meta row, category footer, prev/next links, live-style `/blog` index.
6. **Nav restyle**: bold sans, sentence case, left-aligned.
7. Decide keep/drop for repo-only extras (breadcrumbs, date lines, archive) — recommend keeping but styling them quietly.
8. Mirror featured images per page (needs a page→featured-image map scraped from live site).
9. Responsive pass to match mobile hero behavior.
