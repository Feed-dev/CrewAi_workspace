<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# CrewAI Writer with Gradio UI: Feature Roadmap

## Project Overview

This document provides a detailed breakdown of features for the CrewAI Writer with Gradio UI project. The application leverages specialized AI agents to collaboratively create written content through a simple, locally deployed interface.

## File Structure

```
writer_crew/
├── .cursor/
│   └── rules/           # Cursor AI editor rules
├── config/
│   ├── agents.yaml      # Agent definitions
│   └── tasks.yaml       # Task definitions
├── tools/
│   ├── __init__.py
│   ├── research_tools.py
│   ├── writing_tools.py
│   └── export_tools.py
├── models/              # Data models
│   ├── __init__.py
│   ├── content.py       # Content data models
│   └── settings.py      # User settings models
├── crew.py              # Crew orchestration
├── ui.py                # Gradio interface
├── api.py               # API handlers for OpenAI
├── main.py              # Application entry point
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── markdown_handler.py
│   └── error_handler.py
├── requirements.txt
├── .env.example         # Example environment variables
└── README.md
```


## 1. User Input Interface Features

### Feature Name: Topic/Title Specification

- **Description:** Allows users to enter the main topic or title for their content.
- **User Flow:**

1. User opens the application
2. User enters the topic or title in a text field
3. The topic is validated (not empty, reasonable length)
- **UI/UX Notes:**
    - Use a prominent text field at the top of the form
    - Provide placeholder text (e.g., "Enter your article topic or title")
    - Include real-time validation with character count
- **API Requirements:** None required for this feature
- **Implementation Notes:**

```python
# In models/content.py
from pydantic import BaseModel, Field

class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200, 
                     description="The main topic or title of the content")
    
# In ui.py (Gradio implementation)
import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("# AI Writer Crew")
    topic_input = gr.Textbox(
        label="Topic/Title", 
        placeholder="Enter your article topic or title",
        info="What would you like your content to be about?",
        max_lines=1
    )
```


### Feature Name: Content Type Selection

- **Description:** Allows users to select the type of content they want to generate.
- **User Flow:**

1. User selects from predefined content types in a dropdown menu
2. Different content types may enable specific options or templates
- **UI/UX Notes:**
    - Use a dropdown menu for common content types
    - Include description for each content type
    - Consider showing examples for each type
- **API Requirements:** None required for this feature
- **Implementation Notes:**

```python
# In models/content.py
from enum import Enum
from pydantic import BaseModel, Field

class ContentType(str, Enum):
    BLOG = "blog"
    ARTICLE = "article"
    DOCUMENTATION = "documentation"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"

class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200)
    content_type: ContentType = Field(default=ContentType.ARTICLE)
    
# In ui.py
content_type = gr.Dropdown(
    choices=["Blog Post", "Article", "Documentation", "Social Media Post", "Email"],
    label="Content Type",
    value="Article",
    info="Select the type of content you want to create"
)
```


### Feature Name: Audience, Tone, and Style Preferences

- **Description:** Allows users to specify target audience, tone, and stylistic preferences.
- **User Flow:**

1. User selects target audience from predefined options
2. User chooses tone (formal, casual, technical, etc.)
3. User selects writing style preferences
- **UI/UX Notes:**
    - Group these options in a "Content Style" section
    - Use radio buttons for tone and dropdowns for audience
    - Consider slider for formality level
- **API Requirements:** None required for this feature
- **Implementation Notes:**

```python
# In models/content.py
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
    # Previous fields...
    audience: Audience = Field(default=Audience.GENERAL)
    tone: Tone = Field(default=Tone.INFORMATIVE)
    style_notes: str = Field(default="", max_length=500)
    
# In ui.py
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


### Feature Name: Word Count Target

- **Description:** Allows users to specify how long their content should be.
- **User Flow:**

1. User sets desired word count using a slider or number input
2. System uses this as a target for content generation
- **UI/UX Notes:**
    - Use a slider with common word count ranges
    - Show recommended ranges for different content types
    - Consider preset buttons for common lengths (short, medium, long)
- **API Requirements:** None required for this feature
- **Implementation Notes:**

```python
# In models/content.py
class ContentRequest(BaseModel):
    # Previous fields...
    word_count: int = Field(default=500, ge=100, le=5000)
    
# In ui.py
word_count = gr.Slider(
    minimum=100,
    maximum=5000,
    value=500,
    step=100,
    label="Target Word Count",
    info="Approximate length of your content"
)
```


### Feature Name: Special Requirements Input

- **Description:** Allows users to specify any additional requirements for content generation.
- **User Flow:**

1. User enters special requirements in a text area
2. These requirements are incorporated into agent instructions
- **UI/UX Notes:**
    - Use a text area with ample space
    - Provide examples as placeholder text
    - Include checkboxes for common requirements (citations, data-driven, etc.)
- **API Requirements:** None required for this feature
- **Implementation Notes:**

```python
# In models/content.py
class ContentRequest(BaseModel):
    # Previous fields...
    special_requirements: str = Field(default="", max_length=1000)
    include_citations: bool = Field(default=False)
    data_driven: bool = Field(default=False)
    
# In ui.py
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


## 2. AI Agent Crew Features

### Feature Name: Research Agent

- **Description:** An AI agent that gathers relevant information on the specified topic.
- **User Flow:**

1. After submitting content request, the Research Agent activates first
2. User sees status updates as the agent conducts research
3. Research results are stored for use by other agents
- **UI/UX Notes:**
    - Show "Researching..." status with animated icon
    - Optionally display key search terms being used
    - Consider showing a sample of sources being consulted
- **API Requirements:**
    - OpenAI API for the agent's reasoning
    - Potentially web search tools (optional)
- **Implementation Notes:**

```python
# In config/agents.yaml
researcher:
  role: "Research Specialist"
  goal: "Find accurate and relevant information on the given topic"
  backstory: "You are an expert researcher with years of experience gathering and analyzing information from various sources."
  verbose: true
  allow_delegation: false
  tools:
    - SerperDevTool  # Optional if using web search

# In config/tasks.yaml
research_task:
  description: "Research {topic} thoroughly and provide comprehensive findings"
  expected_output: "Detailed research findings on {topic} including key facts, figures, and insights"
  agent: researcher
  context: "This research will be used to create informative content of type {content_type}"
```


### Feature Name: Outlining Agent

- **Description:** An AI agent that creates a structured outline for the content.
- **User Flow:**

1. After research is complete, the Outlining Agent activates
2. User sees the outline being generated
3. Outline is used as the framework for content creation
- **UI/UX Notes:**
    - Show progress as outline sections are created
    - Consider allowing user to approve/modify the outline before writing begins
    - Display hierarchical structure clearly
- **API Requirements:**
    - OpenAI API for the agent's reasoning
- **Implementation Notes:**

```python
# In config/agents.yaml
outliner:
  role: "Content Structuring Specialist"
  goal: "Create clear, logical, and comprehensive content outlines"
  backstory: "You are an experienced editor known for your ability to organize information in a coherent and engaging structure."
  verbose: true

# In models/content.py
from typing import List, Optional
class OutlineSection(BaseModel):
    title: str
    description: str = ""
    subsections: List['OutlineSection'] = []

class Outline(BaseModel):
    sections: List[OutlineSection] = []
    
# In config/tasks.yaml
outline_task:
  description: "Create a comprehensive outline for {topic} based on the research findings"
  expected_output: "A well-structured outline with main sections and subsections"
  agent: outliner
  context: "This outline will guide the writing of {content_type} content for a {audience} audience in a {tone} tone"
```


### Feature Name: Writing Agent

- **Description:** An AI agent that creates the content draft based on research and outline.
- **User Flow:**

1. After outline is complete, Writing Agent begins drafting content
2. User sees content being generated section by section
3. Draft is prepared for editing
- **UI/UX Notes:**
    - Show real-time content generation if possible
    - Indicate progress through sections of the outline
    - Consider a pulsing cursor or typing animation for engagement
- **API Requirements:**
    - OpenAI API for the agent's reasoning and content generation
- **Implementation Notes:**

```python
# In config/agents.yaml
writer:
  role: "Content Writer"
  goal: "Transform research and outlines into clear, engaging, and informative content"
  backstory: "You are a skilled writer known for your ability to explain complex topics in an accessible way."
  verbose: true

# In models/content.py
class ContentSection(BaseModel):
    title: str
    content: str
    outline_reference: str  # Reference to the outline section

class ContentDraft(BaseModel):
    sections: List[ContentSection] = []
    full_text: str = ""  # The complete content as a single text

# In config/tasks.yaml
writing_task:
  description: "Write content based on the outline and research for {topic}"
  expected_output: "Well-written content following the provided outline"
  agent: writer
  context: "Write {content_type} content for a {audience} audience in a {tone} tone with approximately {word_count} words"
```


### Feature Name: Editing Agent

- **Description:** An AI agent that refines and improves the content draft.
- **User Flow:**

1. After draft is complete, Editing Agent reviews and refines content
2. User sees tracked changes/improvements
3. Final content is prepared for review
- **UI/UX Notes:**
    - Consider showing "before and after" for significant edits
    - Use highlights or different colors to show changes
    - Show editing progress by section
- **API Requirements:**
    - OpenAI API for the agent's reasoning and editing capabilities
- **Implementation Notes:**

```python
# In config/agents.yaml
editor:
  role: "Content Editor"
  goal: "Refine content for clarity, coherence, style, and grammatical correctness"
  backstory: "You are a meticulous editor with an eye for detail and a commitment to polished, professional content."
  verbose: true

# In models/content.py
class EditSuggestion(BaseModel):
    original: str
    edited: str
    reason: str = ""

class EditedContent(BaseModel):
    final_text: str
    suggestions: List[EditSuggestion] = []
    improvement_summary: str = ""

# In config/tasks.yaml
editing_task:
  description: "Edit and refine the draft content for {topic}"
  expected_output: "Polished, error-free content with improved clarity and style"
  agent: editor
  context: "Edit this {content_type} content to ensure it matches a {tone} tone for a {audience} audience"
```


### Feature Name: Fact-Checking Agent (Optional)

- **Description:** An AI agent that verifies factual accuracy of the content.
- **User Flow:**

1. After editing is complete, Fact-Checking Agent reviews content for accuracy
2. User sees verification status for key statements
3. Citations are added where needed
- **UI/UX Notes:**
    - Show verification status with colored indicators
    - Display sources or citations in a distinct format
    - Allow user to toggle between content with/without citation markers
- **API Requirements:**
    - OpenAI API for the agent's reasoning
    - Potentially web search tools for verification
- **Implementation Notes:**

```python
# In config/agents.yaml
fact_checker:
  role: "Fact-Checking Specialist"
  goal: "Verify factual accuracy and add proper citations where needed"
  backstory: "You are a meticulous researcher with a strong commitment to accuracy and verifiability."
  verbose: true
  tools:
    - SerperDevTool  # Optional for verification

# In models/content.py
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


## 3. Process Visualization Features

### Feature Name: Agent Status Updates

- **Description:** Shows which agent is currently working and what they're doing.
- **User Flow:**

1. User submits content request
2. System displays which agent is active and their current task
3. Status updates in real-time as agents complete work
- **UI/UX Notes:**
    - Use clear visual indicators (colors, icons) for different agents
    - Show estimated time remaining if possible
    - Consider a progress bar for overall completion
- **API Requirements:**
    - Real-time status updates from CrewAI processes
- **Implementation Notes:**

```python
# In models/content.py
from datetime import datetime

class AgentStatus(BaseModel):
    agent_name: str
    agent_role: str
    current_task: str
    status: str  # "working", "completed", "waiting"
    started_at: datetime
    estimated_completion: Optional[datetime] = None

# In ui.py
def update_status(agent_name, task, status):
    return gr.update(
        value=f"Agent: {agent_name}\nTask: {task}\nStatus: {status}",
        visible=True
    )

with gr.Blocks() as demo:
    # Other UI elements...
    status_box = gr.Textbox(
        label="Current Status",
        value="Waiting to start...",
        interactive=False
    )
```


### Feature Name: Progress Indicators

- **Description:** Visual indicators showing overall completion progress.
- **User Flow:**

1. User sees overall progress as agents work
2. Progress updates in real-time
3. User gets estimate of remaining time
- **UI/UX Notes:**
    - Use a clear progress bar for overall completion
    - Consider segmented progress for different phases
    - Display time estimates in a user-friendly format
- **API Requirements:**
    - Progress updates from CrewAI processes
- **Implementation Notes:**

```python
# In models/content.py
class ProgressStatus(BaseModel):
    overall_progress: float  # 0.0 to 1.0
    current_phase: str
    phases_completed: List[str] = []
    estimated_time_remaining: Optional[int] = None  # seconds

# In ui.py
with gr.Blocks() as demo:
    # Other UI elements...
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


### Feature Name: Interactive Process View

- **Description:** Interactive visualization showing the workflow between agents.
- **User Flow:**

1. User sees a visual representation of the agent workflow
2. Current active step is highlighted
3. Completed steps show checkmarks or completion indicators
- **UI/UX Notes:**
    - Use a flowchart or step-by-step visualization
    - Highlight the current active step
    - Allow clicking on steps to see more details
- **API Requirements:**
    - Workflow status from CrewAI process
- **Implementation Notes:**

```python
# In models/content.py
class WorkflowStep(BaseModel):
    step_name: str
    agent_name: str
    status: str  # "pending", "active", "completed"
    details: str = ""

class Workflow(BaseModel):
    steps: List[WorkflowStep] = []
    current_step_index: int = 0

# In ui.py
with gr.Blocks() as demo:
    # Other UI elements...
    workflow_html = gr.HTML(
        """
        <div>
            <div>Research</div>
            <div>Outline</div>
            <div>Writing</div>
            <div>Editing</div>
            <div>Fact-Check</div>
        </div>
        """
    )
```


## 4. Content Review and Export Features

### Feature Name: Content Preview

- **Description:** Allows users to preview the generated content in a readable format.
- **User Flow:**

1. When content is completed, it's displayed in a formatted preview
2. User can scroll through and read the entire content
3. Preview shows formatting as it would appear in the final document
- **UI/UX Notes:**
    - Use proper typography and spacing for readability
    - Support Markdown formatting in the preview
    - Consider light/dark mode toggle for reading comfort
- **API Requirements:**
    - Markdown rendering
- **Implementation Notes:**

```python
# In ui.py
# Using Gradio Markdown component for preview
with gr.Blocks() as demo:
    # Other UI elements...
    preview_tab = gr.Tab("Preview")
    with preview_tab:
        preview_md = gr.Markdown("Content will appear here when ready.")
    
    # Update function
    def update_preview(content_markdown):
        return gr.update(value=content_markdown)
```


### Feature Name: Export to Markdown

- **Description:** Allows users to save the generated content as a .md file.
- **User Flow:**

1. User clicks "Export to Markdown" button
2. System generates .md file with proper formatting
3. File is downloaded to user's device
- **UI/UX Notes:**
    - Clear export button in the preview section
    - Show success confirmation after export
    - Consider offering filename customization
- **API Requirements:**
    - File download handling
- **Implementation Notes:**

```python
# In tools/export_tools.py
import os

def export_to_markdown(content, filename="generated_content.md"):
    """Export content to a markdown file"""
    with open(filename, "w") as f:
        f.write(content)
    return filename

# In ui.py
with gr.Blocks() as demo:
    # Other UI elements...
    with gr.Row():
        export_md_btn = gr.Button("Export to Markdown")
        filename_input = gr.Textbox(
            label="Filename",
            value="generated_content.md", 
            max_lines=1
        )
    export_status = gr.Textbox(label="Export Status", visible=False)
```


### Feature Name: Copy to Clipboard

- **Description:** Allows users to copy the entire content or sections to clipboard.
- **User Flow:**

1. User clicks "Copy to Clipboard" button
2. System copies content to clipboard
3. User receives confirmation of the copy action
- **UI/UX Notes:**
    - Offer both "Copy All" and section-specific copy options
    - Provide visual feedback when copied
    - Consider format options (plain text, markdown, etc.)
- **API Requirements:**
    - Clipboard interaction (typically handled by browser)
- **Implementation Notes:**

```python
# In ui.py
# This requires some JavaScript for clipboard functionality
with gr.Blocks() as demo:
    # Other UI elements...
    with gr.Row():
        copy_btn = gr.Button("Copy to Clipboard")
    copy_status = gr.Textbox(label="Copy Status", visible=False)
    
    # Using JavaScript for clipboard functionality
    copy_js = """
    function copyToClipboard() {
        const content = document.querySelector('.content-preview').innerText;
        navigator.clipboard.writeText(content)
            .then(() =&gt; {
                return "Content copied to clipboard!";
            })
            .catch(err =&gt; {
                return "Failed to copy: " + err;
            });
    }
    """
```


## Implementation Timeline

1. **Week 1:** Initial setup, project structure, and agent configuration
2. **Week 1-2:** Task definition and agent implementation
3. **Week 2-3:** Gradio UI development
4. **Week 3-4:** Integration, testing, and optimization
5. **Week 4:** Documentation and deployment preparation

This feature roadmap provides a comprehensive blueprint for developing the CrewAI Writer with Gradio UI application, focusing on user experience while leveraging the power of specialized AI agents working collaboratively.

<div>⁂</div>

[^1]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/1451282/aa53c7d2-93e9-43c6-acf7-32055a3d41e6/CrewAI_Writer_with_Gradio_UI_-MASTERPLAN.md

