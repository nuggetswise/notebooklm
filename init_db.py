#!/usr/bin/env python3
"""
Initialize the SQLite database for the Email RAG system.
"""

import sqlite3
import os
from pathlib import Path

def init_database():
    """Initialize the SQLite database with required tables."""
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Database file path
    db_path = data_dir / "emails.db"
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create emails table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            subject TEXT,
            sender TEXT,
            date TEXT,
            label TEXT,
            parsed_path TEXT,
            has_attachments BOOLEAN,
            attachment_count INTEGER,
            has_media BOOLEAN,
            media_urls TEXT,
            persona_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender ON emails(sender)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_label ON emails(label)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON emails(date)')
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at: {db_path}")
    print(f"📊 Tables created: emails")
    print(f"🔍 Indexes created: sender, label, date")

if __name__ == "__main__":
    init_database() 