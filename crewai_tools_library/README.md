# CrewAI Custom Tools Library

A comprehensive library of custom tools for CrewAI workflows, designed following CrewAI best practices for seamless multi-agent integration.

## Overview

This library provides a collection of high-quality, production-ready tools that extend CrewAI agents' capabilities across multiple domains:

- **Data Tools**: File operations, validation, and directory management
- **Web Tools**: Enhanced search, web scraping, and content extraction
- **Content Tools**: Text analysis, cleaning, and summarization
- **Analysis Tools**: (Coming soon) Sentiment analysis, classification
- **Media Tools**: (Coming soon) Image and video processing

## Key Features

✨ **CrewAI Best Practices**: All tools follow official CrewAI patterns and conventions  
🛡️ **Enhanced Error Handling**: Comprehensive validation and graceful error recovery  
📊 **Performance Monitoring**: Built-in metrics and caching capabilities  
🔧 **Flexible Configuration**: Extensive customization options for different use cases  
📖 **Rich Documentation**: Detailed examples and usage patterns  
🧪 **Thoroughly Tested**: Comprehensive test suite for reliability  

## Installation

### As a Library in Your CrewAI Workspace

1. Navigate to the library directory:
```bash
cd crewai_tools_library/
```

2. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # macOS/Linux
# or .venv\Scripts\activate  # Windows
```

3. Install the library in development mode:
```bash
uv pip install -e .
```

### Using Tools in Your CrewAI Projects

Import and use tools in your crew projects:

```python
from crewai_custom_tools import FileReaderTool, EnhancedSearchTool, TextAnalyzerTool

# In your crew.py file
@agent
def researcher(self) -> Agent:
    return Agent(
        config=self.agents_config['researcher'],
        tools=[EnhancedSearchTool(), FileReaderTool()],
        verbose=True
    )
```

## Quick Start

### Basic File Operations

```python
from crewai_custom_tools import FileReaderTool, FileWriterTool

# Read a file
file_reader = FileReaderTool()
content = file_reader._run(file_path="./document.txt")

# Write content to a file
file_writer = FileWriterTool()
result = file_writer._run(
    file_path="./output.txt",
    content="Generated content",
    overwrite=True
)
```

### Enhanced Web Search

```python
from crewai_custom_tools import EnhancedSearchTool

search_tool = EnhancedSearchTool()
results = search_tool._run(
    query="CrewAI multi-agent systems",
    num_results=10,
    search_type="web"
)
```

### Text Analysis

```python
from crewai_custom_tools import TextAnalyzerTool, TextCleanerTool

# Analyze text
analyzer = TextAnalyzerTool()
analysis = analyzer._run(
    text="Your text content here...",
    analysis_type="comprehensive"
)

# Clean text
cleaner = TextCleanerTool()
cleaned = cleaner._run(
    text="Messy    text   with    extra spaces!",
    cleaning_options=["whitespace", "punctuation"]
)
```

## Available Tools

### Data Tools (`crewai_custom_tools.data`)

| Tool | Description | Key Features |
|------|-------------|--------------|
| `FileReaderTool` | Read various file types safely | JSON, CSV, text support; size limits; encoding detection |
| `FileWriterTool` | Write content to files with safety checks | Overwrite protection; encoding options; error handling |
| `DirectoryListTool` | List directory contents with filtering | File type filtering; hidden file options; detailed info |
| `FileValidatorTool` | Validate file existence and content | Type checking; content validation; structure verification |

### Web Tools (`crewai_custom_tools.web`)

| Tool | Description | Key Features |
|------|-------------|--------------|
| `EnhancedSearchTool` | Advanced web search with rich formatting | Multiple search types; result metadata; caching |
| `WebScrapingTool` | Extract content from web pages | Multiple extraction modes; safety limits; clean output |

### Content Tools (`crewai_custom_tools.content`)

| Tool | Description | Key Features |
|------|-------------|--------------|
| `TextAnalyzerTool` | Comprehensive text analysis | Statistics; readability; keyword frequency; complexity |
| `TextCleanerTool` | Clean and normalize text content | Configurable options; structure preservation; HTML removal |
| `TextSummarizerTool` | Create extractive text summaries | Sentence scoring; key point extraction; compression metrics |

## Advanced Usage

### Custom Error Handling

All tools inherit from `EnhancedBaseTool` which provides consistent error handling:

```python
from crewai_custom_tools.base import ToolValidationError, ToolExecutionError

try:
    result = tool._run(**params)
except ToolValidationError as e:
    print(f"Input validation failed: {e}")
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
```

### Performance Monitoring

Tools include built-in performance metrics:

```python
tool = TextAnalyzerTool()
result = tool._run(text="Sample text")

# Get performance metrics
metrics = tool.get_metrics()
print(f"Executions: {metrics['execution_count']}")
print(f"Average time: {metrics['average_execution_time']:.2f}s")
```

### Caching Configuration

Configure caching behavior for better performance:

```python
tool = EnhancedSearchTool()

# Set cache TTL to 1 hour
tool.set_cache_ttl(60)

# Clear cache when needed
tool.clear_cache()
```

## Integration with CrewAI Projects

### Agent Configuration Example

```python
# In your crew.py file
from crewai_custom_tools import FileReaderTool, EnhancedSearchTool

@CrewBase
class MyResearchCrew:
    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[
                EnhancedSearchTool(),
                FileReaderTool(),
            ],
            verbose=True
        )
    
    @agent  
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'],
            tools=[
                TextAnalyzerTool(),
                TextSummarizerTool(),
            ],
            verbose=True
        )
```

### Task Configuration Example

```yaml
# In your tasks.yaml
research_task:
  description: >
    Research the topic: {topic}
    Use the Enhanced Search Tool to find recent information.
    Use the File Reader Tool to analyze any provided documents.
  expected_output: >
    A comprehensive research report with sources and analysis.
  agent: researcher

analysis_task:
  description: >
    Analyze the research findings using text analysis tools.
    Create a summary of key points and assess content quality.
  expected_output: >
    An analytical summary with text metrics and insights.
  agent: analyst
  context:
    - research_task
```

## Environment Setup

### Required Environment Variables

For web tools, set up your API keys:

```bash
# .env file
SERPER_API_KEY="your_serper_api_key_here"
```

### Optional Dependencies

Install additional features as needed:

```bash
# For advanced analysis tools
uv pip install "crewai-custom-tools[analysis]"

# For document processing
uv pip install "crewai-custom-tools[documents]"

# For media processing
uv pip install "crewai-custom-tools[media]"

# For development
uv pip install "crewai-custom-tools[dev]"
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Contributing

1. Follow CrewAI tool patterns and conventions
2. Include comprehensive tests for new tools
3. Document all tool parameters and expected outputs
4. Add usage examples to the documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the [examples/](examples/) directory for usage patterns
- Review tool docstrings for detailed parameter information
- Refer to CrewAI documentation for integration guidance

---

**Built for the CrewAI community** 🤖✨