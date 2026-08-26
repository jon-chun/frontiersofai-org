# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Static HTML/CSS site for "Programming Humanity: Computational Thinking for Humanity" — migrated from programminghumanity.wordpress.com. ~400 HTML pages, one shared CSS file, no build system or JS framework.

## Local Dev

```bash
python3 -m http.server 8080
# Open http://localhost:8080/
```

## Tests

```bash
cd tests && pip install -r requirements.txt && pytest -v
```

Test suite (pytest + BeautifulSoup/lxml):
- `test_unit_html_structure.py` — every HTML page has DOCTYPE, title, CSS link, header, footer
- `test_integration_links.py` — all internal links (nav, archive, folder indexes) resolve to existing files
- `test_e2e_site.py` — required root files/dirs exist, semester folders have content, minimum page count (200+), target file coverage

Run a single test file: `pytest tests/test_unit_html_structure.py -v`
Run a single test: `pytest tests/test_unit_html_structure.py::TestHTMLStructure::test_all_pages_have_title -v`

## Architecture

**No build step.** All pages are flat `.html` files served statically. Every page shares:
- `css/style.css` — single minified stylesheet (CSS custom properties for theming)
- Common header with nav (`nav.main-nav`) and footer structure
- CSS link uses relative paths (`css/style.css`, `../css/style.css`, etc.) based on depth

**Page template pattern** (all pages follow this):
```
<!DOCTYPE html> → <head> with relative CSS link → <header class="site-header"> with nav →
<section class="hero"> → <main class="content-wrapper"> → <div class="page-content"> → <footer>
```

**Content structure:**
- Year/semester folders (`2018-2019/`, `2019-fall/`, `2021/`, etc.) — course material organized by semester
- `core/` — structural pages (about, contact, faculty, syllabus)
- `labs/`, `topics/`, `research/` — non-year-specific content
- `blog/` — blog posts (127 pages, largest folder)
- Each content folder has an `index.html` listing its pages via `ul.item-list`

**Placeholder pages:** 115 pages have structure but no content (marked with `.badge-placeholder` / `.placeholder-notice`). These need content populated from the live WordPress site.

## Key Conventions

- Flat file structure: `folder/page-name.html`, not `folder/page-name/index.html`
- Images reference WordPress CDN URLs (`programminghumanity.wordpress.com/wp-content/uploads/...`), not local paths, except for files in `images/uploads/`
- CSS classes use WordPress block conventions (`.wp-block-image`, `.wp-block-separator`) alongside custom classes
- Nav links in header must be kept consistent across all pages
- Breadcrumbs use relative links matching the folder structure
