"""Export utilities for CSV and Excel file generation.

Provides:
- CSV writer with proper encoding and escaping
- Excel writer using openpyxl
- Data formatting for export
- Stream writing for large datasets
"""

import csv
from datetime import datetime
from io import StringIO, BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class CSVExporter:
    """CSV file exporter with consistent formatting."""
    
    def __init__(self, filename: str = "export", encoding: str = "utf-8-sig"):
        """Initialize CSV exporter.
        
        Args:
            filename: Output filename (without extension)
            encoding: File encoding (default utf-8-sig for Excel compatibility)
        """
        self.filename = filename
        self.encoding = encoding
        self.filepath = Path(f"{filename}.csv")
    
    def write_rows(
        self,
        data: List[Dict[str, Any]],
        fieldnames: Optional[List[str]] = None,
    ) -> Path:
        """Write list of dicts to CSV file.
        
        Args:
            data: List of dictionaries to write
            fieldnames: Column names (auto-detect if None)
            
        Returns:
            Path to generated CSV file
        """
        if not data:
            # Write empty file with headers
            if fieldnames:
                with open(self.filepath, "w", encoding=self.encoding, newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
            return self.filepath
        
        # Auto-detect fieldnames from first row
        if not fieldnames:
            fieldnames = list(data[0].keys())
        
        with open(self.filepath, "w", encoding=self.encoding, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return self.filepath
    
    def to_string(
        self,
        data: List[Dict[str, Any]],
        fieldnames: Optional[List[str]] = None,
    ) -> str:
        """Convert data to CSV string without writing file.
        
        Args:
            data: List of dictionaries
            fieldnames: Column names
            
        Returns:
            CSV content as string
        """
        if not data and not fieldnames:
            return ""
        
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        elif not fieldnames:
            fieldnames = []
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()


class ExcelExporter:
    """Excel file exporter using openpyxl."""
    
    def __init__(self, filename: str = "export"):
        """Initialize Excel exporter.
        
        Args:
            filename: Output filename (without extension)
            
        Raises:
            ImportError: If openpyxl not installed
        """
        if not OPENPYXL_AVAILABLE:
            raise ImportError("openpyxl required for Excel export. Install with: pip install openpyxl")
        
        self.filename = filename
        self.filepath = Path(f"{filename}.xlsx")
        self.workbook = Workbook()
        self.sheet = self.workbook.active
        self.sheet.title = "Data"
    
    def write_rows(
        self,
        data: List[Dict[str, Any]],
        fieldnames: Optional[List[str]] = None,
        header_style: bool = True,
    ) -> Path:
        """Write list of dicts to Excel file.
        
        Args:
            data: List of dictionaries
            fieldnames: Column names
            header_style: Apply formatting to header row
            
        Returns:
            Path to generated Excel file
        """
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        elif not fieldnames:
            fieldnames = []
        
        # Write headers
        for col_idx, fieldname in enumerate(fieldnames, start=1):
            cell = self.sheet.cell(row=1, column=col_idx, value=fieldname)
            if header_style:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Write data rows
        for row_idx, row_data in enumerate(data, start=2):
            for col_idx, fieldname in enumerate(fieldnames, start=1):
                value = row_data.get(fieldname)
                # Format datetime objects
                if isinstance(value, datetime):
                    value = value.isoformat()
                self.sheet.cell(row=row_idx, column=col_idx, value=value)
        
        # Auto-adjust column widths
        for col_idx, fieldname in enumerate(fieldnames, start=1):
            column_letter = self.sheet.cell(row=1, column=col_idx).column_letter
            # Calculate width based on header and sample data
            max_width = len(str(fieldname))
            for row in data[:10]:  # Check first 10 rows
                cell_value = row.get(fieldname)
                if cell_value:
                    max_width = max(max_width, len(str(cell_value)))
            self.sheet.column_dimensions[column_letter].width = min(max_width + 2, 50)
        
        self.workbook.save(self.filepath)
        return self.filepath
    
    def to_bytes(
        self,
        data: List[Dict[str, Any]],
        fieldnames: Optional[List[str]] = None,
        header_style: bool = True,
    ) -> bytes:
        """Convert data to Excel bytes without writing file.
        
        Args:
            data: List of dictionaries
            fieldnames: Column names
            header_style: Apply formatting to header row
            
        Returns:
            Excel file content as bytes
        """
        # Create temporary workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Data"
        
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        elif not fieldnames:
            fieldnames = []
        
        # Write headers
        for col_idx, fieldname in enumerate(fieldnames, start=1):
            cell = ws.cell(row=1, column=col_idx, value=fieldname)
            if header_style:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        
        # Write data
        for row_idx, row_data in enumerate(data, start=2):
            for col_idx, fieldname in enumerate(fieldnames, start=1):
                value = row_data.get(fieldname)
                if isinstance(value, datetime):
                    value = value.isoformat()
                ws.cell(row=row_idx, column=col_idx, value=value)
        
        # Get bytes
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()


def export_to_csv(
    data: List[Dict[str, Any]],
    filename: str = "export",
    fieldnames: Optional[List[str]] = None,
) -> Path:
    """Convenience function to export data to CSV.
    
    Args:
        data: List of dictionaries
        filename: Output filename (without extension)
        fieldnames: Column names
        
    Returns:
        Path to generated file
    """
    exporter = CSVExporter(filename)
    return exporter.write_rows(data, fieldnames)


def export_to_excel(
    data: List[Dict[str, Any]],
    filename: str = "export",
    fieldnames: Optional[List[str]] = None,
) -> Path:
    """Convenience function to export data to Excel.
    
    Args:
        data: List of dictionaries
        filename: Output filename (without extension)
        fieldnames: Column names
        
    Returns:
        Path to generated file
        
    Raises:
        ImportError: If openpyxl not installed
    """
    exporter = ExcelExporter(filename)
    return exporter.write_rows(data, fieldnames)
