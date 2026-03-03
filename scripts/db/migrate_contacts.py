"""Migrate contacts from SQLite to MySQL database."""
import sqlite3
import asyncio
from datetime import datetime
from sqlalchemy import insert, text
from app.database import AsyncSessionLocal
from app.models.contact import Contact


async def migrate_contacts():
    """Extract contacts from SQLite and insert into MySQL."""
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('db.sqlite3')
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    # Check if contacts table exists in SQLite
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts_contact'")
    if not cursor.fetchone():
        print("[ERROR] No contacts_contact table found in SQLite database")
        sqlite_conn.close()
        return
    
    # Read all contacts from SQLite
    cursor.execute("""
        SELECT id, name, email, phone, serialNumber, cuid, ticketNumber, 
               status, location, notes, last_contact, created_at,
               batchNumber, batchSerialNumber, dateReceived, ticketNumberNos, 
               studyArm, method
        FROM contacts_contact
    """)
    contacts = cursor.fetchall()
    sqlite_conn.close()
    
    if not contacts:
        print("[WARN] No contacts found in SQLite database")
        return
    
    print(f"[INFO] Found {len(contacts)} contacts in SQLite")
    
    # Insert into MySQL
    async with AsyncSessionLocal() as session:
        try:
            # First, disable foreign key checks
            print("[INFO] Disabling foreign key constraints...")
            await session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            await session.commit()
            
            # Clear existing contacts
            print("[INFO] Clearing existing contacts and related data...")
            await session.execute(text("DELETE FROM interview_rounds"))
            await session.execute(text("DELETE FROM responses"))
            await session.execute(text("DELETE FROM interviews"))
            await session.execute(text("DELETE FROM contacts"))
            await session.commit()
            print("[SUCCESS] Cleared existing data")
            
            # Re-enable foreign key checks
            await session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            await session.commit()
            print("[INFO] Re-enabled foreign key constraints")
            
            contact_data = []
            for row in contacts:
                # Parse datetime fields
                last_contact = None
                if row['last_contact']:
                    try:
                        last_contact = datetime.fromisoformat(row['last_contact'])
                    except:
                        last_contact = None
                
                created_at = None
                if row['created_at']:
                    try:
                        created_at = datetime.fromisoformat(row['created_at'])
                    except:
                        created_at = datetime.utcnow()
                else:
                    created_at = datetime.utcnow()
                
                # Generate email if missing - format: name_id@streamcati.dev
                email = row['email']
                if not email:
                    # Create email from name and ID
                    name_slug = row['name'].lower().replace(' ', '_').replace("'", '')
                    email = f"{name_slug}_{row['id']}@streamcati.dev"
                
                # Make serial numbers unique by appending ID if there are duplicates
                serial_number = row['serialNumber']
                if serial_number:
                    serial_number = f"{serial_number}-{row['id']}"
                else:
                    serial_number = f"SN-{row['id']}"
                
                # Map status values from SQLite to valid ones
                status = row['status'] or 'round_1'
                status_map = {
                    'not_started': 'round_1',
                    'round_1': 'round_1',
                    'round_2': 'round_2',
                    'round_3': 'round_3',
                    'round_4': 'round_4',
                    'all_rounds_completed': 'all_rounds_completed',
                }
                status = status_map.get(status, 'round_1')
                
                contact_data.append({
                    'id': row['id'],
                    'name': row['name'],
                    'email': email,
                    'phone': row['phone'],
                    'serial_number': serial_number,
                    'cuid': row['cuid'],
                    'ticket_number': row['ticketNumber'],
                    'status': status,
                    'location': row['location'],
                    'notes': row['notes'],
                    'last_contact': last_contact,
                    'interview_count': 0,
                    'created_at': created_at,
                    'batch_number': row['batchNumber'],
                    'batch_serial_number': row['batchSerialNumber'],
                    'date_received': row['dateReceived'],
                    'ticket_number_nos': row['ticketNumberNos'],
                    'study_arm': row['studyArm'],
                    'method': row['method'],
                })
            
            # Insert all contacts
            stmt = insert(Contact).values(contact_data)
            await session.execute(stmt)
            await session.commit()
            
            print(f"[SUCCESS] Successfully migrated {len(contact_data)} contacts to MySQL")
            
            # Verify count
            count_result = await session.execute(text("SELECT COUNT(*) as count FROM contacts"))
            count = count_result.scalar()
            print(f"[SUCCESS] MySQL contacts table now has {count} records")
            
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(migrate_contacts())
