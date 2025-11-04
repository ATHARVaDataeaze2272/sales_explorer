"""
Excel generation for company targeting data.
Single sheet format with auto-adjusted columns - NO summary sheets.

Requires: pandas, openpyxl
pip install pandas openpyxl
"""

import pandas as pd
from typing import Dict, List, Optional, Union, Any
import tempfile


def flatten_company_data(data: List[Dict]) -> List[Dict]:
    """
    Dynamically flatten company data - handles any fields present in the JSON.
    
    Handles both simple fields (strings) and list fields (like Target_Job_Titles).
    
    Args:
        data: List of company dictionaries
    
    Returns:
        List of flattened dictionaries suitable for DataFrame
    """
    if not data:
        return []
    
    flattened = []
    
    for company in data:
        flattened_row = {}
        
        # Process each field in the company dict
        for key, value in company.items():
            if isinstance(value, list):
                # Join list items with " | " separator
                flattened_row[key] = " | ".join(map(str, value)) if value else ""
            elif isinstance(value, dict):
                # If nested dict, convert to string representation
                flattened_row[key] = str(value)
            elif value is None:
                flattened_row[key] = ""
            else:
                # Simple field - string, number, etc.
                flattened_row[key] = str(value)
        
        flattened.append(flattened_row)
    
    return flattened


def get_field_display_order(df_columns: List[str]) -> List[str]:
    """
    Define preferred column order for better readability.
    Columns not in this list will appear at the end.
    
    Args:
        df_columns: Actual columns in the DataFrame
    
    Returns:
        Ordered list of columns
    """
    # Preferred order (fields that commonly appear first)
    preferred_order = [
        "Company_Name",
        "Country",
        "Key_Interests",
        "Target_Job_Titles",
        "Business_Areas",
        "Company_Main_Activities",
        "Companies_To_Exclude",
        "Excluded_Countries",
        "source_file",  # Added to show which PDF the data came from
    ]
    
    # Start with preferred columns that exist in the data
    ordered = [col for col in preferred_order if col in df_columns]
    
    # Add remaining columns that weren't in preferred order
    remaining = [col for col in df_columns if col not in ordered]
    
    return ordered + remaining


def auto_adjust_column_widths(worksheet, df: pd.DataFrame, max_width: int = 60):
    """
    Auto-adjust column widths based on content.
    
    Args:
        worksheet: openpyxl worksheet object
        df: DataFrame with the data
        max_width: Maximum column width
    """
    for idx, column in enumerate(worksheet.columns):
        max_length = 0
        column_letter = None
        
        try:
            column_letter = column[0].column_letter
        except Exception:
            continue
        
        # Check header length
        col_name = df.columns[idx] if idx < len(df.columns) else ""
        max_length = len(str(col_name))
        
        # Check cell content lengths
        for cell in column:
            try:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            except Exception:
                pass
        
        # Set width with padding and max limit
        adjusted_width = min(max_length + 3, max_width)
        worksheet.column_dimensions[column_letter].width = adjusted_width


def generate_excel_report(
    data: Union[List[Dict], Dict],
    filename: str = "company_report.xlsx"
) -> Optional[str]:
    """
    Simple Excel generator - single sheet with company data only.
    NO summary sheets, NO multiple tabs, just clean data.
    
    Args:
        data: Either a list of company dicts OR {"Target_Companies": [...]}
        filename: Base filename (for reference, actual file will be temp)
    
    Returns:
        Path to temporary Excel file (caller must handle cleanup)
    """
    # Support both formats
    companies = data.get("Target_Companies") if isinstance(data, dict) and "Target_Companies" in data else data
    
    if not companies:
        print("⚠️  No data to export to Excel")
        return None
    
    # Flatten the data dynamically
    flattened_data = flatten_company_data(companies)
    if not flattened_data:
        print("⚠️  No flattened data to export")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(flattened_data)
    
    # Reorder columns for better readability
    ordered_columns = get_field_display_order(df.columns.tolist())
    df = df[ordered_columns]
    
    # Create temporary file
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    tmp_name = tmp.name
    tmp.close()
    
    # Write to Excel - SINGLE SHEET ONLY
    try:
        with pd.ExcelWriter(tmp_name, engine="openpyxl") as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name="Companies", index=False)
            worksheet = writer.sheets["Companies"]
            auto_adjust_column_widths(worksheet, df)
        
        # Print success info
        print(f"✅ Excel generated: {tmp_name}")
        print(f"📊 Total rows: {len(flattened_data)}")
        print(f"🏢 Companies: {len(companies)}")
        print(f"📋 Fields: {len(ordered_columns)}")
        
        return tmp_name
        
    except Exception as e:
        print(f"❌ Failed to generate Excel: {e}")
        return None


# Remove the generate_excel_by_company function entirely
# We only need the simple single-sheet format