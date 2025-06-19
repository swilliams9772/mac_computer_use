# Anthropic Computer Use (for Mac) - Enhanced with Claude 4 🚀

[Anthropic Computer Use](https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/README.md) is a beta Anthropic feature which runs a Docker image with Ubuntu and controls it. This **enhanced fork** allows you to run it natively on macOS with **Claude 3.7 and Claude 4 support**, providing direct system control through native macOS commands and utilities.

> [!CAUTION]
> This comes with obvious risks. The Anthropic agent can control everything on your Mac. Please be careful.
> Anthropic's new Claude models refuse to do unsafe things like purchase items or download illegal content.

## 🆕 New Features (Enhanced Version)

### 🔄 **Automatic Tool Version Selection** (Latest Update)
- **Smart API Versioning** - Automatically selects the correct tool versions based on your chosen model
- **Future-Proof** - Always uses the latest available tool capabilities for each Claude model
- **Backward Compatible** - Maintains support for older Claude 3.5 workflows unchanged

### 🧠 **Claude 4 Support** 
- **Latest Models** - Access to Claude Opus 4 & Sonnet 4 (May 2025)
- **Enhanced Computer Actions** - New actions like `triple_click`, `scroll`, `hold_key`, `wait`
- **Advanced Text Editor** - `str_replace_based_edit_tool` with optimized performance
- **64k Output Tokens** - Handle larger, more complex tasks

### 🔬 **Extended Thinking**
- **Step-by-Step Reasoning** - Claude's transparent thought process for complex tasks
- **Interleaved Thinking** - Think between tool calls for better decision-making
- **Adjustable Budget** - Control thinking depth (1k-32k tokens)

### 🎯 **Smart Model Selection**
- **Easy Switching** - Seamless transition between Claude 3.5, 3.7, and 4 models
- **Optimized Performance** - Each model gets its ideal tool configuration
- **Latest API Compliance** - Uses `computer-use-2025-01-24` beta flag for Claude 4/3.7

## Core Features

- **Native macOS Integration** - No Docker required, direct system control
- **Advanced Computer Actions** - Enhanced mouse, keyboard, and screen interaction
- **Multi-Provider Support** - Anthropic, AWS Bedrock, Google Vertex AI
- **Modern Streamlit UI** - Enhanced interface with debugging tools
- **Automatic Scaling** - Screen resolution optimization
- **File System Integration** - Advanced text editing and file management

## Prerequisites

- macOS Sonoma 15.7 or later
- Python 3.12+
- Homebrew (for installing additional dependencies)
- cliclick (`brew install cliclick`) - Required for mouse and keyboard control

## Setup Instructions

1. Clone the repository and navigate to it:

```bash
git clone https://github.com/deedy/mac_computer_use.git
cd mac_computer_use
```

2. Run the automated setup script (recommended):

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Install Python 3.12 if needed
- Create a virtual environment
- Install all dependencies
- Set up the activation script

3. Alternative manual setup:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Demo

### 🎯 Quick Start with Claude 4

1. Set your API key and run:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
export WIDTH=1280
export HEIGHT=800
streamlit run streamlit.py
```

2. In the sidebar:
   - Select **Claude Sonnet 4** or **Claude Opus 4** for best performance
   - Enable **Extended Thinking** for complex reasoning tasks
   - Adjust the thinking budget for thorough analysis

### Environment Configuration

Create a `.env` file for persistent settings:

```env
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here
WIDTH=1280
HEIGHT=800
DISPLAY_NUM=1
```

Available API providers:
- `anthropic` - Direct Anthropic API (recommended)
- `bedrock` - AWS Bedrock
- `vertex` - Google Cloud Vertex AI

## Model Selection Guide

### 🚀 **Recommended: Claude 4 Models**

| Model | Best For | Max Output | Tools | Extended Thinking |
|-------|----------|------------|-------|-------------------|
| **Claude Opus 4** | Most complex tasks, coding, analysis | 32k tokens | `*_20250124` + `text_editor_20250429` | ✅ |
| **Claude Sonnet 4** | High performance, balanced tasks | 64k tokens | `*_20250124` + `text_editor_20250429` | ✅ |

### 🧪 **Experimental: Claude 3.7**

| Model | Best For | Max Output | Tools | Extended Thinking |
|-------|----------|------------|-------|-------------------|
| **Claude 3.7 Sonnet** | Extended thinking experiments | 64k tokens | `*_20250124` | ✅ |

### 🔄 **Legacy: Claude 3.5 Models**

| Model | Best For | Max Output | Tools | Extended Thinking |
|-------|----------|------------|-------|-------------------|
| **Claude 3.5 Sonnet** | General purpose, reliable | 8k tokens | `*_20241022` | ❌ |
| **Claude 3.5 Haiku** | Fast responses, simple tasks | 8k tokens | `*_20241022` | ❌ |

## 🔧 Enhanced Computer Actions (Claude 4/3.7)

The latest tool versions include powerful new computer actions:

### **New Actions Available:**
- **`triple_click`** - Select entire paragraphs/lines of text
- **`scroll`** - Precise scrolling with direction and amount control
- **`hold_key`** - Hold keys for specified durations
- **`wait`** - Programmatic pauses for timing control
- **`left_mouse_down` / `left_mouse_up`** - Separate mouse press/release actions

### **Enhanced Parameters:**
- **`scroll_direction`** - up, down, left, right
- **`scroll_amount`** - Number of scroll clicks
- **`duration`** - For hold_key and wait actions
- **`start_coordinate`** - Enhanced drag operations

## Extended Thinking Feature

When using Claude 4 or 3.7 models, you can enable **Extended Thinking** for more thorough reasoning:

1. **Enable in Sidebar**: Check "Enable Extended Thinking"
2. **Set Budget**: Adjust thinking budget (1k-32k tokens)
3. **View Process**: Claude's reasoning appears in expandable sections

**Benefits:**
- Step-by-step problem solving
- Better handling of complex computer tasks
- More reliable decision making
- Transparent reasoning process

## Screen Size Considerations

Recommended resolutions for optimal performance:

- **Preferred**: 1280x800 (16:10) - Best balance
- **Alternative**: 1024x768 (4:3) - Classic
- **Widescreen**: 1366x768 (~16:9) - Modern

Higher resolutions are automatically scaled down to optimize model performance.

```bash
export WIDTH=1280
export HEIGHT=800
streamlit run streamlit.py
```

## Advanced Configuration

### Custom System Prompts

Add custom instructions in the sidebar under "Advanced Settings" to customize Claude's behavior for specific tasks.

### Token Management

- **Auto-scaling**: Max tokens automatically set based on model
- **Manual override**: Adjust in Advanced Settings
- **Thinking budget**: Higher budgets enable deeper reasoning

### Multiple Providers

Switch between providers in the sidebar:
- **Anthropic**: Latest models, extended thinking
- **Bedrock**: Enterprise AWS integration  
- **Vertex**: Google Cloud integration

## 🔄 Tool Version Management

This implementation automatically selects the optimal tool versions:

### **Claude 4 Models (Opus/Sonnet 4)**
- Computer Tool: `computer_20250124` 
- Text Editor: `text_editor_20250429` (no `undo_edit`)
- Bash Tool: `bash_20250124`
- Beta Flag: `computer-use-2025-01-24`

### **Claude 3.7 Sonnet**
- Computer Tool: `computer_20250124`
- Text Editor: `text_editor_20250124` (with `undo_edit`)
- Bash Tool: `bash_20250124` 
- Beta Flag: `computer-use-2025-01-24`

### **Claude 3.5 Models (Legacy)**
- Computer Tool: `computer_20241022`
- Text Editor: `text_editor_20241022` (with `undo_edit`)
- Bash Tool: `bash_20241022`
- Beta Flag: `computer-use-2024-10-22`

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure cliclick is installed (`brew install cliclick`)
2. **API Errors**: Verify your API key is valid and has sufficient credits
3. **Screen Capture**: Grant screen recording permissions in System Preferences
4. **Extended Thinking**: Only works with Claude 4 and 3.7 models
5. **Tool Errors**: Check that you're using a supported model for enhanced actions

### Performance Tips

- Use **Claude Sonnet 4** for best speed/performance balance
- Enable **Extended Thinking** only for complex tasks
- Adjust **thinking budget** based on task complexity
- Use **image filtering** to reduce token usage
- **Claude 4** models work best with new enhanced computer actions

## API Documentation

This implementation uses the latest Anthropic API features:

- [Claude 4 Models](https://docs.anthropic.com/en/docs/about-claude/models) - Latest model capabilities
- [Extended Thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking) - Advanced reasoning
- [Computer Use API](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use) - Enhanced computer control
- [Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) - Latest tool versions

> [!IMPORTANT]
> This implementation automatically uses the latest tool versions and beta flags. It's fully compliant with the current Anthropic API as of May 2025. The tools adapt to your selected model for optimal performance.

## Contributing

This enhanced version builds upon the original Mac Computer Use project. Contributions are welcome for:

- Additional model integrations
- Enhanced computer actions
- UI/UX improvements  
- Performance optimizations
- Documentation updates

## License

Same license as the original Anthropic Computer Use demo.
