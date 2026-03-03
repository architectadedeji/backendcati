#!/usr/bin/env python
"""List all tables in db.sqlite3."""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print('Tables in db.sqlite3:\n')
for i, table in enumerate(tables, 1):
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'{i}. {table:30} ({count} records)')

conn.close()
