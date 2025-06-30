# backend/tools/pdf_tools.py

"""
PDF content extraction tools
"""
from typing import Any, Dict

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from langchain_core.tools import tool

from .base_tool import BaseTool
from .html_tools import _parse_url_input


@tool
async def read_pdf_content(pdf_url: str) -> Dict[str, Any]:
    """
    Reads the entire text content of a single PDF document from a URL.

    Args:
        pdf_url: The direct URL to the PDF document.

    Returns:
        A dictionary containing the success status and the full text of the PDF.
    """
    tool_instance = BaseTool("read_pdf_content", "Read all text from a single PDF")
    
    target_url = _parse_url_input(pdf_url)
    if not target_url:
        return tool_instance._create_error_response(f"Invalid PDF URL input: {pdf_url}")

    try:
        tool_instance._log_execution("Starting PDF content extraction", f"URL: {target_url}")

        # Configure a simple PDF pipeline to extract text. OCR is enabled for scanned PDFs.
        pipeline_options = PdfPipelineOptions(do_ocr=True, do_table_structure=False)
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        # Convert the PDF from the URL
        result = converter.convert(target_url)
        
        # We use export_to_text() for a clean, simple text output
        content = result.document.export_to_text()

        tool_instance._log_execution("PDF content extracted successfully", f"Content length: {len(content)}")

        return tool_instance._create_success_response(
            data={"pdf_url": target_url, "content": content},
            metadata={"extraction_method": "pdf_full_text", "content_length": len(content)},
        )

    except Exception as e:
        return tool_instance._create_error_response(f"PDF content extraction failed for URL {target_url}: {str(e)}")