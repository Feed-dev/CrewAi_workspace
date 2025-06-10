"""
Cataloger Crew - Autonomous web cataloging AI crew using CrewAI with Ollama models.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool

# Import custom tools
from .tools.search_tools import enhanced_web_search, evolve_search_queries, plan_search_strategy
from .tools.analysis_tools import analyze_content_quality, extract_metadata, generate_tags
from .tools.catalog_tools import create_catalog_entry, detect_duplicates, export_catalog, generate_catalog_statistics


def load_ollama_config() -> Dict[str, Any]:
    """Load Ollama configuration from yaml file."""
    config_path = Path(__file__).parent.parent.parent / "ollama_config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    else:
        # Default configuration
        return {
            "models": {
                "search_model": "llama3.1:8b",
                "analysis_model": "llama3.1:8b", 
                "cataloger_model": "llama3.1:8b"
            },
            "ollama_host": "http://localhost:11434"
        }


@CrewBase
class CatalogerCrew:
    """Cataloger crew for autonomous web content cataloging."""
    
    def __init__(self):
        # Load configuration
        self.config = load_ollama_config()
        self.agents_config = self._load_config('agents.yaml')
        self.tasks_config = self._load_config('tasks.yaml')
        
        # Set up Ollama environment if needed
        if 'OLLAMA_BASE_URL' not in os.environ:
            os.environ['OLLAMA_BASE_URL'] = self.config.get('ollama_host', 'http://localhost:11434')
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from yaml file."""
        config_path = Path(__file__).parent / 'config' / config_file
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    @agent
    def search_agent(self) -> Agent:
        """Create the search agent with Ollama model."""
        config = self.agents_config['search_agent']
        
        # Format LLM with model from config
        llm = config['llm'].format(search_model=self.config['models']['search_model'])
        
        return Agent(
            config=config,
            llm=llm,
            tools=[
                enhanced_web_search,
                evolve_search_queries,
                plan_search_strategy,
                SerperDevTool()
            ],
            verbose=True
        )
    
    @agent
    def analysis_agent(self) -> Agent:
        """Create the analysis agent with Ollama model."""
        config = self.agents_config['analysis_agent']
        
        # Format LLM with model from config
        llm = config['llm'].format(analysis_model=self.config['models']['analysis_model'])
        
        return Agent(
            config=config,
            llm=llm,
            tools=[
                analyze_content_quality,
                extract_metadata,
                generate_tags,
                SerperDevTool(),  # For additional research if needed
                WebsiteSearchTool()  # For content scraping
            ],
            verbose=True
        )
    
    @agent
    def cataloger_agent(self) -> Agent:
        """Create the cataloger agent with Ollama model."""
        config = self.agents_config['cataloger_agent']
        
        # Format LLM with model from config
        llm = config['llm'].format(cataloger_model=self.config['models']['cataloger_model'])
        
        return Agent(
            config=config,
            llm=llm,
            tools=[
                create_catalog_entry,
                detect_duplicates,
                export_catalog,
                generate_catalog_statistics
            ],
            verbose=True
        )
    
    @task
    def search_task(self) -> Task:
        """Create the autonomous search task."""
        return Task(
            config=self.tasks_config['search_task'],
            agent=self.search_agent()
        )
    
    @task
    def analysis_task(self) -> Task:
        """Create the content analysis task."""
        return Task(
            config=self.tasks_config['analysis_task'],
            agent=self.analysis_agent(),
            context=[self.search_task()]
        )
    
    @task
    def cataloging_task(self) -> Task:
        """Create the cataloging task."""
        return Task(
            config=self.tasks_config['cataloging_task'],
            agent=self.cataloger_agent(),
            context=[self.analysis_task()]
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Cataloger crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,  # Enable crew memory for learning
            planning=True,  # Enable planning for autonomous operation
            planning_llm=self.config['models']['cataloger_model']  # Use cataloger model for planning
        )


def create_cataloger_crew(
    topic: str,
    search_terms: str,
    search_rounds: int = 3,
    search_model: str = None,
    analysis_model: str = None,
    cataloger_model: str = None
) -> CatalogerCrew:
    """
    Create a cataloger crew with specified parameters.
    
    Args:
        topic: Main topic to catalog
        search_terms: Initial search terms
        search_rounds: Number of search rounds to perform
        search_model: Override search model
        analysis_model: Override analysis model
        cataloger_model: Override cataloger model
    
    Returns:
        Configured CatalogerCrew instance
    """
    crew_instance = CatalogerCrew()
    
    # Override models if specified
    if search_model:
        crew_instance.config['models']['search_model'] = search_model
    if analysis_model:
        crew_instance.config['models']['analysis_model'] = analysis_model
    if cataloger_model:
        crew_instance.config['models']['cataloger_model'] = cataloger_model
    
    # Store parameters for task execution
    crew_instance.topic = topic
    crew_instance.search_terms = search_terms
    crew_instance.search_rounds = search_rounds
    
    return crew_instance