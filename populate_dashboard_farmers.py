import sqlite3

DB_PATH = "agriconnect.db"

def populate_dashboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS farmers (
        farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT,
        predicted_credit_score REAL,
        phl_risk_score REAL,
        interventions_adopted TEXT,
        farm_size REAL,
        crop_type TEXT,
        gender TEXT,
        harvest_month TEXT
    )
    """)
    rows = [
        ("Kano", 620, 0.6, "Drying", 2.4, "Maize", "male", "May"),
        ("Oyo", 570, 0.8, "Hermetic Bags", 1.8, "Rice", "female", "Jun"),
        ("Benue", 670, 0.4, "Mechanized", 3.1, "Cassava", "male", "Jul"),
        ("Kano", 690, 0.3, "Drying", 4.0, "Maize", "female", "Jun"),
        ("Plateau", 710, 0.2, "Hermetic Bags", 2.6, "Wheat", "male", "Aug"),
        ("Kaduna", 540, 0.9, "Traditional", 1.5, "Yam", "female", "May"),
        ("Benue", 570, 0.7, "Drying", 2.0, "Maize", "male", "Jul"),
        ("Oyo", 655, 0.5, "Mechanized", 2.2, "Rice", "female", "Jun"),
        ("Plateau", 680, 0.4, "Drying", 3.0, "Wheat", "male", "Aug"),
        ("Kaduna", 600, 0.6, "Hermetic Bags", 2.9, "Yam", "female", "May"),
    ]
    c.executemany("""
        INSERT INTO farmers (region, predicted_credit_score, phl_risk_score, interventions_adopted, farm_size, crop_type, gender, harvest_month)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()
    print("Sample dashboard farmer records added.")

if __name__ == "__main__":
    populate_dashboard()