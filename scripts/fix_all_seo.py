#!/usr/bin/env python3
"""
Comprehensive SEO/GEO fix script for ramanamaharshi.space
Handles: GA bug, HTML comments, hreflang, zh-TW issues, structured data, etc.
"""
import os
import re
import json
from pathlib import Path
from datetime import date

PAGES_DIR = Path(r"f:\ramana\pages")
BASE_URL = "https://ramanamaharshi.space"
TODAY = date.today().isoformat()

# ============================================================
# FIX 1: GA bitwise operator bug (| → ||)  [P0 #7]
# FIX 2: HTML double-nested comments  [P3 #15]
# FIX 3: Description trailing ...  [P3 #19]
# FIX 4: QA pages og:type website→article  [P3 #18]
# FIX 5: Add robots meta if missing  [P3 #17]
# FIX 6: Add x-default hreflang  [P1 #8]
# ============================================================

def fix_ga_bug(content):
    """Fix window.dataLayer = window.dataLayer | []; → ||"""
    # Match both variations
    content = re.sub(
        r'window\.dataLayer\s*=\s*window\.dataLayer\s*\|\s*\[\];',
        'window.dataLayer = window.dataLayer || [];',
        content
    )
    return content

def fix_html_comments(content):
    """Fix <!-- <!-- ... --> → <!-- ... -->"""
    # Replace <!-- <!-- with <!--
    content = re.sub(r'<!--\s*<!--\s*', '<!-- ', content)
    return content

def fix_description_truncation(content):
    """Remove trailing ... in meta descriptions"""
    # Fix in meta description
    content = re.sub(
        r'(<meta\s+name="description"\s+content="[^"]*?)\.\.\.(")',
        r'\1\2',
        content
    )
    # Fix in og:description
    content = re.sub(
        r'(<meta\s+property="og:description"\s+content="[^"]*?)\.\.\.(")',
        r'\1\2',
        content
    )
    return content

def fix_qa_og_type(content):
    """Fix og:type from website to article for QA pages"""
    # Only for qa pages - check if FAQPage schema exists
    if 'FAQPage' in content:
        content = content.replace(
            '<meta property="og:type" content="website">',
            '<meta property="og:type" content="article">'
        )
    return content

def add_robots_meta(content):
    """Add robots meta if missing"""
    if 'name="robots"' not in content:
        # Add after viewport meta
        content = re.sub(
            r'(<meta\s+name="viewport"[^>]*>)',
            r'\1\n    <meta name="robots" content="index, follow">',
            content
        )
    return content

def add_x_default_hreflang(content, file_path):
    """Add x-default hreflang after the last hreflang link"""
    # Check if x-default already exists
    if 'hreflang="x-default"' in content:
        return content
    
    # Find existing hreflang links
    hreflang_pattern = r'<link\s+rel="alternate"\s+hreflang="[^"]*"\s+href="[^"]*">'
    matches = list(re.finditer(hreflang_pattern, content))
    
    if not matches:
        return content
    
    # Determine the default URL (zh-CN version)
    last_match = matches[-1]
    
    # Find the zh-CN href to use as default
    zh_cn_match = re.search(r'hreflang="zh-CN"\s+href="([^"]*)"', content)
    default_url = zh_cn_match.group(1) if zh_cn_match else f'{BASE_URL}/'
    
    x_default_tag = f'\n    <link rel="alternate" hreflang="x-default" href="{default_url}">'
    
    # Insert after the last hreflang link
    pos = last_match.end()
    content = content[:pos] + x_default_tag + content[pos:]
    
    return content

def process_all_html_files():
    """Process all HTML files with simple fixes"""
    html_files = list(PAGES_DIR.rglob("*.html"))
    fixed_count = 0
    
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding='utf-8')
            original = content
            
            # Apply fixes
            content = fix_ga_bug(content)
            content = fix_html_comments(content)
            content = fix_description_truncation(content)
            content = fix_qa_og_type(content)
            content = add_robots_meta(content)
            content = add_x_default_hreflang(content, html_file)
            
            if content != original:
                html_file.write_text(content, encoding='utf-8')
                fixed_count += 1
        except Exception as e:
            print(f"  ERROR processing {html_file}: {e}")
    
    print(f"  Fixed {fixed_count} files (GA bug, comments, descriptions, og:type, robots, x-default)")
    return fixed_count

if __name__ == '__main__':
    print("=== Fix 1: GA bug, HTML comments, descriptions, og:type, robots, x-default ===")
    process_all_html_files()
    print("Done!")
