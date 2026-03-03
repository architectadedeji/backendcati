#!/usr/bin/env python3
"""Import contacts from CSV file into database"""

import asyncio
import csv
import sys
from datetime import datetime
sys.path.insert(0, '/dev-2026/streamcati/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.contact import Contact

async def main():
    try:
        csv_file = r'c:\Users\PC\Downloads\contacts.csv'
        
        print(f"Importing contacts from {csv_file}...")
        
        engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            # Read CSV file (no header)
            imported_count = 0
            skipped_count = 0
            duplicate_count = 0
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        # CSV structure (based on observed data):
                        # 0: ID, 1: Name, 2: Phone, 3: unknown, 4: unknown, 5: CUID, 
                        # 6: Ticket, 7: Location, 8: Status, 9: unknown, 10: timestamp,
                        # 11: timestamp, 12: unknown, 13: interview_count, 14: batch_num,
                        # 15: date_received, 16: ticket_number_nos, 17: study_arm, 18: method, 19: unknown
                        
                        if len(row) < 9:  # Skip incomplete rows
                            skipped_count += 1
                            continue
                        
                        serial_number = str(row[0]).strip()
                        name = row[1].strip() if len(row) > 1 else ''
                        phone = row[2].strip() if len(row) > 2 else ''
                        cuid = row[5].strip() if len(row) > 5 else ''
                        ticket_number = row[6].strip() if len(row) > 6 else ''
                        location = row[7].strip() if len(row) > 7 else ''
                        status = row[8].strip() if len(row) > 8 else 'round_1'
                        interview_count = int(row[13]) if len(row) > 13 and row[13].isdigit() else 0
                        batch_number = row[14].strip() if len(row) > 14 else ''
                        date_received = row[15].strip() if len(row) > 15 else ''
                        ticket_number_nos = row[16].strip() if len(row) > 16 else ''
                        study_arm = row[17].strip() if len(row) > 17 else ''
                        method = row[18].strip() if len(row) > 18 else ''
                        
                        # Validate status
                        valid_statuses = ['round_1', 'round_2', 'round_3', 'round_4', 'all_rounds_completed']
                        if status not in valid_statuses:
                            status = 'round_1'
                        
                        # Skip if missing required fields
                        if not name or not phone or not serial_number:
                            skipped_count += 1
                            continue
                        
                        # Check if already exists
                        result = await db.execute(
                            select(Contact).where(Contact.serial_number == serial_number)
                        )
                        if result.scalar_one_or_none():
                            duplicate_count += 1
                            continue
                        
                        # Create new contact
                        contact = Contact(
                            name=name[:255],
                            phone=phone[:20],
                            serial_number=serial_number[:255],
                            cuid=cuid[:255] if cuid else None,
                            ticket_number=ticket_number[:255] if ticket_number else None,
                            status=status,
                            location=location[:255] if location else None,
                            interview_count=interview_count,
                            batch_number=batch_number[:100] if batch_number else None,
                            batch_serial_number=None,
                            date_received=date_received[:100] if date_received else None,
                            ticket_number_nos=ticket_number_nos[:100] if ticket_number_nos else None,
                            study_arm=study_arm[:500] if study_arm else None,
                            method=method[:100] if method else None,
                            created_at=datetime.utcnow()
                        )
                        
                        db.add(contact)
                        imported_count += 1
                        
                        if imported_count % 10 == 0:
                            print(f"  Processed {imported_count} records...")
                    
                    except Exception as e:
                        print(f"  Error on row {row_num}: {e}")
                        skipped_count += 1
                
                # Commit all at once
                await db.commit()
            
            print(f"\n✅ Import complete:")
            print(f"  ✅ Imported: {imported_count}")
            print(f"  ⏭️  Duplicates (skipped): {duplicate_count}")
            print(f"  ⚠️  Skipped (missing data): {skipped_count}")
            print(f"  📊 Total: {imported_count + duplicate_count + skipped_count} records processed")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
