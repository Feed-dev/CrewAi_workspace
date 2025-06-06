---
title: CLI
description: Learn how to use the CrewAI CLI to interact with CrewAI.
icon: terminal
---

# CrewAI CLI Documentation

The CrewAI CLI provides a set of commands to interact with CrewAI, allowing you to create, train, run, and manage crews & flows.

## Installation

To use the CrewAI CLI, make sure you have CrewAI installed:

```shell Terminal
pip install crewai
```

## Basic Usage

The basic structure of a CrewAI CLI command is:

```shell Terminal
crewai [COMMAND] [OPTIONS] [ARGUMENTS]
```

## Available Commands

### 1. Create

Create a new crew or flow.

```shell Terminal
crewai create [OPTIONS] TYPE NAME
```

- `TYPE`: Choose between "crew" or "flow"
- `NAME`: Name of the crew or flow

Example:
```shell Terminal
crewai create crew my_new_crew
crewai create flow my_new_flow
```

### 2. Version

Show the installed version of CrewAI.

```shell Terminal
crewai version [OPTIONS]
```

- `--tools`: (Optional) Show the installed version of CrewAI tools

Example:
```shell Terminal
crewai version
crewai version --tools
```

### 3. Train

Train the crew for a specified number of iterations.

```shell Terminal
crewai train [OPTIONS]
```

- `-n, --n_iterations INTEGER`: Number of iterations to train the crew (default: 5)
- `-f, --filename TEXT`: Path to a custom file for training (default: "trained_agents_data.pkl")

Example:
```shell Terminal
crewai train -n 10 -f my_training_data.pkl
```

### 4. Replay

Replay the crew execution from a specific task.

```shell Terminal
crewai replay [OPTIONS]
```

- `-t, --task_id TEXT`: Replay the crew from this task ID, including all subsequent tasks

Example:
```shell Terminal    
crewai replay -t task_123456
```

### 5. Log-tasks-outputs

Retrieve your latest crew.kickoff() task outputs.

```shell Terminal
crewai log-tasks-outputs
```

### 6. Reset-memories

Reset the crew memories (long, short, entity, latest_crew_kickoff_outputs).

```shell Terminal
crewai reset-memories [OPTIONS]
```

- `-l, --long`: Reset LONG TERM memory
- `-s, --short`: Reset SHORT TERM memory
- `-e, --entities`: Reset ENTITIES memory
- `-k, --kickoff-outputs`: Reset LATEST KICKOFF TASK OUTPUTS
- `-a, --all`: Reset ALL memories

Example:
```shell Terminal
crewai reset-memories --long --short
crewai reset-memories --all
```

### 7. Test

Test the crew and evaluate the results.

```shell Terminal
crewai test [OPTIONS]
```

- `-n, --n_iterations INTEGER`: Number of iterations to test the crew (default: 3)
- `-m, --model TEXT`: LLM Model to run the tests on the Crew (default: "gpt-4o-mini")

Example:
```shell Terminal    
crewai test -n 5 -m gpt-3.5-turbo
```

### 8. Run

Run the crew or flow.

```shell Terminal
crewai run
```

<Note>
Starting from version 0.103.0, the `crewai run` command can be used to run both standard crews and flows. For flows, it automatically detects the type from pyproject.toml and runs the appropriate command. This is now the recommended way to run both crews and flows.
</Note>

<Note>
Make sure to run these commands from the directory where your CrewAI project is set up. 
Some commands may require additional configuration or setup within your project structure.
</Note>

### 9. Chat

Starting in version `0.98.0`, when you run the `crewai chat` command, you start an interactive session with your crew. The AI assistant will guide you by asking for necessary inputs to execute the crew. Once all inputs are provided, the crew will execute its tasks.

After receiving the results, you can continue interacting with the assistant for further instructions or questions.

```shell Terminal
crewai chat
```
<Note>
Ensure you execute these commands from your CrewAI project's root directory.
</Note>
<Note>
IMPORTANT: Set the `chat_llm` property in your `crew.py` file to enable this command.

```python
@crew
def crew(self) -> Crew:
    return Crew(
        agents=self.agents,
        tasks=self.tasks,
        process=Process.sequential,
        verbose=True,
        chat_llm="gpt-4o",  # LLM for chat orchestration
    )
```
</Note>

### 10. API Keys

When running ```crewai create crew``` command, the CLI will first show you the top 5 most common LLM providers and ask you to select one.

Once you've selected an LLM provider, you will be prompted for API keys.

#### Initial API key providers

The CLI will initially prompt for API keys for the following services:

* OpenAI
* Groq
* Anthropic
* Google Gemini
* SambaNova

When you select a provider, the CLI will prompt you to enter your API key.

#### Other Options

If you select option 6, you will be able to select from a list of LiteLLM supported providers.

When you select a provider, the CLI will prompt you to enter the Key name and the API key.

See the following link for each provider's key name:

* [LiteLLM Providers](https://docs.litellm.ai/docs/providers)


