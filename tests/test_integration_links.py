"""Integration tests: internal links resolve to existing files."""
import pytest
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import unquote

SITE_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_href(href, page_path):
    """Resolve a relative href to an absolute Path, or return None for external/anchor links."""
    if not href or href.startswith(("http://", "https://", "mailto:", "#", "javascript:")):
        return None
    # Strip fragment
    href = href.split("#")[0]
    if not href:
        return None
    href = unquote(href)
    return (page_path.parent / href).resolve()


def _collect_broken_links(page_path, soup, selector="a"):
    """Return list of broken internal hrefs found under the given CSS selector."""
    broken = []
    for tag in soup.select(selector):
        href = tag.get("href", "")
        target = _resolve_href(href, page_path)
        if target is not None and not target.exists():
            broken.append(href)
    return broken


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

class TestNavLinks:
    def test_index_nav_links_resolve(self, site_root):
        """All nav links on index.html must resolve to existing files."""
        index = site_root / "index.html"
        soup = BeautifulSoup(index.read_text(), "lxml")
        broken = _collect_broken_links(index, soup, "nav.main-nav a")
        assert not broken, f"Broken nav links on index.html: {broken}"

    def test_subfolder_nav_has_exactly_3_links(self, site_root, subfolder_html_files):
        """Nav on subfolder pages should have exactly 3 links: Syllabus, Readings, About."""
        expected_labels = {"Syllabus", "Readings", "About"}
        failures = []
        for f in subfolder_html_files[:50]:  # sample for speed
            soup = BeautifulSoup(f.read_text(), "lxml")
            nav = soup.select_one("nav.main-nav")
            if not nav:
                continue
            links = nav.find_all("a")
            labels = {a.get_text(strip=True) for a in links}
            if labels != expected_labels:
                failures.append(
                    f"{f.relative_to(site_root)}: got {sorted(labels)}"
                )
        assert not failures, (
            f"Pages with unexpected nav links: {failures[:10]}"
        )

    def test_subfolder_nav_links_resolve(self, site_root, subfolder_html_files):
        """Nav links on subfolder pages must resolve to existing files."""
        broken = []
        for f in subfolder_html_files:
            soup = BeautifulSoup(f.read_text(), "lxml")
            for link in _collect_broken_links(f, soup, "nav.main-nav a"):
                broken.append(f"{f.relative_to(site_root)} -> {link}")
        assert not broken, f"Broken subfolder nav links: {broken[:10]}"


# ---------------------------------------------------------------------------
# Social link
# ---------------------------------------------------------------------------

class TestSocialLink:
    def test_social_link_points_to_twitter(self, parsed_pages):
        """Social nav must link to twitter.com."""
        failures = []
        for path, _, soup in parsed_pages:
            social = soup.select_one(".social-nav a")
            if social:
                href = social.get("href", "")
                if "twitter.com" not in href:
                    failures.append(
                        f"{path.relative_to(SITE_ROOT)}: {href}"
                    )
            else:
                failures.append(
                    f"{path.relative_to(SITE_ROOT)}: missing .social-nav a"
                )
        assert not failures, f"Social link issues: {failures[:10]}"


# ---------------------------------------------------------------------------
# Archive page
# ---------------------------------------------------------------------------

class TestArchiveLinks:
    def test_archive_links_resolve(self, site_root):
        """All internal links on archive.html must point to existing files."""
        archive = site_root / "archive.html"
        soup = BeautifulSoup(archive.read_text(), "lxml")
        broken = _collect_broken_links(archive, soup, ".page-content a")
        assert not broken, f"Broken archive links: {broken[:20]}"


# ---------------------------------------------------------------------------
# Folder index pages
# ---------------------------------------------------------------------------

class TestFolderIndexLinks:
    def test_folder_index_item_list_links_resolve(self, site_root, folder_index_files):
        """Every link in .item-list on folder index pages must point to an existing file."""
        broken = []
        for idx in folder_index_files:
            soup = BeautifulSoup(idx.read_text(), "lxml")
            for link in _collect_broken_links(idx, soup, ".item-list a"):
                broken.append(f"{idx.parent.name}/{link}")
        assert not broken, f"Broken folder index links: {broken[:20]}"


# ---------------------------------------------------------------------------
# Comprehensive internal link scan
# ---------------------------------------------------------------------------

class TestAllInternalLinks:
    def test_all_internal_links_resolve(self, site_root, parsed_pages):
        """Every internal <a href> across ALL pages must resolve to an existing file."""
        broken = []
        for path, _, soup in parsed_pages:
            for bad in _collect_broken_links(path, soup):
                broken.append(f"{path.relative_to(site_root)} -> {bad}")
        assert not broken, (
            f"{len(broken)} broken internal links found. First 20: {broken[:20]}"
        )


# ---------------------------------------------------------------------------
# CSS file references
# ---------------------------------------------------------------------------

class TestCSSReferences:
    def test_no_page_references_nonexistent_css(self, site_root, parsed_pages):
        """No page should reference a CSS file that does not exist on disk."""
        broken = []
        for path, _, soup in parsed_pages:
            for link in soup.find_all("link", rel="stylesheet"):
                href = link.get("href", "")
                target = _resolve_href(href, path)
                if target is not None and not target.exists():
                    broken.append(
                        f"{path.relative_to(site_root)} -> {href}"
                    )
        assert not broken, f"References to missing CSS files: {broken[:20]}"


# ---------------------------------------------------------------------------
# WordPress internal links
# ---------------------------------------------------------------------------

# Pages that exist locally and should not link to WordPress
_LOCAL_SLUGS = {
    "syllabus", "readings", "about", "contact", "faculty",
    "topics", "labs", "archive",
}


class TestWordPressLinks:
    def test_no_wordpress_internal_links(self, site_root, parsed_pages):
        """No page should link to programminghumanity.wordpress.com for pages that exist locally.

        External links to WP for truly external references are OK, but links
        to syllabus, readings, topics, about, etc. should use local paths.
        """
        failures = []
        for path, _, soup in parsed_pages:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "programminghumanity.wordpress.com" not in href:
                    continue
                # Check if the link target matches a known local slug
                href_lower = href.lower().rstrip("/")
                if any(slug in href_lower.split("/") for slug in _LOCAL_SLUGS):
                    failures.append(
                        f"{path.relative_to(site_root)}: {href}"
                    )
        assert not failures, (
            f"Pages linking to WordPress for local content: {failures[:20]}"
        )


# ---------------------------------------------------------------------------
# Readings page structure
# ---------------------------------------------------------------------------

class TestReadingsPage:
    def test_readings_page_has_topic_links(self, site_root):
        """The readings page (core/readings-2.html) should have at least 10 links in its <ol> list."""
        readings = site_root / "core" / "readings-2.html"
        if not readings.exists():
            pytest.skip("core/readings-2.html does not exist yet")
        soup = BeautifulSoup(readings.read_text(), "lxml")
        ol = soup.find("ol")
        assert ol is not None, "core/readings-2.html has no <ol> element"
        links = ol.find_all("a")
        assert len(links) >= 10, (
            f"core/readings-2.html <ol> has only {len(links)} links, expected >= 10"
        )
