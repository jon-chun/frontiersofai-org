#!/usr/bin/env python3
"""Re-theme all site pages to the Twenty Nineteen-faithful header structure.

For every page:
- classify the header as `has-featured-image` (slug found in
  dev/data/featured-images.json with a featured image) or `no-featured-image`
- insert a `.featured-media` duotone image layer (local mirror under
  images/uploads/) for image pages
- restructure branding to the one-line "Site Title — Tagline" pattern
- move `section.hero` (entry title) inside the header

Idempotent: pages whose header already carries a variant class are skipped.
Run:  uv run python dev/scripts/retheme.py [--dry-run]
"""

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "dev" / "data" / "featured-images.json"
SKIP_DIRS = {"tests", "tmp", "dev", ".git", ".vscode"}
CDN_PREFIX = "https://programminghumanity.wordpress.com/wp-content/uploads/"

SITE_TITLE = "Programming Humanity"
TAGLINE = "Computational Thinking for Humanity"


def local_image(url: str) -> str | None:
    """CDN upload URL -> repo-relative path under images/uploads/, if mirrored."""
    if not url or not url.startswith(CDN_PREFIX):
        return None
    rel = "images/uploads/" + url[len(CDN_PREFIX):].split("?")[0]
    return rel if (ROOT / rel).is_file() else None


def transform(path: Path, fmap: dict) -> str:
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    header = soup.find("header", class_="site-header")
    hero = soup.find("section", class_="hero")
    if header is None or hero is None:
        return "no-header-or-hero"
    classes = header.get("class", [])
    if "has-featured-image" in classes or "no-featured-image" in classes:
        return "already-done"

    rel = path.relative_to(ROOT)
    depth = len(rel.parts) - 1
    prefix = "../" * depth

    # Which featured image (if any)?
    slug = "home" if (depth == 0 and path.name == "index.html") else path.stem
    entry = None if path.name == "index.html" and depth > 0 else fmap.get(slug)
    img_rel = local_image(entry["featured_image"]) if entry and entry.get("featured_image") else None

    # 1. Variant class
    header["class"] = ["site-header", "has-featured-image" if img_rel else "no-featured-image"]

    # 2. Featured media layer
    if img_rel:
        media = soup.new_tag("div", attrs={"class": "featured-media", "aria-hidden": "true"})
        img = soup.new_tag("img", src=prefix + img_rel, alt="")
        media.append(img)
        header.insert(0, media)

    # 3. Branding: one-line title — tagline
    old_title = header.find(class_="site-title")
    if old_title is not None:
        link = old_title.find("a")
        href = link["href"] if link and link.has_attr("href") else prefix + "index.html"
        branding = soup.new_tag("div", attrs={"class": "site-branding"})
        p_title = soup.new_tag("p", attrs={"class": "site-title"})
        a = soup.new_tag("a", href=href)
        a.string = SITE_TITLE
        p_title.append(a)
        sep = soup.new_tag("span", attrs={"class": "site-sep"})
        sep.string = "—"
        p_desc = soup.new_tag("p", attrs={"class": "site-description"})
        p_desc.string = TAGLINE
        branding.append(p_title)
        branding.append(sep)
        branding.append(p_desc)
        old_title.replace_with(branding)

    # 4. Move the hero (entry title) inside the header
    hero.extract()
    header.append(hero)

    path.write_text(str(soup), encoding="utf-8")
    return "with-image" if img_rel else "white"


def main() -> None:
    dry = "--dry-run" in sys.argv
    fmap = json.loads(MAP_PATH.read_text())
    stats: dict[str, int] = {}
    problems = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if dry:
            continue
        result = transform(path, fmap)
        stats[result] = stats.get(result, 0) + 1
        if result == "no-header-or-hero":
            problems.append(str(path.relative_to(ROOT)))
    print("results:", stats)
    if problems:
        print("pages skipped (missing header/hero):")
        for p in problems:
            print("  ", p)


if __name__ == "__main__":
    main()
