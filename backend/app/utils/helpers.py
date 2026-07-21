"""Utility helper functions for common operations.

Provides:
- Checksum generation for file integrity
- Filename sanitization for security
- DateTime formatting and parsing
- Dynamic filter query building
- Sorting/ordering application
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, unquote

from sqlalchemy import ColumnElement, asc, desc, select
from sqlalchemy.orm import DeclarativeBase


def generate_checksum(file_path: str | Path, algorithm: str = "sha256") -> str:
    """Generate checksum for file integrity verification.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm ("md5", "sha1", "sha256", "sha512")
        
    Returns:
        Hex digest of file hash
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If algorithm not supported
    """
    supported = {"md5", "sha1", "sha256", "sha512"}
    if algorithm not in supported:
        raise ValueError(f"Algorithm must be one of {supported}")
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hash_obj = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """Sanitize filename for safe storage and display.
    
    Removes/replaces unsafe characters, limits length.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length (default 255)
        
    Returns:
        Sanitized filename
    """
    # Remove leading/trailing whitespace
    filename = filename.strip()
    
    # Replace path separators with underscore
    filename = re.sub(r"[/\\]", "_", filename)
    
    # Remove control characters
    filename = "".join(c for c in filename if ord(c) >= 32 or c in "\t\n\r")
    
    # Replace sequences of unsafe characters with single underscore
    filename = re.sub(r"[<>:\"|?*\x00-\x1f]+", "_", filename)
    
    # Truncate if needed
    if len(filename) > max_length:
        # Preserve extension
        name, ext = Path(filename).stem, Path(filename).suffix
        available = max_length - len(ext)
        filename = name[:available] + ext
    
    # Ensure not empty
    if not filename or filename == ".":
        filename = "unnamed_file"
    
    return filename


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string.
    
    Args:
        dt: DateTime object
        format_str: Python datetime format string
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse string to datetime object.
    
    Args:
        date_str: DateTime string
        format_str: Python datetime format string
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If string doesn't match format
    """
    return datetime.strptime(date_str, format_str)


def build_filter_query(
    model: type[DeclarativeBase],
    filters: Dict[str, Any],
) -> Tuple[List[ColumnElement[bool]], Dict[str, Any]]:
    """Build SQLAlchemy WHERE conditions from filter dict.
    
    Args:
        model: SQLAlchemy ORM model class
        filters: Dict of field:value pairs for filtering
                 Values can be simple scalars or comparison dicts:
                 {"field": value} -> field = value
                 {"field": {"gte": 10}} -> field >= 10
                 {"field": {"like": "%text%"}} -> field LIKE '%text%'
                 
    Returns:
        Tuple of (where_conditions_list, normalized_filters_dict)
    """
    where_conditions = []
    normalized = {}
    
    for field_name, value in filters.items():
        # Check if field exists on model
        if not hasattr(model, field_name):
            continue
        
        column = getattr(model, field_name)
        normalized[field_name] = value
        
        if isinstance(value, dict):
            # Handle comparison operators
            for op, op_value in value.items():
                if op == "eq":
                    where_conditions.append(column == op_value)
                elif op == "ne":
                    where_conditions.append(column != op_value)
                elif op == "gt":
                    where_conditions.append(column > op_value)
                elif op == "gte":
                    where_conditions.append(column >= op_value)
                elif op == "lt":
                    where_conditions.append(column < op_value)
                elif op == "lte":
                    where_conditions.append(column <= op_value)
                elif op == "like":
                    where_conditions.append(column.like(op_value))
                elif op == "in":
                    where_conditions.append(column.in_(op_value))
        else:
            # Simple equality
            where_conditions.append(column == value)
    
    return where_conditions, normalized


def apply_sorting(
    query: select,
    model: type[DeclarativeBase],
    sort_by: Optional[str] = None,
    order: str = "asc",
) -> select:
    """Apply sorting/ordering to SQLAlchemy select query.
    
    Args:
        query: SQLAlchemy select() query
        model: ORM model class
        sort_by: Field name to sort by
        order: "asc" or "desc"
        
    Returns:
        Query with ORDER BY applied
    """
    if not sort_by or not hasattr(model, sort_by):
        return query
    
    column = getattr(model, sort_by)
    
    if order.lower() == "desc":
        return query.order_by(desc(column))
    else:
        return query.order_by(asc(column))


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to append if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    available = max_length - len(suffix)
    if available < 0:
        return text[:max_length]
    
    return text[:available] + suffix


def build_url_slug(text: str, max_length: int = 50) -> str:
    """Build URL-safe slug from text.
    
    Args:
        text: Text to convert to slug
        max_length: Maximum slug length
        
    Returns:
        URL-safe slug (lowercase, no spaces/special chars)
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces with hyphens
    slug = re.sub(r"\s+", "-", slug)
    
    # Remove non-alphanumeric except hyphens
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    
    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    
    # Truncate
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    
    return slug or "untitled"
