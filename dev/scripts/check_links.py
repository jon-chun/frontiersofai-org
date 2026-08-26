#!/usr/bin/env python3
"""Check internal links and image references across the static site.

Scans every *.html under the given directories (default: whole site) and
verifies that relative href/src targets resolve to files on disk. Absolute
http(s) links are listed separately (not fetched) unless they point at
programminghumanity.wordpress.com, which are flagged as leftovers.

Run:  uv run --with beautifulsoup4 python dev/scripts/check_links.py [dir ...]
"""

import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SKIP = {"tests", "tmp", "dev", ".git", ".vscode"}


def check(dirs):
    broken, wp_leftover = [], []
    pages = []
    for d in dirs:
        pages.extend(sorted((ROOT / d).rglob("*.html")))
    for p in pages:
        if any(x in SKIP for x in p.relative_to(ROOT).parts):
            continue
        soup = BeautifulSoup(p.read_text(encoding="utf-8"), "html.parser")
        refs = [(a.get("href") or "") for a in soup.find_all("a")]
        refs += [(i.get("src") or "") for i in soup.find_all("img")]
        refs += [(l.get("href") or "") for l in soup.find_all("link")]
        for r in refs:
            if not r or r.startswith(("#", "mailto:", "javascript:")):
                continue
            u = urlparse(r)
            if u.scheme in ("http", "https"):
                if "programminghumanity.wordpress.com" in u.netloc and "/wp-content/" not in u.path:
                    wp_leftover.append((str(p.relative_to(ROOT)), r))
                continue
            target = (p.parent / unquote(u.path)).resolve()
            if u.path and not target.exists():
                broken.append((str(p.relative_to(ROOT)), r))
    return broken, wp_leftover


def main():
    dirs = sys.argv[1:] or ["."]
    broken, wp = check(dirs)
    print(f"broken internal refs: {len(broken)}")
    for pg, r in broken[:60]:
        print(f"  {pg}: {r}")
    print(f"links still pointing at live WP site: {len(wp)}")
    for pg, r in wp[:40]:
        print(f"  {pg}: {r}")
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
