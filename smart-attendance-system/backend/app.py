"""
Smart Attendance System - Flask Backend
Main application server
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from pathlib import Path

# Import custom modules
from face_recognition_handler import FaceRecognitionHandler
from dataset_downloader import DatasetDownloader
from attendance_logger import AttendanceLogger

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "attendance_logs"

# Create necessary directories
for directory in [DATASETS_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Initialize handlers
face_handler = FaceRecognitionHandler(str(MODELS_DIR))
dataset_downloader = DatasetDownloader(str(DATASETS_DIR))
attendance_logger = AttendanceLogger(str(LOGS_DIR))

# ==================== API ROUTES ====================

@app.route('/', methods=['GET'])
def index():
    """Home route"""
    return jsonify({"status": "Smart Attendance System Running", "version": "1.0.0"})

# ==================== PERSON MANAGEMENT ====================

@app.route('/api/persons', methods=['GET'])
def get_persons():
    """Get all registered persons"""
    try:
        persons = face_handler.get_all_persons()
        return jsonify({"status": "success", "persons": persons})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/persons', methods=['POST'])
def add_person():
    """Add new person to system"""
    try:
        data = request.json
        person_name = data.get('name')
        
        if not person_name:
            return jsonify({"status": "error", "message": "Name is required"}), 400
        
        result = face_handler.add_person(person_name)
        return jsonify({"status": "success", "person_id": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/persons/<person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Delete a person"""
    try:
        face_handler.delete_person(person_id)
        return jsonify({"status": "success", "message": "Person deleted"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== IMAGE UPLOAD ====================

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Upload image for a person"""
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        
        file = request.files['file']
        person_id = request.form.get('person_id')
        
        if not person_id:
            return jsonify({"status": "error", "message": "Person ID required"}), 400
        
        result = face_handler.add_image_to_person(person_id, file)
        return jsonify({"status": "success", "message": "Image uploaded", "image_id": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== MODEL TRAINING ====================

@app.route('/api/train-model', methods=['POST'])
def train_model():
    """Train face recognition model"""
    try:
        result = face_handler.train_model()
        return jsonify({"status": "success", "message": "Model trained successfully", "stats": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/model-status', methods=['GET'])
def model_status():
    """Check if model is trained"""
    try:
        is_trained = face_handler.is_model_trained()
        stats = face_handler.get_model_stats()
        return jsonify({
            "status": "success",
            "is_trained": is_trained,
            "stats": stats
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== ATTENDANCE MARKING ====================

@app.route('/api/mark-attendance', methods=['POST'])
def mark_attendance():
    """Mark attendance from image or frame"""
    try:
        data = request.json
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({"status": "error", "message": "Image required"}), 400
        
        # Recognize face
        recognized_person = face_handler.recognize_face(image_base64)
        
        if recognized_person:
            # Log attendance
            log_entry = attendance_logger.log_attendance(recognized_person)
            return jsonify({
                "status": "success",
                "person": recognized_person,
                "timestamp": log_entry
            })
        else:
            return jsonify({
                "status": "warning",
                "message": "Face not recognized"
            }), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== ATTENDANCE LOGS ====================

@app.route('/api/attendance-logs', methods=['GET'])
def get_attendance_logs():
    """Get attendance logs"""
    try:
        date = request.args.get('date')
        person_id = request.args.get('person_id')
        
        logs = attendance_logger.get_logs(date=date, person_id=person_id)
        return jsonify({"status": "success", "logs": logs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/attendance-stats', methods=['GET'])
def get_attendance_stats():
    """Get attendance statistics"""
    try:
        stats = attendance_logger.get_statistics()
        return jsonify({"status": "success", "stats": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== DATASET MANAGEMENT ====================

@app.route('/api/datasets/available', methods=['GET'])
def get_available_datasets():
    """Get list of available datasets to download"""
    try:
        datasets = dataset_downloader.get_available_datasets()
        return jsonify({"status": "success", "datasets": datasets})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/datasets/download', methods=['POST'])
def download_dataset():
    """Download dataset"""
    try:
        data = request.json
        dataset_name = data.get('dataset_name')
        
        if not dataset_name:
            return jsonify({"status": "error", "message": "Dataset name required"}), 400
        
        result = dataset_downloader.download_dataset(dataset_name)
        return jsonify({"status": "success", "message": f"Downloaded {dataset_name}", "path": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/datasets/import-local', methods=['POST'])
def import_local_dataset():
    """Import local dataset"""
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        
        file = request.files['file']
        result = dataset_downloader.import_local_dataset(file)
        return jsonify({"status": "success", "message": "Dataset imported", "path": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== SETTINGS ====================

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get system settings"""
    try:
        settings = {
            "datasets_dir": str(DATASETS_DIR),
            "models_dir": str(MODELS_DIR),
            "logs_dir": str(LOGS_DIR),
            "camera_enabled": True
        }
        return jsonify({"status": "success", "settings": settings})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 50)
    print("Smart Attendance System - Backend Server")
    print("=" * 50)
    print(f"Datasets Directory: {DATASETS_DIR}")
    print(f"Models Directory: {MODELS_DIR}")
    print(f"Logs Directory: {LOGS_DIR}")
    print("=" * 50)
    print("Starting server at http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
