# backend/tools/source/ssreyes_tools.py
from typing import Any, Dict
from langchain_core.tools import tool
from ..html_tools import get_page_links
from ..pdf_tools import read_pdf_content

@tool
async def extract_ssreyes_recent_events(url: str) -> Dict[str, Any]:
    """
    Extract events from the most recent SSReyes PDF (julio y agosto 2025).
    Specifically designed for ssreyes.org dinamización social pages.
    """
    try:
        # Get all links from the page
        links_result = await get_page_links.ainvoke({"url": url})
        if not links_result['success']:
            return links_result
        
        # Find the most recent PDF (julio y agosto 2025)
        target_pdf = None
        for link in links_result['data']:
            text = link['text'].lower()
            href = link['href']
            if ('.pdf' in href and 
                'julio' in text and 
                'agosto' in text and 
                '2025' in text):
                target_pdf = href
                break
        
        if not target_pdf:
            return {
                "success": False,
                "data": [],
                "errors": ["No current PDF found for julio y agosto 2025"],
                "metadata": {"tool_name": "extract_ssreyes_recent_events"}
            }
        
        # Read the PDF content
        return await read_pdf_content.ainvoke({"pdf_url": target_pdf})
        
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "errors": [f"SSReyes extraction failed: {str(e)}"],
            "metadata": {"tool_name": "extract_ssreyes_recent_events"}
        }