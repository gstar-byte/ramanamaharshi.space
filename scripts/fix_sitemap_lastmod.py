#!/usr/bin/env python3
"""Update sitemap.xml lastmod dates to today."""
from pathlib import Path
from datetime import date
import re

PAGES_DIR = Path(r"f:\ramana\pages")
TODAY = date.today().isoformat()

def update_sitemap():
    sitemap = PAGES_DIR / "sitemap.xml"
    content = sitemap.read_text(encoding='utf-8')
    new_content = re.sub(
        r'<lastmod>\d{4}-\d{2}-\d{2}</lastmod>',
        f'<lastmod>{TODAY}</lastmod>',
        content
    )
    sitemap.write_text(new_content, encoding='utf-8')
    count = new_content.count(f'<lastmod>{TODAY}</lastmod>')
    print(f"  Updated {count} lastmod dates to {TODAY}")

if __name__ == '__main__':
    print("=== Update sitemap lastmod dates ===")
    update_sitemap()
    print("Done!")
