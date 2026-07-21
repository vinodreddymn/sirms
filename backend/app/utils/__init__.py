"""Utility functions and helpers for the application.

Provides:
- File operations (checksums, sanitization)
- DateTime formatting and parsing
- Dynamic query building (filters, sorting)
- Export utilities (CSV, Excel)
- Data validation (email, phone, URL, custom validators)
"""

from app.utils.helpers import (
    generate_checksum,
    sanitize_filename,
    format_datetime,
    parse_datetime,
    build_filter_query,
    apply_sorting,
    truncate_string,
    build_url_slug,
)
from app.utils.export import (
    CSVExporter,
    ExcelExporter,
    export_to_csv,
    export_to_excel,
)
from app.utils.validation import (
    validate_email,
    validate_phone,
    validate_url,
    validate_slug,
    validate_length,
    validate_range,
    validate_choice,
    validate_with_function,
    validate_all,
)

__all__ = [
    # Helpers
    "generate_checksum",
    "sanitize_filename",
    "format_datetime",
    "parse_datetime",
    "build_filter_query",
    "apply_sorting",
    "truncate_string",
    "build_url_slug",
    # Export
    "CSVExporter",
    "ExcelExporter",
    "export_to_csv",
    "export_to_excel",
    # Validation
    "validate_email",
    "validate_phone",
    "validate_url",
    "validate_slug",
    "validate_length",
    "validate_range",
    "validate_choice",
    "validate_with_function",
    "validate_all",
]
