"""
Example of integrating CrewAI Custom Tools with a complete CrewAI workflow.

This example demonstrates how to create a research and analysis crew that uses
multiple custom tools to gather information, process it, and generate insights.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

# Import custom tools
from crewai_custom_tools import (
    EnhancedSearchTool,
    FileReaderTool,
    FileWriterTool,
    TextAnalyzerTool,
    TextSummarizerTool,
    WebScrapingTool,
)

# Load environment variables
load_dotenv()


@CrewBase
class ResearchAnalysisCrew:
    """
    A CrewAI crew that demonstrates integration with custom tools.
    
    This crew performs research, analysis, and reporting using the custom tools library.
    """
    
    # Define agents with specific tool assignments
    @agent
    def researcher(self) -> Agent:
        """Research agent with web search and scraping capabilities."""
        return Agent(
            role="Senior Research Specialist",
            goal="Gather comprehensive and accurate information on assigned topics using web search and content extraction",
            backstory=(
                "You are an expert researcher with advanced skills in finding, evaluating, and extracting "
                "relevant information from web sources. You use sophisticated search strategies and can "
                "analyze web content to identify the most valuable insights."
            ),
            tools=[
                EnhancedSearchTool(),
                WebScrapingTool(),
                FileReaderTool(),
            ],
            verbose=True,
            allow_delegation=False,
        )
    
    @agent
    def analyst(self) -> Agent:
        """Analysis agent with text processing capabilities."""
        return Agent(
            role="Content Analysis Expert",
            goal="Analyze research findings and extract key insights, patterns, and summaries",
            backstory=(
                "You are a skilled analyst who specializes in processing large amounts of text data "
                "to identify patterns, themes, and key insights. You excel at creating clear, "
                "actionable summaries from complex information."
            ),
            tools=[
                TextAnalyzerTool(),
                TextSummarizerTool(),
                FileReaderTool(),
            ],
            verbose=True,
            allow_delegation=False,
        )
    
    @agent
    def reporter(self) -> Agent:
        """Reporting agent with file output capabilities."""
        return Agent(
            role="Research Report Writer",
            goal="Compile research and analysis into comprehensive, well-structured reports",
            backstory=(
                "You are an experienced technical writer who creates clear, comprehensive reports "
                "from research findings and analytical insights. You excel at organizing complex "
                "information into accessible, actionable documents."
            ),
            tools=[
                FileWriterTool(),
                TextAnalyzerTool(),
            ],
            verbose=True,
            allow_delegation=False,
        )
    
    # Define tasks that utilize the tools
    @task
    def research_task(self) -> Task:
        """Task for gathering research information."""
        return Task(
            description=(
                "Research the topic: {topic}\n\n"
                "Your research should include:\n"
                "1. Use the Enhanced Search Tool to find recent, relevant information\n"
                "2. If any reference documents are provided in {reference_files}, read and analyze them\n"
                "3. Use web scraping when appropriate to extract detailed content from key sources\n"
                "4. Focus on finding authoritative, up-to-date information\n"
                "5. Gather diverse perspectives and comprehensive coverage of the topic\n\n"
                "Organize your findings logically and cite your sources."
            ),
            expected_output=(
                "A comprehensive research report in markdown format containing:\n"
                "- Executive summary of key findings\n"
                "- Detailed information organized by subtopic\n"
                "- Source citations and credibility assessment\n"
                "- Identification of key trends, challenges, and opportunities\n"
                "- Recommendations for further investigation if needed"
            ),
            agent=self.researcher(),
        )
    
    @task
    def analysis_task(self) -> Task:
        """Task for analyzing research findings."""
        return Task(
            description=(
                "Analyze the research findings from the previous task.\n\n"
                "Your analysis should include:\n"
                "1. Use the Text Analyzer Tool to get comprehensive statistics and insights\n"
                "2. Use the Text Summarizer Tool to create executive summaries\n"
                "3. Identify key themes, patterns, and insights from the research\n"
                "4. Assess the quality and comprehensiveness of the information\n"
                "5. Highlight the most important findings and their implications\n\n"
                "Focus on extracting actionable insights and identifying areas that need attention."
            ),
            expected_output=(
                "A detailed analysis report containing:\n"
                "- Statistical analysis of the research content (word count, readability, etc.)\n"
                "- Executive summary of key findings\n"
                "- Thematic analysis with identified patterns and trends\n"
                "- Quality assessment of the research\n"
                "- Strategic insights and implications\n"
                "- Prioritized recommendations based on the findings"
            ),
            agent=self.analyst(),
            context=[self.research_task()],
        )
    
    @task
    def reporting_task(self) -> Task:
        """Task for creating the final report."""
        return Task(
            description=(
                "Create a comprehensive final report combining research and analysis.\n\n"
                "Your report should:\n"
                "1. Synthesize information from both research and analysis tasks\n"
                "2. Use the Text Analyzer Tool to ensure report quality and readability\n"
                "3. Create a well-structured, professional document\n"
                "4. Use the File Writer Tool to save the report to: {output_file}\n"
                "5. Ensure the report is actionable and addresses the original research objectives\n\n"
                "The final report should be suitable for executive review and decision-making."
            ),
            expected_output=(
                "A final comprehensive report saved to the specified file containing:\n"
                "- Executive summary\n"
                "- Research methodology and sources\n"
                "- Key findings and insights\n"
                "- Analysis and implications\n"
                "- Recommendations and next steps\n"
                "- Appendices with detailed data and sources\n\n"
                "The report file should be successfully saved and a confirmation message provided."
            ),
            agent=self.reporter(),
            context=[self.research_task(), self.analysis_task()],
            output_file="research_report.md",
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the research analysis crew."""
        return Crew(
            agents=[self.researcher(), self.analyst(), self.reporter()],
            tasks=[self.research_task(), self.analysis_task(), self.reporting_task()],
            process=Process.sequential,
            verbose=True,
        )


def run_research_crew_example():
    """
    Run the research crew with sample inputs.
    """
    print("=== CrewAI Custom Tools Integration Example ===\n")
    
    # Example inputs for the crew
    inputs = {
        "topic": "Multi-agent AI systems and their applications in business automation",
        "reference_files": [],  # No reference files for this example
        "output_file": "business_ai_research_report.md",
    }
    
    print(f"Starting research on topic: {inputs['topic']}")
    print(f"Output will be saved to: {inputs['output_file']}")
    print("-" * 60)
    
    try:
        # Create and run the crew
        crew = ResearchAnalysisCrew()
        result = crew.crew().kickoff(inputs=inputs)
        
        print("-" * 60)
        print("✅ Research crew completed successfully!")
        print(f"📄 Report saved to: {inputs['output_file']}")
        print("\nFinal result:")
        print(result)
        
    except Exception as e:
        print(f"❌ Error running research crew: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure SERPER_API_KEY is set in your environment")
        print("2. Check that all dependencies are installed")
        print("3. Verify internet connectivity for web tools")


def demonstrate_tool_performance():
    """
    Demonstrate the performance monitoring capabilities of the tools.
    """
    print("\n=== Tool Performance Monitoring ===\n")
    
    # Create tools and run some operations
    search_tool = EnhancedSearchTool()
    analyzer_tool = TextAnalyzerTool()
    
    # Simulate some tool usage
    sample_text = (
        "This is a sample text for performance testing. " * 20 +
        "It contains enough content to provide meaningful analysis metrics."
    )
    
    print("Running performance tests...")
    
    # Run text analysis multiple times
    for i in range(3):
        analyzer_tool._run(text=sample_text, analysis_type="basic")
    
    # Get and display metrics
    analyzer_metrics = analyzer_tool.get_metrics()
    print("Text Analyzer Tool Metrics:")
    for metric, value in analyzer_metrics.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.3f}")
        else:
            print(f"  {metric}: {value}")
    
    # Demonstrate cache functionality
    print(f"\nCache demonstration:")
    print(f"  Current cache entries: {analyzer_tool.get_metrics()['cache_entries']}")
    
    # Run the same analysis again (should use cache)
    analyzer_tool._run(text=sample_text, analysis_type="basic")
    print(f"  Cache entries after repeat: {analyzer_tool.get_metrics()['cache_entries']}")
    
    # Clear cache
    analyzer_tool.clear_cache()
    print(f"  Cache entries after clear: {analyzer_tool.get_metrics()['cache_entries']}")


def main():
    """
    Main function to run the complete integration example.
    """
    print("CrewAI Custom Tools - Integration Example")
    print("=" * 50)
    
    # Check environment setup
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("   The crew may not function properly without it.")
    
    if not os.getenv("SERPER_API_KEY"):
        print("⚠️  Warning: SERPER_API_KEY not found in environment")
        print("   Web search functionality will be limited.")
    
    print()
    
    try:
        # Run the main example
        run_research_crew_example()
        
        # Demonstrate performance monitoring
        demonstrate_tool_performance()
        
        print("\n" + "=" * 50)
        print("✅ Integration example completed!")
        print("\nWhat happened:")
        print("1. 🔍 Researcher agent used EnhancedSearchTool and WebScrapingTool")
        print("2. 📊 Analyst agent used TextAnalyzerTool and TextSummarizerTool")
        print("3. 📝 Reporter agent used FileWriterTool to save the final report")
        print("4. 📈 Performance metrics were collected and displayed")
        
        print("\nNext steps:")
        print("• Check the generated report file for results")
        print("• Try modifying the inputs to research different topics")
        print("• Experiment with different tool configurations")
        print("• Integrate these patterns into your own CrewAI projects")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("\nPlease check:")
        print("• Environment variables (OPENAI_API_KEY, SERPER_API_KEY)")
        print("• Internet connectivity")
        print("• Dependencies installation (uv pip install -e .)")


if __name__ == "__main__":
    main()