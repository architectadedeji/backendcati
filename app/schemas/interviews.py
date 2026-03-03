"""Pydantic schemas for interviews."""
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from typing import Optional, List, Any, Literal


class InterviewRoundResponse(BaseModel):
    id: int
    round_number: int
    status: Literal["pending", "active", "completed", "declined_consent"]
    scheduled_at: Optional[datetime] = None
    can_start_interview: bool
    
    model_config = {"from_attributes": True}


class ResponseCreate(BaseModel):
    question_id: int
    answer: Optional[Any] = None


class ResponseUpdate(BaseModel):
    answer: Optional[Any] = None
    completed_at: Optional[datetime] = None


class ResponseSchema(ResponseCreate):
    id: int
    interview_id: int
    contact_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class InterviewCreate(BaseModel):
    contact_id: int
    round_number: int = 1


class InterviewUpdate(BaseModel):
    status: Optional[str] = None
    stage: Optional[int] = None
    current_question_index: Optional[int] = None
    decline_reason: Optional[str] = None
    completed_at: Optional[datetime] = None
    xform_data: Optional[dict] = None


class InterviewResponse(BaseModel):
    id: int
    contact_id: int
    round_number: int
    status: str
    stage: int
    current_question_index: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    decline_reason: Optional[str] = None
    interview_round: Optional[InterviewRoundResponse] = None
    responses: Optional[List[ResponseSchema]] = None
    xform_data: Optional[dict] = None
    form_schema: Optional[dict] = None  # Form schema embedded in response
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
    
    @field_serializer('xform_data', when_used='json')
    def serialize_xform_data(self, value: Optional[dict]) -> Optional[dict]:
        """Serialize xform_data for JSON output."""
        return value


class QuestionSchema(BaseModel):
    id: int
    text: str
    type: Literal["text", "multiple_choice", "scale", "boolean"]
    stage: int
    round: Optional[int] = None
    options: Optional[List[str]] = None
    required: bool
    routing_logic: Optional[Any] = None
    section: Optional[str] = None
    
    model_config = {"from_attributes": True}
