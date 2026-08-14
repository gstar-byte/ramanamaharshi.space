#!/usr/bin/env python3
"""
全站 Agentic Browsing (3/3) 与 Accessibility (100分) 终极修复脚本
1. 给全站所有交互元素（button, input, toggle）补全无障碍标签 aria-label
2. 在 <head> 中注入 LLMS.txt 发现声明
3. 确保所有内联链接具有明确的语义与无障碍特征
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(r"f:\Ramana\pages")

LLMS_LINK = '<link rel="alternate" type="text/plain" href="/llms.txt" title="LLMs.txt">'

def enhance_html(file_path: Path) -> bool:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 注入 llms.txt 关联
    if 'rel="alternate" type="text/plain" href="/llms.txt"' not in content:
        if '<link rel="icon"' in content:
            content = content.replace(
                '<link rel="icon"',
                f'{LLMS_LINK}\n    <link rel="icon"'
            )

    # 2. 补全 hamburger aria-label
    content = re.sub(
        r'<button class="hamburger" onclick="toggleSidebar\(\)"(?![^>]*aria-label)>',
        r'<button class="hamburger" onclick="toggleSidebar()" aria-label="打开侧边导航菜单">',
        content
    )

    # 3. 补全 menu-toggle aria-label
    content = re.sub(
        r'<button class="menu-toggle" onclick="toggleSidebar\(\)"(?![^>]*aria-label)>',
        r'<button class="menu-toggle" onclick="toggleSidebar()" aria-label="切换侧边栏">',
        content
    )

    # 4. 补全 sidebar-close-btn 和 sidebar-open-btn aria-label
    content = re.sub(
        r'<button class="sidebar-close-btn"([^>]*(?![^>]*aria-label))>',
        r'<button class="sidebar-close-btn" aria-label="收起侧边栏"\1>',
        content
    )
    content = re.sub(
        r'<button class="sidebar-open-btn"([^>]*(?![^>]*aria-label))>',
        r'<button class="sidebar-open-btn" aria-label="展开侧边栏"\1>',
        content
    )

    # 5. 补全 search-input aria-label
    content = re.sub(
        r'<input type="text" id="search-input" placeholder="([^"]*)"([^>]*(?![^>]*aria-label))>',
        r'<input type="text" id="search-input" placeholder="\1" aria-label="搜索框: \1"\2>',
        content
    )

    # 6. 补全 search-trigger aria-label
    content = re.sub(
        r'<button class="search-trigger"([^>]*(?![^>]*aria-label))>',
        r'<button class="search-trigger" aria-label="搜索"\1>',
        content
    )

    # 7. 补全 search-close aria-label
    content = re.sub(
        r'<button class="search-close"([^>]*(?![^>]*aria-label))>',
        r'<button class="search-close" aria-label="关闭搜索"\1>',
        content
    )

    # 8. 补全 TTS 朗读器按钮 aria-label
    content = re.sub(
        r'<button class="tts-play-btn" id="tts-start-btn"([^>]*(?![^>]*aria-label))>',
        r'<button class="tts-play-btn" id="tts-start-btn" aria-label="播放文章语音朗读"\1>',
        content
    )

    # 9. 修复所有页脚未带下划线的内联主页链接
    content = re.sub(
        r'<p><a href="([^"]*index\.html)"(?![^>]*text-decoration)>',
        r'<p><a href="\1" style="text-decoration: underline;">',
        content
    )

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🚀 开始修复 Agentic Browsing (3/3) 与 Accessibility (100分)...")
    html_files = list(BASE_DIR.glob("**/*.html"))
    updated = 0
    for hf in html_files:
        if enhance_html(hf):
            updated += 1
    print(f"✅ 完成！共强化更新了 {updated} 个页面的无障碍树与 Agentic 标签。")

if __name__ == '__main__':
    main()
