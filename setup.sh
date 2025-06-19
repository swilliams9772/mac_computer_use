#!/bin/bash

# Claude Computer Use for Mac - Setup Script
# Enhanced setup for both CLI and Streamlit interfaces

set -e  # Exit on any error

echo "🚀 Claude Computer Use for Mac - Setup"
echo "Enhanced with Claude 3.7 & Claude 4 🧠 • Optimized for macOS 💫"
echo "================================================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS only."
    exit 1
fi

echo "✅ Running on macOS"

# Install Homebrew (if not installed)
if ! command -v brew &>/dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew is already installed"
fi

# Install Python 3.11+ if not available
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2 || echo "0.0")
required_version="3.11"

if ! command -v python3 &>/dev/null || [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "🐍 Installing Python 3.12..."
    brew install python@3.12
    
    # Create symlink for python3 if needed
    if ! command -v python3 &>/dev/null; then
        ln -sf $(brew --prefix)/bin/python3.12 $(brew --prefix)/bin/python3
    fi
else
    echo "✅ Python $python_version is installed"
fi

# Install cliclick for computer control
if ! command -v cliclick &>/dev/null; then
    echo "🖱️  Installing cliclick for mouse/keyboard control..."
    brew install cliclick
else
    echo "✅ cliclick is already installed"
fi

# Verify screencapture (pre-installed on macOS)
if ! command -v screencapture &>/dev/null; then
    echo "❌ screencapture not found. Please ensure you're on macOS."
    exit 1
else
    echo "✅ screencapture is available"
fi

echo ""
echo "🔧 Setting up Python environment..."

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf venv
fi

# Create fresh virtual environment
echo "📦 Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Verify Python version in venv
python_venv_version=$(python --version)
echo "✅ Using $python_venv_version in virtual environment"

# Update pip
echo "📈 Updating pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "🎯 Setup completed successfully!"
echo ""

# Create activation script
echo "📝 Creating activation helper script..."
cat > activate.sh << 'EOL'
#!/bin/bash
# Activate virtual environment for Claude Computer Use

source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "🚀 Virtual environment activated!"
echo ""
echo "Available interfaces:"
echo "1. 🖥️  CLI Interface (recommended for advanced users):"
echo "   python cli.py"
echo ""
echo "2. 🌐 Streamlit Web Interface:"
echo "   streamlit run app.py"
echo ""
echo "🔑 Don't forget to set your API key:"
echo "   export ANTHROPIC_API_KEY=your_api_key_here"
echo ""
echo "📖 For help with CLI commands, run:"
echo "   python cli.py --help"
EOL

chmod +x activate.sh

echo ""
echo "================================================================="
echo "✅ Setup Complete! 🎉"
echo "================================================================="
echo ""
echo "🚀 Quick Start:"
echo "1. Set your Anthropic API key:"
echo "   export ANTHROPIC_API_KEY=your_api_key_here"
echo ""
echo "2. Choose your interface:"
echo ""
echo "   🖥️  CLI Interface (Terminal-based):"
echo "   python cli.py"
echo ""
echo "   🌐 Streamlit Interface (Web-based):"
echo "   streamlit run app.py"
echo ""
echo "🧠 Claude 4 Features Available:"
echo "   • Extended thinking for complex reasoning"
echo "   • Up to 64k output tokens (Sonnet 4)"
echo "   • Advanced computer use capabilities"
echo "   • Session persistence (CLI only)"
echo "   • Smart error recovery (CLI only)"
echo ""
echo "📖 For detailed usage instructions, see README.md"
echo ""
echo "💡 Pro tip: Use 'source activate.sh' to quickly set up your environment"
echo ""

# Test basic imports
echo "🧪 Running setup verification..."
python -c "
try:
    import anthropic
    import streamlit
    from tools import ComputerTool, BashTool, EditTool, AppleScriptTool, SiliconTool
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo "✅ Setup verification complete!"
echo ""
echo "🎯 Ready to use Claude Computer Use for Mac!"

# Auto-activate for current session
source activate.sh 