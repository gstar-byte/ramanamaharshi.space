#!/usr/bin/env python3
"""Fix stray </title> tags in zh-TW QA pages."""
import re
from pathlib import Path

PAGES_DIR = Path(r"f:\ramana\pages")

def fix_stray_title():
    qa_dir = PAGES_DIR / "zh-TW" / "qa"
    fixed = 0
    for f in qa_dir.glob("*.html"):
        content = f.read_text(encoding='utf-8')
        # Remove: <!-- 預加載關鍵資源  -->\n    </title>
        # The stray </title> after a comment and before </head>
        new_content = re.sub(
            r'(<!-- [^>]* -->)\s*</title>\s*\n(</head>)',
            r'\1\n\2',
            content
        )
        if new_content != content:
            f.write_text(new_content, encoding='utf-8')
            fixed += 1
    print(f"  Fixed {fixed} zh-TW QA pages (stray </title>)")
    return fixed

if __name__ == '__main__':
    print("=== Fix stray </title> in zh-TW QA pages ===")
    fix_stray_title()
    print("Done!")
