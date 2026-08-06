import os
import sqlite3
import re
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g
from flask_cors import CORS

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
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/session', methods=['GET'])
def get_session():
    return jsonify({'authenticated': is_authenticated()})

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
@app.route('/admin')
def admin_page():
    # Flask templates folder defaults to 'templates/'
    return render_template('admin.html')

if __name__ == '__main__':
    # Run server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
