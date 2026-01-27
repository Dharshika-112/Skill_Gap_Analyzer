"""
Utility functions for the Skill Gap Analyzer application.
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

from .config import settings


def ensure_upload_directory():
    """Ensure upload directory exists."""
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving the extension."""
    file_extension = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{file_extension}"


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path)


def is_allowed_file_type(filename: str) -> bool:
    """Check if file type is allowed."""
    file_extension = Path(filename).suffix.lower().lstrip('.')
    return file_extension in settings.allowed_file_types


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing potentially dangerous characters."""
    # Remove path separators and other dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    sanitized = filename
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Limit filename length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_object_id(object_id: str) -> bool:
    """Validate if string is a valid MongoDB ObjectId."""
    from bson import ObjectId
    try:
        ObjectId(object_id)
        return True
    except Exception:
        return False