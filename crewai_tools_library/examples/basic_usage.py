"""
Basic usage examples for CrewAI Custom Tools Library.

This file demonstrates how to use individual tools for common tasks.
Run this file to see the tools in action with sample data.
"""

import os
import tempfile
from pathlib import Path

# Import the custom tools
from crewai_custom_tools import (
    FileReaderTool,
    FileWriterTool,
    DirectoryListTool,
    FileValidatorTool,
    EnhancedSearchTool,
    WebScrapingTool,
    TextAnalyzerTool,
    TextCleanerTool,
    TextSummarizerTool,
)


def demonstrate_file_tools():
    """Demonstrate file operation tools."""
    print("=== FILE TOOLS DEMONSTRATION ===\n")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 1. File Writer Tool
        print("1. FileWriterTool - Creating a sample file")
        writer = FileWriterTool()
        sample_file = temp_path / "sample.txt"
        
        sample_content = """
        This is a sample text file created by the FileWriterTool.
        It contains multiple lines and demonstrates the file writing capabilities.
        
        The tool includes safety features like overwrite protection and encoding support.
        """
        
        result = writer._run(
            file_path=str(sample_file),
            content=sample_content,
            overwrite=False
        )
        print(f"Result: {result}\n")
        
        # 2. File Reader Tool
        print("2. FileReaderTool - Reading the created file")
        reader = FileReaderTool()
        
        content = reader._run(
            file_path=str(sample_file),
            encoding="utf-8"
        )
        print(f"Read content:\n{content}\n")
        
        # 3. Create a JSON file for validation demo
        json_file = temp_path / "data.json"
        json_content = '{"name": "John", "age": 30, "city": "New York"}'
        
        writer._run(
            file_path=str(json_file),
            content=json_content,
            overwrite=True
        )
        
        # 4. File Validator Tool
        print("3. FileValidatorTool - Validating files")
        validator = FileValidatorTool()
        
        validation_result = validator._run(
            file_path=str(json_file),
            expected_type="json",
            check_content=True
        )
        print(f"Validation result:\n{validation_result}\n")
        
        # 5. Directory List Tool
        print("4. DirectoryListTool - Listing directory contents")
        lister = DirectoryListTool()
        
        directory_contents = lister._run(
            directory_path=str(temp_path),
            include_hidden=False,
            file_types=['.txt', '.json']
        )
        print(f"Directory contents:\n{directory_contents}\n")


def demonstrate_web_tools():
    """Demonstrate web-related tools."""
    print("=== WEB TOOLS DEMONSTRATION ===\n")
    
    # Check if SERPER_API_KEY is available
    if not os.getenv("SERPER_API_KEY"):
        print("SERPER_API_KEY not found. Skipping search tool demo.")
        print("Set SERPER_API_KEY in your environment to test search functionality.\n")
    else:
        # 1. Enhanced Search Tool
        print("1. EnhancedSearchTool - Web search")
        search_tool = EnhancedSearchTool()
        
        try:
            search_results = search_tool._run(
                query="CrewAI multi-agent systems Python",
                num_results=5,
                search_type="web"
            )
            print(f"Search results:\n{search_results}\n")
        except Exception as e:
            print(f"Search failed: {e}\n")
    
    # 2. Web Scraping Tool
    print("2. WebScrapingTool - Extracting content from a webpage")
    scraper = WebScrapingTool()
    
    try:
        # Use a simple, reliable website for demonstration
        scraped_content = scraper._run(
            url="https://httpbin.org/html",
            extract_type="text",
            max_length=1000
        )
        print(f"Scraped content:\n{scraped_content}\n")
    except Exception as e:
        print(f"Scraping failed: {e}\n")


def demonstrate_text_tools():
    """Demonstrate text processing tools."""
    print("=== TEXT TOOLS DEMONSTRATION ===\n")
    
    # Sample text for demonstration
    sample_text = """
    Artificial Intelligence (AI) and Machine Learning (ML) are revolutionizing various industries today. 
    These technologies enable computers to learn and make decisions without explicit programming for every scenario.
    
    CrewAI is a cutting-edge framework that facilitates the creation of collaborative AI agent teams. 
    It allows developers to build sophisticated multi-agent systems where different AI agents work together 
    to accomplish complex tasks. Each agent can have specialized roles, tools, and capabilities.
    
    The framework supports various AI models and provides a flexible architecture for agent collaboration. 
    This makes it possible to create powerful AI workflows that can handle research, analysis, content creation, 
    and many other cognitive tasks efficiently.
    
    With proper implementation, multi-agent systems can significantly improve productivity and quality 
    of output compared to single-agent approaches.
    """
    
    # 1. Text Analyzer Tool
    print("1. TextAnalyzerTool - Comprehensive text analysis")
    analyzer = TextAnalyzerTool()
    
    analysis_result = analyzer._run(
        text=sample_text,
        analysis_type="comprehensive"
    )
    print(f"Analysis result:\n{analysis_result}\n")
    
    # 2. Text Cleaner Tool
    print("2. TextCleanerTool - Cleaning and normalizing text")
    cleaner = TextCleanerTool()
    
    # Text with extra whitespace and HTML
    messy_text = """
    <p>This   is    some   messy    text   with    
    
    
    extra     whitespace   and   <b>HTML</b> tags.</p>
    
    It also contains URLs like https://example.com and email@test.com addresses.
    """
    
    cleaned_result = cleaner._run(
        text=messy_text,
        cleaning_options=["whitespace", "html", "urls", "emails"],
        preserve_structure=True
    )
    print(f"Cleaning result:\n{cleaned_result}\n")
    
    # 3. Text Summarizer Tool
    print("3. TextSummarizerTool - Creating text summaries")
    summarizer = TextSummarizerTool()
    
    summary_result = summarizer._run(
        text=sample_text,
        summary_type="extractive",
        max_sentences=3
    )
    print(f"Summary result:\n{summary_result}\n")
    
    # Also demonstrate key points extraction
    key_points_result = summarizer._run(
        text=sample_text,
        summary_type="key_points",
        max_sentences=4
    )
    print(f"Key points result:\n{key_points_result}\n")


def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("=== ERROR HANDLING DEMONSTRATION ===\n")
    
    # 1. File tool with invalid path
    print("1. Testing FileReaderTool with non-existent file")
    reader = FileReaderTool()
    
    try:
        reader._run(file_path="/non/existent/file.txt")
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}\n")
    
    # 2. Text analyzer with empty text
    print("2. Testing TextAnalyzerTool with empty text")
    analyzer = TextAnalyzerTool()
    
    try:
        analyzer._run(text="")
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}\n")
    
    # 3. Web scraper with invalid URL
    print("3. Testing WebScrapingTool with invalid URL")
    scraper = WebScrapingTool()
    
    try:
        scraper._run(url="not-a-valid-url")
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}\n")


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring features."""
    print("=== PERFORMANCE MONITORING DEMONSTRATION ===\n")
    
    # Create a tool and run it multiple times
    analyzer = TextAnalyzerTool()
    
    sample_texts = [
        "Short text for analysis.",
        "This is a medium-length text that contains several sentences and provides more content for analysis.",
        "This is a longer text sample that includes multiple paragraphs and various types of content. " * 10
    ]
    
    print("Running text analysis multiple times...")
    for i, text in enumerate(sample_texts, 1):
        print(f"Analysis {i}...")
        analyzer._run(text=text, analysis_type="basic")
    
    # Get performance metrics
    metrics = analyzer.get_metrics()
    print(f"\nPerformance Metrics:")
    print(f"  Total executions: {metrics['execution_count']}")
    print(f"  Total execution time: {metrics['total_execution_time']:.3f}s")
    print(f"  Average execution time: {metrics['average_execution_time']:.3f}s")
    print(f"  Cache entries: {metrics['cache_entries']}")


def main():
    """Run all demonstrations."""
    print("CrewAI Custom Tools Library - Basic Usage Examples")
    print("=" * 60)
    print()
    
    try:
        demonstrate_file_tools()
        demonstrate_web_tools()
        demonstrate_text_tools()
        demonstrate_error_handling()
        demonstrate_performance_monitoring()
        
        print("=" * 60)
        print("All demonstrations completed successfully!")
        print("\nNext steps:")
        print("1. Check out crew_integration_example.py for CrewAI integration")
        print("2. Explore the advanced_usage.py for more complex scenarios")
        print("3. Review the tool documentation in the source code")
        
    except Exception as e:
        print(f"Demonstration failed: {e}")
        print("Please check your environment setup and dependencies.")


if __name__ == "__main__":
    main()