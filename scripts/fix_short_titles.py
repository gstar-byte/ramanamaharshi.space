"""
修复页面 <title> 标签过短的问题。

策略：
- 简体页面：将 " | 拉玛那马哈希" → " — 拉玛那马哈希灵性教导"
- 繁体页面：将 " | 拉玛那馬哈希" → " — 拉玛那馬哈希靈性教導"
- 若标题仍不足 30 字符，追加额外描述词

目标：所有 <title> 不短于 30 字符。
"""
import os
import re
from pathlib import Path

PAGES_DIR = Path("pages")
MIN_LENGTH = 30

# 替换规则：(旧后缀, 新后缀) —— 按页面类型分别处理
SUFFIX_RULES = [
    # 简体
    (" | 拉玛那马哈希",  " — 拉玛那马哈希灵性教导"),
    # 繁体
    (" | 拉玛那馬哈希",  " — 拉玛那馬哈希靈性教導"),
]

def fix_title(title: str) -> str:
    """将过短的 title 扩展到至少 MIN_LENGTH 字符。"""
    for old_suffix, new_suffix in SUFFIX_RULES:
        if old_suffix in title:
            new_title = title.replace(old_suffix, new_suffix)
            if len(new_title) >= MIN_LENGTH:
                return new_title
            # 还不够长，再追加
            if "靈性" in new_suffix:
                return new_title + " · 自我探索"
            else:
                return new_title + " · 自我探索"
    return title  # 未匹配到规则，保持不变

def fix_file(html_path: Path) -> bool:
    """修复单个 HTML 文件的 title，返回是否有修改。"""
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    
    match = re.search(r'(<title>)(.*?)(</title>)', content, re.IGNORECASE | re.DOTALL)
    if not match:
        return False
    
    old_title = match.group(2).strip()
    if len(old_title) >= MIN_LENGTH:
        return False  # 已经够长，不修改
    
    new_title = fix_title(old_title)
    if new_title == old_title:
        return False  # 未变化
    
    new_content = content[:match.start(2)] + new_title + content[match.end(2):]
    html_path.write_text(new_content, encoding="utf-8")
    return True

def main():
    fixed = []
    skipped = []
    errors = []

    html_files = list(PAGES_DIR.rglob("*.html"))
    print(f"扫描 {len(html_files)} 个 HTML 文件...\n")

    for html_file in html_files:
        try:
            changed = fix_file(html_file)
            if changed:
                # 验证修复后的长度
                content = html_file.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                new_title = m.group(1).strip() if m else ""
                fixed.append((str(html_file), new_title, len(new_title)))
            else:
                skipped.append(str(html_file))
        except Exception as e:
            errors.append((str(html_file), str(e)))

    print(f"✅ 修复了 {len(fixed)} 个页面：")
    for path, title, length in fixed[:20]:
        print(f"  [{length:2d}字符] {path}")
        print(f"           \"{title}\"")
    if len(fixed) > 20:
        print(f"  ... 以及另外 {len(fixed) - 20} 个文件")

    print(f"\n⏭  跳过（已够长）：{len(skipped)} 个")

    if errors:
        print(f"\n❌ 错误：{len(errors)} 个")
        for path, err in errors:
            print(f"  {path}: {err}")

    print(f"\n📊 汇总：修复 {len(fixed)} / 扫描 {len(html_files)} 个文件")

if __name__ == "__main__":
    main()
