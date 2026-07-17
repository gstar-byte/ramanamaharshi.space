#!/usr/bin/env python3
"""
Fix hreflang links, zh-TW specific issues, and BreadcrumbList URLs.
Handles: P0 #1, #2, P1 #3, #4, #5, P2 #10, #11
"""
import os
import re
from pathlib import Path

PAGES_DIR = Path(r"f:\ramana\pages")
BASE_URL = "https://ramanamaharshi.space"

def get_page_urls(file_path):
    """Calculate zh-CN, zh-TW, and x-default URLs for a given file."""
    rel_path = file_path.relative_to(PAGES_DIR)
    parts = rel_path.parts
    
    # Check if this is a zh-TW page
    is_zh_tw = len(parts) > 1 and parts[0] == 'zh-TW'
    
    if is_zh_tw:
        # Remove 'zh-TW' prefix to get the zh-CN path
        cn_parts = parts[1:]
    else:
        cn_parts = parts
    
    # Build URL paths
    cn_path = '/' + '/'.join(cn_parts).replace('\\', '/')
    tw_path = '/zh-TW/' + '/'.join(cn_parts).replace('\\', '/')
    
    # Special case: index.html at root → /
    if cn_path == '/index.html':
        cn_path = '/'
    if tw_path == '/zh-TW/index.html':
        tw_path = '/zh-TW/'
    
    # For subdirectory index pages
    if cn_path.endswith('/index.html'):
        cn_path = cn_path[:-10]  # remove index.html, keep trailing /
        if not cn_path.endswith('/'):
            cn_path += '/'
    if tw_path.endswith('/index.html'):
        tw_path = tw_path[:-10]
        if not tw_path.endswith('/'):
            tw_path += '/'
    
    cn_url = f"{BASE_URL}{cn_path}"
    tw_url = f"{BASE_URL}{tw_path}"
    default_url = cn_url  # x-default points to zh-CN
    
    return cn_url, tw_url, default_url, is_zh_tw

def fix_hreflang(content, cn_url, tw_url, default_url):
    """Replace all hreflang links with correct URLs."""
    
    # Remove existing hreflang links (including x-default that was just added)
    content = re.sub(
        r'\s*<link\s+rel="alternate"\s+hreflang="[^"]*"\s+href="[^"]*">',
        '',
        content
    )
    
    # Build new hreflang block
    hreflang_block = (
        f'\n    <link rel="alternate" hreflang="zh-CN" href="{cn_url}">'
        f'\n    <link rel="alternate" hreflang="zh-TW" href="{tw_url}">'
        f'\n    <link rel="alternate" hreflang="x-default" href="{default_url}">'
    )
    
    # Insert before Twitter Card or before </head> if no Twitter Card
    twitter_match = re.search(r'\s*<!--\s*Twitter Card\s*-->', content)
    if twitter_match:
        content = content[:twitter_match.start()] + hreflang_block + content[twitter_match.start():]
    else:
        # Insert before </head>
        content = content.replace('</head>', hreflang_block + '\n</head>', 1)
    
    return content

def fix_zh_tw_canonical(content, is_zh_tw, file_path):
    """Fix zh-TW index canonical extra > and ensure correct canonical."""
    # Fix extra > on canonical
    content = re.sub(
        r'<link\s+rel="canonical"\s+href="([^"]*)">>',
        r'<link rel="canonical" href="\1">',
        content
    )
    return content

def fix_zh_tw_og_url(content, is_zh_tw, cn_url, tw_url):
    """Fix og:url for zh-TW pages to point to their own URL."""
    if is_zh_tw:
        # Replace og:url that points to wrong URL
        content = re.sub(
            r'<meta\s+property="og:url"\s+content="[^"]*">',
            f'<meta property="og:url" content="{tw_url}">',
            content
        )
    return content

def fix_breadcrumb_zh_tw(content, is_zh_tw, file_path):
    """Fix BreadcrumbList URLs in zh-TW pages to point to zh-TW versions."""
    if not is_zh_tw:
        return content
    
    # Replace breadcrumb item URLs: replace ramanamaharshi.space/ with ramanamaharshi.space/zh-TW/
    # But only in BreadcrumbList JSON-LD blocks
    def fix_breadcrumb_block(match):
        block = match.group(0)
        # Replace all "item": "https://ramanamaharshi.space/..." with zh-TW version
        # But keep the homepage breadcrumb as is (or point to zh-TW homepage)
        def fix_item(m):
            url = m.group(1)
            # Don't add zh-TW prefix if already has it
            if '/zh-TW/' in url:
                return m.group(0)
            # Replace https://ramanamaharshi.space/ with https://ramanamaharshi.space/zh-TW/
            if url == f'{BASE_URL}/':
                new_url = f'{BASE_URL}/zh-TW/'
            else:
                new_url = url.replace(f'{BASE_URL}/', f'{BASE_URL}/zh-TW/')
            return f'"item": "{new_url}"'
        
        block = re.sub(r'"item":\s*"(https://ramanamaharshi\.space/[^"]*)"', fix_item, block)
        return block
    
    # Match BreadcrumbList JSON-LD blocks
    content = re.sub(
        r'\{[^}]*"@type":\s*"BreadcrumbList"[^}]*\}',
        fix_breadcrumb_block,
        content,
        flags=re.DOTALL
    )
    return content

def fix_zh_tw_qa_broken_html(content, is_zh_tw, file_path):
    """Fix broken HTML in zh-TW QA pages: title duplication and broken link tag."""
    if not is_zh_tw:
        return content
    
    # Check if this is a QA page
    if 'qa' not in str(file_path).replace('\\', '/').lower():
        return content
    
    # Fix: <title>...拉玛那馬哈希150精選問答  | 拉玛那馬哈希150精選問答 | 拉玛那馬哈希</title>
    # → <title>...| 拉玛那馬哈希</title>
    content = re.sub(
        r'(拉玛那馬哈希150精選問答)\s*\|\s*\1',
        r'\1',
        content
    )
    
    # Fix broken: <link rel=</title>
    # This happens when the preload link got mangled into the title
    content = content.replace('<link rel=</title>', '</title>')
    
    # Also fix the pattern where title content leaks into link tag
    # Pattern: <title>...</title>\n    <!-- ... -->\n<link rel=</title>
    # The real fix: the </title> after <link rel= is spurious
    # Let's check for any remaining <link rel=</title> patterns
    content = re.sub(r'<link\s+rel=</title>', '', content)
    
    return content

def fix_zh_tw_qa_og_title(content, is_zh_tw, file_path):
    """Fix og:title duplication in zh-TW QA pages."""
    if not is_zh_tw:
        return content
    
    if 'qa' not in str(file_path).replace('\\', '/').lower():
        return content
    
    # Fix: og:title with duplicated text
    content = re.sub(
        r'(<meta\s+property="og:title"\s+content="[^"]*?)\s*\|\s*拉玛那馬哈希150精選問答\s*\|\s*拉玛那馬哈希150精選問答\s*\|\s*',
        r'\1 | ',
        content
    )
    # Also handle the pattern without the trailing |
    content = re.sub(
        r'(拉玛那馬哈希150精選問答)\s*\|\s*\1',
        r'\1',
        content
    )
    
    return content

# Simplified → Traditional Chinese character mapping for common characters
# found in zh-TW pages
SIMPLE_TO_TRAD = {
    '页': '頁', '与': '與', '边': '邊', '个': '個', '们': '們',
    '这': '這', '那': '那', '为': '為', '么': '麼', '只': '只',
    '后': '後', '里': '裡', '发': '發', '关': '關', '问': '問',
    '间': '間', '东': '東', '两': '兩', '应': '應', '来': '來',
    '见': '見', '说': '說', '过': '過', '还': '還', '从': '從',
    '当': '當', '处': '處', '学': '學', '门': '門', '动': '動',
    '点': '點', '让': '讓', '认': '認', '记': '記', '难': '難',
    '体': '體', '经': '經', '进': '進', '远': '遠', '实': '實',
    '导': '導', '专': '專', '业': '業', '产': '產', '会': '會',
    '习': '習', '区': '區', '历': '歷', '旧': '舊', '简': '簡',
    '繁': '繁', '类': '類', '别': '別', '读': '讀', '续': '續',
    '关': '關', '开': '開', '写': '寫', '寻': '尋', '尽': '盡',
    '层': '層', '获': '獲', '归': '歸', '达': '達', '观': '觀',
    '识': '識', '论': '論', '证': '證', '觉': '覺', '语': '語',
    '话': '話', '词': '詞', '试': '試', '诚': '誠', '详': '詳',
    '误': '誤', '说': '說', '请': '請', '谁': '誰', '亚': '亞',
    '亲': '親', '亿': '億', '仅': '僅', '从': '從', '仅': '僅',
    '仆': '僕', '仇': '仇', '仍': '仍', '付': '付', '代': '代',
    '件': '件', '价': '價', '众': '眾', '优': '優', '会': '會',
    '传': '傳', '伤': '傷', '伦': '倫', '伪': '偽', '伫': '佇',
    '体': '體', '余': '餘', '佣': '傭', '侠': '俠', '侧': '側',
    '侦': '偵', '债': '債', '倾': '傾', '偿': '償', '储': '儲',
    '催': '催', '像': '像', '僵': '僵', '儿': '兒', '兑': '兌',
    '兰': '蘭', '关': '關', '兴': '興', '养': '養', '内': '內',
    '册': '冊', '军': '軍', '农': '農', '冯': '馮', '冲': '衝',
    '况': '況', '净': '淨', '凉': '涼', '减': '減', '凿': '鑿',
    '刘': '劉', '则': '則', '刚': '剛', '创': '創', '删': '刪',
    '别': '別', '刮': '刮', '到': '到', '剑': '劍', '剂': '劑',
    '办': '辦', '劝': '勸', '功': '功', '动': '動', '务': '務',
    '劣': '劣', '劲': '勁', '势': '勢', '勇': '勇', '勋': '勳',
    '匀': '勻', '区': '區', '医': '醫', '华': '華', '单': '單',
    '卖': '賣', '南': '南', '博': '博', '占': '佔', '卡': '卡',
    '卷': '卷', '却': '卻', '厂': '廠', '厅': '廳', '历': '歷',
    '厉': '厲', '压': '壓', '厌': '厭', '去': '去', '参': '參',
    '又': '又', '双': '雙', '变': '變', '口': '口', '只': '只',
    '叫': '叫', '可': '可', '台': '台', '号': '號', '叶': '葉',
    '响': '響', '备': '備', '复': '復', '够': '夠', '处': '處',
    '外': '外', '多': '多', '大': '大', '天': '天', '太': '太',
    '奇': '奇', '奖': '獎', '奋': '奮', '奥': '奧', '妆': '妝',
    '妇': '婦', '妈': '媽', '妩': '嫵', '姗': '姍', '娆': '嬈',
    '婴': '嬰', '嫔': '嬪', '嬷': '嬤', '孙': '孫', '学': '學',
    '宁': '寧', '宝': '寶', '实': '實', '审': '審', '宪': '憲',
    '宫': '宮', '宾': '賓', '密': '密', '寻': '尋', '将': '將',
    '尝': '嘗', '己': '己', '帐': '帳', '库': '庫', '应': '應',
    '废': '廢', '异': '異', '弃': '棄', '张': '張', '录': '錄',
    '怀': '懷', '态': '態', '怜': '憐', '总': '總', '恢': '恢',
    '息': '息', '悦': '悅', '情': '情', '惯': '慣', '愿': '願',
    '慎': '慎', '慢': '慢', '慧': '慧', '懂': '懂', '懒': '懶',
    '戏': '戲', '护': '護', '报': '報', '担': '擔', '拟': '擬',
    '拥': '擁', '拦': '攔', '拨': '撥', '择': '擇', '挂': '掛',
    '挟': '挾', '挣': '掙', '捐': '捐', '捞': '撈', '损': '損',
    '换': '換', '据': '據', '掌': '掌', '排': '排', '探': '探',
    '接': '接', '揽': '攬', '搪': '搪', '搜': '搜', '据': '據',
    '拥': '擁', '播': '播', '摄': '攝', '摆': '擺', '摇': '搖',
    '摊': '攤', '撑': '撐', '撞': '撞', '撵': '攆', '攀': '攀',
    '攒': '攢', '敛': '斂', '断': '斷', '新': '新', '旧': '舊',
    '时': '時', '旷': '曠', '昼': '晝', '显': '顯', '晓': '曉',
    '晖': '暉', '暂': '暫', '暴': '暴', '曲': '曲', '书': '書',
    '最': '最', '有': '有', '朝': '朝', '期': '期', '术': '術',
    '机': '機', '杀': '殺', '杂': '雜', '权': '權', '树': '樹',
    '条': '條', '来': '來', '杨': '楊', '极': '極', '构': '構',
    '枫': '楓', '枢': '樞', '机': '機', '枚': '枚', '果': '果',
    '枝': '枝', '查': '查', '标': '標', '栋': '棟', '样': '樣',
    '根': '根', '格': '格', '桂': '桂', '桃': '桃', '案': '案',
    '桌': '桌', '梁': '梁', '梅': '梅', '梦': '夢', '检': '檢',
    '楼': '樓', '欢': '歡', '欧': '歐', '止': '止', '正': '正',
    '此': '此', '步': '步', '武': '武', '岁': '歲', '归': '歸',
    '死': '死', '殊': '殊', '残': '殘', '殿': '殿', '毕': '畢',
    '氏': '氏', '气': '氣', '污': '污', '沟': '溝', '浅': '淺',
    '温': '溫', '满': '滿', '渐': '漸', '灭': '滅', '灵': '靈',
    '烦': '煩', '焰': '焰', '煤': '煤', '照': '照', '献': '獻',
    '猎': '獵', '猪': '豬', '猫': '貓', '玩': '玩', '环': '環',
    '画': '畫', '疯': '瘋', '白': '白', '百': '百', '的': '的',
    '皆': '皆', '皇': '皇', '盖': '蓋', '盘': '盤', '省': '省',
    '看': '看', '真': '真', '眼': '眼', '着': '著', '离': '離',
    '种': '種', '积': '積', '称': '稱', '移': '移', '稀': '稀',
    '穷': '窮', '签': '簽', '简': '簡', '类': '類', '级': '級',
    '纯': '純', '纪': '紀', '约': '約', '纯': '純', '纵': '縱',
    '纷': '紛', '纸': '紙', '细': '細', '终': '終', '组': '組',
    '结': '結', '绝': '絕', '统': '統', '继': '繼', '绪': '緒',
    '练': '練', '纪': '紀', '维': '維', '绿': '綠', '编': '編',
    '缘': '緣', '网': '網', '罗': '羅', '罚': '罰', '罢': '罷',
    '罗': '羅', '罪': '罪', '置': '置', '羡': '羨', '群': '群',
    '羽': '羽', '翁': '翁', '而': '而', '耗': '耗', '闻': '聞',
    '联': '聯', '聪': '聰', '肉': '肉', '肃': '肅', '胆': '膽',
    '背': '背', '胜': '勝', '脑': '腦', '脚': '腳', '脱': '脫',
    '脸': '臉', '腊': '臘', '节': '節', '范': '範', '茧': '繭',
    '获': '獲', '蓝': '藍', '藏': '藏', '虑': '慮', '蛇': '蛇',
    '蛋': '蛋', '术': '術', '补': '補', '装': '裝', '里': '裡',
    '览': '覽', '觉': '覺', '观': '觀', '触': '觸', '记': '記',
    '讨': '討', '让': '讓', '议': '議', '论': '論', '设': '設',
    '访': '訪', '诀': '訣', '证': '證', '评': '評', '识': '識',
    '诊': '診', '试': '試', '诗': '詩', '话': '話', '该': '該',
    '详': '詳', '误': '誤', '诵': '誦', '语': '語', '认': '認',
    '谢': '謝', '谱': '譜', '谷': '谷', '豆': '豆', '象': '象',
    '贵': '貴', '赢': '贏', '赞': '贊', '趋': '趨', '踪': '蹤',
    '身': '身', '车': '車', '软': '軟', '轻': '輕', '辉': '輝',
    '辑': '輯', '输': '輸', '辞': '辭', '边': '邊', '达': '達',
    '过': '過', '运': '運', '近': '近', '还': '還', '进': '進',
    '远': '遠', '适': '適', '选': '選', '逊': '遜', '递': '遞',
    '遗': '遺', '邓': '鄧', '邮': '郵', '邻': '鄰', '配': '配',
    '酒': '酒', '酱': '醬', '释': '釋', '采': '採', '里': '裡',
    '量': '量', '金': '金', '针': '針', '铃': '鈴', '铁': '鐵',
    '银': '銀', '锁': '鎖', '镇': '鎮', '镜': '鏡', '长': '長',
    '门': '門', '闭': '閉', '开': '開', '间': '間', '阅': '閱',
    '队': '隊', '阳': '陽', '阴': '陰', '阶': '階', '阻': '阻',
    '附': '附', '陆': '陸', '陈': '陳', '险': '險', '随': '隨',
    '隐': '隱', '难': '難', '雾': '霧', '静': '靜', '项': '項',
    '预': '預', '领': '領', '头': '頭', '颊': '頰', '频': '頻',
    '颜': '顏', '风': '風', '饱': '飽', '饭': '飯', '饮': '飲',
    '骑': '騎', '惊': '驚', '验': '驗', '骤': '驟', '鲜': '鮮',
    '鸟': '鳥', '鸡': '雞', '鸣': '鳴', '鸭': '鴨', '鸿': '鴻',
    '鹤': '鶴', '黄': '黃', '黑': '黑', '默': '默', '齐': '齊',
    '齿': '齒', '龙': '龍', '龟': '龜', '源': '源', '涌': '湧',
}

def fix_zh_tw_chars(content, is_zh_tw):
    """Convert simplified Chinese characters to traditional in zh-TW pages."""
    if not is_zh_tw:
        return content
    
    # Only convert in text content, not in URLs or code
    # We'll be conservative and convert in specific areas:
    # 1. meta description content
    # 2. meta keywords content  
    # 3. title text
    # 4. og:title, og:description content
    # 5. twitter:title, twitter:description content
    # 6. Visible text in body
    
    # For meta tags, convert within content attributes
    def convert_text(text):
        for simp, trad in SIMPLE_TO_TRAD.items():
            text = text.replace(simp, trad)
        return text
    
    # Convert meta description
    def replace_desc(m):
        return f'<meta name="description" content="{convert_text(m.group(1))}">'
    content = re.sub(r'<meta\s+name="description"\s+content="([^"]*)">', replace_desc, content)
    
    # Convert og:description
    def replace_og_desc(m):
        return f'<meta property="og:description" content="{convert_text(m.group(1))}">'
    content = re.sub(r'<meta\s+property="og:description"\s+content="([^"]*)">', replace_og_desc, content)
    
    # Convert og:title
    def replace_og_title(m):
        return f'<meta property="og:title" content="{convert_text(m.group(1))}">'
    content = re.sub(r'<meta\s+property="og:title"\s+content="([^"]*)">', replace_og_title, content)
    
    # Convert twitter:title
    def replace_tw_title(m):
        return f'<meta name="twitter:title" content="{convert_text(m.group(1))}">'
    content = re.sub(r'<meta\s+name="twitter:title"\s+content="([^"]*)">', replace_tw_title, content)
    
    # Convert twitter:description
    def replace_tw_desc(m):
        return f'<meta name="twitter:description" content="{convert_text(m.group(1))}">'
    content = re.sub(r'<meta\s+name="twitter:description"\s+content="([^"]*)">', replace_tw_desc, content)
    
    # Convert keywords
    def replace_kw(m):
        return f'<meta name="keywords" content="{convert_text(m.group(1))}">'
    content = re.sub(r'<meta\s+name="keywords"\s+content="([^"]*)">', replace_kw, content)
    
    # Convert title tag content
    def replace_title(m):
        return f'<title>{convert_text(m.group(1))}</title>'
    content = re.sub(r'<title>([^<]*)</title>', replace_title, content)
    
    return content

def process_files():
    html_files = list(PAGES_DIR.rglob("*.html"))
    fixed_count = 0
    
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding='utf-8')
            original = content
            
            cn_url, tw_url, default_url, is_zh_tw = get_page_urls(html_file)
            
            # P0 #1: Fix hreflang
            content = fix_hreflang(content, cn_url, tw_url, default_url)
            
            # P1 #3: Fix zh-TW canonical extra >
            content = fix_zh_tw_canonical(content, is_zh_tw, html_file)
            
            # P1 #4: Fix zh-TW og:url
            content = fix_zh_tw_og_url(content, is_zh_tw, cn_url, tw_url)
            
            # P1 #5: Fix zh-TW BreadcrumbList URLs
            content = fix_breadcrumb_zh_tw(content, is_zh_tw, html_file)
            
            # P0 #2: Fix zh-TW QA broken HTML
            content = fix_zh_tw_qa_broken_html(content, is_zh_tw, html_file)
            
            # P2 #11: Fix zh-TW QA og:title duplication
            content = fix_zh_tw_qa_og_title(content, is_zh_tw, html_file)
            
            # P2 #10: Fix zh-TW simplified/traditional mixing
            content = fix_zh_tw_chars(content, is_zh_tw)
            
            if content != original:
                html_file.write_text(content, encoding='utf-8')
                fixed_count += 1
        except Exception as e:
            print(f"  ERROR processing {html_file}: {e}")
    
    print(f"  Fixed {fixed_count} files (hreflang, zh-TW canonical/og:url/breadcrumb/QA/chars)")
    return fixed_count

if __name__ == '__main__':
    print("=== Fix 2: hreflang, zh-TW specific issues ===")
    process_files()
    print("Done!")
