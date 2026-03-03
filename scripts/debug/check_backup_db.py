#!/usr/bin/env python
"""Check contents of backup/db.sqlite3."""
import sqlite3

conn = sqlite3.connect('backup/db.sqlite3')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in cursor.fetchall()]

print(f'Tables in backup/db.sqlite3: {len(tables)} tables\n')

for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    
    # Get columns
    cursor.execute(f'PRAGMA table_info({table})')
    columns = [row[1] for row in cursor.fetchall()]
    
    print(f'{table:20} | Records: {count:5} | Columns: {len(columns)}')
    if count > 0:
        print(f'  Columns: {", ".join(columns[:5])}...')

conn.close()
