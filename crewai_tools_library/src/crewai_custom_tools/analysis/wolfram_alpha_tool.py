"""
Wolfram Alpha Tool for CrewAI

A custom tool that provides access to Wolfram Alpha's computational knowledge engine.
Perfect for mathematical calculations, scientific queries, and data analysis.
"""

import os
from typing import Type, Any, Optional
from pydantic import BaseModel, Field
from crewai_tools.tools.base_tool import BaseTool
from ..base.tool_base import EnhancedBaseTool


class WolframAlphaToolSchema(BaseModel):
    """Input schema for WolframAlphaTool."""
    query: str = Field(
        ..., 
        description="The query to search in Wolfram Alpha (e.g., 'integrate x^2 from 0 to 10', 'population of Tokyo', 'solve x^2 + 5x + 6 = 0')"
    )


class WolframAlphaTool(EnhancedBaseTool):
    """
    Wolfram Alpha Tool for CrewAI workflows.
    
    This tool provides access to Wolfram Alpha's computational knowledge engine,
    enabling agents to perform complex mathematical calculations, get factual information,
    solve equations, and analyze data.
    
    Required Environment Variables:
        WOLFRAM_APP_ID: Your Wolfram Alpha App ID
    
    Usage:
        tool = WolframAlphaTool()
        result = tool.run("integrate x^2 from 0 to 10")
    """
    
    name: str = "Wolfram Alpha Tool"
    description: str = (
        "Queries Wolfram Alpha for mathematical calculations, scientific data, "
        "factual information, and computational analysis. Supports complex math, "
        "statistics, physics, chemistry, geography, and more."
    )
    args_schema: Type[BaseModel] = WolframAlphaToolSchema
    
    def __init__(self, app_id: Optional[str] = None, **kwargs):
        """
        Initialize the Wolfram Alpha tool.
        
        Args:
            app_id: Wolfram Alpha App ID (optional, will use WOLFRAM_APP_ID env var if not provided)
        """
        super().__init__(**kwargs)
        self.app_id = app_id or os.getenv('WOLFRAM_APP_ID') or os.getenv('APP_ID')
        
        if not self.app_id:
            raise ValueError(
                "Wolfram Alpha App ID not found. Please set WOLFRAM_APP_ID environment variable "
                "or pass app_id parameter. Get your App ID from: https://developer.wolframalpha.com/"
            )
    
    def _run(self, query: str) -> str:
        """
        Execute a query against Wolfram Alpha.
        
        Args:
            query: The query string to send to Wolfram Alpha
            
        Returns:
            The result from Wolfram Alpha or an error message
        """
        try:
            # Import wolframalpha here to make it an optional dependency
            import wolframalpha
        except ImportError:
            return (
                "Error: wolframalpha package not installed. "
                "Install it with: pip install wolframalpha"
            )
        
        try:
            # Initialize Wolfram Alpha client
            client = wolframalpha.Client(self.app_id)
            
            # Query Wolfram Alpha
            response = client.query(query)
            
            # Check if query was successful
            if not response.get('@success', False):
                return f"Query failed. Wolfram Alpha could not process: '{query}'"
            
            # Extract results
            results = []
            
            # Get the primary result
            if hasattr(response, 'results') and response.results:
                primary_result = next(response.results, None)
                if primary_result and hasattr(primary_result, 'text'):
                    results.append(f"Result: {primary_result.text}")
            
            # Get additional pods with useful information
            if hasattr(response, 'pods'):
                for pod in response.pods:
                    if hasattr(pod, 'title') and hasattr(pod, 'text') and pod.text:
                        # Skip input interpretation and primary result (already captured)
                        if pod.title.lower() not in ['input', 'input interpretation', 'result']:
                            results.append(f"{pod.title}: {pod.text}")
            
            if results:
                return "\n".join(results)
            else:
                return f"No results found for query: '{query}'"
                
        except Exception as e:
            error_msg = str(e)
            if "Invalid appid" in error_msg:
                return (
                    "Error: Invalid Wolfram Alpha App ID. Please check your WOLFRAM_APP_ID "
                    "environment variable. Get a valid App ID from: https://developer.wolframalpha.com/"
                )
            elif "timeout" in error_msg.lower():
                return f"Error: Query timed out. Please try a simpler query: '{query}'"
            else:
                return f"Error querying Wolfram Alpha: {error_msg}"


# Alias for backward compatibility
WolframAlphaTool.__name__ = "WolframAlphaTool"