#!/usr/bin/env python
"""Import contacts from backup/db.sqlite3 into db.sqlite3 (with email fallback)."""
import sqlite3
from datetime import datetime

# Connect to both databases
backup_conn = sqlite3.connect('backup/db.sqlite3')
backup_cursor = backup_conn.cursor()

main_conn = sqlite3.connect('db.sqlite3')
main_cursor = main_conn.cursor()

# Clear existing contacts first
main_cursor.execute("DELETE FROM contacts")
main_conn.commit()
print("✅ Cleared existing contacts\n")

# Get contacts from backup database
backup_cursor.execute("SELECT * FROM contacts_contact ORDER BY id")
backup_contacts = backup_cursor.fetchall()

# Get column names from backup
backup_cursor.execute("PRAGMA table_info(contacts_contact)")
backup_columns = [row[1] for row in backup_cursor.fetchall()]

print(f"📊 Found {len(backup_contacts)} contacts in backup/db.sqlite3\n")

# Import contacts
success_count = 0
for idx, contact in enumerate(backup_contacts, 1):
    contact_dict = dict(zip(backup_columns, contact))
    
    try:
        # Generate email if missing
        email = contact_dict.get('email')
        if not email:
            name = contact_dict.get('name', f'Contact{idx}')
            # Create placeholder email from name
            email = name.lower().replace(' ', '_') + f"_{idx}@example.com"
        
        # Insert with mapped columns
        main_cursor.execute("""
            INSERT INTO contacts 
            (name, email, phone, serial_number, cuid, ticket_number, status, location, notes, 
             last_contact, interview_count, batch_number, batch_serial_number, 
             date_received, study_arm, method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contact_dict.get('name'),
            email,  # Use generated email if missing
            contact_dict.get('phone'),
            contact_dict.get('serialNumber'),
            contact_dict.get('cuid'),
            contact_dict.get('ticketNumber'),
            contact_dict.get('status'),
            contact_dict.get('location'),
            contact_dict.get('notes'),
            contact_dict.get('last_contact'),
            contact_dict.get('interview_count', 0),
            contact_dict.get('batchNumber'),
            contact_dict.get('batchSerialNumber'),
            contact_dict.get('dateReceived'),
            contact_dict.get('studyArm'),
            contact_dict.get('method')
        ))
        success_count += 1
    except Exception as e:
        print(f"❌ Error importing contact{idx}: {e}")

main_conn.commit()

# Verify import
main_cursor.execute("SELECT COUNT(*) FROM contacts")
final_count = main_cursor.fetchone()[0]

print(f"✅ Imported {success_count}/{len(backup_contacts)} contacts")
print(f"✅ Total contacts in db.sqlite3: {final_count}\n")

# Show sample
main_cursor.execute("SELECT id, name, email, phone, location, status FROM contacts LIMIT 10")
samples = main_cursor.fetchall()
print("Sample imported contacts:")
for row in samples:
    print(f"  [{row[0]:2}] {row[1]:30} | {row[2]:35} | {row[4]}")

backup_conn.close()
main_conn.close()

print(f"\n✅ Import complete! All {final_count} contacts imported.")
