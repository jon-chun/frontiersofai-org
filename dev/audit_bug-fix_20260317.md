# Audit & Bug-Fix Report

**Project:** Programming Humanity Static Site
**Date:** 2026-03-17 / 2026-03-18
**Source:** WordPress site (programminghumanity.wordpress.com, Twenty Nineteen theme)
**Scope:** Full migration audit, content population, structural fixes, test suite creation

---

## 1. Executive Summary

Migrated and audited a 416-page static HTML/CSS site generated from a WordPress XML export. Crawled the live WordPress admin (282 pages/posts) to populate content, matched the Twenty Nineteen theme look and feel, fixed 1,500+ issues across navigation, links, images, editor artifacts, and placeholder pages. Delivered a 90-test suite covering unit, integration, and E2E concerns. All tests pass.

---

## 2. Issues Found & Fixed

### 2.1 Theme & Layout (CSS)

| Issue | Resolution |
|-------|-----------|
| CSS did not match WordPress Twenty Nineteen theme | Rewrote `css/style.css`: serif headings (Hoefler Text/Garamond), 22px base font, 1.8 line-height, WP blue links (#0073aa), dark header overlay with featured tree image, clean white footer |
| Hero/header used solid color instead of featured image | Added `background-image` on `.site-header` referencing local `images/uploads/tree-3097419_1920.jpg` with `::before` dark overlay |
| Footer had extra links not present on WP | Simplified to single `<p>Programming Humanity</p>` matching WP |

### 2.2 Navigation

| Issue | Files | Resolution |
|-------|-------|-----------|
| Nav had 6 items (Syllabus, Readings, About, Topics, Blog, Archive); WP has 3 | 416 | Removed Topics, Blog, Archive from all pages |
| Social link pointed to `@jonchun2000`; WP uses `@ai4dhumanities` | 416 | Updated Twitter URL and removed bird emoji |
| Readings nav linked to `2026-spring/readings.html` (placeholder) | 416 | Changed to `core/readings-2.html` (WP's active Readings page) |
| Readings link on `readings-2.html` itself pointed to `2025-spring/index.html` | 1 | Fixed to self-reference `../core/readings-2.html` |

### 2.3 Content Population

| Source | Pages Updated | Method |
|--------|--------------|--------|
| Public/Private WP pages | 128 | Crawled via browser (logged-in admin), extracted `.entry-content` HTML |
| Password-protected WP pages | 20 | Accessed via WP admin block editor, extracted from `iframe[name="editor-canvas"]` `.is-root-container` |
| Lecture stub pages (no WP equivalent) | 104 | Added semester context links (these topics exist as sections within parent Topic pages, not individual WP pages) |
| Empty/short draft blog posts | 20 | Added draft/in-progress notices |
| Remaining `core/` placeholders | 6 | Added syllabus/readings links |

**Total: 278 pages updated with content.**

### 2.4 Broken & Incorrect Links

| Issue | Count | Resolution |
|-------|-------|-----------|
| Internal links pointing to `programminghumanity.wordpress.com` | 152 | Converted to local relative paths |
| Readings page topics 1-14 were plain text | 14 | Added live links to most recent corresponding topic pages (2025-spring where available, then 2022-spring, 2020-spring) |
| `core/contact.html` had absolute WP path `/contact/` | 1 | Changed to local `contact.html` |
| `wp.me` shortlinks (unresolvable without fetching) | ~5 | Left as-is (external shortlinks) |

### 2.5 Images & Media

| Issue | Count | Resolution |
|-------|-------|-----------|
| Hero image referenced WP CDN | 1 | Downloaded locally to `images/uploads/tree-3097419_1920.jpg` (1.3 MB) |
| DataCamp logo referenced WP CDN | 1 | Downloaded locally to `images/uploads/datacamp-50px.png` (5.5 KB) |
| Empty `<img src="">` | 1 | Removed from `blog/predicting-the-future.html` |
| Empty/blob `<iframe>` (lost YouTube embeds) | 19 | Replaced with `<p class="embed-placeholder">` |
| External image references (WP CDN) | 456 | Retained (images still served from WordPress CDN) |

### 2.6 Editor Artifact Cleanup

| Artifact | Count | Resolution |
|----------|-------|-----------|
| `data-wp-block-attribute-key` attributes | 434 | Removed |
| `aria-multiline` / `aria-readonly` attributes | 868 | Removed |
| `placeholder-notice` class divs | 6 | Replaced with content |
| WordPress ad blocks (`wordads-ad-wrapper`) | ~200 | Stripped during content extraction |
| Share widgets (`sharedaddy`, `jp-post-flair`) | ~200 | Stripped during content extraction |

---

## 3. Test Suite

**Location:** `tests/`
**Runner:** `pytest` with `beautifulsoup4` + `lxml`
**Result:** 90 tests, all passing (~2.7s)

### 3.1 Unit Tests (`test_unit_html_structure.py`) &mdash; 17 tests

| Test | What It Checks |
|------|---------------|
| `test_all_pages_have_doctype` | Every HTML file starts with `<!DOCTYPE html>` |
| `test_all_pages_have_nonempty_title` | Every page has a non-empty `<title>` |
| `test_all_titles_end_with_programming_humanity` | Title format consistency |
| `test_all_pages_link_to_style_css` | Every page links to `style.css` |
| `test_all_pages_have_header` | Every page has `<header>` |
| `test_all_pages_have_footer` | Every page has `<footer>` |
| `test_all_pages_have_meta_charset` | UTF-8 charset declared |
| `test_all_pages_have_meta_viewport` | Responsive viewport meta |
| `test_css_file_exists` | `css/style.css` exists |
| `test_css_file_nonempty` | CSS file has content |
| `test_css_has_root_variables` | CSS uses custom properties |
| `test_css_has_key_selectors` | Key class selectors present |
| `test_css_has_font_families` | Theme fonts declared |
| `test_no_empty_img_src` | No `<img>` with empty `src` |
| `test_no_empty_iframes` | No `<iframe>` with empty/blob `src` |
| `test_no_placeholder_notices` | No remaining placeholder banners |
| `test_no_editor_attributes` | No `data-wp-block-attribute-key` artifacts |

### 3.2 Integration Tests (`test_integration_links.py`) &mdash; 10 tests

| Test | What It Checks |
|------|---------------|
| `test_index_nav_links_resolve` | Homepage nav links point to existing files |
| `test_subfolder_nav_has_exactly_3_links` | Nav has exactly 3 items (Syllabus, Readings, About) |
| `test_subfolder_nav_links_resolve` | Subfolder nav links resolve |
| `test_social_link_points_to_twitter` | Social link → twitter.com/ai4dhumanities |
| `test_archive_links_resolve` | Archive page links are valid |
| `test_folder_index_item_list_links_resolve` | Folder index listings link to existing files |
| `test_all_internal_links_resolve` | Comprehensive: every `<a href>` to a local file resolves |
| `test_no_page_references_nonexistent_css` | No broken CSS references |
| `test_no_wordpress_internal_links` | No links to WP for pages that exist locally |
| `test_readings_page_has_topic_links` | Readings `<ol>` has 10+ hyperlinked topics |

### 3.3 E2E Tests (`test_e2e_site.py`) &mdash; 63 tests

| Test | What It Checks |
|------|---------------|
| `test_required_root_files_exist` (4) | index.html, 404.html, archive.html, css/style.css |
| `test_required_directories_exist` (3) | css, core, tests |
| `test_semester_folder_exists` (10) | All 10 semester dirs present |
| `test_semester_folder_has_content` (10) | Each semester has 2+ HTML files |
| `test_minimum_total_pages` | 200+ pages site-wide |
| `test_target_file_exists` (30) | 30 key files verified |
| `test_all_subfolder_pages_have_same_nav_labels` | Consistent nav across all pages |
| `test_all_pages_have_footer_with_text` | Footer present with text |
| `test_all_pages_have_hero_with_h1` | Hero section with `<h1>` on every page |
| `test_subfolder_non_index_pages_have_breadcrumbs` | Breadcrumbs on inner pages |
| `test_no_pages_with_empty_content` | Every `.page-content` has 20+ chars |

---

## 4. Known Remaining Items

| Item | Status | Notes |
|------|--------|-------|
| Per-page featured images | Not implemented | WP uses different header images per page (railroad tracks for Syllabus, etc.); local uses site-wide tree image. Would require downloading each image and adding per-page CSS or inline styles. |
| 456 external image references | Retained | Images still served from WordPress CDN (`programminghumanity.wordpress.com/wp-content/uploads/`). Could be downloaded locally for full offline capability. |
| 19 password-protected page passwords | Not extracted | Lab and Topic pages behind WP post passwords; content was extracted via admin editor bypass. |
| `wp.me` shortlinks (~5) | Unresolved | Cannot resolve without HTTP fetching; left as external links. |
| 111 lecture stub pages | Contextual links only | These lecture topics (e.g., "Building Brains with Artificial Neurons Spring 2025") don't exist as individual WP pages. Content lives within parent Topic pages. Stubs link to semester index and Readings. |
| WP "Share this" / ads | Intentionally omitted | WordPress sharing buttons and advertisements not replicated in static site. |
| Contact form | Non-functional | WP Jetpack contact form HTML preserved but cannot submit (no backend). |

---

## 5. Files Modified

- `css/style.css` &mdash; Complete rewrite (Twenty Nineteen theme match)
- `tests/conftest.py` &mdash; Session-scoped fixtures
- `tests/test_unit_html_structure.py` &mdash; 17 unit tests
- `tests/test_integration_links.py` &mdash; 10 integration tests
- `tests/test_e2e_site.py` &mdash; 63 E2E tests
- `images/uploads/tree-3097419_1920.jpg` &mdash; Downloaded hero image
- `images/uploads/datacamp-50px.png` &mdash; Downloaded DataCamp logo
- **416 HTML files** &mdash; Nav, footer, social link, content, link fixes

---

## 6. Verification

```
$ python3 -m pytest tests/ -v
========================= 90 passed in 2.73s =========================
```
