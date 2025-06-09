# LocalResearcher Crew

Welcome to the LocalResearcher Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

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
    cd local_researcher/
    uv venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    uv pip install -e .
    ```
    
    Alternatively, you can use the CrewAI CLI:
    ```bash
    crewai install
    ```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/local_researcher/config/agents.yaml` to define your agents
- Modify `src/local_researcher/config/tasks.yaml` to define your tasks
- Modify `src/local_researcher/crew.py` to add your own logic, tools and specific args
- Modify `src/local_researcher/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the local-researcher Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The local-researcher Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the LocalResearcher Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
