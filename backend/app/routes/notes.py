"""
Notes CRUD Routes - FastAPI Implementation
Full async support with proper Pydantic validation
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.extensions import get_db
from app.models import Note, Tag, Folder
from app.routes.auth import get_current_user, User

router = APIRouter()


# Pydantic Schemas for Request/Response Validation
class NoteCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = ""
    folder_id: Optional[int] = None
    tag_ids: List[int] = []
    is_pinned: bool = False


class NoteUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    folder_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


class NoteResponse(BaseModel):
    """Response schema for note (matches to_dict output)"""
    id: int
    title: str
    content: Optional[str] = None
    is_pinned: bool
    is_archived: bool
    owner_id: int
    folder_id: Optional[int] = None
    tags: List[dict] = []
    attachments: List[dict] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[dict])
async def list_notes(
    q: Optional[str] = Query(None, description="Search query"),
    folder_id: Optional[int] = Query(None, description="Filter by folder"),
    tag_id: Optional[int] = Query(None, description="Filter by tag"),
    archived: bool = Query(False, description="Show archived notes"),
    pinned: Optional[bool] = Query(None, description="Filter pinned notes"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all notes for current user.
    
    Supports filtering by:
    - Search query (title + content)
    - Folder ID
    - Tag ID
    - Archive status
    - Pin status
    """
    # Build base query
    query = select(Note).where(
        Note.owner_id == current_user.id,
        Note.is_archived == archived
    )
    
    # Apply filters
    if folder_id is not None:
        query = query.where(Note.folder_id == folder_id)
    
    if tag_id is not None:
        query = query.where(Note.tags.any(Tag.id == tag_id))
    
    if pinned is not None:
        query = query.where(Note.is_pinned == pinned)
    
    if q:
        search = f"%{q}%"
        query = query.where(
            or_(Note.title.ilike(search), Note.content.ilike(search))
        )
    
    # Order: pinned first, then by updated_at desc
    query = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
    
    result = await db.execute(query)
    notes = result.scalars().all()
    
    return [note.to_dict(include_content=False) for note in notes]


@router.post("", response_model=dict, status_code=201)
async def create_note(
    data: NoteCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new note"""
    # Validate folder exists and belongs to user
    if data.folder_id:
        result = await db.execute(
            select(Folder).where(Folder.id == data.folder_id, Folder.owner_id == current_user.id)
        )
        folder = result.scalar_one_or_none()
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
    
    # Create note
    note = Note(
        title=data.title,
        content=data.content,
        folder_id=data.folder_id,
        is_pinned=data.is_pinned,
        owner_id=current_user.id,
    )
    
    # Add tags if provided
    if data.tag_ids:
        result = await db.execute(
            select(Tag).where(Tag.id.in_(data.tag_ids), Tag.owner_id == current_user.id)
        )
        tags = result.scalars().all()
        note.tags.extend(tags)
    
    db.add(note)
    await db.commit()
    await db.refresh(note)
    
    return note.to_dict()


@router.get("/{note_id}", response_model=dict)
async def get_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single note by ID (includes full content)"""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.owner_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return note.to_dict()


@router.put("/{note_id}", response_model=dict)
async def update_note(
    note_id: int,
    data: NoteUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing note"""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.owner_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Update fields only if provided
    update_data = data.model_dump(exclude_unset=True)
    
    if "folder_id" in update_data and update_data["folder_id"] == 0:
        update_data["folder_id"] = None
    elif "folder_id" in update_data and update_data["folder_id"]:
        # Validate folder belongs to user
        folder_result = await db.execute(
            select(Folder).where(
                Folder.id == update_data["folder_id"], 
                Folder.owner_id == current_user.id
            )
        )
        if not folder_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
    
    # Update tags separately
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            tag_result = await db.execute(
                select(Tag).where(Tag.id.in_(tag_ids), Tag.owner_id == current_user.id)
            )
            tags = tag_result.scalars().all()
            note.tags = tags
    
    # Apply remaining updates
    for field, value in update_data.items():
        setattr(note, field, value)
    
    await db.commit()
    await db.refresh(note)
    
    return note.to_dict()


@router.delete("/{note_id}", status_code=status.HTTP_200_OK)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a note permanently"""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.owner_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    await db.delete(note)
    await db.commit()
    
    return {"message": "Note deleted"}
