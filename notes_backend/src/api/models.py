# Models for the notes application: User and Note, including Pydantic schemas for API.

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List

# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")

# PUBLIC_INTERFACE
class Token(BaseModel):
    """Response containing a JWT access token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of the token")

# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Shared properties of a note."""
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")

# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Schema for creating a note."""
    pass

# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = Field(None, description="Updated note title")
    content: Optional[str] = Field(None, description="Updated note content")

# PUBLIC_INTERFACE
class NoteOut(NoteBase):
    """Schema for returning a note."""
    id: int = Field(..., description="ID of the note")
    owner_id: int = Field(..., description="ID of the user who owns the note")
    created_at: datetime = Field(..., description="Note creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class NotesListOut(BaseModel):
    """Schema for returning a list of notes."""
    notes: List[NoteOut] = Field(..., description="List of notes")
