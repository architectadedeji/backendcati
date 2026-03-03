#!/usr/bin/env python
"""Seed db_2.sqlite3 with admin user and 35 sample contacts."""
import sqlite3
from datetime import datetime, timedelta
from app.utils.auth import hash_password


def seed_db_2():
    """Seed admin user and 35 contacts."""
    conn = sqlite3.connect("db_2.sqlite3")
    cursor = conn.cursor()
    
    # Create admin user
    try:
        admin_hash = hash_password("admin123")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, phone)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", "admin@example.com", admin_hash, "admin", "+1234567890"))
        conn.commit()
        print("✅ Admin user created")
    except sqlite3.IntegrityError:
        print("ℹ️  Admin user already exists")
    
    # Create 35 sample contacts
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
                 "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    statuses = ["pending", "in_progress", "completed", "declined"]
    base_date = datetime.now() - timedelta(days=60)
    
    # Check existing contacts
    cursor.execute("SELECT COUNT(*) FROM contacts")
    count = cursor.fetchone()[0]
    
    if count < 35:
        contacts_to_add = []
        for i in range(1, 36):
            contacts_to_add.append((
                f"Contact {i:02d}",                    # name
                f"contact{i:02d}@example.com",         # email
                f"+1{200000000 + i:08d}",              # phone
                f"SN{1000 + i}",                       # serial_number
                f"CUID{i:05d}",                        # cuid
                f"TK{5000 + i}",                       # ticket_number
                statuses[(i - 1) % len(statuses)],    # status
                locations[(i - 1) % len(locations)],  # location
                f"Sample contact {i}",                # notes
                (base_date + timedelta(days=i)).isoformat(),  # last_contact
                i % 4,                                 # interview_count
                f"BATCH{i // 10 + 1}",                # batch_number
                f"BS{1000 + i}",                      # batch_serial_number
                (base_date + timedelta(days=i)).isoformat(),  # date_received
                f"Arm {(i % 3) + 1}",                 # study_arm
                "phone"                                # method
            ))
        
        cursor.executemany("""
            INSERT INTO contacts 
            (name, email, phone, serial_number, cuid, ticket_number, status, location, notes, 
             last_contact, interview_count, batch_number, batch_serial_number, 
             date_received, study_arm, method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, contacts_to_add)
        conn.commit()
        print(f"✅ Created 35 sample contacts")
    else:
        print(f"ℹ️  {count} contacts already exist")
    
    # Verify counts
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contacts")
    contacts_count = cursor.fetchone()[0]
    
    print(f"\n📊 Final Database Status (db_2.sqlite3):")
    print(f"   Users: {users_count}")
    print(f"   Contacts: {contacts_count}")
    
    conn.close()


if __name__ == "__main__":
    seed_db_2()
