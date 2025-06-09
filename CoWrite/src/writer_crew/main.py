#!/usr/bin/env python
import sys
import warnings
import os
from dotenv import load_dotenv
from datetime import datetime
from crewai import Crew, Process
from .crew import WriterCrew

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Placeholder for simple console logging callback
def simple_task_callback(task_output):
    """Callback function to print task output."""
    print(f"\n--- Task Output ---")
    # Access description directly from task_output if available
    description = getattr(task_output, 'description', 'N/A') 
    print(f"Task Description: {description}")
    # Access raw output using .raw
    raw_output = getattr(task_output, 'raw', 'N/A')
    print(f"Output:\n{raw_output}")
    print(f"--------------------\n")

def run():
    """
    Run the multi-stage writer crew.
    Handles two parts:
    1. Research and Outline generation.
    2. Drafting, Editing, and Fact-Checking based on the outline.
    """
    # Define initial inputs (replace with desired values or command-line args)
    inputs = {
        'topic': 'The Impact of Quantum Computing on Cryptography',
        'content_type': 'Blog Post',
        'audience': 'Technical Professionals',
        'tone': 'Informative and Formal',
        'length': 1500, # Approx words
        'instructions': 'Focus on potential vulnerabilities in current encryption and the development of quantum-resistant algorithms.',
        'current_year': str(datetime.now().year),
        # Placeholders for values generated/passed later
        'outline_content': '',
        'user_feedback_on_outline': '' # No feedback in this non-interactive version
    }

    try:
        print("--- Initializing Crew Instance ---")
        writer_crew_instance = WriterCrew()

        # --- Part 1: Research & Outline ---
        print("\n--- Starting Part 1: Research & Outline ---")
        # Get only the agents and tasks needed for Part 1
        researcher_agent = writer_crew_instance.researcher()
        outliner_agent = writer_crew_instance.outliner()
        research_task_instance = writer_crew_instance.research_task()
        outlining_task_instance = writer_crew_instance.outlining_task()

        # Define the crew for Part 1 by re-initializing with specific components
        crew_part1 = Crew(
            agents=[researcher_agent, outliner_agent],
            tasks=[research_task_instance, outlining_task_instance],
            process=Process.sequential, # Assuming sequential, adjust if needed
            verbose=True,
            task_callback=simple_task_callback # Pass callback during init
            # manager_callbacks=[simple_task_callback] # Use this for hierarchical process manager
        )

        # Kickoff Part 1
        # The result here *should* be the output of the last task (outlining_task)
        # Note: CrewAI's kickoff result behavior can vary. We access the specific task output.
        print("\n--- Kicking off Part 1 ---")
        crew_part1.kickoff(inputs=inputs)

        # Explicitly get the outline from the completed task
        # Task outputs are stored within the task objects after execution
        outline_result = outlining_task_instance.output.raw if outlining_task_instance.output else None

        if not outline_result:
            print("\nError: Could not retrieve outline from outlining task. Aborting.")
            return

        print(f"\n--- Part 1 Finished ---")
        print(f"Retrieved Outline:\n{outline_result}")

        # --- Part 2: Draft, Edit, Fact-Check ---
        print("\n--- Starting Part 2: Draft, Edit, Fact-Check ---")
        # Update inputs with the generated outline
        inputs['outline_content'] = outline_result

        # Get agents and tasks for Part 2
        writer_agent = writer_crew_instance.writer()
        editor_agent = writer_crew_instance.editor()
        fact_checker_agent = writer_crew_instance.fact_checker()
        drafting_task_instance = writer_crew_instance.drafting_task()
        editing_task_instance = writer_crew_instance.editing_task()
        fact_checking_task_instance = writer_crew_instance.fact_checking_task()

        # Define the crew for Part 2 by re-initializing with specific components
        crew_part2 = Crew(
            agents=[writer_agent, editor_agent, fact_checker_agent],
            tasks=[drafting_task_instance, editing_task_instance, fact_checking_task_instance],
            process=Process.sequential, # Assuming sequential, adjust if needed
            verbose=True,
            task_callback=simple_task_callback # Pass callback during init
            # manager_callbacks=[simple_task_callback] # Use this for hierarchical process manager
        )

        # Kickoff Part 2 with updated inputs
        print("\n--- Kicking off Part 2 ---")
        final_result = crew_part2.kickoff(inputs=inputs)

        print("\n--- Part 2 Finished ---")
        print("\n######################")
        print("Final Crew Result:")
        print(final_result)
        print("######################")

    except Exception as e:
        # Improved error message
        import traceback
        print(f"\n--- An error occurred during crew execution ---")
        print(f"Error: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        print("-------------------------------------------------")
        # Re-raise or handle as needed
        # raise Exception(f"An error occurred while running the crew: {e}")

# Keep the standard entry point check
if __name__ == "__main__":
    # Ensure API keys are set (example check)
    required_keys = ['OPENAI_API_KEY', 'SERPER_API_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        print(f"Error: Missing environment variables: {', '.join(missing_keys)}")
        print("Please ensure your .env file is correctly set up.")
    else:
        print("Starting CoWrite Crew execution...")
        run()
        print("CoWrite Crew execution finished.")

# Removed train(), replay(), test() functions
