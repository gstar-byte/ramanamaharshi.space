#!/usr/bin/env python3
"""CI UI consistency checker for EN vs CN sites.
Run this script locally or via CI to ensure that EN HTML pages contain the required UI components.
It reproduces the earlier detailed comparison and exits with non‑zero status if any mismatch is found.
"""
import os, re, sys

CN_ROOT = r"f:\\26年4月\\kb01\\pages"
EN_ROOT = r"f:\\26年4月\\kb01\\pages\\en"

def get_html_files(base, exclude_dirs=None):
    files = {}
    for root, _, fnames in os.walk(base):
        rel = os.path.relpath(root, base)
        if exclude_dirs and any(rel.startswith(ed) for ed in exclude_dirs):
            continue
        for f in fnames:
            if f.lower().endswith('.html'):
                key = os.path.join(rel, f).replace('\\','/').lstrip('./')
                files[key] = os.path.join(root, f)
    return files

def extract_ui(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        txt = f.read()
    ui = {}
    ui['logo'] = bool(re.search(r'class\s*=\s*"logo"', txt))
    ui['has_close_btn'] = 'sidebar-close-btn' in txt
    ui['has_open_btn'] = 'sidebar-open-btn' in txt
    ui['has_search'] = 'id="search-input"' in txt
    ui['has_breadcrumb'] = 'class="breadcrumb"' in txt
    ui['has_footer'] = 'site-footer' in txt
    ui['has_ga'] = 'G-MYFWHFPSYB' in txt
    ui['has_manifest'] = 'manifest.json' in txt
    ui['has_collapse_js'] = 'initGlobalCollapse' in txt
    ui['has_collapse_css_inline'] = '.sidebar.desktop-hidden' in txt
    # count sidebar sections
    ui['sidebar_sections'] = len(re.findall(r'class="sidebar-section-title"', txt))
    # topbar links count (excluding language dropdown links)
    nav = re.search(r'<nav[^>]*class="topbar-nav[^"]*"[^>]*>(.*?)</nav>', txt, re.DOTALL)
    if nav:
        links = re.findall(r'<a[^>]*>([^<]+)</a>', nav.group(1))
        # filter out language switch links
        ui['topbar_links'] = [l for l in links if l not in ('简体中文','繁體中文','简体','繁體')]
    else:
        ui['topbar_links'] = []
    return ui

def compare_page(rel_path, cn_path, en_path):
    cn = extract_ui(cn_path)
    en = extract_ui(en_path)
    diffs = []
    for key in cn:
        if cn[key] != en[key]:
            # ignore language‑specific differences for logo/text
            if key == 'logo':
                continue
            diffs.append(f"  {key}: CN={cn[key]}, EN={en[key]}")
    return diffs

def main():
    cn_files = get_html_files(CN_ROOT, exclude_dirs=['en','zh-TW'])
    en_files = get_html_files(EN_ROOT)
    # we only compare files that exist in both sides
    common = set(cn_files.keys()) & set(en_files.keys())
    total_errors = 0
    for rel in sorted(common):
        diffs = compare_page(rel, cn_files[rel], en_files[rel])
        if diffs:
            print(f"\n❌ {rel}")
            for d in diffs:
                print(d)
            total_errors += 1
    if total_errors:
        print(f"\n🛑 UI mismatches found: {total_errors} page(s).")
        sys.exit(1)
    else:
        print("✅ All EN pages match CN UI expectations.")
        sys.exit(0)

if __name__ == '__main__':
    main()
