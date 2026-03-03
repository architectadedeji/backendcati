#!/usr/bin/env python
"""Check backup database contents."""
import sqlite3

conn = sqlite3.connect('backup/db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in cursor.fetchall()]

print(f'Tables in backup/db.sqlite3: {tables}\n')
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'  {table}: {count} records')

conn.close()
