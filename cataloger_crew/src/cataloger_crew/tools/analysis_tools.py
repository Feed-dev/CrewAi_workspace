"""
Content analysis and metadata extraction tools for the cataloger crew.
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from crewai import tool


@tool("Content Quality Analyzer")
def analyze_content_quality(content: str, url: str = "") -> str:
    """
    Analyze content quality and generate quality metrics.
    
    Args:
        content: Text content to analyze
        url: Source URL for additional context
    
    Returns:
        Quality analysis report with scores and recommendations
    """
    if not content or len(content.strip()) < 100:
        return "Content too short for quality analysis (minimum 100 characters required)"
    
    # Basic quality metrics
    word_count = len(content.split())
    sentence_count = len(re.split(r'[.!?]+', content))
    paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
    
    # Average sentence length
    avg_sentence_length = word_count / max(sentence_count, 1)
    
    # Calculate readability (simplified Flesch Reading Ease approximation)
    avg_sentence_length_score = min(max((avg_sentence_length - 15) / 10, 0), 1)
    
    # Content structure analysis
    has_headings = bool(re.search(r'^#{1,6}\s', content, re.MULTILINE))
    has_lists = bool(re.search(r'^\s*[-*+]\s', content, re.MULTILINE))
    has_links = bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content))
    
    # Domain authority (basic check)
    domain_authority = "unknown"
    if url:
        domain = urlparse(url).netloc.lower()
        if any(edu_domain in domain for edu_domain in ['.edu', '.ac.', 'university', 'college']):
            domain_authority = "academic"
        elif any(gov_domain in domain for gov_domain in ['.gov', '.mil']):
            domain_authority = "government"
        elif any(org_domain in domain for org_domain in ['.org']):
            domain_authority = "organization"
        else:
            domain_authority = "commercial"
    
    # Calculate overall quality score (0-10)
    structure_score = (
        (1 if has_headings else 0) +
        (1 if has_lists else 0) +
        (1 if has_links else 0)
    ) / 3
    
    length_score = min(word_count / 500, 1)  # Prefer 500+ words
    readability_score = 1 - avg_sentence_length_score  # Prefer shorter sentences
    
    overall_score = (structure_score * 3 + length_score * 4 + readability_score * 3) / 10 * 10
    
    # Domain bonus
    if domain_authority in ["academic", "government"]:
        overall_score = min(overall_score + 1, 10)
    
    quality_report = f"""
Content Quality Analysis Report
{'=' * 40}
Source URL: {url or 'Not provided'}
Analysis Timestamp: {datetime.now().isoformat()}

Content Metrics:
- Word Count: {word_count}
- Sentence Count: {sentence_count}
- Paragraph Count: {paragraph_count}
- Average Sentence Length: {avg_sentence_length:.1f} words

Structure Analysis:
- Has Headings: {'Yes' if has_headings else 'No'}
- Has Lists: {'Yes' if has_lists else 'No'}
- Has External Links: {'Yes' if has_links else 'No'}
- Structure Score: {structure_score:.2f}/1.0

Source Analysis:
- Domain Type: {domain_authority}
- Length Adequacy: {length_score:.2f}/1.0
- Readability: {readability_score:.2f}/1.0

Overall Quality Score: {overall_score:.1f}/10.0

Quality Assessment:
{_get_quality_assessment(overall_score)}

Recommendations:
{_get_quality_recommendations(overall_score, word_count, has_headings, has_lists)}
"""
    
    return quality_report


def _get_quality_assessment(score: float) -> str:
    """Get quality assessment based on score."""
    if score >= 8:
        return "Excellent - High-quality content suitable for cataloging"
    elif score >= 6:
        return "Good - Acceptable quality with minor issues"
    elif score >= 4:
        return "Fair - Meets minimum standards but could be improved"
    else:
        return "Poor - Below minimum quality standards"


def _get_quality_recommendations(score: float, word_count: int, has_headings: bool, has_lists: bool) -> str:
    """Get quality improvement recommendations."""
    recommendations = []
    
    if score < 6:
        recommendations.append("- Consider reviewing content for depth and completeness")
    
    if word_count < 500:
        recommendations.append("- Content may benefit from more detailed information")
    
    if not has_headings:
        recommendations.append("- Adding section headings would improve structure")
    
    if not has_lists:
        recommendations.append("- Consider using lists for better readability")
    
    if not recommendations:
        recommendations.append("- Content meets quality standards for cataloging")
    
    return "\n".join(recommendations)


@tool("Metadata Extractor")
def extract_metadata(content: str, url: str = "", title: str = "") -> str:
    """
    Extract comprehensive metadata from content.
    
    Args:
        content: Text content to analyze
        url: Source URL
        title: Content title if available
    
    Returns:
        Structured metadata in markdown format
    """
    if not content:
        return "No content provided for metadata extraction"
    
    # Basic content analysis
    word_count = len(content.split())
    estimated_reading_time = max(1, word_count // 200)  # ~200 words per minute
    
    # Extract potential dates
    date_patterns = [
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b'
    ]
    
    found_dates = []
    for pattern in date_patterns:
        dates = re.findall(pattern, content, re.IGNORECASE)
        found_dates.extend(dates)
    
    # Extract potential authors
    author_patterns = [
        r'[Bb]y\s+([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)',
        r'[Aa]uthor:\s*([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)',
        r'[Ww]ritten\s+by\s+([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)'
    ]
    
    potential_authors = []
    for pattern in author_patterns:
        authors = re.findall(pattern, content)
        potential_authors.extend(authors)
    
    # Content type detection
    content_type = _detect_content_type(content, url)
    
    # Topic extraction (simplified keyword extraction)
    topics = _extract_topics(content)
    
    # Technical level assessment
    technical_level = _assess_technical_level(content)
    
    metadata_report = f"""
Extracted Metadata
{'=' * 30}
Extraction Timestamp: {datetime.now().isoformat()}
Source URL: {url or 'Not provided'}
Title: {title or 'Not provided'}

Content Characteristics:
- Content Type: {content_type}
- Word Count: {word_count}
- Estimated Reading Time: {estimated_reading_time} minutes
- Technical Level: {technical_level}

Temporal Information:
- Potential Dates Found: {len(found_dates)}
{('- Dates: ' + ', '.join(found_dates[:3])) if found_dates else '- No dates detected'}

Authorship:
- Potential Authors: {len(potential_authors)}
{('- Authors: ' + ', '.join(potential_authors[:3])) if potential_authors else '- No authors detected'}

Topics and Keywords:
{chr(10).join(f'- {topic}' for topic in topics[:10])}

Source Analysis:
- Domain: {urlparse(url).netloc if url else 'Not provided'}
- URL Path Depth: {len(urlparse(url).path.split('/')) - 1 if url else 0}

Content Structure:
- Has Code Blocks: {'Yes' if '```' in content or '    ' in content else 'No'}
- Has Mathematical Content: {'Yes' if any(math_indicator in content.lower() for math_indicator in ['equation', 'formula', 'theorem', '=', '+', '-', '*', '/']) else 'No'}
- Has Citations: {'Yes' if '[' in content and ']' in content else 'No'}
"""
    
    return metadata_report


def _detect_content_type(content: str, url: str = "") -> str:
    """Detect the type of content based on content and URL patterns."""
    content_lower = content.lower()
    
    # Academic/Research indicators
    if any(indicator in content_lower for indicator in ['abstract', 'methodology', 'conclusion', 'references', 'doi:']):
        return "academic_paper"
    
    # Tutorial/Guide indicators
    if any(indicator in content_lower for indicator in ['step 1', 'tutorial', 'how to', 'guide', 'walkthrough']):
        return "tutorial"
    
    # News indicators
    if any(indicator in content_lower for indicator in ['breaking', 'reported', 'according to', 'sources say']):
        return "news"
    
    # Documentation indicators
    if any(indicator in content_lower for indicator in ['api', 'function', 'parameter', 'usage', 'installation']):
        return "documentation"
    
    # Blog post indicators
    if any(indicator in content_lower for indicator in ['opinion', 'i think', 'personal', 'experience']):
        return "blog_post"
    
    return "article"


def _extract_topics(content: str) -> List[str]:
    """Extract potential topics and keywords from content."""
    # Simple keyword extraction - in a real implementation, you might use NLP libraries
    words = re.findall(r'\b[A-Za-z]{4,}\b', content.lower())
    word_freq = {}
    
    # Common stop words to ignore
    stop_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'about', 'would', 'there', 'could', 'other', 'more', 'very', 'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should', 'after', 'being', 'now', 'made', 'before', 'here', 'through', 'when', 'where', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same', 'than', 'too', 'very'}
    
    for word in words:
        if word not in stop_words and len(word) >= 4:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top keywords by frequency
    sorted_topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [topic[0] for topic in sorted_topics[:15]]


def _assess_technical_level(content: str) -> str:
    """Assess the technical difficulty level of content."""
    content_lower = content.lower()
    
    # Technical indicators
    technical_terms = ['algorithm', 'implementation', 'architecture', 'framework', 'methodology', 'optimization', 'configuration', 'deployment', 'integration']
    advanced_terms = ['quantum', 'neural', 'machine learning', 'artificial intelligence', 'cryptography', 'blockchain', 'microservices']
    beginner_terms = ['introduction', 'basics', 'getting started', 'overview', 'beginner', 'simple', 'easy']
    
    technical_count = sum(1 for term in technical_terms if term in content_lower)
    advanced_count = sum(1 for term in advanced_terms if term in content_lower)
    beginner_count = sum(1 for term in beginner_terms if term in content_lower)
    
    if advanced_count >= 2 or technical_count >= 5:
        return "advanced"
    elif technical_count >= 2 or beginner_count == 0:
        return "intermediate"
    else:
        return "beginner"


@tool("Tag Generator")
def generate_tags(content: str, metadata: str = "", topic: str = "") -> str:
    """
    Generate relevant tags for content based on content analysis and metadata.
    
    Args:
        content: Text content to analyze for tags
        metadata: Previously extracted metadata
        topic: Main topic context
    
    Returns:
        Structured tag recommendations
    """
    if not content:
        return "No content provided for tag generation"
    
    content_lower = content.lower()
    
    # Category-based tag generation
    technology_tags = []
    methodology_tags = []
    domain_tags = []
    difficulty_tags = []
    format_tags = []
    temporal_tags = []
    
    # Technology tags
    tech_indicators = {
        'python': ['python', 'django', 'flask', 'pandas'],
        'javascript': ['javascript', 'react', 'node', 'vue'],
        'data-science': ['data science', 'machine learning', 'analytics', 'statistics'],
        'web-development': ['html', 'css', 'frontend', 'backend', 'api'],
        'cloud': ['aws', 'azure', 'cloud', 'kubernetes', 'docker'],
        'ai': ['artificial intelligence', 'neural network', 'deep learning']
    }
    
    for tech, indicators in tech_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            technology_tags.append(tech)
    
    # Methodology tags
    method_indicators = {
        'tutorial': ['tutorial', 'step-by-step', 'how-to', 'guide'],
        'research': ['study', 'research', 'analysis', 'findings'],
        'case-study': ['case study', 'example', 'implementation'],
        'comparison': ['comparison', 'versus', 'vs', 'compare'],
        'review': ['review', 'evaluation', 'assessment']
    }
    
    for method, indicators in method_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            methodology_tags.append(method)
    
    # Difficulty assessment
    if 'beginner' in content_lower or 'introduction' in content_lower:
        difficulty_tags.append('beginner-friendly')
    elif 'advanced' in content_lower or 'expert' in content_lower:
        difficulty_tags.append('advanced')
    else:
        difficulty_tags.append('intermediate')
    
    # Format tags based on content structure
    if '```' in content or 'code' in content_lower:
        format_tags.append('code-examples')
    if any(img_indicator in content_lower for img_indicator in ['image', 'figure', 'chart', 'graph']):
        format_tags.append('visual-content')
    if len(content) > 2000:
        format_tags.append('long-form')
    else:
        format_tags.append('concise')
    
    # Temporal tags
    current_year = datetime.now().year
    if str(current_year) in content or str(current_year - 1) in content:
        temporal_tags.append('recent')
    
    # Combine all tags
    all_tags = {
        'Technology': technology_tags,
        'Methodology': methodology_tags,
        'Difficulty': difficulty_tags,
        'Format': format_tags,
        'Temporal': temporal_tags
    }
    
    # Generate tag report
    tag_report = f"""
Generated Tags
{'=' * 20}
Generation Timestamp: {datetime.now().isoformat()}
Content Topic: {topic or 'General'}

Tag Categories:
"""
    
    for category, tags in all_tags.items():
        if tags:
            tag_report += f"\n{category}:\n"
            for tag in tags:
                tag_report += f"  - {tag}\n"
    
    # Flat tag list for easy consumption
    flat_tags = []
    for tag_list in all_tags.values():
        flat_tags.extend(tag_list)
    
    tag_report += f"""
Complete Tag Set:
{', '.join(flat_tags)}

Tag Statistics:
- Total Tags: {len(flat_tags)}
- Categories Used: {len([cat for cat, tags in all_tags.items() if tags])}
- Technology Tags: {len(technology_tags)}
- Methodology Tags: {len(methodology_tags)}
"""
    
    return tag_report