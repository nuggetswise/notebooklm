import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path
from .models import EmailMetadata
from .config import config

def get_db():
    """Get a database connection for the Streamlit app."""
    # Fix path to work from any directory
    current_dir = Path(__file__).parent
    db_path = str(current_dir.parent / "data" / "email_index.db")
    return sqlite3.connect(db_path)

class EmailDatabase:
    """SQLite database operations for email metadata."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Fix path to work from any directory
            current_dir = Path(__file__).parent
            self.db_path = str(current_dir.parent / "data" / "email_index.db")
        else:
            self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    date TEXT NOT NULL,
                    label TEXT NOT NULL,
                    content TEXT,
                    timestamp TEXT NOT NULL,
                    parsed_path TEXT NOT NULL,
                    has_attachments BOOLEAN DEFAULT FALSE,
                    attachment_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_label ON emails(label)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON emails(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sender ON emails(sender)")
            conn.commit()
    
    def insert_email(self, email: EmailMetadata) -> bool:
        """Insert email metadata into database, keeping only the most recent 100 emails."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO emails (
                        id, subject, sender, date, label, timestamp, 
                        parsed_path, has_attachments, attachment_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    email.id, email.subject, str(email.sender), 
                    email.date.isoformat(), email.label, email.timestamp.isoformat(),
                    email.parsed_path, email.has_attachments, email.attachment_count
                ))
                conn.commit()
                # Enforce max 100 emails
                cursor = conn.execute("SELECT id FROM emails ORDER BY date DESC")
                ids = [row[0] for row in cursor.fetchall()]
                if len(ids) > 100:
                    for old_id in ids[100:]:
                        conn.execute("DELETE FROM emails WHERE id = ?", (old_id,))
                    conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting email: {e}")
            return False
    
    def get_email_by_id(self, email_id: str) -> Optional[EmailMetadata]:
        """Retrieve email metadata by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM emails WHERE id = ?", (email_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return EmailMetadata(
                        id=row['id'],
                        subject=row['subject'],
                        sender=row['sender'],
                        date=datetime.fromisoformat(row['date']),
                        label=row['label'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        parsed_path=row['parsed_path'],
                        has_attachments=bool(row['has_attachments']),
                        attachment_count=row['attachment_count']
                    )
                return None
        except Exception as e:
            print(f"Error retrieving email: {e}")
            return None
    
    def get_emails_by_label(self, label: str, max_age_days: int = None) -> List[EmailMetadata]:
        """Retrieve up to 100 most recent emails by label with optional date filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                if max_age_days:
                    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
                    cursor = conn.execute("""
                        SELECT * FROM emails 
                        WHERE label = ? AND date >= ? 
                        ORDER BY date DESC LIMIT 100
                    """, (label, cutoff_date.isoformat()))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM emails 
                        WHERE label = ? 
                        ORDER BY date DESC LIMIT 100
                    """, (label,))
                emails = []
                for row in cursor.fetchall():
                    emails.append(EmailMetadata(
                        id=row['id'],
                        subject=row['subject'],
                        sender=row['sender'],
                        date=datetime.fromisoformat(row['date']),
                        label=row['label'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        parsed_path=row['parsed_path'],
                        has_attachments=bool(row['has_attachments']),
                        attachment_count=row['attachment_count']
                    ))
                return emails
        except Exception as e:
            print(f"Error retrieving emails by label: {e}")
            return []
    
    def get_all_emails(self, max_age_days: int = None) -> List[EmailMetadata]:
        """Retrieve up to 100 most recent emails with optional date filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                if max_age_days:
                    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
                    cursor = conn.execute("""
                        SELECT * FROM emails 
                        WHERE date >= ? 
                        ORDER BY date DESC LIMIT 100
                    """, (cutoff_date.isoformat(),))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM emails 
                        ORDER BY date DESC LIMIT 100
                    """)
                emails = []
                for row in cursor.fetchall():
                    emails.append(EmailMetadata(
                        id=row['id'],
                        subject=row['subject'],
                        sender=row['sender'],
                        date=datetime.fromisoformat(row['date']),
                        label=row['label'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        parsed_path=row['parsed_path'],
                        has_attachments=bool(row['has_attachments']),
                        attachment_count=row['attachment_count']
                    ))
                return emails
        except Exception as e:
            print(f"Error retrieving all emails: {e}")
            return []
    
    def get_labels(self) -> List[str]:
        """Get all unique labels in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT DISTINCT label FROM emails ORDER BY label")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error retrieving labels: {e}")
            return []
    
    def delete_email(self, email_id: str) -> bool:
        """Delete email from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM emails WHERE id = ?", (email_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting email: {e}")
            return False
    
    def get_email_count(self, label: str = None, max_age_days: int = None) -> int:
        """Get count of emails with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if label and max_age_days:
                    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
                    cursor = conn.execute("""
                        SELECT COUNT(*) FROM emails 
                        WHERE label = ? AND date >= ?
                    """, (label, cutoff_date.isoformat()))
                elif label:
                    cursor = conn.execute("""
                        SELECT COUNT(*) FROM emails WHERE label = ?
                    """, (label,))
                elif max_age_days:
                    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
                    cursor = conn.execute("""
                        SELECT COUNT(*) FROM emails WHERE date >= ?
                    """, (cutoff_date.isoformat(),))
                else:
                    cursor = conn.execute("SELECT COUNT(*) FROM emails")
                
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting email count: {e}")
            return 0

# Global database instance
db = EmailDatabase() 