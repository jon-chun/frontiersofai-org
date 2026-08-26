#!/usr/bin/env python3
"""Match WordPress draft page titles to unmatched static site placeholder slugs.

Strategy:
1. Exact: title-to-slug matches placeholder slug exactly
2. Normalized: strip year suffixes and prefixes, then exact match
3. Substring: one slug contains the other (with high similarity)
4. Fuzzy: SequenceMatcher ratio >= 0.85 on normalized slugs
5. Manual review: lower-confidence matches flagged for review
"""

import json
import re
from difflib import SequenceMatcher

def title_to_slug(title):
    """Convert a page title to a URL slug."""
    s = title.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    s = re.sub(r'-+', '-', s)
    return s.strip('-')

def strip_year(slug):
    """Remove trailing year/semester patterns."""
    # Patterns like: -2019, -spring-2025, -spr-2022, -2023fall, -2023-old, -orig-2023, -2
    s = re.sub(r'-(?:spring-|spr-|fall-|orig-)?20\d{2}(?:fall|spring)?(?:-(?:old|orig|2))?$', '', slug)
    # Also handle just trailing -2 or -3
    s = re.sub(r'-\d$', '', s)
    return s

def strip_prefix(slug):
    """Remove common categorical prefixes."""
    for prefix in ['topic-', 'lab-', 'research-', 'reference-', 'dup-', 'w2-lab-']:
        if slug.startswith(prefix):
            return slug[len(prefix):]
    # Remove leading number prefix like "0-", "3-", "4-"
    s = re.sub(r'^\d+-', '', slug)
    return s

def normalize(slug):
    """Fully normalize a slug for comparison."""
    return strip_prefix(strip_year(slug))

def main():
    with open('/Users/jonc/code/programminghumanity-org/tmp/wp-content-dump.json') as f:
        wp_pages = json.load(f)

    with open('/Users/jonc/code/programminghumanity-org/tmp/content-mapping.json') as f:
        mapping = json.load(f)

    drafts = [p for p in wp_pages if p['status'] == 'Draft']
    unmatched = mapping['unmatched_placeholders']
    placeholder_slugs = {slug: path for path, slug in unmatched}

    # Also include password-protected pages that weren't matched
    pw_pages = [p for p in wp_pages if p['status'] == 'Password protected']

    # Combine drafts and password-protected for matching
    candidates = drafts + pw_pages

    # Build title-to-slug for all candidates
    candidate_info = {}
    for page in candidates:
        gen_slug = title_to_slug(page['title'])
        candidate_info[page['slug']] = {
            'title': page['title'],
            'generated_slug': gen_slug,
            'wp_slug': page['slug'],
            'viewUrl': page['viewUrl'],
            'status': page['status'],
        }

    matches = []
    matched_wp = set()
    matched_ph = set()

    # === Pass 1: Exact title-to-slug match ===
    for wp_slug, info in candidate_info.items():
        gen = info['generated_slug']
        if gen in placeholder_slugs and gen not in matched_ph:
            matches.append({
                'match_type': 'exact',
                'wp_slug': wp_slug,
                'wp_title': info['title'],
                'wp_status': info['status'],
                'generated_slug': gen,
                'static_path': placeholder_slugs[gen],
                'placeholder_slug': gen,
                'confidence': 1.0,
            })
            matched_wp.add(wp_slug)
            matched_ph.add(gen)

    # === Pass 2: Normalized exact match ===
    # Build normalized index of remaining placeholders
    for wp_slug, info in candidate_info.items():
        if wp_slug in matched_wp:
            continue
        gen_norm = normalize(info['generated_slug'])
        if not gen_norm or len(gen_norm) < 3:
            continue
        for ph_slug in placeholder_slugs:
            if ph_slug in matched_ph:
                continue
            ph_norm = normalize(ph_slug)
            if gen_norm == ph_norm:
                matches.append({
                    'match_type': 'normalized',
                    'wp_slug': wp_slug,
                    'wp_title': info['title'],
                    'wp_status': info['status'],
                    'generated_slug': info['generated_slug'],
                    'static_path': placeholder_slugs[ph_slug],
                    'placeholder_slug': ph_slug,
                    'confidence': 0.95,
                })
                matched_wp.add(wp_slug)
                matched_ph.add(ph_slug)
                break

    # === Pass 3: High-confidence fuzzy on normalized slugs (>= 0.85) ===
    for wp_slug, info in candidate_info.items():
        if wp_slug in matched_wp:
            continue
        gen_norm = normalize(info['generated_slug'])
        if not gen_norm or len(gen_norm) < 4:
            continue
        best_match = None
        best_ratio = 0
        for ph_slug in placeholder_slugs:
            if ph_slug in matched_ph:
                continue
            ph_norm = normalize(ph_slug)
            ratio = SequenceMatcher(None, gen_norm, ph_norm).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = ph_slug
        if best_match and best_ratio >= 0.85:
            matches.append({
                'match_type': 'fuzzy_high',
                'wp_slug': wp_slug,
                'wp_title': info['title'],
                'wp_status': info['status'],
                'generated_slug': info['generated_slug'],
                'static_path': placeholder_slugs[best_match],
                'placeholder_slug': best_match,
                'confidence': round(best_ratio, 3),
            })
            matched_wp.add(wp_slug)
            matched_ph.add(best_match)

    # === Pass 4: Lower-confidence candidates for manual review (0.65-0.85) ===
    review_candidates = []
    for wp_slug, info in candidate_info.items():
        if wp_slug in matched_wp:
            continue
        gen_norm = normalize(info['generated_slug'])
        if not gen_norm or len(gen_norm) < 4:
            continue
        best_match = None
        best_ratio = 0
        for ph_slug in placeholder_slugs:
            if ph_slug in matched_ph:
                continue
            ph_norm = normalize(ph_slug)
            ratio = SequenceMatcher(None, gen_norm, ph_norm).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = ph_slug
        if best_match and best_ratio >= 0.65:
            review_candidates.append({
                'match_type': 'needs_review',
                'wp_slug': wp_slug,
                'wp_title': info['title'],
                'wp_status': info['status'],
                'generated_slug': info['generated_slug'],
                'static_path': placeholder_slugs[best_match],
                'placeholder_slug': best_match,
                'confidence': round(best_ratio, 3),
            })

    # Collect remaining unmatched
    remaining_drafts = [info for ws, info in candidate_info.items() if ws not in matched_wp]
    remaining_phs = [{'slug': s, 'static_path': placeholder_slugs[s]} for s in placeholder_slugs if s not in matched_ph]

    output = {
        'summary': {
            'total_draft_candidates': len(candidates),
            'total_unmatched_placeholders': len(unmatched),
            'confident_matches': len(matches),
            'needs_review': len(review_candidates),
            'unmatched_drafts_remaining': len(remaining_drafts),
            'unmatched_placeholders_remaining': len(remaining_phs),
        },
        'confident_matches': sorted(matches, key=lambda x: (-x['confidence'], x['match_type'])),
        'needs_review': sorted(review_candidates, key=lambda x: -x['confidence']),
        'unmatched_drafts': sorted(remaining_drafts, key=lambda x: x['title']),
        'unmatched_placeholders': sorted(remaining_phs, key=lambda x: x['slug']),
    }

    with open('/Users/jonc/code/programminghumanity-org/tmp/draft-mapping.json', 'w') as f:
        json.dump(output, f, indent=2)

    # === Report ===
    print("=== DRAFT-TO-PLACEHOLDER MATCHING RESULTS ===\n")
    print(f"Draft/password-protected candidates: {len(candidates)}")
    print(f"Unmatched placeholders to fill:      {len(unmatched)}")
    print(f"Confident matches found:             {len(matches)}")
    print(f"Candidates needing review:           {len(review_candidates)}")
    print(f"Unmatched drafts remaining:          {len(remaining_drafts)}")
    print(f"Unmatched placeholders remaining:    {len(remaining_phs)}")

    by_type = {}
    for m in matches:
        by_type.setdefault(m['match_type'], []).append(m)

    for mtype in ['exact', 'normalized', 'fuzzy_high']:
        mlist = by_type.get(mtype, [])
        if mlist:
            print(f"\n--- {mtype.upper()} ({len(mlist)}) ---")
            for m in mlist:
                print(f"  WP \"{m['wp_title']}\" [{m['wp_status']}]")
                print(f"    slug: {m['generated_slug']} -> {m['placeholder_slug']}")
                print(f"    path: {m['static_path']}  (conf: {m['confidence']})")

    if review_candidates:
        print(f"\n--- NEEDS REVIEW ({len(review_candidates)}) ---")
        for m in review_candidates:
            print(f"  WP \"{m['wp_title']}\" [{m['wp_status']}]")
            print(f"    slug: {m['generated_slug']} -> {m['placeholder_slug']}")
            print(f"    path: {m['static_path']}  (conf: {m['confidence']})")

    print(f"\n--- UNMATCHED PLACEHOLDERS ({len(remaining_phs)}) ---")
    for p in sorted(remaining_phs, key=lambda x: x['slug']):
        print(f"  {p['slug']} ({p['static_path']})")

if __name__ == '__main__':
    main()
