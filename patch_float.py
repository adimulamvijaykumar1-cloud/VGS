import glob

html_files = glob.glob('*.html')
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace double class
    content = content.replace('class="cms-phone" class="float-btn call"', 'class="cms-phone float-btn call"')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
print('Fixed HTML files')
