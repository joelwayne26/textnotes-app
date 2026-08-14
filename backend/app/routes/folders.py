"""
Folders CRUD Routes - FastAPI Implementation
Organize notes into hierarchical folder structure
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.extensions import get_db
from app.models import Folder
from app.routes.auth import get_current_user, User

router = APIRouter()


# Pydantic Schemas
class FolderCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    parent_id: Optional[int] = None


class FolderUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    parent_id: Optional[int] = None


@router.get("", response_model=List[dict])
async def list_folders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all top-level folders for current user.
    
    Returns folders with nested children (if any).
    """
    result = await db.execute(
        select(Folder)
        .where(Folder.owner_id == current_user.id, Folder.parent_id.is_(None))
        .order_by(Folder.name)
    )
    folders = result.scalars().all()
    
    return [folder.to_dict(include_children=True) for folder in folders]


@router.post("", response_model=dict, status_code=201)
async def create_folder(
    data: FolderCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new folder"""
    # Validate parent folder if provided
    if data.parent_id:
        result = await db.execute(
            select(Folder).where(
                Folder.id == data.parent_id, 
                Folder.owner_id == current_user.id
            )
        )
        parent = result.scalar_one_or_none()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent folder not found"
            )
    
    # Create folder
    folder = Folder(
        name=data.name,
        parent_id=data.parent_id,
        owner_id=current_user.id,
    )
    
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    
    return folder.to_dict()


@router.put("/{folder_id}", response_model=dict)
async def update_folder(
    folder_id: int,
    data: FolderUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing folder's name or parent"""
    result = await db.execute(
        select(Folder).where(Folder.id == folder_id, Folder.owner_id == current_user.id)
    )
    folder = result.scalar_one_or_none()
    
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    # Update name if provided
    if data.name is not None:
        folder.name = data.name
    
    # Update parent if provided
    if data.parent_id is not None:
        if data.parent_id == 0:
            folder.parent_id = None
        else:
            # Validate new parent exists and isn't self or descendant
            if data.parent_id == folder_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot set folder as its own parent"
                )
            
            parent_result = await db.execute(
                select(Folder).where(
                    Folder.id == data.parent_id, 
                    Folder.owner_id == current_user.id
                )
            )
            parent = parent_result.scalar_one_or_none()
            
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid parent folder"
                )
            
            folder.parent_id = data.parent_id
    
    await db.commit()
    await db.refresh(folder)
    
    return folder.to_dict()


@router.delete("/{folder_id}", status_code=status.HTTP_200_OK)
async def delete_folder(
    folder_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a folder and all its contents.
    
    WARNING: This will also delete all notes within this folder!
    """
    result = await db.execute(
        select(Folder).where(Folder.id == folder_id, Folder.owner_id == current_user.id)
    )
    folder = result.scalar_one_or_none()
    
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    await db.delete(folder)
    await db.commit()
    
    return {"message": "Folder deleted"}
