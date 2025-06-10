"""
CrewAI Custom Tools Library

A comprehensive collection of custom tools for CrewAI workflows.
All tools follow CrewAI best practices for seamless integration.
"""

from .base.tool_base import EnhancedBaseTool
from .data.file_tools import (
    FileReaderTool,
    FileWriterTool,
    DirectoryListTool,
    FileValidatorTool,
)
from .web.search_tools import (
    EnhancedSearchTool,
    WebScrapingTool,
)
from .content.text_tools import (
    TextAnalyzerTool,
    TextCleanerTool,
    TextSummarizerTool,
)
from .analysis.wolfram_alpha_tool import (
    WolframAlphaTool,
)

__version__ = "0.1.0"
__author__ = "CrewAI Workspace"

# Export main tool categories
__all__ = [
    # Base classes
    "EnhancedBaseTool",
    
    # Data tools
    "FileReaderTool",
    "FileWriterTool", 
    "DirectoryListTool",
    "FileValidatorTool",
    
    # Web tools
    "EnhancedSearchTool",
    "WebScrapingTool",
    
    # Content tools
    "TextAnalyzerTool",
    "TextCleanerTool",
    "TextSummarizerTool",
    
    # Analysis tools
    "WolframAlphaTool",
]

# Tool registry for easy discovery
TOOL_REGISTRY = {
    "data": {
        "FileReaderTool": FileReaderTool,
        "FileWriterTool": FileWriterTool,
        "DirectoryListTool": DirectoryListTool,
        "FileValidatorTool": FileValidatorTool,
    },
    "web": {
        "EnhancedSearchTool": EnhancedSearchTool,
        "WebScrapingTool": WebScrapingTool,
    },
    "content": {
        "TextAnalyzerTool": TextAnalyzerTool,
        "TextCleanerTool": TextCleanerTool,
        "TextSummarizerTool": TextSummarizerTool,
    },
    "analysis": {
        "WolframAlphaTool": WolframAlphaTool,
    },
}

def get_tool(category: str, tool_name: str):
    """Get a tool class by category and name."""
    if category not in TOOL_REGISTRY:
        raise ValueError(f"Unknown category: {category}")
    if tool_name not in TOOL_REGISTRY[category]:
        raise ValueError(f"Unknown tool: {tool_name} in category: {category}")
    return TOOL_REGISTRY[category][tool_name]

def list_tools(category: str = None) -> dict:
    """List available tools, optionally filtered by category."""
    if category:
        return TOOL_REGISTRY.get(category, {})
    return TOOL_REGISTRY