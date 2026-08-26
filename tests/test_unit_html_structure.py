"""Unit tests: every HTML page has valid structure and required elements."""
import pytest
from bs4 import BeautifulSoup
from pathlib import Path

SITE_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _page_id(val):
    """Show relative path in test parametrize IDs."""
    if isinstance(val, tuple):
        return str(val[0].relative_to(SITE_ROOT))
    if isinstance(val, Path):
        return str(val.relative_to(SITE_ROOT))
    return str(val)


# ---------------------------------------------------------------------------
# DOCTYPE
# ---------------------------------------------------------------------------

class TestDoctype:
    def test_all_pages_have_doctype(self, parsed_pages):
        """Every HTML page must begin with <!DOCTYPE html>."""
        failures = []
        for path, text, _ in parsed_pages:
            if not text.strip().lower().startswith("<!doctype html"):
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"Pages missing <!DOCTYPE html>: {failures}"


# ---------------------------------------------------------------------------
# <title>
# ---------------------------------------------------------------------------

class TestTitle:
    def test_all_pages_have_nonempty_title(self, parsed_pages):
        """Every page must have a non-empty <title>."""
        failures = []
        for path, _, soup in parsed_pages:
            if not soup.title or not soup.title.string or not soup.title.string.strip():
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"Pages with missing or empty <title>: {failures}"

    def test_all_titles_end_with_programming_humanity(self, parsed_pages):
        """Every main-site <title> must end with 'Programming Humanity'.

        archive/ and website/ are standalone sites with their own suffixes
        ("... Archive", "... (Fall 2026)") and are exempt.
        """
        failures = []
        for path, _, soup in parsed_pages:
            if path.relative_to(SITE_ROOT).parts[0] in ("archive", "website"):
                continue
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
                if not title.endswith("Programming Humanity"):
                    failures.append(
                        f"{path.relative_to(SITE_ROOT)}: '{title}'"
                    )
        assert not failures, (
            f"Titles not ending with 'Programming Humanity': {failures[:20]}"
        )


# ---------------------------------------------------------------------------
# CSS <link>
# ---------------------------------------------------------------------------

class TestCSSLink:
    def test_all_pages_link_to_style_css(self, parsed_pages):
        """Every page must have a <link rel='stylesheet'> pointing to style.css."""
        failures = []
        for path, _, soup in parsed_pages:
            links = [
                tag for tag in soup.find_all("link", rel="stylesheet")
                if "style.css" in tag.get("href", "")
            ]
            if not links:
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"Pages missing CSS link to style.css: {failures}"


# ---------------------------------------------------------------------------
# <header> and <footer>
# ---------------------------------------------------------------------------

class TestHeaderFooter:
    def test_all_pages_have_header(self, parsed_pages):
        """Every page must contain a <header> element."""
        failures = []
        for path, _, soup in parsed_pages:
            if not soup.find("header"):
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"Pages missing <header>: {failures}"

    def test_all_pages_have_footer(self, parsed_pages):
        """Every page must contain a <footer> element."""
        failures = []
        for path, _, soup in parsed_pages:
            if not soup.find("footer"):
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"Pages missing <footer>: {failures}"


# ---------------------------------------------------------------------------
# <meta charset> and <meta viewport>
# ---------------------------------------------------------------------------

class TestMetaTags:
    def test_all_pages_have_meta_charset(self, parsed_pages):
        """Every page must have <meta charset='UTF-8'>."""
        failures = []
        for path, _, soup in parsed_pages:
            charset_tag = soup.find("meta", attrs={"charset": True})
            if not charset_tag or charset_tag["charset"].upper() != "UTF-8":
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"Pages missing <meta charset='UTF-8'>: {failures}"

    def test_all_pages_have_meta_viewport(self, parsed_pages):
        """Every page must have <meta name='viewport'>."""
        failures = []
        for path, _, soup in parsed_pages:
            viewport_tag = soup.find("meta", attrs={"name": "viewport"})
            if not viewport_tag:
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"Pages missing <meta name='viewport'>: {failures}"


# ---------------------------------------------------------------------------
# CSS file
# ---------------------------------------------------------------------------

class TestCSSFile:
    def test_css_file_exists(self, css_file):
        """css/style.css must exist."""
        assert css_file.exists(), "css/style.css does not exist"

    def test_css_file_nonempty(self, css_file):
        """css/style.css must have meaningful content."""
        assert css_file.stat().st_size > 100, "css/style.css is too small"

    def test_css_has_root_variables(self, css_file):
        """CSS must define :root with custom properties (Twenty Nineteen style)."""
        content = css_file.read_text()
        assert ":root" in content, "CSS missing :root block"
        for var in ["--bg", "--text", "--accent", "--border"]:
            assert var in content, f"CSS missing variable {var}"

    def test_css_has_key_selectors(self, css_file):
        """CSS must contain key Twenty Nineteen theme selectors."""
        content = css_file.read_text()
        for selector in [
            ".site-header",
            ".main-nav",
            ".hero",
            ".content-wrapper",
            ".site-footer",
            ".breadcrumbs",
            ".page-content",
        ]:
            assert selector in content, f"CSS missing selector {selector}"

    def test_css_has_font_families(self, css_file):
        """CSS must define serif and sans-serif font stacks."""
        content = css_file.read_text()
        assert "--fh" in content, "CSS missing heading font variable --fh"
        assert "--fb" in content, "CSS missing body font variable --fb"
        assert "serif" in content, "CSS missing serif font family"
        assert "sans-serif" in content, "CSS missing sans-serif fallback"


# ---------------------------------------------------------------------------
# <img> validation
# ---------------------------------------------------------------------------

class TestImages:
    def test_no_empty_img_src(self, parsed_pages):
        """No <img> tag should have an empty src attribute."""
        failures = []
        for path, _, soup in parsed_pages:
            for img in soup.find_all("img"):
                src = img.get("src", None)
                if src is not None and not src.strip():
                    failures.append(str(path.relative_to(SITE_ROOT)))
                    break
        assert not failures, f"Pages with empty <img src>: {failures}"


# ---------------------------------------------------------------------------
# <iframe> validation
# ---------------------------------------------------------------------------

class TestIframes:
    def test_no_empty_iframes(self, parsed_pages):
        """No <iframe> should have an empty or blob: src."""
        failures = []
        for path, _, soup in parsed_pages:
            for iframe in soup.find_all("iframe"):
                src = iframe.get("src", "")
                if not src.strip() or src.strip().startswith("blob:"):
                    failures.append(str(path.relative_to(SITE_ROOT)))
                    break
        assert not failures, f"Pages with empty or blob: <iframe src>: {failures}"


# ---------------------------------------------------------------------------
# Placeholder notices
# ---------------------------------------------------------------------------

class TestPlaceholderNotices:
    def test_no_placeholder_notices(self, parsed_pages):
        """No page should contain the placeholder-notice class (all placeholders should be resolved)."""
        failures = []
        for path, _, soup in parsed_pages:
            if soup.select_one(".placeholder-notice"):
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"Pages still containing .placeholder-notice: {failures}"


# ---------------------------------------------------------------------------
# Editor attributes
# ---------------------------------------------------------------------------

class TestEditorAttributes:
    def test_no_editor_attributes(self, parsed_pages):
        """No page should have data-wp-block-attribute-key attributes (leftover editor metadata)."""
        failures = []
        for path, _, soup in parsed_pages:
            if soup.find(attrs={"data-wp-block-attribute-key": True}):
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"Pages with data-wp-block-attribute-key attributes: {failures}"
