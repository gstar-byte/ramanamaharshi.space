#!/usr/bin/env python3
import re
import os

def minify_js(js):
    # 移除单行注释
    js = re.sub(r'//[^\n]*', '', js)
    # 移除多行注释
    js = re.sub(r'/\*[\s\S]*?\*/', '', js)
    # 移除多余空白
    js = re.sub(r'\s+', ' ', js)
    # 移除分号后的空格
    js = re.sub(r';\s*', ';', js)
    # 移除逗号后的空格
    js = re.sub(r',\s*', ',', js)
    # 移除大括号前后的空格
    js = re.sub(r'\s*{\s*', '{', js)
    js = re.sub(r'\s*}\s*', '}', js)
    # 移除小括号前后的空格
    js = re.sub(r'\s*\(\s*', '(', js)
    js = re.sub(r'\s*\)\s*', ')', js)
    # 移除冒号前后的空格（对象字面量）
    js = re.sub(r'\s*:\s*', ':', js)
    # 移除开头和结尾的空白
    js = js.strip()
    return js

def minify_file(filename):
    # 读取原始 JS
    with open(filename, 'r', encoding='utf-8') as f:
        original = f.read()
    
    # 压缩
    minified = minify_js(original)
    
    # 备份原始文件
    backup = filename + '.bak'
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(original)
    
    # 写入压缩后的 JS
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(minified)
    
    return {
        'filename': filename,
        'original': len(original),
        'minified': len(minified),
        'saved': len(original) - len(minified),
        'percent': (1 - len(minified)/len(original))*100
    }

# 需要压缩的 JS 文件
files = ['script.js', 'search.js', 'audio-reader.js', 'pwa-analytics.js']


total_original = 0
total_minified = 0

print('JS 压缩开始...\n')
for f in files:
    if os.path.exists(f):
        result = minify_file(f)
        print(f'{result["filename"]}:')
        print(f'  原始: {result["original"]:,} 字节')
        print(f'  压缩后: {result["minified"]:,} 字节')
        print(f'  节省: {result["saved"]:,} 字节 ({result["percent"]:.1f}%)\n')
        total_original += result['original']
        total_minified += result['minified']
    else:
        print(f'警告: {f} 不存在\n')

print('总计:')
print(f'  原始: {total_original:,} 字节')
print(f'  压缩后: {total_minified:,} 字节')
print(f'  节省: {total_original - total_minified:,} 字节 ({(1 - total_minified/total_original)*100:.1f}%)')
