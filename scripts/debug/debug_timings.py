#!/usr/bin/env python3
"""Debug the round timings endpoint."""

import sys
sys.path.insert(0, '.')

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.contact import Contact
from app.models.interview import Interview
from datetime import datetime, timedelta
import asyncio
import json

async def test():
    try:
        async with AsyncSessionLocal() as db:
            # Get first contact
            result = await db.execute(select(Contact).limit(1))
            contact = result.scalar_one_or_none()
            
            if not contact:
                print("ERROR: No contacts found")
                return
            
            print(f"Contact ID: {contact.id}")
            print(f"Contact Name: {contact.name}")
            print(f"Contact Status: {contact.status}")
            
            # Get interviews for this contact
            result = await db.execute(
                select(Interview).where(Interview.contact_id == contact.id)
            )
            interviews = result.scalars().all()
            print(f"Interviews for contact: {len(interviews)}")
            
            # Simulate the endpoint logic
            status_value = contact.status
            current_round = None
            
            if status_value.startswith('round_'):
                current_round = int(status_value.split('_')[1])
            
            # Simulate timing logic
            testing_mode = True
            interval_days = 1 if testing_mode else 30
            
            # Build round timings
            round_timings = []
            
            for round_num in range(1, 5):
                existing_interview = next(
                    (i for i in interviews if i.round_number == round_num),
                    None
                )
                
                timing_entry = {
                    'roundNumber': round_num,
                    'scheduledAt': None,
                    'nextAvailableAt': None
                }
                
                if status_value == 'all_rounds_completed':
                    timing_entry.update({
                        'status': 'completed',
                        'canStart': False,
                        'message': f'Round {round_num} completed',
                        'scheduledAt': existing_interview.completed_at.isoformat() if existing_interview and existing_interview.completed_at else None
                    })
                elif current_round and round_num < current_round:
                    timing_entry.update({
                        'status': 'completed',
                        'canStart': False,
                        'message': f'Round {round_num} completed',
                        'scheduledAt': existing_interview.completed_at.isoformat() if existing_interview and existing_interview.completed_at else None
                    })
                elif current_round and round_num == current_round:
                    if existing_interview and existing_interview.started_at:
                        if existing_interview.completed_at:
                            timing_entry.update({
                                'status': 'completed',
                                'canStart': False,
                                'message': f'Round {round_num} completed',
                                'scheduledAt': existing_interview.completed_at.isoformat()
                            })
                        else:
                            timing_entry.update({
                                'status': 'active',
                                'canStart': True,
                                'message': f'Continue Round {round_num}',
                                'scheduledAt': existing_interview.started_at.isoformat() if existing_interview.started_at else None
                            })
                    else:
                        # Round is available to start (due now)
                        timing_entry.update({
                            'status': 'available',
                            'canStart': True,
                            'message': 'Start Now',
                            'scheduledAt': datetime.utcnow().isoformat()
                        })
                else:
                    # Future rounds - waiting for previous rounds
                    if round_num > 1 and current_round and round_num > current_round:
                        prev_round_num = round_num - 1
                        prev_interview = next(
                            (i for i in interviews if i.round_number == prev_round_num),
                            None
                        )
                        
                        if prev_interview and prev_interview.completed_at:
                            due_date = prev_interview.completed_at + timedelta(days=interval_days)
                            timing_entry['nextAvailableAt'] = due_date.isoformat()
                            timing_entry['scheduledAt'] = due_date.isoformat()
                    
                    timing_entry.update({
                        'status': 'waiting',
                        'canStart': False,
                        'message': f'Complete Round {round_num - 1} first'
                    })
                
                round_timings.append(timing_entry)
                print(f"Round {round_num}: {timing_entry}")
            
            print("\nFull response:")
            response = {
                'contact_id': contact.id,
                'contact_status': status_value,
                'round_timings': round_timings
            }
            print(json.dumps(response, indent=2))
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
