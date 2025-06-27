# backend/tools/content_analysis_tools.py

"""
Content analysis tools for detecting basic organization patterns in web content
"""
import re
from typing import Any, Dict, List

from langchain_core.tools import tool

from .base_tool import BaseTool


@tool
async def analyze_page_structure(content_items: List[str]) -> Dict[str, Any]:
    """
    Analyze basic structural patterns in page content.

    Args:
        content_items: List of content strings (titles, links, descriptions)

    Returns:
        Dict with structural analysis and organization type
    """
    tool_instance = BaseTool(
        "analyze_page_structure", "Analyze page structural patterns"
    )

    try:
        tool_instance._log_execution(
            "Starting structure analysis", f"Items: {len(content_items)}"
        )

        if not content_items:
            return tool_instance._create_error_response("No content items provided")

        # Analyze structural patterns
        structure_analysis = _analyze_structural_patterns(content_items)
        content_type_analysis = _analyze_content_types(content_items)

        # Determine organization type
        organization_type = _determine_organization_type(
            structure_analysis, content_type_analysis
        )

        # Generate recommendations
        recommendations = _generate_recommendations(
            organization_type, structure_analysis, content_type_analysis
        )

        result = {
            "organization_type": organization_type,
            "structure_analysis": structure_analysis,
            "content_type_analysis": content_type_analysis,
            "recommendations": recommendations,
        }

        tool_instance._log_execution(
            "Structure analysis completed", f"Type: {organization_type}"
        )

        return tool_instance._create_success_response(
            result,
            {"analysis_method": "page_structure", "items_analyzed": len(content_items)},
        )

    except Exception as e:
        return tool_instance._create_error_response(
            f"Structure analysis failed: {str(e)}"
        )


@tool
async def analyze_content_types(content_items: List[str]) -> Dict[str, Any]:
    """
    Analyze types of content present on the page.

    Args:
        content_items: List of content strings to analyze

    Returns:
        Dict with content type analysis and dominant type
    """
    tool_instance = BaseTool("analyze_content_types", "Analyze content types")

    try:
        tool_instance._log_execution(
            "Starting content type analysis", f"Items: {len(content_items)}"
        )

        content_types = {
            "pdf_documents": 0,
            "web_pages": 0,
            "calendar_events": 0,
            "news_items": 0,
            "activities": 0,
            "other": 0,
        }

        type_indicators = {
            "pdf_documents": [".pdf", "documento", "folleto", "programa", "descarga"],
            "calendar_events": ["actividades", "eventos", "programación", "calendario"],
            "news_items": ["noticia", "comunicado", "información", "aviso"],
            "activities": ["taller", "curso", "charla", "encuentro", "sesión"],
        }

        categorized_items = []

        for i, item in enumerate(content_items):
            item_lower = item.lower()
            item_categorized = False

            for content_type, indicators in type_indicators.items():
                if any(indicator in item_lower for indicator in indicators):
                    content_types[content_type] += 1
                    categorized_items.append(
                        {"index": i, "text": item, "type": content_type}
                    )
                    item_categorized = True
                    break

            if not item_categorized:
                content_types["other"] += 1
                categorized_items.append({"index": i, "text": item, "type": "other"})

        # Determine dominant type
        dominant_type = max(content_types, key=content_types.get)
        categorization_ratio = (
            (len(content_items) - content_types["other"]) / len(content_items)
            if content_items
            else 0
        )

        result = {
            "content_types": content_types,
            "dominant_type": dominant_type,
            "categorization_ratio": categorization_ratio,
            "categorized_items": categorized_items,
        }

        tool_instance._log_execution(
            "Content type analysis completed", f"Dominant: {dominant_type}"
        )

        return tool_instance._create_success_response(
            result,
            {
                "analysis_method": "content_types",
                "dominant_type": dominant_type,
                "categorization_success": categorization_ratio,
            },
        )

    except Exception as e:
        return tool_instance._create_error_response(
            f"Content type analysis failed: {str(e)}"
        )


# Helper functions


def _analyze_structural_patterns(content_items: List[str]) -> Dict[str, Any]:
    """Analyze structural patterns in content"""

    # Analyze common prefixes/suffixes
    common_prefixes = _find_common_patterns(content_items, pattern_type="prefix")
    common_suffixes = _find_common_patterns(content_items, pattern_type="suffix")

    # Analyze numbering patterns
    numbered_items = sum(
        1 for item in content_items if re.match(r"^\d+\.?\s", item.strip())
    )

    # Analyze bullet patterns
    bulleted_items = sum(
        1 for item in content_items if re.match(r"^[-•*]\s", item.strip())
    )

    # Analyze length consistency
    lengths = [len(item) for item in content_items]
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    length_variance = (
        sum((l - avg_length) ** 2 for l in lengths) / len(lengths) if lengths else 0
    )

    return {
        "common_prefixes": common_prefixes,
        "common_suffixes": common_suffixes,
        "numbered_items": numbered_items,
        "bulleted_items": bulleted_items,
        "has_consistent_structure": length_variance < (avg_length * 0.5),
        "average_length": avg_length,
        "structure_score": _calculate_structure_score(
            common_prefixes,
            common_suffixes,
            numbered_items,
            bulleted_items,
            len(content_items),
        ),
    }


def _analyze_content_types(content_items: List[str]) -> Dict[str, Any]:
    """Analyze types of content present"""

    content_types = {
        "pdf_links": 0,
        "html_pages": 0,
        "calendar_events": 0,
        "news_articles": 0,
        "documents": 0,
    }

    # Content type indicators
    pdf_indicators = [".pdf", "documento", "folleto", "programa"]
    calendar_indicators = ["actividades", "eventos", "programación", "calendario"]
    news_indicators = ["noticia", "comunicado", "información", "aviso"]

    for item in content_items:
        item_lower = item.lower()

        if any(indicator in item_lower for indicator in pdf_indicators):
            content_types["pdf_links"] += 1

        if any(indicator in item_lower for indicator in calendar_indicators):
            content_types["calendar_events"] += 1

        if any(indicator in item_lower for indicator in news_indicators):
            content_types["news_articles"] += 1

        # Check for document extensions
        if re.search(r"\.(pdf|doc|docx|xls|xlsx)($|\s)", item_lower):
            content_types["documents"] += 1

    # Determine dominant content type
    dominant_type = max(content_types, key=content_types.get)
    total_categorized = sum(content_types.values())

    return {
        "content_types": content_types,
        "dominant_type": dominant_type,
        "categorization_ratio": (
            total_categorized / len(content_items) if content_items else 0
        ),
    }


def _determine_organization_type(
    structure_analysis: Dict, content_type_analysis: Dict
) -> str:
    """Determine the primary organization type"""

    dominant_content = content_type_analysis.get("dominant_type", "unknown")

    if dominant_content == "pdf_links":
        return "pdf_collection"
    elif dominant_content == "calendar_events":
        return "event_listing"
    elif (
        structure_analysis.get("numbered_items", 0)
        > len(content_type_analysis.get("content_types", {})) * 0.5
    ):
        return "numbered_list"
    elif structure_analysis.get("has_consistent_structure", False):
        return "structured_list"
    else:
        return "unstructured_content"


def _generate_recommendations(
    organization_type: str, structure_analysis: Dict, content_type_analysis: Dict
) -> List[str]:
    """Generate extraction strategy recommendations"""

    recommendations = []

    if organization_type == "pdf_collection":
        recommendations.extend(
            [
                "Use PDF extraction tools",
                "Consider temporal analysis for PDF prioritization",
                "Check for naming patterns in PDF links",
            ]
        )

    elif organization_type == "event_listing":
        recommendations.extend(
            [
                "Extract event details systematically",
                "Look for date, location, and description patterns",
                "Consider temporal filtering for current events",
            ]
        )

    elif organization_type in ["numbered_list", "structured_list"]:
        recommendations.extend(
            [
                "Use structural patterns for extraction",
                "Maintain list order for priority",
                "Look for consistent data patterns",
            ]
        )

    else:
        recommendations.extend(
            [
                "Content appears unstructured",
                "May require content-based analysis",
                "Consider alternative extraction strategies",
            ]
        )

    return recommendations


def _find_common_patterns(items: List[str], pattern_type: str = "prefix") -> List[str]:
    """Find common prefixes or suffixes in content items"""
    if not items or len(items) < 2:
        return []

    patterns = []

    if pattern_type == "prefix":
        # Find common prefixes
        for length in range(3, min(20, min(len(item) for item in items))):
            potential_prefix = items[0][:length]
            if (
                sum(1 for item in items if item.startswith(potential_prefix))
                >= len(items) * 0.7
            ):
                patterns.append(potential_prefix)

    elif pattern_type == "suffix":
        # Find common suffixes
        for length in range(3, min(20, min(len(item) for item in items))):
            potential_suffix = items[0][-length:]
            if (
                sum(1 for item in items if item.endswith(potential_suffix))
                >= len(items) * 0.7
            ):
                patterns.append(potential_suffix)

    return patterns[:3]  # Return top 3 patterns


def _calculate_structure_score(
    common_prefixes: List[str],
    common_suffixes: List[str],
    numbered_items: int,
    bulleted_items: int,
    total_items: int,
) -> float:
    """Calculate confidence in structural analysis"""
    if total_items == 0:
        return 0.0

    structure_indicators = 0

    if common_prefixes:
        structure_indicators += 0.3
    if common_suffixes:
        structure_indicators += 0.3
    if numbered_items / total_items > 0.5:
        structure_indicators += 0.2
    if bulleted_items / total_items > 0.5:
        structure_indicators += 0.2

    return min(structure_indicators, 1.0)
