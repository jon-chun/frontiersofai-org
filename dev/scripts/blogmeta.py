#!/usr/bin/env python3
"""Add live-site blog furniture to the static site.

Using dev/data/wxr-meta.json (from the WordPress export):
- blog posts get an `.entry-meta` row (author + date), an `.entry-footer`
  ("Posted in <categories>"), and prev/next `.post-nav` links across the
  published-post chronology
- every page/post that exists on the live site gets a `.share-links` row
  (X + Facebook share intents pointing at the live URL)
- blog/index.html is rebuilt in the live style: title + date + excerpt,
  newest first

Idempotent: skips elements that already exist.
Run:  uv run python dev/scripts/blogmeta.py
"""

import json
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / "dev" / "data" / "wxr-meta.json").read_text())
FMAP = json.loads((ROOT / "dev" / "data" / "featured-images.json").read_text())
SKIP_DIRS = {"tests", "tmp", "dev", ".git", ".vscode"}

published_posts = sorted(
    (s for s, e in META.items() if e["type"] == "post" and e["status"] == "publish"),
    key=lambda s: META[s]["date"],
)


def nice_date(raw: str) -> str:
    return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").strftime("%B %-d, %Y")


def add_post_furniture(path: Path, soup: BeautifulSoup, slug: str) -> bool:
    e = META[slug]
    changed = False
    content = soup.find(class_="page-content")
    wrapper = soup.find(class_="content-wrapper")
    if content is None or wrapper is None:
        return False

    if soup.find(class_="entry-meta") is None:
        meta = soup.new_tag("div", attrs={"class": "entry-meta"})
        by = soup.new_tag("span")
        by.string = f"Posted by {e['author'] or 'jonchun'}"
        when = soup.new_tag("span")
        when.string = nice_date(e["date"])
        meta.append(by)
        meta.append(when)
        content.insert(0, meta)
        changed = True

    if soup.find(class_="entry-footer") is None:
        foot = soup.new_tag("div", attrs={"class": "entry-footer"})
        cats = ", ".join(e["categories"]) or "Uncategorized"
        foot.string = f"Posted by {e['author'] or 'jonchun'} • {nice_date(e['date'])} • Posted in {cats}"
        content.append(foot)
        changed = True

    if soup.find(class_="post-nav") is None and slug in published_posts:
        i = published_posts.index(slug)
        nav = soup.new_tag("nav", attrs={"class": "post-nav"})
        for label, j in (("Previous post", i - 1), ("Next post", i + 1)):
            if 0 <= j < len(published_posts):
                other = published_posts[j]
                if (ROOT / "blog" / f"{other}.html").is_file():
                    d = soup.new_tag("div")
                    small = soup.new_tag("span")
                    small.string = label + ": "
                    a = soup.new_tag("a", href=f"{other}.html")
                    a.string = META[other]["title"]
                    d.append(small)
                    d.append(a)
                    nav.append(d)
        if nav.contents:
            wrapper.append(nav)
            changed = True
    return changed


def add_share_links(soup: BeautifulSoup, slug: str) -> bool:
    if soup.find(class_="share-links") is not None:
        return False
    entry = FMAP.get(slug)
    if not entry:
        return False
    content = soup.find(class_="page-content")
    if content is None:
        return False
    url = quote(entry["url"], safe="")
    div = soup.new_tag("div", attrs={"class": "share-links"})
    label = soup.new_tag("span")
    label.string = "Share this: "
    x = soup.new_tag("a", href=f"https://twitter.com/intent/tweet?url={url}",
                     target="_blank", rel="noopener")
    x.string = "X"
    fb = soup.new_tag("a", href=f"https://www.facebook.com/sharer/sharer.php?u={url}",
                      target="_blank", rel="noopener")
    fb.string = "Facebook"
    div.append(label)
    div.append(x)
    div.append(fb)
    content.append(div)
    return True


def rebuild_blog_index() -> None:
    path = ROOT / "blog" / "index.html"
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    content = soup.find(class_="page-content")
    if content is None:
        return
    listing = soup.new_tag("div", attrs={"class": "post-list"})
    for slug in reversed(published_posts):
        if not (ROOT / "blog" / f"{slug}.html").is_file():
            continue
        e = META[slug]
        art = soup.new_tag("article", attrs={"class": "post-preview"})
        h2 = soup.new_tag("h2")
        a = soup.new_tag("a", href=f"{slug}.html")
        a.string = e["title"]
        h2.append(a)
        meta = soup.new_tag("div", attrs={"class": "entry-meta"})
        when = soup.new_tag("span")
        when.string = nice_date(e["date"])
        meta.append(when)
        p = soup.new_tag("p")
        p.string = e["excerpt"]
        art.append(h2)
        art.append(meta)
        art.append(p)
        listing.append(art)
    # replace the flat item list with the live-style previews; keep other
    # sections (e.g. links to non-post pages) untouched below the listing
    old = content.find("div", class_="post-list")
    if old is not None:
        old.replace_with(listing)
    else:
        first_list = content.find("ul", class_="item-list")
        if first_list is not None:
            section = first_list.find_parent("div", class_="section") or first_list
            section.insert_before(listing)
            section["class"] = (section.get("class") or []) + ["other-blog-pages"]
        else:
            content.append(listing)
    path.write_text(str(soup), encoding="utf-8")


def main() -> None:
    stats = {"post-furniture": 0, "share": 0}
    for path in sorted(ROOT.rglob("*.html")):
        parts = path.relative_to(ROOT).parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        if path.name == "index.html":
            continue
        slug = path.stem
        is_blog_post = parts[0] == "blog" and slug in META and META[slug]["type"] == "post"
        if not is_blog_post and slug not in FMAP:
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        changed = False
        if is_blog_post:
            changed |= add_post_furniture(path, soup, slug)
            if changed:
                stats["post-furniture"] += 1
        if add_share_links(soup, slug):
            changed = True
            stats["share"] += 1
        if changed:
            path.write_text(str(soup), encoding="utf-8")
    rebuild_blog_index()
    print("done:", stats, "| blog index rebuilt with", len(published_posts), "post previews")


if __name__ == "__main__":
    main()
