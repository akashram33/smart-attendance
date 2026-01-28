#!/bin/bash
# Smart Attendance System - Quick Setup Script

echo "================================"
echo "Smart Attendance System Setup"
echo "================================"

# Check Python version
echo "Checking Python installation..."
python --version

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/Scripts/activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/Scripts/activate"
echo "2. Run the server: python backend/app.py"
echo "3. Open browser: http://localhost:5000"
echo ""
echo "================================"
