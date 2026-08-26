#!/usr/bin/env python3
"""Build self-contained per-semester archive sites under archive/{YYYYsem}/.

Source of truth: dev/data/site-export_sanitized_20260825.xml (full WordPress
WXR export). Membership per semester = BFS over internal links from that
semester's root pages (readings/syllabus/topics hubs), unioned with
slug/title-classified pages. The current semester (2025fall) additionally
includes every page modified since 2025-06-01.

Each archive page is rendered with the site theme (white header variant,
or featured image when known), with internal links rewritten to stay inside
the archive (falling back to the main site at ../../, then to absolute URLs).

Outputs:
- archive/{sem}/index.html + {slug}.html pages
- dev/data/archive-manifest.json  (membership, link map, orphans, external
  images still needed)

Run:  uv run --with beautifulsoup4 python dev/scripts/build_archives.py
"""

import html as htmllib
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPORT = ROOT / "dev" / "data" / "site-export_sanitized_20260825.xml"
NS = {"wp": "http://wordpress.org/export/1.2/",
      "content": "http://purl.org/rss/1.0/modules/content/",
      "dc": "http://purl.org/dc/elements/1.1/"}

SEM_LABEL = {
    "2019spring": "Spring 2019", "2020spring": "Spring 2020",
    "2020fall": "Fall 2020", "2021spring": "2021", "2021fall": "Fall 2021",
    "2022spring": "Spring 2022", "2022fall": "Fall 2022",
    "2025fall": "Fall 2025",
}

# semester -> root slugs (readings hub first: it becomes index.html)
ROOTS = {
    "2019spring": ["topics-2019", "syllabus-2019-spring", "readings"],
    "2020spring": ["readings-2020-spring"],
    "2020fall": ["readings-fall-2020"],
    "2021spring": ["readings-2021", "syllabus-2021"],
    "2022spring": ["readings-2022", "syllabus-2022", "readings-3"],
    "2025fall": ["readings-2", "syllabus"],
}

CDN_PREFIXES = (
    "https://programminghumanity.wordpress.com/wp-content/uploads/",
    "https://programminghumanity.files.wordpress.com/",
)


def load_items():
    tree = ET.parse(EXPORT)
    items = {}
    for it in tree.getroot().findall(".//item"):
        ptype = it.findtext("wp:post_type", "", NS)
        if ptype not in ("page", "post"):
            continue
        slug = it.findtext("wp:post_name", "", NS)
        if not slug:
            continue
        thumb = None
        for m in it.findall("wp:postmeta", NS):
            if m.findtext("wp:meta_key", "", NS) == "_thumbnail_id":
                thumb = m.findtext("wp:meta_value", "", NS)
        items[slug] = {
            "slug": slug, "type": ptype,
            "title": it.findtext("title", "") or slug,
            "status": it.findtext("wp:status", "", NS),
            "created": it.findtext("wp:post_date", "", NS),
            "modified": it.findtext("wp:post_modified", "", NS),
            "content": it.findtext("content:encoded", "", NS) or "",
            "thumb_id": thumb,
        }
    # attachment id -> url (for featured images)
    atts = {}
    for it in tree.getroot().findall(".//item"):
        if it.findtext("wp:post_type", "", NS) == "attachment":
            atts[it.findtext("wp:post_id", "", NS)] = it.findtext("wp:attachment_url", "", NS)
    for e in items.values():
        e["featured"] = atts.get(e["thumb_id"])
    return items


def classify(e):
    t, s = e["title"], e["slug"]
    if e["type"] == "post":
        return "blog"
    m = (re.search(r"(?:^|-)(spring|fall|spr)-?(20\d\d)(?:$|-)", s)
         or re.search(r"(?:^|-)(20\d\d)-(spring|fall|spr)(?:$|-)", s))
    if m:
        g = m.groups()
        yr = g[0] if g[0].startswith("20") else g[1]
        se = g[1] if g[0].startswith("20") else g[0]
        return yr + {"spr": "spring"}.get(se, se)
    m = (re.search(r"\(?(Spring|Fall)\s*(20\d\d)\)?", t, re.I)
         or re.search(r"\(?(20\d\d)\s*(Spring|Fall)\)?", t, re.I))
    if m:
        g = m.groups()
        yr = g[0] if g[0].startswith("20") else g[1]
        se = (g[1] if g[0].startswith("20") else g[0]).lower()
        return yr + se
    m = re.search(r"\((20\d\d)\)", t) or re.search(r"-(20\d\d)(?:$|-)", s)
    if m:
        return {"2019": "2019spring", "2021": "2021spring", "2022": "2022spring",
                "2025": "2025fall"}.get(m.group(1))
    return None


def internal_links(content):
    out = []
    for m in re.finditer(r'href="https?://programminghumanity\.wordpress\.com/([^"#?]*)"', content):
        path = m.group(1).rstrip("/")
        if not path or path.startswith(("wp-content", "wp-admin", "wp-login")):
            continue
        out.append(path.split("/")[-1])
    return out


def wpautop(text):
    """Minimal classic-editor paragraph conversion."""
    if "<!-- wp:" in text or "<p>" in text[:2000]:
        return text
    blocks = re.split(r"\n\s*\n", text)
    out = []
    blocklevel = re.compile(r"^\s*<(h[1-6]|ul|ol|li|div|figure|blockquote|table|pre|p|iframe|hr|img|section)", re.I)
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if blocklevel.match(b):
            out.append(b)
        else:
            out.append("<p>" + b.replace("\n", "<br/>\n") + "</p>")
    return "\n".join(out)


def build_membership(items):
    classified = defaultdict(set)
    for s, e in items.items():
        c = classify(e)
        if c and c in SEM_LABEL:
            classified[c].add(s)
    members, linkmap = {}, {}
    for sem, roots in ROOTS.items():
        seen, edges, queue = set(), {}, [r for r in roots if r in items]
        while queue:
            cur = queue.pop(0)
            if cur in seen:
                continue
            seen.add(cur)
            outs = [t for t in internal_links(items[cur]["content"])
                    if t in items and items[t]["type"] == "page"]
            edges[cur] = outs
            queue.extend(t for t in outs if t not in seen)
        seen |= classified.get(sem, set())
        if sem == "2025fall":
            seen |= {s for s, e in items.items()
                     if e["type"] == "page" and e["modified"] >= "2025-06-01"
                     and s not in ("about", "contact", "faculty", "home", "blog", "papers")}
        members[sem] = sorted(seen)
        linkmap[sem] = edges
    return members, linkmap


def repo_path_for(slug):
    """Existing main-site file for a slug, repo-relative, if any."""
    hits = [p for p in ROOT.glob(f"*/{slug}.html")
            if p.parts[len(ROOT.parts)] not in ("tests", "tmp", "dev", "archive", "website")]
    return str(hits[0].relative_to(ROOT)) if hits else None


PAGE_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width,initial-scale=1.0" name="viewport"/>
<title>{title} – Programming Humanity {label} Archive</title>
<link href="../../css/style.css" rel="stylesheet"/>
</head>
<body>
<header class="site-header {variant}">
{media}<div class="header-inner">
<div class="site-branding"><p class="site-title"><a href="index.html">Programming Humanity</a></p><span class="site-sep">—</span><p class="site-description">{label} Archive</p></div>
<nav class="main-nav"><ul>
<li><a href="{syllabus_href}">Syllabus</a></li>
<li><a href="index.html">Readings</a></li>
<li><a href="../../index.html">Current Site</a></li>
</ul></nav>
<div class="social-nav"><a href="https://twitter.com/ai4dhumanities" rel="noopener" target="_blank">Twitter</a></div>
</div>
<section class="hero"><h1>{title}</h1></section>
</header>
<main class="content-wrapper">
<div class="breadcrumbs"><a href="../../index.html">Home</a> » <a href="index.html">{label} Archive</a> » <span>{title}</span></div>
<div class="page-meta">Created: {created} • Modified: {modified} • Archived from programminghumanity.wordpress.com</div>
<div class="page-content">
{body}
</div>
</main>
<footer class="site-footer">
<p>Programming Humanity — {label} Archive</p>
</footer>
</body>
</html>
"""


def rewrite_links(content, sem, members, missing_imgs):
    # author-only edit/admin links: unwrap the anchor, keep its text
    content = re.sub(
        r'<a\s[^>]*href="https?://programminghumanity\.wordpress\.com/wp-(?:admin|login)[^"]*"[^>]*>(.*?)</a>',
        r"\1", content, flags=re.S)

    def repl_href(m):
        url, raw = m.group(0), m.group(1)
        # split off query (dropped) and fragment (kept)
        frag = ""
        if "#" in raw:
            raw, frag = raw.split("#", 1)
            frag = "#" + frag
        path = raw.split("?")[0].rstrip("/")
        if not path:
            return f'href="index.html{frag}"'
        if re.match(r"20\d\d/\d\d/\d\d/", path):
            slug = path.split("/")[-1]
            if (ROOT / "blog" / f"{slug}.html").is_file():
                return f'href="../../blog/{slug}.html{frag}"'
            return url
        slug = path.split("/")[-1]
        if slug in members[sem]:
            return f'href="{slug}.html{frag}"'
        rp = repo_path_for(slug)
        if rp:
            return f'href="../../{rp}{frag}"'
        return url
    content = re.sub(r'href="https?://programminghumanity\.wordpress\.com/([^"]*)"', repl_href, content)

    def repl_img(m):
        url = m.group(1)
        clean = url.split("?")[0]
        for pre in CDN_PREFIXES:
            if clean.startswith(pre):
                rel = "images/uploads/" + clean[len(pre):]
                if (ROOT / rel).is_file():
                    return f'src="../../{rel}"'
                missing_imgs.add(clean)
                return f'src="../../{rel}"'
        return m.group(0)
    content = re.sub(r'src="(https?://[^"]+)"', repl_img, content)
    content = re.sub(r'\s(?:srcset|sizes)="[^"]*"', "", content)
    return content


def main():
    items = load_items()
    members, linkmap = build_membership(items)
    missing_imgs = set()
    manifest = {"semesters": {}, "missing_images": []}

    for sem, slugs in members.items():
        label = SEM_LABEL[sem]
        outdir = ROOT / "archive" / sem
        outdir.mkdir(parents=True, exist_ok=True)
        syllabus_slug = next((s for s in slugs if s.startswith("syllabus")), None)
        readings_root = ROOTS[sem][0]

        for slug in slugs:
            e = items[slug]
            body = rewrite_links(wpautop(e["content"]), sem, members, missing_imgs)
            feat = e.get("featured")
            variant, media = "no-featured-image", ""
            if feat:
                clean = feat.split("?")[0]
                for pre in CDN_PREFIXES:
                    if clean.startswith(pre):
                        rel = "images/uploads/" + clean[len(pre):]
                        if (ROOT / rel).is_file():
                            variant = "has-featured-image"
                            media = f'<div aria-hidden="true" class="featured-media"><img alt="" src="../../{rel}"/></div>\n'
                        break
            page = PAGE_TMPL.format(
                title=htmllib.escape(e["title"]), label=label, variant=variant,
                media=media, body=body,
                syllabus_href=f"{syllabus_slug}.html" if syllabus_slug else "../../core/syllabus.html",
                created=e["created"][:10], modified=e["modified"][:10])
            (outdir / f"{slug}.html").write_text(page, encoding="utf-8")

        # index.html: readings root content + full member listing
        e = items[readings_root]
        body = rewrite_links(wpautop(e["content"]), sem, members, missing_imgs)
        reached = set(linkmap[sem])
        for outs in linkmap[sem].values():
            reached.update(outs)
        orphans = [s for s in slugs if s not in reached]
        listing = ['<div class="section"><h2>All pages in this archive</h2><ul class="item-list">']
        for s in slugs:
            note = "" if s in reached else ' <span class="badge badge-draft">unlinked</span>'
            listing.append(f'<li><a href="{s}.html">{htmllib.escape(items[s]["title"])}</a>{note}</li>')
        listing.append("</ul></div>")
        body += "\n" + "\n".join(listing)
        page = PAGE_TMPL.format(
            title=htmllib.escape(f"Programming Humanity — {label}"), label=label,
            variant="no-featured-image", media="", body=body,
            syllabus_href=f"{syllabus_slug}.html" if syllabus_slug else "../../core/syllabus.html",
            created=e["created"][:10], modified=e["modified"][:10])
        (outdir / "index.html").write_text(page, encoding="utf-8")

        manifest["semesters"][sem] = {
            "label": label, "roots": ROOTS[sem], "pages": slugs,
            "link_map": linkmap[sem], "orphans": orphans,
        }
        print(f"{sem}: {len(slugs)} pages, {len(orphans)} unlinked")

    manifest["missing_images"] = sorted(missing_imgs)
    (ROOT / "dev" / "data" / "archive-manifest.json").write_text(json.dumps(manifest, indent=1))
    print("missing images to download:", len(missing_imgs))


if __name__ == "__main__":
    main()
