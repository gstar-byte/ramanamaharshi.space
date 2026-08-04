#!/usr/bin/env python3
"""
IndexNow 快速提交脚本（日常维护用）
用于在内容新增/修改/删除后，快速提交变动的 URL 给搜索引擎。

用法：
    # 提交单个 URL
    python submit_indexnow_changed.py https://ramanamaharshi.space/concepts/self.html

    # 提交多个 URL
    python submit_indexnow_changed.py \\
        https://ramanamaharshi.space/concepts/self.html \\
        https://ramanamaharshi.space/books/collected-works.html

    # 交互模式（无参数时）
    python submit_indexnow_changed.py
"""

import urllib.request
import urllib.error
import json
import sys

# ==================== 配置 ====================
HOST = "ramanamaharshi.space"
API_KEY = "cb77b97caccf47ba8427199f50123bd9"
KEY_LOCATION = f"https://{HOST}/{API_KEY}.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
# ===============================================


def submit_urls(urls: list[str]) -> None:
    """提交 URL 列表到 IndexNow。"""
    # 校验 URL 都属于本站
    invalid = [u for u in urls if not u.startswith(f"https://{HOST}")]
    if invalid:
        print(f"❌ 以下 URL 不属于 {HOST}，已跳过：")
        for u in invalid:
            print(f"   {u}")
        urls = [u for u in urls if u.startswith(f"https://{HOST}")]

    if not urls:
        print("❌ 没有有效的 URL 可提交。")
        return

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

    print(f"\n📤 正在提交 {len(urls)} 条 URL 到 Bing IndexNow...")
    for u in urls:
        print(f"   - {u}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            if status == 200:
                print(f"\n✅ 提交成功！(HTTP {status})")
                print("   Bing 等搜索引擎将尽快抓取这些 URL。")
            else:
                print(f"\n⚠️  HTTP {status}，请检查响应。")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"\n❌ HTTP 错误 {e.code}: {body[:300]}")
        if e.code == 403:
            print(f"\n  请确认 key 文件已部署并可公开访问：")
            print(f"  https://{HOST}/{API_KEY}.txt")
        elif e.code == 422:
            print("\n  URL 格式不正确，或 URL 不属于声明的 host。")
        elif e.code == 429:
            print("\n  提交频率过高，请稍后再试。")
    except urllib.error.URLError as e:
        print(f"\n❌ 网络错误: {e.reason}")


def main():
    if len(sys.argv) > 1:
        # 命令行参数模式
        urls = sys.argv[1:]
    else:
        # 交互模式
        print("=" * 55)
        print("  IndexNow 快速提交工具")
        print(f"  Host: {HOST}")
        print("=" * 55)
        print("\n请输入要提交的 URL（每行一个，输入空行结束）：")
        urls = []
        while True:
            line = input("> ").strip()
            if not line:
                break
            urls.append(line)

    if not urls:
        print("未输入任何 URL，退出。")
        return

    submit_urls(urls)


if __name__ == "__main__":
    main()
