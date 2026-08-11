#!/usr/bin/env python3
"""
模块化 Sitemap Index 站长 XML 地图生成器
- 自动按类别生成 sitemap-main.xml, sitemap-books.xml, sitemap-concepts.xml, sitemap-methods.xml, sitemap-qa.xml, sitemap-persons.xml, sitemap-zh-tw.xml
- 生成主入口 sitemap.xml (Sitemap Index 架构)
- 引入 <?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?> 实现网页版精美渲染展示
"""
import os
import re
import glob
from datetime import date

PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://ramanamaharshi.space"
ZH_TW_ROOT = "/zh-TW"
TODAY = date.today().strftime("%Y-%m-%d")

# 子地图分类规则与中英文映射
SITEMAP_GROUPS = {
    'sitemap-main.xml': '核心主要页面',
    'sitemap-books.xml': '书籍与章节',
    'sitemap-concepts.xml': '灵性概念',
    'sitemap-methods.xml': '参究方法',
    'sitemap-qa.xml': '问答集合',
    'sitemap-persons.xml': '关联人物',
    'sitemap-zh-tw.xml': '繁體中文專區',
}

def classify_rel_path(rel_path):
    """根据相对路径判断归属哪个子地图文件"""
    p = rel_path.replace('\\', '/')
    if p.startswith('zh-TW/'):
        return 'sitemap-zh-tw.xml'
    elif p.startswith('books/'):
        return 'sitemap-books.xml'
    elif p.startswith('concepts/'):
        return 'sitemap-concepts.xml'
    elif p.startswith('methods/'):
        return 'sitemap-methods.xml'
    elif p.startswith('qa/'):
        return 'sitemap-qa.xml'
    elif p.startswith('persons/'):
        return 'sitemap-persons.xml'
    else:
        return 'sitemap-main.xml'

def hreflang_urls(url_path):
    """根据站点路径返回 (zh-CN 完整 URL, zh-TW 完整 URL)"""
    if url_path.startswith(f"{ZH_TW_ROOT}/"):
        rest = url_path[len(f"{ZH_TW_ROOT}/") :]
        if rest in ("", "index.html"):
            cn_path = "/"
        else:
            cn_path = f"/{rest}"
        cn_full = f"{BASE_URL}/" if cn_path == "/" else f"{BASE_URL}{cn_path}"
        if rest in ("", "index.html"):
            tw_full = f"{BASE_URL}{ZH_TW_ROOT}/"
        else:
            tw_full = f"{BASE_URL}{url_path}"
        return cn_full, tw_full

    if url_path in ("/", "/index.html"):
        cn_full = f"{BASE_URL}/"
        tw_full = f"{BASE_URL}{ZH_TW_ROOT}/"
        return cn_full, tw_full

    cn_full = f"{BASE_URL}{url_path}"
    tw_full = f"{BASE_URL}{ZH_TW_ROOT}{url_path}"
    return cn_full, tw_full

def get_url_and_priority(rel_path):
    """从相对路径生成 URL 和优先级"""
    p = rel_path.replace('\\', '/')
    
    if p == 'index.html':
        return '/', 1.0, 'weekly'
    
    depth = p.count('/')
    basename = os.path.basename(p)
    
    if depth == 0:
        priority = 0.8
        freq = 'monthly'
    elif depth == 1:
        if 'ch' in basename or re.match(r'qa-\d+', basename):
            priority = 0.6
            freq = 'monthly'
        else:
            priority = 0.8
            freq = 'monthly'
    else:
        priority = 0.5
        freq = 'monthly'
    
    return f'/{p}', priority, freq

def generate_child_sitemap(filename, urls):
    """生成子模块 XML Sitemap"""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
    lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml"')
    lines.append('        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9')
    lines.append('        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">')
    
    for url_path, priority, freq in urls:
        full_url = f"{BASE_URL}{url_path}"
        cn_href, tw_href = hreflang_urls(url_path)
        lines.append('  <url>')
        lines.append(f'    <loc>{full_url}</loc>')
        lines.append(f'    <lastmod>{TODAY}</lastmod>')
        lines.append(f'    <changefreq>{freq}</changefreq>')
        lines.append(f'    <priority>{priority:.1f}</priority>')
        lines.append(f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{cn_href}"/>')
        lines.append(f'    <xhtml:link rel="alternate" hreflang="zh-TW" href="{tw_href}"/>')
        lines.append('  </url>')
    
    lines.append('</urlset>')
    
    out_path = os.path.join(PAGES_DIR, filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    
    print(f'   ├─ {filename}: {len(urls)} 条链接')

def generate_index_sitemap(sitemap_files):
    """生成 Sitemap Index 主入口 (sitemap.xml)"""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>')
    lines.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for filename in sitemap_files:
        lines.append('  <sitemap>')
        lines.append(f'    <loc>{BASE_URL}/{filename}</loc>')
        lines.append(f'    <lastmod>{TODAY}</lastmod>')
        lines.append('  </sitemap>')
    
    lines.append('</sitemapindex>')
    
    index_path = os.path.join(PAGES_DIR, 'sitemap.xml')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    
    print(f'   └─ sitemap.xml (Sitemap Index): 包含 {len(sitemap_files)} 个子地图')

def main():
    print(f"🚀 开始生成模块化 XML Sitemap ({TODAY})...\n")

    html_files = glob.glob(os.path.join(PAGES_DIR, '**', '*.html'), recursive=True)
    
    exclude_patterns = {
        '_template.html',
        'sitemap.html',
        'sitemap-v2.html',
        'sitemap-test.html',
        'index_fixed.html',
        'index.html.backup',
    }
    
    groups = {key: [] for key in SITEMAP_GROUPS.keys()}
    total_count = 0

    for fp in sorted(html_files):
        bn = os.path.basename(fp)
        if bn in exclude_patterns:
            continue
        
        rel = os.path.relpath(fp, PAGES_DIR)
        url_path, priority, freq = get_url_and_priority(rel)
        group_key = classify_rel_path(rel)
        
        if group_key in groups:
            groups[group_key].append((url_path, priority, freq))
            total_count += 1

    active_sitemaps = []
    for filename, urls in groups.items():
        if len(urls) > 0:
            urls.sort(key=lambda x: (-x[1], x[0]))
            generate_child_sitemap(filename, urls)
            active_sitemaps.append(filename)

    generate_index_sitemap(active_sitemaps)

    print(f"\n✅ 成功生成模块化 XML Sitemap，全站共记 {total_count} 条页面映射！")

if __name__ == '__main__':
    main()
