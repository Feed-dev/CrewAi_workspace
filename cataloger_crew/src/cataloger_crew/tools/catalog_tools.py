"""
Catalog management and persistence tools for the cataloger crew.
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from crewai import tool


class CatalogManager:
    """Manages catalog data persistence and organization."""
    
    def __init__(self, catalog_dir: str = "catalog_data"):
        self.catalog_dir = Path(catalog_dir)
        self.catalog_dir.mkdir(exist_ok=True)
        
        # Define file paths
        self.catalog_file = self.catalog_dir / "catalog.json"
        self.backup_dir = self.catalog_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def load_catalog(self) -> Dict[str, Any]:
        """Load existing catalog or create new one."""
        if self.catalog_file.exists():
            try:
                with open(self.catalog_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._create_empty_catalog()
        else:
            return self._create_empty_catalog()
    
    def _create_empty_catalog(self) -> Dict[str, Any]:
        """Create empty catalog structure."""
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0",
                "total_entries": 0
            },
            "entries": {},
            "categories": {},
            "tags": {},
            "statistics": {
                "content_types": {},
                "sources": {},
                "quality_distribution": {}
            }
        }
    
    def save_catalog(self, catalog_data: Dict[str, Any]) -> bool:
        """Save catalog data to file."""
        try:
            # Update metadata
            catalog_data["metadata"]["last_updated"] = datetime.now().isoformat()
            catalog_data["metadata"]["total_entries"] = len(catalog_data.get("entries", {}))
            
            # Create backup before saving
            self._create_backup()
            
            # Save main catalog
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving catalog: {e}")
            return False
    
    def _create_backup(self) -> None:
        """Create backup of current catalog."""
        if self.catalog_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"catalog_backup_{timestamp}.json"
            
            try:
                with open(self.catalog_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            except Exception as e:
                print(f"Error creating backup: {e}")


# Global catalog manager instance
catalog_manager = CatalogManager()


@tool("Catalog Entry Creator")
def create_catalog_entry(
    title: str,
    url: str,
    content_summary: str,
    tags: str,
    metadata: str,
    quality_score: float = 5.0
) -> str:
    """
    Create a new catalog entry with comprehensive metadata.
    
    Args:
        title: Content title
        url: Source URL
        content_summary: Brief content summary
        tags: Comma-separated tags
        metadata: JSON string with additional metadata
        quality_score: Quality score (0-10)
    
    Returns:
        Entry creation status and details
    """
    try:
        # Load current catalog
        catalog = catalog_manager.load_catalog()
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Parse metadata
        try:
            meta_dict = json.loads(metadata) if metadata else {}
        except json.JSONDecodeError:
            meta_dict = {"raw_metadata": metadata}
        
        # Generate unique entry ID
        entry_id = f"entry_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(url) % 10000}"
        
        # Check for duplicates
        for existing_id, existing_entry in catalog["entries"].items():
            if existing_entry.get("url") == url:
                return f"Duplicate entry detected: URL already exists in catalog as {existing_id}"
        
        # Create entry
        entry = {
            "id": entry_id,
            "title": title,
            "url": url,
            "summary": content_summary,
            "tags": tag_list,
            "metadata": meta_dict,
            "quality_score": quality_score,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "source_domain": _extract_domain(url),
            "content_type": meta_dict.get("content_type", "unknown"),
            "technical_level": meta_dict.get("technical_level", "unknown")
        }
        
        # Add to catalog
        catalog["entries"][entry_id] = entry
        
        # Update categories and tags
        _update_catalog_indices(catalog, entry)
        
        # Save catalog
        if catalog_manager.save_catalog(catalog):
            return f"""
Entry Created Successfully
{'=' * 30}
Entry ID: {entry_id}
Title: {title}
URL: {url}
Tags: {len(tag_list)} tags assigned
Quality Score: {quality_score}/10
Created: {entry["created"]}

Catalog Statistics:
- Total Entries: {len(catalog["entries"])}
- This Entry's Categories: {_get_entry_categories(entry)}
"""
        else:
            return "Error: Failed to save catalog entry"
            
    except Exception as e:
        return f"Error creating catalog entry: {str(e)}"


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except:
        return "unknown"


def _update_catalog_indices(catalog: Dict[str, Any], entry: Dict[str, Any]) -> None:
    """Update catalog indices for categories and tags."""
    # Update tag index
    for tag in entry["tags"]:
        if tag not in catalog["tags"]:
            catalog["tags"][tag] = []
        catalog["tags"][tag].append(entry["id"])
    
    # Update category index (based on content type)
    content_type = entry["content_type"]
    if content_type not in catalog["categories"]:
        catalog["categories"][content_type] = []
    catalog["categories"][content_type].append(entry["id"])
    
    # Update statistics
    stats = catalog["statistics"]
    
    # Content types
    if content_type not in stats["content_types"]:
        stats["content_types"][content_type] = 0
    stats["content_types"][content_type] += 1
    
    # Sources
    domain = entry["source_domain"]
    if domain not in stats["sources"]:
        stats["sources"][domain] = 0
    stats["sources"][domain] += 1
    
    # Quality distribution
    quality_range = _get_quality_range(entry["quality_score"])
    if quality_range not in stats["quality_distribution"]:
        stats["quality_distribution"][quality_range] = 0
    stats["quality_distribution"][quality_range] += 1


def _get_entry_categories(entry: Dict[str, Any]) -> List[str]:
    """Get categories for an entry."""
    categories = [entry["content_type"]]
    
    # Add technical level as category
    if entry["technical_level"] != "unknown":
        categories.append(f"level_{entry['technical_level']}")
    
    # Add domain-based category
    domain = entry["source_domain"]
    if ".edu" in domain or ".ac." in domain:
        categories.append("academic")
    elif ".gov" in domain:
        categories.append("government")
    elif ".org" in domain:
        categories.append("organization")
    else:
        categories.append("commercial")
    
    return categories


def _get_quality_range(score: float) -> str:
    """Get quality range for score."""
    if score >= 8:
        return "excellent"
    elif score >= 6:
        return "good"
    elif score >= 4:
        return "fair"
    else:
        return "poor"


@tool("Duplicate Detector")
def detect_duplicates(url: str, title: str = "", content_summary: str = "") -> str:
    """
    Detect potential duplicate entries in the catalog.
    
    Args:
        url: URL to check
        title: Title to check
        content_summary: Content summary to check
    
    Returns:
        Duplicate detection report
    """
    try:
        catalog = catalog_manager.load_catalog()
        duplicates = []
        
        for entry_id, entry in catalog["entries"].items():
            similarity_score = 0
            reasons = []
            
            # Check URL match (exact)
            if entry.get("url") == url:
                similarity_score += 100
                reasons.append("Exact URL match")
            
            # Check title similarity (simple word overlap)
            if title and entry.get("title"):
                title_similarity = _calculate_text_similarity(title, entry["title"])
                if title_similarity > 0.8:
                    similarity_score += 50
                    reasons.append(f"Title similarity: {title_similarity:.2f}")
            
            # Check content summary similarity
            if content_summary and entry.get("summary"):
                content_similarity = _calculate_text_similarity(content_summary, entry["summary"])
                if content_similarity > 0.7:
                    similarity_score += 30
                    reasons.append(f"Content similarity: {content_similarity:.2f}")
            
            # If high similarity, flag as potential duplicate
            if similarity_score >= 60:
                duplicates.append({
                    "entry_id": entry_id,
                    "similarity_score": similarity_score,
                    "reasons": reasons,
                    "existing_title": entry.get("title", ""),
                    "existing_url": entry.get("url", "")
                })
        
        if duplicates:
            report = f"""
Potential Duplicates Detected
{'=' * 35}
Checking: {title or 'No title provided'}
URL: {url}

Found {len(duplicates)} potential duplicate(s):
"""
            for i, dup in enumerate(duplicates, 1):
                report += f"""
{i}. Entry ID: {dup['entry_id']}
   Similarity Score: {dup['similarity_score']}%
   Existing Title: {dup['existing_title']}
   Existing URL: {dup['existing_url']}
   Reasons: {', '.join(dup['reasons'])}
"""
        else:
            report = f"""
No Duplicates Detected
{'=' * 25}
Checking: {title or 'No title provided'}
URL: {url}

The content appears to be unique in the catalog.
"""
        
        return report
        
    except Exception as e:
        return f"Error detecting duplicates: {str(e)}"


def _calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity based on word overlap."""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


@tool("Catalog Exporter")
def export_catalog(format_type: str = "json", filter_category: str = "") -> str:
    """
    Export catalog in specified format with optional filtering.
    
    Args:
        format_type: Export format (json, csv, markdown)
        filter_category: Optional category filter
    
    Returns:
        Export status and file information
    """
    try:
        catalog = catalog_manager.load_catalog()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Filter entries if category specified
        entries_to_export = catalog["entries"]
        if filter_category:
            entries_to_export = {
                entry_id: entry for entry_id, entry in catalog["entries"].items()
                if filter_category in _get_entry_categories(entry)
            }
        
        if format_type.lower() == "json":
            export_file = catalog_manager.catalog_dir / f"catalog_export_{timestamp}.json"
            export_data = {
                "metadata": catalog["metadata"],
                "entries": entries_to_export,
                "export_info": {
                    "exported_at": datetime.now().isoformat(),
                    "filter_applied": filter_category or "none",
                    "total_entries": len(entries_to_export)
                }
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        elif format_type.lower() == "csv":
            export_file = catalog_manager.catalog_dir / f"catalog_export_{timestamp}.csv"
            
            with open(export_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Entry ID', 'Title', 'URL', 'Summary', 'Tags', 'Content Type',
                    'Technical Level', 'Quality Score', 'Source Domain', 'Created'
                ])
                
                # Write entries
                for entry_id, entry in entries_to_export.items():
                    writer.writerow([
                        entry_id,
                        entry.get('title', ''),
                        entry.get('url', ''),
                        entry.get('summary', ''),
                        ', '.join(entry.get('tags', [])),
                        entry.get('content_type', ''),
                        entry.get('technical_level', ''),
                        entry.get('quality_score', ''),
                        entry.get('source_domain', ''),
                        entry.get('created', '')
                    ])
        
        elif format_type.lower() == "markdown":
            export_file = catalog_manager.catalog_dir / f"catalog_export_{timestamp}.md"
            
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write(f"# Catalog Export\n\n")
                f.write(f"**Generated:** {datetime.now().isoformat()}\n")
                f.write(f"**Total Entries:** {len(entries_to_export)}\n")
                if filter_category:
                    f.write(f"**Filter Applied:** {filter_category}\n")
                f.write(f"\n---\n\n")
                
                # Group by content type
                by_type = {}
                for entry_id, entry in entries_to_export.items():
                    content_type = entry.get('content_type', 'unknown')
                    if content_type not in by_type:
                        by_type[content_type] = []
                    by_type[content_type].append((entry_id, entry))
                
                for content_type, entries in by_type.items():
                    f.write(f"## {content_type.title().replace('_', ' ')}\n\n")
                    
                    for entry_id, entry in entries:
                        f.write(f"### {entry.get('title', 'Untitled')}\n\n")
                        f.write(f"**URL:** {entry.get('url', '')}\n\n")
                        f.write(f"**Summary:** {entry.get('summary', '')}\n\n")
                        f.write(f"**Tags:** {', '.join(entry.get('tags', []))}\n\n")
                        f.write(f"**Quality Score:** {entry.get('quality_score', 'N/A')}/10\n\n")
                        f.write(f"**Technical Level:** {entry.get('technical_level', 'N/A')}\n\n")
                        f.write(f"---\n\n")
        
        else:
            return f"Error: Unsupported export format '{format_type}'. Use 'json', 'csv', or 'markdown'."
        
        return f"""
Catalog Export Completed
{'=' * 30}
Format: {format_type.upper()}
File: {export_file.name}
Location: {export_file}
Entries Exported: {len(entries_to_export)}
Filter Applied: {filter_category or 'None'}
Export Time: {datetime.now().isoformat()}

File Size: {export_file.stat().st_size if export_file.exists() else 0} bytes
"""
        
    except Exception as e:
        return f"Error exporting catalog: {str(e)}"


@tool("Catalog Statistics")
def generate_catalog_statistics() -> str:
    """
    Generate comprehensive statistics about the catalog.
    
    Returns:
        Detailed statistics report
    """
    try:
        catalog = catalog_manager.load_catalog()
        entries = catalog.get("entries", {})
        
        if not entries:
            return "Catalog is empty - no statistics available."
        
        # Basic counts
        total_entries = len(entries)
        
        # Content type distribution
        content_types = {}
        quality_scores = []
        technical_levels = {}
        source_domains = {}
        creation_dates = []
        
        for entry in entries.values():
            # Content types
            content_type = entry.get("content_type", "unknown")
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Quality scores
            if "quality_score" in entry:
                quality_scores.append(entry["quality_score"])
            
            # Technical levels
            tech_level = entry.get("technical_level", "unknown")
            technical_levels[tech_level] = technical_levels.get(tech_level, 0) + 1
            
            # Source domains
            domain = entry.get("source_domain", "unknown")
            source_domains[domain] = source_domains.get(domain, 0) + 1
            
            # Creation dates
            if "created" in entry:
                creation_dates.append(entry["created"])
        
        # Calculate quality statistics
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            max_quality = max(quality_scores)
            min_quality = min(quality_scores)
        else:
            avg_quality = max_quality = min_quality = 0
        
        # Tag statistics
        all_tags = []
        for entry in entries.values():
            all_tags.extend(entry.get("tags", []))
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Generate report
        stats_report = f"""
Catalog Statistics Report
{'=' * 35}
Generated: {datetime.now().isoformat()}
Catalog Version: {catalog.get('metadata', {}).get('version', 'Unknown')}
Last Updated: {catalog.get('metadata', {}).get('last_updated', 'Unknown')}

Overview:
- Total Entries: {total_entries}
- Unique Tags: {len(tag_counts)}
- Source Domains: {len(source_domains)}
- Content Types: {len(content_types)}

Quality Metrics:
- Average Quality Score: {avg_quality:.2f}/10
- Highest Quality Score: {max_quality}/10
- Lowest Quality Score: {min_quality}/10
- Entries with Quality Scores: {len(quality_scores)}/{total_entries}

Content Type Distribution:
"""
        
        for content_type, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_entries) * 100
            stats_report += f"- {content_type}: {count} ({percentage:.1f}%)\n"
        
        stats_report += f"""
Technical Level Distribution:
"""
        
        for level, count in sorted(technical_levels.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_entries) * 100
            stats_report += f"- {level}: {count} ({percentage:.1f}%)\n"
        
        stats_report += f"""
Top Source Domains:
"""
        
        for domain, count in sorted(source_domains.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / total_entries) * 100
            stats_report += f"- {domain}: {count} ({percentage:.1f}%)\n"
        
        stats_report += f"""
Most Popular Tags:
"""
        
        for tag, count in top_tags:
            stats_report += f"- {tag}: {count} entries\n"
        
        return stats_report
        
    except Exception as e:
        return f"Error generating statistics: {str(e)}"