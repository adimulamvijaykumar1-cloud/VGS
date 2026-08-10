import sqlite3
import re

# 1. Update Database Schema & Data
db = sqlite3.connect('vgs_academy.db')
cursor = db.cursor()
cursor.execute('DROP TABLE IF EXISTS gallery')
db.execute('''
    CREATE TABLE IF NOT EXISTS gallery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_url TEXT NOT NULL,
        caption TEXT,
        category TEXT DEFAULT 'All',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

images = [
    ('https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?auto=format&fit=crop&q=80', 'Classroom Learning', 'Classroom'),
    ('https://images.unsplash.com/photo-1577896851231-70ef18881754?auto=format&fit=crop&q=80', 'Library & Study Area', 'Campus'),
    ('https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&q=80', 'Group Study Session', 'Students'),
    ('https://images.unsplash.com/photo-1588072432836-e10032774350?auto=format&fit=crop&q=80', 'Science Practical', 'Classroom'),
    ('https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?auto=format&fit=crop&q=80', 'Interactive Exam Prep', 'Classroom'),
    ('https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80', 'Graduation Success', 'Events')
]
cursor.executemany('INSERT INTO gallery (image_url, caption, category) VALUES (?, ?, ?)', images)
db.commit()
db.close()

# 2. Update app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()

app_py = app_py.replace('caption TEXT,', 'caption TEXT,\n                category TEXT DEFAULT \\'All\\',')
app_py = app_py.replace('''        caption = data.get('caption')
        if caption is None: caption = ''
        
        cursor.execute('INSERT INTO gallery (image_url, caption) VALUES (?, ?)', (image_url, caption))''', '''        caption = data.get('caption')
        if caption is None: caption = ''
        category = data.get('category', 'All')
        if not category: category = 'All'
        
        cursor.execute('INSERT INTO gallery (image_url, caption, category) VALUES (?, ?, ?)', (image_url, caption, category))''')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py)

print('Updated DB and app.py successfully')
