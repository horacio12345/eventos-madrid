# backend/tools/content_prioritization_tools.py

"""
Content prioritization tools for ranking and selecting most relevant content
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from .base_tool import BaseTool


@tool
async def rank_content_by_strategy(
    content_items: List[Dict],
    ranking_strategy: str = "combined",
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Rank content items using specified strategy and weights.

    Args:
        content_items: List of content items with scores/metadata
        ranking_strategy: Strategy ("temporal", "relevance", "combined", "position")
        weights: Optional weights for combined scoring

    Returns:
        Dict with ranked content items and ranking explanation
    """
    tool_instance = BaseTool("rank_content_by_strategy", "Rank content by strategy")

    try:
        tool_instance._log_execution(
            "Starting content ranking",
            f"Items: {len(content_items)}, Strategy: {ranking_strategy}",
        )

        if not content_items:
            return tool_instance._create_error_response("No content items provided")

        # Set default weights
        default_weights = {
            "temporal_score": 0.4,
            "relevance_score": 0.3,
            "confidence_score": 0.2,
            "position_score": 0.1,
        }

        if weights:
            default_weights.update(weights)

        ranked_items = []

        for i, item in enumerate(content_items):
            item_copy = item.copy()

            # Calculate final score based on strategy
            if ranking_strategy == "temporal":
                final_score = item.get("relevance_score", 0)  # From temporal analysis
            elif ranking_strategy == "relevance":
                final_score = item.get("confidence_score", 0)  # From content analysis
            elif ranking_strategy == "position":
                final_score = 1.0 - (i / len(content_items))  # Position-based
            else:  # combined
                final_score = _calculate_combined_score(
                    item, default_weights, i, len(content_items)
                )

            item_copy["final_score"] = final_score
            item_copy["ranking_strategy"] = ranking_strategy
            item_copy["ranking_explanation"] = _generate_ranking_explanation(
                item, ranking_strategy, final_score
            )

            ranked_items.append(item_copy)

        # Sort by final score (highest first)
        ranked_items.sort(key=lambda x: x["final_score"], reverse=True)

        # Add final ranking
        for rank, item in enumerate(ranked_items, 1):
            item["final_rank"] = rank

        tool_instance._log_execution(
            "Content ranking completed",
            f"Top score: {ranked_items[0]['final_score'] if ranked_items else 0:.3f}",
        )

        return tool_instance._create_success_response(
            ranked_items,
            {
                "ranking_strategy": ranking_strategy,
                "weights_used": default_weights,
                "items_ranked": len(ranked_items),
                "top_score": ranked_items[0]["final_score"] if ranked_items else 0,
            },
        )

    except Exception as e:
        return tool_instance._create_error_response(f"Content ranking failed: {str(e)}")


@tool
async def select_top_content(
    ranked_items: List[Dict], selection_criteria: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Select top content items based on criteria.

    Args:
        ranked_items: List of ranked content items
        selection_criteria: Criteria for selection (count, min_score, etc.)

    Returns:
        Dict with selected items and selection reasoning
    """
    tool_instance = BaseTool("select_top_content", "Select top content items")

    try:
        tool_instance._log_execution(
            "Starting content selection", f"Available items: {len(ranked_items)}"
        )

        if not ranked_items:
            return tool_instance._create_error_response("No ranked items provided")

        # Get selection criteria
        max_count = selection_criteria.get("max_count", 3)
        min_score = selection_criteria.get("min_score", 0.5)
        require_dates = selection_criteria.get("require_dates", False)

        selected_items = []
        rejected_items = []

        for item in ranked_items:
            should_select = True
            rejection_reasons = []

            # Check minimum score
            if item.get("final_score", 0) < min_score:
                should_select = False
                rejection_reasons.append(
                    f"Score {item.get('final_score', 0):.3f} below minimum {min_score}"
                )

            # Check if dates are required
            if require_dates and not item.get("extracted_dates"):
                should_select = False
                rejection_reasons.append("No dates found but dates required")

            # Check count limit
            if len(selected_items) >= max_count:
                should_select = False
                rejection_reasons.append(f"Already selected {max_count} items")

            if should_select:
                selected_items.append(item)
            else:
                item_copy = item.copy()
                item_copy["rejection_reasons"] = rejection_reasons
                rejected_items.append(item_copy)

        # Generate selection summary
        selection_summary = _generate_selection_summary(
            selected_items, selection_criteria
        )

        tool_instance._log_execution(
            "Content selection completed",
            f"Selected: {len(selected_items)}, Rejected: {len(rejected_items)}",
        )

        return tool_instance._create_success_response(
            selected_items,
            {
                "selection_criteria": selection_criteria,
                "items_selected": len(selected_items),
                "items_rejected": len(rejected_items),
                "rejected_items": rejected_items,
                "selection_summary": selection_summary,
            },
        )

    except Exception as e:
        return tool_instance._create_error_response(
            f"Content selection failed: {str(e)}"
        )


@tool
async def prioritize_content_final(
    analyzed_content: Dict,
    temporal_results: Dict,
    validation_results: Dict,
    strategy: str = "comprehensive",
) -> Dict[str, Any]:
    """
    Final prioritization combining all analysis results.

    Args:
        analyzed_content: Results from content analysis
        temporal_results: Results from temporal analysis
        validation_results: Results from content validation
        strategy: Overall prioritization strategy

    Returns:
        Dict with final prioritized content and decision reasoning
    """
    tool_instance = BaseTool("prioritize_content_final", "Final content prioritization")

    try:
        tool_instance._log_execution(
            "Starting final prioritization", f"Strategy: {strategy}"
        )

        # Extract organization type and temporal pattern
        organization_type = analyzed_content.get("organization_type", "unknown")
        dominant_pattern = temporal_results.get("dominant_pattern", "none")

        # Determine optimal approach
        if (
            organization_type == "pdf_collection"
            and dominant_pattern == "monthly_series"
        ):
            approach = "temporal_pdf_priority"
            recommendation = "Focus on most recent PDF in monthly series"
        elif organization_type == "event_listing" and temporal_results.get(
            "has_temporal_organization", False
        ):
            approach = "temporal_event_priority"
            recommendation = "Prioritize upcoming events chronologically"
        elif validation_results.get("events_valid", 0) > 0:
            approach = "validated_content_priority"
            recommendation = "Use validated content as primary source"
        else:
            approach = "fallback_analysis"
            recommendation = "Apply content-based analysis without temporal priority"

        # Generate final decision
        decision = {
            "approach": approach,
            "recommendation": recommendation,
            "confidence": _calculate_decision_confidence(
                analyzed_content, temporal_results, validation_results
            ),
            "next_actions": _generate_next_actions(
                approach, organization_type, dominant_pattern
            ),
        }

        tool_instance._log_execution(
            "Final prioritization completed", f"Approach: {approach}"
        )

        return tool_instance._create_success_response(
            decision,
            {
                "prioritization_strategy": strategy,
                "organization_type": organization_type,
                "temporal_pattern": dominant_pattern,
                "approach_selected": approach,
            },
        )

    except Exception as e:
        return tool_instance._create_error_response(
            f"Final prioritization failed: {str(e)}"
        )


# Helper functions


def _calculate_combined_score(
    item: Dict, weights: Dict[str, float], position: int, total_items: int
) -> float:
    """Calculate combined score using weights"""
    temporal_score = item.get("relevance_score", 0)
    relevance_score = item.get("confidence_score", 0)
    confidence_score = item.get("confidence_score", 0)
    position_score = 1.0 - (position / total_items)

    combined_score = (
        temporal_score * weights["temporal_score"]
        + relevance_score * weights["relevance_score"]
        + confidence_score * weights["confidence_score"]
        + position_score * weights["position_score"]
    )

    return min(combined_score, 1.0)


def _generate_ranking_explanation(item: Dict, strategy: str, final_score: float) -> str:
    """Generate explanation for ranking decision"""
    if strategy == "temporal":
        return f"Ranked by temporal relevance (score: {final_score:.3f})"
    elif strategy == "relevance":
        return f"Ranked by content relevance (score: {final_score:.3f})"
    elif strategy == "position":
        return f"Ranked by position in list (score: {final_score:.3f})"
    else:
        return f"Ranked by combined factors (score: {final_score:.3f})"


def _generate_selection_summary(
    selected_items: List[Dict], criteria: Dict[str, Any]
) -> str:
    """Generate summary of selection process"""
    if not selected_items:
        return "No items met selection criteria"

    avg_score = sum(item.get("final_score", 0) for item in selected_items) / len(
        selected_items
    )

    summary = f"Selected {len(selected_items)} items with average score {avg_score:.3f}"

    if criteria.get("min_score"):
        summary += f", all above {criteria['min_score']} threshold"

    return summary


def _calculate_decision_confidence(
    analyzed_content: Dict, temporal_results: Dict, validation_results: Dict
) -> float:
    """Calculate confidence in final decision"""
    confidence_factors = []

    # Structure analysis confidence
    if analyzed_content.get("structure_analysis", {}).get("structure_score"):
        confidence_factors.append(
            analyzed_content["structure_analysis"]["structure_score"]
        )

    # Temporal analysis confidence
    if temporal_results.get("monthly_pattern", {}).get("confidence"):
        confidence_factors.append(temporal_results["monthly_pattern"]["confidence"])

    # Validation success rate
    if (
        validation_results.get("events_valid", 0) > 0
        and validation_results.get("events_valid", 0)
        + validation_results.get("events_invalid", 0)
        > 0
    ):
        total_events = (
            validation_results["events_valid"] + validation_results["events_invalid"]
        )
        validation_rate = validation_results["events_valid"] / total_events
        confidence_factors.append(validation_rate)

    if confidence_factors:
        return sum(confidence_factors) / len(confidence_factors)
    else:
        return 0.5  # Default moderate confidence


def _generate_next_actions(
    approach: str, organization_type: str, temporal_pattern: str
) -> List[str]:
    """Generate recommended next actions"""
    actions = []

    if approach == "temporal_pdf_priority":
        actions.extend(
            [
                "Extract dates from PDF links",
                "Select most recent PDF",
                "Process selected PDF with appropriate extraction tools",
            ]
        )
    elif approach == "temporal_event_priority":
        actions.extend(
            [
                "Filter events by current/upcoming dates",
                "Extract event details systematically",
                "Validate event information for accuracy",
            ]
        )
    elif approach == "validated_content_priority":
        actions.extend(
            [
                "Use validated events as primary data source",
                "Apply additional quality checks if needed",
                "Format for final output",
            ]
        )
    else:
        actions.extend(
            [
                "Apply general content extraction strategy",
                "Manual review may be required",
                "Consider alternative data sources",
            ]
        )

    return actions
