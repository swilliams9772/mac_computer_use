# Claude Computer Use for Mac 🚀

Enhanced version of [Mac Computer Use](https://github.com/deedy/mac_computer_use), a fork of [Anthropic Computer Use](https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/README.md) optimized for macOS.

## 🆕 What's New

### Claude 4 Support
- **Claude Opus 4** - Most capable model for complex reasoning and coding
- **Claude Sonnet 4** - High-performance model with balanced capabilities
- Up to 64k output tokens (Sonnet 4) and 32k (Opus 4)

### Extended Thinking
- Step-by-step reasoning for complex tasks
- Configurable thinking budget (1k-32k+ tokens)
- Transparent problem-solving process

### Enhanced macOS Integration
- **AppleScript Tool** - Native macOS application automation
- **Silicon Tool** - Apple Silicon hardware monitoring
- **Shortcuts Integration** - Run macOS Shortcuts via command line
- **System Profiler** - Detailed hardware information

### Smart Model Selection
- Easy switching between Claude 3.5, 3.7, and 4 models
- Automatic tool version management
- Model-specific feature detection

## 🏗️ Architecture

### Supported Models

| Model | Use Case | Max Output | Tool Versions | Extended Thinking |
|-------|----------|------------|---------------|-------------------|
| **Claude Opus 4** | Most complex tasks, coding, analysis | 32k tokens | `*_20250124` + `text_editor_20250429` | ✅ |
| **Claude Sonnet 4** | High performance, balanced tasks | 64k tokens | `*_20250124` + `text_editor_20250429` | ✅ |
| **Claude Sonnet 3.7** | Extended thinking capabilities | 64k tokens | `*_20250124` + `text_editor_20250124` | ✅ |
| **Claude Sonnet 3.5 v2** | Previous generation intelligent model | 8k tokens | `*_20241022` | ❌ |
| **Claude Haiku 3.5** | Fast and efficient processing | 8k tokens | `*_20241022` | ❌ |

### Tool Collection

#### Core Tools (Anthropic)
- **Computer Tool** - Screen capture, mouse/keyboard control
- **Text Editor** - File editing with str_replace operations
- **Bash Tool** - Command line execution

#### Custom Tools (macOS)
- **AppleScript Tool** - macOS application automation
- **Silicon Tool** - Apple Silicon hardware monitoring

### Tool Version Matrix

#### Claude 4 Models (Latest)
- Computer: `computer_20250124` 
- Text Editor: `text_editor_20250429` (no `undo_edit`)
- Bash: `bash_20250124`
- AppleScript: `custom`
- Silicon: `custom`

#### Claude 3.7 Sonnet
- Computer: `computer_20250124`
- Text Editor: `text_editor_20250124` (includes `undo_edit`)
- Bash: `bash_20250124`
- AppleScript: `custom`
- Silicon: `custom`

#### Claude 3.5 Models (Legacy)
- Computer: `computer_20241022`
- Text Editor: `text_editor_20241022`
- Bash: `bash_20241022`
- AppleScript: `custom`
- Silicon: `custom`

## 🚀 Quick Start

### Prerequisites
- macOS 10.14+ (Monterey+ recommended)
- Python 3.11+
- Anthropic API key
- Homebrew (recommended)

### Installation

#### Quick Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd mac_computer_use-1

# Run the automated setup script
./setup.sh

# The script will automatically:
# - Install Homebrew (if needed)
# - Install Python 3.11+ and dependencies
# - Create virtual environment
# - Install all requirements
# - Create activation helper script
```

#### Manual Setup
```bash
# Clone the repository
git clone <repository-url>
cd mac_computer_use-1

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Run the Streamlit app
streamlit run app.py

# OR run the CLI version
python cli.py
```

### CLI Usage

The CLI version provides a terminal-based interface with advanced features:

```bash
# Basic usage (interactive model selection)
python cli.py

# Specific model with extended thinking
python cli.py --model claude-3-7-sonnet-20250219 --thinking-budget 15000

# Load previous session
python cli.py --load-session

# Full configuration
python cli.py \
  --model claude-sonnet-4-20250514 \
  --thinking-budget 20000 \
  --max-tokens 8192 \
  --system-prompt "You are an expert macOS automation assistant."
```

#### CLI Features
- **🧠 Extended Thinking** - Step-by-step reasoning display
- **💾 Session Persistence** - Save/load conversations
- **⚡ Progress Indicators** - Visual feedback for operations
- **🛠️ Error Recovery** - Smart error handling with retry options
- **📊 Status Tracking** - Real-time model and session status
- **🎨 Smart Output** - Automatic formatting and truncation

#### CLI Commands
Use these during CLI sessions:
- `/help` - Show available commands
- `/save` - Save current session
- `/load` - Load saved session
- `/clear` - Clear conversation
- `/status` - Show configuration
- `/exit` - Exit with optional save

### Environment Setup

```bash
# Install system dependencies
brew install cliclick

# Optional: Enable accessibility permissions
# System Preferences > Security & Privacy > Privacy > Accessibility
# Add Terminal and Python to allowed applications
```

## 🔧 Configuration

### Model Selection
Choose your model based on your needs:

- **Claude Opus 4** - Complex reasoning, advanced coding, research
- **Claude Sonnet 4** - Balanced performance for most tasks
- **Claude Sonnet 3.7** - Extended thinking, complex problem solving
- **Claude Haiku 3.5** - Fast, lightweight tasks

### Extended Thinking
When enabled, Claude will show its step-by-step reasoning:

```python
# Configuration options
enable_extended_thinking = True
thinking_budget_tokens = 10000  # 1k-32k+ recommended
```

### Custom Tools
The system includes custom macOS tools:

```python
# AppleScript automation
applescript_tool.execute(
    script='display dialog "Hello from Claude!"',
    application="Finder"  # Optional target
)

# Apple Silicon monitoring
silicon_tool.monitor(
    action="performance",  # performance, thermal, memory, system_info
    target=None
)
```

## 📁 Project Structure

```
mac_computer_use-1/
├── tools/                      # Tool implementations
│   ├── __init__.py            # Tool exports
│   ├── base.py                # Base tool classes
│   ├── collection.py          # Tool collection manager
│   ├── computer.py            # Computer use tool
│   ├── edit.py                # Text editor tool
│   ├── bash.py                # Bash execution tool
│   ├── applescript.py         # AppleScript automation (custom)
│   ├── silicon.py             # Apple Silicon monitoring (custom)
│   └── run.py                 # Command execution utilities
├── loop.py                    # Main sampling loop
├── app.py                     # Streamlit UI
├── cli.py                     # CLI interface
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
└── README.md                  # This file
```

## 🎯 Usage Examples

### Basic Computer Use
```python
# Take a screenshot and analyze
# Claude can see the screen and interact with applications

# Navigate to a website
# Claude can control mouse and keyboard

# Edit files
# Claude can read, write, and modify files
```

### AppleScript Automation
```python
# Control macOS applications
applescript_tool.execute(
    script='''
    tell application "Safari"
        make new document
        set URL of current tab to "https://anthropic.com"
    end tell
    ''',
    application="Safari"
)
```

### System Monitoring
```python
# Check Apple Silicon performance
silicon_tool.monitor(action="performance")

# Monitor thermal status
silicon_tool.monitor(action="thermal")

# Check memory usage
silicon_tool.monitor(action="memory")
```

## 🔐 Security & Privacy

- **Screen Access** - Required for computer tool functionality
- **Accessibility** - Needed for mouse/keyboard control
- **API Keys** - Stored locally, never transmitted except to Anthropic
- **Local Execution** - All tools run locally on your machine

## 🐛 Troubleshooting

### Common Issues

1. **Tool Type Validation Error**
   ```
   Input tag 'applescript_20250124' found using 'type' does not match any of the expected tags
   ```
   **Solution**: Custom tools now use `type: "custom"` - this is fixed in the latest version.

2. **Extended Thinking Not Available**
   ```
   Model does not support extended thinking
   ```
   **Solution**: Use Claude 3.7, Sonnet 4, or Opus 4 models.

3. **Max Tokens Exceeded**
   ```
   prompt tokens + max_tokens exceeds context window
   ```
   **Solution**: Reduce `max_tokens` or enable image filtering.

### Performance Tips

- Use **Claude Haiku 3.5** for fast, simple tasks
- Enable **Extended Thinking** for complex reasoning
- Set appropriate **thinking budget** (10k default, 32k+ for complex tasks)
- Use **image filtering** to manage context window

## 🛠️ Development

### Adding Custom Tools

1. Create tool class in `tools/` directory
2. Inherit from `BaseAnthropicTool`
3. Set `api_type = "custom"`
4. Implement `__call__` and `to_params` methods
5. Add to `ToolCollection` in `loop.py`

### Testing

```bash
# Run basic tests
python -m pytest tests/

# Test specific tool
python -c "from tools import AppleScriptTool; print('✅ Import successful')"

# Verify API connectivity
python -c "import anthropic; print('✅ Anthropic SDK ready')"
```

## 📋 Requirements

### System Requirements
- macOS 10.14+ (Monterey+ recommended for full features)
- Python 3.11+
- 8GB+ RAM (16GB+ recommended for extended thinking)
- Internet connection for API calls

### Python Dependencies
See `requirements.txt` for complete list:
- anthropic>=0.40.0
- streamlit>=1.40.0
- pillow>=10.0.0
- And others...

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the same terms as the original Anthropic Computer Use demo.

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for Claude and Computer Use tools
- [Original Computer Use Demo](https://github.com/anthropics/anthropic-quickstarts)
- [Mac Computer Use](https://github.com/deedy/mac_computer_use) fork
- macOS and Apple Silicon optimization community
