from typing import Dict, List, Any, Optional
import requests
import json
import os
from urllib.parse import quote_plus

from .base import BaseAnthropicTool, ToolResult, ToolError


class WebSearchTool(BaseAnthropicTool):
    """Tool for searching the web using DuckDuckGo, Google, or Bing."""

    def __init__(self, name="web_search", engine="duckduckgo"):
        self.name = name
        self.engine = engine

    def __call__(self, search_query: str, num_results: int = 5) -> ToolResult:
        """
        Search the web for information.
        
        Args:
            search_query: The search query to look up
            num_results: Number of results to return (max 10)
        
        Returns:
            ToolResult with search results
        """
        try:
            if not search_query or not isinstance(search_query, str):
                raise ToolError("Search query must be a non-empty string")
            
            # Limit number of results
            num_results = min(max(1, num_results), 10)
            
            if self.engine == "duckduckgo":
                return self._search_duckduckgo(search_query, num_results)
            elif self.engine == "google" and os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_CX_ID"):
                return self._search_google(search_query, num_results)
            elif self.engine == "bing" and os.environ.get("BING_API_KEY"):
                return self._search_bing(search_query, num_results)
            else:
                # Default to DuckDuckGo if API keys not found
                return self._search_duckduckgo(search_query, num_results)
        
        except Exception as e:
            error_msg = f"Error during web search: {str(e)}"
            return ToolResult(error=error_msg)

    def _search_duckduckgo(self, query: str, num_results: int) -> ToolResult:
        """Search using DuckDuckGo."""
        try:
            encoded_query = quote_plus(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract abstract if available
            if data.get("Abstract"):
                results.append({
                    "title": "Abstract",
                    "snippet": data.get("Abstract"),
                    "link": data.get("AbstractURL", "")
                })
            
            # Extract related topics
            for topic in data.get("RelatedTopics", [])[:num_results]:
                if "Text" in topic and "FirstURL" in topic:
                    results.append({
                        "title": topic.get("Text", "").split(" - ")[0],
                        "snippet": topic.get("Text", ""),
                        "link": topic.get("FirstURL", "")
                    })
            
            formatted_results = self._format_results(query, results)
            return ToolResult(output=formatted_results)
            
        except Exception as e:
            return ToolResult(error=f"DuckDuckGo search failed: {str(e)}")

    def _search_google(self, query: str, num_results: int) -> ToolResult:
        """Search using Google Custom Search API."""
        try:
            api_key = os.environ.get("GOOGLE_API_KEY")
            cx_id = os.environ.get("GOOGLE_CX_ID")
            
            if not api_key or not cx_id:
                return ToolResult(error="Google API key or CX ID not found in environment variables")
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": cx_id,
                "q": query,
                "num": num_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", "")
                })
            
            formatted_results = self._format_results(query, results)
            return ToolResult(output=formatted_results)
            
        except Exception as e:
            return ToolResult(error=f"Google search failed: {str(e)}")

    def _search_bing(self, query: str, num_results: int) -> ToolResult:
        """Search using Bing Search API."""
        try:
            api_key = os.environ.get("BING_API_KEY")
            
            if not api_key:
                return ToolResult(error="Bing API key not found in environment variables")
            
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": api_key}
            params = {
                "q": query,
                "count": num_results,
                "responseFilter": "Webpages"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("webPages", {}).get("value", []):
                results.append({
                    "title": item.get("name", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("url", "")
                })
            
            formatted_results = self._format_results(query, results)
            return ToolResult(output=formatted_results)
            
        except Exception as e:
            return ToolResult(error=f"Bing search failed: {str(e)}")

    def _format_results(self, query: str, results: List[Dict[str, str]]) -> str:
        """Format the search results in a readable format."""
        if not results:
            return f"No results found for query: {query}"
        
        formatted = f"Search results for: {query}\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   URL: {result['link']}\n\n"
        
        return formatted

    def to_params(self):
        """Return the tool parameters for API calls."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Search the web for information to answer questions about current events, facts, or any other topic.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string", 
                            "description": "The search query to look up on the web"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return (max 10)",
                            "default": 5,
                        }
                    },
                    "required": ["search_query"]
                }
            }
        } 