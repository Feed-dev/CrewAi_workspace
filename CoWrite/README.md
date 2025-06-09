# CoWrite - Collaborative AI Writing Assistant

Welcome to the CoWrite project, powered by [CrewAI](https://crewai.com). CoWrite leverages a specialized crew of AI agents to collaboratively create cohesive, long-form content (e.g., articles, reports, blog posts). It addresses the challenge of maintaining structure and logical flow in longer documents by simulating a professional writing workflow with distinct agent roles.

## Project Goal

The primary goal of CoWrite is to automate the generation of well-structured, researched, and refined long-form content using a multi-agent system. Agents include:

1.  **Researcher:** Gathers comprehensive information on the topic using web search and file reading.
2.  **Outliner:** Creates a logical, hierarchical outline based on research and user requirements.
3.  **Writer:** Drafts the content section-by-section, adhering to the outline and incorporating research.
4.  **Editor:** Refines the draft for clarity, coherence, grammar, style, and tone.
5.  **Fact-Checker:** Verifies factual claims in the edited content against research and web sources.

## Installation

This project uses a conda + UV environment setup for optimal dependency management.

### Prerequisites
- Conda (Miniconda or Anaconda)
- The workspace conda environment should be set up first

### Setup Instructions

1.  **Activate Workspace Environment:**
    ```bash
    conda activate crewai-workspace
    ```
    
    If the conda environment doesn't exist, create it first:
    ```bash
    conda create -n crewai-workspace python=3.11 -y
    conda activate crewai-workspace
    pip install uv
    ```

2.  **Navigate to Project & Create UV Environment:**
    ```bash
    cd CoWrite/
    uv venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    uv pip install -e .
    ```

3.  **Set Up Environment Variables:**
    Create a file named `.env` in the project root directory (`CoWrite/`) and add your API keys:
    ```dotenv
    OPENAI_API_KEY="sk-your_openai_api_key"
    SERPER_API_KEY="your_serper_api_key"
    ```
    *   Get an OpenAI API key from [OpenAI](https://platform.openai.com/api-keys).
    *   Get a Serper API key from [Serper.dev](https://serper.dev).

## Running the Project

1.  **Activate Virtual Environment:**
    *   **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```
    You should see `(.venv)` at the beginning of your terminal prompt.

2.  **Run the Crew:**
    Execute the main script from the project root directory (`CoWrite/`):
    ```bash
    python -m src.writer_crew.main
    ```

    The script will initialize the crew and execute the sequential writing process (Research -> Outline -> Draft -> Edit -> Fact-Check). Progress and task outputs will be logged to the console.

    *(Note: The inputs like topic, audience, etc., are currently hardcoded in `src/writer_crew/main.py`. You can modify them there for different writing tasks.)*

## Project Structure

*   `src/writer_crew/`: Main source code for the CrewAI project.
    *   `config/`: Contains `agents.yaml` and `tasks.yaml` definitions.
    *   `tools/`: Custom tool implementations (e.g., `file_tools.py`).
    *   `crew.py`: Defines the Crew structure, agent/task instantiation, and workflow process.
    *   `main.py`: Entry point script to configure inputs and run the crew.
*   `tests/`: Contains unit tests (currently pending implementation).
*   `INSTRUCTIONS/`: Contains project planning documents (`MASTERPLAN.md`, `ROADMAP.md`, `TASKS-TO-DO.md`).
*   `knowledge/`: Directory for potential knowledge base files.
*   `.env`: Environment variables (API Keys - **You need to create this file**).
*   `pyproject.toml`: Project metadata and dependencies.
*   `uv.lock`: Locked dependency versions managed by UV.
*   `README.md`: This file.

## Current Status

*   The core multi-agent workflow (Research, Outline, Draft, Edit, Fact-Check) is implemented.
*   Agents and Tasks are configured via YAML.
*   Uses `SerperDevTool` for web search and a custom `FileReadTool`.
*   **Pending:**
    *   Implementation of unit tests in the `tests/` directory.
    *   Refinement of the final output handling in `main.py` (currently logs fact-check report; needs to output final article content, e.g., save to a file).
    *   Potential implementation of loading inputs from configuration files or command-line arguments instead of hardcoding in `main.py`.

## Support

For support specific to CrewAI:
*   Visit the [CrewAI documentation](https://docs.crewai.com)
*   Check the [CrewAI GitHub repository](https://github.com/joaomdmoura/crewai)
*   Join the [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)
