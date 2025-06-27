# backend/tools/base_tool.py

"""
Base tool class for all scraping tools
"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BaseTool:
    """
    Base class for all scraping tools providing common functionality
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.created_at = datetime.now()

    def _create_success_response(
        self, data: Any, metadata: Optional[Dict] = None
    ) -> Dict:
        """Create standardized success response"""
        return {
            "success": True,
            "data": data,
            "errors": [],
            "metadata": {
                "tool_name": self.name,
                "execution_time": datetime.now().isoformat(),
                **(metadata or {}),
            },
        }

    def _create_error_response(self, error_msg: str, data: Any = None) -> Dict:
        """Create standardized error response"""
        logger.error(f"Tool {self.name} error: {error_msg}")
        return {
            "success": False,
            "data": data or [],
            "errors": [error_msg],
            "metadata": {
                "tool_name": self.name,
                "execution_time": datetime.now().isoformat(),
                "error_occurred": True,
            },
        }

    def _log_execution(self, operation: str, details: Optional[str] = None):
        """Log tool execution for debugging"""
        log_msg = f"Tool {self.name} - {operation}"
        if details:
            log_msg += f": {details}"
        logger.info(log_msg)
