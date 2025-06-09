"""
Text processing and analysis tools for CrewAI workflows.
"""

import re
import string
from collections import Counter
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator

from ..base import EnhancedBaseTool, BaseToolInput, ToolValidationError, ToolExecutionError


class TextAnalyzerInput(BaseToolInput):
    """Input schema for TextAnalyzerTool."""
    text: str = Field(..., description="Text to analyze")
    analysis_type: str = Field(
        default="comprehensive",
        description="Type of analysis: basic, comprehensive, or advanced"
    )
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed_types = ['basic', 'comprehensive', 'advanced']
        if v not in allowed_types:
            raise ValueError(f'analysis_type must be one of: {allowed_types}')
        return v


class TextAnalyzerTool(EnhancedBaseTool):
    """
    Tool for comprehensive text analysis including statistics, readability, and patterns.
    """
    
    name: str = "Text Analyzer Tool"
    description: str = (
        "Analyzes text content and provides detailed statistics including word count, "
        "readability metrics, keyword frequency, sentence structure analysis, and more. "
        "Use this when you need to understand text characteristics or quality metrics."
    )
    args_schema: type[BaseModel] = TextAnalyzerInput
    
    def _validate_input(self, **kwargs) -> None:
        """Validate text input."""
        text = kwargs.get("text", "").strip()
        if not text:
            raise ToolValidationError("Text cannot be empty")
        
        if len(text) > 100000:  # 100KB limit
            raise ToolValidationError("Text is too long (max 100,000 characters)")
    
    def _execute(self, **kwargs) -> str:
        """Execute text analysis."""
        text = kwargs["text"]
        analysis_type = kwargs.get("analysis_type", "comprehensive")
        
        try:
            if analysis_type == "basic":
                return self._basic_analysis(text)
            elif analysis_type == "comprehensive":
                return self._comprehensive_analysis(text)
            elif analysis_type == "advanced":
                return self._advanced_analysis(text)
            
        except Exception as e:
            raise ToolExecutionError(f"Text analysis failed: {str(e)}")
    
    def _basic_analysis(self, text: str) -> str:
        """Perform basic text analysis."""
        # Basic counts
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        word_count = len(text.split())
        sentence_count = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        result = [
            "=== BASIC TEXT ANALYSIS ===",
            "",
            f"Characters (with spaces): {char_count:,}",
            f"Characters (without spaces): {char_count_no_spaces:,}",
            f"Words: {word_count:,}",
            f"Sentences: {sentence_count:,}",
            f"Paragraphs: {paragraph_count:,}",
            "",
            f"Average words per sentence: {word_count / max(sentence_count, 1):.1f}",
            f"Average characters per word: {char_count_no_spaces / max(word_count, 1):.1f}",
        ]
        
        return "\n".join(result)
    
    def _comprehensive_analysis(self, text: str) -> str:
        """Perform comprehensive text analysis."""
        # Get basic stats first
        basic_result = self._basic_analysis(text)
        
        # Additional analysis
        words = text.lower().split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Word frequency
        word_freq = Counter(words)
        common_words = word_freq.most_common(10)
        
        # Sentence length analysis
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / max(len(sentence_lengths), 1)
        
        # Readability estimate (simplified Flesch-Kincaid)
        avg_sentence_len = avg_sentence_length
        avg_syllables = self._estimate_syllables_per_word(text)
        readability_score = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables)
        
        # Reading level
        if readability_score >= 90:
            reading_level = "Very Easy (5th grade)"
        elif readability_score >= 80:
            reading_level = "Easy (6th grade)"
        elif readability_score >= 70:
            reading_level = "Fairly Easy (7th grade)"
        elif readability_score >= 60:
            reading_level = "Standard (8th-9th grade)"
        elif readability_score >= 50:
            reading_level = "Fairly Difficult (10th-12th grade)"
        elif readability_score >= 30:
            reading_level = "Difficult (College level)"
        else:
            reading_level = "Very Difficult (Graduate level)"
        
        result = [
            basic_result,
            "",
            "=== DETAILED ANALYSIS ===",
            "",
            f"Average sentence length: {avg_sentence_length:.1f} words",
            f"Longest sentence: {max(sentence_lengths) if sentence_lengths else 0} words",
            f"Shortest sentence: {min(sentence_lengths) if sentence_lengths else 0} words",
            "",
            f"Readability Score: {readability_score:.1f}",
            f"Reading Level: {reading_level}",
            "",
            "Most Common Words:",
        ]
        
        for word, count in common_words:
            if len(word) > 2:  # Skip very short words
                result.append(f"  {word}: {count} times")
        
        return "\n".join(result)
    
    def _advanced_analysis(self, text: str) -> str:
        """Perform advanced text analysis with additional metrics."""
        # Get comprehensive analysis first
        comprehensive_result = self._comprehensive_analysis(text)
        
        # Advanced metrics
        words = text.lower().split()
        unique_words = set(words)
        
        # Lexical diversity
        lexical_diversity = len(unique_words) / max(len(words), 1)
        
        # Punctuation analysis
        punctuation_count = sum(1 for char in text if char in string.punctuation)
        
        # Capitalization analysis
        uppercase_count = sum(1 for char in text if char.isupper())
        
        # Pattern analysis
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        urls_found = len(url_pattern.findall(text))
        emails_found = len(email_pattern.findall(text))
        
        # Text complexity indicators
        long_words = [word for word in words if len(word) > 6]
        long_word_ratio = len(long_words) / max(len(words), 1)
        
        result = [
            comprehensive_result,
            "",
            "=== ADVANCED ANALYSIS ===",
            "",
            f"Unique words: {len(unique_words):,}",
            f"Lexical diversity: {lexical_diversity:.3f}",
            f"Long words (>6 chars): {len(long_words):,} ({long_word_ratio:.1%})",
            "",
            f"Punctuation marks: {punctuation_count:,}",
            f"Uppercase letters: {uppercase_count:,}",
            "",
            f"URLs found: {urls_found}",
            f"Email addresses found: {emails_found}",
            "",
            "Text Characteristics:",
            f"  - Vocabulary richness: {'High' if lexical_diversity > 0.7 else 'Medium' if lexical_diversity > 0.4 else 'Low'}",
            f"  - Complexity level: {'High' if long_word_ratio > 0.2 else 'Medium' if long_word_ratio > 0.1 else 'Low'}",
        ]
        
        return "\n".join(result)
    
    def _estimate_syllables_per_word(self, text: str) -> float:
        """Estimate average syllables per word (simplified method)."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return 0
        
        total_syllables = 0
        for word in words:
            # Simple syllable counting heuristic
            syllables = max(1, len(re.findall(r'[aeiouy]+', word)))
            if word.endswith('e'):
                syllables -= 1
            total_syllables += max(1, syllables)
        
        return total_syllables / len(words)


class TextCleanerInput(BaseToolInput):
    """Input schema for TextCleanerTool."""
    text: str = Field(..., description="Text to clean")
    cleaning_options: List[str] = Field(
        default=["whitespace", "punctuation"],
        description="Cleaning options: whitespace, punctuation, html, urls, emails, numbers, special_chars"
    )
    preserve_structure: bool = Field(
        default=True,
        description="Whether to preserve paragraph and sentence structure"
    )


class TextCleanerTool(EnhancedBaseTool):
    """
    Tool for cleaning and normalizing text content.
    """
    
    name: str = "Text Cleaner Tool"
    description: str = (
        "Cleans and normalizes text by removing or processing unwanted elements like "
        "extra whitespace, HTML tags, URLs, special characters, etc. Configurable "
        "cleaning options allow for precise control over the cleaning process."
    )
    args_schema: type[BaseModel] = TextCleanerInput
    
    def _validate_input(self, **kwargs) -> None:
        """Validate cleaning parameters."""
        text = kwargs.get("text", "")
        if not text.strip():
            raise ToolValidationError("Text cannot be empty")
        
        cleaning_options = kwargs.get("cleaning_options", [])
        valid_options = [
            "whitespace", "punctuation", "html", "urls", 
            "emails", "numbers", "special_chars"
        ]
        
        for option in cleaning_options:
            if option not in valid_options:
                raise ToolValidationError(f"Invalid cleaning option: {option}")
    
    def _execute(self, **kwargs) -> str:
        """Execute text cleaning."""
        text = kwargs["text"]
        cleaning_options = kwargs.get("cleaning_options", ["whitespace", "punctuation"])
        preserve_structure = kwargs.get("preserve_structure", True)
        
        try:
            cleaned_text = text
            applied_operations = []
            
            # Apply cleaning operations in order
            if "html" in cleaning_options:
                cleaned_text = self._remove_html(cleaned_text)
                applied_operations.append("Removed HTML tags")
            
            if "urls" in cleaning_options:
                cleaned_text = self._remove_urls(cleaned_text)
                applied_operations.append("Removed URLs")
            
            if "emails" in cleaning_options:
                cleaned_text = self._remove_emails(cleaned_text)
                applied_operations.append("Removed email addresses")
            
            if "numbers" in cleaning_options:
                cleaned_text = self._remove_numbers(cleaned_text)
                applied_operations.append("Removed numbers")
            
            if "special_chars" in cleaning_options:
                cleaned_text = self._remove_special_chars(cleaned_text, preserve_structure)
                applied_operations.append("Removed special characters")
            
            if "punctuation" in cleaning_options:
                cleaned_text = self._clean_punctuation(cleaned_text, preserve_structure)
                applied_operations.append("Cleaned punctuation")
            
            if "whitespace" in cleaning_options:
                cleaned_text = self._normalize_whitespace(cleaned_text, preserve_structure)
                applied_operations.append("Normalized whitespace")
            
            # Prepare result
            result = [
                "=== TEXT CLEANING RESULTS ===",
                "",
                f"Original length: {len(text):,} characters",
                f"Cleaned length: {len(cleaned_text):,} characters",
                f"Reduction: {len(text) - len(cleaned_text):,} characters ({((len(text) - len(cleaned_text)) / len(text) * 100):.1f}%)",
                "",
                "Applied operations:",
            ]
            
            for operation in applied_operations:
                result.append(f"  ✓ {operation}")
            
            result.extend([
                "",
                "=== CLEANED TEXT ===",
                "",
                cleaned_text
            ])
            
            return "\n".join(result)
            
        except Exception as e:
            raise ToolExecutionError(f"Text cleaning failed: {str(e)}")
    
    def _remove_html(self, text: str) -> str:
        """Remove HTML tags."""
        return re.sub(r'<[^>]+>', '', text)
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs."""
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return url_pattern.sub('', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses."""
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        return email_pattern.sub('', text)
    
    def _remove_numbers(self, text: str) -> str:
        """Remove numbers."""
        return re.sub(r'\b\d+(?:\.\d+)?\b', '', text)
    
    def _remove_special_chars(self, text: str, preserve_structure: bool) -> str:
        """Remove special characters."""
        if preserve_structure:
            # Keep basic punctuation and structure
            return re.sub(r'[^\w\s.!?,;:\n\-]', '', text)
        else:
            # Remove all special characters
            return re.sub(r'[^\w\s]', '', text)
    
    def _clean_punctuation(self, text: str, preserve_structure: bool) -> str:
        """Clean and normalize punctuation."""
        if preserve_structure:
            # Fix multiple punctuation marks
            text = re.sub(r'[.]{2,}', '.', text)
            text = re.sub(r'[!]{2,}', '!', text)
            text = re.sub(r'[?]{2,}', '?', text)
            text = re.sub(r'[,]{2,}', ',', text)
        else:
            # Remove all punctuation
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        return text
    
    def _normalize_whitespace(self, text: str, preserve_structure: bool) -> str:
        """Normalize whitespace."""
        if preserve_structure:
            # Normalize spaces but keep paragraph breaks
            text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
            text = re.sub(r'\n[ \t]*\n', '\n\n', text)  # Clean paragraph breaks
            text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
        else:
            # All whitespace to single spaces
            text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


class TextSummarizerInput(BaseToolInput):
    """Input schema for TextSummarizerTool."""
    text: str = Field(..., description="Text to summarize")
    summary_type: str = Field(
        default="extractive",
        description="Type of summary: extractive or key_points"
    )
    max_sentences: int = Field(
        default=5,
        description="Maximum number of sentences in summary"
    )
    
    @validator('summary_type')
    def validate_summary_type(cls, v):
        allowed_types = ['extractive', 'key_points']
        if v not in allowed_types:
            raise ValueError(f'summary_type must be one of: {allowed_types}')
        return v
    
    @validator('max_sentences')
    def validate_max_sentences(cls, v):
        if not 1 <= v <= 20:
            raise ValueError('max_sentences must be between 1 and 20')
        return v


class TextSummarizerTool(EnhancedBaseTool):
    """
    Tool for creating extractive summaries of text content.
    """
    
    name: str = "Text Summarizer Tool"
    description: str = (
        "Creates summaries of text content using extractive methods. Can generate "
        "sentence-based summaries or key point extractions. Uses statistical "
        "methods to identify the most important sentences based on word frequency "
        "and position."
    )
    args_schema: type[BaseModel] = TextSummarizerInput
    
    def _validate_input(self, **kwargs) -> None:
        """Validate summarization parameters."""
        text = kwargs.get("text", "").strip()
        if not text:
            raise ToolValidationError("Text cannot be empty")
        
        # Check if text has enough sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) < 2:
            raise ToolValidationError("Text must contain at least 2 sentences for summarization")
    
    def _execute(self, **kwargs) -> str:
        """Execute text summarization."""
        text = kwargs["text"]
        summary_type = kwargs.get("summary_type", "extractive")
        max_sentences = kwargs.get("max_sentences", 5)
        
        try:
            if summary_type == "extractive":
                return self._extractive_summary(text, max_sentences)
            elif summary_type == "key_points":
                return self._key_points_summary(text, max_sentences)
                
        except Exception as e:
            raise ToolExecutionError(f"Text summarization failed: {str(e)}")
    
    def _extractive_summary(self, text: str, max_sentences: int) -> str:
        """Create extractive summary using sentence scoring."""
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) <= max_sentences:
            return f"Original text is already short ({len(sentences)} sentences):\n\n" + text
        
        # Calculate word frequencies
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        # Remove very common words (simple stopwords)
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        filtered_freq = {word: freq for word, freq in word_freq.items() 
                        if word not in stopwords and len(word) > 2}
        
        # Score sentences
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            words_in_sentence = re.findall(r'\b\w+\b', sentence.lower())
            score = 0
            
            # Word frequency score
            for word in words_in_sentence:
                if word in filtered_freq:
                    score += filtered_freq[word]
            
            # Position score (first and last sentences get bonus)
            if i == 0 or i == len(sentences) - 1:
                score *= 1.2
            
            # Length penalty for very short sentences
            if len(words_in_sentence) < 5:
                score *= 0.5
            
            sentence_scores.append((score, i, sentence))
        
        # Select top sentences
        sentence_scores.sort(reverse=True)
        selected = sentence_scores[:max_sentences]
        
        # Sort by original order
        selected.sort(key=lambda x: x[1])
        
        summary_sentences = [sentence for _, _, sentence in selected]
        summary = '. '.join(summary_sentences) + '.'
        
        result = [
            f"=== EXTRACTIVE SUMMARY ({max_sentences} sentences) ===",
            "",
            f"Original: {len(sentences)} sentences, {len(text)} characters",
            f"Summary: {max_sentences} sentences, {len(summary)} characters",
            f"Compression ratio: {(len(summary) / len(text)):.1%}",
            "",
            summary
        ]
        
        return "\n".join(result)
    
    def _key_points_summary(self, text: str, max_points: int) -> str:
        """Extract key points from text."""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Look for sentences with key indicators
        key_indicators = [
            'important', 'key', 'main', 'primary', 'essential', 'crucial',
            'significant', 'major', 'critical', 'fundamental', 'central',
            'first', 'second', 'third', 'finally', 'conclusion', 'result',
            'therefore', 'thus', 'however', 'moreover', 'furthermore'
        ]
        
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0
            words = sentence.lower().split()
            
            # Check for key indicators
            for word in words:
                if word in key_indicators:
                    score += 2
            
            # Length score (prefer medium-length sentences)
            if 10 <= len(words) <= 25:
                score += 1
            
            # Position score
            if i < len(sentences) * 0.2 or i > len(sentences) * 0.8:
                score += 1
            
            scored_sentences.append((score, sentence))
        
        # Sort by score and select top points
        scored_sentences.sort(reverse=True)
        key_points = [sentence for _, sentence in scored_sentences[:max_points]]
        
        result = [
            f"=== KEY POINTS SUMMARY ({max_points} points) ===",
            "",
        ]
        
        for i, point in enumerate(key_points, 1):
            result.append(f"{i}. {point}")
        
        return "\n".join(result)