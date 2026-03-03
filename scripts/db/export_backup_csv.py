#!/usr/bin/env python
"""Export all tables from backup/db.sqlite3 as CSV files."""
import sqlite3
import csv
from pathlib import Path

DATABASE_PATH = "backup/db.sqlite3"
EXPORT_DIR = Path("backup/csv_export_backup")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Connect to database
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Get all table names (excluding Django internal tables if desired)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in cursor.fetchall()]

print(f"📊 Exporting backup/db.sqlite3 - Found {len(tables)} tables")
print(f"📁 Exporting to: {EXPORT_DIR.absolute()}\n")

# Export each table
total_records = 0
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
    total_records += row_count
    print(f"✅ {table_name:30} ({row_count:5} rows) → {csv_path.name}")

conn.close()
print(f"\n✅ Export complete!")
print(f"📊 Total records exported: {total_records}")
print(f"📁 CSV files saved to: backup/csv_export_backup/")
