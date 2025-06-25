#!/usr/bin/env python3
"""
Gmail Forwarding Setup Script
Helps you set up Gmail API credentials for email forwarding
"""

import os
import webbrowser
from pathlib import Path

def main():
    print("🚀 Gmail Forwarding Setup for Email RAG System")
    print("=" * 50)
    
    # Check if credentials already exist
    if os.path.exists('gmail_credentials.json'):
        print("✅ Gmail credentials already found!")
        print("You can now run: python gmail_forwarder.py")
        return
    
    print("📋 Setting up Gmail API credentials...")
    print()
    print("Step 1: Create a Google Cloud Project")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Gmail API")
    print()
    
    # Open Google Cloud Console
    input("Press Enter to open Google Cloud Console...")
    webbrowser.open("https://console.cloud.google.com/")
    
    print()
    print("Step 2: Enable Gmail API")
    print("1. In your project, go to 'APIs & Services' > 'Library'")
    print("2. Search for 'Gmail API'")
    print("3. Click on it and press 'Enable'")
    print()
    
    input("Press Enter to open Gmail API page...")
    webbrowser.open("https://console.cloud.google.com/apis/library/gmail.googleapis.com")
    
    print()
    print("Step 3: Create Credentials")
    print("1. Go to 'APIs & Services' > 'Credentials'")
    print("2. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("3. Choose 'Desktop application'")
    print("4. Give it a name like 'Email RAG Forwarder'")
    print("5. Click 'Create'")
    print("6. Download the JSON file")
    print()
    
    input("Press Enter to open Credentials page...")
    webbrowser.open("https://console.cloud.google.com/apis/credentials")
    
    print()
    print("Step 4: Save Credentials")
    print("1. Rename the downloaded JSON file to 'gmail_credentials.json'")
    print("2. Move it to this directory:", os.getcwd())
    print()
    
    # Wait for credentials file
    while not os.path.exists('gmail_credentials.json'):
        input("Press Enter when you've saved gmail_credentials.json in this directory...")
        if not os.path.exists('gmail_credentials.json'):
            print("❌ gmail_credentials.json not found. Please try again.")
    
    print("✅ Credentials file found!")
    print()
    print("Step 5: Install Dependencies")
    print("Run: pip install -r gmail_requirements.txt")
    print()
    
    input("Press Enter to install dependencies...")
    os.system("pip install -r gmail_requirements.txt")
    
    print()
    print("🎉 Setup Complete!")
    print("=" * 50)
    print("Now you can:")
    print("1. Test once: python gmail_forwarder.py once")
    print("2. Run continuously: python gmail_forwarder.py continuous")
    print("3. Run continuously with custom interval: python gmail_forwarder.py continuous 30")
    print()
    print("The forwarder will look for emails with subject containing 'Label: AI'")
    print("You can modify the label pattern in the script if needed.")
    print()
    print("Make sure your RAG system is running on http://localhost:8001")

if __name__ == "__main__":
    main() 