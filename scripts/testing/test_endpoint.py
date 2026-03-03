#!/usr/bin/env python3
"""Test the round-timings endpoint."""

import sys
sys.path.insert(0, '.')

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.contact import Contact
from app.models.interview import Interview
import asyncio

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
            
            for interview in interviews:
                print(f"  - Round {interview.round_number}: {interview.status}, started={interview.started_at}, completed={interview.completed_at}")
            
            # Now test what the endpoint would return
            status_value = contact.status
            current_round = None
            
            if status_value.startswith('round_'):
                current_round = int(status_value.split('_')[1])
            
            print(f"\nParsed current_round: {current_round}")
            
            # Build round timings
            round_timings = []
            
            for round_num in range(1, 5):
                existing_interview = next(
                    (i for i in interviews if i.round_number == round_num),
                    None
                )
                
                if status_value == 'all_rounds_completed':
                    round_timings.append({
                        'roundNumber': round_num,
                        'status': 'completed',
                        'canStart': False,
                        'message': f'Round {round_num} completed'
                    })
                elif current_round and round_num < current_round:
                    round_timings.append({
                        'roundNumber': round_num,
                        'status': 'completed',
                        'canStart': False,
                        'message': f'Round {round_num} completed'
                    })
                elif current_round and round_num == current_round:
                    if existing_interview and existing_interview.started_at:
                        if existing_interview.completed_at:
                            round_timings.append({
                                'roundNumber': round_num,
                                'status': 'completed',
                                'canStart': False,
                                'message': f'Round {round_num} completed'
                            })
                        else:
                            round_timings.append({
                                'roundNumber': round_num,
                                'status': 'active',
                                'canStart': True,
                                'message': f'Continue Round {round_num}'
                            })
                    else:
                        round_timings.append({
                            'roundNumber': round_num,
                            'status': 'available',
                            'canStart': True,
                            'message': 'Start Now'
                        })
                else:
                    round_timings.append({
                        'roundNumber': round_num,
                        'status': 'waiting',
                        'canStart': False,
                        'message': f'Complete Round {round_num - 1} first'
                    })
            
            print("\nRound Timings:")
            for timing in round_timings:
                print(f"  Round {timing['roundNumber']}: {timing['status']} - {timing['message']} (canStart={timing['canStart']})")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
