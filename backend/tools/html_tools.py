# backend/tools/html_tools.py

"""
HTML extraction tools for web scraping
"""
import re
import asyncio
from typing import Dict, List, Any
from urllib.parse import urljoin, urlparse
from langchain_core.tools import tool
from playwright.async_api import async_playwright
import requests

from backend.core import get_settings
from .base_tool import BaseTool

settings = get_settings()


@tool
async def extract_html_simple(url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
    """
    Extract events from simple HTML pages using CSS selectors.
    
    Args:
        url: Website URL to scrape
        selectors: Dict with CSS selectors for event fields
    
    Returns:
        Dict with success status, extracted events data, and metadata
    """
    tool_instance = BaseTool("extract_html_simple", "Extract events from HTML using CSS selectors")
    
    try:
        tool_instance._log_execution("Starting HTML extraction", f"URL: {url}")
        
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=settings.playwright_headless)
            page = await browser.new_page()
            
            # Navigate to page
            await page.goto(url, timeout=settings.playwright_timeout)
            await page.wait_for_load_state("networkidle")
            
            # Extract events using selectors
            events = []
            event_containers = await page.query_selector_all(
                selectors.get("container", ".evento, .event, article")
            )
            
            for i, container in enumerate(event_containers):
                event_data = {}
                
                # Extract each field using provided selectors
                for field, selector in selectors.items():
                    if field == "container":
                        continue
                        
                    try:
                        element = await container.query_selector(selector)
                        if element:
                            if field in ["fecha_inicio", "fecha_fin", "fecha"]:
                                event_data[field] = await element.inner_text()
                            elif field == "precio":
                                price_text = await element.inner_text()
                                event_data[field] = _normalize_price(price_text)
                            else:
                                event_data[field] = await element.inner_text()
                    except Exception as e:
                        tool_instance._log_execution("Field extraction error", f"Field {field}: {str(e)}")
                
                # Add metadata
                event_data["url_original"] = url
                event_data["extraction_method"] = "html_simple"
                event_data["container_index"] = i
                
                if event_data.get("titulo"):  # Only add if has title
                    events.append(event_data)
            
            await browser.close()
            
            tool_instance._log_execution("Extraction completed", f"Found {len(events)} events")
            
            return tool_instance._create_success_response(
                events,
                {"extraction_method": "html_simple", "events_found": len(events)}
            )
            
    except Exception as e:
        return tool_instance._create_error_response(f"HTML extraction failed: {str(e)}")


@tool
async def extract_html_with_pdfs(url: str, pdf_selector: str = "a[href$='.pdf']") -> Dict[str, Any]:
    """
    Extract PDF links from HTML page and return them for further processing.
    
    Args:
        url: Website URL to analyze
        pdf_selector: CSS selector to find PDF links
    
    Returns:
        Dict with success status and list of PDF URLs found
    """
    tool_instance = BaseTool("extract_html_with_pdfs", "Extract PDF links from HTML pages")
    
    try:
        tool_instance._log_execution("Starting PDF link extraction", f"URL: {url}")
        
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=settings.playwright_headless)
            page = await browser.new_page()
            
            await page.goto(url, timeout=settings.playwright_timeout)
            await page.wait_for_load_state("networkidle")
            
            # Extract PDF links
            pdf_links = []
            link_elements = await page.query_selector_all(pdf_selector)
            
            for link_element in link_elements:
                href = await link_element.get_attribute("href")
                text = await link_element.inner_text()
                
                if href:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, href)
                    
                    pdf_links.append({
                        "url": absolute_url,
                        "link_text": text.strip(),
                        "source_page": url
                    })
            
            await browser.close()
            
            tool_instance._log_execution("PDF extraction completed", f"Found {len(pdf_links)} PDF links")
            
            return tool_instance._create_success_response(
                pdf_links,
                {"extraction_method": "html_pdf_links", "pdfs_found": len(pdf_links)}
            )
            
    except Exception as e:
        return tool_instance._create_error_response(f"PDF link extraction failed: {str(e)}")


@tool
async def analyze_web_structure(url: str) -> Dict[str, Any]:
    """
    Analyze website structure to determine optimal scraping strategy.
    
    Args:
        url: Website URL to analyze
    
    Returns:
        Dict with analysis results and recommended strategy
    """
    tool_instance = BaseTool("analyze_web_structure", "Analyze website structure for scraping strategy")
    
    try:
        tool_instance._log_execution("Starting web structure analysis", f"URL: {url}")
        
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=settings.playwright_headless)
            page = await browser.new_page()
            
            await page.goto(url, timeout=settings.playwright_timeout)
            await page.wait_for_load_state("networkidle")
            
            # Analyze page structure
            analysis = {
                "content_type": "unknown",
                "has_events": False,
                "has_pdf_links": False,
                "requires_javascript": False,
                "event_containers": [],
                "pdf_links": [],
                "recommended_strategy": "direct_html"
            }
            
            # Check for PDF links
            pdf_links = await page.query_selector_all("a[href$='.pdf']")
            if pdf_links:
                analysis["has_pdf_links"] = True
                analysis["pdf_links"] = len(pdf_links)
                analysis["content_type"] = "html_with_pdfs"
                analysis["recommended_strategy"] = "cascade_pdf_extraction"
            
            # Check for event-like content
            event_indicators = [
                ".evento", ".event", ".activity", ".actividad",
                "[class*='evento']", "[class*='event']", "article"
            ]
            
            for selector in event_indicators:
                elements = await page.query_selector_all(selector)
                if elements:
                    analysis["has_events"] = True
                    analysis["event_containers"].append({
                        "selector": selector,
                        "count": len(elements)
                    })
            
            # Check if JavaScript heavy
            initial_content = await page.content()
            await page.wait_for_timeout(2000)  # Wait 2 seconds
            final_content = await page.content()
            
            if len(final_content) > len(initial_content) * 1.2:
                analysis["requires_javascript"] = True
            
            # Determine final strategy
            if analysis["has_pdf_links"] and not analysis["has_events"]:
                analysis["recommended_strategy"] = "pdf_cascade_only"
            elif analysis["has_events"] and not analysis["has_pdf_links"]:
                analysis["recommended_strategy"] = "html_direct"
            elif analysis["has_events"] and analysis["has_pdf_links"]:
                analysis["recommended_strategy"] = "hybrid_html_pdf"
            
            await browser.close()
            
            tool_instance._log_execution("Analysis completed", f"Strategy: {analysis['recommended_strategy']}")
            
            return tool_instance._create_success_response(
                analysis,
                {"analysis_type": "web_structure"}
            )
            
    except Exception as e:
        return tool_instance._create_error_response(f"Web analysis failed: {str(e)}")


def _normalize_price(price_text: str) -> str:
    """Normalize price text to standard format"""
    if not price_text:
        return "Gratis"
    
    price_lower = price_text.lower().strip()
    
    # Check for free indicators
    free_words = ["gratis", "gratuito", "libre", "sin coste", "entrada libre", "free"]
    if any(word in price_lower for word in free_words):
        return "Gratis"
    
    # Extract numeric price
    numbers = re.findall(r'\d+(?:[,\.]\d{1,2})?', price_text)
    if numbers:
        price_num = numbers[0].replace(',', '.')
        return f"{price_num}€"
    
    return price_text[:20] if len(price_text) <= 20 else "Consultar precio"