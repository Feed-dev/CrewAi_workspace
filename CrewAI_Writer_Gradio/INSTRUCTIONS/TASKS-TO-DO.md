<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# CrewAI Writer with Gradio UI: Implementation To-Do List

This document provides a step-by-step implementation guide for the CrewAI Writer with Gradio UI project, breaking down each feature into actionable tasks.

## Project Setup Tasks

- [ ] **Initial Project Structure**
    - [ ] Step 1: Create the base project directory and subdirectories

```bash
mkdir -p writer_crew/.cursor/rules writer_crew/config writer_crew/tools writer_crew/models writer_crew/utils
```

    - [ ] Step 2: Create initial files with placeholder content

```bash
touch writer_crew/main.py writer_crew/crew.py writer_crew/ui.py writer_crew/api.py
touch writer_crew/README.md writer_crew/requirements.txt writer_crew/.env.example
```

    - [ ] Dependencies: None
    - [ ] Notes: Follow the file structure as specified in the feature roadmap
- [ ] **Environment Setup**
    - [ ] Step 1: Create requirements.txt with all dependencies

```
crewai==0.28.0
gradio==4.19.1
openai==1.10.0
python-dotenv==1.0.0
langchain==0.0.345
pydantic==2.5.2
markdown==3.5
pyyaml==6.0.1
```

    - [ ] Step 2: Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

    - [ ] Step 3: Create .env file for API keys

```
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key  # If using web search capability
```

    - [ ] Dependencies: Python 3.9+ installed
    - [ ] Notes: Consider using pip-tools for dependency management in larger projects
- [ ] **Cursor AI Editor Rules**
    - [ ] Step 1: Create crewai.md rules file in .cursor/rules/

```markdown
"""
CursorRules for CrewAI Development
Version: 1.0.0
"""

RULES = {
  "file_structure": {
    "MUST": [
      "Place agent definitions in config/agents.yaml",
      "Place task definitions in config/tasks.yaml", 
      "Define crew orchestration logic in crew.py",
      "Store custom tools in tools/ directory",
      "Keep main execution flow in main.py"
    ]
  },
  "code_quality": {
    "MUST": [
      "Follow the 80/20 rule: 80% effort on tasks, 20% on agents",
      "Create specialized agents rather than generalists",
      "Make task descriptions clear and specific",
      "Provide context for each task"
    ]
  }
}
```

    - [ ] Dependencies: Cursor AI editor installed
    - [ ] Notes: These rules help maintain project structure and best practices


## Data Models Implementation

- [ ] **Content Data Models**
    - [ ] Step 1: Create base models in models/content.py

```python
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ContentType(str, Enum):
    BLOG = "blog"
    ARTICLE = "article"
    DOCUMENTATION = "documentation"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"

class Audience(str, Enum):
    GENERAL = "general"
    TECHNICAL = "technical"
    BUSINESS = "business"
    ACADEMIC = "academic"
    
class Tone(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    PERSUASIVE = "persuasive"
    INFORMATIVE = "informative"

class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200, 
                     description="The main topic or title of the content")
    content_type: ContentType = Field(default=ContentType.ARTICLE)
    audience: Audience = Field(default=Audience.GENERAL)
    tone: Tone = Field(default=Tone.INFORMATIVE)
    word_count: int = Field(default=500, ge=100, le=5000)
    style_notes: str = Field(default="", max_length=500)
    special_requirements: str = Field(default="", max_length=1000)
    include_citations: bool = Field(default=False)
    data_driven: bool = Field(default=False)
```

    - [ ] Step 2: Create outline and content models

```python
class OutlineSection(BaseModel):
    title: str
    description: str = ""
    subsections: List['OutlineSection'] = []

class Outline(BaseModel):
    sections: List[OutlineSection] = []

class ContentSection(BaseModel):
    title: str
    content: str
    outline_reference: str  # Reference to the outline section

class ContentDraft(BaseModel):
    sections: List[ContentSection] = []
    full_text: str = ""  # The complete content as a single text
```

    - [ ] Step 3: Create editing and verification models

```python
class EditSuggestion(BaseModel):
    original: str
    edited: str
    reason: str = ""

class EditedContent(BaseModel):
    final_text: str
    suggestions: List[EditSuggestion] = []
    improvement_summary: str = ""

class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNCERTAIN = "uncertain"
    CONTRADICTED = "contradicted"

class Citation(BaseModel):
    text: str  # The text being cited
    source: str  # Source information
    url: Optional[str] = None

class FactCheckResult(BaseModel):
    verified_content: str
    citations: List[Citation] = []
    fact_check_notes: str = ""
```

    - [ ] Dependencies: pydantic
    - [ ] Notes: Consider using model validators to ensure data consistency
- [ ] **Status and Progress Models**
    - [ ] Step 1: Create agent status and workflow models in models/content.py

```python
class AgentStatus(BaseModel):
    agent_name: str
    agent_role: str
    current_task: str
    status: str  # "working", "completed", "waiting"
    started_at: datetime
    estimated_completion: Optional[datetime] = None

class ProgressStatus(BaseModel):
    overall_progress: float  # 0.0 to 1.0
    current_phase: str
    phases_completed: List[str] = []
    estimated_time_remaining: Optional[int] = None  # seconds

class WorkflowStep(BaseModel):
    step_name: str
    agent_name: str
    status: str  # "pending", "active", "completed"
    details: str = ""

class Workflow(BaseModel):
    steps: List[WorkflowStep] = []
    current_step_index: int = 0
```

    - [ ] Dependencies: pydantic, datetime
    - [ ] Notes: These models help track and display the writing process


## Agent and Task Configuration

- [ ] **Agent Configuration**
    - [ ] Step 1: Create agents.yaml configuration file

```yaml
# config/agents.yaml
researcher:
  role: "Research Specialist"
  goal: "Find accurate and relevant information on the given topic"
  backstory: "You are an expert researcher with years of experience gathering and analyzing information from various sources."
  verbose: true
  allow_delegation: false
  tools:
    - SerperDevTool  # Optional if using web search

outliner:
  role: "Content Structuring Specialist"
  goal: "Create clear, logical, and comprehensive content outlines"
  backstory: "You are an experienced editor known for your ability to organize information in a coherent and engaging structure."
  verbose: true

writer:
  role: "Content Writer"
  goal: "Transform research and outlines into clear, engaging, and informative content"
  backstory: "You are a skilled writer known for your ability to explain complex topics in an accessible way."
  verbose: true

editor:
  role: "Content Editor"
  goal: "Refine content for clarity, coherence, style, and grammatical correctness"
  backstory: "You are a meticulous editor with an eye for detail and a commitment to polished, professional content."
  verbose: true

fact_checker:
  role: "Fact-Checking Specialist"
  goal: "Verify factual accuracy and add proper citations where needed"
  backstory: "You are a meticulous researcher with a strong commitment to accuracy and verifiability."
  verbose: true
  tools:
    - SerperDevTool  # Optional for verification
```

    - [ ] Dependencies: YAML format, CrewAI agent requirements
    - [ ] Notes: Follow the 80/20 rule (80% effort on tasks, 20% on agents)
- [ ] **Task Configuration**
    - [ ] Step 1: Create tasks.yaml configuration file

```yaml
# config/tasks.yaml
research_task:
  description: "Research {topic} thoroughly and provide comprehensive findings"
  expected_output: "Detailed research findings on {topic} including key facts, figures, and insights"
  agent: researcher
  context: "This research will be used to create informative content of type {content_type}"

outline_task:
  description: "Create a comprehensive outline for {topic} based on the research findings"
  expected_output: "A well-structured outline with main sections and subsections"
  agent: outliner
  context: "This outline will guide the writing of {content_type} content for a {audience} audience in a {tone} tone"
  async_execution: false
  human_input: false

writing_task:
  description: "Write content based on the outline and research for {topic}"
  expected_output: "Well-written content following the provided outline"
  agent: writer
  context: "Write {content_type} content for a {audience} audience in a {tone} tone with approximately {word_count} words"
  async_execution: false
  human_input: false

editing_task:
  description: "Edit and refine the draft content for {topic}"
  expected_output: "Polished, error-free content with improved clarity and style"
  agent: editor
  context: "Edit this {content_type} content to ensure it matches a {tone} tone for a {audience} audience"
  async_execution: false
  human_input: false

fact_checking_task:
  description: "Verify the factual accuracy of the content about {topic} and add citations where needed"
  expected_output: "Verified content with proper citations for factual statements"
  agent: fact_checker
  context: "This {content_type} content will be published and needs to be factually accurate"
  async_execution: false
  human_input: false
```

    - [ ] Dependencies: YAML format, CrewAI task requirements
    - [ ] Notes: Be explicit about inputs/outputs in task descriptions


## CrewAI Implementation

- [ ] **Crew Orchestration**
    - [ ] Step 1: Create crew.py file with crew setup

```python
from crewai import Crew, Process
from crewai.project import CrewBase, agent, task, crew
import yaml
import os

@CrewBase
class WriterCrew:
    """CrewAI Writer project for generating content"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @crew
    def crew(self) -&gt; Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2
        )
    
    @before_kickoff
    def preprocess_inputs(self, inputs):
        """Preprocess the inputs before starting the crew"""
        # Convert UI-friendly values to model-expected values
        if "content_type" in inputs:
            inputs["content_type"] = inputs["content_type"].upper()
        if "audience" in inputs:
            inputs["audience"] = inputs["audience"].upper()
        if "tone" in inputs:
            inputs["tone"] = inputs["tone"].upper()
        return inputs
    
    @after_kickoff
    def postprocess_result(self, result):
        """Process the result after crew completion"""
        # Any post-processing needed
        return result
```

    - [ ] Step 2: Create OpenAI API handler in api.py

```python
import openai
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_openai_with_retry(messages, model="gpt-4o", max_retries=3, backoff_factor=2):
    """Call OpenAI API with retry mechanism"""
    retries = 0
    while retries &lt;= max_retries:
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )
            return response.choices[^0].message.content
        except (openai.error.RateLimitError, openai.error.APIError) as e:
            wait_time = backoff_factor ** retries
            print(f"API error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
    
    raise Exception("Max retries exceeded when calling OpenAI API")
```

    - [ ] Dependencies: crewai, python-dotenv, openai
    - [ ] Notes: Implement proper error handling for API calls


## User Interface Implementation

- [ ] **Topic/Title Specification**
    - [ ] Step 1: Create basic Gradio interface in ui.py

```python
import gradio as gr
from models.content import ContentType, Audience, Tone

def create_interface():
    """Create the Gradio interface"""
    with gr.Blocks(title="AI Writer Crew") as demo:
        gr.Markdown("# AI Writer Crew")
        
        # Topic/Title input
        topic_input = gr.Textbox(
            label="Topic/Title", 
            placeholder="Enter your article topic or title",
            info="What would you like your content to be about?",
            max_lines=1
        )
        
        # Will add more UI elements in subsequent steps
        
        # Submit button
        submit_btn = gr.Button("Generate Content")
        
    return demo
```

    - [ ] Dependencies: gradio
    - [ ] Notes: Keep the UI clean and focused on the main task
- [ ] **Content Type Selection**
    - [ ] Step 1: Add content type dropdown to the UI

```python
# Add this inside the gr.Blocks() context in create_interface()
content_type = gr.Dropdown(
    choices=["Blog Post", "Article", "Documentation", "Social Media Post", "Email"],
    label="Content Type",
    value="Article",
    info="Select the type of content you want to create"
)
```

    - [ ] Dependencies: gradio
    - [ ] Notes: Consider adding tooltips explaining each content type
- [ ] **Audience, Tone, and Style Preferences**
    - [ ] Step 1: Add audience, tone, and style inputs to the UI

```python
# Add this inside the gr.Blocks() context in create_interface()
with gr.Group(label="Content Style"):
    audience = gr.Dropdown(
        choices=["General", "Technical", "Business", "Academic"],
        label="Target Audience",
        value="General"
    )
    tone = gr.Radio(
        choices=["Formal", "Casual", "Persuasive", "Informative"],
        label="Tone",
        value="Informative"
    )
    style_notes = gr.Textbox(
        label="Style Notes",
        placeholder="Any specific style requirements or preferences",
        max_lines=3
    )
```

    - [ ] Dependencies: gradio
    - [ ] Notes: Group related inputs for better UX
- [ ] **Word Count Target**
    - [ ] Step 1: Add word count slider to the UI

```python
# Add this inside the gr.Blocks() context in create_interface()
word_count = gr.Slider(
    minimum=100,
    maximum=5000,
    value=500,
    step=100,
    label="Target Word Count",
    info="Approximate length of your content"
)
```

    - [ ] Dependencies: gradio
    - [ ] Notes: Consider adding preset buttons for common lengths
- [ ] **Special Requirements Input**
    - [ ] Step 1: Add special requirements inputs to the UI

```python
# Add this inside the gr.Blocks() context in create_interface()
with gr.Group(label="Additional Requirements"):
    special_req = gr.Textbox(
        label="Special Requirements",
        placeholder="Any specific requirements or instructions (e.g., 'Include case studies')",
        max_lines=5
    )
    with gr.Row():
        citations = gr.Checkbox(label="Include Citations")
        data_driven = gr.Checkbox(label="Data-Driven Content")
```

    - [ ] Dependencies: gradio
    - [ ] Notes: Add help text to explain what types of special requirements are useful
- [ ] **Agent Status Updates**
    - [ ] Step 1: Add status updates display to the UI

```python
# Add this inside the gr.Blocks() context in create_interface()
with gr.Group(label="Process Status"):
    status_box = gr.Textbox(
        label="Current Status",
        value="Waiting to start...",
        interactive=False
    )
```

    - [ ] Step 2: Create update_status function

```python
def update_status(agent_name, task, status):
    """Update the status display"""
    return gr.update(
        value=f"Agent: {agent_name}\nTask: {task}\nStatus: {status}",
        visible=True
    )
```

    - [ ] Dependencies: gradio
    - [ ] Notes: Consider using colored text for different status types
- [ ] **Progress Indicators**
    - [ ] Step 1: Add progress indicators to the UI

```python
# Add this inside the Process Status group
progress_bar = gr.Slider(
    minimum=0,
    maximum=100,
    value=0,
    label="Overall Progress",
    interactive=False
)
time_remaining = gr.Textbox(
    label="Estimated Time Remaining",
    value="Calculating...",
    interactive=False
)
```

    - [ ] Step 2: Create update_progress function

```python
def update_progress(progress_percentage, time_left):
    """Update the progress indicators"""
    return {
        progress_bar: gr.update(value=progress_percentage),
        time_remaining: gr.update(value=time_left)
    }
```

    - [ ] Dependencies: gradio
    - [ ] Notes: Update progress in real-time as agents complete tasks
- [ ] **Interactive Process View**
    - [ ] Step 1: Add workflow visualization to the UI

```python
# Add this inside the gr.Blocks() context in create_interface()
workflow_html = gr.HTML(
    """
    <div>
        <div>Research</div>
        <div>Outline</div>
        <div>Writing</div>
        <div>Editing</div>
        <div>Fact-Check</div>
    </div>
    &lt;style&gt;
    .workflow-container {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
    }
    .workflow-step {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        flex: 1;
        margin: 0 5px;
    }
    .pending { background-color: #f0f0f0; color: #666; }
    .active { background-color: #ffd166; color: #000; }
    .completed { background-color: #06d6a0; color: #fff; }
    &lt;/style&gt;
    """
)
```

    - [ ] Step 2: Create update_workflow function

```python
def update_workflow(active_step):
    """Update the workflow visualization"""
    steps = ["research", "outline", "writing", "editing", "fact-check"]
    html = """
    <div>
    """
    
    for i, step in enumerate(steps):
        if i &lt; steps.index(active_step):
            status = "completed"
        elif i == steps.index(active_step):
            status = "active"
        else:
            status = "pending"
            
        html += f'<div>{step.capitalize()}</div>'
        
    html += """
    </div>
    &lt;style&gt;
    .workflow-container {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
    }
    .workflow-step {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        flex: 1;
        margin: 0 5px;
    }
    .pending { background-color: #f0f0f0; color: #666; }
    .active { background-color: #ffd166; color: #000; }
    .completed { background-color: #06d6a0; color: #fff; }
    &lt;/style&gt;
    """
    return html
```

    - [ ] Dependencies: gradio
    - [ ] Notes: Use CSS for clear visual distinction between workflow steps
- [ ] **Content Preview**
    - [ ] Step 1: Add content preview to the UI

```python
# Add this inside the gr.Blocks() context in create_interface()
with gr.Tabs() as tabs:
    with gr.Tab("Preview"):
        preview_md = gr.Markdown("Content will appear here when ready.")
    with gr.Tab("Raw Markdown"):
        raw_md = gr.Code(language="markdown", label="Markdown Source")
```

    - [ ] Step 2: Create update_preview function

```python
def update_preview(content_markdown):
    """Update the content preview"""
    return {
        preview_md: content_markdown,
        raw_md: content_markdown
    }
```

    - [ ] Dependencies: gradio
    - [ ] Notes: The Markdown component handles rendering for preview
- [ ] **Export to Markdown**
    - [ ] Step 1: Create export_tools.py in the tools directory

```python
# tools/export_tools.py
import os

def export_to_markdown(content, filename="generated_content.md"):
    """Export content to a markdown file"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return filename, True, f"Content exported successfully to {filename}"
    except Exception as e:
        return None, False, f"Error exporting content: {str(e)}"
```

    - [ ] Step 2: Add export functionality to the UI

```python
# Add this inside the gr.Blocks() context in create_interface()
with gr.Group(label="Export"):
    with gr.Row():
        export_md_btn = gr.Button("Export to Markdown")
        filename_input = gr.Textbox(
            label="Filename",
            value="generated_content.md", 
            max_lines=1
        )
    export_status = gr.Textbox(label="Export Status", visible=False)
```

    - [ ] Step 3: Connect export button to function

```python
# Add this after defining the Gradio interface
from tools.export_tools import export_to_markdown

def handle_export(content, filename):
    """Handle export button click"""
    _, success, message = export_to_markdown(content, filename)
    return gr.update(value=message, visible=True)
    
export_md_btn.click(
    fn=handle_export,
    inputs=[raw_md, filename_input],
    outputs=[export_status]
)
```

    - [ ] Dependencies: gradio, os
    - [ ] Notes: Validate the filename before exporting
- [ ] **Copy to Clipboard**
    - [ ] Step 1: Add copy to clipboard button to the UI

```python
# Add this inside the Export group
copy_btn = gr.Button("Copy to Clipboard")
copy_status = gr.Textbox(label="Copy Status", visible=False)
```

    - [ ] Step 2: Implement copy functionality

```python
# Add this JavaScript implementation
copy_js = """
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() =&gt; {
            return "Content copied to clipboard!";
        })
        .catch(err =&gt; {
            return "Failed to copy: " + err;
        });
}
"""

# Connect the button to the JavaScript function
copy_btn.click(
    fn=None,
    inputs=[raw_md],
    outputs=[copy_status],
    _js=copy_js
)
```

    - [ ] Dependencies: gradio
    - [ ] Notes: This requires JavaScript for clipboard access


## Integration and Main Application

- [ ] **Main Application Entry Point**
    - [ ] Step 1: Create main.py to tie everything together

```python
from dotenv import load_dotenv
import gradio as gr
import os
from ui import create_interface
from crew import WriterCrew

# Load environment variables
load_dotenv()

# Check for API keys
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

def main():
    """Main application entry point"""
    # Create the Gradio interface
    demo = create_interface()
    
    # Define handler for content generation
    def generate_content(topic, content_type, audience, tone, word_count, 
                         style_notes, special_req, citations, data_driven):
        """Handle content generation request"""
        # Initialize the crew
        writer_crew = WriterCrew()
        
        # Prepare inputs
        inputs = {
            "topic": topic,
            "content_type": content_type,
            "audience": audience,
            "tone": tone,
            "word_count": word_count,
            "style_notes": style_notes,
            "special_requirements": special_req,
            "include_citations": citations,
            "data_driven": data_driven
        }
        
        # Run the crew
        try:
            # Update status to "starting"
            yield update_status("System", "Initialization", "Starting the writing process...")
            yield update_workflow("research")
            
            # Start the crew
            result = writer_crew.kickoff(inputs=inputs)
            
            # Update UI with result
            yield update_preview(result)
            yield update_status("System", "Complete", "Content generation completed!")
            yield update_workflow("completed")
            
        except Exception as e:
            # Handle errors
            yield update_status("System", "Error", f"An error occurred: {str(e)}")
    
    # Connect the submit button to the handler
    demo.submit_btn.click(
        fn=generate_content,
        inputs=[
            demo.topic_input, demo.content_type, demo.audience, 
            demo.tone, demo.word_count, demo.style_notes, 
            demo.special_req, demo.citations, demo.data_driven
        ],
        outputs=[
            demo.status_box, demo.workflow_html, demo.preview_md, 
            demo.raw_md, demo.progress_bar, demo.time_remaining
        ]
    )
    
    # Launch the application
    demo.launch(share=False)

if __name__ == "__main__":
    main()
```

    - [ ] Dependencies: gradio, dotenv, all project modules
    - [ ] Notes: Add proper error handling and status updates
- [ ] **Final Integration Testing**
    - [ ] Step 1: Test the complete workflow
        - Test with a simple topic
        - Verify all agents are working as expected
        - Check output format and quality
    - [ ] Step 2: Test error handling
        - Test with missing or invalid inputs
        - Verify appropriate error messages are displayed
        - Check recovery from API failures
    - [ ] Dependencies: All project components
    - [ ] Notes: Address any edge cases or unexpected behaviors


## Documentation and Deployment

- [ ] **User Documentation**
    - [ ] Step 1: Update README.md with setup and usage instructions

```markdown
# CrewAI Writer with Gradio UI

A locally deployed AI writing assistant that uses specialized CrewAI agents to collaboratively create written content.

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your OpenAI API key:
```

OPENAI_API_KEY=your_key_here

```
4. Run the application: `python main.py`

## Usage

1. Enter a topic for your content
2. Select content type, audience, and tone
3. Set word count and any special requirements
4. Click "Generate Content" and wait for the results
5. Preview, export, or copy the generated content

## Features

- Collaborative AI writing using specialized agents
- Real-time progress tracking
- Export to markdown
- Copy to clipboard functionality
```

    - [ ] Dependencies: None
    - [ ] Notes: Include screenshots if possible
- [ ] **Optional: Docker Containerization**
    - [ ] Step 1: Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

    - [ ] Step 2: Create docker-compose.yml

```yaml
version: '3'

services:
  writer-crew:
    build: .
    ports:
      - "7860:7860"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./:/app
```

    - [ ] Dependencies: Docker, docker-compose
    - [ ] Notes: This allows for easy deployment across different environments

This implementation to-do list provides a comprehensive guide for developing the CrewAI Writer with Gradio UI application. Each feature is broken down into specific steps with code snippets, dependencies, and notes for additional considerations. Follow these steps in sequence to build a fully functional application.

<div>⁂</div>

[^1]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/1451282/aa53c7d2-93e9-43c6-acf7-32055a3d41e6/CrewAI_Writer_with_Gradio_UI_-MASTERPLAN.md

[^2]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/1451282/fb4e1fa5-0efa-43c6-9dac-6850e00fea52/CrewAI_Writer_with_Gradio_UI_FEATURE_ROADMAP.md

