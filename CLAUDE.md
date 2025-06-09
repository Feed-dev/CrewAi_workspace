# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CrewAI workspace containing three multi-agent AI projects that demonstrate different use cases for collaborative AI workflows:

- **CoWrite** - Sophisticated collaborative writing assistant with 5 specialized agents
- **BasicResearcher** - Simple 2-agent research template
- **LocalResearcher** - Local-focused variant of BasicResearcher

## Environment Setup

### Conda Environment (Workspace Level)
First, ensure you have the main conda environment activated:
```bash
# Activate the workspace conda environment
conda activate crewai-workspace

# If not created yet, create it:
conda create -n crewai-workspace python=3.11 -y
conda activate crewai-workspace
pip install uv
```

### Project Setup (Individual Projects)
```bash
# Navigate to specific project directory first
cd CoWrite/  # or basic_researcher/ or local_researcher/

# Create UV virtual environment (within conda environment)
uv venv
uv pip install -e .

# Activate UV virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Running Projects
```bash
# CoWrite (from CoWrite/ directory)
python -m src.writer_crew.main

# BasicResearcher/LocalResearcher (from project directory)
crewai run
# or
python -m src.basic_researcher.main
```

### CrewAI CLI Commands
```bash
crewai create crew <name>    # Create new crew
crewai run                   # Run current crew
crewai train -n 10          # Train crew for 10 iterations
crewai test -n 5            # Test crew for 5 iterations
crewai chat                 # Interactive crew session
crewai reset-memories --all # Reset all memories
```

## Architecture

### Project Structure Pattern
All projects follow this consistent structure:
```
project/
├── src/project_name/
│   ├── config/
│   │   ├── agents.yaml     # Agent definitions with roles, goals, backstories
│   │   └── tasks.yaml      # Task configurations with dependencies
│   ├── crew.py            # CrewBase class with @agent, @task, @crew decorators
│   ├── main.py            # Entry point with hardcoded inputs
│   └── tools/             # Custom tool implementations
├── knowledge/             # Knowledge base files (user_preference.txt)
├── pyproject.toml        # Project config with crewai[tools] dependency
└── uv.lock              # UV dependency lock file
```

### Agent-Task Architecture
- **Agents**: Defined in `agents.yaml` with role, goal, backstory, LLM model
- **Tasks**: Defined in `tasks.yaml` with description, expected_output, agent assignment
- **Context Flow**: Task outputs automatically become context for subsequent tasks
- **Sequential Processing**: Tasks execute in order defined in crew.py

### CoWrite Workflow
Two-stage process with 5 agents:
1. **Research Stage**: Researcher → Outliner
2. **Writing Stage**: Writer → Editor → Fact-Checker

### Tool Integration
- **SerperDevTool**: Web search capabilities (requires SERPER_API_KEY)
- **FileReadTool**: Custom file reading functionality
- **Custom Tools**: Project-specific extensions in tools/ directory

## API Keys Configuration

### Required API Keys
Create `.env` file in project root:
```
OPENAI_API_KEY="sk-your_openai_api_key"
SERPER_API_KEY="your_serper_api_key"
```

### Model Configuration
- Default models: gpt-4o, gpt-4o-mini
- Configured per agent in agents.yaml
- Can be overridden via CLI flags in test/train commands

## Key Files and Configuration

### agents.yaml Format
```yaml
agent_name:
  role: "Job title/function"
  goal: "Specific objective"
  backstory: "Context and expertise"
  llm: "gpt-4o"
  verbose: true
  allow_delegation: false
```

### tasks.yaml Format
```yaml
task_name:
  description: "Detailed instructions with {input_placeholders}"
  expected_output: "Specific format requirements"
  agent: agent_name
  context: [dependent_task_names]  # Optional
```

### crew.py Pattern
Uses CrewAI decorators:
- `@CrewBase` - Base crew class
- `@agent` - Agent definition methods
- `@task` - Task definition methods  
- `@crew` - Main crew assembly

## Input Configuration

Inputs are currently hardcoded in `main.py` files. Common input parameters:
- `topic`: Main subject for research/writing
- `audience`: Target audience description
- `requirements`: Specific output requirements
- `context`: Additional context or constraints

To modify inputs, edit the respective `main.py` file's input dictionary.

## Memory and Persistence

CrewAI maintains several types of memory:
- Long-term memory (across sessions)
- Short-term memory (within session)
- Entity memory (people, places, concepts)
- Latest kickoff outputs

Use `crewai reset-memories` commands to clear when needed.