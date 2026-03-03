"""Contacts API router."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text
from typing import List, Optional

from app.database import get_db
from app.models.contact import Contact
from app.models.interview import Interview
from app.enums import ContactStatus
from sqlalchemy import func
from app.schemas.contacts import ContactCreate, ContactResponse, ContactUpdate
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("/", response_model=dict)
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all contacts with optional filtering and pagination.

    Returns paginated results with count and results.
    """
    # Build query with filters
    query = select(Contact)

    if status:
        query = query.where(Contact.status == status)

    if search:
        # Search in name or serial_number
        search_term = f"%{search}%"
        query = query.where(
            Contact.name.ilike(search_term) |
            Contact.serial_number.ilike(search_term)
        )

    # Get total count of filtered results using a count query
    count_query = select(func.count(Contact.id))
    if status:
        count_query = count_query.where(Contact.status == status)
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(
            Contact.name.ilike(search_term) |
            Contact.serial_number.ilike(search_term)
        )
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply pagination at the SQL level
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    contacts = result.scalars().all()

    return {
        "count": total,
        "skip": skip,
        "limit": limit,
        "results": [ContactResponse.model_validate(contact) for contact in contacts]
    }


@router.get("/contact-statistics/", response_model=dict)
async def contact_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return statistics for contacts."""
    total_contacts_result = await db.execute(select(func.count(Contact.id)))
    total_contacts = total_contacts_result.scalar() or 0

    # Count by status
    status_counts_result = await db.execute(
        select(Contact.status, func.count(Contact.id)).group_by(Contact.status)
    )
    status_counts = {row[0]: row[1] for row in status_counts_result.all()}

    # Attempted = contacts that have at least one completed interview (source of truth: Interview table)
    attempted_result = await db.execute(
        select(func.count(func.distinct(Interview.contact_id))).where(
            Interview.completed_at.isnot(None)
        )
    )
    total_attempted = attempted_result.scalar() or 0

    # Total completed interview attempts across all contacts
    total_attempts_result = await db.execute(
        select(func.count(Interview.id)).where(
            Interview.completed_at.isnot(None)
        )
    )
    total_attempts = total_attempts_result.scalar() or 0

    total_unattempted = total_contacts - total_attempted

    return {
        "total_contacts": total_contacts,
        "status_counts": status_counts,
        "totalAvailableContacts": total_contacts,
        "totalContactsAttempted": total_attempted,
        "numberOfTimesAttempted": total_attempts,
        "totalContactsUnattempted": total_unattempted,
    }


@router.get("/interview-statistics/", response_model=dict)
async def interview_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return statistics for interviews."""
    # Total contacts
    total_contacts_result = await db.execute(select(func.count(Contact.id)))
    total_contacts = total_contacts_result.scalar() or 0

    # Total interviews
    total_interviews_result = await db.execute(select(func.count(Interview.id)))
    total_interviews = total_interviews_result.scalar() or 0

    # Completed interviews (those with completed_at set)
    completed_result = await db.execute(
        select(func.count(Interview.id)).where(Interview.completed_at.isnot(None))
    )
    completed_interviews = completed_result.scalar() or 0

    # "Due" interviews are contacts whose status matches a round but haven't completed that round
    # Count by round based on contact status
    round_1_due_result = await db.execute(
        select(func.count(Contact.id)).where(
            Contact.status == ContactStatus.ROUND_1
        )
    )
    round_1_due = round_1_due_result.scalar() or 0

    round_2_due_result = await db.execute(
        select(func.count(Contact.id)).where(
            Contact.status == ContactStatus.ROUND_2
        )
    )
    round_2_due = round_2_due_result.scalar() or 0

    round_3_due_result = await db.execute(
        select(func.count(Contact.id)).where(
            Contact.status == ContactStatus.ROUND_3
        )
    )
    round_3_due = round_3_due_result.scalar() or 0

    round_4_due_result = await db.execute(
        select(func.count(Contact.id)).where(
            Contact.status == ContactStatus.ROUND_4
        )
    )
    round_4_due = round_4_due_result.scalar() or 0

    # Total due interviews
    total_due_interviews = round_1_due + round_2_due + round_3_due + round_4_due

    # Count by round for completed interviews
    round_1_completed_result = await db.execute(
        select(func.count(Interview.id)).where(
            (Interview.round_number == 1) & (Interview.completed_at.isnot(None))
        )
    )
    round_1_completed = round_1_completed_result.scalar() or 0

    round_2_completed_result = await db.execute(
        select(func.count(Interview.id)).where(
            (Interview.round_number == 2) & (Interview.completed_at.isnot(None))
        )
    )
    round_2_completed = round_2_completed_result.scalar() or 0

    round_3_completed_result = await db.execute(
        select(func.count(Interview.id)).where(
            (Interview.round_number == 3) & (Interview.completed_at.isnot(None))
        )
    )
    round_3_completed = round_3_completed_result.scalar() or 0

    round_4_completed_result = await db.execute(
        select(func.count(Interview.id)).where(
            (Interview.round_number == 4) & (Interview.completed_at.isnot(None))
        )
    )
    round_4_completed = round_4_completed_result.scalar() or 0

    return {
        "total_contacts": total_contacts,
        "total_interviews": total_interviews,
        "completed_interviews": completed_interviews,
        "total_due_interviews": total_due_interviews,
        "round_1_due": round_1_due,
        "round_2_due": round_2_due,
        "round_3_due": round_3_due,
        "round_4_due": round_4_due,
        "round_1_completed": round_1_completed,
        "round_2_completed": round_2_completed,
        "round_3_completed": round_3_completed,
        "round_4_completed": round_4_completed,
    }


@router.get("/{contact_id}/", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific contact by ID."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    return ContactResponse.model_validate(contact)


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new contact."""
    # Check if contact with same serial_number already exists
    result = await db.execute(
        select(Contact).where(
            Contact.serial_number == contact_data.serial_number
        )
    )
    
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact with this serial_number already exists"
        )
    
    contact = Contact(**contact_data.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    
    return ContactResponse.model_validate(contact)


@router.patch("/{contact_id}/", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a contact."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    # Update only provided fields
    update_data = contact_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contact, key, value)
    
    await db.commit()
    await db.refresh(contact)
    
    return ContactResponse.model_validate(contact)


@router.delete("/{contact_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a contact."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    await db.delete(contact)
    await db.commit()


@router.post("/normalize-status/", response_model=dict)
async def normalize_contact_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Normalize all contact status values to use correct enum values (lowercase).
    Fixes data integrity issues from mixed-case status storage.
    """
    # Map of old uppercase names to correct lowercase enum values
    status_mapping = {
        "ROUND_1": ContactStatus.ROUND_1.value,
        "ROUND_2": ContactStatus.ROUND_2.value,
        "ROUND_3": ContactStatus.ROUND_3.value,
        "ROUND_4": ContactStatus.ROUND_4.value,
        "ALL_ROUNDS_COMPLETED": ContactStatus.ALL_ROUNDS_COMPLETED.value,
    }

    updated_count = 0
    for old_status, new_status in status_mapping.items():
        result = await db.execute(
            text("UPDATE contacts SET status = :new_status WHERE status = :old_status"),
            {"new_status": new_status, "old_status": old_status}
        )
        updated_count += result.rowcount

    await db.commit()

    return {
        "message": f"Normalized {updated_count} contact status values",
        "updated_count": updated_count,
    }
