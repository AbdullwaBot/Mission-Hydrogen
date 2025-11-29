#!/bin/bash

echo "🚀 Starting Neural Messenger 2030..."

# Check Python version
python3 --version

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install -r requirements.txt

# Install Playwright browser (system dependencies skip - Render already has them)
echo "🌐 Installing Playwright browser..."
python3 -m playwright install chromium
python3 -m playwright install-deps

# Create templates directory if not exists
mkdir -p templates

# Copy index.html to templates if needed
if [ ! -f "templates/index.html" ]; then
    echo "📁 Creating template structure..."
    # Template will be created by app
fi

# Start the application
echo "🎯 Starting application on port $PORT..."
python3 app.py
