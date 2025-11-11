import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Secret key for Flask sessions (CHANGE THIS IN PRODUCTION!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Folder where uploaded files will be stored locally (optional, we use Firebase Storage)
    UPLOAD_FOLDER = 'static/uploads'
    
    # Maximum file upload size (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg'}
    
    # Admin login credentials
    # IMPORTANT: In production, set these in your .env file for security!
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'changeme123'
    
    # Path to your Firebase credentials JSON file
    FIREBASE_CREDENTIALS = 'firebase_config.json'
    
    # Firebase Storage bucket name
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET') or 'your-valid-bucket-name'