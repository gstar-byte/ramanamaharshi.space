#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成新的QA页面并更新qa-data.json
从 new_qa_data.json 读取数据，生成 qa-71.html 到 qa-90.html
"""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QA_DATA_FILE = os.path.join(SCRIPT_DIR, "qa-data.json")
NEW_QA_FILE = os.path.join(SCRIPT_DIR, "new_qa_data.json")
INDEX_FILE = os.path.join(SCRIPT_DIR, "index.html")

# HTML 模板
def build_html(page_num, title, subtitle, source, items):
    """构建单个QA详情页的HTML"""
    
    # 构建 FAQ JSON-LD schema
    faq_entities = []
    for item in items:
        faq_entities.append({
            "@type": "Question",
            "name": item["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item["a"]
            }
        })
    
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "name": title,
        "mainEntity": faq_entities
    }
    schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
    
    # 构建QA列表HTML
    qa_items_html = ""
    for i, item in enumerate(items, 1):
        qa_items_html += f"""
        <div class="qa-item" id="q{i}">
            <div class="question">
                <span class="q-num">Q{i}</span>
                <h2>{item['q']}</h2>
            </div>
            <div class="answer">
                <p>{item['a']}</p>
                <div class="qa-meta">
                    <span class="category-tag">{item['category']}</span>
                    <span class="source-tag">{source}</span>
                </div>
            </div>
        </div>"""
    
    # 分页导航
    prev_link = f'<a href="qa-{page_num - 1}.html" class="page-btn">&#8249; 上一页</a>' if page_num > 1 else '<span class="page-btn disabled">&#8249; 上一页</span>'
    next_link = f'<a href="qa-{page_num + 1}.html" class="page-btn">下一页 &#8250;</a>' if page_num < 90 else '<span class="page-btn disabled">下一页 &#8250;</span>'
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 拉玛纳·马哈希问答集 第{page_num}页</title>
    <meta name="description" content="{subtitle} - 拉玛纳·马哈希教导精华，{source}">
    <meta name="keywords" content="拉玛纳马哈希,自我参究,不二论,解脱,真我,{title}">
    <link rel="canonical" href="https://ramanamaharshi.space/pages/qa/qa-{page_num}.html">
    <link rel="stylesheet" href="../../index.css">
    <link rel="stylesheet" href="qa-detail.css">
    <script type="application/ld+json">
{schema_json}
    </script>
</head>
<body>
    <header class="site-header">
        <div class="header-inner">
            <a href="../../index.html" class="logo">拉玛纳·马哈希</a>
            <nav class="main-nav">
                <a href="../../index.html">首页</a>
                <a href="index.html" class="active">问答集</a>
                <a href="../books/index.html">著作</a>
                <a href="../about/index.html">关于</a>
            </nav>
        </div>
    </header>

    <main class="qa-detail-main">
        <div class="breadcrumb">
            <a href="../../index.html">首页</a> &rsaquo;
            <a href="index.html">问答集</a> &rsaquo;
            <span>第 {page_num} 页</span>
        </div>

        <div class="page-header">
            <div class="page-num-badge">第 {page_num} 页</div>
            <h1 class="page-title">{title}</h1>
            <p class="page-subtitle">{subtitle}</p>
            <p class="page-source">来源：{source}</p>
        </div>

        <div class="qa-list">
            {qa_items_html}
        </div>

        <div class="pagination">
            {prev_link}
            <a href="index.html" class="page-btn index-btn">返回目录</a>
            {next_link}
        </div>
    </main>

    <footer class="site-footer">
        <div class="footer-inner">
            <p>&copy; 2025 拉玛纳·马哈希知识库 | <a href="../../index.html">ramanamaharshi.space</a></p>
        </div>
    </footer>
</body>
</html>"""
    return html


def main():
    # 1. 读取新QA数据
    print(f"读取新QA数据: {NEW_QA_FILE}")
    with open(NEW_QA_FILE, encoding="utf-8") as f:
        new_pages = json.load(f)
    print(f"  共 {len(new_pages)} 页新数据")

    # 2. 读取现有 qa-data.json
    print(f"读取现有QA数据: {QA_DATA_FILE}")
    with open(QA_DATA_FILE, encoding="utf-8") as f:
        qa_data = json.load(f)
    print(f"  现有条目: {len(qa_data)}")

    # 3. 生成HTML页面 + 收集新QA条目
    new_entries = []
    for page in new_pages:
        page_num = page["page_num"]
        title = page["title"]
        subtitle = page["subtitle"]
        source = page["source"]
        items = page["items"]

        # 生成HTML
        html_path = os.path.join(SCRIPT_DIR, f"qa-{page_num}.html")
        html_content = build_html(page_num, title, subtitle, source, items)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"  生成: qa-{page_num}.html ({len(items)} 条QA)")

        # 收集JSON条目（页面摘要）
        for item in items:
            new_entries.append({
                "id": f"qa-{page_num}",
                "page": page_num,
                "question": item["q"],
                "answer": item["a"],
                "category": item["category"],
                "source": source,
                "title": title
            })

    # 4. 追加到 qa-data.json（去重：检查问题是否已存在）
    existing_questions = {entry.get("question", "") for entry in qa_data}
    added = 0
    for entry in new_entries:
        if entry["question"] not in existing_questions:
            qa_data.append(entry)
            existing_questions.add(entry["question"])
            added += 1

    print(f"\n新增条目: {added}")
    print(f"总条目数: {len(qa_data)}")

    with open(QA_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(qa_data, f, ensure_ascii=False, indent=2)
    print(f"已更新: {QA_DATA_FILE}")

    # 5. 修正 qa-70.html 的下一页链接（如果存在）
    qa70_path = os.path.join(SCRIPT_DIR, "qa-70.html")
    if os.path.exists(qa70_path):
        with open(qa70_path, encoding="utf-8") as f:
            content = f.read()
        if 'class="page-btn disabled">下一页' in content:
            content = content.replace(
                '<span class="page-btn disabled">下一页 &#8250;</span>',
                '<a href="qa-71.html" class="page-btn">下一页 &#8250;</a>'
            )
            with open(qa70_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("已修正 qa-70.html 的下一页链接")

    # 6. 更新 index.html 中的统计数字
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, encoding="utf-8") as f:
            idx = f.read()

        # 替换总页数（60页 -> 90页 或类似模式）
        idx_new = re.sub(r'共\s*\d+\s*页', '共 90 页', idx)
        # 替换总题数（600题 -> 800题 或类似模式）
        idx_new = re.sub(r'共\s*\d+\s*题', f'共 {len(qa_data)} 题', idx_new)
        # 替换600条、800条等数字描述
        idx_new = re.sub(r'(\d+)\s*条问答', f'{len(qa_data)} 条问答', idx_new)

        if idx_new != idx:
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(idx_new)
            print(f"已更新 index.html 统计信息")
        else:
            print("index.html 无需更新（未匹配到数字模式）")

    print("\n全部完成！")
    print(f"  HTML文件: qa-71.html ~ qa-90.html")
    print(f"  QA数据总量: {len(qa_data)} 条")


if __name__ == "__main__":
    main()
