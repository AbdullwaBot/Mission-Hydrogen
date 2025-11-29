#!/usr/bin/env python3
import subprocess
import sys
import os

def run_command(cmd, description):
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"⚠️ {description} - Warning: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {str(e)}")
        return False

def install_system_dependencies():
    print("🚀 Installing Linux system dependencies for Chromium...")
    
    # Update package list
    run_command("apt-get update", "Updating package list")
    
    # Install Chromium dependencies
    dependencies = [
        "apt-get install -y wget",
        "apt-get install -y gnupg",
        "apt-get install -y ca-certificates",
        "apt-get install -y fonts-liberation",
        "apt-get install -y libasound2",
        "apt-get install -y libatk-bridge2.0-0",
        "apt-get install -y libatk1.0-0",
        "apt-get install -y libc6",
        "apt-get install -y libcairo2",
        "apt-get install -y libcups2",
        "apt-get install -y libdbus-1-3",
        "apt-get install -y libexpat1",
        "apt-get install -y libfontconfig1",
        "apt-get install -y libgbm1",
        "apt-get install -y libgcc1",
        "apt-get install -y libglib2.0-0",
        "apt-get install -y libgtk-3-0",
        "apt-get install -y libnspr4",
        "apt-get install -y libnss3",
        "apt-get install -y libpango-1.0-0",
        "apt-get install -y libpangocairo-1.0-0",
        "apt-get install -y libstdc++6",
        "apt-get install -y libx11-6",
        "apt-get install -y libx11-xcb1",
        "apt-get install -y libxcb1",
        "apt-get install -y libxcomposite1",
        "apt-get install -y libxcursor1",
        "apt-get install -y libxdamage1",
        "apt-get install -y libxext6",
        "apt-get install -y libxfixes3",
        "apt-get install -y libxi6",
        "apt-get install -y libxrandr2",
        "apt-get install -y libxrender1",
        "apt-get install -y libxss1",
        "apt-get install -y libxtst6",
        "apt-get install -y lsb-release",
        "apt-get install -y xdg-utils",
        "apt-get install -y libxshmfence1",
        "apt-get install -y libdrm2",
        "apt-get install -y libxkbcommon0",
        "apt-get install -y libxdamage1",
        "apt-get install -y libxcomposite1",
        "apt-get install -y libxrandr2",
        "apt-get install -y libgbm1",
        "apt-get install -y libasound2"
    ]
    
    for cmd in dependencies:
        if not run_command(cmd, f"Installing {cmd.split()[-1]}"):
            print(f"⚠️ Continuing despite failure...")
    
    print("✅ System dependencies installation completed!")

if __name__ == "__main__":
    install_system_dependencies()
