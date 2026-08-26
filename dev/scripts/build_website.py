#!/usr/bin/env python3
"""Build the standalone Fall 2026 live site in website/.

Page set: the most recent version of each course topic (variants deduped by
theme, latest wp:post_modified wins), plus syllabus, readings (homepage),
about, and anything they link (BFS closure over WXR pages). Year/semester
labels are rewritten to Fall 2026. The output is fully self-contained
(own css/ and images/) so website/ can be deployed alone to Netlify.

Run:  uv run --with beautifulsoup4 python dev/scripts/build_website.py
"""

import html as htmllib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "website"
EXPORT = ROOT / "dev" / "data" / "site-export_sanitized_20260825.xml"
NS = {"wp": "http://wordpress.org/export/1.2/",
      "content": "http://purl.org/rss/1.0/modules/content/"}
CDN_PREFIXES = (
    "https://programminghumanity.wordpress.com/wp-content/uploads/",
    "https://programminghumanity.files.wordpress.com/",
)
SEM = "Fall 2026"
CUTOFF = "2025-06-01"          # pages touched after this are "current"
SUFFIX = re.compile(r"(-(?:2019|2020|2021|2022|2023|2025|2026|spring|fall|spr|\d))+$")

# readings outline item (keyword) -> topic theme slug
OUTLINE_LINKS = [
    (r"^Data\b", "topic-data"),
    (r"^Processing", "topic-the-brain-and-computers-cognition-and-consciousness"),
    (r"^Output", "topic-visualizations"),
    (r"^Networks", "topic-networks"),
    (r"^Languages", "topic-programming"),
    (r"^Ro/?bots", "topic-ro-bots"),
    (r"^Quantifying", "topic-probability"),
    (r"^Databases", "topic-databases"),
    (r"^Natural Language", "topic-nlp"),
    (r"^Models", "topic-models"),
    (r"^Simulations", "topic-simulations"),
    (r"^Evolving Life", "topic-bioinformatics"),
    (r"^\s*Social Networks", "topic-social-networks"),
    (r"^Artificial Intelligence", "topic-artificial-intelligence"),
]


def load_items():
    tree = ET.parse(EXPORT)
    items, atts = {}, {}
    for it in tree.getroot().findall(".//item"):
        ptype = it.findtext("wp:post_type", "", NS)
        if ptype == "attachment":
            atts[it.findtext("wp:post_id", "", NS)] = it.findtext("wp:attachment_url", "", NS)
            continue
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
            "modified": it.findtext("wp:post_modified", "", NS),
            "created": it.findtext("wp:post_date", "", NS),
            "content": it.findtext("content:encoded", "", NS) or "",
            "thumb_id": thumb,
        }
    for e in items.values():
        e["featured"] = atts.get(e["thumb_id"])
    return items


def theme_of(slug):
    return SUFFIX.sub("", slug)


def pick_current(items):
    """theme -> winning slug (latest modified among current topic pages)."""
    cands = defaultdict(list)
    for s, e in items.items():
        if e["type"] != "page" or not s.startswith("topic-"):
            continue
        if e["modified"] >= CUTOFF:
            cands[theme_of(s)].append(s)
    return {t: max(ss, key=lambda s: items[s]["modified"]) for t, ss in cands.items()}


def wpautop(text):
    if "<!-- wp:" in text or "<p>" in text[:2000]:
        return text
    blocklevel = re.compile(r"^\s*<(h[1-6]|ul|ol|li|div|figure|blockquote|table|pre|p|iframe|hr|img|section)", re.I)
    out = []
    for b in re.split(r"\n\s*\n", text):
        b = b.strip()
        if b:
            out.append(b if blocklevel.match(b) else "<p>" + b.replace("\n", "<br/>\n") + "</p>")
    return "\n".join(out)


def relabel(text):
    text = text.replace("Fall 2025", SEM).replace("2025 Fall", SEM)
    text = re.sub(r"\(\s*(?:Spring|Fall)?\s*20(?:19|20|21|22|23|25)\s*(?:Spring|Fall)?\s*\)", f"({SEM})", text)
    return text


def relabel_title(title):
    """Titles also get bare trailing semester years normalized."""
    title = relabel(title)
    title = re.sub(r"\s*\(?(?:Spring|Fall)?\s*20(?:19|20|21|22|23|25)\)?\s*$", "", title).rstrip()
    if f"({SEM})" not in title:
        title += f" ({SEM})"
    return title


PAGE_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width,initial-scale=1.0" name="viewport"/>
<title>{title} – Programming Humanity ({sem})</title>
<link href="css/style.css" rel="stylesheet"/>
</head>
<body>
<header class="site-header {variant}">
{media}<div class="header-inner">
<div class="site-branding"><p class="site-title"><a href="index.html">Programming Humanity</a></p><span class="site-sep">—</span><p class="site-description">Computational Thinking for Humanity</p></div>
<nav class="main-nav"><ul>
<li><a href="syllabus.html">Syllabus</a></li>
<li><a href="index.html">Readings</a></li>
<li><a href="about.html">About</a></li>
</ul></nav>
<div class="social-nav"><a href="https://twitter.com/ai4dhumanities" rel="noopener" target="_blank">Twitter</a></div>
</div>
<section class="hero"><h1>{h1}</h1></section>
</header>
<main class="content-wrapper">
<div class="page-meta">{sem} • Updated {modified}</div>
<div class="page-content">
{body}
</div>
</main>
<footer class="site-footer">
<p>Programming Humanity — {sem}</p>
</footer>
</body>
</html>
"""

used_images = set()


def localize_media(content):
    def repl(m):
        url = m.group(1)
        clean = url.split("?")[0]
        for pre in CDN_PREFIXES:
            if clean.startswith(pre):
                rel = "images/uploads/" + clean[len(pre):]
                used_images.add((clean, rel))
                return f'src="{rel}"'
        return m.group(0)
    content = re.sub(r'src="(https?://[^"]+)"', repl, content)
    return re.sub(r'\s(?:srcset|sizes)="[^"]*"', "", content)


def main():
    items = load_items()
    winners = pick_current(items)          # theme -> source slug
    out_name = {}                          # source slug -> output filename stem
    for theme, slug in winners.items():
        out_name[slug] = theme
    for extra in ("syllabus", "readings-2", "about"):
        out_name.setdefault(extra, {"readings-2": "readings"}.get(extra, extra))

    # BFS closure over internal page links
    queue = list(out_name)
    while queue:
        cur = queue.pop(0)
        for m in re.finditer(r'href="https?://programminghumanity\.wordpress\.com/([^"#?]*)"',
                             items[cur]["content"]):
            path = m.group(1).rstrip("/")
            if not path or path.startswith(("wp-content", "wp-admin", "wp-login")) or re.match(r"20\d\d/", path):
                continue
            slug = path.split("/")[-1]
            if slug in items and items[slug]["type"] == "page" and slug not in out_name:
                out_name[slug] = slug
                queue.append(slug)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    def rewrite(content):
        content = re.sub(
            r'<a\s[^>]*href="https?://programminghumanity\.wordpress\.com/wp-(?:admin|login)[^"]*"[^>]*>(.*?)</a>',
            r"\1", content, flags=re.S)

        def repl(m):
            raw = m.group(1)
            frag = ""
            if "#" in raw:
                raw, frag = raw.split("#", 1)
                frag = "#" + frag
            path = raw.split("?")[0].rstrip("/")
            slug = path.split("/")[-1] if path else ""
            if not path:
                return f'href="index.html{frag}"'
            if slug in out_name:
                return f'href="{out_name[slug]}.html{frag}"'
            return m.group(0)
        return re.sub(r'href="https?://programminghumanity\.wordpress\.com/([^"]*)"', repl, content)

    for slug, stem in out_name.items():
        e = items[slug]
        body = localize_media(rewrite(relabel(wpautop(e["content"]))))
        title = relabel_title(e["title"]) if stem.startswith("topic-") or stem in ("syllabus", "readings") else relabel(e["title"])
        variant, media = "no-featured-image", ""
        feat = e.get("featured")
        if feat:
            clean = feat.split("?")[0]
            for pre in CDN_PREFIXES:
                if clean.startswith(pre):
                    rel = "images/uploads/" + clean[len(pre):]
                    used_images.add((clean, rel))
                    variant = "has-featured-image"
                    media = f'<div aria-hidden="true" class="featured-media"><img alt="" src="{rel}"/></div>\n'
                    break
        page = PAGE_TMPL.format(title=htmllib.escape(title), h1=htmllib.escape(title),
                                sem=SEM, variant=variant, media=media, body=body,
                                modified=e["modified"][:10])
        (OUT / f"{stem}.html").write_text(page, encoding="utf-8")

    # homepage: readings content with the topic outline linkified
    e = items["readings-2"]
    body = wpautop(relabel(e["content"]))
    for pat, theme in OUTLINE_LINKS:
        def li_repl(m, theme=theme, pat=pat):
            inner = m.group(1)
            if re.search(pat, re.sub(r"<[^>]+>", "", inner).strip(), re.I) and theme in winners.values() or \
               re.search(pat, re.sub(r"<[^>]+>", "", inner).strip(), re.I) and any(theme_of(s) == theme for s in winners.values()):
                return f'<li><a href="{theme}.html">{inner}</a></li>'
            return m.group(0)
        body = re.sub(r"<li[^>]*>(.*?)</li>", li_repl, body, flags=re.S)
    body = localize_media(rewrite(body))
    home_feat = "images/uploads/2019/01/tree-3097419_1920.jpg"
    used_images.add(("https://programminghumanity.wordpress.com/wp-content/uploads/2019/01/tree-3097419_1920.jpg", home_feat))
    media = f'<div aria-hidden="true" class="featured-media"><img alt="" src="{home_feat}"/></div>\n'
    page = PAGE_TMPL.format(title="Readings", h1=f"Programming Humanity — {SEM}",
                            sem=SEM, variant="has-featured-image", media=media,
                            body=body, modified=e["modified"][:10])
    (OUT / "index.html").write_text(page, encoding="utf-8")

    # self-contained assets
    (OUT / "css").mkdir()
    shutil.copy2(ROOT / "css" / "style.css", OUT / "css" / "style.css")
    copied = missing = 0
    for url, rel in used_images:
        src = ROOT / rel
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, dst)
            copied += 1
        else:
            missing += 1
            print("MISSING IMAGE:", url, "->", rel)

    manifest = {"semester": SEM, "pages": sorted(f"{v}.html" for v in out_name.values()),
                "sources": {v: k for k, v in out_name.items()}, "images": copied}
    (ROOT / "dev" / "data" / "website-manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"website/: {len(out_name) + 1} pages, {copied} images copied, {missing} missing")


if __name__ == "__main__":
    main()
