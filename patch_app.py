import re

with open('app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()

# 1. Update init_db()
init_db_replacement = """
def init_db():
    with app.app_context():
        db = get_db()
        # Create enquiries table
        db.execute('''
            CREATE TABLE IF NOT EXISTS enquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                class_name TEXT NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create users table for Google profiles
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create site_settings table
        db.execute('''
            CREATE TABLE IF NOT EXISTS site_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        # Initialize default settings if empty
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM site_settings')
        if cursor.fetchone()['count'] == 0:
            default_settings = [
                ('phone', '9963736363'),
                ('instagram', 'https://instagram.com/vgsacademyofficial'),
                ('location', 'Jammi Chettu Veedhi, Near Sloka School, Vempalli'),
                ('nav_icon', 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2222%22 fill=%22%230B1F4D%22/><text x=%2250%22 y=%2266%22 font-size=%2244%22 fill=%22%23D4AF37%22 text-anchor=%22middle%22 font-family=%22serif%22>V</text></svg>')
            ]
            cursor.executemany('INSERT INTO site_settings (key, value) VALUES (?, ?)', default_settings)

        # Create courses table
        db.execute('''
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
        ''')

        # Create gallery table
        db.execute('''
            CREATE TABLE IF NOT EXISTS gallery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_url TEXT NOT NULL,
                caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()
"""

app_py = re.sub(r'def init_db\(\):.*?db\.commit\(\)', init_db_replacement.strip(), app_py, flags=re.DOTALL)

# 2. Add API endpoints for CMS
cms_endpoints = """
# --- CMS ENDPOINTS ---
@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM site_settings')
        settings = {row['key']: row['value'] for row in cursor.fetchall()}
        return jsonify({'success': True, 'settings': settings})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/settings', methods=['POST'])
def update_settings():
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        for key, value in data.items():
            cursor.execute('INSERT INTO site_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, value))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM courses ORDER BY id ASC')
        courses = [dict(row) for row in cursor.fetchall()]
        return jsonify({'success': True, 'courses': courses})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/courses', methods=['POST'])
def add_course():
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO courses (title, subtitle, description, icon, bullets, badge_num, badge_text) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                       (data['title'], data['subtitle'], data['description'], data['icon'], data['bullets'], data['badge_num'], data['badge_text']))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        db = get_db()
        db.cursor().execute('DELETE FROM courses WHERE id = ?', (course_id,))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gallery', methods=['GET'])
def get_gallery():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM gallery ORDER BY created_at DESC')
        images = [dict(row) for row in cursor.fetchall()]
        return jsonify({'success': True, 'images': images})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/gallery', methods=['POST'])
def add_gallery_image():
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO gallery (image_url, caption) VALUES (?, ?)', (data['image_url'], data.get('caption', '')))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/gallery/<int:image_id>', methods=['DELETE'])
def delete_gallery_image(image_id):
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        db = get_db()
        db.cursor().execute('DELETE FROM gallery WHERE id = ?', (image_id,))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
"""

app_py = app_py.replace("@app.route('/admin')", cms_endpoints + "\n@app.route('/admin')")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py)

print('Updated app.py successfully')
