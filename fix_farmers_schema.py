import sqlite3

DB_PATH = "agriconnect.db"

def fix_schema():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS farmers")
    conn.commit()
    print("Dropped old farmers table (if any). Now run your populate_dashboard_farmers.py script again to recreate with correct columns.")

if __name__ == "__main__":
    fix_schema()