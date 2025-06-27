# backend/tools/pdf_tools.py

"""
PDF extraction tools for document processing
"""
import re
from typing import Any, Dict, List

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from langchain_core.tools import tool

from .base_tool import BaseTool


@tool
async def extract_pdf_direct(
    pdf_url: str, extraction_patterns: Dict[str, str]
) -> Dict[str, Any]:
    """
    Extract events directly from a single PDF document.

    Args:
        pdf_url: Direct URL to PDF document
        extraction_patterns: Dict with regex patterns for event fields

    Returns:
        Dict with success status and extracted events
    """
    tool_instance = BaseTool(
        "extract_pdf_direct", "Extract events from single PDF document"
    )

    try:
        tool_instance._log_execution("Starting PDF extraction", f"URL: {pdf_url}")

        # Configure PDF pipeline
        pipeline_options = PdfPipelineOptions(do_ocr=True, do_table_structure=True)

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        # Convert PDF
        result = converter.convert(pdf_url)
        content = result.document.export_to_markdown()

        tool_instance._log_execution("PDF converted", f"Content length: {len(content)}")

        # Extract events using patterns
        events = _extract_events_from_text(content, extraction_patterns, pdf_url)

        tool_instance._log_execution(
            "Extraction completed", f"Found {len(events)} events"
        )

        return tool_instance._create_success_response(
            events, {"extraction_method": "pdf_direct", "events_found": len(events)}
        )

    except Exception as e:
        return tool_instance._create_error_response(f"PDF extraction failed: {str(e)}")


@tool
async def extract_multiple_pdfs(
    pdf_urls: List[str], extraction_patterns: Dict[str, str]
) -> Dict[str, Any]:
    """
    Extract events from multiple PDF documents.

    Args:
        pdf_urls: List of PDF URLs to process
        extraction_patterns: Dict with regex patterns for event fields

    Returns:
        Dict with success status and combined extracted events
    """
    tool_instance = BaseTool(
        "extract_multiple_pdfs", "Extract events from multiple PDF documents"
    )

    try:
        tool_instance._log_execution(
            "Starting multiple PDF extraction", f"PDFs: {len(pdf_urls)}"
        )

        all_events = []
        processing_errors = []

        # Configure PDF pipeline
        pipeline_options = PdfPipelineOptions(do_ocr=True, do_table_structure=True)

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        # Process each PDF
        for i, pdf_url in enumerate(pdf_urls):
            try:
                tool_instance._log_execution(
                    "Processing PDF", f"{i+1}/{len(pdf_urls)}: {pdf_url}"
                )

                # Convert PDF
                result = converter.convert(pdf_url)
                content = result.document.export_to_markdown()

                # Extract events
                events = _extract_events_from_text(
                    content, extraction_patterns, pdf_url
                )
                all_events.extend(events)

            except Exception as e:
                error_msg = f"Failed to process PDF {pdf_url}: {str(e)}"
                processing_errors.append(error_msg)
                tool_instance._log_execution("PDF processing error", error_msg)

        tool_instance._log_execution(
            "Multiple PDF extraction completed",
            f"Total events: {len(all_events)}, Errors: {len(processing_errors)}",
        )

        return tool_instance._create_success_response(
            all_events,
            {
                "extraction_method": "pdf_multiple",
                "events_found": len(all_events),
                "pdfs_processed": len(pdf_urls) - len(processing_errors),
                "pdfs_failed": len(processing_errors),
                "processing_errors": processing_errors,
            },
        )

    except Exception as e:
        return tool_instance._create_error_response(
            f"Multiple PDF extraction failed: {str(e)}"
        )


def _extract_events_from_text(
    content: str, patterns: Dict[str, str], source_url: str
) -> List[Dict]:
    """Extract events from text content using regex patterns"""
    events = []

    # Split content into potential event sections
    sections = _split_into_event_sections(content)

    for i, section in enumerate(sections):
        event_data = {}

        # Extract fields using patterns
        for field, pattern in patterns.items():
            try:
                match = re.search(pattern, section, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
                    event_data[field] = value.strip()
            except Exception:
                continue

        # Add metadata
        event_data["url_original"] = source_url
        event_data["extraction_method"] = "pdf_text"
        event_data["section_index"] = i

        # Only add if has minimum required fields
        if event_data.get("titulo") or event_data.get("fecha"):
            events.append(event_data)

    return events


def _split_into_event_sections(content: str) -> List[str]:
    """Split text content into sections that likely contain individual events"""
    # Common patterns for splitting events in Spanish documents
    split_patterns = [
        r"\n(?=\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})",  # Date at start of line
        r"\n(?=[A-ZÁÉÍÓÚ][A-Za-záéíóúñü\s]{10,})",  # Title-like text
        r"\n\s*[-•]\s*",  # Bullet points
        r"\n\s*\d+[\.\)]\s*",  # Numbered lists
    ]

    # Try each pattern
    for pattern in split_patterns:
        sections = re.split(pattern, content)
        if len(sections) > 1:
            return [s.strip() for s in sections if len(s.strip()) > 50]

    # Fallback: split by paragraphs
    paragraphs = content.split("\n\n")
    return [p.strip() for p in paragraphs if len(p.strip()) > 50]
