"""End-to-end tests: site completeness, consistency, and structure."""
import pytest
from bs4 import BeautifulSoup
from pathlib import Path

SITE_ROOT = Path(__file__).parent.parent

# archive/ (per-semester frozen sites) and website/ (standalone Fall 2026
# deploy) are separate sites by design: different nav, titles, no breadcrumbs.
STANDALONE_DIRS = {"archive", "website"}


def in_standalone(f):
    return f.relative_to(SITE_ROOT).parts[0] in STANDALONE_DIRS


# ---------------------------------------------------------------------------
# Required files and directories
# ---------------------------------------------------------------------------

class TestRequiredFiles:
    @pytest.mark.parametrize("filename", [
        "index.html",
        "404.html",
        "archive.html",
        "css/style.css",
    ])
    def test_required_root_files_exist(self, site_root, filename):
        """Key root-level files must exist."""
        assert (site_root / filename).exists(), f"Missing required file: {filename}"

    @pytest.mark.parametrize("dirname", [
        "css",
        "core",
        "tests",
    ])
    def test_required_directories_exist(self, site_root, dirname):
        """Key directories must exist."""
        assert (site_root / dirname).is_dir(), f"Missing required directory: {dirname}"


# ---------------------------------------------------------------------------
# Semester folders
# ---------------------------------------------------------------------------

SEMESTER_FOLDERS = [
    "2018-2019",
    "2019-fall",
    "2020",
    "2020-fall",
    "2020-spring",
    "2021",
    "2022-spring",
    "2023",
    "2025-spring",
    "2026-spring",
]


class TestSemesterFolders:
    @pytest.mark.parametrize("folder", SEMESTER_FOLDERS)
    def test_semester_folder_exists(self, site_root, folder):
        """Each semester folder must exist."""
        assert (site_root / folder).is_dir(), f"Missing semester folder: {folder}"

    @pytest.mark.parametrize("folder", SEMESTER_FOLDERS)
    def test_semester_folder_has_content(self, site_root, folder):
        """Each semester folder must contain at least 2 HTML files."""
        d = site_root / folder
        if not d.is_dir():
            pytest.skip(f"{folder} does not exist")
        html_count = len(list(d.glob("*.html")))
        assert html_count >= 2, (
            f"{folder} has only {html_count} HTML file(s), expected >= 2"
        )


# ---------------------------------------------------------------------------
# Page count
# ---------------------------------------------------------------------------

class TestPageCount:
    def test_minimum_total_pages(self, all_html_files):
        """Site must have at least 200 HTML pages."""
        count = len(all_html_files)
        assert count >= 200, f"Only {count} HTML files found, expected >= 200"


# ---------------------------------------------------------------------------
# Target file coverage
# ---------------------------------------------------------------------------

TARGET_FILES = {
    "2018-2019": [
        "assignments", "course-schedule", "exercises", "nlp-tools",
        "posters-fall-2019", "posters-spring-2019", "posters",
        "quantitative-reasoning", "sample-exercises", "syllabus", "topics",
    ],
    "2019-fall": [
        "ai-evolution-and-neuroscience", "ai-topics-fall-2019",
        "building-brains-ai-2019", "composing-ai-2019",
    ],
    "2021": [
        "0-readings-2021", "introduction-to-ai-2021",
        "building-brains-with-artificial-neurons",
    ],
    "2022-spring": [
        "introduction-to-ai-spr-2022", "machine-learning-introduction-2022",
    ],
    "2026-spring": [
        "syllabus-2", "building-brains-with-artificial-neurons-spring-2026",
    ],
    "core": ["contact", "faculty", "about", "syllabus"],
    "topics": ["topic-artificial-intelligence", "topic-data"],
    "labs": ["lab-data", "lab-nlp"],
}


class TestTargetCoverage:
    @pytest.mark.parametrize(
        "folder,stem",
        [
            (folder, stem)
            for folder, stems in TARGET_FILES.items()
            for stem in stems
        ],
        ids=lambda val: val if isinstance(val, str) else "",
    )
    def test_target_file_exists(self, site_root, folder, stem):
        """Key content files must exist."""
        path = site_root / folder / f"{stem}.html"
        assert path.exists(), f"Missing target file: {folder}/{stem}.html"


# ---------------------------------------------------------------------------
# Consistent nav structure
# ---------------------------------------------------------------------------

class TestConsistentNav:
    def test_all_subfolder_pages_have_same_nav_labels(
        self, site_root, subfolder_html_files
    ):
        """All subfolder pages must share the same set of nav link labels."""
        expected = {"Syllabus", "Readings", "About"}
        failures = []
        for f in subfolder_html_files:
            if in_standalone(f):
                continue
            soup = BeautifulSoup(f.read_text(), "lxml")
            nav = soup.select_one("nav.main-nav")
            if not nav:
                failures.append(f"{f.relative_to(site_root)}: missing nav")
                continue
            labels = {a.get_text(strip=True) for a in nav.find_all("a")}
            if labels != expected:
                failures.append(
                    f"{f.relative_to(site_root)}: {sorted(labels)}"
                )
        assert not failures, (
            f"Pages with inconsistent nav: {failures[:15]}"
        )


# ---------------------------------------------------------------------------
# Consistent footer structure
# ---------------------------------------------------------------------------

class TestConsistentFooter:
    def test_all_pages_have_footer_with_text(self, parsed_pages):
        """Every page footer must contain 'Programming Humanity'."""
        failures = []
        for path, _, soup in parsed_pages:
            footer = soup.find("footer")
            if not footer:
                failures.append(f"{path.relative_to(SITE_ROOT)}: no footer")
                continue
            if "Programming Humanity" not in footer.get_text():
                failures.append(
                    f"{path.relative_to(SITE_ROOT)}: footer text mismatch"
                )
        assert not failures, f"Footer issues: {failures[:15]}"


# ---------------------------------------------------------------------------
# Hero section
# ---------------------------------------------------------------------------

class TestHeroSection:
    def test_all_pages_have_hero_with_h1(self, parsed_pages):
        """Every page must have a .hero section containing an <h1>."""
        failures = []
        for path, _, soup in parsed_pages:
            hero = soup.select_one("section.hero")
            if not hero:
                failures.append(f"{path.relative_to(SITE_ROOT)}: missing .hero")
                continue
            if not hero.find("h1"):
                failures.append(f"{path.relative_to(SITE_ROOT)}: .hero has no h1")
        assert not failures, f"Hero section issues: {failures[:15]}"


# ---------------------------------------------------------------------------
# Breadcrumbs on subfolder pages
# ---------------------------------------------------------------------------

class TestBreadcrumbs:
    def test_subfolder_non_index_pages_have_breadcrumbs(
        self, site_root, subfolder_non_index_files
    ):
        """Non-index pages inside subfolders should have .breadcrumbs."""
        failures = []
        for f in subfolder_non_index_files:
            if in_standalone(f):
                continue
            soup = BeautifulSoup(f.read_text(), "lxml")
            if not soup.select_one(".breadcrumbs"):
                failures.append(str(f.relative_to(site_root)))
        assert not failures, (
            f"Subfolder pages missing breadcrumbs: {failures[:15]}"
        )


# ---------------------------------------------------------------------------
# Empty content detection
# ---------------------------------------------------------------------------

class TestContentNotEmpty:
    def test_no_pages_with_empty_content(self, parsed_pages):
        """No page's .page-content div should have fewer than 20 characters of text."""
        failures = []
        for path, _, soup in parsed_pages:
            content_div = soup.select_one(".page-content")
            if not content_div:
                continue
            text = content_div.get_text(strip=True)
            if len(text) < 20:
                failures.append(
                    f"{path.relative_to(SITE_ROOT)}: only {len(text)} chars"
                )
        assert not failures, (
            f"Pages with near-empty .page-content: {failures[:20]}"
        )
