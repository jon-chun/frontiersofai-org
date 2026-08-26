#!/usr/bin/env python3
"""Update password-protected pages and placeholder pages."""

import json
import os
import re
from pathlib import Path

SITE_ROOT = Path("/Users/jonc/code/programminghumanity-org")
SKIP_DIRS = {"tests", ".vscode", ".git", "tmp", "images"}

# ── Part 1: Update pages from pw-pages-content.json ──

with open(SITE_ROOT / "tmp" / "pw-pages-content.json") as f:
    pw_pages = json.load(f)

print(f"Loaded {len(pw_pages)} password-protected page entries")

def find_files_for_slug(slug):
    """Find HTML files matching a slug."""
    matches = []
    for root, dirs, files in os.walk(SITE_ROOT):
        # Skip excluded directories
        rel = Path(root).relative_to(SITE_ROOT)
        parts = rel.parts
        if parts and parts[0] in SKIP_DIRS:
            continue
        for fname in files:
            if fname.endswith(".html"):
                stem = fname[:-5]  # remove .html
                if stem == slug:
                    matches.append(Path(root) / fname)
    # Special case: readings-2021 should also update 2021/0-readings-2021.html
    if slug == "readings-2021":
        special = SITE_ROOT / "2021" / "0-readings-2021.html"
        if special.exists() and special not in matches:
            matches.append(special)
    return matches

def update_file_content(filepath, content_html):
    """Replace page-content div contents and remove placeholder badge."""
    html = filepath.read_text(encoding="utf-8")

    # Replace content between <div class="page-content"> and last </div> before </main>
    # Pattern: find <div class="page-content"> ... </div>\n</main>
    pattern = r'(<div class="page-content">).*?(</div>\s*</main>)'
    replacement = r'\1\n' + content_html + r'\n\2'
    new_html, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)

    if count == 0:
        print(f"  WARNING: Could not find page-content div in {filepath}")
        return False

    # Remove placeholder badge
    new_html = new_html.replace(' <span class="badge badge-placeholder">Placeholder</span>', '')

    filepath.write_text(new_html, encoding="utf-8")
    return True

part1_updated = 0
part1_files = []

for entry in pw_pages:
    slug = entry["slug"]
    content_html = entry["contentHTML"]
    files = find_files_for_slug(slug)
    if not files:
        print(f"  No files found for slug: {slug}")
        continue
    for fpath in files:
        rel = fpath.relative_to(SITE_ROOT)
        if update_file_content(fpath, content_html):
            part1_updated += 1
            part1_files.append(str(rel))
            print(f"  Updated: {rel}")

print(f"\n=== Part 1 Complete: {part1_updated} files updated ===")
for f in sorted(part1_files):
    print(f"  {f}")

# ── Part 2: Update remaining placeholder leaf-node pages ──

# Semester directories (folders that have an index.html)
SEMESTER_DIRS = {
    "2018-2019", "2019-fall", "2020", "2020-fall", "2020-spring",
    "2021", "2022-spring", "2023", "2025-spring", "2026-spring"
}

# Build friendly semester names from directory names
def semester_name(dirname):
    """Convert directory name to friendly semester name."""
    parts = dirname.replace("-", " ").split()
    return " ".join(p.capitalize() for p in parts)

part2_updated = 0
part2_files = []

for root, dirs, files in os.walk(SITE_ROOT):
    rel = Path(root).relative_to(SITE_ROOT)
    parts = rel.parts
    if parts and parts[0] in SKIP_DIRS:
        continue
    # Only process files in semester directories
    if not parts or parts[0] not in SEMESTER_DIRS:
        continue
    # Only process direct children (not nested further)
    if len(parts) != 1:
        continue

    folder_name = parts[0]
    sem_name = semester_name(folder_name)

    for fname in sorted(files):
        if not fname.endswith(".html") or fname == "index.html":
            continue
        fpath = Path(root) / fname

        # Skip files already updated in Part 1
        if str(fpath.relative_to(SITE_ROOT)) in part1_files:
            continue

        html = fpath.read_text(encoding="utf-8")

        # Only process placeholders
        if "placeholder-notice" not in html:
            continue

        # Extract page title from hero h1
        title_match = re.search(r'<section class="hero"><h1>(.*?)(?:\s*<span[^>]*>.*?</span>)?</h1></section>', html)
        page_title = title_match.group(1).strip() if title_match else fname[:-5].replace("-", " ").title()

        # Build replacement content
        new_content = (
            f'\n<p>This lecture is part of the <a href="index.html">{sem_name}</a> '
            f'semester of Programming Humanity.</p>\n'
            f'<p>For the complete course outline, readings, and resources, see the '
            f'<a href="../core/readings-2.html">Readings</a> page.</p>\n'
        )

        # Replace page-content div contents
        pattern = r'(<div class="page-content">).*?(</div>\s*</main>)'
        replacement = r'\1' + new_content + r'\2'
        new_html, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)

        if count == 0:
            print(f"  WARNING: Could not find page-content div in {fpath.relative_to(SITE_ROOT)}")
            continue

        # Remove placeholder badge
        new_html = new_html.replace(' <span class="badge badge-placeholder">Placeholder</span>', '')

        fpath.write_text(new_html, encoding="utf-8")
        part2_updated += 1
        part2_files.append(str(fpath.relative_to(SITE_ROOT)))
        print(f"  Updated: {fpath.relative_to(SITE_ROOT)}")

print(f"\n=== Part 2 Complete: {part2_updated} placeholder pages updated ===")
print(f"\n=== TOTAL: {part1_updated + part2_updated} files updated ===")
