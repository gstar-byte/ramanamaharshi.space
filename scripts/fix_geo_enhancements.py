#!/usr/bin/env python3
"""
GEO Enhancements:
- Add Organization schema to homepage
- Add datePublished/dateModified to Article schema
- Add inLanguage to FAQPage schema
- Add sameAs to WebSite schema
- Add about/mentions to concept Article schema
"""
import re
import json
from pathlib import Path
from datetime import date

PAGES_DIR = Path(r"f:\ramana\pages")
BASE_URL = "https://ramanamaharshi.space"
TODAY = date.today().isoformat()

ORG_SCHEMA = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "拉玛那马哈希知识库",
  "alternateName": "Ramana Maharshi Knowledge Base",
  "url": "https://ramanamaharshi.space",
  "logo": "https://ramanamaharshi.space/icons/icon-512.png",
  "description": "室利·拉玛那·马哈希灵性教示中文知识库",
  "sameAs": [
    "https://en.wikipedia.org/wiki/Ramana_Maharshi",
    "https://www.sriramanamaharshi.org/"
  ]
}
</script>'''

def add_organization_schema(content, file_path):
    """Add Organization schema to homepage only."""
    # Only add to index.html at root or zh-TW root
    rel = file_path.relative_to(PAGES_DIR)
    rel_str = str(rel).replace('\\', '/')
    
    is_homepage = rel_str in ('index.html', 'zh-TW/index.html')
    
    if not is_homepage:
        return content
    
    if '"Organization"' in content:
        return content  # Already has it
    
    # Insert before the first BreadcrumbList or before </head>
    breadcrumb_match = re.search(r'<script type="application/ld\+json">\s*\{[^}]*"BreadcrumbList"', content)
    if breadcrumb_match:
        pos = breadcrumb_match.start()
        content = content[:pos] + ORG_SCHEMA + '\n' + content[pos:]
    else:
        content = content.replace('</head>', ORG_SCHEMA + '\n</head>', 1)
    
    return content

def add_same_as_to_website(content):
    """Add sameAs to WebSite schema on homepage."""
    if '"WebSite"' not in content:
        return content
    
    # Check if sameAs already exists in WebSite block
    def fix_website_block(match):
        block = match.group(0)
        if 'sameAs' in block:
            return block
        
        # Add sameAs before the closing }
        same_as = '''  "sameAs": [
    "https://en.wikipedia.org/wiki/Ramana_Maharshi",
    "https://www.sriramanamaharshi.org/"
  ],
  "potentialAction"'''
        block = block.replace('"potentialAction"', same_as)
        return block
    
    content = re.sub(
        r'\{[^}]*"@type":\s*"WebSite"[^}]*"potentialAction"[^}]*\}',
        fix_website_block,
        content,
        flags=re.DOTALL
    )
    return content

def add_article_dates(content):
    """Add datePublished and dateModified to Article schema."""
    if '"Article"' not in content:
        return content
    
    # Add datePublished and dateModified if missing
    if 'datePublished' in content:
        return content  # Already has dates
    
    def fix_article_block(match):
        block = match.group(0)
        # Insert dates before "url" field
        dates = f'  "datePublished": "{TODAY}",\n  "dateModified": "{TODAY}",\n'
        block = block.replace('"url"', dates + '  "url"')
        return block
    
    content = re.sub(
        r'\{[^}]*"@type":\s*"Article"[^}]*\}',
        fix_article_block,
        content,
        flags=re.DOTALL
    )
    return content

def add_faq_inlanguage(content):
    """Add inLanguage to FAQPage schema."""
    if '"FAQPage"' not in content:
        return content
    
    if 'inLanguage' in content:
        return content
    
    # Determine language from html lang attribute
    lang_match = re.search(r'<html\s+lang="([^"]*)"', content)
    lang = lang_match.group(1) if lang_match else 'zh-CN'
    
    def fix_faq_block(match):
        block = match.group(0)
        # Add inLanguage after "name" field
        block = block.replace(
            '"name":',
            f'"inLanguage": "{lang}",\n  "name":'
        )
        return block
    
    content = re.sub(
        r'\{[^}]*"@type":\s*"FAQPage"[^}]*"mainEntity"',
        fix_faq_block,
        content,
        flags=re.DOTALL
    )
    return content

def add_book_dates(content):
    """Add datePublished to Book schema."""
    if '"Book"' not in content:
        return content
    
    if 'datePublished' in content:
        return content
    
    def fix_book_block(match):
        block = match.group(0)
        # Add datePublished before "url" field
        block = block.replace('"url"', f'"datePublished": "1879-01-01",\n  "url"')
        return block
    
    content = re.sub(
        r'\{[^}]*"@type":\s*"Book"[^}]*\}',
        fix_book_block,
        content,
        flags=re.DOTALL
    )
    return content

def process_geo():
    html_files = list(PAGES_DIR.rglob("*.html"))
    fixed_count = 0
    
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding='utf-8')
            original = content
            
            content = add_organization_schema(content, html_file)
            content = add_same_as_to_website(content)
            content = add_article_dates(content)
            content = add_faq_inlanguage(content)
            content = add_book_dates(content)
            
            if content != original:
                html_file.write_text(content, encoding='utf-8')
                fixed_count += 1
        except Exception as e:
            print(f"  ERROR processing {html_file}: {e}")
    
    print(f"  Enhanced {fixed_count} files (GEO: Organization, dates, inLanguage, sameAs)")
    return fixed_count

if __name__ == '__main__':
    print("=== GEO Enhancements ===")
    process_geo()
    print("Done!")
