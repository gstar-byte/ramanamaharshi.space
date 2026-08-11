#!/usr/bin/env python3
"""
KB01 性能优化脚本 - 压缩CSS、合并JS、减少HTTP请求
"""
import re
import os
from pathlib import Path

KB01 = Path(__file__).parent.resolve()

def minify_css(css_path):
    """压缩CSS：去除注释、空格、换行"""
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 去除注释
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    # 去除多余空格（保留CSS属性之间的空格）
    content = re.sub(r'\s*([{}:;,])\s*', r'\1', content)
    content = re.sub(r';\s*}', '}', content)
    content = re.sub(r'\s+', ' ', content)

    # 去除首尾空白
    content = content.strip()

    return content

def minify_js(js_path):
    """压缩JS：去除注释和多余空格"""
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 去除单行注释
    content = re.sub(r'//[^\n]*', '', content)

    # 去除多行注释
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    # 去除多余空格
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*([{}();,=+\-*/<>!&|.?:])\s*', r'\1', content)

    return content.strip() + '\n'

def create_bundle_js():
    """合并script.js、search.js和audio-reader.js为一个bundle"""
    script_path = KB01 / "script.js"
    search_path = KB01 / "search.js"
    audio_path = KB01 / "audio-reader.js"

    bundle = ""

    if script_path.exists():
        bundle += minify_js(script_path) + "\n"

    if search_path.exists():
        bundle += minify_js(search_path) + "\n"

    if audio_path.exists():
        bundle += minify_js(audio_path) + "\n"

    return bundle


def update_html_references():
    """更新HTML文件中的JS/CSS引用"""
    html_files = list(KB01.glob("*.html")) + list(KB01.glob("**/*.html"))
    updated = 0

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content

            # 替换 styles.css 为 styles.min.css
            content = content.replace('href="styles.css"', 'href="styles.min.css"')
            content = content.replace("href='styles.css'", "href='styles.min.css'")

            # 替换 script.js + search.js 为 bundle.min.js
            # 先移除旧的script标签
            content = re.sub(r'<script\s+[^>]*src=["\']script\.js["\'][^>]*></script>\s*', '', content)
            content = re.sub(r'<script\s+[^>]*src=["\']search\.js["\'][^>]*></script>\s*', '', content)

            # 添加bundle.min.js（在</body>前）
            if 'bundle.min.js' not in content and 'app.js' not in content:
                content = content.replace('</body>', '<script src="bundle.min.js" defer></script>\n</body>')

            # 对于使用app.js的页面，保持不变或改为bundle
            # 因为app.js已经包含了搜索功能

            if content != original:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated += 1

        except Exception as e:
            print(f"Error processing {html_file}: {e}")

    return updated

def create_bundle_js_for(dir_path):
    """合并指定目录下的 script.js、search.js 和 audio-reader.js"""
    script_path = dir_path / "script.js"
    search_path = dir_path / "search.js"
    audio_path = dir_path / "audio-reader.js"

    bundle = ""

    if script_path.exists():
        bundle += minify_js(script_path) + "\n"

    if search_path.exists():
        bundle += minify_js(search_path) + "\n"

    if audio_path.exists():
        bundle += minify_js(audio_path) + "\n"

    return bundle

def main():
    print("🚀 KB01 性能优化与资源打包开始...")

    dirs_to_process = [KB01, KB01 / "zh-TW"]

    for target_dir in dirs_to_process:
        if not target_dir.exists():
            continue

        print(f"\n📂 处理目录: {target_dir}")

        css_path = target_dir / "styles.css"
        if css_path.exists():
            css_size_before = css_path.stat().st_size
            minified_css = minify_css(css_path)
            min_css_path = target_dir / "styles.min.css"
            with open(min_css_path, 'w', encoding='utf-8') as f:
                f.write(minified_css)
            css_size_after = min_css_path.stat().st_size
            print(f"   styles.css: {css_size_before:,} → {css_size_after:,} bytes (节省 {(1-css_size_after/css_size_before)*100:.1f}%)")

        bundle = create_bundle_js_for(target_dir)
        if bundle.strip():
            bundle_path = target_dir / "bundle.min.js"
            with open(bundle_path, 'w', encoding='utf-8') as f:
                f.write(bundle)
            bundle_size = len(bundle.encode('utf-8'))
            print(f"   bundle.min.js: {bundle_size:,} bytes (已合并 script.js + search.js + audio-reader.js)")

    print("\n🔗 更新全站HTML引用...")
    updated = update_html_references()
    print(f"   更新了 {updated} 个HTML文件")

    print("\n✅ 全站优化完成!")

if __name__ == "__main__":
    main()

