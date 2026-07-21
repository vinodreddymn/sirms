"""Data validation utilities for common operations.

Provides:
- Email validation
- Phone number validation
- URL validation
- Custom type validators
- Range validators
"""

import re
from typing import Any, Callable, List, Optional, Pattern, Tuple


EMAIL_PATTERN: Pattern = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

PHONE_PATTERN: Pattern = re.compile(
    r"^(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$"
)

URL_PATTERN: Pattern = re.compile(
    r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE
)

SLUG_PATTERN: Pattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email cannot be empty"
    
    email = email.strip()
    
    if len(email) > 254:
        return False, "Email is too long (max 254 characters)"
    
    if not EMAIL_PATTERN.match(email):
        return False, "Email format is invalid"
    
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """Validate phone number format (US format assumed).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone cannot be empty"
    
    phone = phone.strip()
    
    if not PHONE_PATTERN.match(phone):
        return False, "Phone format is invalid"
    
    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"
    
    url = url.strip()
    
    if not URL_PATTERN.match(url):
        return False, "URL format is invalid"
    
    return True, None


def validate_slug(slug: str) -> Tuple[bool, Optional[str]]:
    """Validate URL-safe slug format.
    
    Args:
        slug: Slug to validate (lowercase alphanumeric and hyphens)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not slug:
        return False, "Slug cannot be empty"
    
    slug = slug.strip()
    
    if not SLUG_PATTERN.match(slug):
        return False, "Slug must contain only lowercase letters, numbers, and hyphens"
    
    return True, None


def validate_length(
    value: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    """Validate string length.
    
    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, "Value cannot be None"
    
    value_len = len(str(value))
    
    if min_length is not None and value_len < min_length:
        return False, f"Must be at least {min_length} characters"
    
    if max_length is not None and value_len > max_length:
        return False, f"Must be at most {max_length} characters"
    
    return True, None


def validate_range(
    value: float | int,
    min_value: Optional[float | int] = None,
    max_value: Optional[float | int] = None,
) -> Tuple[bool, Optional[str]]:
    """Validate numeric value range.
    
    Args:
        value: Number to validate
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, "Value cannot be None"
    
    if min_value is not None and value < min_value:
        return False, f"Must be at least {min_value}"
    
    if max_value is not None and value > max_value:
        return False, f"Must be at most {max_value}"
    
    return True, None


def validate_choice(
    value: Any,
    choices: List[Any],
) -> Tuple[bool, Optional[str]]:
    """Validate value is one of allowed choices.
    
    Args:
        value: Value to validate
        choices: List of allowed values
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, "Value cannot be None"
    
    if value not in choices:
        choices_str = ", ".join(str(c) for c in choices)
        return False, f"Must be one of: {choices_str}"
    
    return True, None


def validate_with_function(
    value: Any,
    validator: Callable[[Any], bool],
    error_message: str = "Validation failed",
) -> Tuple[bool, Optional[str]]:
    """Validate value using custom validator function.
    
    Args:
        value: Value to validate
        validator: Function that returns bool
        error_message: Error message if validation fails
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if validator(value):
            return True, None
        else:
            return False, error_message
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_all(
    data: dict[str, Any],
    rules: dict[str, List[Tuple[Callable, str]]],
) -> Tuple[bool, dict[str, List[str]]]:
    """Validate multiple fields with multiple rules.
    
    Args:
        data: Dict of field:value pairs
        rules: Dict of field: [(validator_func, error_msg), ...]
        
    Returns:
        Tuple of (is_valid, dict of field:errors_list)
    """
    errors = {}
    
    for field, field_rules in rules.items():
        field_errors = []
        value = data.get(field)
        
        for validator_func, error_msg in field_rules:
            is_valid, msg = validator_func(value)
            if not is_valid:
                field_errors.append(msg or error_msg)
        
        if field_errors:
            errors[field] = field_errors
    
    return len(errors) == 0, errors
