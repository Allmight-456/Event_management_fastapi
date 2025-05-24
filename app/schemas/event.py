from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.event import RecurrenceType

class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)

class EventCreate(EventBase):
    start_time: datetime
    end_time: datetime
    is_recurring: bool = False
    recurrence_type: RecurrenceType = RecurrenceType.NONE
    recurrence_pattern: Optional[Dict[str, Any]] = None
    
    @validator('end_time')
    def validate_end_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None

class EventResponse(EventBase):
    id: int
    start_time: datetime
    end_time: datetime
    is_recurring: bool
    recurrence_type: str
    recurrence_pattern: Optional[Dict[str, Any]]
    owner_id: int
    version: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class EventBatchCreate(BaseModel):
    events: List[EventCreate] = Field(..., min_items=1, max_items=50)
