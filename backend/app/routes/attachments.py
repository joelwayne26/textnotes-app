"""
Attachments Routes - FastAPI Implementation
File upload/download for notes
"""

import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.extensions import get_db
from app.models import Note, Attachment
from app.routes.auth import get_current_user, User

router = APIRouter()

# Configuration (in production, use settings)
UPLOAD_FOLDER = "/app/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "md", "txt"}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return (
        "." in filename 
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_unique_filename(original_filename: str) -> str:
    """Generate unique filename to prevent collisions"""
    ext = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else ""
    return f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex


@router.post("/notes/{note_id}", response_model=dict, status_code=201)
async def upload_attachment(
    note_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a file attachment to a note.
    
    Supported formats: png, jpg, jpeg, gif, webp, pdf, md, txt
    Max size: 16MB
    """
    # Validate note exists and belongs to user
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.owner_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No selected file"
        )
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    unique_name = get_unique_filename(file.filename)
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    content = await file.read()
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Create attachment record
    attachment = Attachment(
        filename=unique_name,
        original_filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        note_id=note.id,
    )
    
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    
    return attachment.to_dict()


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download an attachment by ID.
    
    Returns the file with proper Content-Disposition header.
    """
    from sqlalchemy import join
    
    result = await db.execute(
        select(Attachment)
        .join(Note)
        .where(Attachment.id == attachment_id, Note.owner_id == current_user.id)
    )
    attachment = result.scalar_one_or_none()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    filepath = os.path.join(UPLOAD_FOLDER, attachment.filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    return FileResponse(
        path=filepath,
        filename=attachment.original_filename,
        media_type=attachment.content_type,
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_200_OK)
async def delete_attachment(
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an attachment and its associated file.
    """
    from sqlalchemy import join
    
    result = await db.execute(
        select(Attachment)
        .join(Note)
        .where(Attachment.id == attachment_id, Note.owner_id == current_user.id)
    )
    attachment = result.scalar_one_or_none()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Delete physical file
    filepath = os.path.join(UPLOAD_FOLDER, attachment.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Delete database record
    await db.delete(attachment)
    await db.commit()
    
    return {"message": "Attachment deleted"}
