#!/bin/bash

# Invoice App Quick Start Script
# This script installs dependencies and starts the app

echo "=========================================="
echo "   Invoice Dashboard - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if uploads folder exists
if [ ! -d "uploads" ]; then
    echo "📁 Creating uploads folder..."
    mkdir uploads
fi

echo ""
echo "=========================================="
echo "   Starting Invoice Dashboard"
echo "=========================================="
echo ""
echo "🚀 Backend starting on http://localhost:8000"
echo "📄 API Docs available at http://localhost:8000/docs"
echo "🌐 Open index.html in a web browser"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Run the app
python3 app.py
