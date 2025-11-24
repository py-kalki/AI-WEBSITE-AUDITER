import sqlite3
import os
from config import DB_PATH

def get_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with necessary tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Leads Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            category TEXT,
            address TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Audits Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            performance_score INTEGER,
            seo_score INTEGER,
            ux_score INTEGER,
            mobile_score INTEGER,
            overall_score INTEGER,
            audit_data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads (id)
        )
    ''')
    
    # Migration: Add email column if it doesn't exist (for existing DBs)
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN email TEXT")
        print("Migrated DB: Added email column.")
    except sqlite3.OperationalError:
        pass

    # Migration: Add outreach columns
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN outreach_status TEXT DEFAULT 'Pending'")
        cursor.execute("ALTER TABLE leads ADD COLUMN outreach_time TIMESTAMP")
        print("Migrated DB: Added outreach columns.")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def insert_lead(lead_data):
    """Inserts a new lead into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO leads (business_name, category, address, phone, email, website, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            lead_data.get('business_name'),
            lead_data.get('category'),
            lead_data.get('address'),
            lead_data.get('phone'),
            lead_data.get('email'),
            lead_data.get('website'),
            lead_data.get('source')
        ))
        conn.commit()
        lead_id = cursor.lastrowid
        return lead_id
    except Exception as e:
        print(f"Error inserting lead: {e}")
        return None
    finally:
        conn.close()

def delete_lead(lead_id):
    """Deletes a lead and its audits from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM audits WHERE lead_id = ?", (lead_id,))
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting lead: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    # Ensure storage directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    init_db()
