# backend/tools/html_tools.py

"""
Core HTML interaction tools for web scraping agents.
"""
from typing import Any, Dict, List, Union
from urllib.parse import urljoin

from langchain_core.tools import tool
from playwright.async_api import async_playwright

from backend.core import get_settings

from .base_tool import BaseTool


def _parse_url_input(input_data: Union[str, Dict]) -> str:
    """
    Parses various input formats from the agent to robustly extract a URL.
    """
    if isinstance(input_data, dict):
        return input_data.get("url", "")
    if isinstance(input_data, str):
        # Handles plain URLs and "url='...'" formats
        if '=' in input_data:
            parts = input_data.split('=', 1)
            if len(parts) == 2 and parts[0].strip().lower() == 'url':
                return parts[1].strip().strip('"\'')
        return input_data.strip()
    return ""


@tool
async def get_page_links(url: Union[str, Dict]) -> Dict[str, Any]:
    """
    Visits a URL and extracts all links, returning them with their anchor texts.
    This is the primary tool for exploring a web page.

    Args:
        url: The URL of the page to explore.

    Returns:
        A dictionary containing the success status and a list of found links,
        each with its text and absolute URL.
    """
    tool_instance = BaseTool("get_page_links", "Get all links from a web page")
    
    target_url = _parse_url_input(url)
    if not target_url:
        return tool_instance._create_error_response(f"Invalid URL input: {url}")

    try:
        tool_instance._log_execution("Starting link extraction", f"URL: {target_url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(target_url, wait_until="networkidle", timeout=30000)

            links = await page.eval_on_selector_all("a", """
                (anchors) =>
                    anchors.map((a) => ({
                        text: a.innerText.trim(),
                        href: a.href,
                    }))
            """)
            
            await browser.close()

            # Make all hrefs absolute
            for link in links:
                if link["href"]:
                    link["href"] = urljoin(target_url, link["href"])

            tool_instance._log_execution("Link extraction successful", f"Found {len(links)} links.")

            return tool_instance._create_success_response(
                data=links,
                metadata={"url": target_url, "links_found": len(links)}
            )

    except Exception as e:
        return tool_instance._create_error_response(f"Failed to get links from {target_url}: {str(e)}")
