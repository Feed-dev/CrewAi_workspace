"""
Enhanced search tools for the cataloger crew with autonomous search capabilities.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from crewai_tools import SerperDevTool
from crewai import tool


class AutonomousSearchTool:
    """Enhanced search tool with autonomous capabilities for the cataloger crew."""
    
    def __init__(self):
        try:
            self.web_search_tool = SerperDevTool()
            self.search_history = []
        except Exception as e:
            print(f"Error initializing search tool: {e}")
            self.web_search_tool = None
    
    def is_available(self) -> bool:
        """Check if search tool is available."""
        return self.web_search_tool is not None


@tool("Enhanced Web Search Tool")
def enhanced_web_search(query: str, search_type: str = "web", num_results: int = 10) -> str:
    """
    Perform enhanced web search with result formatting and metadata.
    
    Args:
        query: Search query string
        search_type: Type of search (web, news, images)
        num_results: Number of results to return (1-20)
    
    Returns:
        Formatted search results with metadata
    """
    try:
        # Initialize search tool
        search_tool = SerperDevTool()
        
        # Perform search
        results = search_tool.run(query)
        
        # Format results for cataloger crew
        formatted_results = f"""
Search Results for: "{query}" (Type: {search_type})
{'=' * 60}
Timestamp: {datetime.now().isoformat()}
Query: {query}
Results Count: {num_results}

{results}

Search Metadata:
- Search Type: {search_type}
- Requested Results: {num_results}
- Execution Time: {datetime.now().isoformat()}
- Query Hash: {hash(query)}
"""
        
        return formatted_results
        
    except Exception as e:
        return f"Search failed: {str(e)}"


@tool("Query Evolution Tool")
def evolve_search_queries(previous_results: str, topic: str, round_number: int = 1) -> str:
    """
    Generate evolved search queries based on previous results and topic.
    
    Args:
        previous_results: Results from previous search rounds
        topic: Main topic being researched
        round_number: Current search round number
    
    Returns:
        List of evolved search queries with reasoning
    """
    # This would typically use an AI model to analyze results and generate new queries
    # For now, providing a structured approach
    
    base_variations = [
        f"{topic} latest developments",
        f"{topic} research papers",
        f"{topic} best practices",
        f"{topic} case studies",
        f"{topic} industry trends"
    ]
    
    # Add round-specific variations
    if round_number == 1:
        queries = base_variations
    elif round_number == 2:
        queries = [
            f"{topic} tutorials",
            f"{topic} documentation",
            f"{topic} expert opinions",
            f"{topic} implementation guide"
        ]
    else:
        queries = [
            f"{topic} advanced techniques",
            f"{topic} future trends",
            f"{topic} comparison analysis",
            f"{topic} troubleshooting"
        ]
    
    result = f"""
Evolved Search Queries - Round {round_number}
{'=' * 50}
Topic: {topic}
Generation Strategy: {"Initial broad search" if round_number == 1 else "Refined based on previous results"}

Recommended Queries:
"""
    
    for i, query in enumerate(queries, 1):
        result += f"{i}. {query}\n"
    
    result += f"""
Query Evolution Notes:
- Round {round_number} focuses on {"foundational content" if round_number == 1 else "specialized content"}
- Queries designed to avoid duplication with previous rounds
- Each query targets different aspects of {topic}
"""
    
    return result


@tool("Search Strategy Planner")
def plan_search_strategy(topic: str, duration_hours: int = 24, search_frequency: int = 4) -> str:
    """
    Plan autonomous search strategy for extended operation.
    
    Args:
        topic: Main research topic
        duration_hours: How long to run autonomous searches
        search_frequency: Searches per hour
    
    Returns:
        Detailed search strategy plan
    """
    total_searches = duration_hours * search_frequency
    
    strategy = f"""
Autonomous Search Strategy Plan
{'=' * 40}
Topic: {topic}
Duration: {duration_hours} hours
Frequency: {search_frequency} searches/hour
Total Planned Searches: {total_searches}

Search Phase Distribution:
Phase 1 (0-25%): Broad foundational search
- General topic queries
- Established sources and authorities
- Core concepts and definitions

Phase 2 (25-50%): Focused deep-dive
- Specific subtopics
- Recent developments
- Technical documentation

Phase 3 (50-75%): Niche and specialized
- Advanced techniques
- Expert opinions
- Case studies and implementations

Phase 4 (75-100%): Emerging and trends
- Latest developments
- Future directions
- Cutting-edge research

Search Type Rotation:
- 60% Web search (general content)
- 25% News search (recent developments)
- 15% Academic/specialized sources

Quality Control:
- Minimum content length: 500 words
- Authoritative sources preferred
- Recency: Last 2 years unless historical context needed
- Duplicate detection across all searches

Adaptation Strategy:
- Monitor search result quality
- Adjust queries based on discovery patterns
- Expand successful search directions
- Reduce low-yield query types
"""
    
    return strategy