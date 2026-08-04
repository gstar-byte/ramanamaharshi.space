#!/usr/bin/env python3
"""
IndexNow 批量提交脚本
功能：从 sitemap.xml 中读取所有 URL，分批提交到 Bing IndexNow API。

用法：
    python submit_indexnow.py

IndexNow API 文档：https://www.indexnow.org/documentation
"""

import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import json
import time
import sys
import os

# ==================== 配置 ====================
HOST = "ramanamaharshi.space"
API_KEY = "cb77b97caccf47ba8427199f50123bd9"
KEY_LOCATION = f"https://{HOST}/{API_KEY}.txt"
SITEMAP_PATH = os.path.join(os.path.dirname(__file__), "..", "pages", "sitemap.xml")

# IndexNow API 端点（api.indexnow.org 会自动分发给 Bing、Yandex 等多个引擎）
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

# 每批提交的 URL 数量（官方最大 10,000，建议 1000 避免超时）
BATCH_SIZE = 1000

# 批次间隔秒数（避免 429 Too Many Requests）
BATCH_DELAY = 2
# ===============================================


def parse_sitemap(sitemap_path: str) -> list[str]:
    """解析 sitemap.xml，提取所有 <loc> URL。"""
    print(f"📄 正在解析 sitemap: {sitemap_path}")
    
    if not os.path.exists(sitemap_path):
        print(f"❌ 找不到 sitemap 文件: {sitemap_path}")
        sys.exit(1)

    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    # sitemap 命名空间
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text.strip() for loc in root.findall(".//sm:loc", ns) if loc.text]

    print(f"✅ 共解析到 {len(urls)} 条 URL")
    return urls


def submit_batch(urls: list[str], batch_num: int, total_batches: int) -> bool:
    """向 IndexNow API 提交一批 URL，返回是否成功。"""
    payload = {
        "host": HOST,
        "key": API_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": f"IndexNow-Submitter/1.0 ({HOST})"
        },
        method="POST"
    )

    print(f"\n📤 提交第 {batch_num}/{total_batches} 批（共 {len(urls)} 条 URL）...")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="replace")
            if status == 200:
                print(f"   ✅ 成功 (HTTP {status})")
            else:
                print(f"   ⚠️  响应 HTTP {status}: {body[:200]}")
            return status == 200
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"   ❌ HTTP 错误 {e.code}: {body[:300]}")
        if e.code == 429:
            print("   ⏳ 触发速率限制，等待 10 秒后继续...")
            time.sleep(10)
        elif e.code == 403:
            print("   ⚠️  403 Forbidden: key 文件可能尚未部署到网站，请先确认：")
            print(f"      https://{HOST}/{API_KEY}.txt 可公开访问")
        return False
    except urllib.error.URLError as e:
        print(f"   ❌ 网络错误: {e.reason}")
        return False


def main():
    print("=" * 60)
    print("  Bing IndexNow 批量提交工具")
    print(f"  Host:        {HOST}")
    print(f"  API Key:     {API_KEY}")
    print(f"  Key 文件:    {KEY_LOCATION}")
    print(f"  API 端点:    {INDEXNOW_ENDPOINT}")
    print("=" * 60)

    # 1. 解析 sitemap
    all_urls = parse_sitemap(SITEMAP_PATH)

    if not all_urls:
        print("❌ 未找到任何 URL，退出。")
        sys.exit(1)

    # 2. 分批提交
    batches = [all_urls[i:i + BATCH_SIZE] for i in range(0, len(all_urls), BATCH_SIZE)]
    total_batches = len(batches)
    success_count = 0
    fail_count = 0

    print(f"\n🚀 开始提交，共 {total_batches} 批（每批最多 {BATCH_SIZE} 条）\n")

    for idx, batch in enumerate(batches, start=1):
        ok = submit_batch(batch, idx, total_batches)
        if ok:
            success_count += len(batch)
        else:
            fail_count += len(batch)

        if idx < total_batches:
            print(f"   ⏱  等待 {BATCH_DELAY} 秒...")
            time.sleep(BATCH_DELAY)

    # 3. 汇总
    print("\n" + "=" * 60)
    print("  提交完成！汇总：")
    print(f"  ✅ 成功提交：{success_count} 条 URL")
    if fail_count:
        print(f"  ❌ 提交失败：{fail_count} 条 URL")
    print("=" * 60)
    print("\n📋 后续步骤：")
    print("  1. 访问 https://www.bing.com/webmasters 查看 IndexNow 提交状态")
    print("  2. 日常内容更新后，使用 submit_indexnow_changed.py 提交变动 URL")


if __name__ == "__main__":
    main()
