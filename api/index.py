#!/usr/bin/env python
import sys
import os

print("[INIT] Starting imports...", file=sys.stderr, flush=True)

try:
    from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
    print("[INIT] Flask imported successfully", file=sys.stderr, flush=True)
except ImportError as e:
    print(f"[ERROR] Failed to import Flask: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

try:
    from functools import wraps
    import base64
    print("[INIT] Standard libraries imported", file=sys.stderr, flush=True)
except ImportError as e:
    print(f"[ERROR] Failed to import standard libraries: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Create Flask app with proper folder handling
try:
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    print(f"[INIT] Template dir: {template_dir}", file=sys.stderr, flush=True)
    print(f"[INIT] Static dir: {static_dir}", file=sys.stderr, flush=True)
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    print("[INIT] Flask app created successfully", file=sys.stderr, flush=True)
except Exception as e:
    print(f"[ERROR] Failed to create Flask app: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Configuration
try:
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin')
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    print("[INIT] Configuration loaded", file=sys.stderr, flush=True)
except Exception as e:
    print(f"[ERROR] Failed to load configuration: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Firebase lazy loader
_firebase_instance = None

def get_firebase():
    """Lazy Firebase initialization"""
    global _firebase_instance
    if _firebase_instance is None:
        try:
            creds_b64 = os.environ.get('FIREBASE_CREDENTIALS_BASE64')
            if creds_b64:
                print("[INIT] Firebase env var found", file=sys.stderr, flush=True)
                # Don't initialize yet - do it when actually needed
        except Exception as e:
            print(f"[WARN] Firebase setup error: {e}", file=sys.stderr, flush=True)
    return _firebase_instance

print("[INIT] App initialization complete", file=sys.stderr, flush=True)

# ============ DIAGNOSTIC ROUTES ============

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "App is running"}), 200

@app.route('/api/health')
def api_health():
    """API health check with diagnostics"""
    return jsonify({
        "status": "ok",
        "firebase_available": get_firebase() is not None,
        "templates_dir_exists": os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))),
        "static_dir_exists": os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static')))
    }), 200

# ============ PUBLIC ROUTES ============

@app.route('/')
def index():
    """Home page"""
    print("[ROUTE] index() called", file=sys.stderr, flush=True)
    try:
        # Check if templates directory exists
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'index.html')
        print(f"[ROUTE] Looking for template at: {template_path}", file=sys.stderr, flush=True)
        print(f"[ROUTE] Template exists: {os.path.exists(template_path)}", file=sys.stderr, flush=True)
        
        return render_template('index.html')
    except Exception as e:
        print(f"[ERROR] index() failed: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/calendar')
def calendar():
    """Classes calendar page"""
    print("[ROUTE] calendar() called", file=sys.stderr, flush=True)
    try:
        return render_template('calendar.html')
    except Exception as e:
        print(f"[ERROR] calendar() failed: {e}", file=sys.stderr, flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/materials')
def materials():
    """Study materials page"""
    print("[ROUTE] materials() called", file=sys.stderr, flush=True)
    try:
        return render_template('materials.html')
    except Exception as e:
        print(f"[ERROR] materials() failed: {e}", file=sys.stderr, flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/camps')
def camps():
    """Camps page"""
    print("[ROUTE] camps() called", file=sys.stderr, flush=True)
    try:
        return render_template('camps.html')
    except Exception as e:
        print(f"[ERROR] camps() failed: {e}", file=sys.stderr, flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/contact')
def contact():
    """Contact page"""
    print("[ROUTE] contact() called", file=sys.stderr, flush=True)
    try:
        return render_template('contact.html')
    except Exception as e:
        print(f"[ERROR] contact() failed: {e}", file=sys.stderr, flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/about')
def about():
    """About page"""
    print("[ROUTE] about() called", file=sys.stderr, flush=True)
    try:
        return render_template('about.html')
    except Exception as e:
        print(f"[ERROR] about() failed: {e}", file=sys.stderr, flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    print("[ROUTE] admin_login() called", file=sys.stderr, flush=True)
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('admin_dashboard'))
            else:
                return jsonify({"error": "Invalid credentials"}), 401
        
        return render_template('admin/login.html')
    except Exception as e:
        print(f"[ERROR] admin_login() failed: {e}", file=sys.stderr, flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    print("[ROUTE] admin_dashboard() called", file=sys.stderr, flush=True)
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        return render_template('admin/dashboard.html')
    except Exception as e:
        print(f"[ERROR] admin_dashboard() failed: {e}", file=sys.stderr, flush=True)
        return jsonify({"error": str(e)}), 500

print("[INIT] All routes registered", file=sys.stderr, flush=True)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    print(f"[ERROR] 404: {error}", file=sys.stderr, flush=True)
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    print(f"[ERROR] 500: {error}", file=sys.stderr, flush=True)
    return jsonify({"error": "Server error", "details": str(error)}), 500

if __name__ == '__main__':
    print("[MAIN] Starting Flask app...", file=sys.stderr, flush=True)
    app.run(debug=False)