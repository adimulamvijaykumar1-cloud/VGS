import sqlite3
import re

# 1. Update database schema directly
db = sqlite3.connect('vgs_academy.db')
try:
    db.execute("ALTER TABLE courses ADD COLUMN image_url TEXT DEFAULT ''")
    db.commit()
    print("Added image_url column to courses table.")
except sqlite3.OperationalError as e:
    print("Column might already exist or error:", e)
db.close()


# 2. Update app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()

# Update init_db to include image_url
app_py = app_py.replace('''
        # Create courses table
        db.execute(\'\'\'
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subtitle TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                bullets TEXT NOT NULL,
                badge_num TEXT NOT NULL,
                badge_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \'\'\')''', '''
        # Create courses table
        db.execute(\'\'\'
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subtitle TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                bullets TEXT NOT NULL,
                badge_num TEXT NOT NULL,
                badge_text TEXT NOT NULL,
                image_url TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \'\'\')
        try:
            db.execute("ALTER TABLE courses ADD COLUMN image_url TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
''')


# Update POST /api/admin/courses
old_post = """
@app.route('/api/admin/courses', methods=['POST'])
def add_course():
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        
        # Replace None with empty string to satisfy NOT NULL constraints if user cancels prompts
        def s(val): return val if val is not None else ''
        
        cursor.execute('INSERT INTO courses (title, subtitle, description, icon, bullets, badge_num, badge_text) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                       (s(data.get('title')), s(data.get('subtitle')), s(data.get('description')), s(data.get('icon', 'fa-solid fa-book')), s(data.get('bullets')), s(data.get('badge_num')), s(data.get('badge_text'))))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
"""

new_post_and_put = """
@app.route('/api/admin/courses', methods=['POST'])
def add_course():
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        
        def s(val): return val if val is not None else ''
        
        cursor.execute('INSERT INTO courses (title, subtitle, description, icon, bullets, badge_num, badge_text, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                       (s(data.get('title')), s(data.get('subtitle')), s(data.get('description')), s(data.get('icon', 'fa-solid fa-book')), s(data.get('bullets')), s(data.get('badge_num')), s(data.get('badge_text')), s(data.get('image_url'))))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/courses/<int:course_id>', methods=['PUT'])
def edit_course(course_id):
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        
        def s(val): return val if val is not None else ''
        
        cursor.execute('''
            UPDATE courses 
            SET title = ?, subtitle = ?, description = ?, icon = ?, bullets = ?, badge_num = ?, badge_text = ?, image_url = ?
            WHERE id = ?
        ''', (s(data.get('title')), s(data.get('subtitle')), s(data.get('description')), s(data.get('icon', 'fa-solid fa-book')), s(data.get('bullets')), s(data.get('badge_num')), s(data.get('badge_text')), s(data.get('image_url')), course_id))
        
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
"""

app_py = app_py.replace(old_post.strip(), new_post_and_put.strip())

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py)

print("Updated app.py successfully.")
