#!/usr/bin/env python3
"""
Wolfram Alpha Tool Usage Example

This example demonstrates how to use the WolframAlphaTool in CrewAI workflows.
The tool provides access to Wolfram Alpha's computational knowledge engine.

Prerequisites:
1. Set WOLFRAM_APP_ID environment variable with your Wolfram Alpha App ID
2. Get your App ID from: https://developer.wolframalpha.com/
3. Install dependencies: pip install wolframalpha

Usage:
    python examples/wolfram_alpha_example.py
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai_custom_tools import WolframAlphaTool

# Load environment variables
load_dotenv()

def main():
    """Demonstrate WolframAlphaTool usage in a CrewAI workflow."""
    
    # Initialize the Wolfram Alpha tool
    wolfram_tool = WolframAlphaTool()
    
    # Create a mathematician agent with Wolfram Alpha capabilities
    mathematician = Agent(
        role="Mathematical Analyst",
        goal="Solve complex mathematical problems and provide detailed explanations",
        backstory=(
            "You are an expert mathematician with access to Wolfram Alpha's "
            "computational engine. You can solve equations, perform calculations, "
            "and analyze mathematical concepts with precision."
        ),
        tools=[wolfram_tool],
        verbose=True
    )
    
    # Create tasks that utilize the Wolfram Alpha tool
    calculation_task = Task(
        description=(
            "Use the Wolfram Alpha tool to solve the following mathematical problems:\n"
            "1. Calculate the integral of x^2 from 0 to 10\n"
            "2. Solve the equation x^2 + 5x + 6 = 0\n"
            "3. Find the derivative of sin(x) * cos(x)\n"
            "4. Calculate the population of Tokyo, Japan\n"
            "5. What is the distance from Earth to Mars?\n\n"
            "Provide clear explanations for each result."
        ),
        expected_output="Detailed solutions and explanations for all mathematical problems",
        agent=mathematician
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[mathematician],
        tasks=[calculation_task],
        verbose=True
    )
    
    print("Starting mathematical analysis with Wolfram Alpha...")
    result = crew.kickoff()
    print("\n" + "="*50)
    print("FINAL RESULTS:")
    print("="*50)
    print(result)

def test_direct_tool_usage():
    """Test the Wolfram Alpha tool directly."""
    print("\n" + "="*50)
    print("DIRECT TOOL TESTING:")
    print("="*50)
    
    # Initialize the tool
    wolfram_tool = WolframAlphaTool()
    
    # Test queries
    test_queries = [
        "integrate x^2 from 0 to 10",
        "solve x^2 + 5x + 6 = 0", 
        "population of Tokyo",
        "distance from Earth to Mars",
        "derivative of sin(x)*cos(x)"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        result = wolfram_tool.run(query)
        print(f"Result: {result}")

if __name__ == "__main__":
    # Check if Wolfram Alpha App ID is configured
    if not os.getenv('WOLFRAM_APP_ID') and not os.getenv('APP_ID'):
        print("❌ Error: WOLFRAM_APP_ID environment variable not found!")
        print("Please set your Wolfram Alpha App ID:")
        print("export WOLFRAM_APP_ID='your_app_id_here'")
        print("\nGet your App ID from: https://developer.wolframalpha.com/")
        exit(1)
    
    print("🔬 Wolfram Alpha Tool Example")
    print("=" * 50)
    
    # Test direct tool usage first
    test_direct_tool_usage()
    
    # Then run the full CrewAI example
    main()