#!/bin/bash
echo "🚀 2025 December - Installing Dependencies..."
pip install -r requirements.txt
echo "📦 Installing Playwright Browser..."
python -m playwright install chromium --with-deps
echo "✅ Setup Complete!"
