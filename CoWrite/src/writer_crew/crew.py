from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Import tools directly
# from .tools.search_tools import web_search_tool # No longer importing the instance
from crewai_tools import SerperDevTool # Import the class
from .tools.file_tools import file_reading_tool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class WriterCrew():
	"""WriterCrew crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		# Instantiate SerperDevTool directly here
		try:
			search_tool_instance = SerperDevTool()
		except Exception as e:
			print(f"Error instantiating SerperDevTool in researcher agent: {e}")
			search_tool_instance = None

		# Compile the list of tools, adding only those that were successfully instantiated
		available_tools = []
		if search_tool_instance:
			available_tools.append(search_tool_instance)
		if file_reading_tool:
			available_tools.append(file_reading_tool)

		return Agent(
			config=self.agents_config['researcher'],
			tools=available_tools,
			verbose=True
		)

	@agent
	def outliner(self) -> Agent:
		return Agent(
			config=self.agents_config['outliner'],
			verbose=True
			# Tools are not needed for the outliner as it uses context
		)

	@agent
	def writer(self) -> Agent:
		return Agent(
			config=self.agents_config['writer'],
			verbose=True
			# Tools are not needed for the writer as it uses context
		)

	@agent
	def editor(self) -> Agent:
		return Agent(
			config=self.agents_config['editor'],
			verbose=True
			# Tools not needed for editor
		)

	@agent
	def fact_checker(self) -> Agent:
		# Instantiate SerperDevTool directly here as well for consistency
		try:
			search_tool_instance = SerperDevTool()
		except Exception as e:
			print(f"Error instantiating SerperDevTool in fact_checker agent: {e}")
			search_tool_instance = None

		# Fact checker needs web search to verify claims against external sources
		available_tools = []
		if search_tool_instance:
			available_tools.append(search_tool_instance)
		# Potentially add file_reading_tool if needed later

		return Agent(
			config=self.agents_config['fact_checker'],
			tools=available_tools,
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			# No agent needed here as it's inferred from the YAML
		)

	@task
	def outlining_task(self) -> Task:
		return Task(
			config=self.tasks_config['outlining_task'],
			# Agent inferred from YAML, context specified in YAML
		)

	@task
	def drafting_task(self) -> Task:
		return Task(
			config=self.tasks_config['drafting_task'],
			# Agent and context are specified in YAML
		)

	@task
	def editing_task(self) -> Task:
		return Task(
			config=self.tasks_config['editing_task'],
			# Agent and context are specified in YAML
		)

	@task
	def fact_checking_task(self) -> Task:
		return Task(
			config=self.tasks_config['fact_checking_task'],
			# Agent and context are specified in YAML
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the WriterCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			# Explicitly define agents and tasks in sequence
			agents=[self.researcher(), self.outliner(), self.writer(), self.editor(), self.fact_checker()],
			tasks=[self.research_task(), self.outlining_task(), self.drafting_task(), self.editing_task(), self.fact_checking_task()],
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
