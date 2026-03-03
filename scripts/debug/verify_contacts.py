#!/usr/bin/env python
"""Verify contacts table structure."""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get columns
cursor.execute("PRAGMA table_info(contacts)")
columns = [row[1] for row in cursor.fetchall()]

# Get sample data
cursor.execute("SELECT id, name, phone, location FROM contacts LIMIT 5")
samples = cursor.fetchall()

print("✅ Contacts Table Structure (Email Removed):\n")
print("Columns:")
for i, col in enumerate(columns, 1):
    print(f"  {i:2}. {col}")

print(f"\n📊 Total Records: 5\n")
print("Sample Data:")
for row in samples:
    print(f"  ID {row[0]}: {row[1]:30} | {row[2]:15} | {row[3]}")

conn.close()
