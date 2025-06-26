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
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "current_session_title" not in st.session_state:
        st.session_state.current_session_title = None
    if "session_manager" not in st.session_state:
        st.session_state.session_manager = SessionManager()
    if "auto_save_enabled" not in st.session_state:
        st.session_state.auto_save_enabled = True
    if "smart_naming_enabled" not in st.session_state:
        st.session_state.smart_naming_enabled = True
    if "conversation_completed" not in st.session_state:
        st.session_state.conversation_completed = False
    if "session_widget_key_counter" not in st.session_state:
        st.session_state.session_widget_key_counter = 0
    if "api_key" not in st.session_state:
        # Try to load API key from file first, then environment
        st.session_state.api_key = load_from_storage("api_key") or os.getenv(
            "ANTHROPIC_API_KEY", ""
        )
    if "provider" not in st.session_state:
        st.session_state.provider = (
            os.getenv("API_PROVIDER", "anthropic") or APIProvider.ANTHROPIC
        )
    if "provider_radio" not in st.session_state:
        st.session_state.provider_radio = st.session_state.provider
    if "model" not in st.session_state:
        _reset_model()
    if "auth_validated" not in st.session_state:
        st.session_state.auth_validated = False
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "tools" not in st.session_state:
        st.session_state.tools = {}
    if "only_n_most_recent_images" not in st.session_state:
        st.session_state.only_n_most_recent_images = 3  # Very conservative default to prevent timeouts
    if "custom_system_prompt" not in st.session_state:
        st.session_state.custom_system_prompt = load_from_storage("system_prompt") or ""
    if "hide_images" not in st.session_state:
        st.session_state.hide_images = False
    if "enable_extended_thinking" not in st.session_state:
        st.session_state.enable_extended_thinking = False
    if "thinking_budget_tokens" not in st.session_state:
        st.session_state.thinking_budget_tokens = 10000  # Standard default per documentation
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = None
    # Performance tracking
    if "tool_usage_stats" not in st.session_state:
        st.session_state.tool_usage_stats = {}
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    if "current_tool_execution" not in st.session_state:
        st.session_state.current_tool_execution = None
    if "api_timeout" not in st.session_state:
        st.session_state.api_timeout = 120  # Default 2 minute timeout


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
        
        # Restore session settings
        if "model" in metadata:
            st.session_state.model = metadata["model"]
        if "provider" in metadata:
            st.session_state.provider = metadata["provider"]
            st.session_state.provider_radio = metadata["provider"]
        if "thinking_enabled" in metadata:
            st.session_state.enable_extended_thinking = metadata["thinking_enabled"]
        if "thinking_budget" in metadata:
            st.session_state.thinking_budget_tokens = metadata["thinking_budget"]
        if "tool_usage_stats" in metadata:
            st.session_state.tool_usage_stats = metadata["tool_usage_stats"]
        if "smart_naming_enabled" in metadata:
            st.session_state.smart_naming_enabled = metadata["smart_naming_enabled"]
        if "conversation_completed" in metadata:
            st.session_state.conversation_completed = metadata["conversation_completed"]
        
        # Reset conversation completion status when loading a session
        st.session_state.conversation_completed = False
        
        st.success(f"✅ Loaded chat: {title}")
        st.rerun()


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


def render_chat_sidebar():
    """Render the chat history sidebar"""
    with st.sidebar:
        st.markdown("---")
        
        # Chat Management Section
        st.subheader("💬 Chat History")
        
        # New Chat Button
        if st.button("🆕 New Chat", type="primary", use_container_width=True):
            start_new_chat()
        
        # Auto-save toggle
        st.checkbox(
            "Auto-save chats",
            key="auto_save_enabled",
            help="Automatically save conversations when starting new chats"
        )
        
        # Smart naming toggle
        st.checkbox(
            "Smart auto-naming",
            key="smart_naming_enabled",
            help="Automatically generate meaningful chat titles based on conversation content"
        )
        
        # Current session info
        if st.session_state.current_session_title:
            st.info(f"📝 Current: {st.session_state.current_session_title}")
            
            # Manual save button
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save", use_container_width=True):
                    auto_save_current_session()
                    st.success("Chat saved!")
            
            with col2:
                # Rename current chat
                if st.button("✏️ Rename", use_container_width=True):
                    st.session_state.show_rename_input = True
            
            # Smart naming option
            if st.session_state.smart_naming_enabled and len(st.session_state.messages) >= 3:
                if st.button("🤖 Smart Rename", use_container_width=True, help="Generate a smart title based on conversation content"):
                    auto_save_current_session(force_smart_naming=True)
                    st.success("Smart title generated!")
                    st.rerun()
            
            # Rename input
            if getattr(st.session_state, "show_rename_input", False):
                new_title = st.text_input(
                    "New chat title:",
                    value=st.session_state.current_session_title,
                    key="rename_input"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Save"):
                        st.session_state.current_session_title = new_title
                        auto_save_current_session()
                        st.session_state.show_rename_input = False
                        st.success("Chat renamed!")
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel"):
                        st.session_state.show_rename_input = False
                        st.rerun()
        
        # Session List with categorization
        sessions = st.session_state.session_manager.list_sessions()
        
        if sessions:
            # Session organization options
            organization_options = ["All Chats", "Recent (7 days)", "By Model", "With Tools", "With Thinking"]
            selected_org = st.selectbox(
                "📂 Organize by:",
                organization_options,
                key="session_organization"
            )
            
            # Filter sessions based on organization choice
            if selected_org == "Recent (7 days)":
                from datetime import timedelta
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                sessions = [s for s in sessions if s.get("updated_at", "") >= week_ago]
            elif selected_org == "By Model":
                # Group by model
                st.markdown("**📊 Sessions by Model:**")
                model_groups = {}
                for session in sessions:
                    model = session.get("model", "Unknown")
                    if model not in model_groups:
                        model_groups[model] = []
                    model_groups[model].append(session)
                
                for model, model_sessions in model_groups.items():
                    with st.expander(f"🎯 {model} ({len(model_sessions)} chats)", expanded=len(model_groups) == 1):
                        for idx, session in enumerate(model_sessions[:5]):  # Show first 5 per model
                            _render_session_item(session, st.session_state.session_manager, f"{model}_{idx}")
            elif selected_org == "With Tools":
                # Filter sessions that used tools
                filtered_sessions = []
                for session in sessions:
                    _, metadata, _ = st.session_state.session_manager.load_session(session["id"])
                    stats = metadata.get("conversation_stats", {})
                    if stats.get("tool_uses", 0) > 0:
                        filtered_sessions.append(session)
                sessions = filtered_sessions
            elif selected_org == "With Thinking":
                # Filter sessions that used extended thinking
                filtered_sessions = []
                for session in sessions:
                    _, metadata, _ = st.session_state.session_manager.load_session(session["id"])
                    stats = metadata.get("conversation_stats", {})
                    if stats.get("thinking_blocks", 0) > 0:
                        filtered_sessions.append(session)
                sessions = filtered_sessions
            
            # Apply search filter if active
            if getattr(st.session_state, 'search_active', False) and getattr(st.session_state, 'search_query', ''):
                search_query = st.session_state.search_query
                filtered_sessions = []
                for session in sessions:
                    if search_query.lower() in session['title'].lower():
                        filtered_sessions.append(session)
                    else:
                        # Search in message content
                        messages, _, _ = st.session_state.session_manager.load_session(session["id"])
                        for msg in messages:
                            content = str(msg.get("content", "")).lower()
                            if search_query.lower() in content:
                                filtered_sessions.append(session)
                                break
                
                if filtered_sessions:
                    st.info(f"🔍 Found {len(filtered_sessions)} chats matching '{search_query}'")
                    sessions = filtered_sessions
                else:
                    st.warning(f"🔍 No chats found matching '{search_query}'")
                    sessions = []
            
            st.markdown("**📚 Recent Chats:**")
            
            # Show only recent sessions by default, with option to show more
            display_count = 10
            show_all = st.checkbox("Show all chats", value=False)
            if show_all:
                display_count = len(sessions)
            
            for i, session in enumerate(sessions[:display_count]):
                if session["id"] == st.session_state.current_session_id:
                    continue  # Skip current session
                
                _render_session_item(session, st.session_state.session_manager, i)
            
            # Show count info
            if len(sessions) > display_count:
                st.caption(f"Showing {display_count} of {len(sessions)} chats")
        else:
            st.info("No saved chats yet. Start chatting to create your first conversation!")
        
        # Export/Import functionality
        with st.expander("📤 Export/Import", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📤 Export All Chats", use_container_width=True, key="export_all_chats_btn"):
                    # Create export data
                    all_sessions = st.session_state.session_manager.list_sessions()
                    export_data = {
                        "exported_at": datetime.now().isoformat(),
                        "export_version": "1.0",
                        "total_sessions": len(all_sessions),
                        "sessions": []
                    }
                    
                    for session in all_sessions:
                        messages, metadata, title = st.session_state.session_manager.load_session(session["id"])
                        export_data["sessions"].append({
                            "id": session["id"],
                            "title": title,
                            "created_at": metadata.get("created_at", ""),
                            "metadata": metadata,
                            "messages": st.session_state.session_manager._serialize_messages(messages)
                        })
                    
                    # Offer download
                    export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="💾 Download Chats",
                        data=export_json,
                        file_name=f"claude_chats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True,
                        key="download_chats_btn"
                    )
            
            with col2:
                # Search functionality
                search_query = st.text_input("🔍 Search chats", placeholder="Search by title or content...", key="search_chats_input")
                
            # Import functionality
            uploaded_file = st.file_uploader("📥 Import Chats", type=['json'], key="import_chats_uploader")
            if uploaded_file is not None:
                try:
                    import_data = json.load(uploaded_file)
                    imported_count = 0
                    skipped_count = 0
                    
                    for session_data in import_data.get("sessions", []):
                        session_id = session_data.get("id", str(uuid.uuid4()))
                        title = session_data.get("title", "Imported Chat")
                        metadata = session_data.get("metadata", {})
                        messages = st.session_state.session_manager._deserialize_messages(
                            session_data.get("messages", [])
                        )
                        
                        # Check if session already exists
                        existing_sessions = [s["id"] for s in st.session_state.session_manager.list_sessions()]
                        if session_id in existing_sessions:
                            session_id = f"{session_id}_imported_{int(datetime.now().timestamp())}"
                        
                        if st.session_state.session_manager.save_session(session_id, title, messages, metadata):
                            imported_count += 1
                        else:
                            skipped_count += 1
                    
                    if imported_count > 0:
                        st.success(f"✅ Imported {imported_count} chats!")
                        if skipped_count > 0:
                            st.warning(f"⚠️ Skipped {skipped_count} chats (possibly duplicates)")
                        st.rerun()
                    else:
                        st.error("❌ No chats were imported")
                except Exception as e:
                    st.error(f"❌ Import failed: {e}")
            
            # Apply search filter if provided
            if search_query:
                st.session_state.search_active = True
                st.session_state.search_query = search_query
            elif getattr(st.session_state, 'search_active', False):
                st.session_state.search_active = False
                st.session_state.search_query = ""


def _render_session_item(session: Dict, session_manager, item_index: int = 0) -> None:
    """Helper function to render a single session item"""
    # Format session info
    created_date = ""
    if session.get("created_at"):
        try:
            dt = datetime.fromisoformat(session["created_at"].replace("Z", "+00:00"))
            created_date = dt.strftime("%m/%d %H:%M")
        except:
            created_date = ""
    
    session_info = f"{session['title']}"
    if created_date:
        session_info += f" ({created_date})"
    
    # Enhanced session item with more details
    col1, col2 = st.columns([4, 1])
    
    # Load session metadata for enhanced display
    _, session_metadata, _ = session_manager.load_session(session["id"])
    conversation_stats = session_metadata.get("conversation_stats", {})
    
    # Build tooltip with enhanced information
    tooltip_parts = [
        f"Model: {session.get('model', 'Unknown')}",
        f"Messages: {session.get('message_count', 0)}",
    ]
    
    if conversation_stats:
        if conversation_stats.get("tool_uses", 0) > 0:
            tooltip_parts.append(f"Tools used: {conversation_stats['tool_uses']}")
        if conversation_stats.get("thinking_blocks", 0) > 0:
            tooltip_parts.append(f"Thinking blocks: {conversation_stats['thinking_blocks']}")
        if conversation_stats.get("tools_used"):
            tools = ", ".join(conversation_stats["tools_used"][:3])
            if len(conversation_stats["tools_used"]) > 3:
                tools += "..."
            tooltip_parts.append(f"Tools: {tools}")
    
    tooltip = " | ".join(tooltip_parts)
    
    with col1:
        # Add icons based on session content
        icons = []
        if conversation_stats.get("thinking_blocks", 0) > 0:
            icons.append("🧠")
        if conversation_stats.get("tool_uses", 0) > 0:
            icons.append("🔧")
        if conversation_stats.get("has_images", False):
            icons.append("📸")
        
        icon_prefix = " ".join(icons) + " " if icons else ""
        
        # Create unique key using full session ID and index to prevent collisions
        unique_key = f"{st.session_state.session_widget_key_counter}_{session['id']}_{item_index}"
        
        if st.button(
            f"{icon_prefix}{session_info}",
            key=f"load_session_{unique_key}",
            help=tooltip,
            use_container_width=True
        ):
            load_chat_session(session["id"])
    
    with col2:
        if st.button("🗑️", key=f"delete_session_{unique_key}", help="Delete chat"):
            if session_manager.delete_session(session["id"]):
                st.success("Chat deleted!")
                st.rerun()


async def main():
    """Render loop for streamlit"""
    setup_state()

    st.markdown(STREAMLIT_STYLE, unsafe_allow_html=True)

    st.title("🚀 Claude Computer Use for Mac")
    st.caption("Enhanced with Claude 3.7 & Claude 4 🧠 • Optimized for macOS 💫")

    st.markdown("""
    This is an enhanced version of [Mac Computer Use](https://github.com/deedy/mac_computer_use), a fork of [Anthropic Computer Use](https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/README.md) to work natively on Mac.
    
    **🆕 New Features:**
    - **Claude 4 Support** - Most capable models with enhanced reasoning
    - **Extended Thinking** - Claude's step-by-step reasoning for complex tasks
    - **Smart Model Selection** - Easy switching between Claude 3.5, 3.7, and 4 models
    - **Enhanced UI** - Better model configuration and debugging tools
    - **🍎 Apple Silicon Support** - Native performance on M-series chips
    - **🔧 macOS Integration** - AppleScript automation and system tools
    - **💾 Memory Efficient** - Optimized context window management
    
    **⚡ Quick Start:** Select Claude Sonnet 4 or Opus 4 from the sidebar for the best performance!
    """)
    
    # Enhanced model status with real-time info
    current_model = st.session_state.get('model', 'Not selected')
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if model_supports_extended_thinking(current_model):
            st.success(f"🎯 **Current Model:** {current_model} (Extended Thinking Supported)")
        else:
            st.info(f"🎯 **Current Model:** {current_model}")
    
    with col2:
        # Show current tool execution status
        if st.session_state.current_tool_execution:
            st.warning(f"⚡ Executing: {st.session_state.current_tool_execution}")
        else:
            # Show session statistics
            total_tools_used = sum(st.session_state.tool_usage_stats.values()) if st.session_state.tool_usage_stats else 0
            if total_tools_used > 0:
                st.metric("Tools Used", total_tools_used)
            else:
                st.info("Ready 🚀")
    

    with st.sidebar:

        def _reset_api_provider():
            # Initialize provider if not set
            if "provider" not in st.session_state:
                st.session_state.provider = APIProvider.ANTHROPIC
            
            if st.session_state.provider_radio != st.session_state.provider:
                _reset_model()
                st.session_state.provider = st.session_state.provider_radio
                st.session_state.auth_validated = False

        provider_options = [option.value for option in APIProvider]
        st.radio(
            "API Provider",
            options=provider_options,
            key="provider_radio",
            format_func=lambda x: x.title(),
            on_change=_reset_api_provider,
        )

        # Model selection with dropdown
        available_models = AVAILABLE_MODELS.get(st.session_state.provider, [])
        model_options = [model[0] for model in available_models]
        model_descriptions = {model[0]: model[1] for model in available_models}
        
        if st.session_state.model not in model_options and model_options:
            st.session_state.model = model_options[0]
        
        selected_model = st.selectbox(
            "Model",
            options=model_options,
            index=model_options.index(st.session_state.model) if st.session_state.model in model_options else 0,
            format_func=lambda x: f"{x} - {model_descriptions.get(x, '')}",
            key="model_selector"
        )
        
        if selected_model != st.session_state.model:
            st.session_state.model = selected_model
            # Reset max_tokens when model changes
            st.session_state.max_tokens = None
        
        # Show model capabilities
        if model_supports_extended_thinking(st.session_state.model):
            st.success("✨ This model supports Extended Thinking")
        
        max_tokens_for_model = get_max_tokens_for_model(st.session_state.model)
        st.info(f"📊 Max output tokens: {max_tokens_for_model:,}")
        
        # Allow manual model entry for advanced users
        with st.expander("🔧 Advanced: Custom Model"):
            custom_model = st.text_input(
                "Enter custom model name",
                value=st.session_state.model,
                help="For advanced users who want to specify a custom model name"
            )
            if custom_model != st.session_state.model:
                st.session_state.model = custom_model

        if st.session_state.provider == APIProvider.ANTHROPIC:
            st.text_input(
                "Anthropic API Key",
                type="password",
                key="api_key",
                on_change=lambda: save_to_storage("api_key", st.session_state.api_key),
            )

        # Extended Thinking Configuration
        if model_supports_extended_thinking(st.session_state.model):
            with st.expander("🧠 Extended Thinking Settings", expanded=False):
                st.checkbox(
                    "Enable Extended Thinking",
                    key="enable_extended_thinking",
                    help="Enable Claude's step-by-step reasoning process for complex tasks"
                )
                
                if st.session_state.enable_extended_thinking:
                    st.slider(
                        "Thinking Budget (tokens)",
                        min_value=1024,
                        max_value=64000,  # Increased for M4 + 16GB
                        value=st.session_state.thinking_budget_tokens,
                        step=1024,
                        key="thinking_budget_tokens",
                        help="Maximum tokens Claude can use for internal reasoning"
                    )
                    st.info("💡 Higher budgets allow for more thorough analysis")



        # Advanced Settings
        with st.expander("⚙️ Advanced Settings", expanded=False):
            # Max tokens override - enhanced for M4
            default_max_tokens = get_max_tokens_for_model(st.session_state.model)
            st.number_input(
                "Max Output Tokens",
                min_value=1000,
                max_value=default_max_tokens,
                value=st.session_state.max_tokens or default_max_tokens,
                step=1000,
                key="max_tokens",
                help=f"Maximum tokens for output (default: {default_max_tokens:,})"
            )
            
            # API Timeout configuration
            st.slider(
                "API Timeout (seconds)",
                min_value=30,
                max_value=300,
                value=120,
                step=30,
                key="api_timeout",
                help="How long to wait for API responses. Lower values prevent long hangs but may timeout complex requests."
            )
            
            st.number_input(
                "Recent Images Cache",
                min_value=0,
                max_value=30,  # Conservative default
                value=st.session_state.only_n_most_recent_images,
                key="only_n_most_recent_images",
                help="Number of recent screenshots to keep in memory",
            )
            
            st.text_area(
                "Custom System Prompt Suffix",
                key="custom_system_prompt",
                help="Additional instructions to append to the system prompt. see computer_use_demo/loop.py for the base system prompt.",
                on_change=lambda: save_to_storage(
                    "system_prompt", st.session_state.custom_system_prompt
                ),
            )
            
            st.checkbox("Hide screenshots", key="hide_images")

        # Performance Metrics Section
        with st.expander("📊 Session Analytics", expanded=False):
            # Session duration
            session_duration = datetime.now() - st.session_state.session_start_time
            st.metric("Session Duration", f"{session_duration.seconds // 60}m {session_duration.seconds % 60}s")
            
            # Total messages
            total_messages = len(st.session_state.messages)
            st.metric("Total Messages", total_messages)
            
            # Tool usage statistics
            if st.session_state.tool_usage_stats:
                st.markdown("**🔧 Tool Usage:**")
                for tool_name, count in sorted(st.session_state.tool_usage_stats.items()):
                    if tool_name != 'unknown':
                        tool_icons = {
                            'computer': '🖥️',
                            'bash': '💻', 
                            'str_replace_based_edit_tool': '📝',
                            'applescript': '🍎',
                            'silicon': '⚡'
                        }
                        icon = tool_icons.get(tool_name, '🔧')
                        st.write(f"{icon} {tool_name.replace('_', ' ').title()}: {count} uses")
            else:
                st.info("No tools used yet")
            
            # System performance indicators
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                st.markdown("**💾 System Performance:**")
                st.write(f"• CPU: {cpu_percent}%")
                st.write(f"• Memory: {memory.percent}% ({memory.available // (1024**3):.1f}GB free)")
            except ImportError:
                st.caption("Install psutil for system performance metrics")

        # Chat History and Session Management
        render_chat_sidebar()

        if st.button("Reset", type="primary"):
            with st.spinner("Resetting..."):
                st.session_state.clear()
                setup_state()

                subprocess.run("pkill Xvfb; pkill tint2", shell=True)  # noqa: ASYNC221
                await asyncio.sleep(1)
                subprocess.run("./start_all.sh", shell=True)  # noqa: ASYNC221

    if not st.session_state.auth_validated:
        if auth_error := validate_auth(
            st.session_state.provider, st.session_state.api_key
        ):
            st.warning(f"Please resolve the following auth issue:\n\n{auth_error}")
            return
        else:
            st.session_state.auth_validated = True

    chat, http_logs = st.tabs(["Chat", "HTTP Exchange Logs"])
    new_message = st.chat_input(
        "Type a message to send to Claude to control the computer..."
    )

    with chat:
        # render past chats
        for message in st.session_state.messages:
            if isinstance(message["content"], str):
                _render_message(message["role"], message["content"])
            elif isinstance(message["content"], list):
                for block in message["content"]:
                    # the tool result we send back to the Anthropic API isn't sufficient to render all details,
                    # so we store the tool use responses
                    if isinstance(block, dict) and block["type"] == "tool_result":
                        _render_message(
                            Sender.TOOL, st.session_state.tools[block["tool_use_id"]]
                        )
                    elif isinstance(block, dict) and block.get("type") in ["thinking", "redacted_thinking"]:
                        # Handle thinking blocks
                        _render_message(message["role"], block)
                    else:
                        _render_message(
                            message["role"],
                            cast(BetaTextBlock | BetaToolUseBlock, block),
                        )

        # render past http exchanges
        for identity, response in st.session_state.responses.items():
            _render_api_response(response, identity, http_logs)

        # render past chats
        if new_message:
            st.session_state.messages.append(
                {
                    "role": Sender.USER,
                    "content": [TextBlock(type="text", text=new_message)],
                }
            )
            _render_message(Sender.USER, new_message)
            
            # Auto-save after adding user message if enabled
            if st.session_state.auto_save_enabled and len(st.session_state.messages) > 1:
                auto_save_current_session()

        try:
            most_recent_message = st.session_state["messages"][-1]
        except IndexError:
            return

        if most_recent_message["role"] is not Sender.USER:
            # we don't have a user message to respond to, exit early
            return

        with st.spinner("Running Agent..."):
            try:
                # run the agent sampling loop with the newest message
                st.session_state.messages = await sampling_loop(
                    system_prompt_suffix=st.session_state.custom_system_prompt,
                    model=st.session_state.model,
                    provider=st.session_state.provider,
                    messages=st.session_state.messages,
                    output_callback=partial(_render_message, Sender.BOT),
                    tool_output_callback=partial(
                        _tool_output_callback, tool_state=st.session_state.tools
                    ),
                    api_response_callback=partial(
                        _api_response_callback,
                        tab=http_logs,
                        response_state=st.session_state.responses,
                    ),
                    api_key=st.session_state.api_key,
                    only_n_most_recent_images=st.session_state.only_n_most_recent_images,
                    max_tokens=st.session_state.max_tokens,
                    enable_extended_thinking=st.session_state.enable_extended_thinking,
                    thinking_budget_tokens=st.session_state.thinking_budget_tokens,
                    api_timeout=st.session_state.api_timeout,
                )
                
                # Mark conversation as completed for smart naming
                st.session_state.conversation_completed = True
                
                # Auto-save after assistant response if enabled
                if st.session_state.auto_save_enabled:
                    auto_save_current_session()
                    
            except TimeoutError as e:
                st.error(f"**⏱️ Request Timeout:** {str(e)}")
                st.info("💡 **Suggestions:** Increase the API timeout in Advanced Settings, reduce thinking budget, or try a simpler request.")
                # Show timeout-specific help
                with st.expander("🔧 Timeout Troubleshooting", expanded=True):
                    st.markdown("""
                    **Common solutions:**
                    - Increase **API Timeout** to 180-300 seconds for complex tasks
                    - Reduce **Thinking Budget** if using Extended Thinking (try 5000-8000 tokens)
                    - Break complex requests into smaller steps
                    - Check your internet connection
                    - Switch to a faster model (e.g., Claude Haiku)
                    """)
            except Exception as e:
                st.error(f"**❌ Agent Error:** {str(e)}")
                st.info("💡 Try refreshing the page or checking your API key and model settings.")
                # Log the error but don't crash the app
                import traceback
                with st.expander("🔍 Error Details", expanded=False):
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


# Run the main function directly (Streamlit handles the async context)
asyncio.run(main())
