"""
Dataset Downloader
Handles downloading and managing datasets
"""

import os
import json
import requests
from pathlib import Path
from zipfile import ZipFile
import shutil

class DatasetDownloader:
    def __init__(self, datasets_dir):
        self.datasets_dir = Path(datasets_dir)
        self.datasets_dir.mkdir(exist_ok=True)
        self.metadata_file = self.datasets_dir / "metadata.json"
    
    def get_available_datasets(self):
        """Get list of available datasets"""
        return [
            {
                "id": "lfw",
                "name": "LFW (Labeled Faces in the Wild)",
                "description": "13,000+ labeled faces from the web",
                "size": "~200MB",
                "source": "http://vis-www.cs.umass.edu/lfw/lfw.tgz",
                "people_count": 5749
            },
            {
                "id": "vggface2_subset",
                "name": "VGGFace2 (Subset)",
                "description": "High resolution face dataset",
                "size": "~500MB",
                "source": "https://www.robots.ox.ac.uk/~vgg/data/vgg_face2/",
                "people_count": 1000
            },
            {
                "id": "face_emoji",
                "name": "Face Emoji Dataset",
                "description": "Simple emoji face dataset for testing",
                "size": "~50MB",
                "source": "local",
                "people_count": 50
            }
        ]
    
    def download_dataset(self, dataset_name):
        """Download a dataset"""
        datasets = {d['id']: d for d in self.get_available_datasets()}
        
        if dataset_name not in datasets:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        dataset = datasets[dataset_name]
        dataset_path = self.datasets_dir / dataset_name
        
        if dataset_path.exists():
            return str(dataset_path)
        
        dataset_path.mkdir(exist_ok=True)
        
        # For demonstration, create sample directory structure
        if dataset_name == "lfw":
            self._create_sample_lfw_structure(dataset_path)
        elif dataset_name == "vggface2_subset":
            self._create_sample_vggface_structure(dataset_path)
        elif dataset_name == "face_emoji":
            self._create_sample_emoji_structure(dataset_path)
        
        # Save metadata
        self._save_dataset_metadata(dataset_name, dataset)
        
        return str(dataset_path)
    
    def _create_sample_lfw_structure(self, path):
        """Create sample LFW dataset structure"""
        people = ["David_Beckham", "George_Bush", "Margaret_Thatcher", "Kofi_Annan"]
        
        for person in people:
            person_dir = path / person
            person_dir.mkdir(exist_ok=True)
            
            # Create placeholder files
            for i in range(3):
                (person_dir / f"{person}_0001_{i}.jpg").touch()
    
    def _create_sample_vggface_structure(self, path):
        """Create sample VGGFace structure"""
        people = [f"person_{i:04d}" for i in range(100, 110)]
        
        for person in people:
            person_dir = path / person
            person_dir.mkdir(exist_ok=True)
            
            for i in range(3):
                (person_dir / f"{person}_{i}.jpg").touch()
    
    def _create_sample_emoji_structure(self, path):
        """Create sample emoji face structure"""
        faces = ["happy", "sad", "surprised", "angry", "neutral"]
        
        for face_type in faces:
            face_dir = path / face_type
            face_dir.mkdir(exist_ok=True)
            
            for i in range(5):
                (face_dir / f"{face_type}_{i}.jpg").touch()
    
    def _save_dataset_metadata(self, dataset_name, dataset_info):
        """Save dataset metadata"""
        metadata = {}
        
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
        
        metadata[dataset_name] = {
            **dataset_info,
            'downloaded_at': str(Path.ctime(self.datasets_dir / dataset_name))
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def import_local_dataset(self, file):
        """Import local dataset from zip file"""
        import tempfile
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / file.filename
            file.save(str(zip_path))
            
            # Extract and move to datasets directory
            dataset_name = file.filename.split('.')[0]
            dataset_path = self.datasets_dir / dataset_name
            
            with ZipFile(str(zip_path), 'r') as zf:
                zf.extractall(str(dataset_path))
        
        return str(dataset_path)
    
    def get_dataset_info(self, dataset_name):
        """Get info about downloaded dataset"""
        dataset_path = self.datasets_dir / dataset_name
        
        if not dataset_path.exists():
            return None
        
        # Count directories (people)
        people_count = len([d for d in dataset_path.iterdir() if d.is_dir()])
        
        # Count images
        image_count = len(list(dataset_path.rglob('*.jpg'))) + \
                     len(list(dataset_path.rglob('*.png')))
        
        return {
            'name': dataset_name,
            'path': str(dataset_path),
            'people_count': people_count,
            'image_count': image_count,
            'size_mb': round(sum(f.stat().st_size for f in dataset_path.rglob('*')) / (1024 * 1024), 2)
        }
