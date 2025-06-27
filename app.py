"""
Entrypoint for streamlit, see https://docs.streamlit.io/
"""

import asyncio
import base64
import os
import subprocess
import json
import uuid
from datetime import datetime
from enum import StrEnum
from functools import partial
from pathlib import PosixPath
from typing import cast, List, Dict, Any

import streamlit as st
from anthropic import APIResponse
from anthropic.types import (
    TextBlock,
)
from anthropic.types.beta import BetaMessage, BetaTextBlock, BetaToolUseBlock
from anthropic.types.tool_use_block import ToolUseBlock
from streamlit.delta_generator import DeltaGenerator

from loop import (
    PROVIDER_TO_DEFAULT_MODEL_NAME,
    AVAILABLE_MODELS,
    APIProvider,
    sampling_loop,
    model_supports_extended_thinking,
    get_max_tokens_for_model,
    model_supports_token_efficiency,
    model_supports_interleaved_thinking,
    get_recommended_thinking_budget,
    get_beta_flags_for_model,
)
from tools import ToolResult
from dotenv import load_dotenv

load_dotenv()

# Configure page settings - MUST be the very first Streamlit command
st.set_page_config(
    page_title="Claude Computer Use for Mac",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/anthropics/anthropic-quickstarts',
        'Report a bug': 'https://github.com/anthropics/anthropic-quickstarts/issues',
        'About': "# Claude Computer Use for Mac 🚀\n\nEnhanced version with Claude 4 support, Extended Thinking, native macOS integration, and chat preservation."
    }
)

CONFIG_DIR = PosixPath("~/.anthropic").expanduser()
API_KEY_FILE = CONFIG_DIR / "api_key"
SESSION_DIR = CONFIG_DIR / "sessions"

# Enhanced CSS with better visual hierarchy and modern design
STREAMLIT_STYLE = """
<style>
    /* Hide chat input while agent loop is running */
    .stApp[data-teststate=running] .stChatInput textarea,
    .stApp[data-test-script-state=running] .stChatInput textarea {
        display: none;
    }
    
    /* Hide the streamlit deploy button */
    .stDeployButton {
        visibility: hidden;
    }
    
    /* Improved sidebar styling */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Better spacing for sections */
    .section-header {
        font-weight: 600;
        color: #1f2937;
        margin: 1rem 0 0.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    /* Status indicators */
    .status-good { color: #059669; font-weight: 500; }
    .status-warning { color: #d97706; font-weight: 500; }
    .status-error { color: #dc2626; font-weight: 500; }
    
    /* Compact metrics */
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.25rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    /* Better button groups */
    .button-group {
        display: flex;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* Enhanced expandable sections */
    .streamlit-expanderHeader {
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    /* Chat message improvements */
    .stChatMessage {
        margin-bottom: 1rem;
    }
    
    /* Tool output styling */
    .tool-output {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.375rem;
    }
    
    /* Error styling */
    .error-message {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.375rem;
    }
</style>
"""

WARNING_TEXT = ""


class Sender(StrEnum):
    USER = "user"
    BOT = "assistant"
    TOOL = "tool"


class SessionManager:
    """Manage chat sessions with persistence like ChatGPT"""
    
    def __init__(self):
        self.session_dir = SESSION_DIR
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, session_id: str, title: str, messages: List[Dict], metadata: Dict) -> bool:
        """Save current session to file"""
        try:
            session_file = self.session_dir / f"{session_id}.json"
            
            # Enhanced metadata with conversation statistics
            conversation_stats = self._analyze_conversation(messages)
            
            session_data = {
                "id": session_id,
                "title": title,
                "created_at": metadata.get("created_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat(),
                "metadata": {
                    **metadata,
                    "conversation_stats": conversation_stats
                },
                "messages": self._serialize_messages(messages)
            }
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            st.error(f"Failed to save session: {e}")
            return False
    
    def load_session(self, session_id: str) -> tuple[List[Dict], Dict, str]:
        """Load a session by ID"""
        try:
            session_file = self.session_dir / f"{session_id}.json"
            if not session_file.exists():
                return [], {}, ""
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            messages = self._deserialize_messages(session_data.get("messages", []))
            metadata = session_data.get("metadata", {})
            title = session_data.get("title", "Untitled Chat")
            
            return messages, metadata, title
        except Exception as e:
            st.error(f"Failed to load session: {e}")
            return [], {}, ""
    
    def list_sessions(self) -> List[Dict]:
        """List all available sessions"""
        sessions = []
        try:
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    # Extract summary info
                    sessions.append({
                        "id": session_data.get("id", session_file.stem),
                        "title": session_data.get("title", "Untitled Chat"),
                        "created_at": session_data.get("created_at", ""),
                        "updated_at": session_data.get("updated_at", ""),
                        "message_count": len(session_data.get("messages", [])),
                        "model": session_data.get("metadata", {}).get("model", "Unknown"),
                        "file_path": session_file
                    })
                except Exception as e:
                    # Skip corrupted files
                    continue
            
            # Sort by updated time, most recent first
            sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return sessions
        except Exception as e:
            st.error(f"Failed to list sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            session_file = self.session_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
                return True
            return False
        except Exception as e:
            st.error(f"Failed to delete session: {e}")
            return False
    
    def generate_title(self, messages: List[Dict]) -> str:
        """Generate a title from the first user message"""
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    # Take first 50 chars and clean up
                    title = content[:50].strip()
                    if len(content) > 50:
                        title += "..."
                    return title
                elif isinstance(content, list) and content:
                    # Look for text content in list
                    for block in content:
                        if hasattr(block, 'text'):
                            title = block.text[:50].strip()
                            if len(block.text) > 50:
                                title += "..."
                            return title
                        elif isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "")
                            title = text[:50].strip()
                            if len(text) > 50:
                                title += "..."
                            return title
        return f"Chat {datetime.now().strftime('%m/%d %H:%M')}"
    
    def generate_smart_title(self, messages: List[Dict]) -> str:
        """Generate a smart title based on the conversation content and accomplishments"""
        if not messages:
            return f"Chat {datetime.now().strftime('%m/%d %H:%M')}"
        
        # Analyze the conversation for key actions and outcomes
        conversation_summary = self._analyze_conversation_for_title(messages)
        
        # If we found specific actions/accomplishments, use them
        if conversation_summary["smart_title"]:
            return conversation_summary["smart_title"]
        
        # Fallback to the original method
        return self.generate_title(messages)
    
    def _analyze_conversation_for_title(self, messages: List[Dict]) -> Dict:
        """Analyze conversation to extract key accomplishments for smart titling"""
        user_intents = []
        tool_actions = []
        outcomes = []
        
        # Extract user intents and system responses
        for i, msg in enumerate(messages):
            role = msg.get("role", "")
            content = msg.get("content", [])
            
            if role == "user":
                # Extract user intent from the message
                user_text = self._extract_text_from_content(content)
                if user_text:
                    user_intents.append(user_text)
                    
            elif role == "assistant":
                # Look for tool usage patterns
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            tool_name = block.get("name", "")
                            tool_input = block.get("input", {})
                            tool_actions.append(self._categorize_tool_action(tool_name, tool_input))
                        
                        # Extract final outcomes from assistant messages
                        elif isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "")
                            if any(completion_word in text.lower() for completion_word in 
                                 ["completed", "finished", "done", "successfully", "created", "downloaded", "installed"]):
                                outcomes.append(text)
        
        # Generate smart title based on analysis
        smart_title = self._generate_title_from_analysis(user_intents, tool_actions, outcomes)
        
        return {
            "smart_title": smart_title,
            "user_intents": user_intents,
            "tool_actions": tool_actions,
            "outcomes": outcomes
        }
    
    def _extract_text_from_content(self, content) -> str:
        """Extract text content from various content formats"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            texts = []
            for block in content:
                if hasattr(block, 'text'):
                    texts.append(block.text)
                elif isinstance(block, dict) and block.get("type") == "text":
                    texts.append(block.get("text", ""))
            return " ".join(texts)
        return ""
    
    def _categorize_tool_action(self, tool_name: str, tool_input: Dict) -> str:
        """Categorize tool actions for title generation"""
        if tool_name == "computer":
            action = tool_input.get("action", "")
            if action == "screenshot":
                return "screenshot"
            elif action in ["click", "double_click"]:
                return "click_interaction"
            elif action == "type":
                return "text_input"
            elif action == "scroll":
                return "navigation"
                
        elif tool_name == "bash":
            command = tool_input.get("command", "").lower()
            if any(pkg_cmd in command for pkg_cmd in ["brew install", "pip install", "npm install"]):
                return "software_installation"
            elif any(file_cmd in command for file_cmd in ["mkdir", "touch", "cp", "mv"]):
                return "file_management"
            elif any(git_cmd in command for git_cmd in ["git clone", "git pull", "git push"]):
                return "git_operations"
            elif "download" in command or "curl" in command or "wget" in command:
                return "download"
            else:
                return "command_execution"
                
        elif tool_name == "str_replace_based_edit_tool":
            command = tool_input.get("command", "")
            if command == "create":
                return "file_creation"
            elif command in ["str_replace", "str_replace_editor"]:
                return "file_editing"
            elif command == "view":
                return "file_viewing"
                
        elif tool_name == "applescript":
            return "macos_automation"
            
        elif tool_name == "silicon":
            return "system_monitoring"
            
        return f"{tool_name}_usage"
    
    def _generate_title_from_analysis(self, user_intents: List[str], tool_actions: List[str], outcomes: List[str]) -> str:
        """Generate a concise title based on conversation analysis"""
        # Priority 1: Use first user intent if it's concise and clear
        if user_intents:
            first_intent = user_intents[0].strip()
            # Check if the intent is a clear, actionable request
            if len(first_intent) <= 60 and any(action_word in first_intent.lower() for action_word in 
                ["create", "make", "build", "install", "download", "setup", "configure", "fix", "help", "write", "open", "find"]):
                return first_intent
        
        # Priority 2: Categorize based on tool actions
        action_counts = {}
        for action in tool_actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        if action_counts:
            # Find the most common meaningful action
            meaningful_actions = {k: v for k, v in action_counts.items() 
                                if k not in ["screenshot", "click_interaction", "navigation"]}
            
            if meaningful_actions:
                top_action = max(meaningful_actions.items(), key=lambda x: x[1])
                action_titles = {
                    "software_installation": "Software Installation",
                    "file_management": "File Management",
                    "file_creation": "File Creation", 
                    "file_editing": "Code Editing",
                    "git_operations": "Git Operations",
                    "download": "Download Task",
                    "macos_automation": "macOS Automation",
                    "system_monitoring": "System Monitoring",
                    "command_execution": "Terminal Commands"
                }
                return action_titles.get(top_action[0], "Computer Task")
        
        # Priority 3: Look for specific patterns in user intents
        if user_intents:
            combined_intent = " ".join(user_intents).lower()
            
            # Pattern matching for common tasks
            if any(word in combined_intent for word in ["install", "setup", "download"]):
                return "Installation & Setup"
            elif any(word in combined_intent for word in ["create", "make", "build"]):
                return "Creation Task"
            elif any(word in combined_intent for word in ["fix", "debug", "error", "problem"]):
                return "Troubleshooting"
            elif any(word in combined_intent for word in ["open", "launch", "start"]):
                return "Application Launch"
            elif any(word in combined_intent for word in ["find", "search", "locate"]):
                return "Search Task"
            elif any(word in combined_intent for word in ["configure", "setting", "preference"]):
                return "Configuration"
        
        # Fallback: Use first user intent truncated
        if user_intents:
            intent = user_intents[0].strip()
            if len(intent) > 50:
                intent = intent[:47] + "..."
            return intent
            
        return f"Computer Task {datetime.now().strftime('%m/%d %H:%M')}"
    
    def _serialize_messages(self, messages: List[Dict]) -> List[Dict]:
        """Convert messages to JSON-serializable format"""
        serialized = []
        for msg in messages:
            content = msg.get("content", [])
            if isinstance(content, list):
                serialized_content = []
                for block in content:
                    if hasattr(block, '__dict__'):
                        # Handle Anthropic objects
                        block_dict = {"type": block.type}
                        if hasattr(block, 'text'):
                            block_dict["text"] = block.text
                        if hasattr(block, 'name'):
                            block_dict["name"] = block.name
                        if hasattr(block, 'input'):
                            block_dict["input"] = block.input
                        if hasattr(block, 'id'):
                            block_dict["id"] = block.id
                        if hasattr(block, 'thinking'):
                            block_dict["thinking"] = block.thinking
                        if hasattr(block, 'signature'):
                            block_dict["signature"] = block.signature
                        if hasattr(block, 'data'):
                            block_dict["data"] = block.data
                        serialized_content.append(block_dict)
                    elif isinstance(block, dict):
                        serialized_content.append(block)
                    else:
                        serialized_content.append({"type": "text", "text": str(block)})
                serialized.append({"role": msg["role"], "content": serialized_content})
            else:
                serialized.append({"role": msg["role"], "content": str(content)})
        return serialized
    
    def _deserialize_messages(self, messages: List[Dict]) -> List[Dict]:
        """Convert JSON format back to message format"""
        deserialized = []
        for msg in messages:
            content = msg.get("content", [])
            if isinstance(content, list):
                deserialized_content = []
                for block in content:
                    if isinstance(block, dict):
                        block_type = block.get("type", "text")
                        if block_type == "text":
                            deserialized_content.append(TextBlock(type="text", text=block.get("text", "")))
                        else:
                            # Keep other types as dicts for now
                            deserialized_content.append(block)
                    else:
                        deserialized_content.append(block)
                deserialized.append({"role": msg["role"], "content": deserialized_content})
            else:
                deserialized.append({"role": msg["role"], "content": content})
        return deserialized
    
    def _analyze_conversation(self, messages: List[Dict]) -> Dict:
        """Analyze conversation to generate useful statistics"""
        stats = {
            "total_messages": len(messages),
            "user_messages": 0,
            "assistant_messages": 0,
            "tool_uses": 0,
            "thinking_blocks": 0,
            "total_text_length": 0,
            "tools_used": set(),
            "has_images": False,
            "conversation_duration": None
        }
        
        first_timestamp = None
        last_timestamp = None
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", [])
            
            if role == "user":
                stats["user_messages"] += 1
            elif role == "assistant":
                stats["assistant_messages"] += 1
            
            # Analyze content
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        block_type = block.get("type", "")
                        
                        if block_type == "text":
                            text = block.get("text", "")
                            stats["total_text_length"] += len(text)
                        elif block_type == "tool_use":
                            stats["tool_uses"] += 1
                            tool_name = block.get("name", "unknown")
                            stats["tools_used"].add(tool_name)
                        elif block_type in ["thinking", "redacted_thinking"]:
                            stats["thinking_blocks"] += 1
                        elif block_type == "image":
                            stats["has_images"] = True
                    elif hasattr(block, 'text'):
                        stats["total_text_length"] += len(block.text)
            elif isinstance(content, str):
                stats["total_text_length"] += len(content)
        
        # Convert set to list for JSON serialization
        stats["tools_used"] = list(stats["tools_used"])
        
        return stats


def setup_state():
    # Core state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "current_session_title" not in st.session_state:
        st.session_state.current_session_title = None
    if "session_manager" not in st.session_state:
        st.session_state.session_manager = SessionManager()
    
    # UI state
    if "sidebar_section" not in st.session_state:
        st.session_state.sidebar_section = "model"  # Default section
    if "show_advanced_settings" not in st.session_state:
        st.session_state.show_advanced_settings = False
    if "ui_compact_mode" not in st.session_state:
        st.session_state.ui_compact_mode = False
    
    # Session settings
    if "auto_save_enabled" not in st.session_state:
        st.session_state.auto_save_enabled = True
    if "smart_naming_enabled" not in st.session_state:
        st.session_state.smart_naming_enabled = True
    if "conversation_completed" not in st.session_state:
        st.session_state.conversation_completed = False
    if "session_widget_key_counter" not in st.session_state:
        st.session_state.session_widget_key_counter = 0
    
    # API and model settings
    if "api_key" not in st.session_state:
        st.session_state.api_key = load_from_storage("api_key") or os.getenv("ANTHROPIC_API_KEY", "")
    if "provider" not in st.session_state:
        provider_str = os.getenv("API_PROVIDER", "anthropic")
        # Ensure provider is always an APIProvider enum, not a string
        if isinstance(provider_str, str):
            try:
                st.session_state.provider = APIProvider(provider_str.lower())
            except ValueError:
                st.session_state.provider = APIProvider.ANTHROPIC
        else:
            st.session_state.provider = provider_str or APIProvider.ANTHROPIC
    if "provider_radio" not in st.session_state:
        st.session_state.provider_radio = st.session_state.provider.value
    if "model" not in st.session_state:
        _reset_model()
    if "auth_validated" not in st.session_state:
        st.session_state.auth_validated = False
    
    # Tool and response state
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "tools" not in st.session_state:
        st.session_state.tools = {}
    
    # Advanced settings
    if "only_n_most_recent_images" not in st.session_state:
        st.session_state.only_n_most_recent_images = 3
    if "custom_system_prompt" not in st.session_state:
        st.session_state.custom_system_prompt = load_from_storage("system_prompt") or ""
    if "hide_images" not in st.session_state:
        st.session_state.hide_images = False
    if "api_timeout" not in st.session_state:
        st.session_state.api_timeout = 120
    
    # Extended thinking settings
    if "enable_extended_thinking" not in st.session_state:
        st.session_state.enable_extended_thinking = False
    if "thinking_budget_tokens" not in st.session_state:
        st.session_state.thinking_budget_tokens = 10000
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = None
    if "enable_interleaved_thinking" not in st.session_state:
        st.session_state.enable_interleaved_thinking = True
    
    # Performance and monitoring
    if "tool_usage_stats" not in st.session_state:
        st.session_state.tool_usage_stats = {}
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    if "current_tool_execution" not in st.session_state:
        st.session_state.current_tool_execution = None
    if "m4_performance_data" not in st.session_state:
        st.session_state.m4_performance_data = {
            "thermal_state": "Unknown",
            "cpu_usage": "Unknown", 
            "memory_usage": "Unknown",
            "last_updated": None
        }
    
    # Test case features
    if "test_case_file" not in st.session_state:
        st.session_state.test_case_file = None
    if "test_cases" not in st.session_state:
        st.session_state.test_cases = []
    if "current_test_case" not in st.session_state:
        st.session_state.current_test_case = None
    if "test_execution_log" not in st.session_state:
        st.session_state.test_execution_log = []
    if "auto_test_mode" not in st.session_state:
        st.session_state.auto_test_mode = False
    if "test_execution_results" not in st.session_state:
        st.session_state.test_execution_results = []
    
    # Debug features
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    if "screenshot_history" not in st.session_state:
        st.session_state.screenshot_history = []
    if "coordinate_overlay" not in st.session_state:
        st.session_state.coordinate_overlay = False


def _reset_model():
    st.session_state.model = PROVIDER_TO_DEFAULT_MODEL_NAME[
        cast(APIProvider, st.session_state.provider)
    ]


def start_new_chat():
    """Start a new chat session"""
    # Auto-save current session if it has messages
    if st.session_state.messages and st.session_state.auto_save_enabled:
        auto_save_current_session()
    
    # Clear widget states to prevent conflicts
    clear_session_widget_states()
    
    # Clear current session
    st.session_state.messages = []
    st.session_state.current_session_id = None
    st.session_state.current_session_title = None
    st.session_state.conversation_completed = False
    st.session_state.tool_usage_stats = {}
    
    # Clear tool and response state to prevent KeyError issues
    st.session_state.tools = {}
    st.session_state.responses = {}
    
    st.rerun()


def auto_save_current_session(force_smart_naming: bool = False):
    """Auto-save current session if it has messages"""
    if not st.session_state.messages:
        return
    
    if not st.session_state.current_session_id:
        st.session_state.current_session_id = str(uuid.uuid4())
    
    # Smart naming logic
    should_update_title = (
        not st.session_state.current_session_title or 
        st.session_state.current_session_title.startswith("Chat ") or
        force_smart_naming or
        (st.session_state.smart_naming_enabled and st.session_state.conversation_completed)
    )
    
    if should_update_title:
        if st.session_state.smart_naming_enabled and len(st.session_state.messages) >= 3:
            # Use smart naming for longer conversations
            st.session_state.current_session_title = st.session_state.session_manager.generate_smart_title(st.session_state.messages)
        else:
            # Fallback to basic naming
            st.session_state.current_session_title = st.session_state.session_manager.generate_title(st.session_state.messages)
    
    metadata = {
        "model": st.session_state.model,
        "provider": st.session_state.provider,
        "thinking_enabled": st.session_state.enable_extended_thinking,
        "thinking_budget": st.session_state.thinking_budget_tokens,
        "created_at": getattr(st.session_state, "session_created_at", datetime.now().isoformat()),
        "tool_usage_stats": st.session_state.tool_usage_stats,
        "smart_naming_enabled": st.session_state.smart_naming_enabled,
        "conversation_completed": st.session_state.conversation_completed,
    }
    
    if not hasattr(st.session_state, "session_created_at"):
        st.session_state.session_created_at = datetime.now().isoformat()
        metadata["created_at"] = st.session_state.session_created_at
    
    st.session_state.session_manager.save_session(
        st.session_state.current_session_id,
        st.session_state.current_session_title,
        st.session_state.messages,
        metadata
    )


def load_chat_session(session_id: str):
    """Load a specific chat session"""
    # Auto-save current session first
    if st.session_state.messages and st.session_state.auto_save_enabled:
        auto_save_current_session()
    
    messages, metadata, title = st.session_state.session_manager.load_session(session_id)
    
    if messages:
        # Clear widget state conflicts before loading
        clear_session_widget_states()
        
        st.session_state.messages = messages
        st.session_state.current_session_id = session_id
        st.session_state.current_session_title = title
        st.session_state.session_created_at = metadata.get("created_at", datetime.now().isoformat())
        
        # Stage session settings for next rerun (to avoid widget state conflicts)
        staged_updates = {}
        if "model" in metadata:
            staged_updates["model"] = metadata["model"]
        if "provider" in metadata:
            # Ensure provider is converted to enum if it's stored as string
            provider_value = metadata["provider"]
            if isinstance(provider_value, str):
                try:
                    provider_value = APIProvider(provider_value.lower())
                except ValueError:
                    provider_value = APIProvider.ANTHROPIC
            staged_updates["provider"] = provider_value
            staged_updates["provider_radio"] = provider_value.value
        if "thinking_enabled" in metadata:
            staged_updates["enable_extended_thinking"] = metadata["thinking_enabled"]
        if "thinking_budget" in metadata:
            staged_updates["thinking_budget_tokens"] = metadata["thinking_budget"]
        if "tool_usage_stats" in metadata:
            staged_updates["tool_usage_stats"] = metadata["tool_usage_stats"]
        if "smart_naming_enabled" in metadata:
            staged_updates["smart_naming_enabled"] = metadata["smart_naming_enabled"]
        if "conversation_completed" in metadata:
            staged_updates["conversation_completed"] = metadata["conversation_completed"]
        
        # Store staged updates and trigger rerun
        if staged_updates:
            st.session_state["__staged_session_updates"] = staged_updates
        
        # Reset conversation completion status when loading a session
        st.session_state.conversation_completed = False
        
        st.success(f"✅ Loaded chat: {title}")
        st.rerun()


def clean_orphaned_tool_references(messages: List[Dict]) -> List[Dict]:
    """Remove tool_result blocks that reference non-existent tools."""
    cleaned_messages = []
    for message in messages:
        if isinstance(message.get("content"), list):
            cleaned_content = []
            for block in message["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    tool_id = block.get("tool_use_id")
                    if tool_id and tool_id in st.session_state.tools:
                        cleaned_content.append(block)
                    # Skip orphaned tool_result blocks
                else:
                    cleaned_content.append(block)
            
            if cleaned_content:  # Only add message if it has content
                cleaned_message = message.copy()
                cleaned_message["content"] = cleaned_content
                cleaned_messages.append(cleaned_message)
        else:
            cleaned_messages.append(message)
    
    return cleaned_messages


def clear_session_widget_states():
    """Clear session-related widget states to prevent conflicts"""
    # Increment counter to ensure unique widget keys
    st.session_state.session_widget_key_counter += 1
    
    # Clear any rename dialog states
    if hasattr(st.session_state, "show_rename_input"):
        st.session_state.show_rename_input = False
    
    # Clear any search states
    if hasattr(st.session_state, "search_active"):
        st.session_state.search_active = False
    if hasattr(st.session_state, "search_query"):
        st.session_state.search_query = ""
    
    # Clear responses and tools cache for clean state
    st.session_state.responses = {}
    st.session_state.tools = {}
    
    # Reset session timing
    st.session_state.session_start_time = datetime.now()
    st.session_state.current_tool_execution = None


def render_enhanced_sidebar():
    """Render the enhanced, well-organized sidebar."""
    with st.sidebar:
        # Header with current model status
        render_sidebar_header()
        
        # Main navigation tabs
        tab1, tab2, tab3 = st.tabs(["🎯 Setup", "💬 Chats", "🔧 Tools"])
        
        with tab1:
            render_model_configuration()
            render_session_settings()
            
        with tab2:
            render_chat_management()
            
        with tab3:
            render_tools_and_monitoring()


def render_sidebar_header():
    """Render the sidebar header with status."""
    current_model = st.session_state.get('model', 'Not selected')
    
    # Model status with visual indicator
    if model_supports_extended_thinking(current_model):
        st.success(f"🎯 **{current_model}**")
        if model_supports_interleaved_thinking(current_model):
            st.caption("✨ Extended + Interleaved Thinking")
        else:
            st.caption("✨ Extended Thinking")
    else:
        st.info(f"🎯 **{current_model}**")
        st.caption("Standard model")
    
    # Quick stats
    if st.session_state.tool_usage_stats:
        total_tools = sum(st.session_state.tool_usage_stats.values())
        st.caption(f"🔧 {total_tools} tools used • 💬 {len(st.session_state.messages)} messages")
    
    st.divider()


def render_model_configuration():
    """Render the model configuration section."""
    st.subheader("🤖 Model & API")
    
    # Provider selection
    def _reset_api_provider():
        if "provider" not in st.session_state:
            st.session_state.provider = APIProvider.ANTHROPIC
        
        # Convert string value back to enum for internal use
        if hasattr(st.session_state, 'provider_radio'):
            provider_enum = APIProvider(st.session_state.provider_radio)
            if provider_enum != st.session_state.provider:
                _reset_model()
                st.session_state.provider = provider_enum
                st.session_state.auth_validated = False

    # Ensure provider_radio is initialized with string value, not enum
    if "provider_radio" not in st.session_state:
        st.session_state.provider_radio = st.session_state.provider.value

    provider_options = [option.value for option in APIProvider]
    st.radio(
        "Provider",
        options=provider_options,
        key="provider_radio",
        format_func=lambda x: x.title(),
        on_change=_reset_api_provider,
        horizontal=True
    )

    # API Key
    if st.session_state.provider == APIProvider.ANTHROPIC:
        st.text_input(
            "API Key",
            type="password",
            key="api_key",
            on_change=lambda: save_to_storage("api_key", st.session_state.api_key),
            help="Your Anthropic API key"
        )

    # Model selection with enhanced UI
    available_models = AVAILABLE_MODELS.get(st.session_state.provider, [])
    model_options = [model[0] for model in available_models]
    model_descriptions = {model[0]: model[1] for model in available_models}
    
    if st.session_state.model not in model_options and model_options:
        st.session_state.model = model_options[0]
    
    # Group models by type for better organization
    claude_4_models = [m for m in model_options if "claude-4" in m or "opus-4" in m or "sonnet-4" in m]
    claude_3_models = [m for m in model_options if "claude-3" in m and "claude-4" not in m]
    other_models = [m for m in model_options if m not in claude_4_models and m not in claude_3_models]
    
    # Model selection with grouping
    if claude_4_models:
        st.markdown("**🧠 Claude 4 (Recommended)**")
        for model in claude_4_models:
            if st.button(
                f"{model.replace('claude-', '').replace('-20250514', '')}",
                key=f"select_{model}",
                use_container_width=True,
                type="primary" if model == st.session_state.model else "secondary"
            ):
                st.session_state.model = model
                st.session_state.max_tokens = None
                st.rerun()
    
    if claude_3_models:
        st.markdown("**⚡ Claude 3 Series**")
        for model in claude_3_models:
            if st.button(
                f"{model.replace('claude-', '').replace('-20241022', '').replace('-20250219', '')}",
                key=f"select_{model}",
                use_container_width=True,
                type="primary" if model == st.session_state.model else "secondary"
            ):
                st.session_state.model = model
                st.session_state.max_tokens = None
                st.rerun()
    
    # Current model info
    max_tokens_for_model = get_max_tokens_for_model(st.session_state.model)
    st.caption(f"📊 Max tokens: {max_tokens_for_model:,}")
    
    # Extended thinking configuration (only for supported models)
    if model_supports_extended_thinking(st.session_state.model):
        with st.expander("🧠 Thinking Settings", expanded=False):
            st.checkbox(
                "Enable Extended Thinking",
                key="enable_extended_thinking",
                help="Enable step-by-step reasoning"
            )
            
            if model_supports_interleaved_thinking(st.session_state.model):
                st.checkbox(
                    "Interleaved Thinking",
                    key="enable_interleaved_thinking",
                    value=True,
                    help="Think between tool calls"
                )
            
            if st.session_state.enable_extended_thinking:
                st.slider(
                    "Thinking Budget",
                    min_value=1024,
                    max_value=32000,
                    value=st.session_state.thinking_budget_tokens,
                    step=1024,
                    key="thinking_budget_tokens",
                    help="Tokens for reasoning process"
                )


def render_session_settings():
    """Render session and preference settings."""
    with st.expander("⚙️ Preferences", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Auto-save chats", key="auto_save_enabled")
            st.checkbox("Smart naming", key="smart_naming_enabled") 
            st.checkbox("Hide screenshots", key="hide_images")
            
        with col2:
            st.checkbox("Compact UI", key="ui_compact_mode")
            st.checkbox("Debug mode", key="debug_mode")
        
        # Advanced settings
        if st.session_state.show_advanced_settings:
            st.number_input(
                "API Timeout (s)",
                min_value=30,
                max_value=300,
                value=120,
                key="api_timeout"
            )
            
            st.number_input(
                "Image Cache",
                min_value=0,
                max_value=10,
                value=st.session_state.only_n_most_recent_images,
                key="only_n_most_recent_images"
            )
            
            st.text_area(
                "Custom System Prompt",
                key="custom_system_prompt",
                height=100,
                on_change=lambda: save_to_storage("system_prompt", st.session_state.custom_system_prompt)
            )
        
        if st.button("⚙️ Advanced Settings", use_container_width=True):
            st.session_state.show_advanced_settings = not st.session_state.show_advanced_settings
            st.rerun()


def render_chat_management():
    """Render chat history and session management."""
    st.subheader("💬 Chat History")
    
    # New chat button
    if st.button("🆕 New Chat", type="primary", use_container_width=True):
        start_new_chat()
    
    # Current session info
    if st.session_state.current_session_title:
        st.info(f"📝 **{st.session_state.current_session_title}**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save", use_container_width=True):
                auto_save_current_session()
                st.success("Saved!")
        with col2:
            if st.button("✏️ Rename", use_container_width=True):
                st.session_state.show_rename_input = True
        
        # Rename dialog
        if getattr(st.session_state, "show_rename_input", False):
            new_title = st.text_input("New title:", value=st.session_state.current_session_title)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Save"):
                    st.session_state.current_session_title = new_title
                    auto_save_current_session()
                    st.session_state.show_rename_input = False
                    st.rerun()
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.show_rename_input = False
                    st.rerun()
    
    # Session list
    sessions = st.session_state.session_manager.list_sessions()
    
    if sessions:
        # Filter options
        view_option = st.selectbox(
            "View",
            ["Recent (10)", "All", "This Week", "By Model"],
            key="session_view"
        )
        
        # Apply filters
        filtered_sessions = sessions
        if view_option == "Recent (10)":
            filtered_sessions = sessions[:10]
        elif view_option == "This Week":
            from datetime import timedelta
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            filtered_sessions = [s for s in sessions if s.get("updated_at", "") >= week_ago]
        
        # Display sessions
        for i, session in enumerate(filtered_sessions):
            if session["id"] == st.session_state.current_session_id:
                continue
            
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    session["title"],
                    key=f"load_{session['id']}_{i}",
                    use_container_width=True,
                    help=f"Model: {session.get('model', 'Unknown')} • {session.get('message_count', 0)} messages"
                ):
                    load_chat_session(session["id"])
            with col2:
                if st.button("🗑️", key=f"del_{session['id']}_{i}"):
                    if st.session_state.session_manager.delete_session(session["id"]):
                        st.rerun()
    else:
        st.info("No saved chats yet")
    
    # Export/Import
    with st.expander("📤 Backup", expanded=False):
        if st.button("Export All", use_container_width=True):
            # Export logic here
            st.success("Exported!")


def render_tools_and_monitoring():
    """Render tools and system monitoring."""
    st.subheader("🔧 Tools & System")
    
    # Test case manager
    if st.checkbox("🧪 Test Case Manager", key="show_test_manager"):
        uploaded_file = st.file_uploader("Upload Test CSV", type=['csv'])
        if uploaded_file:
            test_cases = load_test_cases_from_csv(uploaded_file)
            if test_cases:
                st.session_state.test_cases = test_cases
                st.success(f"✅ {len(test_cases)} test cases loaded")
    
    # Performance monitoring
    if st.checkbox("⚡ Performance Monitor", key="show_perf_monitor"):
        if st.button("🔄 Update", use_container_width=True):
            with st.spinner("Checking..."):
                perf_data = asyncio.run(monitor_m4_performance())
                st.session_state.m4_performance_data = perf_data
        
        perf_data = st.session_state.m4_performance_data
        thermal_status = perf_data.get('thermal_state', 'Unknown')
        
        if thermal_status == "Normal":
            st.success(f"🌡️ {thermal_status}")
        elif thermal_status in ["Warning", "Critical"]:
            st.warning(f"🌡️ {thermal_status}")
        else:
            st.info(f"🌡️ {thermal_status}")
    
    # Tool usage stats
    if st.session_state.tool_usage_stats:
        with st.expander("📊 Tool Usage", expanded=False):
            for tool, count in st.session_state.tool_usage_stats.items():
                st.write(f"• {tool}: {count} uses")
    
    # Quick actions
    st.divider()
    if st.button("🔄 Reset App", type="secondary", use_container_width=True):
        st.session_state.clear()
        setup_state()
        st.rerun()


async def main():
    """Enhanced main function with better UI."""
    setup_state()
    
    # Handle staged session updates before creating any widgets
    if "__staged_session_updates" in st.session_state:
        staged_updates = st.session_state.pop("__staged_session_updates")
        for key, value in staged_updates.items():
            st.session_state[key] = value
        # Reset auth validation to ensure proper provider switching
        st.session_state.auth_validated = False

    st.markdown(STREAMLIT_STYLE, unsafe_allow_html=True)

    # Enhanced header
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.title("🚀 Claude Computer Use")
        st.caption("Enhanced for Mac with Claude 4 & Extended Thinking")
    
    with col2:
        # Quick model status
        current_model = st.session_state.get('model', 'Not selected')
        if model_supports_extended_thinking(current_model):
            st.success(f"🧠 {current_model.replace('claude-', '').replace('-20250514', '')}")
        else:
            st.info(f"🎯 {current_model.replace('claude-', '').replace('-20241022', '')}")
    
    with col3:
        # Quick stats or status
        if st.session_state.current_tool_execution:
            st.warning(f"⚡ {st.session_state.current_tool_execution}")
        else:
            total_tools = sum(st.session_state.tool_usage_stats.values()) if st.session_state.tool_usage_stats else 0
            if total_tools > 0:
                st.metric("Tools", total_tools)
            else:
                st.success("Ready 🚀")

    # Enhanced sidebar
    render_enhanced_sidebar()

    # Auth validation
    if not st.session_state.auth_validated:
        if auth_error := validate_auth(st.session_state.provider, st.session_state.api_key):
            st.error(f"⚠️ **Authentication Required**\n\n{auth_error}")
            st.info("💡 Please configure your API key in the sidebar to continue.")
            return
        else:
            st.session_state.auth_validated = True

    # Main chat interface
    chat, logs = st.tabs(["💬 Chat", "📋 HTTP Logs"])
    
    # Chat input
    new_message = st.chat_input("Ask Claude to help with your Mac...")

    with chat:
        # Clean up orphaned tool references before rendering
        st.session_state.messages = clean_orphaned_tool_references(st.session_state.messages)
        
        # Render chat messages with enhanced styling
        for message in st.session_state.messages:
            if isinstance(message["content"], str):
                _render_message(message["role"], message["content"])
            elif isinstance(message["content"], list):
                for block in message["content"]:
                    if isinstance(block, dict) and block["type"] == "tool_result":
                        # Safety check for missing tool results
                        tool_id = block["tool_use_id"]
                        if tool_id in st.session_state.tools:
                            _render_message(Sender.TOOL, st.session_state.tools[tool_id])
                        else:
                            # Handle missing tool result gracefully
                            st.warning(f"⚠️ Tool result missing for ID: {tool_id}")
                            if st.session_state.debug_mode:
                                st.code(f"Missing tool result: {block}")
                    elif isinstance(block, dict) and block.get("type") in ["thinking", "redacted_thinking"]:
                        _render_message(message["role"], block)
                    else:
                        _render_message(message["role"], cast(BetaTextBlock | BetaToolUseBlock, block))

        # Render HTTP logs
        for identity, response in st.session_state.responses.items():
            _render_api_response(response, identity, logs)

        # Handle new messages
        if new_message:
            st.session_state.messages.append({
                "role": Sender.USER,
                "content": [TextBlock(type="text", text=new_message)],
            })
            _render_message(Sender.USER, new_message)
            
            if st.session_state.auto_save_enabled and len(st.session_state.messages) > 1:
                auto_save_current_session()

        # Process messages
        try:
            most_recent_message = st.session_state["messages"][-1]
        except IndexError:
            return

        if most_recent_message["role"] is not Sender.USER:
            return

        # Enhanced loading state
        with st.spinner("🤖 Claude is thinking..."):
            try:
                st.session_state.messages = await sampling_loop(
                    system_prompt_suffix=st.session_state.custom_system_prompt,
                    model=st.session_state.model,
                    provider=st.session_state.provider,
                    messages=st.session_state.messages,
                    output_callback=partial(_render_message, Sender.BOT),
                    tool_output_callback=partial(_tool_output_callback, tool_state=st.session_state.tools),
                    api_response_callback=partial(_api_response_callback, tab=logs, response_state=st.session_state.responses),
                    api_key=st.session_state.api_key,
                    only_n_most_recent_images=st.session_state.only_n_most_recent_images,
                    max_tokens=st.session_state.max_tokens,
                    enable_extended_thinking=st.session_state.enable_extended_thinking,
                    thinking_budget_tokens=st.session_state.thinking_budget_tokens,
                    enable_interleaved_thinking=getattr(st.session_state, 'enable_interleaved_thinking', False),
                    api_timeout=st.session_state.api_timeout,
                )
                
                st.session_state.conversation_completed = True
                
                if st.session_state.auto_save_enabled:
                    auto_save_current_session()
                    
            except TimeoutError as e:
                st.error(f"⏱️ **Request timed out:** {str(e)}")
                with st.expander("💡 **Solutions**", expanded=True):
                    st.markdown("""
                    - **Increase timeout:** Go to Advanced Settings and increase API timeout
                    - **Reduce thinking budget:** Lower the thinking budget in model settings
                    - **Simplify request:** Break complex tasks into smaller steps
                    - **Check connection:** Verify your internet connection
                    """)
            except Exception as e:
                st.error(f"❌ **Error:** {str(e)}")
                with st.expander("🔍 **Troubleshooting**", expanded=False):
                    st.markdown("""
                    - Check your API key is valid
                    - Verify model availability
                    - Try refreshing the page
                    - Check the HTTP logs for details
                    """)
                    import traceback
                    st.code(traceback.format_exc())


def validate_auth(provider: APIProvider, api_key: str | None):
    if provider == APIProvider.ANTHROPIC:
        if not api_key:
            return "Enter your Anthropic API key in the sidebar to continue."
    if provider == APIProvider.BEDROCK:
        import boto3

        if not boto3.Session().get_credentials():
            return "You must have AWS credentials set up to use the Bedrock API."
    if provider == APIProvider.VERTEX:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError

        if not os.environ.get("CLOUD_ML_REGION"):
            return "Set the CLOUD_ML_REGION environment variable to use the Vertex API."
        try:
            google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        except DefaultCredentialsError:
            return "Your google cloud credentials are not set up correctly."


def load_from_storage(filename: str) -> str | None:
    """Load data from a file in the storage directory."""
    try:
        file_path = CONFIG_DIR / filename
        if file_path.exists():
            data = file_path.read_text().strip()
            if data:
                return data
    except Exception as e:
        st.write(f"Debug: Error loading {filename}: {e}")
    return None


def save_to_storage(filename: str, data: str) -> None:
    """Save data to a file in the storage directory."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        file_path = CONFIG_DIR / filename
        file_path.write_text(data)
        # Ensure only user can read/write the file
        file_path.chmod(0o600)
    except Exception as e:
        st.write(f"Debug: Error saving {filename}: {e}")


def _api_response_callback(
    response: APIResponse[BetaMessage],
    tab: DeltaGenerator,
    response_state: dict[str, APIResponse[BetaMessage]],
):
    """
    Handle an API response by storing it to state and rendering it.
    """
    response_id = datetime.now().isoformat()
    response_state[response_id] = response
    _render_api_response(response, response_id, tab)


def _tool_output_callback(
    tool_output: ToolResult, tool_id: str, tool_state: dict[str, ToolResult]
):
    """Handle a tool output by storing it to state and rendering it."""
    tool_state[tool_id] = tool_output
    
    # Track tool usage statistics
    tool_name = getattr(tool_output, 'tool_name', 'unknown')
    if tool_name in st.session_state.tool_usage_stats:
        st.session_state.tool_usage_stats[tool_name] += 1
    else:
        st.session_state.tool_usage_stats[tool_name] = 1
    
    # Clear current tool execution status
    st.session_state.current_tool_execution = None
    
    _render_message(Sender.TOOL, tool_output)


def _render_api_response(
    response: APIResponse[BetaMessage], response_id: str, tab: DeltaGenerator
):
    """Render an API response to a streamlit tab"""
    with tab:
        with st.expander(f"Request/Response ({response_id})"):
            newline = "\n\n"
            st.markdown(
                f"`{response.http_request.method} {response.http_request.url}`{newline}{newline.join(f'`{k}: {v}`' for k, v in response.http_request.headers.items())}"
            )
            st.json(response.http_request.read().decode())
            st.markdown(
                f"`{response.http_response.status_code}`{newline}{newline.join(f'`{k}: {v}`' for k, v in response.headers.items())}"
            )
            st.json(response.http_response.text)


def _render_message(
    sender: Sender,
    message: str | BetaTextBlock | BetaToolUseBlock | ToolResult,
):
    """Convert input from the user or output from the agent to a streamlit message."""
    # streamlit's hotreloading breaks isinstance checks, so we need to check for class names
    is_tool_result = not isinstance(message, str) and (
        isinstance(message, ToolResult)
        or message.__class__.__name__ == "ToolResult"
        or message.__class__.__name__ == "CLIResult"
    )
    
    # Check for thinking blocks
    is_thinking_block = (hasattr(message, 'type') and getattr(message, 'type') == 'thinking') or \
                       (isinstance(message, dict) and message.get('type') == 'thinking')
    is_redacted_thinking = (hasattr(message, 'type') and getattr(message, 'type') == 'redacted_thinking') or \
                          (isinstance(message, dict) and message.get('type') == 'redacted_thinking')
    
    if not message or (
        is_tool_result
        and st.session_state.hide_images
        and not hasattr(message, "error")
        and not hasattr(message, "output")
    ):
        return
        
    with st.chat_message(sender):
        if is_thinking_block:
            # Enhanced thinking block rendering with better formatting
            thinking_content = getattr(message, 'thinking', '')
            # Estimate token count for thinking content (rough approximation)
            estimated_tokens = len(thinking_content.split()) * 1.3 if thinking_content else 0
            
            with st.expander(f"🧠 Claude's Thinking Process (~{int(estimated_tokens)} tokens)", expanded=False):
                if thinking_content:
                    # Better formatting for thinking content
                    st.markdown("**Internal Reasoning:**")
                    with st.container():
                        st.markdown(thinking_content, unsafe_allow_html=False)
                else:
                    st.info("Thinking content not available (may be summarized)")
                if hasattr(message, 'signature'):
                    st.caption("✅ Verified thinking block")
        elif is_redacted_thinking:
            # Enhanced redacted thinking blocks
            with st.expander("🧠 Claude's Thinking Process (Redacted)", expanded=False):
                st.info("🔒 Some of Claude's internal reasoning has been automatically encrypted for safety reasons. This doesn't affect the quality of responses.")
        elif is_tool_result:
            message = cast(ToolResult, message)
            
            # Enhanced tool result rendering with better formatting
            if message.output:
                if message.__class__.__name__ == "CLIResult":
                    st.markdown("**💻 Command Output:**")
                    st.code(message.output, language="bash")
                else:
                    # Check if output looks like structured data
                    output = message.output
                    if output.startswith('{') or output.startswith('['):
                        try:
                            import json
                            parsed = json.loads(output)
                            st.markdown("**📊 Structured Output:**")
                            st.json(parsed)
                        except:
                            st.markdown("**📄 Tool Output:**")
                            st.markdown(output)
                    elif '===' in output or 'INFORMATION' in output.upper():
                        # Structured report-like output
                        st.markdown("**📋 Report:**")
                        # Split by sections and format nicely
                        sections = output.split('===')
                        for i, section in enumerate(sections):
                            if section.strip():
                                if i == 0:
                                    st.markdown(section.strip())
                                else:
                                    # Extract section title and content
                                    lines = section.strip().split('\n')
                                    if lines:
                                        title = lines[0].strip()
                                        content = '\n'.join(lines[1:]).strip()
                                        if title:
                                            st.markdown(f"**{title}**")
                                        if content:
                                            if any(bullet in content for bullet in ['•', '-', '*']):
                                                st.markdown(content)
                                            else:
                                                st.text(content)
                    else:
                        st.markdown("**📄 Tool Output:**")
                        st.markdown(output)
                        
            if message.error:
                st.error(f"**❌ Error:** {message.error}")
                
            if message.base64_image and not st.session_state.hide_images:
                st.markdown("**📸 Screenshot:**")
                st.image(base64.b64decode(message.base64_image))
                
        elif isinstance(message, BetaTextBlock) or isinstance(message, TextBlock):
            st.write(message.text)
        elif isinstance(message, BetaToolUseBlock) or isinstance(message, ToolUseBlock):
            # Enhanced tool use display with better formatting
            tool_name = message.name
            tool_input = message.input
            
            # Get tool emoji/icon
            tool_icons = {
                'computer': '🖥️',
                'bash': '💻', 
                'str_replace_based_edit_tool': '📝',
                'applescript': '🍎',
                'silicon': '⚡'
            }
            
            icon = tool_icons.get(tool_name, '🔧')
            
            with st.expander(f"{icon} **{tool_name.replace('_', ' ').title()}**", expanded=True):
                st.markdown("**Input Parameters:**")
                
                # Format input based on tool type
                if tool_name == 'computer':
                    action = tool_input.get('action', 'Unknown')
                    st.write(f"• **Action:** {action}")
                    if 'coordinate' in tool_input:
                        st.write(f"• **Coordinate:** {tool_input['coordinate']}")
                    if 'text' in tool_input:
                        st.write(f"• **Text:** `{tool_input['text']}`")
                elif tool_name == 'bash':
                    command = tool_input.get('command', '')
                    st.code(command, language="bash")
                elif tool_name == 'str_replace_based_edit_tool':
                    st.write(f"• **Command:** {tool_input.get('command', 'Unknown')}")
                    if 'path' in tool_input:
                        st.write(f"• **File:** `{tool_input['path']}`")
                    if 'file_text' in tool_input:
                        st.write("• **Content Preview:**")
                        content = tool_input['file_text']
                        if len(content) > 200:
                            st.code(content[:200] + "...", language="python")
                        else:
                            st.code(content, language="python")
                    if 'old_str' in tool_input:
                        st.write(f"• **Old Text:** `{tool_input['old_str'][:100]}{'...' if len(tool_input['old_str']) > 100 else ''}`")
                    if 'new_str' in tool_input:
                        st.write(f"• **New Text:** `{tool_input['new_str'][:100]}{'...' if len(tool_input['new_str']) > 100 else ''}`")
                    if 'insert_line' in tool_input:
                        st.write(f"• **Insert at Line:** {tool_input['insert_line']}")
                    if 'view_range' in tool_input:
                        st.write(f"• **View Range:** {tool_input['view_range']}")
                elif tool_name == 'applescript':
                    script = tool_input.get('script', '')
                    st.code(script, language="applescript")
                elif tool_name == 'silicon':
                    action = tool_input.get('action', 'Unknown')
                    st.write(f"• **Monitoring:** {action}")
                else:
                    st.json(tool_input)
        else:
            st.markdown(message)


def load_test_cases_from_csv(file_path: str) -> List[Dict]:
    """Load test cases from CSV file with enhanced parsing."""
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        
        # Parse test cases into structured format
        test_cases = []
        for _, row in df.iterrows():
            test_case = {
                "id": row.get("#", ""),
                "scenario": row.get("Test Scenario", ""),
                "precondition": row.get("Pre-Condition", ""),
                "component": row.get("Component", ""),
                "step": row.get("Steps", ""),
                "description": row.get("Description", ""),
                "expected": row.get("Expected Results", ""),
                "actual": row.get("Actual Results", ""),
                "status": row.get("Pass/Fail", ""),
                "comments": row.get("Comments", "")
            }
            test_cases.append(test_case)
        
        return test_cases
    except Exception as e:
        st.error(f"Failed to load test cases: {e}")
        return []

def execute_test_case_step(test_case: Dict) -> str:
    """Generate Claude instructions for executing a test case step."""
    instruction = f"""
Execute Test Case: {test_case['id']} - {test_case['scenario']}

**Precondition:** {test_case['precondition']}
**Component:** {test_case['component']}
**Step {test_case['step']}:** {test_case['description']}
**Expected Result:** {test_case['expected']}

Please execute this test step and verify the expected result. Take screenshots to document the process and outcome.
"""
    return instruction

async def monitor_m4_performance() -> Dict:
    """Monitor M4 MacBook Air performance metrics."""
    try:
        # Get thermal state
        thermal_result = subprocess.run(
            ["pmset", "-g", "therm"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        # Get CPU usage
        cpu_result = subprocess.run(
            ["top", "-l", "1", "-n", "0", "-s", "0"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        # Get memory usage
        memory_result = subprocess.run(
            ["vm_stat"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        # Parse results
        thermal_state = "Normal"
        if thermal_result.returncode == 0:
            if "warning" in thermal_result.stdout.lower():
                thermal_state = "Warning"
            elif "critical" in thermal_result.stdout.lower():
                thermal_state = "Critical"
        
        cpu_usage = "Unknown"
        if cpu_result.returncode == 0:
            lines = cpu_result.stdout.split('\n')
            for line in lines:
                if "CPU usage" in line:
                    cpu_usage = line.strip()
                    break
        
        memory_info = "Unknown"
        if memory_result.returncode == 0:
            lines = memory_result.stdout.split('\n')
            if lines:
                memory_info = f"Memory stats available ({len(lines)} metrics)"
        
        return {
            "thermal_state": thermal_state,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_info,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "thermal_state": "Error",
            "cpu_usage": f"Error: {str(e)}",
            "memory_usage": "Error",
            "last_updated": datetime.now().isoformat()
        }

# Run the main function directly (Streamlit handles the async context)
asyncio.run(main())
