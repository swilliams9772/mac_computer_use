#!/usr/bin/env python3
"""
CLI version of Claude Computer Use for Mac
Enhanced with Claude 4 support and Extended Thinking
"""

import asyncio
import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import PosixPath
from typing import cast, List, Dict, Any

from anthropic.types import TextBlock
from anthropic.types.beta import BetaMessage, BetaTextBlock, BetaToolUseBlock

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

CONFIG_DIR = PosixPath("~/.anthropic").expanduser()
API_KEY_FILE = CONFIG_DIR / "api_key"
SESSION_DIR = CONFIG_DIR / "sessions"

class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'
    END = '\033[0m'

class ProgressIndicator:
    """Simple progress indicator for long-running tasks"""
    def __init__(self, message: str = "Processing"):
        self.message = message
        self.active = False
        self.chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.current = 0
        
    async def start(self):
        """Start the progress indicator"""
        self.active = True
        print(f"\n{Colors.YELLOW}{self.message}... ", end="", flush=True)
        while self.active:
            print(f"\r{Colors.YELLOW}{self.message}... {self.chars[self.current % len(self.chars)]}{Colors.END}", end="", flush=True)
            self.current += 1
            await asyncio.sleep(0.1)
    
    def stop(self):
        """Stop the progress indicator"""
        self.active = False
        print(f"\r{Colors.GREEN}✅ {self.message} complete{Colors.END}")

class SessionManager:
    """Manage chat sessions with persistence"""
    def __init__(self):
        self.session_dir = SESSION_DIR
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None
        
    def save_session(self, messages: List[Dict], metadata: Dict):
        """Save current session to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = self.session_dir / f"session_{timestamp}.json"
        
        session_data = {
            "timestamp": timestamp,
            "metadata": metadata,
            "messages": self._serialize_messages(messages)
        }
        
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            self.current_session = session_file
            print_colored(f"💾 Session saved to {session_file.name}", Colors.GREEN)
        except Exception as e:
            print_colored(f"❌ Failed to save session: {e}", Colors.RED)
    
    def load_session(self, session_file: str = None) -> tuple[List[Dict], Dict]:
        """Load a session from file"""
        if session_file:
            session_path = self.session_dir / session_file
        else:
            # Load most recent session
            session_files = sorted(self.session_dir.glob("session_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
            if not session_files:
                return [], {}
            session_path = session_files[0]
        
        try:
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            messages = self._deserialize_messages(session_data.get("messages", []))
            metadata = session_data.get("metadata", {})
            
            print_colored(f"📂 Loaded session from {session_path.name}", Colors.GREEN)
            return messages, metadata
        except Exception as e:
            print_colored(f"❌ Failed to load session: {e}", Colors.RED)
            return [], {}
    
    def list_sessions(self):
        """List available sessions"""
        session_files = sorted(self.session_dir.glob("session_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        if not session_files:
            print_colored("📁 No saved sessions found", Colors.YELLOW)
            return
        
        print_colored("\n📂 Available Sessions:", Colors.BOLD + Colors.CYAN)
        for i, session_file in enumerate(session_files[:10], 1):  # Show last 10 sessions
            stat = session_file.stat()
            timestamp = datetime.fromtimestamp(stat.st_mtime)
            size = stat.st_size
            print(f"{i:2d}. {session_file.name} ({timestamp.strftime('%Y-%m-%d %H:%M')} - {size:,} bytes)")
    
    def _serialize_messages(self, messages: List[Dict]) -> List[Dict]:
        """Convert messages to JSON-serializable format"""
        serialized = []
        for msg in messages:
            if isinstance(msg.get("content"), list):
                content = []
                for block in msg["content"]:
                    if hasattr(block, '__dict__'):
                        content.append(block.__dict__)
                    else:
                        content.append(block)
                serialized.append({"role": msg["role"], "content": content})
            else:
                serialized.append(msg)
        return serialized
    
    def _deserialize_messages(self, messages: List[Dict]) -> List[Dict]:
        """Convert JSON format back to message format"""
        deserialized = []
        for msg in messages:
            if isinstance(msg.get("content"), list):
                content = []
                for block in msg["content"]:
                    if isinstance(block, dict) and block.get("type") == "text":
                        content.append(TextBlock(type="text", text=block.get("text", "")))
                    else:
                        content.append(block)
                deserialized.append({"role": msg["role"], "content": content})
            else:
                deserialized.append(msg)
        return deserialized

def print_colored(text: str, color: str = Colors.WHITE):
    """Print text with color"""
    print(f"{color}{text}{Colors.END}")

def print_header():
    """Print the application header"""
    print_colored("🚀 Claude Computer Use for Mac - CLI Version", Colors.BOLD + Colors.BLUE)
    print_colored("Enhanced with Claude 3.7 & Claude 4 🧠 • Optimized for macOS 💫", Colors.CYAN)
    print_colored("=" * 70, Colors.WHITE)

def print_status_bar(model: str, thinking: bool, messages_count: int, session_active: bool = False):
    """Print a status bar with current configuration"""
    status_items = [
        f"Model: {model}",
        f"Messages: {messages_count}",
        f"Thinking: {'ON' if thinking else 'OFF'}",
        f"Session: {'ACTIVE' if session_active else 'NEW'}"
    ]
    status = f"{Colors.DIM}[{' | '.join(status_items)}]{Colors.END}"
    print(status)

def load_from_storage(filename: str) -> str | None:
    """Load data from a file in the storage directory."""
    try:
        file_path = CONFIG_DIR / filename
        if file_path.exists():
            data = file_path.read_text().strip()
            if data:
                return data
    except Exception as e:
        print_colored(f"Error loading {filename}: {e}", Colors.YELLOW)
    return None

def save_to_storage(filename: str, data: str) -> None:
    """Save data to a file in the storage directory."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        file_path = CONFIG_DIR / filename
        file_path.write_text(data)
        # Ensure only user can read/write the file
        file_path.chmod(0o600)
        print_colored(f"✅ Saved {filename}", Colors.GREEN)
    except Exception as e:
        print_colored(f"Error saving {filename}: {e}", Colors.RED)

def validate_auth(provider: APIProvider, api_key: str | None) -> str | None:
    """Validate authentication for the selected provider"""
    if provider == APIProvider.ANTHROPIC:
        if not api_key:
            return "Enter your Anthropic API key to continue."
    elif provider == APIProvider.BEDROCK:
        import boto3
        if not boto3.Session().get_credentials():
            return "You must have AWS credentials set up to use the Bedrock API."
    elif provider == APIProvider.VERTEX:
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
    return None

def select_model(provider: APIProvider) -> str:
    """Interactive model selection"""
    available_models = AVAILABLE_MODELS.get(provider, [])
    if not available_models:
        return PROVIDER_TO_DEFAULT_MODEL_NAME[provider]
    
    print_colored("\n📋 Available Models:", Colors.BOLD + Colors.CYAN)
    for i, (model_name, description) in enumerate(available_models, 1):
        thinking_support = "🧠" if model_supports_extended_thinking(model_name) else "  "
        max_tokens = get_max_tokens_for_model(model_name)
        print(f"{i:2d}. {thinking_support} {Colors.BOLD}{model_name}{Colors.END} - {description} ({max_tokens:,} tokens)")
    
    while True:
        try:
            choice = input(f"\n{Colors.CYAN}Select model (1-{len(available_models)}) or press Enter for default: {Colors.END}")
            if not choice.strip():
                return available_models[0][0]  # Default to first model
            
            index = int(choice) - 1
            if 0 <= index < len(available_models):
                selected_model = available_models[index][0]
                print_colored(f"✅ Selected: {selected_model}", Colors.GREEN)
                return selected_model
            else:
                print_colored("Invalid selection. Please try again.", Colors.RED)
        except ValueError:
            print_colored("Please enter a valid number.", Colors.RED)
        except KeyboardInterrupt:
            print_colored("\n\nExiting...", Colors.YELLOW)
            sys.exit(0)

def get_api_key(provider: APIProvider) -> str:
    """Get API key from user or storage"""
    # Try to load from storage first
    stored_key = load_from_storage("api_key")
    if stored_key:
        print_colored(f"✅ Using stored {provider.title()} API key", Colors.GREEN)
        return stored_key
    
    # Try environment variable
    env_key = os.getenv("ANTHROPIC_API_KEY")
    if env_key:
        print_colored(f"✅ Using {provider.title()} API key from environment", Colors.GREEN)
        return env_key
    
    # Ask user for key
    print_colored(f"\n🔑 {provider.title()} API Key Required", Colors.BOLD + Colors.YELLOW)
    while True:
        try:
            api_key = input(f"{Colors.CYAN}Enter your {provider.title()} API key: {Colors.END}").strip()
            if api_key:
                # Ask if they want to save it
                save_choice = input(f"{Colors.CYAN}Save API key for future use? (y/N): {Colors.END}").strip().lower()
                if save_choice in ['y', 'yes']:
                    save_to_storage("api_key", api_key)
                return api_key
            else:
                print_colored("API key cannot be empty. Please try again.", Colors.RED)
        except KeyboardInterrupt:
            print_colored("\n\nExiting...", Colors.YELLOW)
            sys.exit(0)

def configure_extended_thinking(model: str) -> tuple[bool, int]:
    """Configure extended thinking settings"""
    if not model_supports_extended_thinking(model):
        return False, 0
    
    print_colored(f"\n🧠 Extended Thinking Available for {model}", Colors.BOLD + Colors.PURPLE)
    print("Extended Thinking enables Claude's step-by-step reasoning for complex tasks.")
    
    try:
        enable = input(f"{Colors.CYAN}Enable Extended Thinking? (Y/n): {Colors.END}").strip().lower()
        if enable in ['', 'y', 'yes']:
            while True:
                try:
                    budget = input(f"{Colors.CYAN}Thinking budget in tokens (1024-64000, default 10000): {Colors.END}").strip()
                    if not budget:
                        return True, 10000
                    
                    budget_int = int(budget)
                    if 1024 <= budget_int <= 64000:
                        print_colored(f"✅ Extended Thinking enabled with {budget_int:,} token budget", Colors.GREEN)
                        return True, budget_int
                    else:
                        print_colored("Budget must be between 1024 and 64000 tokens.", Colors.RED)
                except ValueError:
                    print_colored("Please enter a valid number.", Colors.RED)
        else:
            return False, 0
    except KeyboardInterrupt:
        print_colored("\n\nUsing default settings...", Colors.YELLOW)
        return False, 0

def render_message_cli(role: str, content, show_thinking: bool = True):
    """Enhanced message rendering with better formatting"""
    if role == "user":
        print_colored(f"\n👤 You:", Colors.BOLD + Colors.BLUE)
        print(f"{content}")
    elif role == "assistant":
        if isinstance(content, BetaTextBlock):
            print_colored(f"\n🤖 Claude:", Colors.BOLD + Colors.GREEN)
            # Format long responses better
            text = content.text
            if len(text) > 1000:
                print(f"{text[:1000]}...")
                expand = input(f"{Colors.DIM}[Show full response? (y/N)]: {Colors.END}").strip().lower()
                if expand in ['y', 'yes']:
                    print(text[1000:])
            else:
                print(text)
        elif isinstance(content, BetaToolUseBlock):
            print_colored(f"\n🔧 Tool Use: {content.name}", Colors.BOLD + Colors.YELLOW)
            # Format tool input better
            input_str = str(content.input)
            if len(input_str) > 200:
                print(f"Input: {input_str[:200]}...")
                expand = input(f"{Colors.DIM}[Show full input? (y/N)]: {Colors.END}").strip().lower()
                if expand in ['y', 'yes']:
                    print(f"Full Input: {input_str}")
            else:
                print(f"Input: {input_str}")
        elif isinstance(content, dict) and show_thinking:
            if content.get("type") == "thinking":
                thinking_text = content.get("thinking", "")
                token_count = len(thinking_text.split()) * 1.3 if thinking_text else 0
                print_colored(f"\n🧠 Claude's Thinking (~{int(token_count)} tokens):", Colors.BOLD + Colors.PURPLE)
                if thinking_text:
                    # Show first few lines of thinking with option to see more
                    lines = thinking_text.split('\n')
                    preview_lines = lines[:5]  # Show more lines by default
                    print('\n'.join(preview_lines))
                    if len(lines) > 5:
                        show_more = input(f"{Colors.CYAN}Show full thinking process? (y/N): {Colors.END}").strip().lower()
                        if show_more in ['y', 'yes']:
                            print('\n'.join(lines[5:]))
                else:
                    print("Thinking content not available")
            elif content.get("type") == "redacted_thinking":
                print_colored(f"\n🧠 Claude's Thinking (Redacted):", Colors.BOLD + Colors.PURPLE)
                print("Some internal reasoning was encrypted for safety.")
        else:
            print_colored(f"\n🤖 Claude:", Colors.BOLD + Colors.GREEN)
            print(f"{content}")
    elif role == "tool":
        tool_result = cast(ToolResult, content)
        print_colored(f"\n⚙️  Tool Result:", Colors.BOLD + Colors.CYAN)
        if tool_result.output:
            output = tool_result.output
            # Handle long outputs better
            if len(output) > 500:
                print(f"{output[:500]}...")
                expand = input(f"{Colors.DIM}[Show full output? (y/N)]: {Colors.END}").strip().lower()
                if expand in ['y', 'yes']:
                    print(output[500:])
            else:
                print(output)
        if tool_result.error:
            print_colored(f"❌ Error: {tool_result.error}", Colors.RED)

def handle_special_commands(user_input: str, session_manager: SessionManager, messages: List[Dict], metadata: Dict) -> tuple[bool, str]:
    """Handle special CLI commands"""
    command = user_input.strip().lower()
    
    if command == '/help':
        print_colored("\n🆘 Special Commands:", Colors.BOLD + Colors.CYAN)
        commands = [
            "/help - Show this help",
            "/save - Save current session",
            "/load - Load a session",
            "/sessions - List saved sessions", 
            "/clear - Clear current conversation",
            "/status - Show current status",
            "/thinking - Toggle thinking display",
            "/exit or /quit - Exit the application"
        ]
        for cmd in commands:
            print(f"  {cmd}")
        return True, ""
    
    elif command == '/save':
        session_manager.save_session(messages, metadata)
        return True, ""
    
    elif command == '/load':
        session_manager.list_sessions()
        session_file = input(f"{Colors.CYAN}Enter session filename (or press Enter for most recent): {Colors.END}").strip()
        loaded_messages, loaded_metadata = session_manager.load_session(session_file if session_file else None)
        if loaded_messages:
            messages.clear()
            messages.extend(loaded_messages)
            metadata.update(loaded_metadata)
        return True, ""
    
    elif command == '/sessions':
        session_manager.list_sessions()
        return True, ""
    
    elif command == '/clear':
        confirm = input(f"{Colors.YELLOW}Clear current conversation? (y/N): {Colors.END}").strip().lower()
        if confirm in ['y', 'yes']:
            messages.clear()
            print_colored("🧹 Conversation cleared", Colors.GREEN)
        return True, ""
    
    elif command == '/status':
        print_colored(f"\n📊 Current Status:", Colors.BOLD + Colors.CYAN)
        print(f"  Messages: {len(messages)}")
        print(f"  Model: {metadata.get('model', 'Unknown')}")
        print(f"  Extended Thinking: {metadata.get('thinking_enabled', False)}")
        print(f"  Session Active: {session_manager.current_session is not None}")
        return True, ""
    
    elif command in ['/exit', '/quit']:
        return True, "exit"
    
    return False, ""

async def chat_loop(
    provider: APIProvider,
    model: str,
    api_key: str,
    enable_extended_thinking: bool,
    thinking_budget_tokens: int,
    max_tokens: int | None = None,
    custom_system_prompt: str = "",
    max_images: int = 10,
    load_session: bool = False
):
    """Enhanced chat loop with better error handling and features"""
    session_manager = SessionManager()
    messages = []
    tools_state = {}
    responses_state = {}
    show_thinking = True
    
    # Session metadata
    metadata = {
        "model": model,
        "thinking_enabled": enable_extended_thinking,
        "thinking_budget": thinking_budget_tokens,
        "start_time": datetime.now().isoformat()
    }
    
    # Load session if requested
    if load_session:
        loaded_messages, loaded_metadata = session_manager.load_session()
        if loaded_messages:
            messages = loaded_messages
            metadata.update(loaded_metadata)
    
    print_colored(f"\n💬 Chat started with {model}", Colors.BOLD + Colors.GREEN)
    if enable_extended_thinking:
        print_colored(f"🧠 Extended Thinking enabled ({thinking_budget_tokens:,} tokens)", Colors.PURPLE)
    print_colored("Type '/help' for commands, 'exit', 'quit', or press Ctrl+C to end.", Colors.YELLOW)
    print_colored("=" * 70, Colors.WHITE)
    
    # Setup signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print_colored("\n\n🔄 Saving session before exit...", Colors.YELLOW)
        if messages:
            session_manager.save_session(messages, metadata)
        print_colored("Goodbye! 👋", Colors.GREEN)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        try:
            # Show status bar
            print_status_bar(model, enable_extended_thinking, len(messages), session_manager.current_session is not None)
            
            # Get user input
            user_input = input(f"\n{Colors.BOLD + Colors.BLUE}You: {Colors.END}").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                if messages:
                    save_choice = input(f"{Colors.CYAN}Save session before exit? (Y/n): {Colors.END}").strip().lower()
                    if save_choice not in ['n', 'no']:
                        session_manager.save_session(messages, metadata)
                print_colored("\nGoodbye! 👋", Colors.GREEN)
                break
            
            if not user_input:
                continue
            
            # Handle special commands
            is_command, command_result = handle_special_commands(user_input, session_manager, messages, metadata)
            if is_command:
                if command_result == "exit":
                    break
                continue
            
            # Add user message
            messages.append({
                "role": "user",
                "content": [TextBlock(type="text", text=user_input)]
            })
            
            # Create progress indicator
            progress = ProgressIndicator("Claude is processing your request")
            progress_task = asyncio.create_task(progress.start())
            
            # Run the sampling loop with better error handling
            try:
                start_time = time.time()
                messages = await sampling_loop(
                    system_prompt_suffix=custom_system_prompt,
                    model=model,
                    provider=provider,
                    messages=messages,
                    output_callback=lambda content: render_message_cli("assistant", content, show_thinking),
                    tool_output_callback=lambda tool_output, tool_id: (
                        tools_state.update({tool_id: tool_output}),
                        render_message_cli("tool", tool_output)
                    )[1],
                    api_response_callback=lambda response: responses_state.update({len(responses_state): response}),
                    api_key=api_key,
                    only_n_most_recent_images=max_images,
                    max_tokens=max_tokens,
                    enable_extended_thinking=enable_extended_thinking,
                    thinking_budget_tokens=thinking_budget_tokens,
                )
                
                # Stop progress and show timing
                progress.stop()
                progress_task.cancel()
                elapsed = time.time() - start_time
                print_colored(f"{Colors.DIM}⏱️  Response generated in {elapsed:.1f}s{Colors.END}", Colors.DIM)
                
            except Exception as e:
                # Stop progress indicator
                progress.stop()
                progress_task.cancel()
                
                error_msg = str(e)
                print_colored(f"\n❌ Error: {error_msg}", Colors.RED)
                
                # Offer recovery options
                print_colored("\n🔧 Recovery Options:", Colors.YELLOW)
                print("1. Try again")
                print("2. Modify your request")  
                print("3. Continue with conversation")
                print("4. Exit")
                
                choice = input(f"{Colors.CYAN}Choose option (1-4): {Colors.END}").strip()
                if choice == "4":
                    break
                elif choice == "1":
                    # Remove the failed message and try again
                    if messages and messages[-1]["role"] == "user":
                        messages.pop()
                    continue
                elif choice == "2":
                    # Remove the failed message and ask for new input
                    if messages and messages[-1]["role"] == "user":
                        messages.pop()
                    continue
                else:
                    # Continue with conversation
                    continue
                
        except KeyboardInterrupt:
            print_colored("\n\n🔄 Saving session...", Colors.YELLOW)
            if messages:
                session_manager.save_session(messages, metadata)
            print_colored("Goodbye! 👋", Colors.GREEN)
            break
        except EOFError:
            print_colored("\n\nGoodbye! 👋", Colors.GREEN)
            break

async def main():
    """Enhanced main CLI application"""
    parser = argparse.ArgumentParser(description="Claude Computer Use for Mac - CLI Version")
    parser.add_argument("--provider", choices=[p.value for p in APIProvider], 
                       default=APIProvider.ANTHROPIC, help="API provider to use")
    parser.add_argument("--model", help="Specific model to use")
    parser.add_argument("--api-key", help="API key (will prompt if not provided)")
    parser.add_argument("--no-thinking", action="store_true", help="Disable extended thinking")
    parser.add_argument("--thinking-budget", type=int, default=10000, 
                       help="Thinking budget in tokens (default: 10000)")
    parser.add_argument("--max-tokens", type=int, help="Maximum output tokens")
    parser.add_argument("--max-images", type=int, default=10, 
                       help="Maximum recent images to keep (default: 10)")
    parser.add_argument("--system-prompt", help="Custom system prompt suffix")
    parser.add_argument("--load-session", action="store_true", help="Load most recent session on startup")
    parser.add_argument("--auto-save", action="store_true", help="Auto-save session every 10 messages")
    
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Set up provider
    provider = APIProvider(args.provider)
    print_colored(f"📡 Provider: {provider.title()}", Colors.CYAN)
    
    # Get API key
    api_key = args.api_key or get_api_key(provider)
    
    # Validate authentication
    auth_error = validate_auth(provider, api_key)
    if auth_error:
        print_colored(f"❌ Authentication Error: {auth_error}", Colors.RED)
        return 1
    
    print_colored("✅ Authentication successful", Colors.GREEN)
    
    # Select model
    if args.model:
        model = args.model
        print_colored(f"📋 Using specified model: {model}", Colors.CYAN)
    else:
        model = select_model(provider)
    
    # Configure extended thinking
    if args.no_thinking or not model_supports_extended_thinking(model):
        enable_extended_thinking = False
        thinking_budget_tokens = 0
        if not model_supports_extended_thinking(model):
            print_colored(f"ℹ️  Extended Thinking not available for {model}", Colors.YELLOW)
    else:
        enable_extended_thinking, thinking_budget_tokens = configure_extended_thinking(model)
        if args.thinking_budget and enable_extended_thinking:
            thinking_budget_tokens = args.thinking_budget
    
    # Configure max tokens
    max_tokens = args.max_tokens or get_max_tokens_for_model(model)
    print_colored(f"📊 Max output tokens: {max_tokens:,}", Colors.CYAN)
    
    # Load custom system prompt
    custom_system_prompt = args.system_prompt or load_from_storage("system_prompt") or ""
    if custom_system_prompt:
        print_colored("📝 Using custom system prompt", Colors.CYAN)
    
    # Start chat loop
    await chat_loop(
        provider=provider,
        model=model,
        api_key=api_key,
        enable_extended_thinking=enable_extended_thinking,
        thinking_budget_tokens=thinking_budget_tokens,
        max_tokens=max_tokens,
        custom_system_prompt=custom_system_prompt,
        max_images=args.max_images,
        load_session=args.load_session
    )
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_colored("\n\nExiting...", Colors.YELLOW)
        sys.exit(0) 