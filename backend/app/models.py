from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
    Column,
    Integer,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


# Association table for Note <-> Tag (many-to-many)
note_tags = Table(
    "note_tags",
    db.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    notes: Mapped[List["Note"]] = relationship("Note", back_populates="owner", cascade="all, delete-orphan")
    folders: Mapped[List["Folder"]] = relationship(
        "Folder", back_populates="owner", cascade="all, delete-orphan"
    )
    tags: Mapped[List["Tag"]] = relationship("Tag", back_populates="owner", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Folder(db.Model):
    __tablename__ = "folders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("folders.id", ondelete="SET NULL"), nullable=True
    )
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="folders")
    parent: Mapped[Optional["Folder"]] = relationship(
        "Folder", remote_side=[id], back_populates="children"
    )
    children: Mapped[List["Folder"]] = relationship("Folder", back_populates="parent")
    notes: Mapped[List["Note"]] = relationship("Note", back_populates="folder")

    def to_dict(self, include_children: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_children:
            data["children"] = [c.to_dict() for c in self.children]
        return data


class Tag(db.Model):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name", "owner_id", name="uq_tag_name_owner"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), default="#6366f1")  # hex
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    owner: Mapped["User"] = relationship("User", back_populates="tags")
    notes: Mapped[List["Note"]] = relationship(
        "Note", secondary=note_tags, back_populates="tags"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "owner_id": self.owner_id,
        }


class Note(db.Model):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, default="")  # Markdown
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    folder_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("folders.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="notes")
    folder: Mapped[Optional["Folder"]] = relationship("Folder", back_populates="notes")
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=note_tags, back_populates="notes"
    )
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", back_populates="note", cascade="all, delete-orphan"
    )

    def to_dict(self, include_content: bool = True) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "is_pinned": self.is_pinned,
            "is_archived": self.is_archived,
            "owner_id": self.owner_id,
            "folder_id": self.folder_id,
            "tags": [t.to_dict() for t in self.tags],
            "attachments": [a.to_dict() for a in self.attachments],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_content:
            data["content"] = self.content
        return data


class Attachment(db.Model):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    note: Mapped["Note"] = relationship("Note", back_populates="attachments")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "content_type": self.content_type,
            "size": self.size,
            "url": f"/api/attachments/{self.id}/download",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
