# backend/tools/date_tools.py

"""
Date processing tools for temporal filtering
"""
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from langchain_core.tools import tool

from .base_tool import BaseTool


@tool
async def extract_month_from_text(text: str, language: str = "es") -> Dict[str, Any]:
    """
    Extract month and year information from text (PDF names, content).
    
    Args:
        text: Text content to analyze
        language: Language for month names (es/en)
    
    Returns:
        Dict with extracted date information
    """
    tool_instance = BaseTool("extract_month_from_text", "Extract month/year from text")
    
    try:
        tool_instance._log_execution("Starting month extraction", f"Text length: {len(text)}")
        
        # Month mappings
        if language == "es":
            months_map = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
        else:
            months_map = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
        
        extracted_dates = []
        
        # Pattern for "month YYYY" format
        if language == "es":
            pattern = r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(\d{4})'
        else:
            pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})'
        
        matches = re.finditer(pattern, text.lower())
        
        for match in matches:
            month_name = match.group(1)
            year = int(match.group(2))
            month_num = months_map.get(month_name)
            
            if month_num:
                extracted_dates.append({
                    "month": month_num,
                    "year": year,
                    "month_name": month_name,
                    "text_position": match.span(),
                    "matched_text": match.group(0)
                })
        
        # Pattern for "MM/YYYY" or "MM-YYYY" format
        numeric_pattern = r'(\d{1,2})[\/\-](\d{4})'
        numeric_matches = re.finditer(numeric_pattern, text)
        
        for match in numeric_matches:
            month_num = int(match.group(1))
            year = int(match.group(2))
            
            if 1 <= month_num <= 12:
                extracted_dates.append({
                    "month": month_num,
                    "year": year,
                    "month_name": None,
                    "text_position": match.span(),
                    "matched_text": match.group(0)
                })
        
        tool_instance._log_execution("Month extraction completed", f"Found {len(extracted_dates)} dates")
        
        return tool_instance._create_success_response(
            extracted_dates,
            {
                "extraction_method": "regex_month_year",
                "language": language,
                "dates_found": len(extracted_dates)
            }
        )
        
    except Exception as e:
        return tool_instance._create_error_response(f"Month extraction failed: {str(e)}")


@tool
async def get_relevant_date_range(base_date: str = None) -> Dict[str, Any]:
    """
    Get relevant date range for current and next month filtering.
    
    Args:
        base_date: Base date in YYYY-MM-DD format (optional, uses current date)
    
    Returns:
        Dict with date range information
    """
    tool_instance = BaseTool("get_relevant_date_range", "Calculate relevant date range for filtering")
    
    try:
        if base_date:
            current_date = datetime.strptime(base_date, "%Y-%m-%d")
        else:
            current_date = datetime.now()
        
        tool_instance._log_execution("Calculating date range", f"Base date: {current_date.strftime('%Y-%m-%d')}")
        
        # Current month
        current_month_start = current_date.replace(day=1)
        
        # Next month
        if current_date.month == 12:
            next_month_start = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            next_month_start = current_date.replace(month=current_date.month + 1, day=1)
        
        # Month after next (for end range)
        if next_month_start.month == 12:
            month_after_next = next_month_start.replace(year=next_month_start.year + 1, month=1, day=1)
        else:
            month_after_next = next_month_start.replace(month=next_month_start.month + 1, day=1)
        
        # End of next month
        next_month_end = month_after_next - timedelta(days=1)
        
        date_range = {
            "base_date": current_date.strftime("%Y-%m-%d"),
            "current_month": {
                "start": current_month_start.strftime("%Y-%m-%d"),
                "end": (next_month_start - timedelta(days=1)).strftime("%Y-%m-%d"),
                "month_num": current_date.month,
                "year": current_date.year
            },
            "next_month": {
                "start": next_month_start.strftime("%Y-%m-%d"),
                "end": next_month_end.strftime("%Y-%m-%d"),
                "month_num": next_month_start.month,
                "year": next_month_start.year
            },
            "overall_range": {
                "start": current_month_start.strftime("%Y-%m-%d"),
                "end": next_month_end.strftime("%Y-%m-%d")
            }
        }
        
        tool_instance._log_execution("Date range calculated", f"Range: {date_range['overall_range']['start']} to {date_range['overall_range']['end']}")
        
        return tool_instance._create_success_response(
            date_range,
            {"calculation_method": "current_next_month"}
        )
        
    except Exception as e:
        return tool_instance._create_error_response(f"Date range calculation failed: {str(e)}")