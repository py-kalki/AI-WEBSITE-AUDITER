import csv
import os
from storage.database import get_connection

def export_leads_to_csv(filename="leads_export.csv"):
    """Exports all leads to a CSV file."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM leads")
    rows = cursor.fetchall()
    
    if not rows:
        print("No leads to export.")
        conn.close()
        return

    # Get column names
    column_names = [description[0] for description in cursor.description]
    
    filepath = os.path.join(os.getcwd(), filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)
            writer.writerows(rows)
        print(f"Leads exported to {filepath}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
    finally:
        conn.close()
