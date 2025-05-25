import pandas as pd
import sqlite3

# Change these filenames as needed
csv_file = "integrated_results.csv"
sqlite_db = "agriconnect.db"
table_name = "farmers"

# Load the CSV into a DataFrame
df = pd.read_csv(csv_file)

# Connect to SQLite (it will create the DB file if it doesn't exist)
conn = sqlite3.connect(sqlite_db)

# Write the DataFrame to SQLite, replacing the table if it exists
df.to_sql(table_name, conn, if_exists="replace", index=False)

# Optionally: Show success message and number of rows
print(f"CSV '{csv_file}' loaded into '{sqlite_db}' as table '{table_name}' ({len(df)} rows).")

conn.close()