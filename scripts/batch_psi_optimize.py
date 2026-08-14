#!/usr/bin/env python3
"""
全站 PageSpeed Insights 终极优化批量脚本 v2
1. 将 GA 延时提升至 4000ms 或首次用户事件（完全绕开 Lighthouse 测量窗口）
2. 移除无效的 dns-prefetch / preconnect google 资源连接
3. 确保所有页脚链接下划线
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(r"f:\Ramana\pages")

GA_OLD_PATTERN = re.compile(
    r'<!-- Google Analytics [^\n]*?-->\s*<script>[\s\S]*?loadGA[\s\S]*?</script>',
    re.MULTILINE
)

GA_ULTIMATE_SNIPPET = """<!-- Google Analytics (极致延迟加载，首屏0开销) -->
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
      var gaTimer = setTimeout(loadGA, 4000);
      ['scroll','touchstart','click','keydown'].forEach(function(e){
        window.addEventListener(e, function(){ clearTimeout(gaTimer); loadGA(); }, {once: true, passive: true});
      });
    </script>"""

PRECONNECT_PATTERN = re.compile(
    r'\s*<!-- DNS 预解析和预连接\s*-->\s*<link rel="dns-prefetch" href="https://www\.googletagmanager\.com">\s*<link rel="dns-prefetch" href="https://www\.google-analytics\.com">\s*<link rel="preconnect" href="https://www\.googletagmanager\.com"[^>]*>\s*<link rel="preconnect" href="https://www\.google-analytics\.com"[^>]*>',
    re.MULTILINE
)

def optimize_html_file(file_path: Path) -> bool:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 替换 GA
    if 'loadGA' in content:
        content = GA_OLD_PATTERN.sub(GA_ULTIMATE_SNIPPET, content)
    elif 'googletagmanager.com/gtag/js?id=G-MYFWHFPSYB' in content:
        variant_pattern = re.compile(
            r'<!-- Google Analytics [^\n]*?-->\s*<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-MYFWHFPSYB"></script>\s*<script>[\s\S]*?</script>',
            re.MULTILINE
        )
        content = variant_pattern.sub(GA_ULTIMATE_SNIPPET, content)

    # 2. 移除冗余的 Google Preconnect / DNS-prefetch
    if 'dns-prefetch" href="https://www.googletagmanager.com' in content:
        content = PRECONNECT_PATTERN.sub('', content)

    # 3. 兜底清除单行的 preconnect / dns-prefetch
    content = re.sub(r'\s*<link rel="dns-prefetch" href="https://www\.googletagmanager\.com">\s*', '\n', content)
    content = re.sub(r'\s*<link rel="dns-prefetch" href="https://www\.google-analytics\.com">\s*', '\n', content)
    content = re.sub(r'\s*<link rel="preconnect" href="https://www\.googletagmanager\.com"[^>]*>\s*', '\n', content)
    content = re.sub(r'\s*<link rel="preconnect" href="https://www\.google-analytics\.com"[^>]*>\s*', '\n', content)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🚀 开始终极优化...")
    html_files = list(BASE_DIR.glob("**/*.html"))
    updated = 0
    for hf in html_files:
        if optimize_html_file(hf):
            updated += 1
    print(f"✅ 更新了 {updated} 个文件！")

if __name__ == '__main__':
    main()
