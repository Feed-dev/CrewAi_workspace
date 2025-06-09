# CoWrite/src/writer_crew/tools/file_tools.py
"""
This module provides tools related to file system interactions, primarily reading files.
"""

from crewai_tools import FileReadTool

# Instantiate the FileReadTool
# This tool allows agents to read the content of a specified file.
# Usage: agent.tools[0].run(file_path='/path/to/your/file.txt')
# It handles basic error checking for file existence.
try:
    file_reading_tool = FileReadTool()

    # Potential future enhancements:
    # - Add specific file type handlers (e.g., PDF, DOCX) if needed,
    #   possibly using libraries like PyPDF2 or python-docx.
    # - Implement more granular error handling or logging.

except Exception as e:
    print(f"Error instantiating file tools: {e}")
    # Set tool to None or raise an error
    file_reading_tool = None

# Example of adding specific file type support later:
# from crewai import tool
# import PyPDF2
#
# @tool("Read PDF File Content")
# def read_pdf(file_path: str) -> str:
#     """Reads the text content from a PDF file."""
#     try:
#         with open(file_path, 'rb') as f:
#             reader = PyPDF2.PdfReader(f)
#             text = "".join(page.extract_text() for page in reader.pages)
#         return text
#     except FileNotFoundError:
#         return f"Error: File not found at {file_path}"
#     except Exception as e:
#         return f"Error reading PDF file: {e}" 