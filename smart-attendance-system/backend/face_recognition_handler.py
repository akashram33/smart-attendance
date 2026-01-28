"""
Face Recognition Handler
Handles face detection, encoding, and recognition
"""

import cv2
import numpy as np
import os
import json
import pickle
import base64
from pathlib import Path
from PIL import Image
from io import BytesIO

# Try to import face_recognition, fallback to OpenCV-only mode
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Note: face_recognition not available. Using OpenCV face detection only.")

class FaceRecognitionHandler:
    def __init__(self, models_dir):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.persons_file = self.models_dir / "persons.json"
        self.encodings_file = self.models_dir / "encodings.pkl"
        self.persons_data = self._load_persons_data()
        self.known_encodings = []
        self.known_names = []
        self._load_encodings()
        
        # Load OpenCV face detector cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def _load_persons_data(self):
        """Load persons data from file"""
        if self.persons_file.exists():
            with open(self.persons_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_persons_data(self):
        """Save persons data to file"""
        with open(self.persons_file, 'w') as f:
            json.dump(self.persons_data, f, indent=2)
    
    def _load_encodings(self):
        """Load face encodings"""
        if self.encodings_file.exists():
            with open(self.encodings_file, 'rb') as f:
                data = pickle.load(f)
                self.known_encodings = data.get('encodings', [])
                self.known_names = data.get('names', [])
    
    def _save_encodings(self):
        """Save face encodings"""
        data = {
            'encodings': self.known_encodings,
            'names': self.known_names
        }
        with open(self.encodings_file, 'wb') as f:
            pickle.dump(data, f)
    
    def add_person(self, name):
        """Add new person"""
        person_id = f"person_{len(self.persons_data) + 1}"
        self.persons_data[person_id] = {
            "name": name,
            "images": [],
            "encodings": []
        }
        self._save_persons_data()
        return person_id
    
    def get_all_persons(self):
        """Get all registered persons"""
        persons = []
        for person_id, data in self.persons_data.items():
            persons.append({
                "id": person_id,
                "name": data["name"],
                "image_count": len(data.get("images", []))
            })
        return persons
    
    def delete_person(self, person_id):
        """Delete a person"""
        if person_id in self.persons_data:
            del self.persons_data[person_id]
            self._save_persons_data()
            # Retrain model
            self.train_model()
    
    def add_image_to_person(self, person_id, image_file):
        """Add image to person"""
        if person_id not in self.persons_data:
            raise ValueError(f"Person {person_id} not found")
        
        # Save image
        image_id = f"img_{len(self.persons_data[person_id]['images']) + 1}"
        image_path = self.models_dir / person_id / f"{image_id}.jpg"
        image_path.parent.mkdir(exist_ok=True)
        
        image_file.save(str(image_path))
        
        # Extract encoding
        if FACE_RECOGNITION_AVAILABLE:
            try:
                image = face_recognition.load_image_file(str(image_path))
                face_encodings = face_recognition.face_encodings(image)
                
                if face_encodings:
                    encoding = face_encodings[0].tolist()
                    self.persons_data[person_id]['encodings'].append(encoding)
                    self.persons_data[person_id]['images'].append(str(image_path))
                    self._save_persons_data()
                    return image_id
                else:
                    # Delete image if no face found
                    image_path.unlink()
                    raise ValueError("No face detected in image")
            except Exception as e:
                image_path.unlink()
                raise ValueError(f"Error processing image: {str(e)}")
        else:
            # Fallback to OpenCV detection
            img = cv2.imread(str(image_path))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                # Use histogram as simple encoding
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                encoding = cv2.normalize(hist, hist).flatten().tolist()
                self.persons_data[person_id]['encodings'].append(encoding)
                self.persons_data[person_id]['images'].append(str(image_path))
                self._save_persons_data()
                return image_id
            else:
                image_path.unlink()
                raise ValueError("No face detected in image")
    
    def train_model(self):
        """Train face recognition model"""
        self.known_encodings = []
        self.known_names = []
        
        face_count = 0
        for person_id, data in self.persons_data.items():
            if data['encodings']:
                for encoding in data['encodings']:
                    self.known_encodings.append(encoding)
                    self.known_names.append(data['name'])
                    face_count += 1
        
        self._save_encodings()
        
        return {
            "faces_encoded": face_count,
            "persons": len(self.persons_data),
            "status": "trained"
        }
    
    def is_model_trained(self):
        """Check if model is trained"""
        return len(self.known_encodings) > 0
    
    def get_model_stats(self):
        """Get model statistics"""
        return {
            "total_persons": len(self.persons_data),
            "total_encoded_faces": len(self.known_encodings),
            "persons_trained": sum(1 for p in self.persons_data.values() if p['encodings'])
        }
    
    def recognize_face(self, image_base64):
        """Recognize face from base64 image"""
        if not self.is_model_trained():
            raise ValueError("Model not trained yet")
        
        # Decode base64 image
        image_data = base64.b64decode(image_base64.split(',')[1])
        image = Image.open(BytesIO(image_data))
        image_np = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        
        if FACE_RECOGNITION_AVAILABLE:
            try:
                # Find faces using face_recognition
                face_locations = face_recognition.face_locations(image_rgb)
                face_encodings = face_recognition.face_encodings(image_rgb, face_locations)
                
                if not face_encodings:
                    return None
                
                # Compare with known encodings
                face_encoding = face_encodings[0]
                matches = face_recognition.compare_faces(
                    self.known_encodings, 
                    face_encoding,
                    tolerance=0.6
                )
                face_distances = face_recognition.face_distance(
                    self.known_encodings, 
                    face_encoding
                )
                
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    return self.known_names[best_match_index]
                
                return None
            except Exception as e:
                print(f"Error in face recognition: {str(e)}")
                return None
        else:
            # Fallback to OpenCV detection
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return None
            
            # Use histogram for comparison
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            face_encoding = cv2.normalize(hist, hist).flatten().tolist()
            
            # Simple similarity comparison
            if len(self.known_encodings) > 0:
                similarities = []
                for known_enc in self.known_encodings:
                    # Calculate cosine similarity
                    known_arr = np.array(known_enc)
                    curr_arr = np.array(face_encoding)
                    similarity = np.dot(known_arr, curr_arr) / (
                        np.linalg.norm(known_arr) * np.linalg.norm(curr_arr) + 1e-10
                    )
                    similarities.append(similarity)
                
                best_match = np.argmax(similarities)
                if similarities[best_match] > 0.7:
                    return self.known_names[best_match]
            
            return None
