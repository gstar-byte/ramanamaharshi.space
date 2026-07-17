#!/usr/bin/env python3
"""Fix BreadcrumbList URLs in zh-TW pages to point to zh-TW versions.
Also fix zh-TW og:url that still points to wrong URL.
"""
import re
from pathlib import Path

PAGES_DIR = Path(r"f:\ramana\pages")
BASE_URL = "https://ramanamaharshi.space"

def fix_breadcrumb_in_zh_tw():
    """Fix all BreadcrumbList JSON-LD in zh-TW pages."""
    zh_tw_dir = PAGES_DIR / "zh-TW"
    fixed = 0
    
    for f in zh_tw_dir.rglob("*.html"):
        content = f.read_text(encoding='utf-8')
        original = content
        
        # Find all JSON-LD script blocks
        def fix_script_block(match):
            block = match.group(0)
            if '"BreadcrumbList"' not in block:
                return block
            
            # Replace all "item": "https://ramanamaharshi.space/..." 
            # with zh-TW version (if not already zh-TW)
            def fix_item(m):
                url = m.group(1)
                if '/zh-TW/' in url:
                    return m.group(0)
                # Replace base URL with zh-TW version
                if url == f'{BASE_URL}/':
                    new_url = f'{BASE_URL}/zh-TW/'
                else:
                    new_url = url.replace(f'{BASE_URL}/', f'{BASE_URL}/zh-TW/', 1)
                return f'"item": "{new_url}"'
            
            block = re.sub(
                r'"item":\s*"(https://ramanamaharshi\.space/[^"]*)"',
                fix_item,
                block
            )
            return block
        
        content = re.sub(
            r'<script type="application/ld\+json">.*?</script>',
            fix_script_block,
            content,
            flags=re.DOTALL
        )
        
        if content != original:
            f.write_text(content, encoding='utf-8')
            fixed += 1
    
    print(f"  Fixed {fixed} zh-TW files (breadcrumb URLs)")
    return fixed

def fix_zh_tw_og_url_remaining():
    """Fix any remaining og:url issues in zh-TW pages."""
    zh_tw_dir = PAGES_DIR / "zh-TW"
    fixed = 0
    
    for f in zh_tw_dir.rglob("*.html"):
        content = f.read_text(encoding='utf-8')
        original = content
        
        rel = f.relative_to(zh_tw_dir)
        rel_str = str(rel).replace('\\', '/')
        
        # Build the correct zh-TW URL
        if rel_str == 'index.html':
            tw_url = f'{BASE_URL}/zh-TW/'
        else:
            tw_url = f'{BASE_URL}/zh-TW/{rel_str}'
        
        # Fix og:url if it doesn't point to zh-TW
        def fix_og_url(m):
            url = m.group(1)
            if '/zh-TW/' in url:
                return m.group(0)
            return f'<meta property="og:url" content="{tw_url}">'
        
        content = re.sub(
            r'<meta\s+property="og:url"\s+content="([^"]*)">',
            fix_og_url,
            content
        )
        
        if content != original:
            f.write_text(content, encoding='utf-8')
            fixed += 1
    
    print(f"  Fixed {fixed} zh-TW files (og:url)")
    return fixed

if __name__ == '__main__':
    print("=== Fix BreadcrumbList URLs and og:url in zh-TW pages ===")
    fix_breadcrumb_in_zh_tw()
    fix_zh_tw_og_url_remaining()
    print("Done!")
