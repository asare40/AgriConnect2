import sqlite3

REQUIRED_COLUMNS = {
    "region": "TEXT",
    "predicted_credit_score": "REAL",
    "phl_risk_score": "REAL",
    "interventions_adopted": "TEXT",
    "latitude": "REAL",
    "longitude": "REAL"
}

DB_PATH = "agriconnect.db"
TABLE = "farmers"

def get_existing_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]

def add_missing_columns():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    existing_cols = get_existing_columns(c, TABLE)
    added = []
    for col, coltype in REQUIRED_COLUMNS.items():
        if col not in existing_cols:
            try:
                c.execute(f"ALTER TABLE {TABLE} ADD COLUMN {col} {coltype}")
                print(f"Added column: {col} ({coltype})")
                added.append(col)
            except sqlite3.OperationalError as e:
                print(f"Error adding column {col}: {e}")
        else:
            print(f"Column already exists: {col}")
    conn.commit()
    conn.close()
    print("Done. Added columns:", added if added else "No new columns needed.")

if __name__ == "__main__":
    add_missing_columns()