#!/usr/bin/env python3
"""
Verify that the environment is properly set up for running the application.
"""

import os
import sys
import shutil
import subprocess
import importlib.util
import pkg_resources

def check_python_version():
    """Check if Python version is 3.12 or higher."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 12):
        print("❌ Error: Python 3.12 or higher is required.")
        print(f"   Current version: {major}.{minor}")
        print("   Please install Python 3.12 or higher.")
        return False
    print(f"✅ Python version: {major}.{minor}")
    return True

def check_dependencies():
    """Check if required Python dependencies are installed."""
    required_packages = [
        "streamlit>=1.38.0", 
        "anthropic>=0.49.0",
        "keyboard>=0.13.5",
        "pyautogui>=0.9.54",
        "python-dotenv>=1.0.1"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        package_name = package.split(">=")[0].split(">")[0].split("==")[0].split("<")[0]
        try:
            pkg_resources.get_distribution(package_name)
            print(f"✅ Found package: {package_name}")
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package_name)
            print(f"❌ Missing package: {package_name}")
    
    if missing_packages:
        print("\nMissing dependencies. Please run:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_cliclick():
    """Check if cliclick is installed."""
    if not shutil.which("cliclick"):
        print("❌ cliclick is not installed.")
        print("   Please install it with: brew install cliclick")
        return False
    print("✅ cliclick is installed")
    return True

def check_anthropic_sdk_version():
    """Check if the Anthropic SDK version supports Claude 3.7 Sonnet thinking."""
    try:
        import anthropic
        version = anthropic.__version__
        print(f"✅ Anthropic SDK version: {version}")
        
        # Parse version number
        major, minor, patch = map(int, version.split("."))
        
        if major < 0 or (major == 0 and minor < 20):
            print("❌ Warning: Anthropic SDK version may not support Claude 3.7 thinking.")
            print("   Please upgrade with: pip install --upgrade anthropic")
            return False
        return True
    except (ImportError, AttributeError):
        print("❌ Could not determine Anthropic SDK version.")
        return False

def check_api_key():
    """Check if the Anthropic API key is set."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Check if it might be in a .env file
        if os.path.exists(".env"):
            print("⚠️ ANTHROPIC_API_KEY not found in environment, but .env file exists.")
            print("   Will try to load from .env file during runtime.")
        else:
            print("⚠️ ANTHROPIC_API_KEY not set and no .env file found.")
            print("   Please set your API key in the sidebar or in a .env file.")
        return False
    
    print("✅ ANTHROPIC_API_KEY is set")
    return True

def main():
    """Run all checks."""
    print("Verifying environment for Mac Computer Use...\n")
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_cliclick(),
        check_anthropic_sdk_version(),
        check_api_key()
    ]
    
    if all(checks):
        print("\n✅ All checks passed! You're ready to run the application.")
        print("   Run: streamlit run streamlit.py")
        return 0
    else:
        print("\n⚠️ Some checks failed. Please fix the issues above before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 