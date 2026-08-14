"""
Tags CRUD Routes - FastAPI Implementation
Categorize notes with color-coded tags
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.extensions import get_db
from app.models import Tag
from app.routes.auth import get_current_user, User

router = APIRouter()


# Pydantic Schemas
class TagCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TagUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


@router.get("", response_model=List[dict])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all tags for current user.
    
    Tags are returned with note counts for easy display.
    """
    result = await db.execute(
        select(Tag)
        .where(Tag.owner_id == current_user.id)
        .order_by(Tag.name)
    )
    tags = result.scalars().all()
    
    return [tag.to_dict() for tag in tags]


@router.post("", response_model=dict, status_code=201)
async def create_tag(
    data: TagCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tag (color is optional, defaults to indigo)"""
    
    # Check for duplicate tag name (case-insensitive)
    result = await db.execute(
        select(Tag).where(
            Tag.name.ilike(data.name), 
            Tag.owner_id == current_user.id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag already exists"
        )
    
    # Create tag with default color if not provided
    tag = Tag(
        name=data.name.lower(),
        color=data.color or "#6366f1",
        owner_id=current_user.id,
    )
    
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return tag.to_dict()


@router.put("/{tag_id}", response_model=dict)
async def update_tag(
    tag_id: int,
    data: TagUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing tag's name or color"""
    result = await db.execute(
        select(Tag).where(Tag.id == tag_id, Tag.owner_id == current_user.id)
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Update fields if provided
    if data.name is not None:
        # Check for duplicate name (excluding current tag)
        dup_result = await db.execute(
            select(Tag).where(
                Tag.name.ilike(data.name),
                Tag.owner_id == current_user.id,
                Tag.id != tag_id
            )
        )
        if dup_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tag already exists"
            )
        tag.name = data.name.lower()
    
    if data.color is not None:
        tag.color = data.color
    
    await db.commit()
    await db.refresh(tag)
    
    return tag.to_dict()


@router.delete("/{tag_id}", status_code=status.HTTP_200_OK)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a tag.
    
    Note: This removes the tag from all associated notes but does NOT delete the notes themselves.
    """
    result = await db.execute(
        select(Tag).where(Tag.id == tag_id, Tag.owner_id == current_user.id)
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    await db.delete(tag)
    await db.commit()
    
    return {"message": "Tag deleted"}
