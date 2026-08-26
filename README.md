# Programming Humanity — Static Site

Static HTML/CSS recreation of [programminghumanity.wordpress.com](https://programminghumanity.wordpress.com/).

## Directory Structure

| Folder | Description | Items |
|--------|-------------|-------|
| `2018-2019/` | 2018 2019 | 37 |
| `2019-fall/` | 2019 Fall | 23 |
| `2020/` | 2020 | 1 |
| `2020-fall/` | 2020 Fall | 13 |
| `2020-spring/` | 2020 Spring | 16 |
| `2021/` | 2021 | 31 |
| `2022-spring/` | 2022 Spring | 24 |
| `2023/` | 2023 | 6 |
| `2025-spring/` | 2025 Spring | 18 |
| `2026-spring/` | 2026 Spring | 15 |
| `blog/` | Blog | 127 |
| `core/` | Core | 40 |
| `labs/` | Labs | 15 |
| `research/` | Research | 14 |
| `topics/` | Topics | 18 |
| `css/` | Stylesheet | 1 |
| `images/uploads/` | Media assets | — |
| `tests/` | Test suite | 3 |

## Content Stats

- **283** pages from WordPress export (with full content)
- **115** placeholder stubs (content exists on live site but not in XML export)
- **15** content directories

## Placeholder Pages

Pages marked with a gray "Placeholder" badge have their structure defined but content
needs to be populated from the live WordPress site. These are primarily lecture/week
pages from the AI course semesters (2019-fall, 2021, 2022, 2023, 2025, 2026).

## Local Dev

```bash
python3 -m http.server 8080
# Then open http://localhost:8080/
```

## Tests

```bash
cd tests && pip install -r requirements.txt && pytest -v
```
