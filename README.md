# Anthropic Computer Use (for Mac)

[Anthropic Computer Use](https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/README.md) is a beta Anthropic feature which runs a Docker image with Ubuntu and controls it. This fork allows you to run it natively on macOS, providing direct system control through native macOS commands and utilities.

> [!CAUTION]
> This comes with obvious risks. The Anthropic agent can control everything on your Mac. Please be careful.
> Anthropic's new Claude 3.5 Sonnet model refuses to do unsafe things like purchase items or download illegal content.

## Features

- Native macOS GUI interaction (no Docker required)
- Screen capture using native macOS commands
- Keyboard and mouse control through cliclick
- Multiple LLM provider support (Anthropic, Bedrock, Vertex)
- Support for Claude 3.5 Sonnet and Claude 3.7 Sonnet models
- Claude 3.7 Sonnet "thinking" mode for more thorough reasoning
- Streamlit-based interface with enhanced user experience
- Automatic screen resolution scaling
- File system interaction and editing capabilities
- Robust error handling and user feedback
- Visual progress indicators for thinking processes

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

2. Create and activate a virtual environment:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

3. Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

4. Install Python requirements:

```bash
pip install -r requirements.txt
```

5. Verify your environment setup:

```bash
python verify_env.py
```

This script checks that all required dependencies are correctly installed and configured before running the application.

## Running the Demo

### Set up your environment and Anthropic API key

1. In a `.env` file add:

```
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=<key>
WIDTH=800
HEIGHT=600
DISPLAY_NUM=1
```

Set the screen dimensions (recommended: stay within XGA/WXGA resolution), and put in your key from [Anthropic Console](https://console.anthropic.com/settings/keys).

2. Start the Streamlit app:

```bash
streamlit run streamlit.py
```

The interface will be available at http://localhost:8501

## Using Claude 3.7 Sonnet with Thinking

This fork now supports Claude 3.7 Sonnet with its "thinking" capabilities. When enabled, Claude will show its step-by-step reasoning process, providing transparency into how it arrives at its responses. This can be particularly helpful for complex tasks.

To use this feature:

1. Select "Claude 3.7 Sonnet" from the model dropdown in the sidebar
2. Enable the "Enable Thinking" checkbox
3. Start chatting with Claude

The application will automatically allocate a token budget for thinking (approximately half of the max_tokens setting). The thinking feature helps Claude perform complex tasks by allowing it to work through problems step-by-step, resulting in more accurate and reliable task execution.

### Production-Ready Features

This application includes several production-ready features:

- **Comprehensive Error Handling**: The application catches and handles errors gracefully, providing clear feedback to users
- **Visual Progress Indicators**: When using the thinking feature, a progress bar shows the thinking process
- **Intuitive UI**: Clear indicators show which models support the thinking feature
- **Automatic Token Budget Management**: The application automatically allocates an appropriate thinking budget
- **Support for Multiple API Providers**: Works with Anthropic, AWS Bedrock, and Google Vertex AI
- **Detailed Error Messages**: User-friendly error descriptions with specific troubleshooting instructions

### Troubleshooting

If you encounter errors:

1. **Thinking Parameter Issues**: Make sure you have the latest Anthropic SDK (v0.49.0+) and application code
```bash
pip install --upgrade "anthropic[bedrock,vertex]>=0.49.0"
```

   According to the latest AWS documentation, the thinking parameter for Claude 3.7 Sonnet should use the following format:
   
   ```json
   "thinking": {
       "type": "enabled",
       "budget_tokens": 16000
   }
   ```
   
   If you see errors about "thinking: Input tag does not match any of the expected tags", make sure you're using the latest version of the application that uses the correct parameter format.

2. **Tool Type Compatibility**: Claude 3.7 Sonnet requires newer tool types than Claude 3.5 Sonnet.
   
   For Claude 3.5 Sonnet, use:
   ```
   computer_20241022
   bash_20241022
   text_editor_20241022
   ```
   
   For Claude 3.7 Sonnet, use:
   ```
   bash_20250124
   text_editor_20250124
   ```
   
   **Note**: Unlike Claude 3.5 Sonnet, Claude 3.7 Sonnet does **not** support the `computer_20250124` tool type.
   
   The application now automatically selects the correct tool types based on the model you choose.

3. **Beta Flag Compatibility**: Claude 3.7 Sonnet does not require the beta flag that Claude 3.5 Sonnet needs.
   
   If you see an error like: `Unexpected value(s) for the anthropic-beta header`, the application has been updated to not send beta flags to Claude 3.7 Sonnet models.

4. **API Key Errors**: Verify your API key is correct in the sidebar or .env file

5. **Model Availability**: Ensure you've selected an available model for your API provider

6. **Rate Limiting**: If you encounter rate limit errors, wait a few moments before retrying

## Screen Size Considerations

We recommend using one of these resolutions for optimal performance:

-   XGA: 1024x768 (4:3)
-   WXGA: 1280x800 (16:10)
-   FWXGA: 1366x768 (~16:9)

Higher resolutions will be automatically scaled down to these targets to optimize model performance. You can set the resolution using environment variables:

```bash
export WIDTH=1024
export HEIGHT=768
streamlit run streamlit.py
```

> [!IMPORTANT]
> The Beta API used in this reference implementation is subject to change. Please refer to the [API release notes](https://docs.anthropic.com/en/release-notes/api) for the most up-to-date information.
