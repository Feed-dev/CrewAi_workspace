# CoWrite/src/writer_crew/tools/search_tools.py
"""
This module provides tools related to searching external resources, primarily web search.
"""

import os
from crewai_tools import SerperDevTool

# Note: Requires the SERPER_API_KEY environment variable to be set.
# You can get a key from https://serper.dev
# Consider using a .env file to manage environment variables.

try:
    # Instantiate the SerperDevTool
    # This tool performs web searches using the Serper.dev API.
    web_search_tool = SerperDevTool()

    # You could add more tools here, e.g., for specific website searches
    # or other search APIs if needed later.

except Exception as e:
    print(f"Error instantiating search tools: {e}")
    print("Please ensure the SERPER_API_KEY environment variable is set correctly.")
    # Set tool to None or raise an error to prevent use if initialization fails
    web_search_tool = None

# Example of how to potentially add more tools later:
# from crewai_tools import WebsiteSearchTool
# specific_site_search = WebsiteSearchTool(website='example.com')

# You can also create custom tools using the @tool decorator
# from crewai import tool
# @tool("Custom Search Tool")
# def custom_search(query: str) -> str:
#     """Performs a custom search operation."""
#     # Implementation here...
#     return f"Results for {query}" 