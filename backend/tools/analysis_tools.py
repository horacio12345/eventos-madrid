# backend/tools/analysis_tools.py

"""
Analysis tools for content validation and filtering
"""
import re
from typing import Dict, List, Any
from datetime import datetime, timedelta
from langchain_core.tools import tool

from .base_tool import BaseTool


@tool
async def filter_by_current_month(events: List[Dict], current_date: str = None) -> Dict[str, Any]:
    """
    Filter events to include only current month and next month.
    
    Args:
        events: List of event dictionaries
        current_date: Current date in YYYY-MM-DD format (optional)
    
    Returns:
        Dict with filtered events and metadata
    """
    tool_instance = BaseTool("filter_by_current_month", "Filter events by current and next month")
    
    try:
        if current_date:
            base_date = datetime.strptime(current_date, "%Y-%m-%d")
        else:
            base_date = datetime.now()
        
        tool_instance._log_execution("Starting date filtering", f"Base date: {base_date.strftime('%Y-%m-%d')}")
        
        # Calculate current and next month
        current_month = base_date.month
        current_year = base_date.year
        
        next_month_date = base_date.replace(day=1) + timedelta(days=32)
        next_month = next_month_date.month
        next_year = next_month_date.year
        
        relevant_months = [
            (current_month, current_year),
            (next_month, next_year)
        ]
        
        filtered_events = []
        rejected_events = []
        
        for event in events:
            event_date = _extract_event_date(event)
            
            if event_date:
                event_month = event_date.month
                event_year = event_date.year
                
                if (event_month, event_year) in relevant_months:
                    event["date_filter_passed"] = True
                    filtered_events.append(event)
                else:
                    event["date_filter_passed"] = False
                    event["rejection_reason"] = f"Date {event_date.strftime('%Y-%m')} not in current/next month"
                    rejected_events.append(event)
            else:
                event["date_filter_passed"] = False
                event["rejection_reason"] = "Could not parse event date"
                rejected_events.append(event)
        
        tool_instance._log_execution("Date filtering completed", 
                                    f"Filtered: {len(filtered_events)}, Rejected: {len(rejected_events)}")
        
        return tool_instance._create_success_response(
            filtered_events,
            {
                "filter_type": "current_next_month",
                "base_date": base_date.strftime("%Y-%m-%d"),
                "relevant_months": [f"{year}-{month:02d}" for month, year in relevant_months],
                "events_passed": len(filtered_events),
                "events_rejected": len(rejected_events),
                "rejected_events": rejected_events
            }
        )
        
    except Exception as e:
        return tool_instance._create_error_response(f"Date filtering failed: {str(e)}", events)


@tool
async def validate_event_relevance(events: List[Dict], validation_criteria: Dict) -> Dict[str, Any]:
    """
    Validate events for relevance to seniors in Madrid.
    
    Args:
        events: List of event dictionaries
        validation_criteria: Dict with validation rules
    
    Returns:
        Dict with validated events and rejection details
    """
    tool_instance = BaseTool("validate_event_relevance", "Validate event relevance for seniors")
    
    try:
        tool_instance._log_execution("Starting relevance validation", f"Events: {len(events)}")
        
        valid_events = []
        invalid_events = []
        
        # Get criteria
        max_price = validation_criteria.get("max_price", 15)
        excluded_keywords = validation_criteria.get("excluded_keywords", [])
        preferred_keywords = validation_criteria.get("preferred_keywords", [])
        location_keywords = validation_criteria.get("location_keywords", ["madrid"])
        
        for event in events:
            is_valid = True
            rejection_reasons = []
            
            # Check price
            if not _is_price_acceptable(event.get("precio", ""), max_price):
                is_valid = False
                rejection_reasons.append(f"Price exceeds {max_price}€")
            
            # Check for excluded keywords
            text_content = f"{event.get('titulo', '')} {event.get('descripcion', '')}".lower()
            for keyword in excluded_keywords:
                if keyword.lower() in text_content:
                    is_valid = False
                    rejection_reasons.append(f"Contains excluded keyword: {keyword}")
            
            # Check location relevance
            location_text = event.get("ubicacion", "").lower()
            if location_text and not any(loc.lower() in location_text for loc in location_keywords):
                is_valid = False
                rejection_reasons.append("Location not in Madrid area")
            
            # Assign relevance score
            relevance_score = _calculate_relevance_score(event, preferred_keywords)
            event["relevance_score"] = relevance_score
            
            if is_valid:
                valid_events.append(event)
            else:
                event["rejection_reasons"] = rejection_reasons
                invalid_events.append(event)
        
        tool_instance._log_execution("Relevance validation completed", 
                                    f"Valid: {len(valid_events)}, Invalid: {len(invalid_events)}")
        
        return tool_instance._create_success_response(
            valid_events,
            {
                "validation_type": "relevance_seniors",
                "events_valid": len(valid_events),
                "events_invalid": len(invalid_events),
                "validation_criteria": validation_criteria,
                "invalid_events": invalid_events
            }
        )
        
    except Exception as e:
        return tool_instance._create_error_response(f"Relevance validation failed: {str(e)}", events)


def _extract_event_date(event: Dict) -> datetime:
    """Extract and parse date from event"""
    date_fields = ["fecha_inicio", "fecha", "date"]
    
    for field in date_fields:
        date_str = event.get(field)
        if date_str:
            return _parse_date_string(date_str)
    
    return None


def _parse_date_string(date_str: str) -> datetime:
    """Parse date string with multiple format support"""
    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y/%m/%d"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    # Try to extract date with regex
    date_match = re.search(r'(\d{1,2})[\.\/\-](\d{1,2})[\.\/\-](\d{4})', date_str)
    if date_match:
        day, month, year = map(int, date_match.groups())
        try:
            return datetime(year, month, day)
        except ValueError:
            pass
    
    return None


def _is_price_acceptable(price_str: str, max_price: float) -> bool:
    """Check if price is within acceptable range"""
    if not price_str:
        return True
    
    price_lower = price_str.lower()
    
    # Free events are always acceptable
    free_words = ["gratis", "gratuito", "libre", "sin coste", "free"]
    if any(word in price_lower for word in free_words):
        return True
    
    # Extract numeric price
    numbers = re.findall(r'\d+(?:[,\.]\d{1,2})?', price_str)
    if numbers:
        try:
            price = float(numbers[0].replace(',', '.'))
            return price <= max_price
        except ValueError:
            pass
    
    return True  # If can't parse, assume acceptable


def _calculate_relevance_score(event: Dict, preferred_keywords: List[str]) -> float:
    """Calculate relevance score for event"""
    score = 0.5  # Base score
    
    text_content = f"{event.get('titulo', '')} {event.get('descripcion', '')}".lower()
    
    # Boost score for preferred keywords
    for keyword in preferred_keywords:
        if keyword.lower() in text_content:
            score += 0.1
    
    # Boost for having complete information
    if event.get("ubicacion"):
        score += 0.1
    if event.get("descripcion"):
        score += 0.1
    if event.get("precio"):
        score += 0.05
    
    return min(score, 1.0)  # Cap at 1.0