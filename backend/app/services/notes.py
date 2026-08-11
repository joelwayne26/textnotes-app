"""
Service layer for Notes business logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Note, Tag, Folder, User, note_tags


class NoteService:
    """Service class for Note operations"""
    
    @staticmethod
    def get_user_notes(
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        folder_id: Optional[int] = None,
        tag_id: Optional[int] = None,
        is_archived: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Get paginated notes for a user with optional filters.
        
        Args:
            user_id: The owner's ID
            page: Page number (1-based)
            per_page: Items per page
            search: Search query string
            folder_id: Filter by folder
            tag_id: Filter by tag
            is_archived: Filter archived status
            is_pinned: Filter pinned status
            
        Returns:
            Paginated result dict with items, total, pages, etc.
        """
        query = Note.query.options(
            joinedload(Note.tags),
            joinedload(Note.attachments),
            joinedload(Note.folder)
        ).filter(Note.owner_id == user_id)
        
        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Note.title.ilike(search_filter),
                    Note.content.ilike(search_filter)
                )
            )
        
        if folder_id is not None:
            query = query.filter(Note.folder_id == folder_id)
            
        if tag_id is not None:
            query = query.join(note_tags).filter(note_tags.c.tag_id == tag_id)
            
        if is_archived is not None:
            query = query.filter(Note.is_archived == is_archived)
            
        if is_pinned is not None:
            query = query.filter(Note.is_pinned == is_pinned)
        
        # Order: pinned first, then by updated_at desc
        query = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            "items": [note.to_dict() for note in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "per_page": per_page,
        }
    
    @staticmethod
    def get_note_by_id(note_id: int, user_id: int) -> Optional[Note]:
        """Get a single note by ID, ensuring ownership."""
        return Note.query.options(
            joinedload(Note.tags),
            joinedload(Note.attachments),
            joinedload(Note.folder)
        ).filter(
            Note.id == note_id,
            Note.owner_id == user_id
        ).first()
    
    @staticmethod
    def create_note(user_id: int, data: Dict[str, Any]) -> Note:
        """Create a new note."""
        note = Note(
            title=data.get("title", "Untitled Note"),
            content=data.get("content", ""),
            is_pinned=data.get("is_pinned", False),
            is_archived=data.get("is_archived", False),
            owner_id=user_id,
            folder_id=data.get("folder_id"),
        )
        
        # Handle tags if provided
        if "tag_ids" in data:
            tags = Tag.query.filter(Tag.id.in_(data["tag_ids"])).all()
            note.tags.extend(tags)
        
        db.session.add(note)
        db.session.commit()
        
        return note
    
    @staticmethod
    def update_note(note: Note, data: Dict[str, Any]) -> Note:
        """Update an existing note."""
        updatable_fields = ["title", "content", "is_pinned", "is_archived", "folder_id"]
        
        for field in updatable_fields:
            if field in data:
                setattr(note, field, data[field])
        
        # Handle tags update
        if "tag_ids" in data:
            tags = Tag.query.filter(Tag.id.in_(data["tag_ids"])).all()
            note.tags = tags
        
        db.session.commit()
        
        return note
    
    @staticmethod
    def delete_note(note: Note) -> bool:
        """Delete a note. Returns True on success."""
        try:
            db.session.delete(note)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def toggle_pin(note: Note) -> Note:
        """Toggle pin status of a note."""
        note.is_pinned = not note.is_pinned
        db.session.commit()
        return note
    
    @staticmethod
    def toggle_archive(note: Note) -> Note:
        """Toggle archive status of a note."""
        note.is_archived = not note.is_archived
        db.session.commit()
        return note


class FolderService:
    """Service class for Folder operations"""
    
    @staticmethod
    def get_user_folders(user_id: int, include_nested: bool = True) -> List[Folder]:
        """Get all folders for a user."""
        query = Folder.query.filter(Folder.owner_id == user_id)
        
        folders = query.all()
        
        if include_nested:
            return [f.to_dict(include_children=True) for f in folders]
        return [f.to_dict() for f in folders]
    
    @staticmethod
    def create_folder(user_id: int, name: str, parent_id: Optional[int] = None) -> Folder:
        """Create a new folder."""
        folder = Folder(
            name=name,
            owner_id=user_id,
            parent_id=parent_id,
        )
        db.session.add(folder)
        db.session.commit()
        return folder


class TagService:
    """Service class for Tag operations"""
    
    @staticmethod
    def get_user_tags(user_id: int) -> List[Tag]:
        """Get all tags for a user."""
        return Tag.query.filter(Tag.owner_id == user_id).all()
    
    @staticmethod
    def create_tag(user_id: int, name: str, color: str = "#6366f1") -> Tag:
        """Create a new tag (or return existing if same name exists)."""
        existing = Tag.query.filter(
            Tag.name == name.lower(),
            Tag.owner_id == user_id
        ).first()
        
        if existing:
            return existing
        
        tag = Tag(
            name=name.lower(),
            color=color,
            owner_id=user_id,
        )
        db.session.add(tag)
        db.session.commit()
        return tag
