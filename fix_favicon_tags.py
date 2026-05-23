import os
import re

def fix_favicon_tag(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match the pattern: whitespace followed by rel="icon" without <link
    pattern = r'^(\s*)rel="icon"(\s.*)$'
    replacement = r'\1<link rel="icon"\2'
    
    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
    
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed: {file_path}')
        return True
    return False

def main():
    pages_dir = '/workspace/pages'
    fixed_count = 0
    
    for root, dirs, files in os.walk(pages_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if fix_favicon_tag(file_path):
                    fixed_count += 1
    
    print(f'\nTotal fixed files: {fixed_count}')

if __name__ == '__main__':
    main()
