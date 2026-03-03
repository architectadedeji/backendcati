#!/usr/bin/env python
"""Export all database tables as CSV files."""
import sqlite3
import csv
from pathlib import Path

DATABASE_PATH = "db.sqlite3"
EXPORT_DIR = Path("backup/csv_export")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Connect to database
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in cursor.fetchall()]

print(f"📊 Found {len(tables)} tables to export")
print(f"📁 Exporting to: {EXPORT_DIR.absolute()}\n")

# Export each table
for table_name in tables:
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Get all rows
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Write to CSV
    csv_path = EXPORT_DIR / f"{table_name}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)  # Header
        writer.writerows(rows)    # Data
    
    row_count = len(rows)
    print(f"✅ {table_name:20} ({row_count:4} rows) → {csv_path.name}")

conn.close()
print(f"\n✅ Export complete! CSV files saved to backup/csv_export/")
