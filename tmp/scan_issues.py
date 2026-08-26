#!/usr/bin/env python3
"""Scan all HTML files for remaining content issues."""

import os
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path("/Users/jonc/code/programminghumanity-org")
EXCLUDE_DIRS = {"tests", ".vscode", ".git", "tmp", "node_modules"}

# Issues collectors
issues = {
    "placeholder_notice_class": [],
    "content_pending_text": [],
    "empty_or_short_content": [],
    "contenteditable_attr": [],
    "data_wp_attributes": [],
    "block_editor_classes": [],
    "broken_internal_links": [],
}


class PageContentExtractor(HTMLParser):
    """Extract text content from <div class='page-content'>."""
    def __init__(self):
        super().__init__()
        self.in_page_content = False
        self.depth = 0
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        if self.in_page_content:
            self.depth += 1
        else:
            attrs_dict = dict(attrs)
            cls = attrs_dict.get("class", "")
            if tag == "div" and "page-content" in cls:
                self.in_page_content = True
                self.depth = 1

    def handle_endtag(self, tag):
        if self.in_page_content:
            self.depth -= 1
            if self.depth <= 0:
                self.in_page_content = False

    def handle_data(self, data):
        if self.in_page_content:
            self.text_parts.append(data)

    def get_text(self):
        return "".join(self.text_parts).strip()


def get_html_files():
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for f in filenames:
            if f.endswith(".html"):
                files.append(Path(dirpath) / f)
    return sorted(files)


def check_file(filepath):
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return

    rel = filepath.relative_to(ROOT)

    # 1. placeholder-notice class
    if "placeholder-notice" in content:
        issues["placeholder_notice_class"].append(str(rel))

    # 2. "Content Pending" text
    if "Content Pending" in content:
        issues["content_pending_text"].append(str(rel))

    # 3. Empty or very short page-content
    extractor = PageContentExtractor()
    try:
        extractor.feed(content)
        text = extractor.get_text()
        if extractor.text_parts is not None:
            # Only flag if the file actually has a page-content div
            if 'class="page-content"' in content or "class='page-content'" in content:
                if len(text) < 100:
                    issues["empty_or_short_content"].append(
                        (str(rel), len(text), text[:80] if text else "(empty)")
                    )
    except Exception:
        pass

    # 4. contenteditable attributes
    if "contenteditable" in content:
        count = content.count("contenteditable")
        issues["contenteditable_attr"].append((str(rel), count))

    # 5. data-wp- attributes
    wp_attrs = re.findall(r'data-wp-[a-z-]+', content)
    if wp_attrs:
        unique = sorted(set(wp_attrs))
        issues["data_wp_attributes"].append((str(rel), unique))

    # 6. block-editor- classes
    be_classes = re.findall(r'block-editor-[a-zA-Z0-9_-]+', content)
    if be_classes:
        unique = sorted(set(be_classes))
        issues["block_editor_classes"].append((str(rel), unique))

    # 7. Broken internal links
    href_pattern = re.compile(r'href=["\']([^"\']+)["\']')
    for match in href_pattern.finditer(content):
        href = match.group(1)
        # Skip external, anchors, mailto, tel, javascript
        if any(href.startswith(p) for p in ("http://", "https://", "#", "mailto:", "tel:", "javascript:")):
            continue
        # Skip empty
        if not href.strip():
            continue

        # Resolve relative to file's directory
        href_clean = href.split("#")[0].split("?")[0]
        if not href_clean:
            continue

        target = (filepath.parent / unquote(href_clean)).resolve()
        if not target.exists():
            issues["broken_internal_links"].append((str(rel), href))


def main():
    html_files = get_html_files()
    print(f"Scanning {len(html_files)} HTML files...\n")

    for f in html_files:
        check_file(f)

    # Report
    print("=" * 70)
    print("CONTENT ISSUES REPORT")
    print("=" * 70)

    # 1
    items = issues["placeholder_notice_class"]
    print(f"\n## 1. Files with 'placeholder-notice' class: {len(items)}")
    for f in items:
        print(f"   {f}")

    # 2
    items = issues["content_pending_text"]
    print(f"\n## 2. Files with 'Content Pending' text: {len(items)}")
    for f in items:
        print(f"   {f}")

    # 3
    items = issues["empty_or_short_content"]
    print(f"\n## 3. Files with empty/short page-content (<100 chars): {len(items)}")
    for f, length, preview in items:
        print(f"   {f} ({length} chars): {preview}")

    # 4
    items = issues["contenteditable_attr"]
    print(f"\n## 4. Files with 'contenteditable' attributes: {len(items)}")
    for f, count in items:
        print(f"   {f} ({count} occurrences)")

    # 5
    items = issues["data_wp_attributes"]
    print(f"\n## 5. Files with 'data-wp-*' attributes: {len(items)}")
    for f, attrs in items:
        print(f"   {f}: {', '.join(attrs)}")

    # 6
    items = issues["block_editor_classes"]
    print(f"\n## 6. Files with 'block-editor-*' classes: {len(items)}")
    for f, classes in items:
        print(f"   {f}: {', '.join(classes)}")

    # 7
    items = issues["broken_internal_links"]
    print(f"\n## 7. Broken internal links: {len(items)}")
    # Group by target for readability
    by_target = {}
    for f, href in items:
        by_target.setdefault(href, []).append(f)
    for href, files in sorted(by_target.items()):
        print(f"   -> {href}")
        for f in files:
            print(f"      in: {f}")

    # Summary
    print("\n" + "=" * 70)
    total = sum(
        len(v) for v in issues.values()
    )
    print(f"TOTAL ISSUES FOUND: {total}")
    print("=" * 70)


if __name__ == "__main__":
    main()
