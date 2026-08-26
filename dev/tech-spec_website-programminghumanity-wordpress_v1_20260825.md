# Tech Spec — programminghumanity.wordpress.com (Live WordPress Site)

**Version:** v1
**Date:** 2026-08-25
**Author:** Claude Code analysis (live-site inspection via headless browser)
**Subject:** Structure, content, design, and flow of the live WordPress.com site that this repo mirrors.

---

## Table of Contents

1. [Platform & Theme](#1-platform--theme)
2. [Site Structure & Content Inventory](#2-site-structure--content-inventory)
3. [Design System](#3-design-system)
4. [Page Anatomy](#4-page-anatomy)
5. [Navigation & Flow](#5-navigation--flow)
6. [Blog Behavior](#6-blog-behavior)
7. [WordPress.com Platform Features](#7-wordpresscom-platform-features)
8. [Responsive Behavior](#8-responsive-behavior)
9. [Evidence & Method](#9-evidence--method)

---

## 1. Platform & Theme

| Attribute | Value |
|---|---|
| Platform | WordPress.com (free tier — shows WP.com marketing bar + ads) |
| Theme | **Twenty Nineteen** (`pub/twentynineteen`), with Customizer styles applied |
| Body classes (home) | `home page-template-default page page-id-49 wp-embed-responsive wp-theme-pubtwentynineteen customizer-styles-applied singular image-filters-enabled jetpack-reblog-enabled has-marketing-bar` |
| Primary/accent color | `#0073a8` (WP preset `--wp--preset--color--primary`); link blue renders as `rgb(0,115,170)` ≈ `#0073aa` |
| Image filters | **Enabled** (`image-filters-enabled`) — this produces the signature blue duotone hero |
| Homepage | Static page (page-id 49, titled "Home"); blog posts live at `/blog/` |

The visual identity of the site is essentially **stock Twenty Nineteen**: serif body text,
system-sans headings, generous whitespace, and full-viewport duotone featured-image
headers. There is no custom CSS beyond Customizer color settings.

## 2. Site Structure & Content Inventory

From `sitemap.xml` (single sitemap, no index, 80 URLs): **~60 static pages + 19 dated
blog posts + home**.

### 2.1 Page categories (flat URL space — no folders)

All pages live at root-level slugs (`/syllabus/`, `/topic-algorithms/`). WordPress
versioning-by-suffix is used for successive semesters:

- **Core:** `about`, `contact`, `faculty`, `readings`, `readings-2` (current), `syllabus`, `blog`, `topics`, `papers`, `projects`, `laptop-setup`
- **Per-semester copies (suffix pattern):** `syllabus-2021`, `syllabus-2022`, `readings-2021`, `readings-2022`, `topic-data-2021`, `topic-data-2022`, `topic-algorithms-2019`, `topic-algorithms-2019-2`, `topic-algorithms-fall-2020`, `topic-artificial-intelligence-2025`, `topic-social-networks-2025`, …
- **Topic pages (course units):** `topic-ai`, `topic-algorithms`, `topic-analytics`, `topic-bioinformatics` (+`-2`, `-2019`), `topic-data-*`, `topic-networks`, `topic-programming`, `topic-simulations`, `topic-social-networks`
- **Labs:** `lab-algorithms` (+`-2019`), `lab-artificial-intelligence`, `lab-bioinformatics`, `lab-data` (+`-2`), `lab-data-analytics`, `lab-models`, `lab-nlp`, `lab-probability`, `lab-programming`, `lab-social-networks`, `lab-visualization`
- **Student work:** `posters-2019`, `posters-fall-2020`, `posters-spring-2020`, `projects-2020-spr`
- **Misc/one-off:** `ap-us-history-2020`, `class-1-intro-and-overview`, `dh-colab`, `digital-humanities-research-fellow`, `lda-topic-modeling`, `references-data`, `reinforcement-learning-and-great-communication`, `why-study-quant-finance`, `workshop-natural-language-processing`
- **Blog posts (19 in sitemap):** dated permalinks `/YYYY/MM/DD/slug/`, e.g. `/2019/09/12/statistics-vs-ml/`, `/2018/01/04/first-blog-post/`

### 2.2 Media

All images are served from the WP.com CDN under
`programminghumanity.wordpress.com/wp-content/uploads/YYYY/MM/…` with query-string
resizing (`?w=1568`). The sitemap embeds per-page image lists (featured images,
inline figures, student poster thumbnails).

## 3. Design System

### 3.1 Typography (measured computed styles, 1280px viewport)

| Element | Font stack | Size / weight / line-height | Color |
|---|---|---|---|
| Body & paragraphs | `"Hoefler Text", Garamond, "Times New Roman", serif` | 22px / 400 / 39.6px (1.8) | `#111111` |
| Site title | system sans (`-apple-system, "Segoe UI", Roboto, …`) | 24.75px / 400 / 1.2, letter-spacing −0.02em | white on hero, near-black on plain header |
| Tagline (site description) | serif (same as body) | 24.75px / 400 | white on hero |
| Nav links | system sans | 24.75px / **700** | white on hero; `#0073aa` on plain header |
| H1 (`.entry-title`) | system sans | 49.5px / 700 / 1.2, letter-spacing −0.02em | white on hero overlay; `#111` on plain pages |
| H2/H3 in content | system sans, bold | scaled down from H1 | `#111` |
| Links in content | inherits serif context; color `#0073aa` | underline 2px | `#0073aa` |
| Image captions | small sans, centered | ~16px | gray |
| Buttons (subscribe etc.) | sans | — | bg `rgb(60,67,74)` |

**The defining typographic contrast:** serif reading text at a large 22px with 1.8
line-height, against tight bold sans headings.

### 3.2 Color palette

| Token | Value | Use |
|---|---|---|
| Text | `#111111` | body copy |
| Background | `#ffffff` | page background |
| Primary / links | `#0073a8` – `#0073aa` | links, nav on plain header, duotone tint, selection |
| Hero overlay | primary blue over `grayscale(1)` image (screen/multiply blend) | featured-image headers |
| White | `#ffffff` | hero text, title accent dash |
| Dark button | `rgb(60,67,74)` | form buttons |

### 3.3 Signature visual: the duotone hero

Every page with a featured image gets a **full-viewport header**:

- The featured `<img>` is rendered with `filter: grayscale(1)`.
- The theme's `image-filters-enabled` mode blends the primary color (`#0073a8`)
  over it, producing a dark **blue duotone** (e.g. home = tree photo, syllabus = train tracks).
- Site title + tagline (separated by an em dash), nav, and social icon overlay the
  image top-left in white.
- The **page title sits at the bottom-left** of the hero, preceded by a small
  2px × ~50px white horizontal dash (`h1.entry-title::before`).
- On pages/posts **without** a featured image, the header is plain white: black
  site title, blue nav links, and the H1 appears in black at the top of the content
  with a gray dash above it.

### 3.4 Layout

- Single column, **no sidebar**.
- Content (`.entry-content`) is `max-width: 80%` with large asymmetric margins
  (~128px left/right at 1280px, plus 60px left padding) — content sits
  **left-of-center**, a Twenty Nineteen signature (measured 1024px wide at 1280
  viewport, but text column is narrower).
- Wide/full-aligned images (`alignwide`/`alignfull`) can break out of the column.
- Footer (`#colophon`) is minimal: site name + "Create a free website or blog at WordPress.com."

## 4. Page Anatomy

```
[WP.com marketing bar — platform-injected, top]
<header id="masthead">
  .site-featured-image          ← only when featured image set
    figure.post-thumbnail       ← grayscale img + blue blend
    .entry-header > h1.entry-title   ← page title, bottom-left
  .site-branding
    .site-title  — .site-description (em-dash separated, one line)
    nav#site-navigation > ul.main-menu   (Syllabus | Readings | About)
    nav.social-navigation (Twitter icon → twitter.com/ai4dhumanities)
</header>
<main>
  article
    .entry-content              ← serif prose, wp-blocks (images, separators, lists, embeds)
    .entry-footer               ← posts only: author, date, categories
  .post-navigation              ← posts only: previous/next post
  #respond / comments           ← posts only
  .sharedaddy                   ← share buttons: X, Facebook (pages & posts)
</main>
<footer id="colophon">Programming Humanity, · Create a free website or blog at WordPress.com.</footer>
[Jetpack action bar: Comment / Reblog / Subscribe — floating bottom-right]
[Cookie consent bar — bottom]
```

### Content patterns observed

- **Syllabus:** long-form article — H2 course code, H3 section headings (Office
  Hours, Course Description, Course Materials, Attendance, Quizzes, DataCamp
  Assignments, Final Project, Grades), italic serif epigraph quote (McLuhan).
- **Topic pages:** class-by-class listings with embedded slide images, YouTube
  embeds, and links to readings/labs.
- **Blog post:** bold sans H1, meta row with icons (👤 jonchun · 🕐 date ·
  💬 Leave a comment), figure with centered small-sans caption, serif body,
  category footer ("Posted in Uncategorized"), prev/next navigation, comment form.
- **Posters/projects:** gallery grids of student poster thumbnails (per sitemap
  image lists).

## 5. Navigation & Flow

- **Global nav (3 items only):** Syllabus → `/syllabus/`, Readings → `/readings-2/`,
  About → `/about/`. One `.sub-menu` exists in the DOM but renders no items.
- **Social nav:** single Twitter icon (`@ai4dhumanities`).
- **Primary user flow:** land on Home (course pitch + DataCamp credit) → nav to
  Syllabus/Readings → follow in-content links to topic pages, labs, and
  semester-specific copies. Discovery of older semesters happens through
  **in-content cross-links**, not menus — there is no archive index page on the
  live site.
- **Blog flow:** `/blog/` lists posts (11 per page, paginated) → dated permalink →
  prev/next post navigation at the bottom.
- **No search UI, no breadcrumbs** on the live site.

## 6. Blog Behavior

- Posts index at `/blog/` (static "Posts page"), ~11 articles per page.
- Dated permalinks `/YYYY/MM/DD/slug/`.
- 19 posts in the sitemap (2018-01 → 2019-09 era, e.g. "Statistics vs ML",
  "Learn Python and Programming", "AI Matures Beyond Computer Science").
- Per-post: author `jonchun`, date, category (mostly Uncategorized), comments
  enabled, share buttons, previous/next navigation.

## 7. WordPress.com Platform Features

Injected by the platform (not part of the content design, and mostly noise to
replicate):

- Top marketing bar: "Design a site like this with WordPress.com / Get started".
- Jetpack floating action bar: Comment · Reblog · Subscribe (+ Follow overlay).
- Cookie/privacy consent bar (bottom).
- Share buttons (X, Facebook) after content.
- Comment form with WP.com auth on posts.
- Gravatar hovercards, image lazy-load/`?w=` CDN resizing.
- Advertisement slots ("Advertisement" label seen inside syllabus content — free-tier ads).

## 8. Responsive Behavior

Mobile (375×812 measured):

- Hero collapses to a **solid primary-blue block** (image hidden/cropped at small
  width), white branding/nav wrap onto multiple lines; nav items remain inline
  (Twenty Nineteen shows the full menu at this width; hamburger only appears when
  items overflow).
- Page title still bottom-left of the hero block with the white dash.
- Single column content, fluid images.

## 9. Evidence & Method

- Inspected live via headless Chromium (gstack browse) on 2026-08-25.
- Theme/platform from `meta[name=generator]` and `body` classes.
- Design tokens from `getComputedStyle` on home, `/syllabus/`, and
  `/2019/09/12/statistics-vs-ml/`.
- Inventory from `sitemap.xml` (80 URLs; no sitemap index; `sitemap-2.xml` → 404).
- Screenshots captured: home (desktop + mobile), syllabus hero + content,
  blog post header + body.
