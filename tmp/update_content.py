#!/usr/bin/env python3
"""Update static HTML files with WordPress content from the content dump."""

import json
import os
import re
import sys

SITE_ROOT = "/Users/jonc/code/programminghumanity-org"
CONTENT_DUMP = os.path.join(SITE_ROOT, "tmp", "wp-content-dump.json")
CONTENT_MAPPING = os.path.join(SITE_ROOT, "tmp", "content-mapping.json")

# Classes to strip from WP content
STRIP_CLASSES = [
    "wordads-ad-wrapper",
    "wordads-ad",
    "sharedaddy",
    "jp-post-flair",
    "wpcnt",
]


def strip_ad_widgets(html):
    """Remove WordPress ad blocks and share widgets from content HTML."""
    for cls in STRIP_CLASSES:
        # Remove entire elements (div, section, etc.) with these classes
        # Handle self-closing and block elements
        pattern = re.compile(
            r'<(\w+)\b[^>]*\bclass\s*=\s*"[^"]*\b' + re.escape(cls) + r'\b[^"]*"[^>]*>.*?</\1>',
            re.DOTALL
        )
        html = pattern.sub('', html)
    return html


def update_file(static_path, content_html, wp_title):
    """Update a single static HTML file with WordPress content."""
    full_path = os.path.join(SITE_ROOT, static_path)

    if not os.path.exists(full_path):
        return False, f"File not found: {full_path}"

    with open(full_path, 'r', encoding='utf-8') as f:
        original = f.read()

    # Clean the WP content
    cleaned_content = strip_ad_widgets(content_html)

    # Replace content between <div class="page-content"> and </div>\n</main>
    pattern = re.compile(
        r'(<div class="page-content">).*?(</div>\s*</main>)',
        re.DOTALL
    )

    match = pattern.search(original)
    if not match:
        return False, f"Could not find page-content div in {static_path}"

    replacement = f'<div class="page-content">\n{cleaned_content}\n</div>\n</main>'
    updated = pattern.sub(replacement, original, count=1)

    # Check if this was a placeholder page
    is_placeholder = "placeholder-notice" in original

    if is_placeholder:
        # Remove the placeholder badge from hero h1
        updated = re.sub(
            r' <span class="badge badge-placeholder">Placeholder</span>',
            '',
            updated
        )

        # Update page-meta: replace "Folder: ..." with WP title info
        updated = re.sub(
            r'<div class="page-meta">Folder: [^<]*</div>',
            f'<div class="page-meta">{wp_title}</div>',
            updated
        )

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(updated)

    return True, "placeholder" if is_placeholder else "content"


def main():
    # Load data
    with open(CONTENT_DUMP, 'r', encoding='utf-8') as f:
        wp_pages = json.load(f)

    with open(CONTENT_MAPPING, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    # Build slug -> wp page lookup
    slug_map = {}
    for page in wp_pages:
        slug_map[page["slug"]] = page

    matched = mapping["matched"]
    total = len(matched)
    updated_content = 0
    updated_placeholder = 0
    skipped = 0
    errors = []

    for static_path, slug in matched:
        wp_page = slug_map.get(slug)
        if not wp_page:
            errors.append(f"Slug not found in dump: {slug} (for {static_path})")
            skipped += 1
            continue

        if not wp_page.get("accessible", False):
            errors.append(f"Page not accessible: {slug} (reason: {wp_page.get('reason', 'unknown')})")
            skipped += 1
            continue

        content_html = wp_page.get("contentHTML", "")
        if not content_html or not content_html.strip():
            errors.append(f"Empty content for slug: {slug} (for {static_path})")
            skipped += 1
            continue

        wp_title = wp_page.get("title", "")
        success, status = update_file(static_path, content_html, wp_title)

        if success:
            if status == "placeholder":
                updated_placeholder += 1
            else:
                updated_content += 1
        else:
            errors.append(status)
            skipped += 1

    print(f"=== Content Update Summary ===")
    print(f"Total matched pairs: {total}")
    print(f"Updated (had content): {updated_content}")
    print(f"Updated (was placeholder): {updated_placeholder}")
    print(f"Total updated: {updated_content + updated_placeholder}")
    print(f"Skipped/errors: {skipped}")

    if errors:
        print(f"\n=== Errors ({len(errors)}) ===")
        for e in errors:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
