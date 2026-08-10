import glob

html_files = glob.glob('*.html')

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'https://accounts.google.com/gsi/client' not in content:
        content = content.replace('</head>', '<script src="https://accounts.google.com/gsi/client" async></script>\n</head>')

    content = content.replace('>Enroll Now</a>', '><i class="fa-solid fa-graduation-cap" style="margin-right: 5px;"></i>Enroll Now</a>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Updated HTML files.')
