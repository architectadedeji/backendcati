"""Interviews API router."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import List, Optional
import json
from pathlib import Path

from app.database import get_db


def _iso_utc(dt: Optional[datetime]) -> Optional[str]:
    """Format a datetime as ISO 8601 with Z suffix to indicate UTC."""
    if dt is None:
        return None
    return dt.isoformat() + "Z"
from app.models.interview import Interview, InterviewRound, Response
from app.models.contact import Contact
from app.enums import ContactStatus
from app.schemas.interviews import InterviewCreate, InterviewResponse, InterviewUpdate, ResponseCreate, QuestionSchema
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/interviews", tags=["interviews"])


def load_form_schema() -> Optional[dict]:
    """Load form schema from file, return None if not found."""
    try:
        schema_path = Path(__file__).parent.parent.parent.parent / "streamcati-frontend" / "public" / "form_schema_with_nav.json"
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None


@router.post("/contact/{contact_id}/round/{round_number}/start/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    contact_id: int,
    round_number: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start or create an interview for a contact."""
    # Check if contact exists
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )

    # Block if all rounds are already completed
    if contact.status == ContactStatus.ALL_ROUNDS_COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All interview rounds have been completed for this contact"
        )

    # Ensure InterviewRound exists for this round
    result = await db.execute(
        select(InterviewRound).where(
            and_(InterviewRound.contact_id == contact_id, InterviewRound.round_number == round_number)
        )
    )
    interview_round = result.scalar_one_or_none()
    
    if not interview_round:
        # Create InterviewRound if it doesn't exist
        interview_round = InterviewRound(
            contact_id=contact_id,
            round_number=round_number,
            status="active",
            can_start_interview=True
        )
        db.add(interview_round)
    
    # Check if interview for this round already exists
    result = await db.execute(
        select(Interview).where(
            and_(Interview.contact_id == contact_id, Interview.round_number == round_number)
        )
    )
    interview = result.scalar_one_or_none()
    
    # If not exist, create new interview
    if not interview:
        interview = Interview(
            contact_id=contact_id,
            round_number=round_number,
            status=f"round_{round_number}",
            started_at=datetime.utcnow()
        )
        db.add(interview)
        await db.commit()
        await db.refresh(interview)
    elif not interview.started_at:
        # If exists but not started, mark as started now
        interview.started_at = datetime.utcnow()
        await db.commit()
        await db.refresh(interview)
    
    # Build response dict manually to avoid async lazy-loading errors
    form_schema = load_form_schema()
    interview_data = {
        'id': interview.id,
        'contact_id': interview.contact_id,
        'round_number': interview.round_number,
        'status': interview.status,
        'stage': interview.stage,
        'current_question_index': interview.current_question_index,
        'started_at': _iso_utc(interview.started_at),
        'completed_at': _iso_utc(interview.completed_at),
        'decline_reason': interview.decline_reason,
        'xform_data': interview.xform_data,
        'form_schema': form_schema,
        'created_at': _iso_utc(interview.created_at),
        'updated_at': _iso_utc(interview.updated_at),
    }

    return interview_data


# IMPORTANT: Static path routes MUST come before /{interview_id}/ to avoid
# FastAPI matching "due-rounds" or "response" as an interview_id parameter.

@router.get("/submitted/")
async def list_submitted_interviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    round_number: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all completed/submitted interviews with contact info."""
    query = select(Interview).where(Interview.completed_at.isnot(None))

    if round_number:
        query = query.where(Interview.round_number == round_number)

    query = query.order_by(Interview.completed_at.desc())

    # Get total count
    count_query = select(Interview).where(Interview.completed_at.isnot(None))
    if round_number:
        count_query = count_query.where(Interview.round_number == round_number)
    count_result = await db.execute(count_query)
    total = len(count_result.fetchall())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    interviews = result.scalars().all()

    # Gather contact IDs and fetch contacts in one query
    contact_ids = list(set(i.contact_id for i in interviews))
    contacts_map = {}
    if contact_ids:
        contacts_result = await db.execute(
            select(Contact).where(Contact.id.in_(contact_ids))
        )
        for c in contacts_result.scalars().all():
            contacts_map[c.id] = {
                'id': c.id,
                'name': c.name,
                'phone': c.phone,
                'serial_number': c.serial_number,
                'cuid': c.cuid,
                'ticket_number': c.ticket_number,
                'location': c.location,
                'study_arm': c.study_arm,
            }

    # Build results with contact info
    results = []
    for interview in interviews:
        contact_info = contacts_map.get(interview.contact_id, {})

        # Filter by search query on contact name/cuid/ticket
        if search:
            search_lower = search.lower()
            match = False
            for field in ['name', 'cuid', 'ticket_number', 'phone', 'serial_number']:
                val = contact_info.get(field)
                if val and search_lower in str(val).lower():
                    match = True
                    break
            if not match:
                total -= 1
                continue

        # Count how many form fields have answers
        xform = interview.xform_data or {}
        answered_count = sum(1 for v in xform.values() if v is not None and v != '')

        results.append({
            'id': interview.id,
            'contact_id': interview.contact_id,
            'contact': contact_info,
            'round_number': interview.round_number,
            'status': interview.status,
            'started_at': _iso_utc(interview.started_at),
            'completed_at': _iso_utc(interview.completed_at),
            'answered_count': answered_count,
            'xform_data': interview.xform_data,
        })

    return {
        "count": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
        "results": results,
    }


@router.get("/due-rounds/")
async def get_due_rounds(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all interviews with due rounds that can be started."""
    try:
        # Get all interview rounds where can_start_interview is True
        result = await db.execute(
            select(InterviewRound).where(InterviewRound.can_start_interview == True)
        )
        rounds = result.scalars().all()
        
        # Convert to interview responses (enriched with contact data)
        interviews = []
        
        for round in rounds:
            interview_result = await db.execute(
                select(Interview).where(
                    and_(Interview.contact_id == round.contact_id, Interview.round_number == round.round_number)
                )
            )
            interview = interview_result.scalar_one_or_none()
            
            if interview:
                interview_dict = {
                    'id': interview.id,
                    'contact_id': interview.contact_id,
                    'round_number': interview.round_number,
                    'status': interview.status,
                    'stage': interview.stage,
                    'current_question_index': interview.current_question_index,
                    'started_at': _iso_utc(interview.started_at),
                    'completed_at': _iso_utc(interview.completed_at),
                    'decline_reason': interview.decline_reason,
                    'xform_data': interview.xform_data,
                    'form_schema': None,
                    'created_at': _iso_utc(interview.created_at),
                    'updated_at': _iso_utc(interview.updated_at),
                }
                interviews.append(interview_dict)
        
        return {
            "count": len(interviews),
            "results": interviews
        }
    except Exception as e:
        print(f"ERROR in get_due_rounds: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/questions/", response_model=dict)
async def get_questions(
    round: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get questions, optionally filtered by round.
    """
    return {
        "results": [],
        "count": 0
    }


@router.get("/")
async def list_interviews(
    contact_id: Optional[int] = Query(None),
    round_number: Optional[int] = Query(None),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all interviews with optional filtering.
    
    Returns paginated results.
    """
    query = select(Interview)
    
    if contact_id:
        query = query.where(Interview.contact_id == contact_id)
    
    if round_number:
        query = query.where(Interview.round_number == round_number)
    
    # Get total count (apply same filters as main query)
    count_query = select(Interview)
    if contact_id:
        count_query = count_query.where(Interview.contact_id == contact_id)
    if round_number:
        count_query = count_query.where(Interview.round_number == round_number)
    count_result = await db.execute(count_query)
    total = len(count_result.fetchall())
    
    # Apply pagination
    query = query.limit(page_size)
    result = await db.execute(query)
    interviews = result.scalars().all()
    
    # Build interview dicts manually
    interview_list = []
    for interview in interviews:
        interview_dict = {
            'id': interview.id,
            'contact_id': interview.contact_id,
            'round_number': interview.round_number,
            'status': interview.status,
            'stage': interview.stage,
            'current_question_index': interview.current_question_index,
            'started_at': _iso_utc(interview.started_at),
            'completed_at': _iso_utc(interview.completed_at),
            'decline_reason': interview.decline_reason,
            'xform_data': interview.xform_data,
            'form_schema': None,
            'created_at': _iso_utc(interview.created_at),
            'updated_at': _iso_utc(interview.updated_at),
        }
        interview_list.append(interview_dict)
    
    return {
        "count": total,
        "page_size": page_size,
        "results": interview_list
    }


@router.get("/{interview_id}/", response_model=InterviewResponse)
async def get_interview(
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific interview by ID."""
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Build response dict manually to avoid async lazy-loading errors
    form_schema = load_form_schema()
    interview_data = {
        'id': interview.id,
        'contact_id': interview.contact_id,
        'round_number': interview.round_number,
        'status': interview.status,
        'stage': interview.stage,
        'current_question_index': interview.current_question_index,
        'started_at': _iso_utc(interview.started_at),
        'completed_at': _iso_utc(interview.completed_at),
        'decline_reason': interview.decline_reason,
        'xform_data': interview.xform_data,
        'form_schema': form_schema,
        'created_at': _iso_utc(interview.created_at),
        'updated_at': _iso_utc(interview.updated_at),
    }

    return interview_data


@router.post("/response/", status_code=status.HTTP_201_CREATED)
async def save_response(
    response_data: ResponseCreate,
    interview_id: int = Query(...),
    contact_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a response to an interview question."""
    # Check if interview exists
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Check if response for this question already exists
    result = await db.execute(
        select(Response).where(
            and_(Response.interview_id == interview_id, Response.question_id == response_data.question_id)
        )
    )
    existing_response = result.scalar_one_or_none()
    
    if existing_response:
        # Update existing response
        existing_response.answer = response_data.answer
        existing_response.completed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing_response)
        return {"id": existing_response.id, "status": "updated"}
    else:
        # Create new response
        response = Response(
            interview_id=interview_id,
            question_id=response_data.question_id,
            contact_id=contact_id,
            answer=response_data.answer,
            completed_at=datetime.utcnow()
        )
        db.add(response)
        await db.commit()
        await db.refresh(response)
        return {"id": response.id, "status": "created"}


@router.patch("/{interview_id}/", response_model=InterviewResponse)
async def update_interview(
    interview_id: int,
    interview_data: InterviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an interview."""
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Update only provided fields
    update_data = interview_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(interview, key, value)
    
    await db.commit()
    await db.refresh(interview)
    
    # Build dict manually to avoid async lazy-loading issues
    interview_dict = {
        'id': interview.id,
        'contact_id': interview.contact_id,
        'round_number': interview.round_number,
        'status': interview.status,
        'stage': interview.stage,
        'current_question_index': interview.current_question_index,
        'started_at': _iso_utc(interview.started_at),
        'completed_at': _iso_utc(interview.completed_at),
        'decline_reason': interview.decline_reason,
        'interview_round': None,
        'responses': [],
        'xform_data': interview.xform_data,
        'form_schema': None,
        'created_at': _iso_utc(interview.created_at),
        'updated_at': _iso_utc(interview.updated_at),
    }
    return interview_dict


@router.post("/{interview_id}/xform-submit/", response_model=dict)
async def xform_submit(
    interview_id: int,
    xform_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit xform data for an interview."""
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Extract form_data from wrapper if frontend sends {form_data: {...}, status: ...}
    actual_form_data = xform_data.get('form_data', xform_data) if isinstance(xform_data, dict) else xform_data
    
    # Store xform data and mark as completed
    interview.xform_data = actual_form_data
    interview.status = 'completed'
    interview.completed_at = datetime.utcnow()

    # Also update the associated InterviewRound status
    round_result = await db.execute(
        select(InterviewRound).where(
            and_(
                InterviewRound.contact_id == interview.contact_id,
                InterviewRound.round_number == interview.round_number
            )
        )
    )
    interview_round = round_result.scalar_one_or_none()
    if interview_round:
        interview_round.status = "completed"
        interview_round.can_start_interview = False

    await db.commit()
    await db.refresh(interview)
    
    # Get the contact and update status based on completed round
    contact = await db.execute(
        select(Contact).where(Contact.id == interview.contact_id)
    )
    contact_obj = contact.scalar_one_or_none()
    
    if contact_obj:
        # Update contact status to next round using enum for data integrity
        current_round = interview.round_number

        if current_round == 4:
            # For round 4, verify all rounds are completed before marking as complete
            result = await db.execute(
                select(Interview).where(Interview.contact_id == interview.contact_id)
            )
            all_interviews = result.scalars().all()

            completed_rounds = [
                i.round_number for i in all_interviews
                if i.completed_at is not None
            ]

            if set(completed_rounds) >= {1, 2, 3, 4}:
                contact_obj.status = ContactStatus.ALL_ROUNDS_COMPLETED
            else:
                contact_obj.status = ContactStatus.ROUND_4
        else:
            # Advance to next round using enum
            next_status_map = {
                1: ContactStatus.ROUND_2,
                2: ContactStatus.ROUND_3,
                3: ContactStatus.ROUND_4,
            }
            contact_obj.status = next_status_map.get(current_round, contact_obj.status)

        # Update interview tracking fields
        contact_obj.interview_count = (contact_obj.interview_count or 0) + 1
        contact_obj.last_contact = datetime.utcnow()

        await db.commit()
        await db.refresh(contact_obj)
    
    return {"status": "submitted", "interview_id": interview.id}


@router.get("/contact/{contact_id}/round-timings/")
async def get_contact_round_timings(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get round timings based on contact's current status with scheduled dates.
    """
    import json
    from datetime import timedelta
    import os
    
    # Get contact
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    # Get all interviews for this contact
    result = await db.execute(
        select(Interview).where(Interview.contact_id == contact_id)
    )
    interviews = result.scalars().all()
    
    # Get system config for timing rules
    testing_mode = os.getenv('TESTING_MODE', 'false').lower() == 'true'
    interval_days = 1 if testing_mode else 30  # Testing: 1 day, Production: 30 days
    
    # Parse contact status to determine round availability
    # Ensure we work with the string value (handles both enum members and raw strings)
    status_value = contact.status.value if hasattr(contact.status, 'value') else str(contact.status)
    current_round = None

    if status_value.startswith('round_'):
        current_round = int(status_value.split('_')[1])
    
    # Build round timings based on contact status
    round_timings_list = []
    
    for round_num in range(1, 5):
        # Find existing interview for this round
        existing_interview = next(
            (i for i in interviews if i.round_number == round_num),
            None
        )
        
        round_data = {
            'roundNumber': round_num,
            'status': 'unknown',
            'canStart': False,
            'message': 'Loading...',
            'scheduledAt': None,
            'nextAvailableAt': None
        }
        
        if status_value == 'all_rounds_completed':
            # For all rounds completed, use database if available, otherwise contact created_at
            scheduled_date = None
            if existing_interview and existing_interview.completed_at:
                scheduled_date = _iso_utc(existing_interview.completed_at)
            else:
                # Safe fallback: use contact creation date (assumes interview happened around signup)
                scheduled_date = _iso_utc(contact.created_at)
            
            round_data.update({
                'status': 'completed',
                'canStart': False,
                'message': f'Round {round_num} completed',
                'scheduledAt': scheduled_date
            })
        elif current_round and round_num < current_round:
            # For past rounds, use database if available, otherwise contact created_at
            scheduled_date = None
            if existing_interview and existing_interview.completed_at:
                scheduled_date = _iso_utc(existing_interview.completed_at)
            else:
                # Safe fallback: use contact creation date (assumes interview happened around signup)
                scheduled_date = _iso_utc(contact.created_at)
            
            round_data.update({
                'status': 'completed',
                'canStart': False,
                'message': f'Round {round_num} completed',
                'scheduledAt': scheduled_date
            })
        elif current_round and round_num == current_round:
            if existing_interview and existing_interview.started_at:
                if existing_interview.completed_at:
                    round_data.update({
                        'status': 'completed',
                        'canStart': False,
                        'message': f'Round {round_num} completed',
                        'scheduledAt': _iso_utc(existing_interview.completed_at)
                    })
                else:
                    round_data.update({
                        'status': 'active',
                        'canStart': True,
                        'message': f'Continue Round {round_num}',
                        'scheduledAt': _iso_utc(existing_interview.started_at)
                    })
            else:
                # Round is available to start right now
                current_time = _iso_utc(datetime.utcnow())
                round_data.update({
                    'status': 'available',
                    'canStart': True,
                    'message': 'Start Now',
                    'scheduledAt': current_time
                })
        else:
            # Future rounds - waiting
            round_data.update({
                'status': 'waiting',
                'canStart': False,
                'message': f'Complete Round {round_num - 1} first'
            })
            
            # Calculate when next round will be available
            if current_round and round_num > current_round:
                # Check if previous round is completed
                prev_round_num = round_num - 1
                prev_int = next((i for i in interviews if i.round_number == prev_round_num), None)
                
                if prev_int and prev_int.completed_at:
                    # Previous round completed - schedule next based on completion + interval
                    future_date = prev_int.completed_at + timedelta(days=interval_days)
                else:
                    # Previous round not completed - estimate based on current round's expected completion
                    if current_round == round_num - 1:
                        # Previous round is the current one - estimate completion
                        if existing_interview and existing_interview.started_at:
                            # Assume round takes ~30 minutes, or use standard 30-day interval
                            future_date = existing_interview.started_at + timedelta(days=interval_days)
                        else:
                            # Current round not started yet - use current time + interval
                            future_date = datetime.utcnow() + timedelta(days=interval_days)
                    else:
                        # Fallback: current time + days for each round in between
                        days_from_now = (round_num - current_round) * interval_days
                        future_date = datetime.utcnow() + timedelta(days=days_from_now)
                
                round_data['nextAvailableAt'] = _iso_utc(future_date)
                round_data['scheduledAt'] = _iso_utc(future_date)
        
        round_timings_list.append(round_data)
    
    return {
        'contact_id': contact_id,
        'contact_status': status_value,
        'round_timings': round_timings_list
    }


