# Smart Attendance System with Face Recognition

A machine learning-based attendance system that uses face recognition to automatically mark attendance. Simple to implement, easy to use, and supports online dataset downloads.

## Features

- 👤 **Face Recognition**: Automatic face detection and recognition
- 📱 **Web UI**: User-friendly web interface for attendance management
- 🗃️ **Dataset Management**: Download and manage datasets online
- 📊 **Attendance Logs**: View attendance records and statistics
- 🔧 **Simple Configuration**: Easy setup and deployment
- 📷 **Real-time Processing**: Live camera feed processing

## Project Structure

```
smart-attendance-system/
├── backend/              # Flask API server
├── frontend/             # Web UI (HTML, CSS, JavaScript)
├── models/               # Trained face recognition models
├── datasets/             # Face dataset storage
├── attendance_logs/      # Attendance records
└── requirements.txt      # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup

1. **Clone/Navigate to project**:
   ```bash
   cd smart-attendance-system
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python backend/app.py
   ```

5. **Open web browser**:
   Navigate to `http://localhost:5000`

## Usage

### Simple Mode (Quick Start)

1. Go to Dashboard
2. Click "Add New Person"
3. Enter name and upload 5-10 photos
4. Click "Train Model"
5. Start attendance marking with camera

### Advanced Features

- **Download Dataset**: Go to Settings → Download Dataset from online sources
- **View Logs**: Check attendance records in Reports section
- **Export Data**: Export attendance as CSV/PDF

## Dataset Sources

The system supports downloading from:
- LFW (Labeled Faces in the Wild)
- VGGFace2 (subset)
- Custom dataset upload

## API Endpoints

- `GET /api/persons` - Get all registered persons
- `POST /api/persons` - Add new person
- `POST /api/mark-attendance` - Mark attendance
- `GET /api/attendance-logs` - Get attendance records
- `POST /api/train-model` - Train face recognition model

## Configuration

Edit `.env` file:
```
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_PATH=./attendance_logs
MODEL_PATH=./models
```

## Troubleshooting

- **No faces detected**: Ensure good lighting and clear face images
- **Installation issues**: Use `pip install --upgrade face-recognition`
- **Port already in use**: Change `FLASK_PORT` in `.env`

## License

MIT License

## Support

For issues and questions, please refer to the documentation or create an issue.
