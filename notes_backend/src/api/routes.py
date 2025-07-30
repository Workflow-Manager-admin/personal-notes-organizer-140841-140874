# API routes: Authentication, CRUD for notes, Search
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import db_models
from .database import get_db
from .auth import (
    hash_password, verify_password, create_access_token, get_current_user_email
)

from .models import (
    UserCreate,
    UserLogin,
    Token,
    NoteCreate,
    NoteUpdate,
    NoteOut,
    NotesListOut,
)

router = APIRouter()

# ==========================
# AUTH ROUTES
# ==========================

@router.post(
    "/auth/register",
    response_model=Token,
    summary="Register a new user",
    description="Creates a new user account and returns a JWT access token.",
    tags=["authentication"]
)
# PUBLIC_INTERFACE
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user after checking for existing email."""
    if db.query(db_models.User).filter_by(email=user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = db_models.User(email=user_data.email, hashed_password=hash_password(user_data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token(subject=new_user.email)
    return Token(access_token=token, token_type="bearer")

@router.post(
    "/auth/login",
    response_model=Token,
    summary="Login a user",
    description="Authenticate with email and password to get a JWT access token.",
    tags=["authentication"]
)
# PUBLIC_INTERFACE
def login_user(login: UserLogin, db: Session = Depends(get_db)):
    """Authenticates a user and returns JWT."""
    user = db.query(db_models.User).filter_by(email=login.email).first()
    if not user or not verify_password(login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(subject=user.email)
    return Token(access_token=token, token_type="bearer")


# ==========================
# NOTES ROUTES
# ==========================

@router.post(
    "/notes",
    response_model=NoteOut,
    status_code=201,
    summary="Create a note",
    description="Create a new note for the authenticated user.",
    tags=["notes"]
)
# PUBLIC_INTERFACE
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email),
):
    """Create a new note belonging to the authenticated user."""
    owner = db.query(db_models.User).filter_by(email=user_email).first()
    db_note = db_models.Note(title=note.title, content=note.content, owner_id=owner.id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return NoteOut(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        owner_id=db_note.owner_id,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at,
    )

@router.get(
    "/notes",
    response_model=NotesListOut,
    summary="List notes",
    description="Get all notes of the authenticated user (optionally search by keyword).",
    tags=["notes"]
)
# PUBLIC_INTERFACE
def list_notes(
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email),
    search: str = Query("", description="Optional search by keyword"),
):
    """List all notes for the current user, optionally filtered by a search term."""
    owner = db.query(db_models.User).filter_by(email=user_email).first()
    query = db.query(db_models.Note).filter_by(owner_id=owner.id)
    if search:
        query = query.filter(
            (db_models.Note.title.ilike(f"%{search}%")) |
            (db_models.Note.content.ilike(f"%{search}%"))
        )
    db_notes = query.order_by(db_models.Note.updated_at.desc()).all()
    notes_out = [
        NoteOut(
            id=note.id,
            title=note.title,
            content=note.content,
            owner_id=note.owner_id,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
        for note in db_notes
    ]
    return NotesListOut(notes=notes_out)

@router.get(
    "/notes/{note_id}",
    response_model=NoteOut,
    summary="Get a note",
    description="Retrieve a specific note by ID for the authenticated user.",
    tags=["notes"]
)
# PUBLIC_INTERFACE
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email),
):
    """Retrieve a single note by ID for the current user."""
    owner = db.query(db_models.User).filter_by(email=user_email).first()
    note = db.query(db_models.Note).filter_by(id=note_id, owner_id=owner.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteOut(
        id=note.id,
        title=note.title,
        content=note.content,
        owner_id=note.owner_id,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )

@router.put(
    "/notes/{note_id}",
    response_model=NoteOut,
    summary="Update a note",
    description="Update title or content of a note owned by the authenticated user.",
    tags=["notes"]
)
# PUBLIC_INTERFACE
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email),
):
    """Update title/content of an existing note by ID."""
    owner = db.query(db_models.User).filter_by(email=user_email).first()
    note = db.query(db_models.Note).filter_by(id=note_id, owner_id=owner.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    db.commit()
    db.refresh(note)
    return NoteOut(
        id=note.id,
        title=note.title,
        content=note.content,
        owner_id=note.owner_id,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )

@router.delete(
    "/notes/{note_id}",
    status_code=204,
    summary="Delete a note",
    description="Delete a note owned by the authenticated user.",
    tags=["notes"]
)
# PUBLIC_INTERFACE
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email),
):
    """Delete a note by ID if owned by the current user."""
    owner = db.query(db_models.User).filter_by(email=user_email).first()
    note = db.query(db_models.Note).filter_by(id=note_id, owner_id=owner.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None
