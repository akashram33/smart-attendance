/* ==================== GLOBAL VARIABLES ==================== */

const API_BASE_URL = 'http://localhost:5000/api';
let currentPersonId = null;
let cameraStream = null;

/* ==================== INITIALIZATION ==================== */

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Load initial data
    loadDashboardData();
    loadPersons();
    loadAvailableDatasets();
    loadAttendanceLogs();
    setDefaultLogDate();
    
    // Setup navigation
    setupNavigation();
    
    // Setup upload area
    setupUploadArea();
}

/* ==================== TIME & DATE ==================== */

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeString;
    document.getElementById('current-attendance-time').textContent = timeString;
}

function setDefaultLogDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('log-date').value = today;
}

/* ==================== NAVIGATION ==================== */

function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            navigateTo(section);
        });
    });
}

function navigateTo(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));
    
    // Remove active from nav buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Mark nav button as active
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
    
    // Update header title
    const titles = {
        'dashboard': 'Dashboard',
        'attendance': 'Mark Attendance',
        'persons': 'Persons',
        'logs': 'Attendance Logs',
        'datasets': 'Dataset Management',
        'settings': 'Settings'
    };
    document.getElementById('section-title').textContent = titles[sectionId] || 'Dashboard';
    
    // Initialize section-specific logic
    if (sectionId === 'attendance') {
        initializeCamera();
    }
    if (sectionId === 'logs') {
        loadAttendanceLogs();
    }
}

/* ==================== DASHBOARD ==================== */

function loadDashboardData() {
    // Load stats
    loadPersonStats();
    loadModelStatus();
    loadTodayStats();
}

async function loadPersonStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/persons`);
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('total-persons').textContent = data.persons.length;
        }
    } catch (error) {
        console.error('Error loading person stats:', error);
    }
}

async function loadModelStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/model-status`);
        const data = await response.json();
        if (data.status === 'success') {
            const status = data.is_trained ? '✅ Trained' : '⚠️ Not Trained';
            document.getElementById('model-status').textContent = status;
            if (data.stats) {
                document.getElementById('faces-encoded').textContent = data.stats.total_encoded_faces || 0;
            }
        }
    } catch (error) {
        console.error('Error loading model status:', error);
    }
}

async function loadTodayStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance-stats`);
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('present-today').textContent = data.stats.total_present || 0;
        }
    } catch (error) {
        console.error('Error loading today stats:', error);
    }
}

/* ==================== PERSONS MANAGEMENT ==================== */

async function loadPersons() {
    try {
        const response = await fetch(`${API_BASE_URL}/persons`);
        const data = await response.json();
        
        if (data.status === 'success') {
            displayPersons(data.persons);
        }
    } catch (error) {
        console.error('Error loading persons:', error);
    }
}

function displayPersons(persons) {
    const grid = document.getElementById('persons-grid');
    grid.innerHTML = '';
    
    persons.forEach(person => {
        const card = document.createElement('div');
        card.className = 'person-card';
        card.innerHTML = `
            <div class="person-avatar">👤</div>
            <div class="person-info">
                <div class="person-name">${person.name}</div>
                <div class="person-images">Images: ${person.image_count}</div>
                <div class="person-actions">
                    <button onclick="openUploadModal('${person.id}', '${person.name}')">📷</button>
                    <button onclick="deletePerson('${person.id}')">🗑️</button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function openAddPersonModal() {
    document.getElementById('add-person-modal').classList.add('active');
}

async function addPerson(event) {
    event.preventDefault();
    
    const name = document.getElementById('person-name').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/persons`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Person added successfully!');
            document.getElementById('person-name').value = '';
            closeModal('add-person-modal');
            loadPersons();
            loadDashboardData();
        }
    } catch (error) {
        showNotification('Error adding person: ' + error.message, 'error');
    }
}

function openUploadModal(personId, personName) {
    currentPersonId = personId;
    document.getElementById('modal-person-name').textContent = personName;
    document.getElementById('upload-images-modal').classList.add('active');
}

async function uploadPersonImages() {
    const fileInput = document.getElementById('person-images');
    const files = fileInput.files;
    
    if (files.length === 0) {
        showNotification('Please select at least one image', 'error');
        return;
    }
    
    for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('person_id', currentPersonId);
        
        try {
            const response = await fetch(`${API_BASE_URL}/upload-image`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                showNotification(`Failed to upload ${file.name}: ${data.message}`, 'error');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
        }
    }
    
    showNotification('Images uploaded successfully!');
    closeModal('upload-images-modal');
    loadPersons();
}

function displaySelectedImages() {
    const fileInput = document.getElementById('person-images');
    const preview = document.getElementById('preview-images');
    preview.innerHTML = '';
    
    for (let file of fileInput.files) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            preview.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
}

async function deletePerson(personId) {
    if (!confirm('Are you sure you want to delete this person?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/persons/${personId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Person deleted successfully');
            loadPersons();
            loadDashboardData();
        }
    } catch (error) {
        showNotification('Error deleting person: ' + error.message, 'error');
    }
}

/* ==================== MODEL TRAINING ==================== */

async function trainModel() {
    try {
        showNotification('Training model... Please wait', 'info');
        
        const response = await fetch(`${API_BASE_URL}/train-model`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Model trained successfully! Faces encoded: ' + data.stats.faces_encoded);
            loadModelStatus();
        } else {
            showNotification('Error training model: ' + data.message, 'error');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

/* ==================== ATTENDANCE MARKING ==================== */

function initializeCamera() {
    if (!cameraStream) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                cameraStream = stream;
                const video = document.getElementById('camera-feed');
                video.srcObject = stream;
            })
            .catch(error => {
                showNotification('Cannot access camera: ' + error.message, 'error');
            });
    }
}

function captureAndMarkAttendance() {
    const video = document.getElementById('camera-feed');
    const canvas = document.getElementById('camera-canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg');
    markAttendance(imageData);
}

async function markAttendance(imageBase64) {
    try {
        document.getElementById('attendance-status').textContent = 'Processing...';
        
        const response = await fetch(`${API_BASE_URL}/mark-attendance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageBase64 })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            document.getElementById('last-person').textContent = data.person;
            document.getElementById('attendance-status').textContent = '✅ Marked!';
            showNotification('Attendance marked for ' + data.person);
            loadTodayStats();
        } else if (data.status === 'warning') {
            document.getElementById('attendance-status').textContent = '⚠️ Not Recognized';
            showNotification('Face not recognized. Please try again.', 'warning');
        }
    } catch (error) {
        document.getElementById('attendance-status').textContent = '❌ Error';
        showNotification('Error marking attendance: ' + error.message, 'error');
    }
}

/* ==================== ATTENDANCE LOGS ==================== */

async function loadAttendanceLogs() {
    const date = document.getElementById('log-date').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/attendance-logs?date=${date}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            displayAttendanceLogs(data.logs);
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

function displayAttendanceLogs(logs) {
    const tbody = document.getElementById('logs-tbody');
    tbody.innerHTML = '';
    
    logs.forEach(log => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${log.person_name}</td>
            <td>${formatTime(log.timestamp)}</td>
            <td>${log.checkout_time ? formatTime(log.checkout_time) : '-'}</td>
            <td>${log.duration || '-'}</td>
        `;
    });
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">No attendance records for this date</td></tr>';
    }
}

function formatTime(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

/* ==================== DATASETS ==================== */

async function loadAvailableDatasets() {
    try {
        const response = await fetch(`${API_BASE_URL}/datasets/available`);
        const data = await response.json();
        
        if (data.status === 'success') {
            displayAvailableDatasets(data.datasets);
        }
    } catch (error) {
        console.error('Error loading datasets:', error);
    }
}

function displayAvailableDatasets(datasets) {
    const grid = document.getElementById('datasets-grid');
    grid.innerHTML = '';
    
    datasets.forEach(dataset => {
        const card = document.createElement('div');
        card.className = 'dataset-card';
        card.innerHTML = `
            <h4>${dataset.name}</h4>
            <p>${dataset.description}</p>
            <div class="dataset-meta">
                <p>👥 ${dataset.people_count} people</p>
                <p>📦 ${dataset.size}</p>
            </div>
            <button class="btn btn-primary" onclick="downloadDataset('${dataset.id}')">
                Download
            </button>
        `;
        grid.appendChild(card);
    });
}

async function downloadDataset(datasetId) {
    try {
        showNotification('Downloading dataset... Please wait', 'info');
        
        const response = await fetch(`${API_BASE_URL}/datasets/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dataset_name: datasetId })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Dataset downloaded successfully!');
        }
    } catch (error) {
        showNotification('Error downloading dataset: ' + error.message, 'error');
    }
}

function setupUploadArea() {
    const uploadArea = document.getElementById('upload-area');
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f0f0f0';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.background = 'white';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = 'white';
        
        const files = e.dataTransfer.files;
        document.getElementById('dataset-file').files = files;
        uploadDataset();
    });
}

async function uploadDataset() {
    const fileInput = document.getElementById('dataset-file');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showNotification('Uploading dataset...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/datasets/import-local`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Dataset uploaded successfully!');
            fileInput.value = '';
        }
    } catch (error) {
        showNotification('Error uploading dataset: ' + error.message, 'error');
    }
}

/* ==================== TAB SWITCHING ==================== */

function switchTab(tabId) {
    // Hide all tab contents
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active from tab buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    
    // Mark button as active
    event.target.classList.add('active');
}

/* ==================== MODALS ==================== */

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    });
});

/* ==================== NOTIFICATIONS ==================== */

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#ff6b6b' : type === 'warning' ? '#ffa500' : type === 'info' ? '#4dabf7' : '#51cf66'};
        color: white;
        border-radius: 5px;
        z-index: 10000;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        animation: slideInRight 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

/* ==================== UTILITY FUNCTIONS ==================== */

function getCurrentDate() {
    return new Date().toISOString().split('T')[0];
}
