import pytest
from pathlib import Path
from bs4 import BeautifulSoup

SITE_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def site_root():
    return SITE_ROOT


@pytest.fixture(scope="session")
def css_file(site_root):
    return site_root / "css" / "style.css"


@pytest.fixture(scope="session")
def all_html_files(site_root):
    """All HTML files in the project, excluding tests/."""
    return sorted(
        f for f in site_root.rglob("*.html")
        if "tests" not in f.relative_to(site_root).parts
        and ".vscode" not in f.relative_to(site_root).parts
    )


@pytest.fixture(scope="session")
def parsed_pages(all_html_files):
    """Pre-parsed (path, soup) pairs for every HTML page."""
    pages = []
    for f in all_html_files:
        text = f.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(text, "lxml")
        pages.append((f, text, soup))
    return pages


@pytest.fixture(scope="session")
def subfolder_html_files(site_root, all_html_files):
    """HTML files that live inside a subdirectory (not at root level)."""
    return [f for f in all_html_files if f.parent != site_root]


@pytest.fixture(scope="session")
def subfolder_non_index_files(subfolder_html_files):
    """Subfolder HTML files that are NOT index.html."""
    return [f for f in subfolder_html_files if f.name != "index.html"]


@pytest.fixture(scope="session")
def folder_index_files(site_root, all_html_files):
    """All index.html files inside subdirectories."""
    return [
        f for f in all_html_files
        if f.name == "index.html" and f.parent != site_root
    ]
