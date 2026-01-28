# Quick Start Guide - 5 Minutes Setup

## ⚡ 5-Minute Quick Start

### Step 1: Install (2 minutes)
```bash
cd smart-attendance-system
python -m venv venv

# Windows
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Run Server (1 minute)
```bash
python backend/app.py
```

You'll see:
```
Starting server at http://localhost:5000
```

### Step 3: Open Browser (1 minute)
- Go to: `http://localhost:5000`
- You should see the dashboard

### Step 4: Add Your First Person (1 minute)
1. Click "👥 Persons"
2. Click "➕ Add Person"
3. Type your name
4. Click "Create Person"

---

## 🎯 First Attendance in 10 Minutes

### Add Photos (3 minutes)
1. Click 📷 on your person card
2. Upload 5-10 clear selfies
3. Different angles and expressions
4. Click "Upload Images"

### Train Model (3 minutes)
1. Go to "Dashboard"
2. Click "Train Model 🤖"
3. Wait for completion
4. Status should show "✅ Trained"

### Mark Attendance (2 minutes)
1. Click "✅ Mark Attendance"
2. Position face in camera
3. Click "📸 Capture Face"
4. ✅ Done! Attendance marked

---

## 📚 Common Tasks

### Download a Dataset
```
Datasets → Available → Click "Download" → Wait
```

### View Today's Attendance
```
📋 Attendance Logs → Date is pre-selected → See all marked attendance
```

### Add Multiple People
```
Repeat "Add Your First Person" section for each person
```

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Camera not working | Check camera permissions in OS |
| Face not detected | Better lighting, face must be clear |
| Module not found | Run: `pip install -r requirements.txt` again |
| Port 5000 in use | Change FLASK_PORT in .env file |
| Recognition failing | Retrain model with more diverse images |

---

## 📱 System Requirements

✅ **Minimum:**
- Python 3.8+
- 2GB RAM
- Webcam
- Modern browser

✅ **Recommended:**
- Python 3.9+
- 4GB+ RAM
- SSD storage
- i5/i7 CPU

---

## 🔑 Key Features at a Glance

| Feature | Location |
|---------|----------|
| Add Persons | Click "👥 Persons" → Add Person |
| Upload Photos | Click 📷 on person card |
| Train Model | Dashboard → "Train Model" button |
| Mark Attendance | Click "✅ Mark Attendance" → Capture |
| View Logs | Click "📋 Attendance Logs" → Select date |
| Download Dataset | "🗃️ Datasets" → "Available" → Click Download |
| Check Status | Dashboard → View stat cards |

---

## 📞 Need Help?

1. Check **INSTALL.md** for detailed troubleshooting
2. Check **README.md** for comprehensive documentation
3. Ensure Python 3.8+ is installed
4. Make sure all dependencies installed via requirements.txt

---

## 🚀 Ready to Go!

Your Smart Attendance System is ready to use. Start marking attendance! 📸✅

**Remember:** Better photos = Better recognition! 📷
