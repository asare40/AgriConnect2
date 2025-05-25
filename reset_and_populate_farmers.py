import sqlite3
import random

conn = sqlite3.connect("agriconnect.db")
c = conn.cursor()

# Drop and recreate the farmers table
c.execute("DROP TABLE IF EXISTS farmers")
c.execute("""
CREATE TABLE farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT,
    predicted_credit_score REAL,
    phl_risk_score REAL,
    interventions_adopted TEXT,
    latitude REAL,
    longitude REAL
)
""")

regions = [
    ("Kano", 12.0, 8.5),
    ("Oyo", 7.85, 3.93),
    ("Benue", 7.34, 8.77),
    ("Kaduna", 10.52, 7.44),
    ("Plateau", 9.22, 9.52),
    ("Sokoto", 13.06, 5.24),
    ("Niger", 9.63, 6.54),
    ("Bauchi", 10.31, 9.84)
]
interventions = [
    "Improved Storage", "Hermetic Bags", "Drying", "Crop Rotation", "Farmer Training"
]

rows = []
for i in range(50):
    region, lat, lon = random.choice(regions)
    jitter_lat = lat + random.uniform(-0.15, 0.15)
    jitter_lon = lon + random.uniform(-0.15, 0.15)
    credit = random.randint(400, 800)
    phl_risk = round(random.uniform(0.10, 0.60), 2)
    intervention = random.choice(interventions)
    rows.append((region, credit, phl_risk, intervention, jitter_lat, jitter_lon))

c.executemany(
    "INSERT INTO farmers (region, predicted_credit_score, phl_risk_score, interventions_adopted, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)",
    rows
)
conn.commit()
conn.close()
print("Farmers table reset and 50 demo records inserted.")