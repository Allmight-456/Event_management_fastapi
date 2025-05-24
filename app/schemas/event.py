from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.event import RecurrenceType

class EventBase(BaseModel):
    """Base event schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    location: Optional[str] = Field(None, max_length=500, description="Event location")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values, **kwargs):
        """Ensure event end time is after start time."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class EventCreate(EventBase):
    """Schema for event creation."""
    is_recurring: bool = Field(default=False, description="Whether event recurs")
    recurrence_type: RecurrenceType = Field(default=RecurrenceType.NONE)
    recurrence_pattern: Optional[Dict[str, Any]] = Field(None, description="Recurrence pattern details")

class EventUpdate(BaseModel):
    """Schema for event updates - all fields optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None

class EventResponse(EventBase):
    """Schema for event responses."""
    id: int
    owner_id: int
    version: int
    is_recurring: bool
    recurrence_type: RecurrenceType
    recurrence_pattern: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class EventBatchCreate(BaseModel):
    """Schema for batch event creation."""
    events: List[EventCreate] = Field(..., min_items=1, max_items=100, 
                                     description="List of events to create (max 100)")
