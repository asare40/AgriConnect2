import sqlite3
import random

DB_PATH = "agriconnect.db"
NUM_ROWS = 1000  # Change this value for even more data

regions = ["Kano", "Oyo", "Benue", "Kaduna", "Plateau"]
interventions = ["Drying", "Hermetic Bags", "Mechanized", "Traditional"]
crop_types = ["Maize", "Rice", "Cassava", "Wheat", "Yam"]
genders = ["male", "female"]
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def rand_score(a, b): return round(random.uniform(a, b), 2)

def main():
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
    # Optional: Clear existing data
    c.execute("DELETE FROM farmers")
    for _ in range(NUM_ROWS):
        region = random.choice(regions)
        score = rand_score(500, 800)
        phl = rand_score(0.2, 0.95)
        intervention = random.choice(interventions)
        farm_size = rand_score(1.0, 5.0)
        crop = random.choice(crop_types)
        gender = random.choice(genders)
        month = random.choice(months)
        c.execute("""
            INSERT INTO farmers (region, predicted_credit_score, phl_risk_score, interventions_adopted, farm_size, crop_type, gender, harvest_month)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (region, score, phl, intervention, farm_size, crop, gender, month))
    conn.commit()
    conn.close()
    print(f"Inserted {NUM_ROWS} synthetic farmer records into 'farmers' table.")

if __name__ == "__main__":
    main()