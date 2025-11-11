from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import base64
from config import Config
from utils.firebase_utils import FirebaseManager

app = Flask(__name__)
app.config.from_object(Config)

# Handle Firebase credentials from base64 environment variable
# This is needed for Vercel deployment where the service account JSON
# cannot be committed to the repository
creds_b64 = os.environ.get('FIREBASE_CREDENTIALS_BASE64')
if creds_b64:
    try:
        creds_bytes = base64.b64decode(creds_b64)
        creds_path = app.config.get('FIREBASE_CREDENTIALS', 'firebase_config.json')
        with open(creds_path, 'wb') as f:
            f.write(creds_bytes)
        print(f"[INFO] Firebase credentials loaded from FIREBASE_CREDENTIALS_BASE64 env var")
    except Exception as e:
        print(f"[ERROR] Failed to decode FIREBASE_CREDENTIALS_BASE64: {e}")
        # Don't raise on Vercel - allow app to start even if Firebase isn't configured yet

# Initialize Firebase
try:
    firebase = FirebaseManager(app.config['FIREBASE_CREDENTIALS'])
    print("[INFO] Firebase initialized successfully")
except Exception as e:
    print(f"[ERROR] Firebase initialization failed: {e}")
    print("[WARNING] App will continue but Firebase-dependent features will fail")
    firebase = None


# Helper function to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ============ PUBLIC ROUTES ============

@app.route('/')
def index():
    """Home page with recent announcements"""
    announcements = firebase.get_announcements(limit=5)
    settings = firebase.get_settings()
    return render_template('index.html', announcements=announcements, settings=settings)

@app.route('/calendar')
def calendar():
    """Classes calendar page"""
    classes = firebase.get_all_classes()
    settings = firebase.get_settings()
    return render_template('calendar.html', classes=classes, settings=settings)

@app.route('/materials')
def materials():
    """Study materials page"""
    materials = firebase.get_all_materials()
    return render_template('materials.html', materials=materials)

@app.route('/camps')
def camps():
    """Camps and special events page"""
    try:
        camps = firebase.get_all_camps()  # Fetch camps from Firestore
        settings = firebase.get_settings()  # Fetch settings from Firestore
        return render_template('camps.html', camps=camps, settings=settings)
    except Exception as e:
        print(f"Error fetching camps: {e}")  # Debugging
        flash('Error loading camps. Please try again later.', 'danger')
        return redirect(url_for('index'))

@app.route('/contact')
def contact():
    """Contact page"""
    settings = firebase.get_settings()
    return render_template('contact.html', settings=settings)

@app.route('/about')
def about():
    """About Us page"""
    return render_template('about.html')

# ============ ADMIN ROUTES ============

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    classes = firebase.get_all_classes()
    camps = firebase.get_all_camps()
    materials = firebase.get_all_materials()
    announcements = firebase.get_announcements(limit=10)
    settings = firebase.get_settings()
    
    return render_template('admin/dashboard.html', 
                         classes=classes, 
                         camps=camps, 
                         materials=materials,
                         announcements=announcements,
                         settings=settings)

# ============ ADMIN API ROUTES ============

@app.route('/admin/api/add_class', methods=['POST'])
@login_required
def add_class():
    """Add a new class"""
    class_data = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'date': request.form.get('date'),
        'time': request.form.get('time'),
        'duration': request.form.get('duration'),
        'type': request.form.get('type', 'regular')
    }
    firebase.add_class(class_data)
    flash('Class added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/api/delete_class/<class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    """Delete a class"""
    if not class_id or class_id == 'None':
        flash('Invalid class ID', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    print(f"Attempting to delete class with ID: {class_id}")
    try:
        firebase.delete_class(class_id)
        flash('Class deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting class: {e}")
        flash(f'Error deleting class: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/api/add_camp', methods=['POST'])
@login_required
def add_camp():
    """Add a new camp"""
    camp_data = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date'),
        'location': request.form.get('location'),
        'price': request.form.get('price')
    }
    firebase.add_camp(camp_data)
    flash('Camp added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/api/delete_camp/<camp_id>', methods=['POST'])
@login_required
def delete_camp(camp_id):
    """Delete a camp"""
    if not camp_id or camp_id == 'None':
        flash('Invalid camp ID', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    print(f"Attempting to delete camp with ID: {camp_id}")
    try:
        firebase.delete_camp(camp_id)
        flash('Camp deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting camp: {e}")
        flash(f'Error deleting camp: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/api/add_announcement', methods=['POST'])
@login_required
def add_announcement():
    """Add a new announcement"""
    announcement_data = {
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'priority': request.form.get('priority', 'normal')
    }
    firebase.add_announcement(announcement_data)
    flash('Announcement added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/api/delete_announcement/<announcement_id>', methods=['POST'])
@login_required
def delete_announcement(announcement_id):
    """Delete an announcement"""
    if not announcement_id or announcement_id == 'None':
        flash('Invalid announcement ID', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        firebase.delete_announcement(announcement_id)
        flash('Announcement deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting announcement: {e}")
        flash(f'Error deleting announcement: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/upload_material', methods=['POST'])
@login_required
def upload_material():
    try:
        if 'file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(url_for('admin_dashboard'))
                
        file = request.files['file']
                
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('admin_dashboard'))
                
        # Prepare material data
        material_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'category': request.form.get('category', 'general'),
            'grade': request.form.get('grade')  # Add this line to get the grade
        }
                
        # Use FirebaseManager to add material
        firebase.add_material(material_data, file)
        flash('Material uploaded successfully!', 'success')
            
    except Exception as e:
        flash(f'Error uploading material: {str(e)}', 'danger')
        print(f"Upload error: {e}")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_material/<material_id>', methods=['POST'])
@login_required  # Add the decorator here instead of manual check
def delete_material(material_id):
    try:
        firebase.delete_material(material_id)  # Use 'firebase' not 'firebase_manager'
        flash('Material deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting material: {str(e)}', 'danger')
        print(f"Delete error: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/api/update_settings', methods=['POST'])
@login_required
def update_settings():
    """Update website settings"""
    settings_data = {
        'class_price': request.form.get('class_price'),
        'camp_price': request.form.get('camp_price'),
        'whatsapp_number': request.form.get('whatsapp_number'),
        'email': request.form.get('email'),
        'teacher_name': request.form.get('teacher_name'),
        'about': request.form.get('about')
    }
    firebase.update_settings(settings_data)
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print(f"Loaded Admin Username: {app.config['ADMIN_USERNAME']}")
    print(f"Loaded Admin Password: {app.config['ADMIN_PASSWORD']}")
    app.run(debug=True)