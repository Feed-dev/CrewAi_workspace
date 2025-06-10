# Cataloger Crew

An autonomous AI crew that searches the web over extended periods and creates a comprehensive library-style catalog of information with metadata and tags.

## Features

- **Autonomous Web Searching**: Continuously searches for specified content types
- **Intelligent Analysis**: Extracts metadata, tags, and categorizes content
- **Library Cataloging**: Maintains organized catalog with proper metadata
- **Extended Operation**: Designed for long-running autonomous operation
- **Duplicate Detection**: Prevents redundant catalog entries
- **Flexible Storage**: Supports JSON and CSV export formats

## Architecture

### 3-Agent Workflow

1. **Search Agent**: Performs web searches with intelligent query evolution
2. **Analysis Agent**: Extracts metadata, tags, and categorizes content
3. **Cataloger Agent**: Maintains the organized library catalog

### Key Components

- **Search Tools**: Enhanced web search with multiple search types
- **Analysis Tools**: Metadata extraction and content analysis
- **Catalog Tools**: Persistent storage and organization
- **Scheduling**: Configurable search intervals for autonomous operation

## Setup

### 1. Ollama Setup (Required)
First, install and set up Ollama with your preferred models:

```bash
# Install Ollama (see https://ollama.ai for installation instructions)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models
ollama pull llama3.1:8b
# Or for better performance with more VRAM:
# ollama pull llama3.1:70b
# ollama pull qwen2.5:14b
```

### 2. Project Setup
```bash
cd cataloger_crew
uv venv
source .venv/bin/activate  # macOS/Linux or .venv\Scripts\activate on Windows
uv pip install -e .
```

### 3. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
SERPER_API_KEY="your_serper_api_key"  # Get from https://serper.dev
OLLAMA_BASE_URL="http://localhost:11434"  # Default Ollama URL
```

### 4. Model Configuration
Edit `ollama_config.yaml` to specify your Ollama models:

```yaml
models:
  search_model: "llama3.1:8b"      # For search query generation
  analysis_model: "llama3.1:8b"   # For content analysis  
  cataloger_model: "llama3.1:8b"  # For catalog management
```

## Usage

### Single Session Mode
```bash
# Run one cataloging session
python -m src.cataloger_crew.main single
```

### Autonomous Mode
```bash
# Run continuous autonomous cataloging
python -m src.cataloger_crew.main autonomous
```

### Configuration Options

Edit `src/cataloger_crew/main.py` to configure:
- **Topic**: Main subject area to catalog
- **Search Terms**: Initial search keywords
- **Search Rounds**: Number of search iterations per session
- **Duration**: How long to run in autonomous mode
- **Models**: Which Ollama models to use for each agent

## Catalog Structure

The catalog maintains:
- **Title**: Primary identifier
- **URL**: Source location
- **Type**: Content classification
- **Tags**: Relevant keywords
- **Summary**: Brief description
- **Metadata**: Creation date, source, relevance score
- **Category**: Hierarchical organization

## Output Formats

- **JSON**: Full catalog with all metadata
- **CSV**: Tabular format for analysis
- **Markdown**: Human-readable catalog listing