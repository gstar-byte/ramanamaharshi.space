#!/usr/bin/env python3
"""
全站 PageSpeed Insights 性能与体验自动化批量优化脚本
涵盖：
1. 修复损坏的 Favicon 标签
2. 规避 Cloudflare email-decode.min.js 阻塞 (email_off)
3. 延迟加载 Google Analytics (解除首屏带宽和主线程争抢)
4. 修复低对比度文本 (WCAG AA 规范)
5. 清除 HTML 中重复声明的 searchIndex / JS 报错
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(r"f:\Ramana\pages")

GA_OLD_PATTERN = re.compile(
    r'<!-- Google Analytics [^\n]*?-->\s*<script async src="https://www.googletagmanager.com/gtag/js\?id=G-MYFWHFPSYB"></script>\s*<script>[\s\S]*?gtag\(\'event\',\s*\'page_view\'\);?\s*}\);?\s*</script>',
    re.MULTILINE
)

GA_NEW_SNIPPET = """<!-- Google Analytics (延迟加载，彻底消除首屏带宽/CPU竞争) -->
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      function loadGA(){
        if(window._gaLoaded) return;
        window._gaLoaded = true;
        var s = document.createElement('script');
        s.async = true;
        s.src = 'https://www.googletagmanager.com/gtag/js?id=G-MYFWHFPSYB';
        document.head.appendChild(s);
        gtag('js', new Date());
        gtag('config', 'G-MYFWHFPSYB');
      }
      if('requestIdleCallback' in window){
        requestIdleCallback(function(){ setTimeout(loadGA, 1500); });
      } else {
        window.addEventListener('load', function(){ setTimeout(loadGA, 1500); });
      }
      ['scroll','touchstart','keydown','mousemove'].forEach(function(e){
        window.addEventListener(e, loadGA, {once: true, passive: true});
      });
    </script>"""

# 修复 favicon 的正则
FAVICON_CORRUPTED_PATTERN = re.compile(
    r'<link rel="icon" type="image/svg\+xml" href="[^"]*favicon\.svg[^"]*">'
)
FAVICON_NEW = '<link rel="icon" type="image/svg+xml" href="/favicon.svg">'

def optimize_html_file(file_path: Path) -> bool:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 修复损坏的 Favicon
    if "favicon.svg'http" in content or "href='/favicon.svg'http" in content or 'viewBox=' in content:
        content = FAVICON_CORRUPTED_PATTERN.sub(FAVICON_NEW, content)
        # 兜底纯字符串替换
        content = re.sub(
            r"<link rel=\"icon\" type=\"image/svg\+xml\" href=\"/favicon\.svg'http:[^>]*>",
            FAVICON_NEW,
            content
        )

    # 2. 优化 Google Analytics
    if 'googletagmanager.com/gtag/js?id=G-MYFWHFPSYB' in content:
        # 如果是旧版 GA 结构
        if GA_OLD_PATTERN.search(content):
            content = GA_OLD_PATTERN.sub(GA_NEW_SNIPPET, content)
        else:
            # 兼容其他可能的 GA 变体
            variant_pattern = re.compile(
                r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-MYFWHFPSYB"></script>\s*<script>[\s\S]*?</script>',
                re.MULTILINE
            )
            content = variant_pattern.sub(GA_NEW_SNIPPET, content)

    # 3. 规避 Cloudflare 邮箱解码脚本 (email_off)
    if '591611431@qq.com' in content and '<!--email_off-->' not in content:
        content = content.replace(
            '<a href="mailto:591611431@qq.com"',
            '<!--email_off--><a href="mailto:591611431@qq.com"'
        )
        content = content.replace(
            '591611431@qq.com</a>',
            '591611431@qq.com</a><!--/email_off-->'
        )

    # 4. 修复低对比度样式 (移除 opacity:0.6)
    if 'opacity:0.6' in content or 'opacity: 0.6' in content:
        content = re.sub(r'opacity:\s*0\.6;?', '', content)

    # 5. 移除 index.html 中重复的 searchIndex / doSearch 脚本块
    if 'const searchIndex =' in content and 'function doSearch' in content:
        search_block_pattern = re.compile(
            r'// 搜索数据索引\s*const searchIndex\s*=\s*\[[\s\S]*?function doSearch[\s\S]*?</script>',
            re.MULTILINE
        )
        content = search_block_pattern.sub('</script>', content)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🚀 开始执行全站 PageSpeed 性能与体验批量优化...")
    html_files = list(BASE_DIR.glob("**/*.html"))
    print(f"📁 共发现 {len(html_files)} 个 HTML 页面待检查")

    updated_count = 0
    for hf in html_files:
        try:
            if optimize_html_file(hf):
                updated_count += 1
        except Exception as e:
            print(f"❌ 处理文件失败 {hf}: {e}")

    print(f"\n✅ 批量优化完成！共更新了 {updated_count} 个页面。")

if __name__ == '__main__':
    main()
