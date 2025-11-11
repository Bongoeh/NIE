import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.utils import secure_filename
from flask import url_for
from datetime import datetime
import os

class FirebaseManager:
    def __init__(self, credentials_path):
        # Initialize Firebase app if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
        
        # Set up local upload folder
        self.upload_folder = 'static/uploads'
        os.makedirs(self.upload_folder, exist_ok=True)

    def get_announcements(self, limit=5):
        """Fetch recent announcements from Firestore."""
        db = firestore.client()
        try:
            # Try to order by timestamp
            announcements_ref = db.collection('announcements').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            announcements = []
            for doc in announcements_ref.stream():
                announcement_data = doc.to_dict()
                announcement_data['id'] = doc.id
                # Only include if timestamp exists and is not None
                if announcement_data.get('timestamp') is not None:
                    announcements.append(announcement_data)
            return announcements
        except Exception as e:
            print(f"[ERROR] Failed to fetch announcements with ordering: {e}")
            # Fallback: get all announcements without ordering
            announcements_ref = db.collection('announcements').limit(limit)
            announcements = []
            for doc in announcements_ref.stream():
                announcement_data = doc.to_dict()
                announcement_data['id'] = doc.id
                announcements.append(announcement_data)
            return announcements

    def get_settings(self):
        """Fetch website settings from Firestore."""
        db = firestore.client()
        settings_ref = db.collection('settings').document('default')
        settings_doc = settings_ref.get()
        return settings_doc.to_dict() if settings_doc.exists else {}

    def get_all_classes(self):
        """Fetch all classes from Firestore."""
        db = firestore.client()
        classes_ref = db.collection('classes')
        classes = []
        for doc in classes_ref.stream():
            class_data = doc.to_dict()
            class_data['id'] = doc.id
            classes.append(class_data)
        return classes

    def get_all_materials(self):
        """Fetch all study materials from Firestore."""
        db = firestore.client()
        materials_ref = db.collection('materials')
        materials = []
        for doc in materials_ref.stream():
            material_data = doc.to_dict()
            material_data['id'] = doc.id
            materials.append(material_data)
        return materials

    def get_all_camps(self):
        """Fetch all camps from Firestore."""
        db = firestore.client()
        camps_ref = db.collection('camps')
        camps = []
        for doc in camps_ref.stream():
            camp_data = doc.to_dict()
            camp_data['id'] = doc.id
            camps.append(camp_data)
        return camps

    def add_class(self, class_data):
        """Add a new class to Firestore."""
        db = firestore.client()
        classes_ref = db.collection('classes')
        classes_ref.add(class_data)

    def add_camp(self, camp_data):
        """Add a new camp to Firestore."""
        db = firestore.client()
        camps_ref = db.collection('camps')
        camps_ref.add(camp_data)

    def add_material(self, material_data, file):
        """Add a new study material to Firestore and save file locally."""
        db = firestore.client()

        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Add timestamp to avoid duplicate names
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        # Save file locally
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        
        # Create URL for the file
        file_url = url_for('static', filename=f'uploads/{filename}', _external=True)

        # Add material metadata to Firestore
        material_data['file_name'] = filename
        material_data['file_url'] = file_url
        material_data['uploaded_at'] = firestore.SERVER_TIMESTAMP
        materials_ref = db.collection('materials')
        materials_ref.add(material_data)

    def add_announcement(self, announcement_data):
        """Add a new announcement to Firestore."""
        db = firestore.client()
        # Use Python datetime for immediate availability
        announcement_data['timestamp'] = datetime.now()
        announcement_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        announcements_ref = db.collection('announcements')
        doc_ref = announcements_ref.add(announcement_data)
        print(f"[DEBUG] Announcement added with ID: {doc_ref[1].id}")
        return doc_ref

    def update_settings(self, settings_data):
        """Update website settings in Firestore."""
        db = firestore.client()
        settings_ref = db.collection('settings').document('default')
        settings_ref.set(settings_data, merge=True)

    def delete_class(self, class_id):
        """Delete a class from Firestore."""
        db = firestore.client()
        class_ref = db.collection('classes').document(class_id)
        print(f"Deleting class document with ID: {class_id}")
        class_ref.delete()

    def delete_camp(self, camp_id):
        """Delete a camp from Firestore."""
        db = firestore.client()
        camp_ref = db.collection('camps').document(camp_id)
        print(f"Deleting camp document with ID: {camp_id}")
        camp_ref.delete()

    def delete_material(self, material_id):
        """Delete a study material from Firestore and remove file."""
        db = firestore.client()
        
        # Get material data first
        material_ref = db.collection('materials').document(material_id)
        material_doc = material_ref.get()
        
        if material_doc.exists:
            material_data = material_doc.to_dict()
            
            # Delete the actual file if it exists
            if 'file_name' in material_data:
                file_path = os.path.join(self.upload_folder, material_data['file_name'])
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            
            # Delete from Firestore
            print(f"Deleting material document with ID: {material_id}")
            material_ref.delete()

    def delete_announcement(self, announcement_id):
        """Delete an announcement from Firestore."""
        db = firestore.client()
        announcement_ref = db.collection('announcements').document(announcement_id)
        print(f"Deleting announcement document with ID: {announcement_id}")
        announcement_ref.delete()