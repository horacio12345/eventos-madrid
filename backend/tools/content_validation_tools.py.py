# backend/tools/content_validation_tools.py

"""
Analysis tools for content validation and filtering
"""
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List

from langchain_core.tools import tool

from .base_tool import BaseTool


@tool
async def validate_event_relevance(
    events: List[Dict], validation_criteria: Dict
) -> Dict[str, Any]:
    """
    Validate events for relevance to seniors in Madrid.

    Args:
        events: List of event dictionaries
        validation_criteria: Dict with validation rules

    Returns:
        Dict with validated events and rejection details
    """
    tool_instance = BaseTool(
        "validate_event_relevance", "Validate event relevance for seniors"
    )

    try:
        tool_instance._log_execution(
            "Starting relevance validation", f"Events: {len(events)}"
        )

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
            text_content = (
                f"{event.get('titulo', '')} {event.get('descripcion', '')}".lower()
            )
            for keyword in excluded_keywords:
                if keyword.lower() in text_content:
                    is_valid = False
                    rejection_reasons.append(f"Contains excluded keyword: {keyword}")

            # Check location relevance
            location_text = event.get("ubicacion", "").lower()
            if location_text and not any(
                loc.lower() in location_text for loc in location_keywords
            ):
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

        tool_instance._log_execution(
            "Relevance validation completed",
            f"Valid: {len(valid_events)}, Invalid: {len(invalid_events)}",
        )

        return tool_instance._create_success_response(
            valid_events,
            {
                "validation_type": "relevance_seniors",
                "events_valid": len(valid_events),
                "events_invalid": len(invalid_events),
                "validation_criteria": validation_criteria,
                "invalid_events": invalid_events,
            },
        )

    except Exception as e:
        return tool_instance._create_error_response(
            f"Relevance validation failed: {str(e)}", events
        )


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
    numbers = re.findall(r"\d+(?:[,\.]\d{1,2})?", price_str)
    if numbers:
        try:
            price = float(numbers[0].replace(",", "."))
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
