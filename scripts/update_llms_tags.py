#!/usr/bin/env python3
"""
更新全站 HTML 的 llms.txt 链接声明
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(r"f:\Ramana\pages")

NEW_LLMS_TAGS = '<link rel="alternate" type="text/markdown" href="/llms.txt" title="LLMs.txt">\n    <link rel="alternate" type="text/plain" href="/llms.txt" title="LLMs.txt">'

def update_html(file_path: Path) -> bool:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 替换旧的单行 llms.txt 链接
    old_tag = '<link rel="alternate" type="text/plain" href="/llms.txt" title="LLMs.txt">'
    if old_tag in content and 'type="text/markdown"' not in content:
        content = content.replace(old_tag, NEW_LLMS_TAGS)
    elif 'href="/llms.txt"' not in content:
        if '<link rel="icon"' in content:
            content = content.replace(
                '<link rel="icon"',
                f'{NEW_LLMS_TAGS}\n    <link rel="icon"'
            )

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🚀 批量更新全站 llms.txt 链接声明...")
    html_files = list(BASE_DIR.glob("**/*.html"))
    updated = 0
    for hf in html_files:
        if update_html(hf):
            updated += 1
    print(f"✅ 更新了 {updated} 个文件！")

if __name__ == '__main__':
    main()
