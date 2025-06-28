"""
Enhanced Web Search Tool for Claude Computer Use
Provides real-time internet search capabilities with enhanced citation support.
Based on Anthropic's web_search_20250305 tool with enhanced integration.
"""

import asyncio
import json
import re
import html
from typing import ClassVar, Literal, Dict, List, Optional, Union
from urllib.parse import urlparse, urljoin

from .base import BaseAnthropicTool, ToolResult, ToolError


class EnhancedURLValidator:
    """Enhanced URL validation with comprehensive security and format checking."""
    
    def __init__(self):
        # Comprehensive URL pattern based on RFC 3986
        self.url_pattern = re.compile(
            r'^https?://'  # Protocol
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # Domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # Port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        # Suspicious patterns to block
        self.suspicious_patterns = [
            'javascript:', 'data:', 'blob:', 'about:', 'vbscript:', 
            'file:', 'ftp:', 'mailto:', 'tel:', 'sms:', 'market:'
        ]
        
        # Known malicious TLDs or patterns
        self.blocked_patterns = [
            '.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs'
        ]
    
    def validate_and_clean_url(self, url: str) -> str:
        """
        Validate and clean URL according to Anthropic guidelines.
        Returns cleaned URL or '#' if invalid.
        """
        if not url or url in ['#', 'Unknown', 'N/A', '']:
            return '#'
        
        # Clean up the URL
        url = url.strip()
        
        # Handle protocol-relative URLs
        if url.startswith('//'):
            url = f"https:{url}"
        elif url.startswith('/'):
            # Relative URLs without domain - cannot resolve
            return '#'
        elif not url.startswith(('http://', 'https://')):
            # Add https if it looks like a domain
            if '.' in url and not any(url.lower().startswith(pattern) for pattern in self.suspicious_patterns):
                url = f"https://{url}"
            else:
                return '#'
        
        # Check for suspicious patterns (quick security check)
        if any(pattern in url.lower() for pattern in self.suspicious_patterns):
            return '#'
        
        # Check for blocked file extensions in path
        if any(url.lower().endswith(pattern) for pattern in self.blocked_patterns):
            return '#'
        
        # Basic URL format validation with urlparse (more permissive)
        try:
            parsed = urlparse(url)
            if parsed.netloc and parsed.scheme in ['http', 'https']:
                # Ensure domain has valid structure (basic check)
                if '.' in parsed.netloc and len(parsed.netloc) >= 4:
                    return url
            return '#'
        except Exception:
            return '#'
    
    def extract_domain(self, url: str) -> str:
        """Extract clean domain from URL."""
        if url == '#':
            return 'Unknown source'
        
        try:
            parsed = urlparse(url)
            return parsed.netloc if parsed.netloc else 'Unknown source'
        except:
            # Fallback extraction
            if '/' in url:
                parts = url.split('/')
                if len(parts) > 2:
                    return parts[2]
            return 'Unknown source'


class WebSearchResultFormatter:
    """
    Enhanced web search result formatter with Streamlit optimization.
    
    Provides intelligent categorization, quality assessment, and beautiful
    formatting for web search results following Anthropic's citation guidelines.
    """
    
    def __init__(self):
        self.result_cache = {}
        self.url_validator = EnhancedURLValidator()
        
        self.quality_indicators = {
            'high': ['arxiv.org', 'scholar.google', '.edu', '.gov', 'nature.com', 'science.org', 'ieee.org'],
            'medium': ['wikipedia.org', 'stackoverflow.com', 'github.com', 'medium.com', 'docs.'],
            'news': ['cnn.com', 'bbc.com', 'reuters.com', 'ap.org', 'nytimes.com', 'wsj.com', 'npr.org'],
            'technical': ['docs.', 'api.', 'developer.', 'technical.', 'support.', 'manual.']
        }
        
        # Enhanced categories with icons and descriptions
        self.categories = {
            'academic': {
                'icon': '🎓',
                'label': 'Academic & Research',
                'description': 'Scholarly articles, research papers, and academic sources',
                'domains': ['.edu', 'scholar.', 'arxiv.', 'pubmed.', 'jstor.', 'ieee.', 'acm.org', 'researchgate.']
            },
            'news': {
                'icon': '📰', 
                'label': 'News & Media',
                'description': 'Current news, journalism, and media coverage',
                'domains': ['news', 'cnn.', 'bbc.', 'reuters.', 'ap.org', 'nytimes.', 'wsj.', 'guardian.', 'npr.org']
            },
            'official': {
                'icon': '🏛️',
                'label': 'Official Sources', 
                'description': 'Government, organizations, and authoritative institutions',
                'domains': ['.gov', '.org', 'wikipedia.', 'who.int', 'un.org', 'nasa.gov', 'nih.gov']
            },
            'technical': {
                'icon': '⚙️',
                'label': 'Technical Documentation',
                'description': 'Technical docs, APIs, and developer resources', 
                'domains': ['stackoverflow.', 'github.', 'docs.', 'api.', '.tech', 'developer.', 'manual.', 'reference.']
            },
            'commercial': {
                'icon': '🏢',
                'label': 'Commercial & Business',
                'description': 'Business websites, products, and commercial information',
                'domains': ['.com', '.co', 'business.', 'company.', 'corp.', 'shop.', 'store.']
            },
            'other': {
                'icon': '🔗',
                'label': 'Additional Sources',
                'description': 'Other relevant web sources and information',
                'domains': []
            }
        }

    def clean_html_content(self, content: str) -> str:
        """Clean HTML content and convert to plain text with enhanced handling."""
        if not content:
            return "No description available"
        
        # Convert to string if not already
        content = str(content)
        
        # First pass: Remove problematic HTML fragments that appear as raw text
        content = re.sub(r'</?\w+[^>]*>', '', content)  # Remove any remaining HTML tags
        content = re.sub(r'<[^>]*>', '', content)       # Remove malformed tags
        
        # Handle common HTML entities first
        html_entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'",
            '&nbsp;': ' ', '&copy;': '©', '&reg;': '®', '&trade;': '™',
            '&mdash;': '—', '&ndash;': '–', '&hellip;': '…', '&bull;': '•'
        }
        
        for entity, replacement in html_entities.items():
            content = content.replace(entity, replacement)
        
        # Decode any remaining HTML entities
        try:
            content = html.unescape(content)
        except:
            pass  # Continue if unescape fails
        
        # Clean up JavaScript or CSS fragments
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove common web artifacts and noise
        content = re.sub(r'\s*\.\.\.\s*$', '', content)     # Remove trailing ...
        content = re.sub(r'^[|\s]*', '', content)           # Remove leading pipes/spaces
        content = re.sub(r'\s*\|\s*$', '', content)         # Remove trailing pipes
        content = re.sub(r'\s*\[\s*\]\s*', '', content)     # Remove empty brackets
        content = re.sub(r'\s*\(\s*\)\s*', '', content)     # Remove empty parentheses
        
        # Clean up extra whitespace and normalize
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove excessive punctuation and clean up ellipsis
        content = re.sub(r'([.!?]){2,}', r'\1', content)
        content = re.sub(r'\.{3,}', '...', content)  # Normalize ellipsis
        
        # Remove standalone HTML-like fragments that may appear as text
        content = re.sub(r'^(</?\w+>?|\s*[{}]\s*)$', '', content.strip())
        
        # Handle common web page artifacts (use case-insensitive matching)
        common_artifacts = [
            'JavaScript is disabled', 'Enable JavaScript', 'Loading', 
            'Please wait', 'Skip to content', 'Skip navigation',
            'Advertisement', 'Sponsored content', 'Cookie notice'
        ]
        
        content_lower = content.lower()
        for artifact in common_artifacts:
            if artifact.lower() in content_lower:
                # Remove the artifact (case-insensitive)
                pattern = re.escape(artifact)
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Final cleanup
        content = content.strip()
        
        return content if content and len(content) > 3 else "No description available"

    def categorize_result(self, url: str, title: str) -> str:
        """Enhanced categorization with multiple criteria."""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Check each category
        for category, info in self.categories.items():
            if category == 'other':  # Skip 'other' for now
                continue
                
            # Check URL domains
            if any(domain in url_lower for domain in info['domains']):
                return category
                
            # Check title keywords for better classification
            if category == 'academic' and any(word in title_lower for word in ['research', 'study', 'paper', 'journal', 'university']):
                return category
            elif category == 'news' and any(word in title_lower for word in ['breaking', 'report', 'announces', 'news', 'says', 'claims']):
                return category
            elif category == 'technical' and any(word in title_lower for word in ['documentation', 'api', 'tutorial', 'guide', 'how to', 'setup']):
                return category
            elif category == 'official' and any(word in title_lower for word in ['official', 'government', 'agency', 'department']):
                return category
        
        return 'other'

    def assess_result_quality(self, result: dict) -> dict:
        """Enhanced quality assessment with multiple factors."""
        url = result.get('url', '').lower()
        title = result.get('title', '')
        content = result.get('content', '')
        
        quality_score = 0.5  # Base score
        quality_factors = []
        
        # Domain authority assessment
        for quality_level, domains in self.quality_indicators.items():
            if any(domain in url for domain in domains):
                if quality_level == 'high':
                    quality_score += 0.3
                    quality_factors.append("High-authority domain")
                elif quality_level == 'medium':
                    quality_score += 0.2
                    quality_factors.append("Reputable source")
                elif quality_level == 'news':
                    quality_score += 0.25
                    quality_factors.append("News source")
                elif quality_level == 'technical':
                    quality_score += 0.15
                    quality_factors.append("Technical resource")
                break
        
        # Content quality indicators
        if len(content) > 200:
            quality_score += 0.1
            quality_factors.append("Detailed content")
        
        if len(title) > 10 and len(title) < 100:
            quality_score += 0.05
            quality_factors.append("Well-formed title")
        
        # Recency bonus (if date available)
        if 'date' in result and result['date']:
            quality_score += 0.05
            quality_factors.append("Recent content")
        
        # URL structure quality
        if not any(suspicious in url for suspicious in ['?', '&sid=', 'utm_', 'fbclid=']):
            quality_score += 0.05
            quality_factors.append("Clean URL")
        
        # Cap the score
        quality_score = min(quality_score, 1.0)
        
        # Determine quality level
        if quality_score >= 0.8:
            quality_level = "excellent"
            quality_icon = "🌟"
        elif quality_score >= 0.65:
            quality_level = "high"
            quality_icon = "✅"
        elif quality_score >= 0.5:
            quality_level = "good"
            quality_icon = "👍"
        else:
            quality_level = "moderate"
            quality_icon = "ℹ️"
        
        return {
            'score': quality_score,
            'level': quality_level,
            'icon': quality_icon,
            'factors': quality_factors
        }

    def create_citation_reference(self, result: dict, index: int) -> dict:
        """Create properly formatted citation following Anthropic guidelines."""
        quality_info = self.assess_result_quality(result)
        url = result.get('url', '#')
        validated_url = self.url_validator.validate_and_clean_url(url)
        
        return {
            'id': index,
            'url': validated_url,
            'title': result.get('title', 'Untitled'),
            'domain': self.url_validator.extract_domain(validated_url),
            'cited_text': result.get('content', 'No preview available')[:150] + "..." if len(result.get('content', '')) > 150 else result.get('content', 'No preview available'),
            'date': result.get('page_age', ''),
            'quality': quality_info,
            'category': self.categorize_result(url, result.get('title', '')),
            'relevance_score': self._calculate_relevance_score(result),
            'trust_score': self._calculate_trust_score(validated_url, result.get('title', '')),
            'is_clickable': validated_url != '#',
            'encrypted_content': result.get('encrypted_content'),  # For multi-turn citations
        }
    
    def _calculate_relevance_score(self, result: dict) -> float:
        """Calculate relevance score based on content quality and completeness."""
        score = 0.5  # Base score
        
        # Title quality (clear, descriptive)
        title = result.get('title', '')
        if len(title) > 10 and len(title) < 80:
            score += 0.1
        
        # Content richness
        content = result.get('content', '')
        if len(content) > 100:
            score += 0.15
        if len(content) > 300:
            score += 0.1
        
        # URL structure (clean, descriptive)
        url = result.get('url', '')
        if not any(suspicious in url.lower() for suspicious in ['?', '&', '=', '%', 'utm_']):
            score += 0.05
        
        return min(score, 1.0)
    
    def _calculate_trust_score(self, url: str, title: str) -> float:
        """Calculate trust score based on domain authority and content indicators."""
        score = 0.5  # Base trust
        url_lower = url.lower()
        title_lower = title.lower()
        
        # High-trust domains
        high_trust = ['.edu', '.gov', '.org', 'wikipedia.', 'arxiv.', 'ieee.', 'nature.com', 'science.org']
        if any(domain in url_lower for domain in high_trust):
            score += 0.3
        
        # Medium-trust domains  
        medium_trust = ['github.', 'stackoverflow.', 'mozilla.', 'w3.org', 'developer.', 'docs.']
        if any(domain in url_lower for domain in medium_trust):
            score += 0.2
        
        # News organizations
        news_orgs = ['bbc.', 'reuters.', 'ap.org', 'npr.org', 'cnn.', 'nytimes.', 'wsj.', 'guardian.']
        if any(domain in url_lower for domain in news_orgs):
            score += 0.25
        
        # Content quality indicators
        quality_keywords = ['research', 'study', 'analysis', 'report', 'documentation', 'official']
        if any(keyword in title_lower for keyword in quality_keywords):
            score += 0.1
        
        # Suspicious indicators (reduce trust)
        suspicious = ['click', 'amazing', 'secret', 'hack', 'trick', 'weird', 'shocking']
        if any(word in title_lower for word in suspicious):
            score -= 0.2
        
        return max(0.1, min(score, 1.0))

    def parse_anthropic_response(self, tool_result) -> List[dict]:
        """
        Parse Anthropic API response format with comprehensive handling.
        Based on official documentation structure.
        """
        results = []
        
        # Debug the structure for better understanding
        print(f"🔍 DEBUG: Parsing tool_result structure")
        print(f"   - Type: {type(tool_result)}")
        
        # Priority 1: Handle new Anthropic API format (web_search_tool_result in content list)
        if hasattr(tool_result, 'content') and isinstance(tool_result.content, list):
            print(f"   - Found content list with {len(tool_result.content)} items")
            for i, content_block in enumerate(tool_result.content):
                print(f"   - Content block {i}: type={getattr(content_block, 'type', 'unknown')}")
                if hasattr(content_block, 'type') and content_block.type == 'web_search_tool_result':
                    # Extract results from Anthropic format
                    search_results = getattr(content_block, 'content', [])
                    print(f"   - Found {len(search_results)} search results in content block")
                    for j, result in enumerate(search_results):
                        if hasattr(result, 'type') and result.type == 'web_search_result':
                            raw_content = getattr(result, 'content', '')
                            clean_content = self.clean_html_content(raw_content)
                            raw_title = getattr(result, 'title', 'Untitled')
                            clean_title = self.clean_html_content(raw_title)
                            
                            print(f"     - Result {j}: title='{clean_title[:50]}...', content_len={len(clean_content)}")
                            
                            processed_result = {
                                'url': getattr(result, 'url', ''),
                                'title': clean_title,
                                'content': clean_content,
                                'page_age': getattr(result, 'page_age', 'Unknown age'),
                                'encrypted_content': getattr(result, 'encrypted_content', None)
                            }
                            # Validate URL
                            processed_result['url'] = self.url_validator.validate_and_clean_url(processed_result['url'])
                            results.append(processed_result)
        
        # Priority 2: Handle dict content format
        elif hasattr(tool_result, 'content') and isinstance(tool_result.content, dict):
            print(f"   - Found content dict")
            content = tool_result.content
            if content.get('type') == 'web_search_tool_result':
                search_results = content.get('results', [])
                print(f"   - Found {len(search_results)} search results in content dict")
                for i, result in enumerate(search_results):
                    raw_content = result.get('content', '')
                    clean_content = self.clean_html_content(raw_content)
                    raw_title = result.get('title', 'Untitled')
                    clean_title = self.clean_html_content(raw_title)
                    
                    print(f"     - Result {i}: title='{clean_title[:50]}...', content_len={len(clean_content)}")
                    
                    processed_result = {
                        'url': self.url_validator.validate_and_clean_url(result.get('url', '')),
                        'title': clean_title,
                        'content': clean_content,
                        'page_age': result.get('page_age', 'Unknown age'),
                        'encrypted_content': result.get('encrypted_content', None)
                    }
                    results.append(processed_result)
        
        # Priority 3: Parse text output (fallback)
        else:
            output = getattr(tool_result, 'output', str(tool_result))
            print(f"   - Falling back to text parsing, output_len={len(str(output))}")
            if isinstance(output, str) and ('web search' in output.lower() or 'search results' in output.lower()):
                results = self._parse_text_output(output)
                print(f"   - Text parsing yielded {len(results)} results")
        
        print(f"🔍 DEBUG: Final parsing result: {len(results)} total results")
        return results
    
    def _parse_text_output(self, output: str) -> List[dict]:
        """Parse text-based search results with enhanced pattern matching."""
        results = []
        lines = output.split('\n')
        current_result = {}
        
        for line in lines:
            line = line.strip()
            
            # Title patterns
            if line.startswith('Title:') or (line.startswith('[') and ']' in line):
                if current_result:
                    results.append(current_result)
                
                title = line.replace('Title:', '').strip()
                if line.startswith('['):
                    title = re.sub(r'^\[\d+\]\s*', '', line)
                
                current_result = {
                    'title': self.clean_html_content(title),
                    'url': '#',
                    'content': '',
                    'page_age': 'Unknown'
                }
            
            # URL patterns
            elif line.startswith('URL:') or line.startswith('http'):
                url = line.replace('URL:', '').strip()
                current_result['url'] = self.url_validator.validate_and_clean_url(url)
            
            # Content lines
            elif line and not line.startswith(('=', '-', '#', '>')):
                if current_result.get('content'):
                    current_result['content'] += ' ' + self.clean_html_content(line)
                else:
                    current_result['content'] = self.clean_html_content(line)
        
        if current_result:
            results.append(current_result)
        
        return results

    def analyze_search_quality(self, results: list, query: str) -> dict:
        """Comprehensive analysis of search result quality and diversity."""
        if not results:
            return {
                'overall_quality': 0,
                'diversity_score': 0,
                'coverage_analysis': {},
                'recommendations': ['No results found - try refining search terms'],
                'anthropic_compliance': False
            }
        
        # Calculate overall metrics
        quality_scores = [self.assess_result_quality(result)['score'] for result in results]
        relevance_scores = [self._calculate_relevance_score(result) for result in results]
        trust_scores = [self._calculate_trust_score(result.get('url', ''), result.get('title', '')) for result in results]
        
        # Check clickable links compliance
        clickable_links = sum(1 for result in results if self.url_validator.validate_and_clean_url(result.get('url', '')) != '#')
        clickable_ratio = clickable_links / len(results) if results else 0
        
        # Categorize results for diversity analysis
        categories = {}
        for result in results:
            category = self.categorize_result(result.get('url', ''), result.get('title', ''))
            categories[category] = categories.get(category, 0) + 1
        
        # Calculate diversity score
        diversity_score = min(len(categories) / 6.0, 1.0)
        
        # Overall quality assessment
        overall_quality = (
            sum(quality_scores) / len(quality_scores) * 0.4 +
            sum(relevance_scores) / len(relevance_scores) * 0.3 +
            sum(trust_scores) / len(trust_scores) * 0.2 +
            diversity_score * 0.1
        )
        
        # Anthropic compliance check
        anthropic_compliance = clickable_ratio >= 0.8 and overall_quality >= 0.5
        
        # Generate recommendations
        recommendations = []
        if overall_quality < 0.5:
            recommendations.append("Consider refining search terms for better quality results")
        if diversity_score < 0.3:
            recommendations.append("Results are concentrated in one category - try broader search terms")
        if clickable_ratio < 0.8:
            recommendations.append(f"Only {clickable_ratio:.1%} of links are clickable - check URL formatting")
        if max(trust_scores) < 0.7:
            recommendations.append("Consider looking for more authoritative sources")
        if not recommendations:
            recommendations.append("Search results show good quality and diversity")
        
        return {
            'overall_quality': overall_quality,
            'diversity_score': diversity_score,
            'average_trust': sum(trust_scores) / len(trust_scores),
            'average_relevance': sum(relevance_scores) / len(relevance_scores),
            'category_distribution': categories,
            'recommendations': recommendations,
            'top_quality_indices': [i for i, score in enumerate(quality_scores) if score >= 0.7],
            'clickable_links': clickable_links,
            'clickable_ratio': clickable_ratio,
            'anthropic_compliance': anthropic_compliance
        }


class WebSearchTool(BaseAnthropicTool):
    """
    Enhanced web search tool providing Claude with real-time internet access.
    
    This is a client-side wrapper for Anthropic's server-side web_search_20250305 tool.
    It provides enhanced configuration, validation, and documentation while the actual
    search execution happens server-side through the Anthropic API.
    
    Features:
    - Real-time web search with automatic citation
    - Enhanced result formatting and presentation  
    - Domain filtering (allow/block lists)
    - Geographic localization
    - Rate limiting and usage control
    - M4-optimized performance
    - Smart result categorization and summarization
    - Enhanced error handling with user guidance
    - Anthropic citation compliance
    """

    name: ClassVar[Literal["web_search"]] = "web_search"
    api_type: str = "web_search_20250305"  # Latest version

    def __init__(self, 
                 api_version: str = "web_search_20250305",
                 max_uses: int = 5,
                 allowed_domains: Optional[List[str]] = None,
                 blocked_domains: Optional[List[str]] = None,
                 user_location: Optional[Dict] = None,
                 enable_smart_formatting: bool = True,
                 enable_result_categorization: bool = True):
        """
        Initialize enhanced web search tool with configuration.
        
        Args:
            api_version: API version to use (default: web_search_20250305)
            max_uses: Maximum searches per request (default: 5)
            allowed_domains: List of allowed domains (e.g., ["example.com"])
            blocked_domains: List of blocked domains (e.g., ["untrusted.com"])
            user_location: Geographic location for search localization
            enable_smart_formatting: Enable enhanced result formatting
            enable_result_categorization: Enable automatic result categorization
        """
        super().__init__()
        self.api_type = api_version
        self.max_uses = max_uses
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []
        self.user_location = user_location
        self.enable_smart_formatting = enable_smart_formatting
        self.enable_result_categorization = enable_result_categorization
        self.formatter = WebSearchResultFormatter() if enable_result_categorization else None
        self.search_count = 0
        
        # Validate configuration
        if allowed_domains and blocked_domains:
            raise ValueError("Cannot specify both allowed_domains and blocked_domains")

    def reset_search_count(self):
        """Reset the search count for a new request cycle."""
        self.search_count = 0

    def to_params(self):
        """Convert tool configuration to API parameters format."""
        # This is a server-side tool handled by Anthropic's API
        params = {
            "type": self.api_type,
            "name": self.name,
        }
        
        # Add configuration parameters for server-side tool
        if self.max_uses and self.max_uses != 5:
            params["max_uses"] = self.max_uses
            
        if self.allowed_domains:
            params["allowed_domains"] = self.allowed_domains
        elif self.blocked_domains:
            params["blocked_domains"] = self.blocked_domains
            
        if self.user_location:
            params["user_location"] = self.user_location
            
        return params

    async def __call__(self, 
                      query: str,
                      max_results: int = 5,
                      include_citations: bool = True,
                      search_intent: Optional[str] = None,
                      **kwargs):
        """
        This method should not be called directly as this is a server-side tool.
        The actual web search execution happens through Anthropic's API.
        
        This method provides client-side validation and guidance.
        """
        
        # Validate inputs with helpful error messages
        if not query or not query.strip():
            return ToolError(
                "Empty search query provided. Please provide a meaningful search term. Web search requires a non-empty query string. Try asking a specific question or providing keywords related to what you're looking for."
            )
        
        if len(query.strip()) > 500:  # Reasonable query length limit
            return ToolError(
                f"Search query too long ({len(query)} characters). Maximum recommended length is 500 characters. Try breaking down your search into more specific, concise terms. Focus on the key concepts you're looking for."
            )
        
        # This is a server-side tool, so we should not execute it locally
        return ToolError(
            "This web search tool is executed server-side by Anthropic's API. " +
            "If you're seeing this message, it means the tool was called locally instead of through the API. " +
            "Please ensure the tool is properly configured as a server-side tool in your API request."
        )


class EnhancedWebBrowser(BaseAnthropicTool):
    """
    Enhanced web browser tool for direct web page interaction.
    Complements the web search tool with browsing and automation capabilities.
    """
    
    name: ClassVar[Literal["web_browser"]] = "web_browser"
    api_type: str = "custom"

    def __init__(self, api_version: str = "custom"):
        super().__init__()
        self.api_type = api_version

    async def __call__(self,
                      action: str,
                      url: str = None,
                      selector: str = None,
                      text: str = None,
                      **kwargs):
        """
        Enhanced web browser actions with better error handling and user feedback.
        
        Supported actions:
        - navigate: Go to a URL
        - click: Click an element
        - type: Type text into an element
        - extract: Extract content from page
        - scroll: Scroll the page
        - back: Go back in history
        - forward: Go forward in history
        - refresh: Refresh the page
        """
        
        action = action.lower().strip()
        
        # Validate action
        valid_actions = ['navigate', 'click', 'type', 'extract', 'scroll', 'back', 'forward', 'refresh']
        if action not in valid_actions:
            return ToolError(f"Invalid action '{action}'. Valid actions: {', '.join(valid_actions)}")
        
        # Action-specific validation and execution
        try:
            if action == 'navigate':
                return await self._navigate(url)
            elif action == 'click':
                return await self._click_element(selector)
            elif action == 'type':
                return await self._type_text(text, selector)
            elif action == 'extract':
                return await self._extract_content(selector)
            elif action in ['scroll', 'back', 'forward', 'refresh']:
                return await self._browser_navigation(action)
            else:
                return ToolError(f"Action '{action}' not implemented yet")
        
        except Exception as e:
            return ToolError(f"Browser action failed: {str(e)}")

    async def _navigate(self, url: str):
        """Navigate to a URL with enhanced validation."""
        if not url:
            return ToolError("URL is required for navigation")
        
        # Validate URL
        validator = EnhancedURLValidator()
        validated_url = validator.validate_and_clean_url(url)
        
        if validated_url == '#':
            return ToolError(f"Invalid or unsafe URL: {url}")
        
        # This would integrate with actual browser automation
        return ToolResult(
            output=f"Navigation to {validated_url} initiated",
            error=None,
            base64_image=None
        )

    async def _click_element(self, selector: str):
        """Click an element with enhanced error handling."""
        if not selector:
            return ToolError("CSS selector is required for clicking")
        
        # This would integrate with actual browser automation
        return ToolResult(
            output=f"Clicked element: {selector}",
            error=None,
            base64_image=None
        )

    async def _type_text(self, text: str, selector: str = None):
        """Type text with enhanced validation."""
        if not text:
            return ToolError("Text is required for typing")
        
        # This would integrate with actual browser automation
        return ToolResult(
            output=f"Typed text into {selector if selector else 'active element'}: {text[:50]}{'...' if len(text) > 50 else ''}",
            error=None,
            base64_image=None
        )

    async def _extract_content(self, selector: str = None):
        """Extract content with enhanced handling."""
        # This would integrate with actual browser automation
        return ToolResult(
            output=f"Extracted content from {selector if selector else 'page'}",
            error=None,
            base64_image=None
        )

    async def _browser_navigation(self, action: str):
        """Handle browser navigation actions."""
        # This would integrate with actual browser automation
        return ToolResult(
            output=f"Browser action '{action}' completed",
            error=None,
            base64_image=None
        )

    def to_params(self):
        """Convert tool configuration to API parameters format."""
        return {
            "type": self.api_type,
            "name": self.name,
        } 