#!/usr/bin/env python3
"""Add datePublished/dateModified to Article and Book schemas using JSON-LD block parsing."""
import re
import json
from pathlib import Path
from datetime import date

PAGES_DIR = Path(r"f:\ramana\pages")
TODAY = date.today().isoformat()

def fix_jsonld_blocks(content, lang='zh-CN'):
    """Find all JSON-LD script blocks and fix them."""
    def process_block(match):
        script_tag = match.group(0)
        json_text = match.group(1)
        
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            return script_tag  # Skip invalid JSON
        
        changed = False
        
        # Add dates to Article
        if data.get('@type') == 'Article' and 'datePublished' not in data:
            data['datePublished'] = TODAY
            data['dateModified'] = TODAY
            changed = True
        
        # Add datePublished to Book (use original publication date)
        if data.get('@type') == 'Book' and 'datePublished' not in data:
            data['datePublished'] = '1879-01-01'
            changed = True
        
        if changed:
            new_json = json.dumps(data, ensure_ascii=False, indent=2)
            return f'<script type="application/ld+json">\n{new_json}\n</script>'
        
        return script_tag
    
    # Match all JSON-LD blocks
    content = re.sub(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        process_block,
        content,
        flags=re.DOTALL
    )
    return content

def process_all():
    html_files = list(PAGES_DIR.rglob("*.html"))
    fixed_count = 0
    
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding='utf-8')
            original = content
            
            content = fix_jsonld_blocks(content)
            
            if content != original:
                html_file.write_text(content, encoding='utf-8')
                fixed_count += 1
        except Exception as e:
            print(f"  ERROR: {html_file}: {e}")
    
    print(f"  Fixed {fixed_count} files (Article/Book dates)")
    return fixed_count

if __name__ == '__main__':
    print("=== Fix Article/Book dates in JSON-LD ===")
    process_all()
    print("Done!")
