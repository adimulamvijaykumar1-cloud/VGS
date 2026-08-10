import os
import sqlite3
import re
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g
from flask_cors import CORS
from google.oauth2 import id_token
from google.auth.transport import requests

# Configure application
# Serve static files from the root directory ('.') to run the entire app under Flask
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='templates')

# Enable CORS for development (useful if frontend is opened directly via file://)
CORS(app, supports_credentials=True)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'vgs_academy_super_secret_key_13579')
DATABASE = os.environ.get('DATABASE_PATH', 'vgs_academy.db')
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'vgsadmin123')
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '638149794802-79bhlcut9ucie9cgtuq1g2jm8s0cveth.apps.googleusercontent.com')

# Database Helpers
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Enable dictionary-like row factory for JSON serialization
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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
                image_url TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        try:
            db.execute("ALTER TABLE courses ADD COLUMN image_url TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass


        # Create gallery categories table
        db.execute('''
            CREATE TABLE IF NOT EXISTS gallery_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # Create gallery table
        db.execute('''
            CREATE TABLE IF NOT EXISTS gallery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_url TEXT NOT NULL,
                caption TEXT,
                category TEXT DEFAULT 'All',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

# Initialize database on startup
init_db()

# --- HELPER FUNCTIONS ---
def is_authenticated():
    return session.get('logged_in') is True

# --- STATIC CONTENT ROUTES ---
@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/about.html')
def about():
    return app.send_static_file('about.html')

@app.route('/courses.html')
def courses():
    return app.send_static_file('courses.html')

@app.route('/gallery.html')
def gallery():
    return app.send_static_file('gallery.html')

@app.route('/contact.html')
def contact():
    return app.send_static_file('contact.html')

# --- API ENDPOINTS ---

# 1. POST Enquiry
@app.route('/api/enquiry', methods=['POST'])
def add_enquiry():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        class_name = data.get('class', '').strip()
        message = data.get('message', '').strip()
        
        # Validations
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        if not phone or not re.match(r'^\d{10}$', phone):
            return jsonify({'success': False, 'error': 'A valid 10-digit phone number is required'}), 400
        if not class_name:
            return jsonify({'success': False, 'error': 'Class selection is required'}), 400
            
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO enquiries (name, phone, class_name, message, status) VALUES (?, ?, ?, ?, ?)',
            (name, phone, class_name, message, 'pending')
        )
        db.commit()
        
        return jsonify({'success': True, 'message': 'Enquiry submitted successfully'}), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 2. Auth Endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No credentials provided'}), 400
        
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        return jsonify({'success': True, 'message': 'Logged in successfully'})
    else:
        return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/session', methods=['GET'])
def get_session():
    user = session.get('user')
    return jsonify({
        'authenticated': user is not None or is_authenticated(),
        'user': user
    })

@app.route('/api/auth/google-login', methods=['POST'])
def google_login():
    data = request.get_json()
    token = data.get('credential')
    
    if not token:
        return jsonify({'success': False, 'error': 'No token provided'}), 400
        
    try:
        # Verify the Google JWT token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        
        google_id = idinfo['sub']
        email = idinfo.get('email', '')
        name = idinfo.get('name', 'User')
        picture = idinfo.get('picture', '')
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id, name, email, picture FROM users WHERE google_id = ?", (google_id,))
        user = cursor.fetchone()
        
        if not user:
            # Create new user
            cursor.execute("INSERT INTO users (google_id, email, name, picture) VALUES (?, ?, ?, ?)",
                           (google_id, email, name, picture))
            db.commit()
            user_id = cursor.lastrowid
        else:
            # Update existing user profile picture/name just in case it changed
            cursor.execute("UPDATE users SET name = ?, picture = ? WHERE google_id = ?", (name, picture, google_id))
            db.commit()
            user_id = user['id']
            
        # Set session data
        session['user'] = {
            'id': user_id,
            'google_id': google_id,
            'name': name,
            'email': email,
            'picture': picture
        }
        
        return jsonify({'success': True, 'user': session['user']})
        
    except ValueError as e:
        # Invalid token
        return jsonify({'success': False, 'error': 'Invalid token: ' + str(e)}), 401

# 3. Admin Data APIs (Protected)
@app.route('/api/enquiries', methods=['GET'])
def get_enquiries():
    if not is_authenticated():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM enquiries ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        enquiries = []
        for row in rows:
            enquiries.append({
                'id': row['id'],
                'name': row['name'],
                'phone': row['phone'],
                'class': row['class_name'],
                'message': row['message'],
                'status': row['status'],
                'created_at': row['created_at']
            })
            
        return jsonify({'success': True, 'enquiries': enquiries})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
def get_users():
    if not is_authenticated():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            users.append({
                'id': row['id'],
                'name': row['name'],
                'email': row['email'],
                'picture': row['picture'],
                'created_at': row['created_at']
            })
            
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/enquiry/<int:enquiry_id>', methods=['PUT'])
def update_enquiry_status(enquiry_id):
    if not is_authenticated():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'success': False, 'error': 'Status field is required'}), 400
            
        status = data.get('status').strip()
        if status not in ['pending', 'contacted', 'archived']:
            return jsonify({'success': False, 'error': 'Invalid status value'}), 400
            
        db = get_db()
        cursor = db.cursor()
        
        # Check if exists
        cursor.execute('SELECT id FROM enquiries WHERE id = ?', (enquiry_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Enquiry not found'}), 404
            
        cursor.execute('UPDATE enquiries SET status = ? WHERE id = ?', (status, enquiry_id))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Status updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/enquiry/<int:enquiry_id>', methods=['DELETE'])
def delete_enquiry(enquiry_id):
    if not is_authenticated():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Check if exists
        cursor.execute('SELECT id FROM enquiries WHERE id = ?', (enquiry_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Enquiry not found'}), 404
            
        cursor.execute('DELETE FROM enquiries WHERE id = ?', (enquiry_id,))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Enquiry deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- VIEW ROUTES ---

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

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM gallery_categories ORDER BY id ASC')
        categories = [dict(row) for row in cursor.fetchall()]
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/categories', methods=['POST'])
def add_category():
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'error': 'Category name is required'}), 400
        
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO gallery_categories (name) VALUES (?)', (name,))
            db.commit()
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'error': 'Category already exists'}), 400
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    if not is_authenticated(): return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT name FROM gallery_categories WHERE id = ?', (cat_id,))
        cat = cursor.fetchone()
        if cat:
            cursor.execute('DELETE FROM gallery WHERE category = ?', (cat['name'],))
            cursor.execute('DELETE FROM gallery_categories WHERE id = ?', (cat_id,))
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
        
        image_url = data.get('image_url')
        if not image_url: return jsonify({'success': False, 'error': 'Image URL is required'}), 400
        
        caption = data.get('caption')
        if caption is None: caption = ''
        category = data.get('category', 'All')
        if not category: category = 'All'
        
        cursor.execute('INSERT INTO gallery (image_url, caption, category) VALUES (?, ?, ?)', (image_url, caption, category))
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

@app.route('/admin')
def admin_page():
    # Flask templates folder defaults to 'templates/'
    return render_template('admin.html')

if __name__ == '__main__':
    # Run server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
