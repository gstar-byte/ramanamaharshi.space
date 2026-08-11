#!/usr/bin/env python3
"""
本站专属模块化 XML Sitemap 生成器
根据拉玛那马哈希知识库体系生成 4 大核心主题地图：
1. sitemap-books.xml   (首页、知识图谱及著作章节)
2. sitemap-concepts.xml(灵性概念条款与实修方法)
3. sitemap-qa.xml      (灵性问答与关联人物)
4. sitemap-zh-tw.xml   (繁体中文专区)

自动清理生硬的旧碎小 Sitemap 文件。
"""
import os
import re
import glob
from datetime import date

PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://ramanamaharshi.space"
ZH_TW_ROOT = "/zh-TW"
TODAY = date.today().strftime("%Y-%m-%d")

# 站点独有的 4 大 Sitemap 模块定义
SITEMAP_GROUPS = {
    'sitemap-books.xml': '📕 著作与主页 (Books & Main)',
    'sitemap-concepts.xml': '💡 概念与参究 (Concepts & Methods)',
    'sitemap-qa.xml': '❓ 问答与人物 (QA & Persons)',
    'sitemap-zh-tw.xml': '🌏 繁體中文專區 (ZH-TW Region)',
}

# 旧的需要被清理的无意义文件
DEPRECATED_FILES = [
    'sitemap-main.xml',
    'sitemap-methods.xml',
    'sitemap-persons.xml',
]

def classify_rel_path(rel_path):
    """根据本站真实业务结构归类页面"""
    p = rel_path.replace('\\', '/')
    
    # 繁体专区
    if p.startswith('zh-TW/'):
        return 'sitemap-zh-tw.xml'
    
    # 概念与参究方法合并
    elif p.startswith('concepts/') or p.startswith('methods/'):
        return 'sitemap-concepts.xml'
    
    # 问答解答与人物介绍合并
    elif p.startswith('qa/') or p.startswith('persons/'):
        return 'sitemap-qa.xml'
    
    # 首页、图谱及所有书籍章节统一收录进 books/主分类
    else:
        return 'sitemap-books.xml'

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
    
    label = SITEMAP_GROUPS.get(filename, filename)
    print(f'   ├─ {filename} [{label}]: {len(urls)} 条页面映射')

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
    
    print(f'   └─ sitemap.xml (Sitemap Index): 包含 {len(sitemap_files)} 个主主题地图文件')

def cleanup_deprecated_files():
    """清理遗留的过时 XML 文件"""
    for old_file in DEPRECATED_FILES:
        old_path = os.path.join(PAGES_DIR, old_file)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
                print(f'   🗑️ 已清理废弃文件: {old_file}')
            except Exception as e:
                print(f'   ⚠️ 清理 {old_file} 失败: {e}')

def main():
    print(f"🚀 开始根据本站独有架构生成 XML Sitemap ({TODAY})...\n")

    # 先清理废弃多余文件
    cleanup_deprecated_files()

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

    print(f"\n✅ 成功完成定制化 XML Sitemap 生成，全站累计包含 {total_count} 个页面！")

if __name__ == '__main__':
    main()
