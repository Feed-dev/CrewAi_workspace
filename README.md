Last Updated: 2026-01-15

A comprehensive workspace containing multiple CrewAI-powered multi-agent AI projects demonstrating different use cases for collaborative AI workflows.

## Projects

- **CoWrite** - Sophisticated collaborative writing assistant with 5 specialized agents
- **BasicResearcher** - Simple 2-agent research template  
- **LocalResearcher** - Local-focused variant of BasicResearcher
- **crewai_tools_library** - Custom tools library for CrewAI projects

## Environment Setup

This workspace uses a hierarchical conda + UV environment setup:
- **Conda environment** - Workspace-level Python environment
- **UV environments** - Individual project-level virtual environments

### Prerequisites
- Conda (Miniconda or Anaconda)

### Initial Setup

1. **Create & Activate Conda Environment:**
   ```bash
   conda create -n crewai-workspace python=3.11 -y
   conda activate crewai-workspace
   pip install uv
   ```

2. **Navigate to Specific Project:**
   ```bash
   cd CoWrite/  # or basic_researcher/ or local_researcher/
   ```

3. **Create Project Environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

## Quick Start

After environment setup, you can run projects using:

```bash
# For CoWrite
conda activate crewai-workspace
cd CoWrite/
source .venv/bin/activate
python -m src.writer_crew.main

# For BasicResearcher/LocalResearcher  
conda activate crewai-workspace
cd basic_researcher/  # or local_researcher/
source .venv/bin/activate
crewai run
```

## Documentation

See individual project README files for detailed setup and usage instructions:
- [CoWrite README](./CoWrite/README.md)
- [BasicResearcher README](./basic_researcher/README.md)
- [LocalResearcher README](./local_researcher/README.md)

For development guidance, see [CLAUDE.md](./CLAUDE.md).

Last Updated: 2025-06-09