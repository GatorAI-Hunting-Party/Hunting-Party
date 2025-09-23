#!/usr/bin/env python3
"""
Setup script for HuntingParty.ai
Initializes the project environment and database
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        "data/raw/gp_documents",
        "data/raw/market_feeds", 
        "data/processed",
        "data/training",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect("hunting_party.db")
    cursor = conn.cursor()
    
    # Create deals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            source_document TEXT NOT NULL,
            extraction_date TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            data_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create market data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            property_type TEXT NOT NULL,
            property_class TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metric_unit TEXT NOT NULL,
            data_source TEXT NOT NULL,
            collection_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id TEXT NOT NULL,
            analysis_type TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            gp_value REAL,
            market_value REAL,
            variance REAL,
            outlier_score REAL,
            flag_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_env_file():
    """Create .env file from template"""
    if not os.path.exists(".env"):
        if os.path.exists("env.example"):
            with open("env.example", "r") as src:
                with open(".env", "w") as dst:
                    dst.write(src.read())
            print("✅ Created .env file from template")
        else:
            print("⚠️  env.example not found, skipping .env creation")
    else:
        print("✅ .env file already exists")

def install_dependencies():
    """Install Python dependencies"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False
    return True

def check_tesseract():
    """Check if Tesseract OCR is available"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is available")
        return True
    except Exception as e:
        print("⚠️  Tesseract OCR not found. Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up HuntingParty.ai...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Initialize database
    init_database()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return
    
    # Check Tesseract OCR
    check_tesseract()
    
    print("=" * 50)
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Install Tesseract OCR if not already installed")
    print("2. Run the backend: python api/main.py")
    print("3. Run the frontend: cd frontend && npm install && npm run dev")
    print("\nFor more information, see the README.md file")

if __name__ == "__main__":
    main()
