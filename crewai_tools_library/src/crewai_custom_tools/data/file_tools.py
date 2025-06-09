"""
File operation tools for CrewAI workflows.
"""

import os
import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from ..base import EnhancedBaseTool, BaseToolInput, ToolValidationError, ToolExecutionError


class FileReaderInput(BaseToolInput):
    """Input schema for FileReaderTool."""
    file_path: str = Field(..., description="Path to the file to read")
    encoding: str = Field(default="utf-8", description="File encoding (default: utf-8)")
    max_size_mb: float = Field(default=10.0, description="Maximum file size in MB (default: 10)")


class FileReaderTool(EnhancedBaseTool):
    """
    Tool for reading various file types with safety checks.
    Supports text files, JSON, CSV, and basic binary file info.
    """
    
    name: str = "File Reader Tool"
    description: str = (
        "Reads and returns the content of text files, JSON files, or CSV files. "
        "Includes safety checks for file size and type. Use this when you need to "
        "read file contents for analysis or processing."
    )
    args_schema: type[BaseModel] = FileReaderInput
    
    def _validate_input(self, **kwargs) -> None:
        """Validate file path and safety constraints."""
        file_path = kwargs.get("file_path")
        max_size_mb = kwargs.get("max_size_mb", 10.0)
        
        if not file_path:
            raise ToolValidationError("file_path is required")
        
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            raise ToolValidationError(f"File does not exist: {file_path}")
        
        if not path.is_file():
            raise ToolValidationError(f"Path is not a file: {file_path}")
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ToolValidationError(
                f"File too large: {file_size_mb:.2f}MB > {max_size_mb}MB limit"
            )
    
    def _execute(self, **kwargs) -> str:
        """Execute file reading."""
        file_path = kwargs["file_path"]
        encoding = kwargs.get("encoding", "utf-8")
        
        path = Path(file_path)
        file_extension = path.suffix.lower()
        
        try:
            if file_extension == ".json":
                return self._read_json(path, encoding)
            elif file_extension == ".csv":
                return self._read_csv(path, encoding)
            else:
                return self._read_text(path, encoding)
                
        except UnicodeDecodeError:
            raise ToolExecutionError(
                f"Could not decode file with encoding '{encoding}'. "
                "Try a different encoding or check if file is binary."
            )
        except Exception as e:
            raise ToolExecutionError(f"Failed to read file: {str(e)}")
    
    def _read_text(self, path: Path, encoding: str) -> str:
        """Read plain text file."""
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return f"File: {path.name}\nContent:\n{content}"
    
    def _read_json(self, path: Path, encoding: str) -> str:
        """Read and format JSON file."""
        with open(path, 'r', encoding=encoding) as f:
            data = json.load(f)
        
        formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
        return f"JSON File: {path.name}\n{formatted_json}"
    
    def _read_csv(self, path: Path, encoding: str) -> str:
        """Read and format CSV file."""
        rows = []
        with open(path, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                rows.append(row)
                if i >= 100:  # Limit preview to first 100 rows
                    rows.append(["... (truncated after 100 rows)"])
                    break
        
        if not rows:
            return f"CSV File: {path.name}\n(Empty file)"
        
        # Format as table
        result = f"CSV File: {path.name}\n"
        for row in rows:
            result += " | ".join(str(cell) for cell in row) + "\n"
        
        return result


class FileWriterInput(BaseToolInput):
    """Input schema for FileWriterTool."""
    file_path: str = Field(..., description="Path where to write the file")
    content: str = Field(..., description="Content to write to the file")
    encoding: str = Field(default="utf-8", description="File encoding (default: utf-8)")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing file")


class FileWriterTool(EnhancedBaseTool):
    """
    Tool for writing content to files safely.
    """
    
    name: str = "File Writer Tool"
    description: str = (
        "Writes content to a specified file path. Includes safety checks to prevent "
        "accidental overwrites unless explicitly allowed. Use this when you need to "
        "save generated content, reports, or processed data to files."
    )
    args_schema: type[BaseModel] = FileWriterInput
    
    def _validate_input(self, **kwargs) -> None:
        """Validate write operation."""
        file_path = kwargs.get("file_path")
        content = kwargs.get("content")
        overwrite = kwargs.get("overwrite", False)
        
        if not file_path:
            raise ToolValidationError("file_path is required")
        
        if not content:
            raise ToolValidationError("content is required")
        
        path = Path(file_path)
        
        # Check if file exists and overwrite permission
        if path.exists() and not overwrite:
            raise ToolValidationError(
                f"File already exists: {file_path}. Set overwrite=True to replace it."
            )
        
        # Check if parent directory exists
        if not path.parent.exists():
            raise ToolValidationError(f"Parent directory does not exist: {path.parent}")
    
    def _execute(self, **kwargs) -> str:
        """Execute file writing."""
        file_path = kwargs["file_path"]
        content = kwargs["content"]
        encoding = kwargs.get("encoding", "utf-8")
        
        try:
            path = Path(file_path)
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            file_size = path.stat().st_size
            return f"Successfully wrote {len(content)} characters ({file_size} bytes) to {file_path}"
            
        except Exception as e:
            raise ToolExecutionError(f"Failed to write file: {str(e)}")


class DirectoryListInput(BaseToolInput):
    """Input schema for DirectoryListTool."""
    directory_path: str = Field(..., description="Path to the directory to list")
    include_hidden: bool = Field(default=False, description="Include hidden files/directories")
    file_types: Optional[List[str]] = Field(
        default=None, 
        description="Filter by file extensions (e.g., ['.txt', '.py'])"
    )


class DirectoryListTool(EnhancedBaseTool):
    """
    Tool for listing directory contents with filtering options.
    """
    
    name: str = "Directory List Tool"
    description: str = (
        "Lists the contents of a directory with optional filtering by file type. "
        "Can include or exclude hidden files. Use this when you need to explore "
        "directory structure or find specific types of files."
    )
    args_schema: type[BaseModel] = DirectoryListInput
    
    def _validate_input(self, **kwargs) -> None:
        """Validate directory path."""
        directory_path = kwargs.get("directory_path")
        
        if not directory_path:
            raise ToolValidationError("directory_path is required")
        
        path = Path(directory_path)
        
        if not path.exists():
            raise ToolValidationError(f"Directory does not exist: {directory_path}")
        
        if not path.is_dir():
            raise ToolValidationError(f"Path is not a directory: {directory_path}")
    
    def _execute(self, **kwargs) -> str:
        """Execute directory listing."""
        directory_path = kwargs["directory_path"]
        include_hidden = kwargs.get("include_hidden", False)
        file_types = kwargs.get("file_types")
        
        try:
            path = Path(directory_path)
            items = []
            
            for item in path.iterdir():
                # Skip hidden files if not requested
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                # Filter by file types if specified
                if file_types and item.is_file():
                    if item.suffix.lower() not in [ft.lower() for ft in file_types]:
                        continue
                
                # Get item info
                if item.is_dir():
                    item_type = "DIR"
                    size_info = ""
                else:
                    item_type = "FILE"
                    size = item.stat().st_size
                    size_info = f" ({size} bytes)"
                
                items.append(f"{item_type}: {item.name}{size_info}")
            
            if not items:
                return f"Directory '{directory_path}' is empty (with current filters)"
            
            result = f"Contents of '{directory_path}':\n"
            result += "\n".join(sorted(items))
            result += f"\n\nTotal items: {len(items)}"
            
            return result
            
        except Exception as e:
            raise ToolExecutionError(f"Failed to list directory: {str(e)}")


class FileValidatorInput(BaseToolInput):
    """Input schema for FileValidatorTool."""
    file_path: str = Field(..., description="Path to the file to validate")
    expected_type: Optional[str] = Field(
        default=None,
        description="Expected file type (json, csv, txt, etc.)"
    )
    check_content: bool = Field(
        default=True,
        description="Whether to validate file content structure"
    )


class FileValidatorTool(EnhancedBaseTool):
    """
    Tool for validating file existence, type, and basic content structure.
    """
    
    name: str = "File Validator Tool"
    description: str = (
        "Validates file existence, type, and optionally checks content structure. "
        "Useful for ensuring files meet expected criteria before processing. "
        "Can validate JSON syntax, CSV structure, etc."
    )
    args_schema: type[BaseModel] = FileValidatorInput
    
    def _execute(self, **kwargs) -> str:
        """Execute file validation."""
        file_path = kwargs["file_path"]
        expected_type = kwargs.get("expected_type")
        check_content = kwargs.get("check_content", True)
        
        path = Path(file_path)
        validation_results = []
        
        # Basic existence check
        if not path.exists():
            return f"INVALID: File does not exist: {file_path}"
        
        if not path.is_file():
            return f"INVALID: Path is not a file: {file_path}"
        
        validation_results.append("✓ File exists")
        
        # File type check
        actual_extension = path.suffix.lower()
        if expected_type:
            expected_extension = f".{expected_type.lower()}" if not expected_type.startswith('.') else expected_type.lower()
            if actual_extension == expected_extension:
                validation_results.append(f"✓ File type matches expected: {expected_type}")
            else:
                validation_results.append(f"✗ File type mismatch: expected {expected_type}, got {actual_extension}")
        
        # Content validation if requested
        if check_content:
            content_result = self._validate_content(path, actual_extension)
            validation_results.append(content_result)
        
        # File size info
        file_size = path.stat().st_size
        validation_results.append(f"ℹ File size: {file_size} bytes ({file_size / 1024:.2f} KB)")
        
        status = "VALID" if all("✗" not in result for result in validation_results) else "INVALID"
        result = f"{status}: {file_path}\n" + "\n".join(validation_results)
        
        return result
    
    def _validate_content(self, path: Path, extension: str) -> str:
        """Validate file content based on extension."""
        try:
            if extension == ".json":
                with open(path, 'r', encoding='utf-8') as f:
                    json.load(f)
                return "✓ Valid JSON syntax"
            
            elif extension == ".csv":
                with open(path, 'r', encoding='utf-8') as f:
                    csv.reader(f).__next__()  # Try to read first row
                return "✓ Valid CSV format"
            
            else:
                # For other file types, just check if it's readable as text
                with open(path, 'r', encoding='utf-8') as f:
                    f.read(1024)  # Read first 1KB
                return "✓ File is readable as text"
                
        except json.JSONDecodeError:
            return "✗ Invalid JSON syntax"
        except csv.Error as e:
            return f"✗ CSV format error: {str(e)}"
        except UnicodeDecodeError:
            return "✗ File is not valid text (possibly binary)"
        except Exception as e:
            return f"✗ Content validation failed: {str(e)}"