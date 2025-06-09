"""
Enhanced web search and scraping tools for CrewAI workflows.
"""

import requests
from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, Field, validator
import time

from ..base import EnhancedBaseTool, BaseToolInput, ToolValidationError, ToolExecutionError


class EnhancedSearchInput(BaseToolInput):
    """Input schema for EnhancedSearchTool."""
    query: str = Field(..., description="Search query string")
    num_results: int = Field(default=10, description="Number of results to return (1-20)")
    search_type: str = Field(default="web", description="Type of search: web, news, images")
    country: str = Field(default="us", description="Country code for localized results")
    
    @validator('num_results')
    def validate_num_results(cls, v):
        if not 1 <= v <= 20:
            raise ValueError('num_results must be between 1 and 20')
        return v
    
    @validator('search_type')
    def validate_search_type(cls, v):
        allowed_types = ['web', 'news', 'images']
        if v not in allowed_types:
            raise ValueError(f'search_type must be one of: {allowed_types}')
        return v


class EnhancedSearchTool(EnhancedBaseTool):
    """
    Enhanced search tool that extends SerperDevTool functionality.
    Provides structured search results with additional metadata.
    """
    
    name: str = "Enhanced Search Tool"
    description: str = (
        "Performs web searches with enhanced result formatting and metadata. "
        "Supports different search types (web, news, images) and provides "
        "structured results with titles, URLs, snippets, and relevance scoring. "
        "Use this for comprehensive research and information gathering."
    )
    args_schema: type[BaseModel] = EnhancedSearchInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://google.serper.dev"
        
        # Try to get API key from environment
        import os
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            self._log_warning("SERPER_API_KEY not found in environment variables")
    
    def _validate_input(self, **kwargs) -> None:
        """Validate search parameters."""
        if not self.api_key:
            raise ToolValidationError(
                "SERPER_API_KEY is required. Please set it in your environment variables."
            )
        
        query = kwargs.get("query", "").strip()
        if not query:
            raise ToolValidationError("Query cannot be empty")
        
        if len(query) > 500:
            raise ToolValidationError("Query is too long (max 500 characters)")
    
    def _execute(self, **kwargs) -> str:
        """Execute enhanced search."""
        query = kwargs["query"]
        num_results = kwargs.get("num_results", 10)
        search_type = kwargs.get("search_type", "web")
        country = kwargs.get("country", "us")
        
        try:
            # Prepare search request
            endpoint = f"{self.base_url}/search"
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": num_results,
                "gl": country,
            }
            
            # Add search type specific parameters
            if search_type == "news":
                payload["type"] = "news"
            elif search_type == "images":
                payload["type"] = "images"
            
            # Make API request
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Format results
            return self._format_search_results(data, search_type, query)
            
        except requests.exceptions.RequestException as e:
            raise ToolExecutionError(f"Search API request failed: {str(e)}")
        except Exception as e:
            raise ToolExecutionError(f"Search execution failed: {str(e)}")
    
    def _format_search_results(self, data: Dict, search_type: str, query: str) -> str:
        """Format search results into structured text."""
        results = []
        results.append(f"Search Results for: '{query}' (Type: {search_type})")
        results.append("=" * 60)
        
        # Handle different result types
        if search_type == "web":
            organic_results = data.get("organic", [])
            for i, result in enumerate(organic_results, 1):
                title = result.get("title", "No title")
                url = result.get("link", "No URL")
                snippet = result.get("snippet", "No description available")
                
                results.append(f"\n{i}. {title}")
                results.append(f"   URL: {url}")
                results.append(f"   Description: {snippet}")
        
        elif search_type == "news":
            news_results = data.get("news", [])
            for i, result in enumerate(news_results, 1):
                title = result.get("title", "No title")
                url = result.get("link", "No URL")
                source = result.get("source", "Unknown source")
                date = result.get("date", "No date")
                
                results.append(f"\n{i}. {title}")
                results.append(f"   Source: {source}")
                results.append(f"   Date: {date}")
                results.append(f"   URL: {url}")
        
        elif search_type == "images":
            image_results = data.get("images", [])
            for i, result in enumerate(image_results, 1):
                title = result.get("title", "No title")
                image_url = result.get("imageUrl", "No URL")
                source = result.get("source", "Unknown source")
                
                results.append(f"\n{i}. {title}")
                results.append(f"   Image URL: {image_url}")
                results.append(f"   Source: {source}")
        
        # Add metadata
        total_results = len(data.get("organic", []) + data.get("news", []) + data.get("images", []))
        results.append(f"\n\nTotal results returned: {total_results}")
        
        # Add related searches if available
        related = data.get("relatedSearches", [])
        if related:
            results.append("\nRelated searches:")
            for related_query in related[:5]:  # Limit to 5
                results.append(f"  - {related_query.get('query', '')}")
        
        return "\n".join(results)


class WebScrapingInput(BaseToolInput):
    """Input schema for WebScrapingTool."""
    url: str = Field(..., description="URL to scrape")
    extract_type: str = Field(
        default="text", 
        description="What to extract: text, links, images, or structured"
    )
    max_length: int = Field(
        default=5000, 
        description="Maximum length of extracted content"
    )
    
    @validator('extract_type')
    def validate_extract_type(cls, v):
        allowed_types = ['text', 'links', 'images', 'structured']
        if v not in allowed_types:
            raise ValueError(f'extract_type must be one of: {allowed_types}')
        return v
    
    @validator('url')
    def validate_url(cls, v):
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError('Invalid URL format')
        return v


class WebScrapingTool(EnhancedBaseTool):
    """
    Tool for scraping web page content with different extraction modes.
    """
    
    name: str = "Web Scraping Tool"
    description: str = (
        "Scrapes content from web pages with multiple extraction modes. "
        "Can extract plain text, links, images, or structured data. "
        "Includes safety limits and error handling. Use this when you need "
        "to extract specific information from web pages."
    )
    args_schema: type[BaseModel] = WebScrapingInput
    
    def _validate_input(self, **kwargs) -> None:
        """Validate scraping parameters."""
        url = kwargs.get("url")
        
        # Check for potentially dangerous URLs
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            raise ToolValidationError("Only HTTP and HTTPS URLs are allowed")
        
        # Block localhost and private IPs for security
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            raise ToolValidationError("Cannot scrape localhost URLs")
    
    def _execute(self, **kwargs) -> str:
        """Execute web scraping."""
        url = kwargs["url"]
        extract_type = kwargs.get("extract_type", "text")
        max_length = kwargs.get("max_length", 5000)
        
        try:
            # Set up session with headers
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (CrewAI Custom Tool) Web Scraper',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            })
            
            # Fetch the page
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract based on type
            if extract_type == "text":
                result = self._extract_text(soup, max_length)
            elif extract_type == "links":
                result = self._extract_links(soup, url)
            elif extract_type == "images":
                result = self._extract_images(soup, url)
            elif extract_type == "structured":
                result = self._extract_structured(soup, url)
            else:
                raise ToolValidationError(f"Unknown extract_type: {extract_type}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise ToolExecutionError(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            raise ToolExecutionError(f"Scraping failed: {str(e)}")
    
    def _extract_text(self, soup: BeautifulSoup, max_length: int) -> str:
        """Extract clean text content."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)
        
        # Truncate if necessary
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length] + "... (truncated)"
        
        return f"Extracted Text Content:\n\n{clean_text}"
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract all links from the page."""
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)
            
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            # Skip anchor links and javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            links.append({
                'url': full_url,
                'text': text or '(no text)',
                'title': a_tag.get('title', '')
            })
        
        # Format results
        result = ["Extracted Links:\n"]
        for i, link in enumerate(links[:50], 1):  # Limit to 50 links
            result.append(f"{i}. {link['text']}")
            result.append(f"   URL: {link['url']}")
            if link['title']:
                result.append(f"   Title: {link['title']}")
            result.append("")
        
        result.append(f"Total links found: {len(links)}")
        return "\n".join(result)
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract image information."""
        images = []
        
        for img_tag in soup.find_all('img', src=True):
            src = img_tag['src']
            alt = img_tag.get('alt', '')
            title = img_tag.get('title', '')
            
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, src)
            
            images.append({
                'url': full_url,
                'alt': alt,
                'title': title
            })
        
        # Format results
        result = ["Extracted Images:\n"]
        for i, img in enumerate(images[:30], 1):  # Limit to 30 images
            result.append(f"{i}. {img['alt'] or '(no alt text)'}")
            result.append(f"   URL: {img['url']}")
            if img['title']:
                result.append(f"   Title: {img['title']}")
            result.append("")
        
        result.append(f"Total images found: {len(images)}")
        return "\n".join(result)
    
    def _extract_structured(self, soup: BeautifulSoup, url: str) -> str:
        """Extract structured data overview."""
        result = [f"Structured Data from: {url}\n"]
        
        # Page title
        title_tag = soup.find('title')
        if title_tag:
            result.append(f"Title: {title_tag.get_text(strip=True)}")
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            result.append(f"Description: {meta_desc.get('content', '')}")
        
        # Headings structure
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                headings.append(f"H{level}: {heading.get_text(strip=True)}")
        
        if headings:
            result.append("\nHeadings Structure:")
            result.extend(headings[:20])  # Limit to 20 headings
        
        # Basic counts
        result.append(f"\nPage Statistics:")
        result.append(f"  Paragraphs: {len(soup.find_all('p'))}")
        result.append(f"  Links: {len(soup.find_all('a', href=True))}")
        result.append(f"  Images: {len(soup.find_all('img', src=True))}")
        result.append(f"  Lists: {len(soup.find_all(['ul', 'ol']))}")
        
        return "\n".join(result)