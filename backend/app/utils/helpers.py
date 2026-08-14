"""
Utility functions for the Notes API
"""

import re
import uuid
from datetime import datetime
from typing import Optional
from werkzeug.utils import secure_filename
import os


def generate_slug(text: str) -> str:
    """Generate URL-safe slug from text."""
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename to prevent collisions."""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return secure_filename(unique_name)


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime for JSON response."""
    if dt is None:
        return None
    return dt.isoformat()


def get_file_size_display(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def sanitize_markdown(content: str) -> str:
    """
    Basic markdown sanitization.
    For production, use a proper library like bleach or DOMPurify.
    """
    # Remove potentially dangerous HTML tags
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form']
    for tag in dangerous_tags:
        content = re.sub(
            rf'<{tag}[^>]*>.*?</{tag}>',
            '',
            content,
            flags=re.IGNORECASE | re.DOTALL
        )
    
    # Remove javascript: URLs
    content = re.sub(
        r'javascript:',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    return content


def paginate_query(query, page: int = 1, per_page: int = 20):
    """Apply pagination to a SQLAlchemy query."""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }
