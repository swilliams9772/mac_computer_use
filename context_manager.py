"""
Model Context Pruning (MCP) module for managing conversation history efficiently.

This module provides functions to:
1. Summarize long conversation histories
2. Prune less relevant messages
3. Compress content based on relevance
4. Track token usage
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from anthropic.types.beta import BetaContentBlockParam, BetaMessageParam


class ConversationManager:
    """Manages conversation history with Model Context Pruning techniques."""
    
    def __init__(
        self, 
        max_context_length: int = 100000,
        max_messages: int = 50,
        prune_threshold: float = 0.7,
        summary_interval: int = 10
    ):
        """
        Initialize the conversation manager.
        
        Args:
            max_context_length: Maximum number of tokens to keep in context
            max_messages: Maximum number of messages to keep before pruning
            prune_threshold: Percentage of max_context_length that triggers pruning
            summary_interval: Number of messages after which to generate a summary
        """
        self.max_context_length = max_context_length
        self.max_messages = max_messages
        self.prune_threshold = prune_threshold
        self.summary_interval = summary_interval
        self.summaries = []
        self.current_tokens = 0
        self.workspace_memory = {}
        
    def estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in a string."""
        # Very rough approximation: 1 token ~= 4 characters for English text
        return len(text) // 4
    
    def should_prune(self, messages: List[BetaMessageParam]) -> bool:
        """Check if conversation history needs pruning."""
        # Check if number of messages exceeds threshold
        if len(messages) > self.max_messages:
            return True
            
        # Estimate total tokens
        total_tokens = 0
        for message in messages:
            if isinstance(message["content"], str):
                total_tokens += self.estimate_tokens(message["content"])
            elif isinstance(message["content"], list):
                for content in message["content"]:
                    if content.get("type") == "text":
                        total_tokens += self.estimate_tokens(content.get("text", ""))
        
        self.current_tokens = total_tokens
        return total_tokens > (self.max_context_length * self.prune_threshold)
    
    def prune_messages(
        self, 
        messages: List[BetaMessageParam],
        retain_recent: int = 5
    ) -> List[BetaMessageParam]:
        """
        Prune messages to reduce context size.
        
        Strategies:
        1. Keep most recent messages intact
        2. Summarize older exchanges
        3. Remove redundant tool outputs
        4. Keep only most relevant information
        
        Args:
            messages: List of messages to prune
            retain_recent: Number of recent messages to keep intact
            
        Returns:
            Pruned message list
        """
        if len(messages) <= retain_recent:
            return messages
            
        # Keep the most recent messages
        recent_messages = messages[-retain_recent:]
        older_messages = messages[:-retain_recent]
        
        # Generate a summary of older messages if we have enough
        if len(older_messages) >= self.summary_interval:
            summary = self._generate_summary(older_messages)
            self.summaries.append(summary)
            
            # Create a system message with the summary
            summary_message = {
                "role": "system",
                "content": f"Previous conversation summary: {summary}"
            }
            
            # Return the summary + recent messages
            return [summary_message] + recent_messages
            
        # If we don't have enough for a summary, just keep a few key older messages
        else:
            # Keep first message (usually contains the original task/question)
            first_message = older_messages[0:1] if older_messages else []
            
            # Keep messages with important decisions or high information density
            important_indices = self._identify_important_messages(older_messages)
            important_messages = [older_messages[i] for i in important_indices if i < len(older_messages)]
            
            return first_message + important_messages + recent_messages
    
    def _identify_important_messages(self, messages: List[BetaMessageParam]) -> List[int]:
        """
        Identify indices of important messages.
        
        Uses heuristics like:
        - Length (longer messages tend to be more information-dense)
        - Presence of decisions or conclusions
        - Questions and their direct answers
        
        Returns:
            List of indices of important messages
        """
        important_indices = []
        
        # Simple heuristic: select longer messages and question-answer pairs
        for i, message in enumerate(messages):
            message_str = ""
            
            # Extract text from message
            if isinstance(message["content"], str):
                message_str = message["content"]
            elif isinstance(message["content"], list):
                for content in message["content"]:
                    if content.get("type") == "text":
                        message_str += content.get("text", "")
            
            # Check if this is a relatively long message (information-dense)
            if len(message_str) > 200:
                important_indices.append(i)
                
            # Check if message contains a question (and include the answer)
            if "?" in message_str and i + 1 < len(messages):
                important_indices.append(i)
                important_indices.append(i + 1)
                
            # Check for decision indicators
            decision_indicators = ["decision", "conclusion", "agreed", "plan", "next steps"]
            if any(indicator in message_str.lower() for indicator in decision_indicators):
                important_indices.append(i)
                
        # Remove duplicates and sort
        return sorted(list(set(important_indices)))
    
    def _generate_summary(self, messages: List[BetaMessageParam]) -> str:
        """
        Generate a concise summary of a message sequence.
        
        This is a simplified implementation that concatenates and condenses.
        In a production system, you would call an LLM to create the summary.
        
        Returns:
            Summary text
        """
        summary_parts = []
        
        for message in messages:
            role = message["role"]
            
            if isinstance(message["content"], str):
                content = message["content"]
                # Add a condensed version
                if len(content) > 100:
                    summary_parts.append(f"{role}: {content[:100]}...")
                else:
                    summary_parts.append(f"{role}: {content}")
            
            elif isinstance(message["content"], list):
                for item in message["content"]:
                    if item.get("type") == "text":
                        text = item.get("text", "")
                        if len(text) > 100:
                            summary_parts.append(f"{role}: {text[:100]}...")
                        else:
                            summary_parts.append(f"{role}: {text}")
        
        return "\n".join(summary_parts)
    
    def add_to_workspace_memory(self, key: str, value: Any) -> None:
        """
        Store information in workspace memory for long-term retrieval.
        
        Args:
            key: Identifier for the information
            value: The information to store
        """
        self.workspace_memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_from_workspace_memory(self, key: str) -> Optional[Any]:
        """
        Retrieve information from workspace memory.
        
        Args:
            key: Identifier for the information to retrieve
            
        Returns:
            The stored information or None if not found
        """
        if key in self.workspace_memory:
            return self.workspace_memory[key]["value"]
        return None
    
    def get_token_usage(self) -> int:
        """Get the current token usage estimate."""
        return self.current_tokens
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of the context manager's state."""
        return {
            "current_tokens": self.current_tokens,
            "max_tokens": self.max_context_length,
            "summary_count": len(self.summaries),
            "workspace_keys": list(self.workspace_memory.keys())
        }


def apply_mcp(messages: List[BetaMessageParam]) -> List[BetaMessageParam]:
    """
    Apply Model Context Pruning to a message list.
    
    This is a convenience function that creates a conversation manager
    and applies pruning if needed.
    
    Args:
        messages: The message list to prune
        
    Returns:
        Pruned message list
    """
    manager = ConversationManager()
    if manager.should_prune(messages):
        return manager.prune_messages(messages)
    return messages 