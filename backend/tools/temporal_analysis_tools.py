# backend/tools/temporal_analysis_tools.py

"""
Temporal analysis tools for detecting time-based patterns and extracting dates
"""
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from .base_tool import BaseTool


@tool
async def detect_temporal_patterns(content_items: List[str]) -> Dict[str, Any]:
    """
    Detect temporal organization patterns in content.

    Args:
        content_items: List of content strings to analyze for temporal patterns

    Returns:
        Dict with detected patterns and dominant temporal organization
    """
    tool_instance = BaseTool(
        "detect_temporal_patterns", "Detect temporal organization patterns"
    )

    try:
        tool_instance._log_execution(
            "Starting temporal pattern detection", f"Items: {len(content_items)}"
        )

        if not content_items:
            return tool_instance._create_error_response("No content items provided")

        # Detect monthly patterns
        spanish_months = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]
        monthly_items = 0
        months_found = set()

        for item in content_items:
            item_lower = item.lower()
            for month in spanish_months:
                if month in item_lower:
                    monthly_items += 1
                    months_found.add(month)
                    break

        monthly_confidence = monthly_items / len(content_items) if content_items else 0
        monthly_pattern = {
            "detected": monthly_confidence > 0.5,
            "confidence": monthly_confidence,
            "monthly_items": monthly_items,
            "months_found": sorted(list(months_found)),
        }

        # Detect yearly patterns
        year_pattern = r"\b(20\d{2})\b"
        yearly_items = 0
        years_found = set()

        for item in content_items:
            years = re.findall(year_pattern, item)
            if years:
                yearly_items += 1
                years_found.update(years)

        yearly_confidence = yearly_items / len(content_items) if content_items else 0
        yearly_pattern = {
            "detected": yearly_confidence > 0.3 and len(years_found) > 1,
            "confidence": yearly_confidence,
            "yearly_items": yearly_items,
            "years_found": sorted(list(years_found)),
        }

        # Determine dominant pattern
        if monthly_pattern["detected"] and monthly_confidence > yearly_confidence:
            dominant_pattern = "monthly_series"
            recommendations = [
                "Use latest month prioritization",
                "Focus on most recent month content",
            ]
        elif yearly_pattern["detected"]:
            dominant_pattern = "yearly_series"
            recommendations = ["Prioritize current year content"]
        else:
            dominant_pattern = "none"
            recommendations = [
                "No clear temporal pattern - use content-based prioritization"
            ]

        result = {
            "monthly_pattern": monthly_pattern,
            "yearly_pattern": yearly_pattern,
            "dominant_pattern": dominant_pattern,
            "has_temporal_organization": monthly_pattern["detected"]
            or yearly_pattern["detected"],
            "recommendations": recommendations,
        }

        tool_instance._log_execution(
            "Temporal pattern detection completed", f"Dominant: {dominant_pattern}"
        )

        return tool_instance._create_success_response(
            result,
            {
                "detection_method": "temporal_patterns",
                "dominant_pattern": dominant_pattern,
            },
        )

    except Exception as e:
        return tool_instance._create_error_response(
            f"Temporal pattern detection failed: {str(e)}"
        )


@tool
async def extract_dates_from_text(
    text_items: List[str], language: str = "es"
) -> Dict[str, Any]:
    """
    Extract and normalize dates from text items.

    Args:
        text_items: List of text strings to analyze for dates
        language: Language for month detection ("es" or "en")

    Returns:
        Dict with extracted dates and confidence scores
    """
    tool_instance = BaseTool("extract_dates_from_text", "Extract dates from text")

    try:
        tool_instance._log_execution(
            "Starting date extraction", f"Analyzing {len(text_items)} items"
        )

        results = []

        for i, text in enumerate(text_items):
            if not text or len(text.strip()) < 3:
                continue

            extracted_dates = _extract_all_date_patterns(text.strip(), language)

            if extracted_dates:
                # Calculate confidence based on date quality and context
                confidence_score = max(d["confidence"] for d in extracted_dates)
                date_indicators = [
                    "actividades",
                    "programación",
                    "calendario",
                    "eventos",
                    "folleto",
                ]
                if any(indicator in text.lower() for indicator in date_indicators):
                    confidence_score += 0.1

                results.append(
                    {
                        "item_index": i,
                        "original_text": text,
                        "extracted_dates": extracted_dates,
                        "confidence_score": min(confidence_score, 1.0),
                    }
                )

        tool_instance._log_execution(
            "Date extraction completed", f"Found dates in {len(results)} items"
        )

        return tool_instance._create_success_response(
            results,
            {
                "extraction_method": "date_patterns",
                "language": language,
                "items_processed": len(text_items),
                "items_with_dates": len(results),
            },
        )

    except Exception as e:
        return tool_instance._create_error_response(f"Date extraction failed: {str(e)}")


@tool
async def prioritize_by_temporal_relevance(
    items_with_dates: List[Dict],
    strategy: str = "latest",
    base_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prioritize content items by temporal relevance.

    Args:
        items_with_dates: List of items with extracted date information
        strategy: Prioritization strategy ("latest", "current_month", "relevant_period")
        base_date: Base date for calculations (YYYY-MM-DD format)

    Returns:
        Dict with prioritized items and ranking explanations
    """
    tool_instance = BaseTool(
        "prioritize_by_temporal_relevance", "Prioritize by temporal relevance"
    )

    try:
        if base_date:
            reference_date = datetime.strptime(base_date, "%Y-%m-%d").date()
        else:
            reference_date = date.today()

        tool_instance._log_execution(
            "Starting prioritization", f"Strategy: {strategy}, Base: {reference_date}"
        )

        prioritized_items = []

        for item in items_with_dates:
            item_copy = item.copy()

            # Calculate relevance score based on strategy
            relevance_score = _calculate_relevance_score(
                item["extracted_dates"], strategy, reference_date
            )

            item_copy["relevance_score"] = relevance_score
            item_copy["priority_reasoning"] = _generate_priority_reasoning(
                item["extracted_dates"], strategy, reference_date
            )

            prioritized_items.append(item_copy)

        # Sort by relevance score (highest first)
        prioritized_items.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Add ranking
        for rank, item in enumerate(prioritized_items, 1):
            item["rank"] = rank

        tool_instance._log_execution(
            "Prioritization completed",
            f"Top item score: {prioritized_items[0]['relevance_score'] if prioritized_items else 0:.2f}",
        )

        return tool_instance._create_success_response(
            prioritized_items,
            {
                "prioritization_strategy": strategy,
                "reference_date": reference_date.strftime("%Y-%m-%d"),
                "items_ranked": len(prioritized_items),
                "top_item_score": (
                    prioritized_items[0]["relevance_score"] if prioritized_items else 0
                ),
            },
        )

    except Exception as e:
        return tool_instance._create_error_response(
            f"Prioritization failed: {str(e)}", items_with_dates
        )


# Essential helper functions only


def _extract_all_date_patterns(text: str, language: str) -> List[Dict]:
    """Extract all possible date patterns from text"""
    extracted_dates = []

    # Spanish month mappings
    if language == "es":
        months_map = {
            "enero": 1,
            "febrero": 2,
            "marzo": 3,
            "abril": 4,
            "mayo": 5,
            "junio": 6,
            "julio": 7,
            "agosto": 8,
            "septiembre": 9,
            "octubre": 10,
            "noviembre": 11,
            "diciembre": 12,
        }

        # Pattern for "Month YYYY" or "Month and Month YYYY"
        month_year_pattern = r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s+y\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre))?\s+(\d{4})"

        matches = re.finditer(month_year_pattern, text.lower())
        for match in matches:
            month1 = match.group(1)
            month2 = match.group(2) if match.group(2) else None
            year = int(match.group(3))

            # For ranges like "julio y agosto 2025"
            if month2:
                extracted_dates.append(
                    {
                        "type": "month_range",
                        "start_month": months_map[month1],
                        "end_month": months_map[month2],
                        "year": year,
                        "original_text": match.group(0),
                        "position": match.span(),
                        "confidence": 0.95,
                    }
                )
            else:
                extracted_dates.append(
                    {
                        "type": "month_year",
                        "month": months_map[month1],
                        "year": year,
                        "original_text": match.group(0),
                        "position": match.span(),
                        "confidence": 0.9,
                    }
                )

    # Numeric date patterns
    numeric_patterns = [
        r"(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})",  # DD/MM/YYYY
        r"(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})",  # YYYY/MM/DD
        r"(\d{1,2})[\/\-](\d{4})",  # MM/YYYY
    ]

    for pattern in numeric_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            try:
                if len(match.groups()) == 3:
                    # Full date
                    if len(match.group(1)) == 4:  # YYYY/MM/DD format
                        year, month, day = map(int, match.groups())
                    else:  # DD/MM/YYYY format
                        day, month, year = map(int, match.groups())

                    if 1 <= month <= 12 and 1 <= day <= 31 and 2020 <= year <= 2030:
                        extracted_dates.append(
                            {
                                "type": "full_date",
                                "day": day,
                                "month": month,
                                "year": year,
                                "original_text": match.group(0),
                                "position": match.span(),
                                "confidence": 0.8,
                            }
                        )

                elif len(match.groups()) == 2:
                    # Month/Year
                    month, year = map(int, match.groups())
                    if 1 <= month <= 12 and 2020 <= year <= 2030:
                        extracted_dates.append(
                            {
                                "type": "month_year_numeric",
                                "month": month,
                                "year": year,
                                "original_text": match.group(0),
                                "position": match.span(),
                                "confidence": 0.7,
                            }
                        )
            except (ValueError, IndexError):
                continue

    return extracted_dates


def _calculate_relevance_score(
    extracted_dates: List[Dict], strategy: str, reference_date: date
) -> float:
    """Calculate relevance score based on strategy"""
    if not extracted_dates:
        return 0.0

    current_year = reference_date.year
    current_month = reference_date.month

    max_score = 0.0

    for date_info in extracted_dates:
        score = 0.0

        if strategy == "latest":
            # Score based on how recent the date is
            if date_info.get("year"):
                year_diff = date_info["year"] - current_year
                if year_diff >= 0:  # Future or current year
                    score = 1.0 - (year_diff * 0.1)  # Penalize distant future

                    if date_info.get("month"):
                        month_diff = (
                            (date_info["year"] - current_year) * 12
                            + date_info["month"]
                            - current_month
                        )
                        if month_diff >= 0:  # Future or current month
                            score += 0.5 - (month_diff * 0.05)  # Bonus for near future

        elif strategy == "current_month":
            # Score based on proximity to current month
            if (
                date_info.get("year") == current_year
                and date_info.get("month") == current_month
            ):
                score = 1.0
            elif date_info.get("year") == current_year:
                month_diff = abs(date_info["month"] - current_month)
                score = max(0, 0.8 - (month_diff * 0.1))

        elif strategy == "relevant_period":
            # Score for current and next 2 months
            if date_info.get("year") and date_info.get("month"):
                target_date = date(date_info["year"], date_info["month"], 1)
                days_diff = (target_date - reference_date).days

                if -30 <= days_diff <= 60:  # Within relevant period
                    score = 1.0 - (abs(days_diff) / 100)

        # Handle month ranges (e.g., "julio y agosto 2025")
        if date_info.get("type") == "month_range":
            # Use the later month for scoring
            end_month = date_info.get("end_month", date_info.get("start_month"))
            if end_month:
                date_info_copy = date_info.copy()
                date_info_copy["month"] = end_month
                range_score = _calculate_relevance_score(
                    [date_info_copy], strategy, reference_date
                )
                score = max(score, range_score + 0.1)  # Bonus for ranges

        max_score = max(max_score, score)

    return min(max_score, 1.0)


def _generate_priority_reasoning(
    extracted_dates: List[Dict], strategy: str, reference_date: date
) -> str:
    """Generate human-readable reasoning for prioritization"""
    if not extracted_dates:
        return "No dates found"

    # Find the highest confidence date
    best_date = max(extracted_dates, key=lambda d: d.get("confidence", 0))

    if best_date.get("type") == "month_range":
        month_names = [
            "",
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]
        start_month = month_names[best_date.get("start_month", 1)]
        end_month = month_names[best_date.get("end_month", 1)]
        date_str = f"{start_month} y {end_month} {best_date.get('year')}"
    elif best_date.get("month") and best_date.get("year"):
        month_names = [
            "",
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]
        month_name = month_names[best_date.get("month")]
        date_str = f"{month_name} {best_date.get('year')}"
    else:
        date_str = best_date.get("original_text", "fecha detectada")

    if strategy == "latest":
        return f"Priorizado por ser el más reciente: {date_str}"
    elif strategy == "current_month":
        return f"Priorizado por proximidad al mes actual: {date_str}"
    else:
        return f"Priorizado por relevancia temporal ({strategy}): {date_str}"
