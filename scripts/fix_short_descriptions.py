"""
修复 meta description 过短的页面。

策略：
1. sitemap 页面：追加描述性文字
2. qa-7x/8x/9x 页面：在现有简短描述后追加标准后缀
3. concepts/whoami 空描述：从页面 <h1> 或 <p> 提取内容生成描述
4. spiritual-stories-ch1：追加更完整描述
"""
import re
from pathlib import Path

PAGES_DIR = Path("pages")
MIN_LEN = 50

def get_desc(content):
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else None

def set_desc(content, new_desc):
    """替换 meta description 内容。"""
    return re.sub(
        r'(<meta\s+name=["\']description["\']\s+content=["\']).*?(["\'])',
        lambda m: m.group(1) + new_desc + m.group(2),
        content,
        count=1,
        flags=re.IGNORECASE | re.DOTALL
    )

def add_desc(content, new_desc):
    """在 </head> 前插入 meta description（适用于完全没有的情况）。"""
    tag = f'<meta name="description" content="{new_desc}">\n    '
    return content.replace('</head>', tag + '</head>', 1)

def fix_file(html_path: Path) -> bool:
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    old_desc = get_desc(content)
    
    if old_desc is not None and len(old_desc) >= MIN_LEN:
        return False  # 已够长

    path_str = str(html_path).replace("\\", "/")
    is_tw = "zh-TW" in path_str
    
    new_desc = None

    # === sitemap 页面 ===
    if "sitemap" in html_path.name:
        if is_tw:
            new_desc = "拉瑪那馬哈希知識庫完整網站地圖，涵蓋核心概念、問答錄、書籍導讀與修行方法索引，助您系統探索非二元吠檀多靈性智慧。"
        else:
            new_desc = "拉玛那马哈希知识库完整网站地图，涵盖核心概念、问答录、书籍导读与修行方法索引，助您系统探索非二元吠檀多灵性智慧。"

    # === whoami（空描述）===
    elif "whoami" in html_path.name:
        if is_tw:
            new_desc = "「我是誰？」是拉瑪那馬哈希最核心的修行問題。透過自我探究，直接追問內在「我」的根源，是通往真我覺醒的直接之道。本頁收錄完整教示與修行指引。"
        else:
            new_desc = "「我是谁？」是拉玛那马哈希最核心的修行问题。通过自我探究，直接追问内在「我」的根源，是通往真我觉醒的直接之道。本页收录完整教示与修行指引。"

    # === spiritual-stories-ch1 ===
    elif "spiritual-stories-ch1" in html_path.name:
        if is_tw:
            new_desc = "靈性故事 第一章：拉瑪那馬哈希的教示故事，收錄聖者以真實故事傳遞的修行智慧，探索非二元吠檀多的深邃洞見，引導修行者走向內在覺醒與解脫。"
        else:
            new_desc = "灵性故事 第一章：拉玛那马哈希的教示故事，收录圣者以真实故事传递的修行智慧，探索非二元吠檀多的深邃洞见，引导修行者走向内在觉醒与解脱之道。"

    # === qa-7x/8x/9x 系列（已有短描述，追加标准后缀）===
    elif old_desc and re.search(r'qa-[789]\d', path_str):
        suffix = "通过拉玛那马哈希的直接教示，深入探索自我本性、解脱之道与非二元智慧，适合所有寻求灵性觉醒的修行者。"
        new_desc = old_desc + suffix

    # === 其他未匹配情况：通用追加 ===
    elif old_desc:
        if is_tw:
            new_desc = old_desc + "本頁收錄拉瑪那馬哈希的核心教示，涵蓋自我探究、靜默教示與非二元吠檀多智慧，適合所有靈性修行者深入研讀。"
        else:
            new_desc = old_desc + "本页收录拉玛那马哈希的核心教示，涵盖自我探究、静默教示与非二元吠檀多智慧，适合所有灵性修行者深入研读。"
    else:
        # 无描述
        if is_tw:
            new_desc = "拉瑪那馬哈希靈性教示知識庫，收錄自我探究、靜默、解脫等核心概念的完整教示，引導修行者走向內在覺醒之道。"
        else:
            new_desc = "拉玛那马哈希灵性教示知识库，收录自我探究、静默、解脱等核心概念的完整教示，引导修行者走向内在觉醒之道。"

    # 确保不超过 160 字符
    if len(new_desc) > 160:
        new_desc = new_desc[:157] + "..."

    # 写入文件
    if old_desc is not None:
        new_content = set_desc(content, new_desc)
    else:
        new_content = add_desc(content, new_desc)

    html_path.write_text(new_content, encoding="utf-8")
    return True


def main():
    fixed = []
    for html_file in PAGES_DIR.rglob("*.html"):
        try:
            if fix_file(html_file):
                content = html_file.read_text(encoding="utf-8", errors="ignore")
                new_desc = get_desc(content) or ""
                fixed.append((len(new_desc), str(html_file), new_desc))
        except Exception as e:
            print(f"ERROR {html_file}: {e}")

    print(f"✅ 修复了 {len(fixed)} 个页面：\n")
    for length, path, desc in sorted(fixed):
        print(f"  [{length:3d}字符] {Path(path).name}")
        print(f"           \"{desc[:80]}\"")
        print()

    # 验证：是否还有过短的
    remaining = []
    for html_file in PAGES_DIR.rglob("*.html"):
        content = html_file.read_text(encoding="utf-8", errors="ignore")
        desc = get_desc(content)
        if desc is None or len(desc) < MIN_LEN:
            remaining.append((len(desc) if desc else 0, str(html_file), desc or "（无）"))
    
    if remaining:
        print(f"\n⚠️  仍然过短的页面：{len(remaining)} 个")
        for l, p, d in sorted(remaining):
            print(f"  [{l:3d}字符] {p}: \"{d[:60]}\"")
    else:
        print(f"\n🎉 所有页面 meta description 均已达标（≥ {MIN_LEN} 字符）！")


if __name__ == "__main__":
    main()
