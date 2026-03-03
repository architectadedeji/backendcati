#!/usr/bin/env python
"""Remove email column from contacts table."""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check current contacts count
cursor.execute("SELECT COUNT(*) FROM contacts")
count_before = cursor.fetchone()[0]
print(f"📊 Contacts before: {count_before}")

# Get current schema
cursor.execute("PRAGMA table_info(contacts)")
columns = [row[1] for row in cursor.fetchall()]
print(f"📄 Columns before: {', '.join(columns)}")

# Create new table without email
cursor.execute("""
    CREATE TABLE contacts_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(20),
        serial_number VARCHAR(50),
        cuid VARCHAR(50),
        ticket_number VARCHAR(50),
        status VARCHAR(50),
        location VARCHAR(255),
        notes TEXT,
        last_contact DATETIME,
        interview_count INTEGER DEFAULT 0,
        created_at DATETIME,
        batch_number VARCHAR(50),
        batch_serial_number VARCHAR(50),
        date_received DATETIME,
        ticket_number_nos VARCHAR(50),
        study_arm VARCHAR(255),
        method VARCHAR(50)
    )
""")

# Copy data without email column
cursor.execute("""
    INSERT INTO contacts_new 
    (id, name, phone, serial_number, cuid, ticket_number, status, location, notes, 
     last_contact, interview_count, created_at, batch_number, batch_serial_number, 
     date_received, ticket_number_nos, study_arm, method)
    SELECT 
        id, name, phone, serial_number, cuid, ticket_number, status, location, notes,
        last_contact, interview_count, created_at, batch_number, batch_serial_number,
        date_received, ticket_number_nos, study_arm, method
    FROM contacts
""")

# Drop old table
cursor.execute("DROP TABLE contacts")

# Rename new table
cursor.execute("ALTER TABLE contacts_new RENAME TO contacts")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM contacts")
count_after = cursor.fetchone()[0]

cursor.execute("PRAGMA table_info(contacts)")
new_columns = [row[1] for row in cursor.fetchall()]

print(f"\n✅ Email column removed!")
print(f"📊 Contacts after: {count_after}")
print(f"📄 Columns after: {', '.join(new_columns)}")
print(f"\n✅ Migration complete!")

conn.close()
