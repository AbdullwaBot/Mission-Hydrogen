#!/bin/bash

echo "🚀 Starting Neural Messenger 2030..."

# Check Python version
python3 --version

# Install system dependencies for Chromium
echo "📦 Installing system dependencies..."
python3 install_deps.py

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p templates

# Make sure the template exists
if [ ! -f "templates/index.html" ]; then
    echo "📁 Creating template directory..."
    # The template will be created by the app if needed
fi

# Start the application
echo "🌐 Starting application..."
python3 app.py
