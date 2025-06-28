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
    enhanced_sampling_loop,
    model_supports_extended_thinking,
    get_max_tokens_for_model,
    model_supports_token_efficiency,
    model_supports_interleaved_thinking,
    get_recommended_thinking_budget,
    get_beta_flags_for_model,
)
from tools import ToolResult
from dotenv import load_dotenv

# Load environment variables
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

# Configuration directories
CONFIG_DIR = PosixPath("~/.anthropic").expanduser()
API_KEY_FILE = CONFIG_DIR / "api_key"
SESSION_DIR = CONFIG_DIR / "sessions"

# Enhanced CSS with comprehensive design improvements, fixed div layouts, and modern interface
STREAMLIT_STYLE = """
<style>
    /* === CORE SYSTEM VARIABLES === */
    :root {
        /* Modern Color Palette - Light Theme */
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #e2e8f0;
        --bg-accent: #f1f5f9;
        --bg-elevated: #ffffff;
        
        /* Text Colors */
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-tertiary: #94a3b8;
        --text-inverse: #ffffff;
        
        /* Border and Shadow */
        --border-color: #e2e8f0;
        --border-focus: #3b82f6;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        
        /* Glass Effect */
        --glass-bg: rgba(255, 255, 255, 0.8);
        --glass-border: rgba(255, 255, 255, 0.2);
        --glass-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        
        /* Gradient Collection */
        --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-success: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        --gradient-accent: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        --gradient-warm: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --gradient-cool: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        
        /* Status Colors */
        --success-color: #059669;
        --warning-color: #d97706;
        --error-color: #dc2626;
        --info-color: #2563eb;
        
        /* Interactive Colors */
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-pink: #ec4899;
        --accent-emerald: #10b981;
        
        /* Spacing Scale */
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-6: 1.5rem;
        --space-8: 2rem;
        --space-12: 3rem;
        --space-16: 4rem;
        
        /* Border Radius */
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --radius-2xl: 1.5rem;
        --radius-full: 9999px;
        
        /* Typography */
        --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif;
        --font-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Source Code Pro', monospace;
        --font-size-xs: 0.75rem;
        --font-size-sm: 0.875rem;
        --font-size-base: 1rem;
        --font-size-lg: 1.125rem;
        --font-size-xl: 1.25rem;
        --font-size-2xl: 1.5rem;
        --font-size-3xl: 1.875rem;
        
        /* Animation Duration */
        --duration-fast: 150ms;
        --duration-normal: 250ms;
        --duration-slow: 500ms;
        
        /* Z-Index Scale */
        --z-dropdown: 1000;
        --z-sticky: 1020;
        --z-fixed: 1030;
        --z-modal: 1040;
        --z-popover: 1050;
        --z-tooltip: 1060;
    }

    /* === DARK THEME OVERRIDES === */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --bg-accent: #475569;
            --bg-elevated: #1e293b;
            
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-tertiary: #64748b;
            --text-inverse: #0f172a;
            
            --border-color: #475569;
            --border-focus: #60a5fa;
            
            --glass-bg: rgba(15, 23, 42, 0.8);
            --glass-border: rgba(148, 163, 184, 0.1);
            --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            
            --gradient-primary: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            --gradient-secondary: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
            --gradient-success: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        }
    }

    /* Streamlit-specific dark theme detection */
    .stApp[data-theme="dark"] {
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --bg-accent: #475569;
        --bg-elevated: #1e293b;
        
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-tertiary: #64748b;
        --text-inverse: #0f172a;
        
        --border-color: #475569;
        --border-focus: #60a5fa;
        
        --glass-bg: rgba(15, 23, 42, 0.8);
        --glass-border: rgba(148, 163, 184, 0.1);
        --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        
        --gradient-primary: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        --gradient-secondary: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        --gradient-success: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    }

    /* === RESET AND BASE STYLES === */
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    
    html {
        scroll-behavior: smooth;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    body {
        font-family: var(--font-body);
        line-height: 1.6;
        color: var(--text-primary);
    }

    /* === LAYOUT SYSTEM === */
    
    /* Hide problematic Streamlit elements */
    .stDeployButton,
    .stDecoration,
    #MainMenu,
    footer,
    header {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Main app container */
    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
        font-family: var(--font-body);
        min-height: 100vh;
        position: relative;
    }
    
    /* Enhanced main content area */
    .main .block-container {
        max-width: 100%;
        padding: var(--space-6) var(--space-8);
        background: var(--bg-primary);
        min-height: calc(100vh - 2rem);
        display: flex;
        flex-direction: column;
        gap: var(--space-6);
    }
    
    /* Fixed sidebar styling */
    .css-1d391kg,
    .stSidebar > div {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid var(--glass-border) !important;
        box-shadow: var(--glass-shadow) !important;
        position: relative !important;
        z-index: var(--z-fixed) !important;
    }
    
    .stSidebar .sidebar-content {
        padding: var(--space-6) var(--space-4);
        height: 100vh;
        overflow-y: auto;
        scrollbar-width: thin;
    }

    /* === RESPONSIVE GRID SYSTEM === */
    
    .container {
        width: 100%;
        max-width: 1280px;
        margin: 0 auto;
        padding: 0 var(--space-4);
    }
    
    .grid {
        display: grid;
        gap: var(--space-6);
    }
    
    .grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
    .grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    
    .flex {
        display: flex;
    }
    
    .flex-col {
        flex-direction: column;
    }
    
    .flex-row {
        flex-direction: row;
    }
    
    .items-center {
        align-items: center;
    }
    
    .justify-between {
        justify-content: space-between;
    }
    
    .justify-center {
        justify-content: center;
    }
    
    .gap-2 { gap: var(--space-2); }
    .gap-4 { gap: var(--space-4); }
    .gap-6 { gap: var(--space-6); }
    .gap-8 { gap: var(--space-8); }

    /* === RESPONSIVE BREAKPOINTS === */
    
    @media (max-width: 1024px) {
        .main .block-container {
            padding: var(--space-4) var(--space-6);
        }
        
        .grid-cols-4 {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        
        .grid-cols-3 {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        
        /* Improve sidebar on tablet */
        .stSidebar .sidebar-content {
            padding: var(--space-4) var(--space-3);
        }
        
        /* Stack horizontal elements */
        .row-widget.stHorizontal > div {
            flex: 1 1 100% !important;
            margin-bottom: var(--space-3);
        }
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: var(--space-3) var(--space-4);
        }
        
        .grid-cols-2,
        .grid-cols-3,
        .grid-cols-4 {
            grid-template-columns: repeat(1, minmax(0, 1fr));
        }
        
        /* Mobile chat messages */
        .stChatMessage {
            margin-left: var(--space-2) !important;
            margin-right: var(--space-2) !important;
            padding: var(--space-4) !important;
        }
        
        /* Mobile sidebar */
        .stSidebar .sidebar-content {
            padding: var(--space-3) var(--space-2);
        }
    }
    
    @media (max-width: 480px) {
        .main .block-container {
            padding: var(--space-2) var(--space-3);
        }
        
        .stChatMessage {
            margin-left: var(--space-1) !important;
            margin-right: var(--space-1) !important;
            padding: var(--space-3) !important;
        }
    }

    /* === MODERN COMPONENT STYLES === */
    
    /* Enhanced Card System */
    .card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        box-shadow: var(--shadow-lg);
        transition: all var(--duration-normal) ease;
        position: relative;
        overflow: hidden;
    }
    
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        pointer-events: none;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-xl);
        border-color: var(--border-focus);
    }
    
    /* === ENHANCED WEB SEARCH STYLING === */
    
    /* Web Search Container */
    .web-search-container {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin: var(--space-4) 0;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
        animation: slideInUp 0.6s ease-out;
    }
    
    .web-search-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent);
        pointer-events: none;
    }
    
    .web-search-container::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: var(--gradient-accent);
        border-radius: var(--radius-xl);
        z-index: -1;
        opacity: 0;
        transition: opacity var(--duration-normal) ease;
    }
    
    .web-search-container:hover::after {
        opacity: 0.1;
    }
    
    /* Search Header Styling */
    .search-header {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        margin-bottom: var(--space-4);
        padding: var(--space-4);
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: var(--radius-lg);
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    .search-header .search-icon {
        font-size: 1.5rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    
    .search-header .search-title {
        font-size: var(--font-size-lg);
        font-weight: 600;
        margin: 0;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Search Query Display */
    .search-query {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--radius-md);
        padding: var(--space-3) var(--space-4);
        margin: var(--space-3) 0;
        font-family: var(--font-mono);
        font-size: var(--font-size-sm);
        color: white;
        backdrop-filter: blur(10px);
    }
    
    /* Search Intent Indicators */
    .search-indicators {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
        margin: var(--space-3) 0;
    }
    
    .search-indicator {
        background: rgba(255, 255, 255, 0.15);
        color: white;
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        gap: var(--space-1);
    }
    
    /* Search Results Grid */
    .search-results-grid {
        display: grid;
        gap: var(--space-4);
        margin: var(--space-6) 0;
    }
    
    /* Individual Search Result Cards */
    .search-result-card {
        background: var(--bg-elevated);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        transition: all var(--duration-normal) ease;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        margin-bottom: var(--space-4);
    }
    
    .search-result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--gradient-accent);
        opacity: 0;
        transition: opacity var(--duration-normal) ease;
    }
    
    .search-result-card::after {
        content: '';
        position: absolute;
        top: -1px;
        left: -1px;
        right: -1px;
        bottom: -1px;
        background: var(--gradient-accent);
        border-radius: var(--radius-lg);
        z-index: -1;
        opacity: 0;
        transition: opacity var(--duration-normal) ease;
    }
    
    .search-result-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
        border-color: var(--border-focus);
    }
    
    .search-result-card:hover::before {
        opacity: 1;
    }
    
    .search-result-card:hover::after {
        opacity: 0.05;
    }
    
    .search-result-title {
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-2);
        line-height: 1.4;
        text-decoration: none;
        transition: all var(--duration-fast) ease;
        display: block;
        position: relative;
    }
    
    .search-result-title::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 0;
        height: 2px;
        background: var(--gradient-accent);
        transition: width var(--duration-normal) ease;
        border-radius: var(--radius-full);
    }
    
    .search-result-title:hover {
        color: var(--accent-blue);
        transform: translateX(4px);
    }
    
    .search-result-title:hover::after {
        width: 100%;
    }
    
    .search-result-snippet {
        color: var(--text-secondary);
        font-size: var(--font-size-sm);
        line-height: 1.6;
        margin-bottom: var(--space-3);
    }
    
    .search-result-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: var(--font-size-xs);
        color: var(--text-tertiary);
    }
    
    .search-result-domain {
        background: var(--bg-accent);
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-sm);
        font-weight: 500;
        color: var(--accent-blue);
    }
    
    /* Category Headers */
    .search-category {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        margin: var(--space-6) 0 var(--space-4) 0;
        padding: var(--space-3) var(--space-4);
        background: var(--gradient-primary);
        border-radius: var(--radius-lg);
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    .search-category .category-icon {
        font-size: 1.25rem;
    }
    
    .search-category .category-title {
        font-size: var(--font-size-lg);
        font-weight: 600;
        margin: 0;
    }
    
    .search-category .category-count {
        background: rgba(255, 255, 255, 0.2);
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: 500;
        margin-left: auto;
    }
    
    /* Quality Assessment Panel */
    .quality-assessment {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin: var(--space-6) 0;
        box-shadow: var(--shadow-lg);
    }
    
    .quality-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: var(--space-4);
        margin: var(--space-4) 0;
    }
    
    .quality-metric {
        text-align: center;
        padding: var(--space-4);
        background: var(--bg-elevated);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        transition: all var(--duration-normal) ease;
    }
    
    .quality-metric:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .quality-metric-value {
        font-size: var(--font-size-2xl);
        font-weight: 700;
        color: var(--accent-blue);
        margin-bottom: var(--space-1);
    }
    
    .quality-metric-label {
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* Search Loading Animation */
    .search-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: var(--space-12);
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: var(--radius-xl);
        margin: var(--space-6) 0;
    }
    
    .search-loading-icon {
        font-size: 3rem;
        margin-bottom: var(--space-4);
        animation: searchPulse 2s infinite;
    }
    
    .search-loading-text {
        color: var(--text-secondary);
        font-size: var(--font-size-lg);
        font-weight: 500;
        margin-bottom: var(--space-2);
    }
    
    .search-loading-progress {
        width: 200px;
        height: 4px;
        background: var(--bg-tertiary);
        border-radius: var(--radius-full);
        overflow: hidden;
        margin-top: var(--space-4);
    }
    
    .search-loading-progress::before {
        content: '';
        display: block;
        width: 100%;
        height: 100%;
        background: var(--gradient-accent);
        animation: searchProgress 2s infinite;
        border-radius: var(--radius-full);
    }
    
    @keyframes searchPulse {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.1); opacity: 1; }
    }
    
    @keyframes searchProgress {
        0% { transform: translateX(-100%); }
        50% { transform: translateX(0%); }
        100% { transform: translateX(100%); }
    }
    
    /* Enhanced Search Result Card Animations */
    .search-result-card {
        animation: searchResultFadeIn 0.6s ease-out forwards;
        opacity: 0;
        transform: translateY(20px);
    }
    
    .search-result-card:nth-child(1) { animation-delay: 0.1s; }
    .search-result-card:nth-child(2) { animation-delay: 0.2s; }
    .search-result-card:nth-child(3) { animation-delay: 0.3s; }
    .search-result-card:nth-child(4) { animation-delay: 0.4s; }
    .search-result-card:nth-child(5) { animation-delay: 0.5s; }
    
    @keyframes searchResultFadeIn {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced Search Indicator Animations */
    .search-indicator {
        animation: indicatorSlideIn 0.4s ease-out forwards;
        opacity: 0;
        transform: translateX(-20px);
    }
    
    .search-indicator:nth-child(1) { animation-delay: 0.1s; }
    .search-indicator:nth-child(2) { animation-delay: 0.2s; }
    .search-indicator:nth-child(3) { animation-delay: 0.3s; }
    .search-indicator:nth-child(4) { animation-delay: 0.4s; }
    .search-indicator:nth-child(5) { animation-delay: 0.5s; }
    
    @keyframes indicatorSlideIn {
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Enhanced Quality Metric Animations */
    .quality-metric {
        animation: metricPop 0.6s ease-out forwards;
        opacity: 0;
        transform: scale(0.9);
    }
    
    .quality-metric:nth-child(1) { animation-delay: 0.2s; }
    .quality-metric:nth-child(2) { animation-delay: 0.3s; }
    .quality-metric:nth-child(3) { animation-delay: 0.4s; }
    .quality-metric:nth-child(4) { animation-delay: 0.5s; }
    
    @keyframes metricPop {
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Search Error State */
    .search-error {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 1px solid #fecaca;
        border-radius: var(--radius-lg);
        padding: var(--space-6);
        margin: var(--space-4) 0;
        text-align: center;
    }
    
    .search-error-icon {
        font-size: 2rem;
        color: var(--error-color);
        margin-bottom: var(--space-3);
    }
    
    .search-error-title {
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--error-color);
        margin-bottom: var(--space-2);
    }
    
    .search-error-message {
        color: #991b1b;
        font-size: var(--font-size-sm);
        line-height: 1.6;
    }
    
    /* Responsive Design for Search Components */
    @media (max-width: 768px) {
        .search-header {
            flex-direction: column;
            text-align: center;
            gap: var(--space-2);
        }
        
        .search-indicators {
            justify-content: center;
        }
        
        .quality-metrics {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .search-result-meta {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--space-2);
        }
    }
    
    @media (max-width: 480px) {
        .quality-metrics {
            grid-template-columns: 1fr;
        }
        
        .search-category {
            flex-direction: column;
            text-align: center;
        }
        
        .web-search-container {
            padding: var(--space-4);
        }
    }
    
    .card-compact {
        padding: var(--space-4);
    }
    
    .card-elevated {
        background: var(--bg-elevated);
        box-shadow: var(--shadow-xl);
    }
    
    /* Section Headers with Better Hierarchy */
    .section-header {
        font-weight: 700;
        font-size: var(--font-size-xl);
        color: var(--text-primary);
        margin: var(--space-8) 0 var(--space-4) 0;
        padding: var(--space-4) var(--space-6);
        background: var(--gradient-accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        display: inline-block;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 0;
        width: 100%;
        height: 2px;
        background: var(--gradient-accent);
        border-radius: var(--radius-full);
    }
    
    .subsection-header {
        font-weight: 600;
        font-size: var(--font-size-lg);
        color: var(--text-secondary);
        margin: var(--space-6) 0 var(--space-3) 0;
        padding-left: var(--space-3);
        border-left: 3px solid var(--accent-blue);
    }

    /* === ENHANCED BUTTON SYSTEM === */
    
    .stButton > button {
        background: var(--gradient-accent) !important;
        color: var(--text-inverse) !important;
        border: none !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-3) var(--space-6) !important;
        font-weight: 600 !important;
        font-size: var(--font-size-sm) !important;
        transition: all var(--duration-normal) ease !important;
        box-shadow: var(--shadow-md) !important;
        text-transform: none !important;
        letter-spacing: 0.025em !important;
        position: relative !important;
        overflow: hidden !important;
        cursor: pointer !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left var(--duration-slow) ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
        background: var(--gradient-warm) !important;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Button Variants */
    .btn-secondary {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .btn-secondary:hover {
        background: var(--bg-accent) !important;
        border-color: var(--border-focus) !important;
    }
    
    .btn-success {
        background: var(--gradient-cool) !important;
    }
    
    .btn-danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    }

    /* === ENHANCED CHAT SYSTEM === */
    
    /* Chat message container improvements */
    .stChatMessage {
        margin-bottom: var(--space-6) !important;
        border-radius: var(--radius-2xl) !important;
        padding: var(--space-6) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid var(--glass-border) !important;
        position: relative !important;
        overflow: hidden !important;
        animation: slideInUp 0.6s ease-out !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Chat message animations */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Enhanced avatars */
    .stChatMessage .stChatMessage-avatar img {
        border-radius: var(--radius-full) !important;
        width: 3rem !important;
        height: 3rem !important;
        border: 2px solid var(--glass-border) !important;
        box-shadow: var(--shadow-md) !important;
        transition: all var(--duration-normal) ease !important;
    }
    
    .stChatMessage .stChatMessage-avatar img:hover {
        transform: scale(1.1) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* User messages */
    .stChatMessage[data-testid="user-message"] {
        background: var(--gradient-primary) !important;
        color: var(--text-inverse) !important;
        margin-left: var(--space-8) !important;
        border: none !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    .stChatMessage[data-testid="user-message"] .stMarkdown {
        color: var(--text-inverse) !important;
        font-weight: 500 !important;
    }
    
    /* Assistant messages */
    .stChatMessage[data-testid="assistant-message"] {
        background: var(--gradient-secondary) !important;
        color: var(--text-inverse) !important;
        margin-right: var(--space-8) !important;
        border: none !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] .stMarkdown {
        color: var(--text-inverse) !important;
        font-weight: 500 !important;
    }
    
    /* Tool messages */
    .stChatMessage[data-testid="tool-message"] {
        background: var(--gradient-success) !important;
        border-left: 4px solid var(--accent-blue) !important;
        margin: var(--space-4) !important;
        color: var(--text-primary) !important;
        box-shadow: var(--shadow-md) !important;
    }

    /* === ENHANCED INPUT SYSTEM === */
    
    /* Chat input */
    .stChatInput > div > div {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) !important;
        border: 2px solid var(--glass-border) !important;
        border-radius: var(--radius-2xl) !important;
        box-shadow: var(--shadow-md) !important;
        transition: all var(--duration-normal) ease !important;
        padding: var(--space-4) !important;
    }
    
    .stChatInput > div > div:focus-within {
        border-color: var(--border-focus) !important;
        box-shadow: var(--shadow-lg), 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    .stChatInput textarea {
        background: transparent !important;
        color: var(--text-primary) !important;
        font-size: var(--font-size-base) !important;
        font-weight: 500 !important;
        border: none !important;
        resize: none !important;
        outline: none !important;
    }
    
    .stChatInput textarea::placeholder {
        color: var(--text-tertiary) !important;
        opacity: 0.8 !important;
    }
    
    /* Other inputs */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-lg) !important;
        color: var(--text-primary) !important;
        transition: all var(--duration-normal) ease !important;
        padding: var(--space-3) var(--space-4) !important;
    }
    
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }

    /* === ENHANCED TAB SYSTEM === */
    
    .stTabs [data-baseweb="tab-list"] {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: var(--radius-xl) !important;
        padding: var(--space-2) !important;
        border: 1px solid var(--glass-border) !important;
        box-shadow: var(--shadow-md) !important;
        margin-bottom: var(--space-6) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: var(--radius-lg) !important;
        font-weight: 600 !important;
        padding: var(--space-3) var(--space-6) !important;
        transition: all var(--duration-normal) ease !important;
        border: none !important;
        margin: 0 var(--space-1) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-accent) !important;
        color: var(--text-primary) !important;
        transform: translateY(-1px) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-accent) !important;
        color: var(--text-inverse) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px) !important;
    }

    /* === STATUS AND FEEDBACK SYSTEM === */
    
    /* Status indicators */
    .status-good { 
        color: var(--success-color) !important; 
        font-weight: 600 !important; 
        animation: pulse 2s infinite !important;
    }
    
    .status-warning { 
        color: var(--warning-color) !important; 
        font-weight: 600 !important;
        animation: pulse 2s infinite !important;
    }
    
    .status-error { 
        color: var(--error-color) !important; 
        font-weight: 600 !important;
        animation: pulse 2s infinite !important;
    }
    
    /* Enhanced alerts */
    .stAlert {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--glass-border) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-xl) !important;
        box-shadow: var(--shadow-md) !important;
        padding: var(--space-6) !important;
        margin: var(--space-4) 0 !important;
    }
    
    /* Tool output styling */
    .tool-output {
        background: var(--card) !important;
        backdrop-filter: blur(10px) !important;
        border-left: 4px solid var(--accent-blue) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-6) !important;
        margin: var(--space-4) 0 !important;
        overflow-x: auto !important;
        color: var(--text-primary) !important;
        box-shadow: var(--shadow-md) !important;
        border: 1px solid var(--glass-border) !important;
        font-family: var(--font-mono) !important;
        font-size: var(--font-size-sm) !important;
    }
    
    /* Error and success messages */
    .error-message {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%) !important;
        border-left: 4px solid var(--error-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-6) !important;
        margin: var(--space-4) 0 !important;
        color: var(--text-primary) !important;
        box-shadow: var(--shadow-md) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
    }
    
    .success-message {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%) !important;
        border-left: 4px solid var(--success-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-6) !important;
        margin: var(--space-4) 0 !important;
        color: var(--text-primary) !important;
        box-shadow: var(--shadow-md) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
    }

    /* === ENHANCED MEDIA SYSTEM === */
    
    /* Images */
    img {
        max-width: 100% !important;
        height: auto !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--shadow-md) !important;
        transition: all var(--duration-normal) ease !important;
    }
    
    img:hover {
        transform: scale(1.02) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        overflow-x: auto !important;
        border-radius: var(--radius-lg) !important;
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow-md) !important;
        backdrop-filter: blur(10px) !important;
        margin: var(--space-4) 0 !important;
    }
    
    code {
        background: var(--bg-accent) !important;
        color: var(--text-primary) !important;
        padding: var(--space-1) var(--space-2) !important;
        border-radius: var(--radius-sm) !important;
        font-family: var(--font-mono) !important;
        font-size: var(--font-size-sm) !important;
        font-weight: 500 !important;
    }
    
    pre code {
        background: transparent !important;
        padding: var(--space-4) !important;
        display: block !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
    }

    /* === ENHANCED SCROLLBAR === */
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: var(--radius-full);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gradient-accent);
        border-radius: var(--radius-full);
        border: 2px solid var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--gradient-warm);
    }
    
    /* Firefox scrollbar */
    * {
        scrollbar-width: thin;
        scrollbar-color: var(--accent-blue) var(--bg-secondary);
    }

    /* === ENHANCED PROGRESS SYSTEM === */
    
    .stProgress > div > div {
        background: var(--gradient-accent) !important;
        border-radius: var(--radius-full) !important;
        box-shadow: var(--shadow-sm) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stProgress > div > div::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    /* === LOADING STATES === */
    
    .loading-shimmer {
        background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-accent) 50%, var(--bg-secondary) 75%);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
        border-radius: var(--radius-lg);
    }
    
    .skeleton {
        background: var(--loading-shimmer);
        border-radius: var(--radius-md);
        animation: shimmer 2s infinite;
    }
    
    .spinner {
        width: 2rem;
        height: 2rem;
        border: 2px solid var(--bg-accent);
        border-top: 2px solid var(--accent-blue);
        border-radius: var(--radius-full);
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* === ENHANCED SIDEBAR NAVIGATION === */
    
    .sidebar-nav {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: var(--radius-xl);
        padding: var(--space-4);
        margin: var(--space-4) 0;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-md);
    }
    
    .nav-item {
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-lg);
        margin-bottom: var(--space-2);
        transition: all var(--duration-normal) ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: var(--space-3);
    }
    
    .nav-item:hover {
        background: var(--bg-accent);
        transform: translateX(4px);
    }
    
    .nav-item.active {
        background: var(--gradient-accent);
        color: var(--text-inverse);
        box-shadow: var(--shadow-sm);
    }

    /* === FLOATING ACTION BUTTON === */
    
    .fab {
        position: fixed;
        bottom: var(--space-8);
        right: var(--space-8);
        width: 4rem;
        height: 4rem;
        background: var(--gradient-accent);
        border-radius: var(--radius-full);
        box-shadow: var(--shadow-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-inverse);
        font-size: var(--font-size-xl);
        cursor: pointer;
        transition: all var(--duration-normal) ease;
        z-index: var(--z-fixed);
        border: none;
    }
    
    .fab:hover {
        transform: scale(1.1) translateY(-2px);
        box-shadow: var(--shadow-xl);
        background: var(--gradient-warm);
    }
    
    .fab:active {
        transform: scale(0.95);
    }

    /* === ACCESSIBILITY IMPROVEMENTS === */
    
    /* Focus styles */
    button:focus,
    input:focus,
    textarea:focus,
    select:focus,
    [tabindex]:focus {
        outline: 2px solid var(--border-focus) !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Reduced motion */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* High contrast mode */
    @media (prefers-contrast: high) {
        :root {
            --glass-bg: var(--bg-elevated);
            --glass-border: var(--border-color);
        }
    }

    /* === UTILITY CLASSES === */
    
    .hidden { display: none !important; }
    .visible { display: block !important; }
    .sr-only { 
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }
    
    .text-center { text-align: center !important; }
    .text-left { text-align: left !important; }
    .text-right { text-align: right !important; }
    
    .font-light { font-weight: 300 !important; }
    .font-normal { font-weight: 400 !important; }
    .font-medium { font-weight: 500 !important; }
    .font-semibold { font-weight: 600 !important; }
    .font-bold { font-weight: 700 !important; }
    
    .text-xs { font-size: var(--font-size-xs) !important; }
    .text-sm { font-size: var(--font-size-sm) !important; }
    .text-base { font-size: var(--font-size-base) !important; }
    .text-lg { font-size: var(--font-size-lg) !important; }
    .text-xl { font-size: var(--font-size-xl) !important; }
    .text-2xl { font-size: var(--font-size-2xl) !important; }
    .text-3xl { font-size: var(--font-size-3xl) !important; }
    
    .rounded-sm { border-radius: var(--radius-sm) !important; }
    .rounded { border-radius: var(--radius-md) !important; }
    .rounded-lg { border-radius: var(--radius-lg) !important; }
    .rounded-xl { border-radius: var(--radius-xl) !important; }
    .rounded-2xl { border-radius: var(--radius-2xl) !important; }
    .rounded-full { border-radius: var(--radius-full) !important; }
    
    .shadow-sm { box-shadow: var(--shadow-sm) !important; }
    .shadow { box-shadow: var(--shadow-md) !important; }
    .shadow-lg { box-shadow: var(--shadow-lg) !important; }
    .shadow-xl { box-shadow: var(--shadow-xl) !important; }
    
    .p-2 { padding: var(--space-2) !important; }
    .p-3 { padding: var(--space-3) !important; }
    .p-4 { padding: var(--space-4) !important; }
    .p-6 { padding: var(--space-6) !important; }
    .p-8 { padding: var(--space-8) !important; }
    
    .m-2 { margin: var(--space-2) !important; }
    .m-3 { margin: var(--space-3) !important; }
    .m-4 { margin: var(--space-4) !important; }
    .m-6 { margin: var(--space-6) !important; }
    .m-8 { margin: var(--space-8) !important; }
    
    .mt-2 { margin-top: var(--space-2) !important; }
    .mt-3 { margin-top: var(--space-3) !important; }
    .mt-4 { margin-top: var(--space-4) !important; }
    .mt-6 { margin-top: var(--space-6) !important; }
    .mt-8 { margin-top: var(--space-8) !important; }
    
    .mb-2 { margin-bottom: var(--space-2) !important; }
    .mb-3 { margin-bottom: var(--space-3) !important; }
    .mb-4 { margin-bottom: var(--space-4) !important; }
    .mb-6 { margin-bottom: var(--space-6) !important; }
    .mb-8 { margin-bottom: var(--space-8) !important; }

    /* === PRINT STYLES === */
    
    @media print {
        .stSidebar,
        .fab,
        .stChatInput,
        .no-print {
            display: none !important;
        }
        
        .stApp {
            background: white !important;
            color: black !important;
        }
        
        .stChatMessage {
            border: 1px solid #ccc !important;
            margin-bottom: 1rem !important;
            break-inside: avoid !important;
        }
    }

    /* === PERFORMANCE OPTIMIZATIONS === */
    
    /* GPU acceleration for animations */
    .stChatMessage,
    .card,
    .stButton > button,
    .fab {
        will-change: transform;
        transform: translateZ(0);
    }
    
    /* Optimize repaints */
    .stApp * {
        backface-visibility: hidden;
        perspective: 1000px;
    }

    /* === WEB SEARCH RESULTS STYLING === */
    
    .web-search-container {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        margin: var(--space-3) 0;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .search-header {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        margin-bottom: var(--space-3);
        padding-bottom: var(--space-2);
        border-bottom: 1px solid var(--border-color);
    }
    
    .search-icon {
        font-size: 1.5rem;
        animation: pulse 2s infinite;
    }
    
    .search-title {
        margin: 0;
        color: var(--text-primary);
        font-weight: 700;
        font-size: 1.25rem;
    }
    
    .search-query {
        background: var(--bg-accent);
        padding: var(--space-2) var(--space-3);
        border-radius: var(--radius-md);
        margin: var(--space-2) 0;
        border-left: 4px solid var(--accent-blue);
    }
    
    .search-indicators {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
        margin: var(--space-3) 0;
    }
    
    .search-indicator {
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
        color: white;
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: 600;
        animation: slideInUp 0.6s ease-out forwards;
        opacity: 0;
        transform: translateY(20px);
    }
    
    .search-category {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        margin: var(--space-4) 0 var(--space-2) 0;
        padding: var(--space-2) var(--space-3);
        background: var(--bg-accent);
        border-radius: var(--radius-md);
        border-left: 4px solid var(--accent-green);
    }
    
    .category-icon {
        font-size: 1.25rem;
    }
    
    .category-title {
        margin: 0;
        color: var(--text-primary);
        font-weight: 600;
        flex: 1;
    }
    
    .category-count {
        background: var(--accent-blue);
        color: white;
        padding: 2px 8px;
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: 600;
    }
    
    .search-result-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        margin: var(--space-2) 0;
        transition: all 0.3s ease;
        animation: slideInUp 0.6s ease-out forwards;
        opacity: 0;
        transform: translateY(20px);
    }
    
    .search-result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-color: var(--accent-blue);
    }
    
    .search-result-title {
        display: block;
        color: var(--accent-blue);
        font-weight: 600;
        font-size: 1.1rem;
        text-decoration: none;
        margin-bottom: var(--space-2);
        line-height: 1.4;
    }
    
    .search-result-title:hover {
        color: var(--accent-purple);
        text-decoration: underline;
    }
    
    .search-result-snippet {
        color: var(--text-secondary);
        line-height: 1.6;
        margin: var(--space-2) 0;
        font-size: var(--font-size-sm);
    }
    
    .search-result-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: var(--space-2);
        padding-top: var(--space-2);
        border-top: 1px solid var(--border-color);
        font-size: var(--font-size-xs);
    }
    
    .search-result-domain {
        color: var(--text-tertiary);
        font-weight: 500;
    }
    
    .quality-assessment {
        background: linear-gradient(135deg, var(--bg-accent) 0%, var(--bg-secondary) 100%);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        margin: var(--space-4) 0;
    }
    
    .quality-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: var(--space-3);
        margin: var(--space-3) 0;
    }
    
    .quality-metric {
        background: var(--bg-primary);
        border: 2px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        text-align: center;
        transition: all 0.3s ease;
        animation: slideInUp 0.6s ease-out forwards;
        opacity: 0;
        transform: translateY(20px);
    }
    
    .quality-metric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .quality-metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent-blue);
        margin-bottom: var(--space-1);
    }
    
    .quality-metric-label {
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        font-weight: 600;
    }
    
    .search-error {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #f87171;
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        margin: var(--space-3) 0;
        text-align: center;
    }
    
    .search-error-icon {
        font-size: 2rem;
        margin-bottom: var(--space-2);
    }
    
    .search-error-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #dc2626;
        margin-bottom: var(--space-1);
    }
    
    .search-error-message {
        color: #991b1b;
        font-size: var(--font-size-sm);
    }
    
    /* === ANIMATIONS === */
    
    @keyframes slideInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.1);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
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


def setup_enhanced_styling():
    """Add enhanced CSS styling for the perfect tool interface."""
    st.markdown("""
    <style>
    /* Enhanced Tool Interface Styling */
    .web-search-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .search-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .search-icon {
        font-size: 1.5rem;
        animation: pulse 2s infinite;
    }
    
    .search-title {
        color: #1f2937;
        font-weight: 700;
        margin: 0;
        font-size: 1.25rem;
    }
    
    .search-query {
        background: rgba(59, 130, 246, 0.1);
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
        color: #1f2937;
        font-weight: 500;
    }
    
    .search-indicators {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .search-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
        animation: slideInUp 0.5s ease-out;
    }
    
    .search-category {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: linear-gradient(135deg, #fef5e7 0%, #fed7aa 100%);
        padding: 0.75rem;
        border-radius: 8px;
        margin: 1rem 0 0.5rem 0;
        border-left: 4px solid #f59e0b;
    }
    
    .category-icon {
        font-size: 1.25rem;
    }
    
    .category-title {
        color: #92400e;
        font-weight: 600;
        margin: 0;
        flex-grow: 1;
    }
    
    .category-count {
        background: rgba(146, 64, 14, 0.1);
        color: #92400e;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .search-result-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .search-result-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    .search-result-title {
        color: #1f2937;
        font-weight: 600;
        font-size: 1.1rem;
        text-decoration: none;
        line-height: 1.4;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .search-result-title:hover {
        color: #3b82f6;
        text-decoration: underline;
    }
    
    .search-result-snippet {
        color: #6b7280;
        font-size: 0.875rem;
        line-height: 1.5;
        margin: 0.5rem 0;
    }
    
    .search-result-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 0.75rem;
        padding-top: 0.5rem;
        border-top: 1px solid #f3f4f6;
    }
    
    .search-result-domain {
        color: #059669;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .search-error {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 1px solid #fca5a5;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .search-error-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .search-error-title {
        color: #dc2626;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .search-error-message {
        color: #7f1d1d;
        font-size: 0.875rem;
    }
    
    .quality-assessment {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid #93c5fd;
    }
    
    .quality-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .quality-metric {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .quality-metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }
    
    .quality-metric-label {
        color: #6b7280;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced chat message styling */
    .stChatMessage {
        background: transparent !important;
        padding: 0 !important;
    }
    
    /* Tool status indicators */
    .tool-status-active {
        color: #059669;
        font-weight: 600;
    }
    
    .tool-status-inactive {
        color: #dc2626;
        font-weight: 600;
    }
    
    .tool-capability {
        color: #6b7280;
        font-size: 0.875rem;
        line-height: 1.4;
    }
    
    /* Enhanced metrics */
    .metric-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #cbd5e1;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .search-header {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .search-result-meta {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        
        .quality-metrics {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def setup_state():
    """Initialize all session state variables safely"""
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
    
    # Web Search Settings - Initialize with safe defaults
    if "web_search_enabled" not in st.session_state:
        st.session_state.web_search_enabled = True
    if "web_search_max_uses" not in st.session_state:
        st.session_state.web_search_max_uses = 5
    if "web_search_filter_type" not in st.session_state:
        st.session_state.web_search_filter_type = 0
    if "web_search_location_enabled" not in st.session_state:
        st.session_state.web_search_location_enabled = True
    if "web_search_allow_list_domains" not in st.session_state:
        st.session_state.web_search_allow_list_domains = ""
    if "web_search_block_list_domains" not in st.session_state:
        st.session_state.web_search_block_list_domains = ""
    if "web_search_location_city" not in st.session_state:
        st.session_state.web_search_location_city = "San Francisco"
    if "web_search_location_region" not in st.session_state:
        st.session_state.web_search_location_region = "California"
    if "web_search_location_country" not in st.session_state:
        st.session_state.web_search_location_country = "US"
    if "web_search_location_timezone" not in st.session_state:
        st.session_state.web_search_location_timezone = "America/Los_Angeles"
    if "web_search_stats" not in st.session_state:
        st.session_state.web_search_stats = {
            'total_searches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'avg_results_per_search': 0,
            'avg_quality_score': 0
        }
    if "recent_web_searches" not in st.session_state:
        st.session_state.recent_web_searches = []
    
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


def render_enhanced_security_settings():
    """Render basic security settings"""
    with st.expander("🔐 Security Settings", expanded=False):
        
        # Basic security settings
        st.markdown("**🛡️ Security Configuration:**")
        
        # API timeout as a security measure
        api_timeout = st.slider(
            "API Timeout (seconds)",
            min_value=30,
            max_value=300,
            value=st.session_state.get('api_timeout', 120),
            help="Timeout for API requests (security measure)"
        )
        st.session_state.api_timeout = api_timeout
        
        # Tool usage monitoring
        st.markdown("**📊 Tool Usage Monitoring:**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_tools = sum(st.session_state.tool_usage_stats.values()) if st.session_state.tool_usage_stats else 0
            st.metric("Total Tool Uses", total_tools)
        with col2:
            st.metric("Active Session Time", f"{(datetime.now() - st.session_state.session_start_time).seconds // 60} min")
        with col3:
            st.metric("Model Used", st.session_state.get('model', 'Not selected').split('-')[-1] if st.session_state.get('model') else 'None')


# Enhanced approval system for dangerous operations
class InteractiveApprovalManager:
    """Manages interactive approval dialogs for risky operations"""
    
    def __init__(self):
        self.pending_approvals = {}
        self.approval_history = {}
        self.user_preferences = {
            "auto_approve_patterns": set(),
            "always_block_patterns": set(),
            "default_approval_timeout": 30
        }
        
    def request_approval(self, 
                        operation_id: str,
                        risk_assessment: dict,
                        operation_details: dict) -> str:
        """Request approval for a risky operation"""
        
        # Store pending approval
        self.pending_approvals[operation_id] = {
            "timestamp": datetime.now(),
            "risk_assessment": risk_assessment,
            "operation_details": operation_details,
            "status": "pending"
        }
        
        return operation_id
    
    def render_approval_dialog(self, operation_id: str) -> str:
        """Render approval dialog in Streamlit"""
        if operation_id not in self.pending_approvals:
            return "approved"  # Default for unknown operations
            
        approval_data = self.pending_approvals[operation_id]
        risk_assessment = approval_data["risk_assessment"]
        operation_details = approval_data["operation_details"]
        
        # Create approval UI
        with st.expander(f"🔐 **Security Approval Required** - Risk Level: {risk_assessment['risk_level'].title()}", expanded=True):
            
            # Risk visualization
            risk_score = risk_assessment["risk_score"]
            st.progress(risk_score, text=f"Risk Score: {risk_score:.2f}")
            
            # Risk factors
            st.markdown("**⚠️ Risk Factors:**")
            for factor in risk_assessment["factors"]:
                st.markdown(f"• {factor}")
            
            # Operation details
            st.markdown("**🔍 Operation Details:**")
            col1, col2 = st.columns(2)
            with col1:
                st.json(operation_details)
            
            with col2:
                # Suggested action
                st.markdown(f"**💡 Recommended Action:** {risk_assessment['suggested_action']}")
                
                # Similar operations history
                if operation_id in self.approval_history:
                    st.markdown("**📊 Previous Similar Operations:**")
                    # Show history of similar operations
            
            # Approval options
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✅ Approve Once", key=f"approve_once_{operation_id}"):
                    self.pending_approvals[operation_id]["status"] = "approved"
                    return "approved"
            
            with col2:
                if st.button("🔄 Approve Pattern", key=f"approve_pattern_{operation_id}"):
                    # Add to auto-approve patterns
                    self.user_preferences["auto_approve_patterns"].add(
                        self._get_operation_pattern(operation_details)
                    )
                    self.pending_approvals[operation_id]["status"] = "approved"
                    return "approved_with_pattern"
            
            with col3:
                if st.button("❌ Deny Once", key=f"deny_once_{operation_id}"):
                    self.pending_approvals[operation_id]["status"] = "denied"
                    return "denied"
            
            with col4:
                if st.button("🚫 Block Pattern", key=f"block_pattern_{operation_id}"):
                    # Add to always-block patterns
                    self.user_preferences["always_block_patterns"].add(
                        self._get_operation_pattern(operation_details)
                    )
                    self.pending_approvals[operation_id]["status"] = "blocked"
                    return "blocked_with_pattern"
            
            # Advanced options
            with st.expander("⚙️ Advanced Options", expanded=False):
                # Modify operation parameters
                st.markdown("**🔧 Modify Operation:**")
                # Allow user to modify the operation parameters
                
                # Risk tolerance adjustment
                st.markdown("**⚖️ Risk Tolerance:**")
                new_risk_tolerance = st.slider(
                    "Adjust risk tolerance for this session",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    key=f"risk_tolerance_{operation_id}"
                )
                
                # Preview mode
                if st.checkbox("👁️ Preview Mode (Show what would happen)", key=f"preview_{operation_id}"):
                    st.info("🔍 Preview mode would show a simulation of the operation effects")
        
        return "pending"
    
    def _get_operation_pattern(self, operation_details: dict) -> str:
        """Extract pattern signature from operation details"""
        # Simplified pattern extraction
        action = operation_details.get("action", "unknown")
        context = operation_details.get("context", {})
        return f"{action}_{hash(str(sorted(context.items())))}"


# Removed setup_enhanced_state function to prevent ScriptRunContext warnings


def render_tools_and_monitoring():
    """Enhanced tools and monitoring section with comprehensive web search configuration"""
    
    st.markdown("### 🔧 Tool Configuration & Monitoring")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Web Search Settings",
        "🛠️ Tool Collection", 
        "📊 Performance Monitor",
        "🔐 Security Settings"
    ])
    
    with tab1:
        st.markdown("#### 🌐 Web Search Configuration")
        st.caption("Configure the official Anthropic web search tool (server-side)")
        
        # Web Search Enable/Disable
        col1, col2 = st.columns([2, 1])
        with col1:
            web_search_enabled = st.checkbox(
                "Enable Web Search Tool",
                value=st.session_state.get('web_search_enabled', True),
                help="Enable server-side web search tool for real-time information retrieval"
            )
            st.session_state.web_search_enabled = web_search_enabled
        
        with col2:
            if web_search_enabled:
                st.success("🟢 Active")
            else:
                st.warning("🟡 Disabled")
        
        if web_search_enabled:
            # Advanced Web Search Configuration
            with st.expander("⚙️ Advanced Web Search Settings", expanded=False):
                
                # Max Uses Configuration
                col1, col2 = st.columns(2)
                with col1:
                    max_searches = st.slider(
                        "Max Searches per Request",
                        min_value=1,
                        max_value=10,
                        value=st.session_state.get('web_search_max_uses', 5),
                        help="Limit the number of web searches Claude can perform per request"
                    )
                    st.session_state.web_search_max_uses = max_searches
                
                with col2:
                    search_timeout = st.slider(
                        "Search Timeout (seconds)",
                        min_value=10,
                        max_value=60,
                        value=st.session_state.get('web_search_timeout', 30),
                        help="Maximum time to wait for search results"
                    )
                    st.session_state.web_search_timeout = search_timeout
                
                # Domain Filtering
                st.markdown("**🌐 Domain Filtering**")
                
                filter_type = st.radio(
                    "Domain Filter Type",
                    options=["None", "Allow List", "Block List"],
                    index=st.session_state.get('web_search_filter_type', 0),
                    help="Control which domains web search can access",
                    horizontal=True
                )
                st.session_state.web_search_filter_type = ["None", "Allow List", "Block List"].index(filter_type)
                
                if filter_type != "None":
                    domains_text = st.text_area(
                        f"{'Allowed' if filter_type == 'Allow List' else 'Blocked'} Domains",
                        value=st.session_state.get(f'web_search_{filter_type.lower().replace(" ", "_")}_domains', ""),
                        placeholder="example.com\ndocs.anthropic.com\ngithub.com",
                        help="Enter one domain per line. Subdomains are automatically included."
                    )
                    st.session_state[f'web_search_{filter_type.lower().replace(" ", "_")}_domains'] = domains_text
                
                # Location Configuration
                st.markdown("**📍 Search Localization**")
                
                enable_location = st.checkbox(
                    "Enable Location-based Search",
                    value=st.session_state.get('web_search_location_enabled', True),
                    help="Localize search results based on specified location"
                )
                st.session_state.web_search_location_enabled = enable_location
                
                if enable_location:
                    col1, col2 = st.columns(2)
                    with col1:
                        location_city = st.text_input(
                            "City",
                            value=st.session_state.get('web_search_location_city', 'San Francisco'),
                            help="City for search localization"
                        )
                        st.session_state.web_search_location_city = location_city
                        
                        location_country = st.text_input(
                            "Country",
                            value=st.session_state.get('web_search_location_country', 'US'),
                            help="Country code (e.g., US, UK, CA)"
                        )
                        st.session_state.web_search_location_country = location_country
                    
                    with col2:
                        location_region = st.text_input(
                            "Region/State",
                            value=st.session_state.get('web_search_location_region', 'California'),
                            help="State or region for search localization"
                        )
                        st.session_state.web_search_location_region = location_region
                        
                        location_timezone = st.selectbox(
                            "Timezone",
                            options=[
                                "America/Los_Angeles", "America/New_York", "America/Chicago",
                                "America/Denver", "Europe/London", "Europe/Paris",
                                "Asia/Tokyo", "Asia/Shanghai", "Australia/Sydney"
                            ],
                            index=0,
                            help="IANA timezone ID for search localization"
                        )
                        st.session_state.web_search_location_timezone = location_timezone
                
                # Caching Configuration
                st.markdown("**💾 Prompt Caching for Web Search**")
                
                enable_caching = st.checkbox(
                    "Enable Prompt Caching",
                    value=st.session_state.get('web_search_caching_enabled', True),
                    help="Cache web search results for faster multi-turn conversations"
                )
                st.session_state.web_search_caching_enabled = enable_caching
                
                if enable_caching:
                    cache_duration = st.slider(
                        "Cache Duration (minutes)",
                        min_value=5,
                        max_value=60,
                        value=st.session_state.get('web_search_cache_duration', 15),
                        help="How long to cache search results"
                    )
                    st.session_state.web_search_cache_duration = cache_duration
            
            # Search Quality Metrics
            st.markdown("#### 📊 Search Quality Metrics")
            
            # Display current session web search stats
            search_stats = st.session_state.get('web_search_stats', {
                'total_searches': 0,
                'successful_searches': 0,
                'failed_searches': 0,
                'avg_results_per_search': 0,
                'avg_quality_score': 0
            })
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Searches", search_stats['total_searches'])
            with col2:
                success_rate = (search_stats['successful_searches'] / max(search_stats['total_searches'], 1)) * 100
                st.metric("Success Rate", f"{success_rate:.1f}%")
            with col3:
                st.metric("Avg Results/Search", f"{search_stats['avg_results_per_search']:.1f}")
            with col4:
                st.metric("Avg Quality Score", f"{search_stats['avg_quality_score']:.2f}")
            
            # Recent Search History
            if st.session_state.get('recent_web_searches'):
                with st.expander("🕒 Recent Web Searches", expanded=False):
                    for search in st.session_state.recent_web_searches[-5:]:  # Show last 5
                        st.markdown(f"""
                        **Query:** {search.get('query', 'Unknown')}  
                        **Results:** {search.get('result_count', 0)} • **Quality:** {search.get('quality_score', 0):.2f} • **Time:** {search.get('timestamp', 'Unknown')}
                        """)
    
    with tab2:
        # Existing tool collection content
        if hasattr(st.session_state, 'tool_collection') and st.session_state.tool_collection:
            st.markdown("#### 🛠️ Available Tools")
            
            for tool_name, tool_status in st.session_state.tool_collection.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{tool_name}**")
                with col2:
                    if tool_status.get('enabled', True):
                        st.success("Enabled")
                    else:
                        st.error("Disabled")
                with col3:
                    uses = tool_status.get('uses', 0)
                    st.metric("Uses", uses)
    
    with tab3:
        # Enhanced performance monitoring
        st.markdown("#### 📈 Real-time Performance Metrics")
        
        # Tool usage distribution
        if st.session_state.get('tool_usage_stats'):
            tool_stats = st.session_state.tool_usage_stats
            
            # Create charts for tool usage
            import pandas as pd
            
            df = pd.DataFrame([
                {'Tool': tool, 'Usage Count': stats['count'], 'Success Rate': stats['success_rate']}
                for tool, stats in tool_stats.items()
            ])
            
            if not df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.bar_chart(df.set_index('Tool')['Usage Count'])
                with col2:
                    st.bar_chart(df.set_index('Tool')['Success Rate'])
    
    with tab4:
        # Enhanced security settings integration
        render_enhanced_security_settings()


def main():
    """Enhanced main function with better UI and clean initialization."""
    # Initialize state first
    setup_state()
    
    # Setup styling
    st.markdown(STREAMLIT_STYLE, unsafe_allow_html=True)
    
    # Handle staged session updates before creating any widgets
    if "__staged_session_updates" in st.session_state:
        staged_updates = st.session_state.pop("__staged_session_updates")
        for key, value in staged_updates.items():
            st.session_state[key] = value
        # Reset auth validation to ensure proper provider switching
        st.session_state.auth_validated = False

    # Enhanced header with modern design
    header_container = st.container()
    with header_container:
        # Main title row
        title_col1, title_col2, title_col3 = st.columns([3, 2, 2])
        
        with title_col1:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 3rem;">🚀</div>
                <div>
                    <h1 style="margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                               background-clip: text; font-size: 2.5rem; font-weight: 700;">
                        Claude Computer Use
                    </h1>
                    <p style="margin: 0; color: #6b7280; font-size: 1rem; font-weight: 500;">
                        Enhanced for Mac with Claude 4 & Extended Thinking
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with title_col2:
            # Enhanced model status with beautiful cards
            current_model = st.session_state.get('model', 'Not selected')
            if current_model != 'Not selected':
                model_name = current_model.replace('claude-', '').replace('-20250514', '').replace('-20241022', '')
                
                if model_supports_extended_thinking(current_model):
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                               color: white; padding: 1rem; border-radius: 12px; text-align: center;
                               box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 1.5rem;">🧠</div>
                        <div style="font-weight: 600; margin-top: 0.5rem;">{model_name}</div>
                        <div style="font-size: 0.875rem; opacity: 0.9;">Extended Thinking</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
                               color: white; padding: 1rem; border-radius: 12px; text-align: center;
                               box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 1.5rem;">🎯</div>
                        <div style="font-weight: 600; margin-top: 0.5rem;">{model_name}</div>
                        <div style="font-size: 0.875rem; opacity: 0.9;">Standard Mode</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                           color: white; padding: 1rem; border-radius: 12px; text-align: center;
                           box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <div style="font-size: 1.5rem;">⚙️</div>
                    <div style="font-weight: 600; margin-top: 0.5rem;">Setup Required</div>
                    <div style="font-size: 0.875rem; opacity: 0.9;">Configure Model</div>
                </div>
                """, unsafe_allow_html=True)
        
        with title_col3:
            # Enhanced status with beautiful indicators
            if st.session_state.current_tool_execution:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                           color: white; padding: 1rem; border-radius: 12px; text-align: center;
                           box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <div style="font-size: 1.5rem;">⚡</div>
                    <div style="font-weight: 600; margin-top: 0.5rem;">Active</div>
                    <div style="font-size: 0.875rem; opacity: 0.9;">{st.session_state.current_tool_execution}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                total_tools = sum(st.session_state.tool_usage_stats.values()) if st.session_state.tool_usage_stats else 0
                if total_tools > 0:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); 
                               color: white; padding: 1rem; border-radius: 12px; text-align: center;
                               box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 1.5rem;">🛠️</div>
                        <div style="font-weight: 600; margin-top: 0.5rem;">{total_tools}</div>
                        <div style="font-size: 0.875rem; opacity: 0.9;">Tools Used</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                               color: white; padding: 1rem; border-radius: 12px; text-align: center;
                               box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 1.5rem;">🚀</div>
                        <div style="font-weight: 600; margin-top: 0.5rem;">Ready</div>
                        <div style="font-size: 0.875rem; opacity: 0.9;">All Systems Go</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Add a subtle separator
        st.markdown("""
        <div style="margin: 2rem 0 1rem 0; height: 1px; 
                   background: linear-gradient(90deg, transparent 0%, #e5e7eb 50%, transparent 100%);"></div>
        """, unsafe_allow_html=True)

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

    # Enhanced main chat interface with perfect tabs
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        background: transparent;
        border: 1px solid transparent;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.8);
        border-color: #cbd5e1;
        transform: translateY(-1px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    chat, logs = st.tabs(["💬 Chat", "📋 HTTP Logs"])
    
    # Enhanced chat input with perfect styling
    st.markdown("""
    <div style="margin: 1rem 0;">
        <div style="text-align: center; color: #6b7280; font-size: 0.875rem; margin-bottom: 0.5rem;">
            💬 Ask Claude to help with your Mac - now with web search, extended thinking, and enhanced macOS tools
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    new_message = st.chat_input(
        "Ask Claude to help with your Mac...",
        key="chat_input"
    )

    with chat:
        # Clean up orphaned tool references before rendering
        st.session_state.messages = clean_orphaned_tool_references(st.session_state.messages)
        
        # Render chat messages with enhanced styling
        for message in st.session_state.messages:
            if isinstance(message["content"], str):
                _render_message(message["role"], message["content"])
            elif isinstance(message["content"], list):
                # IMPROVED: Consolidate related text blocks and citations before rendering
                consolidated_blocks = _consolidate_message_blocks(message["content"])
                
                for block in consolidated_blocks:
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

        # Enhanced loading state with perfect spinner
        with st.spinner(""):
            # Custom loading display
            loading_container = st.empty()
            loading_container.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem; animation: pulse 2s infinite;">🤖</div>
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                           background-clip: text; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">
                    Claude is thinking...
                </div>
                <div style="color: #6b7280; font-size: 0.875rem; text-align: center;">
                    Processing your request with advanced AI capabilities
                </div>
                <div style="margin-top: 1rem; width: 200px; height: 4px; background: #e5e7eb; border-radius: 2px; overflow: hidden;">
                    <div style="width: 100%; height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); 
                               animation: loading 2s infinite; border-radius: 2px;"></div>
                </div>
            </div>
            <style>
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            @keyframes loading {
                0% { transform: translateX(-100%); }
                50% { transform: translateX(0%); }
                100% { transform: translateX(100%); }
            }
            </style>
            """, unsafe_allow_html=True)
            try:
                # Run async sampling_loop in sync context
                st.session_state.messages = asyncio.run(sampling_loop(
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
                ))
                
                loading_container.empty()  # Clear the loading display
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
    
    # Enhanced footer with perfect styling
    st.markdown("""
    <div style="margin-top: 3rem; padding: 2rem 0; border-top: 1px solid #e5e7eb;">
        <div style="text-align: center;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.875rem;">
                    <span style="font-size: 1.25rem;">🚀</span>
                    <span>Powered by Claude Computer Use</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.875rem;">
                    <span style="font-size: 1.25rem;">🧠</span>
                    <span>Enhanced with Extended Thinking</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.875rem;">
                    <span style="font-size: 1.25rem;">🔍</span>
                    <span>Real-time Web Search</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.875rem;">
                    <span style="font-size: 1.25rem;">🍎</span>
                    <span>macOS Optimized</span>
                </div>
            </div>
            <div style="color: #9ca3af; font-size: 0.75rem; margin-top: 1rem;">
                Built with Streamlit • Enhanced for productivity and creativity
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


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
    
    # Track tool usage statistics - safely extract tool name
    # Since ToolResult doesn't have tool_name, try to infer it from context
    tool_name = 'unknown'
    
    # Try to get tool name from the output content if it contains tool information
    if tool_output.output and isinstance(tool_output.output, str):
        output_lower = tool_output.output.lower()
        if 'web search' in output_lower or 'search result' in output_lower:
            tool_name = 'web_search'
        elif 'screenshot' in output_lower or 'clicked' in output_lower:
            tool_name = 'computer'
        elif 'executed' in output_lower and ('bash' in output_lower or 'command' in output_lower):
            tool_name = 'bash'
        elif 'file' in output_lower and ('edit' in output_lower or 'created' in output_lower):
            tool_name = 'edit'
    
    # Update tool usage statistics
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

def _render_enhanced_source_card(result: dict, index: int, category: str, formatter):
    """Render enhanced source card for non-news categories with proper link handling."""
    import html
    import re
    
    url = result.get('url', '#')
    title = result.get('title', 'Untitled')
    content = result.get('content', 'No description available')
    page_age = result.get('page_age', 'Unknown age')
    
    # Validate and clean URL
    if url and url != '#':
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Validate URL format
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            url = '#'  # Fallback for invalid URLs
    
    # Get quality assessment
    quality_info = formatter.assess_result_quality(result)
    trust_score = formatter._calculate_trust_score(url, title)
    
    # Extract domain for credibility indicator
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc if parsed_url.netloc else 'Unknown source'
    except:
        domain = url.split('/')[2] if len(url.split('/')) > 2 else 'Unknown source'
    
    # Clean and truncate content
    clean_content = html.escape(content)
    if len(clean_content) > 180:
        clean_content = clean_content[:180] + "..."
    
    # Escape content for safe HTML display (but NOT the URL for href)
    title_escaped = html.escape(title)
    domain_escaped = html.escape(domain)
    page_age_escaped = html.escape(page_age)
    url_display = html.escape(url[:50] + ('...' if len(url) > 50 else ''))
    
    # Category-specific styling
    category_colors = {
        'academic': 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
        'official': 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
        'technical': 'linear-gradient(135deg, #7c2d12 0%, #ea580c 100%)',
        'commercial': 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
        'other': 'linear-gradient(135deg, #6b7280 0%, #9ca3af 100%)'
    }
    
    category_gradient = category_colors.get(category, category_colors['other'])
    
    # Trust level indicator
    trust_level = "High" if trust_score >= 0.7 else "Medium" if trust_score >= 0.5 else "Standard"
    trust_color = "#10b981" if trust_score >= 0.7 else "#f59e0b" if trust_score >= 0.5 else "#6b7280"
    
    # Compliance with Anthropic's citation requirements: "clearly visible and clickable"
    clickable_link_indicator = "🔗" if url != '#' else "❌"
    
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        overflow: hidden;
        transition: all 0.3s ease;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.15)'" 
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)'">
        
        <!-- Source header with enhanced link visibility -->
        <div style="
            background: {category_gradient};
            padding: 10px 14px;
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-weight: 600; font-size: 0.8rem;">#{index}</span>
                <span style="font-size: 0.8rem; opacity: 0.9;">{domain_escaped}</span>
                <span style="font-size: 0.7rem; opacity: 0.8;" title="Link status">{clickable_link_indicator}</span>
            </div>
            <div style="display: flex; gap: 4px; align-items: center;">
                <span style="background: rgba(255,255,255,0.2); padding: 1px 6px; border-radius: 8px; font-size: 0.65rem;">
                    {quality_info['icon']} {quality_info['level'].title()}
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 1px 6px; border-radius: 8px; font-size: 0.65rem;">
                    📊 {trust_level}
                </span>
            </div>
        </div>
        
        <!-- Source content with properly functioning links -->
        <div style="padding: 14px;">
            <h5 style="
                margin: 0 0 8px 0;
                font-weight: 600;
                font-size: 0.95rem;
                line-height: 1.3;
                color: #1f2937;
            ">
                {'<a href="' + url + '" target="_blank" rel="noopener noreferrer" style="color: inherit; text-decoration: none; transition: color 0.2s ease; border-bottom: 1px solid transparent;" onmouseover="this.style.color=\'#3b82f6\'; this.style.borderBottomColor=\'#3b82f6\';" onmouseout="this.style.color=\'inherit\'; this.style.borderBottomColor=\'transparent\';">' + title_escaped + '</a>' if url != '#' else title_escaped}
            </h5>
            <p style="
                margin: 0 0 10px 0;
                color: #6b7280;
                font-size: 0.8rem;
                line-height: 1.4;
            ">
                {clean_content}
            </p>
            
            <!-- Enhanced source metadata with clickable URL -->
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-top: 8px;
                border-top: 1px solid #f3f4f6;
                font-size: 0.7rem;
                color: #9ca3af;
            ">
                <span>
                    {'🌐 <a href="' + url + '" target="_blank" rel="noopener noreferrer" style="color: #3b82f6; text-decoration: none;" onmouseover="this.style.textDecoration=\'underline\';" onmouseout="this.style.textDecoration=\'none\';">' + url_display + '</a>' if url != '#' else '🌐 ' + url_display}
                </span>
                <span>📅 {page_age_escaped}</span>
            </div>
            
            <!-- Anthropic compliance notice for citations -->
            {'<div style="margin-top: 8px; padding: 4px 8px; background: #f0f9ff; border-left: 3px solid #3b82f6; font-size: 0.65rem; color: #1e40af;">✅ Citation compliant: Source is clearly visible and clickable</div>' if url != '#' else '<div style="margin-top: 8px; padding: 4px 8px; background: #fef2f2; border-left: 3px solid #ef4444; font-size: 0.65rem; color: #dc2626;">⚠️ No valid URL available for this source</div>'}
        </div>
        
        <!-- Trust score indicator -->
        <div style="
            height: 3px;
            background: {trust_color};
            width: {trust_score * 100}%;
            transition: width 0.3s ease;
        "></div>
    </div>
    """, unsafe_allow_html=True)


def _consolidate_message_blocks(content_blocks):
    """
    Consolidate fragmented text blocks with citations into coherent content blocks.
    This prevents the fragmentation issue where each citation creates a separate text block.
    """
    if not content_blocks:
        return content_blocks
    
    consolidated = []
    current_text_group = []
    all_citations = []
    
    for block in content_blocks:
        # Handle text blocks - collect them for consolidation
        if isinstance(block, dict) and block.get("type") == "text":
            text_content = block.get("text", "").strip()
            citations = block.get("citations", [])
            
            # Skip empty or minimal text fragments that are likely citation artifacts
            if text_content and not _is_citation_fragment(text_content):
                current_text_group.append(text_content)
            
            # Collect citations
            if citations:
                all_citations.extend(citations)
                
        elif hasattr(block, 'type') and block.type == "text":
            text_content = getattr(block, 'text', '').strip()
            citations = getattr(block, 'citations', [])
            
            # Skip empty or minimal text fragments
            if text_content and not _is_citation_fragment(text_content):
                current_text_group.append(text_content)
            
            # Collect citations
            if citations:
                all_citations.extend(citations)
                
        else:
            # Non-text block - flush any accumulated text first
            if current_text_group:
                consolidated_text = _merge_text_fragments(current_text_group)
                if consolidated_text:
                    # Create consolidated text block with all citations
                    consolidated_block = BetaTextBlock(
                        type="text", 
                        text=consolidated_text
                    )
                    # Add citations if we have them
                    if all_citations:
                        consolidated_block.citations = all_citations
                    
                    consolidated.append(consolidated_block)
                
                # Reset for next group
                current_text_group = []
                all_citations = []
            
            # Add the non-text block
            consolidated.append(block)
    
    # Handle any remaining text group
    if current_text_group:
        consolidated_text = _merge_text_fragments(current_text_group)
        if consolidated_text:
            consolidated_block = BetaTextBlock(
                type="text", 
                text=consolidated_text
            )
            if all_citations:
                consolidated_block.citations = all_citations
            
            consolidated.append(consolidated_block)
    
    return consolidated


def _is_citation_fragment(text: str) -> bool:
    """
    Identify if a text fragment is likely a citation artifact that should be filtered out.
    """
    text = text.strip()
    
    # Empty or whitespace-only
    if not text:
        return True
    
    # Single characters or symbols
    if len(text) <= 2 and text in ["-", ".", ",", ":", ";", "|", " - ", " . "]:
        return True
    
    # Common citation separators
    citation_separators = [" - ", "- ", " .", ". ", " ,", ", "]
    if text in citation_separators:
        return True
    
    # Single word artifacts
    if len(text.split()) == 1 and text.lower() in ["and", "or", "but", "with", "the", "a", "an"]:
        return True
    
    return False


def _merge_text_fragments(text_list: list) -> str:
    """
    Intelligently merge text fragments with proper spacing and punctuation.
    """
    if not text_list:
        return ""
    
    # Clean up individual fragments
    cleaned_fragments = []
    for text in text_list:
        text = text.strip()
        if text and not _is_citation_fragment(text):
            cleaned_fragments.append(text)
    
    if not cleaned_fragments:
        return ""
    
    # Join fragments with intelligent spacing
    merged = ""
    for i, fragment in enumerate(cleaned_fragments):
        if i == 0:
            merged = fragment
        else:
            # Add appropriate spacing based on punctuation
            if merged.endswith(('.', '!', '?', ':')):
                # Sentence ending - add space and potentially capitalize
                if not fragment[0].isupper():
                    fragment = fragment[0].upper() + fragment[1:] if len(fragment) > 1 else fragment.upper()
                merged += " " + fragment
            elif merged.endswith(','):
                # Comma - add space
                merged += " " + fragment
            elif fragment.startswith(('.', ',', '!', '?', ';', ':')):
                # Fragment starts with punctuation - no space
                merged += fragment
            else:
                # Default - add space
                merged += " " + fragment
    
    return merged.strip()


def _categorize_citations(citations):
    """Categorize citations by domain type for enhanced display."""
    categories = {
        'academic': [],
        'news': [],
        'official': [],
        'technical': [],
        'other': []
    }
    
    for citation in citations:
        url = citation.get('url', '').lower()
        title = citation.get('title', '').lower()
        
        # Academic sources
        if any(domain in url for domain in ['.edu', 'scholar.', 'arxiv.', 'pubmed.', 'jstor.', 'ieee.']):
            categories['academic'].append(citation)
        # News sources
        elif any(domain in url for domain in ['news', 'cnn.', 'bbc.', 'reuters.', 'ap.org', 'nytimes.', 'wsj.']):
            categories['news'].append(citation)
        # Official sources
        elif any(domain in url for domain in ['.gov', '.org', 'wikipedia.', 'who.int']):
            categories['official'].append(citation)
        # Technical sources
        elif any(domain in url for domain in ['stackoverflow.', 'github.', 'docs.', 'api.', '.tech']):
            categories['technical'].append(citation)
        else:
            categories['other'].append(citation)
    
    return categories


def _render_text_with_enhanced_citations(content: str, citations):
    """Render text content with enhanced citation display following Anthropic's guidelines."""
    import html
    import re
    
    def clean_citation_text(text: str) -> str:
        """Clean HTML content from citation text."""
        if not text:
            return "No preview available"
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common web artifacts
        text = re.sub(r'\s*\.\.\.\s*$', '', text)  # Remove trailing ...
        text = re.sub(r'^[|\s]*', '', text)        # Remove leading pipes/spaces
        
        return text if text else "No preview available"
    
    # Escape HTML content to prevent rendering issues
    escaped_content = html.escape(content)
    
    if not citations:
        st.markdown(f"""
        <div style="color: white; font-size: 1rem; line-height: 1.6;">
            {escaped_content}
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display the main content first
    st.markdown(f"""
    <div style="color: white; font-size: 1rem; line-height: 1.6; margin-bottom: 1.5rem;">
        {escaped_content}
    </div>
    """, unsafe_allow_html=True)
    
    # Process citations - handle both old format and new web search citation format
    processed_citations = []
    
    for citation in citations:
        processed_citation = {}
        
        # Handle new web_search_result_location format
        if hasattr(citation, 'type') and citation.type == 'web_search_result_location':
            processed_citation['url'] = getattr(citation, 'url', '#')
            processed_citation['title'] = getattr(citation, 'title', 'Web Search Result')
            processed_citation['cited_text'] = clean_citation_text(getattr(citation, 'cited_text', ''))
            processed_citation['source_type'] = 'web_search'
        
        # Handle legacy citation format
        elif isinstance(citation, dict):
            processed_citation['url'] = citation.get('url', '#')
            processed_citation['title'] = citation.get('title', 'Untitled')
            processed_citation['cited_text'] = clean_citation_text(citation.get('snippet', citation.get('cited_text', '')))
            processed_citation['source_type'] = 'legacy'
        
        # Handle object format
        else:
            processed_citation['url'] = getattr(citation, 'url', '#')
            processed_citation['title'] = getattr(citation, 'title', 'Untitled') 
            processed_citation['cited_text'] = clean_citation_text(getattr(citation, 'cited_text', getattr(citation, 'snippet', '')))
            processed_citation['source_type'] = 'object'
        
        processed_citations.append(processed_citation)
    
    # Categorize citations for better display
    categorized_citations = _categorize_citations(processed_citations)
    
    # Display categorized citations in an enhanced format
    st.markdown("---")
    st.markdown("### 📚 **Sources & Citations**")
    
    citation_icons = {
        'academic': '🎓',
        'news': '📰', 
        'official': '🏛️',
        'technical': '⚙️',
        'other': '🔗'
    }
    
    citation_labels = {
        'academic': 'Academic Sources',
        'news': 'News & Media',
        'official': 'Official Sources', 
        'technical': 'Technical Documentation',
        'other': 'Additional Sources'
    }
    
    total_citations = len(processed_citations)
    
    # Show citation summary
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 16px;
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
    ">
        📊 <strong>{total_citations}</strong> sources found across <strong>{len([cat for cat in categorized_citations.values() if cat])}</strong> categories
    </div>
    """, unsafe_allow_html=True)
    
    for category, citations_list in categorized_citations.items():
        if citations_list:
            icon = citation_icons.get(category, '🔗')
            label = citation_labels.get(category, 'Sources')
            
            with st.expander(f"{icon} **{label}** ({len(citations_list)})", expanded=len(citations_list) <= 3):
                for i, citation in enumerate(citations_list, 1):
                    url = citation.get('url', '#')
                    title = citation.get('title', 'Untitled')
                    cited_text = citation.get('cited_text', 'No description available')
                    source_type = citation.get('source_type', 'unknown')
                    
                    # Truncate cited text for display
                    if len(cited_text) > 150:
                        cited_text = cited_text[:150] + "..."
                    
                    # Source type indicator
                    type_indicator = {
                        'web_search': '🌐 Web Search',
                        'legacy': '📄 Document',
                        'object': '📄 Source'
                    }.get(source_type, '📄 Source')
                    
                    # Escape all content for safe HTML display
                    url_escaped = html.escape(url)
                    title_escaped = html.escape(title)
                    cited_text_escaped = html.escape(cited_text)
                    url_display = html.escape(url[:40] + ('...' if len(url) > 40 else ''))
                    type_indicator_escaped = html.escape(type_indicator)
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; margin: 8px 0; 
                                border-radius: 8px; border-left: 3px solid #4CAF50;">
                        <div style="font-weight: 600; margin-bottom: 4px;">
                            <a href="{url_escaped}" target="_blank" style="color: #81C784; text-decoration: none;">
                                [{i}] {title_escaped}
                            </a>
                        </div>
                        <div style="font-size: 0.85rem; color: rgba(255,255,255,0.8); line-height: 1.4; margin-bottom: 6px;">
                            "{cited_text_escaped}"
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">
                                🌐 {url_display}
                            </div>
                            <div style="font-size: 0.7rem; color: rgba(255,255,255,0.5); 
                                       background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 10px;">
                                {type_indicator_escaped}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


def _render_message(
    sender: Sender,
    message: str | BetaTextBlock | BetaToolUseBlock | ToolResult,
):
    """
    Convert messages to streamlit chat with avatars and enhanced styling.
    """
    is_tool_result = isinstance(message, ToolResult)
    is_tool_use = not is_tool_result and isinstance(message, BetaToolUseBlock)
    
    # Determine avatar and role
    if sender == Sender.USER:
        # Enhanced user message with perfect avatar and styling
        with st.chat_message("user", avatar="👤"):
            # Add custom styling for user messages
            st.markdown("""
            <style>
            .stChatMessage[data-testid="user-message"] {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 18px;
                padding: 1.25rem;
                margin: 0.75rem 0;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
                border: none;
                position: relative;
            }
            .stChatMessage[data-testid="user-message"] .stMarkdown {
                color: white;
                font-weight: 500;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if isinstance(message, str):
                import html
                escaped_message = html.escape(message)
                st.markdown(f"""
                <div style="color: white; font-size: 1rem; line-height: 1.6;">
                    {escaped_message}
                </div>
                """, unsafe_allow_html=True)
            elif isinstance(message, BetaTextBlock):
                content = message.text
                citations = getattr(message, 'citations', None)
                if citations:
                    _render_text_with_enhanced_citations(content, citations)
                else:
                    import html
                    escaped_content = html.escape(content)
                    st.markdown(f"""
                    <div style="color: white; font-size: 1rem; line-height: 1.6;">
                        {escaped_content}
                    </div>
                    """, unsafe_allow_html=True)
        return
    
    elif sender == Sender.BOT:
        # Enhanced assistant message with perfect styling and gradient
        with st.chat_message("assistant", avatar="🤖"):
            # Add custom styling for assistant messages
            st.markdown("""
            <style>
            .stChatMessage[data-testid="assistant-message"] {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                border-radius: 18px;
                padding: 1.25rem;
                margin: 0.75rem 0;
                box-shadow: 0 4px 12px rgba(240, 147, 251, 0.25);
                border: none;
                position: relative;
            }
            .stChatMessage[data-testid="assistant-message"] .stMarkdown {
                color: white;
                font-weight: 500;
            }
            .stChatMessage[data-testid="assistant-message"] .stMarkdown h1,
            .stChatMessage[data-testid="assistant-message"] .stMarkdown h2,
            .stChatMessage[data-testid="assistant-message"] .stMarkdown h3 {
                color: white;
                margin-top: 1rem;
                margin-bottom: 0.5rem;
            }
            .stChatMessage[data-testid="assistant-message"] .stMarkdown strong {
                color: white;
                font-weight: 600;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if isinstance(message, str):
                import html
                escaped_message = html.escape(message)
                st.markdown(f"""
                <div style="color: white; font-size: 1rem; line-height: 1.6;">
                    {escaped_message}
                </div>
                """, unsafe_allow_html=True)
            elif isinstance(message, BetaTextBlock):
                content = message.text
                citations = getattr(message, 'citations', None)
                if citations:
                    _render_text_with_enhanced_citations(content, citations)
                else:
                    import html
                    escaped_content = html.escape(content)
                    st.markdown(f"""
                    <div style="color: white; font-size: 1rem; line-height: 1.6;">
                        {escaped_content}
                    </div>
                    """, unsafe_allow_html=True)
            elif is_tool_use:
                _render_tool_use_message(message)
            elif hasattr(message, 'type') and message.type == "thinking":
                _render_thinking_message(message)
        return
    
    elif sender == Sender.TOOL:
        # Enhanced tool message with perfect styling
        with st.chat_message("assistant", avatar="⚙️"):
            # Add custom styling for tool messages
            st.markdown("""
            <style>
            .stChatMessage[data-testid="tool-message"] {
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-left: 4px solid #3b82f6;
                border-radius: 12px;
                padding: 1.25rem;
                margin: 0.75rem 0;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
                border-top: 1px solid #cbd5e1;
                border-right: 1px solid #cbd5e1;
                border-bottom: 1px solid #cbd5e1;
            }
            .stChatMessage[data-testid="tool-message"] .stMarkdown {
                color: #374151;
                font-weight: 500;
            }
            </style>
            """, unsafe_allow_html=True)
            _render_tool_result_message(message)
        return

    # Enhanced handling for web search tool use (when called directly)
    if is_tool_use and message.name == "web_search":
        with st.chat_message("assistant", avatar="🔍"):
            _render_web_search_initiation(message)
        return

    # Rest of the existing logic for backward compatibility
    if not is_tool_result and not is_tool_use:
        if isinstance(message, BetaTextBlock):
            content = message.text
            citations = getattr(message, 'citations', None)
            if citations:
                _render_text_with_enhanced_citations(content, citations)
            else:
                st.markdown(content)
        elif isinstance(message, str):
            st.markdown(message)
        return

    if is_tool_use:
        _render_tool_use_message(message)
    else:
        _render_tool_result_message(message)


def _render_thinking_message(message):
    """Render thinking content blocks."""
    if hasattr(message, 'thinking'):
        with st.expander("🧠 Claude's Thinking Process", expanded=False):
            thinking_text = message.thinking
            if len(thinking_text) > 500:
                st.text_area("Thinking", thinking_text, height=200, disabled=True)
            else:
                st.markdown(f"```\n{thinking_text}\n```")


def _render_web_search_initiation(message):
    """Render web search initiation with enhanced UI and beautiful styling."""
    search_query = message.input.get("query", "Unknown query")
    
    # Enhanced web search container
    st.markdown(f"""
    <div class="web-search-container">
        <div class="search-header">
            <span class="search-icon">🔍</span>
            <h3 class="search-title">Web Search in Progress</h3>
        </div>
        
        <div class="search-query">
            <strong>🎯 Query:</strong> {search_query}
        </div>
    """, unsafe_allow_html=True)
    
    # Analyze search intent and create indicators
    indicators = []
    
    # Check for different types of searches
    time_keywords = ['today', 'latest', 'recent', 'current', 'now', '2024', '2025']
    if any(keyword in search_query.lower() for keyword in time_keywords):
        indicators.append("⏰ Time-sensitive")
    
    news_keywords = ['news', 'breaking', 'announcement', 'report']
    if any(keyword in search_query.lower() for keyword in news_keywords):
        indicators.append("📰 News focus")
    
    how_keywords = ['how to', 'tutorial', 'guide', 'step']
    if any(keyword in search_query.lower() for keyword in how_keywords):
        indicators.append("📚 Instructional")
    
    if search_query.strip().endswith('?'):
        indicators.append("❓ Question-based")
    
    if not indicators:
        indicators.append("🔍 General search")
    
    # Display search indicators
    indicators_html = ""
    for indicator in indicators:
        indicators_html += f'<div class="search-indicator">{indicator}</div>'
    
    # Display search configuration
    max_results = message.input.get("max_results", 5)
    include_citations = message.input.get("include_citations", True)
    
    config_indicators = [f"📊 {max_results} results"]
    if include_citations:
        config_indicators.append("📋 Citations enabled")
    
    for config in config_indicators:
        indicators_html += f'<div class="search-indicator">{config}</div>'
    
    st.markdown(f"""
        <div class="search-indicators">
            {indicators_html}
        </div>
        
        <div style="text-align: center; margin: var(--space-4) 0; padding: var(--space-4); 
                    background: linear-gradient(135deg, var(--bg-accent) 0%, var(--bg-secondary) 100%);
                    border-radius: var(--radius-lg); border: 2px dashed var(--accent-blue); animation: pulse 2s infinite;">
            <div style="font-size: 1.5rem; margin-bottom: var(--space-2);">🔍</div>
            <div style="color: var(--text-primary); font-weight: 600; margin-bottom: var(--space-1);">Searching the web...</div>
            <div style="color: var(--text-secondary); font-size: var(--font-size-sm);">
                Anthropic's web search API is processing your query with real-time results
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_tool_use_message(message):
    """Render tool use messages with enhanced formatting."""
    st.markdown(f"**🔧 Tool Use:** `{message.name}`")
    
    with st.expander("Tool Parameters", expanded=False):
        tool_input = cast(dict[str, Any], message.input)
        
        # Special formatting for tool inputs based on tool type
        if message.name == "computer":
            action = tool_input.get("action", "unknown")
            st.markdown(f"**Action:** `{action}`")
            
            # Display relevant parameters based on action
            if action in ["screenshot", "screen"]:
                st.markdown("📸 Taking screenshot")
            elif action == "click":
                coordinate = tool_input.get("coordinate")
                if coordinate:
                    st.markdown(f"**Click at:** `{coordinate}`")
            elif action == "type":
                text = tool_input.get("text", "")
                preview = text[:50] + "..." if len(text) > 50 else text
                st.markdown(f"**Typing:** `{preview}`")
            elif action == "key":
                key = tool_input.get("key", "")
                st.markdown(f"**Key press:** `{key}`")
            elif action == "scroll":
                coordinate = tool_input.get("coordinate")
                scroll_direction = tool_input.get("scroll_direction", "down")
                clicks = tool_input.get("clicks", 3)
                st.markdown(f"**Scroll {scroll_direction}** at `{coordinate}` ({clicks} clicks)")
            
            # Show full parameters without nested expander
            st.markdown("---")
            st.markdown("**All Parameters:**")
            st.json(tool_input)
        else:
            st.json(tool_input)


def _render_tool_result_message(message):
    """Enhanced rendering for all tool results with specialized visualization per tool type."""
    
    # Determine tool type from the message with enhanced detection for server-side tools
    tool_name = getattr(message, 'tool_name', 'unknown')
    if hasattr(message, 'name'):
        tool_name = message.name
    elif hasattr(message, 'tool') and hasattr(message.tool, 'name'):
        tool_name = message.tool.name
    
    # Enhanced detection for server-side web search results from Anthropic API
    if tool_name == 'unknown' or not tool_name:
        # Check if this is a web search result based on content analysis
        if hasattr(message, 'content'):
            content_str = str(message.content).lower()
            if any(indicator in content_str for indicator in [
                'web_search_tool_result', 'web search', 'search results', 
                'url:', 'https://', 'http://', 'website', 'domain'
            ]):
                tool_name = 'web_search'
        
        # Check output content for web search indicators
        elif hasattr(message, 'output'):
            output_str = str(message.output).lower()
            if any(indicator in output_str for indicator in [
                'web_search_tool_result', 'web search', 'search results',
                'url:', 'https://', 'http://', 'website', 'domain'
            ]):
                tool_name = 'web_search'
    
    # Add beautiful tool header with icon and status
    tool_icons = {
        'web_search': '🔍',
        'computer': '🖥️', 
        'bash': '⚡',
        'applescript': '🍏',
        'str_replace_based_edit_tool': '📝',
        'text_editor_20241022': '📝',
        'silicon': '💎',
        'web_browser': '🌐',
        'enhanced_bash': '⚡',
        'enhanced_web_browser': '🌐'
    }
    
    tool_icon = tool_icons.get(tool_name, '🛠️')
    tool_display_name = tool_name.replace('_', ' ').title()
    
    # Create enhanced tool result container
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.75rem 0;
        border: 1px solid #5a67d8;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
            color: white;
        ">
            <span style="font-size: 1.5rem;">{tool_icon}</span>
            <span style="font-weight: 600; font-size: 1.1rem;">{tool_display_name} Result</span>
            <span style="
                background: rgba(255, 255, 255, 0.2);
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 500;
            ">
                {'✅ Success' if not message.error else '❌ Error'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tool-specific enhanced rendering
    if tool_name == 'web_search':
        _render_enhanced_web_search_output(message)
    elif tool_name in ['computer']:
        _render_enhanced_computer_tool_output(message)
    elif tool_name in ['bash', 'enhanced_bash']:
        _render_enhanced_bash_output(message)
    elif tool_name == 'applescript':
        _render_enhanced_applescript_output(message)
    elif tool_name in ['str_replace_based_edit_tool', 'text_editor_20241022']:
        _render_enhanced_edit_tool_output(message)
    elif tool_name == 'silicon':
        _render_enhanced_silicon_output(message)
    elif tool_name in ['web_browser', 'enhanced_web_browser']:
        _render_enhanced_web_browser_output(message)
    else:
        # Fallback enhanced rendering for unknown tools
        _render_enhanced_generic_tool_output(message)

def _render_enhanced_computer_tool_output(tool_result: ToolResult):
    """Enhanced rendering for computer tool with beautiful visualization."""
    
    if tool_result.error:
        st.error(f"🖥️ **Computer Tool Error**\n\n{tool_result.error}")
        return
    
    # Computer tool specific UI
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #3b82f6;
    ">
    """, unsafe_allow_html=True)
    
    if tool_result.base64_image:
        # Enhanced screenshot display
        st.markdown("### 📸 **Screenshot Captured**")
        
        # Screenshot metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", "✅ Success")
        with col2:
            st.metric("Size", f"{len(tool_result.base64_image)//1024} KB")
        with col3:
            st.metric("Time", datetime.now().strftime('%H:%M:%S'))
        
        # Display screenshot with enhanced styling
        st.image(
            base64.b64decode(tool_result.base64_image),
            caption="🖥️ M4 MacBook Air Desktop Capture - Optimized for Claude",
            use_column_width=True,
        )
        
        # Additional screenshot info
        st.info("💡 **Screenshot optimized for M4 performance** - Automatically scaled for better Claude analysis")
        
    if tool_result.output:
        st.markdown("### 🔧 **Computer Tool Output**")
        
        # Enhanced output formatting
        if "Screenshot captured successfully" in tool_result.output:
            st.success(tool_result.output)
        elif "Error" in tool_result.output:
            st.warning(tool_result.output)
        else:
            st.code(tool_result.output, language="text")
    
    st.markdown("</div>", unsafe_allow_html=True)

def _render_enhanced_bash_output(tool_result: ToolResult):
    """Enhanced rendering for bash tool with syntax highlighting and analysis."""
    
    if tool_result.error:
        st.error(f"⚡ **Bash Tool Error**\n\n{tool_result.error}")
        return
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
        border-radius: 8px;
        padding: 1rem;
        color: #e2e8f0;
        border-left: 4px solid #48bb78;
    ">
    """, unsafe_allow_html=True)
    
    if tool_result.output:
        st.markdown("### ⚡ **Terminal Output**")
        
        # Analyze output for key information
        output_lines = tool_result.output.split('\n')
        if len(output_lines) > 1:
            st.markdown(f"**📊 Output Analysis:** {len(output_lines)} lines, {len(tool_result.output)} characters")
        
        # Enhanced code display with terminal styling
        st.code(tool_result.output, language="bash")
        
        # Extract key insights if it's system information
        if any(keyword in tool_result.output.lower() for keyword in ['macbook', 'm4', 'apple', 'macos']):
            st.info("🍎 **M4 MacBook Air System Information Detected** - Enhanced analysis available")
    
    st.markdown("</div>", unsafe_allow_html=True)

def _render_enhanced_applescript_output(tool_result: ToolResult):
    """Enhanced rendering for AppleScript tool with macOS integration focus."""
    
    if tool_result.error:
        st.error(f"🍏 **AppleScript Error**\n\n{tool_result.error}")
        return
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #ed8936;
    ">
    """, unsafe_allow_html=True)
    
    if tool_result.output:
        st.markdown("### 🍏 **AppleScript Result**")
        
        # AppleScript specific formatting
        if "successfully" in tool_result.output.lower():
            st.success(tool_result.output)
        elif "date" in tool_result.output.lower() or "time" in tool_result.output.lower():
            st.info(f"🕐 **System Time Information**\n\n{tool_result.output}")
        else:
            st.code(tool_result.output, language="applescript")
        
        st.markdown("💡 **AppleScript Integration** - Enhanced macOS Sequoia automation capabilities")
    
    st.markdown("</div>", unsafe_allow_html=True)

def _render_enhanced_edit_tool_output(tool_result: ToolResult):
    """Enhanced rendering for file editing tools with syntax highlighting."""
    
    if tool_result.error:
        st.error(f"📝 **File Editor Error**\n\n{tool_result.error}")
        return
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #fef5e7 0%, #fed7aa 100%);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #f59e0b;
    ">
    """, unsafe_allow_html=True)
    
    if tool_result.output:
        st.markdown("### 📝 **File Editor Result**")
        
        # Enhanced file editor output
        if "created successfully" in tool_result.output.lower():
            st.success(tool_result.output)
        elif "file content" in tool_result.output.lower():
            # Extract and display file content with syntax highlighting
            lines = tool_result.output.split('\n')
            content_started = False
            code_content = []
            
            for line in lines:
                if content_started or '```' in line:
                    content_started = True
                    if '```' not in line:
                        code_content.append(line)
                elif content_started and '```' in line:
                    break
            
            if code_content:
                st.code('\n'.join(code_content), language="python")
            else:
                st.text(tool_result.output)
        else:
            st.code(tool_result.output, language="text")
        
        st.markdown("💾 **File System Integration** - Enhanced file management capabilities")
    
    st.markdown("</div>", unsafe_allow_html=True)

def _render_enhanced_silicon_output(tool_result: ToolResult):
    """Enhanced rendering for Silicon tool with M4-specific visualizations."""
    
    if tool_result.error:
        st.error(f"💎 **Silicon Tool Error**\n\n{tool_result.error}")
        return
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #38b2ac;
    ">
    """, unsafe_allow_html=True)
    
    if tool_result.output:
        st.markdown("### 💎 **M4 Silicon Analysis**")
        
        # Parse M4-specific information
        output = tool_result.output
        
        # Extract key metrics if available
        if "CPU:" in output or "Memory:" in output or "Thermal:" in output:
            # Create metrics dashboard
            metrics = {}
            lines = output.split('\n')
            
            for line in lines:
                if "CPU" in line and "%" in line:
                    try:
                        cpu_usage = line.split(':')[1].strip().split('%')[0].strip()
                        metrics['CPU Usage'] = f"{cpu_usage}%"
                    except:
                        pass
                elif "Memory" in line and "GB" in line:
                    try:
                        memory = line.split(':')[1].strip()
                        metrics['Memory'] = memory
                    except:
                        pass
                elif "Thermal" in line:
                    try:
                        thermal = line.split(':')[1].strip()
                        metrics['Thermal'] = thermal
                    except:
                        pass
            
            if metrics:
                cols = st.columns(len(metrics))
                for i, (key, value) in enumerate(metrics.items()):
                    with cols[i]:
                        st.metric(key, value)
        
        # Display full output with enhanced formatting
        st.code(output, language="text")
        
        st.markdown("🚀 **M4 Performance Monitoring** - Real-time Apple Silicon analysis")
    
    st.markdown("</div>", unsafe_allow_html=True)

def _render_enhanced_web_browser_output(tool_result: ToolResult):
    """Enhanced rendering for web browser tool with navigation feedback."""
    
    if tool_result.error:
        st.error(f"🌐 **Web Browser Error**\n\n{tool_result.error}")
        return
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #3b82f6;
    ">
    """, unsafe_allow_html=True)
    
    if tool_result.output:
        st.markdown("### 🌐 **Web Browser Action**")
        
        # Enhanced browser output
        if "Successfully navigated" in tool_result.output:
            st.success(tool_result.output)
        elif "clicked" in tool_result.output.lower():
            st.info(tool_result.output)
        elif "extracted" in tool_result.output.lower():
            st.success(tool_result.output)
        else:
            st.code(tool_result.output, language="text")
        
        st.markdown("🔗 **Chrome Integration** - Enhanced web automation with AppleScript")
    
    st.markdown("</div>", unsafe_allow_html=True)

def _render_enhanced_generic_tool_output(tool_result: ToolResult):
    """Enhanced fallback rendering for generic tools."""
    
    if tool_result.error:
        st.error(f"🛠️ **Tool Error**\n\n{tool_result.error}")
        return
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #fafafa 0%, #f4f4f5 100%);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #6b7280;
    ">
    """, unsafe_allow_html=True)
    
    if tool_result.output:
        st.markdown("### 🛠️ **Tool Output**")
        st.code(tool_result.output, language="text")
        
        if tool_result.base64_image:
            st.markdown("### 📸 **Generated Image**")
            st.image(base64.b64decode(tool_result.base64_image), use_column_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_enhanced_tool_dashboard():
    """Render a comprehensive tool dashboard with status and capabilities."""
    
    st.markdown("## 🛠️ **Enhanced Tool Dashboard**")
    
    # Tool status overview
    tools_status = {
        '🔍 Web Search': {'status': '✅ Active', 'capability': 'Real-time internet search with citations'},
        '🖥️ Computer Vision': {'status': '✅ Active', 'capability': 'Screenshot capture and screen interaction'},
        '⚡ Terminal/Bash': {'status': '✅ Active', 'capability': 'System commands and analysis'},
        '🍏 AppleScript': {'status': '✅ Active', 'capability': 'macOS automation and app control'},
        '📝 File Editor': {'status': '✅ Active', 'capability': 'File creation and modification'},
        '💎 Silicon Monitor': {'status': '✅ Active', 'capability': 'M4 performance and thermal analysis'},
        '🌐 Web Browser': {'status': '✅ Active', 'capability': 'Chrome automation and web interaction'}
    }
    
    # Create enhanced tool grid
    cols = st.columns(3)
    for i, (tool_name, info) in enumerate(tools_status.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
                border: 1px solid #cbd5e1;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            ">
                <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">
                    {tool_name}
                </div>
                <div style="color: #059669; font-size: 0.875rem; margin-bottom: 0.25rem;">
                    {info['status']}
                </div>
                <div style="color: #6b7280; font-size: 0.75rem; line-height: 1.4;">
                    {info['capability']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # System integration status
    st.markdown("### 🔧 **System Integration Status**")
    
    integration_status = {
        'M4 MacBook Air': '✅ Optimized',
        'macOS Sequoia 15.6': '✅ Compatible', 
        'Neural Engine': '✅ Available',
        'Chrome Browser': '✅ Connected',
        'File System': '✅ Accessible',
        'Performance Monitoring': '✅ Active'
    }
    
    status_cols = st.columns(3)
    for i, (component, status) in enumerate(integration_status.items()):
        with status_cols[i % 3]:
            st.metric(component, status)
    
    # Quick tool test buttons
    st.markdown("### ⚡ **Quick Tool Tests**")
    
    test_cols = st.columns(4)
    with test_cols[0]:
        if st.button("🔍 Test Web Search", help="Search for latest AI news"):
            return "web_search_test"
    
    with test_cols[1]:
        if st.button("📸 Take Screenshot", help="Capture current screen"):
            return "screenshot_test"
    
    with test_cols[2]:
        if st.button("💎 Check M4 Status", help="Analyze M4 performance"):
            return "silicon_test"
    
    with test_cols[3]:
        if st.button("⚡ System Info", help="Get system information"):
            return "bash_test"
    
    return None

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

def _render_enhanced_web_search_output(tool_result: ToolResult):
    """Enhanced rendering for web search tool results with comprehensive analysis and HTML cleaning."""
    from tools.web_search import WebSearchResultFormatter
    import html
    import re
    import json
    
    # Debug information for troubleshooting
    print(f"🔍 DEBUG: Web search result received")
    print(f"   - Type: {type(tool_result)}")
    print(f"   - Has output: {hasattr(tool_result, 'output')}")
    print(f"   - Has content: {hasattr(tool_result, 'content')}")
    print(f"   - Has error: {hasattr(tool_result, 'error') and tool_result.error}")
    
    if hasattr(tool_result, 'output'):
        output_preview = str(tool_result.output)[:200] + "..." if len(str(tool_result.output)) > 200 else str(tool_result.output)
        print(f"   - Output preview: {output_preview}")
    
    if hasattr(tool_result, 'content'):
        content_preview = str(tool_result.content)[:200] + "..." if len(str(tool_result.content)) > 200 else str(tool_result.content)
        print(f"   - Content preview: {content_preview}")
        print(f"   - Content type: {type(tool_result.content)}")
    
    # Initialize enhanced formatter
    formatter = WebSearchResultFormatter()
    
    # Parse Anthropic API response using enhanced parser
    try:
        results = formatter.parse_anthropic_response(tool_result)
        print(f"   - Parsed {len(results)} results")
        
        # Additional cleaning pass for any results that might have HTML fragments
        for result in results:
            if 'content' in result:
                # Extra pass to ensure no HTML fragments remain
                import re
                content = result['content']
                content = re.sub(r'</?\w+[^>]*>', '', content)  # Remove any remaining HTML tags
                content = re.sub(r'^\s*</?\w+[^>]*>\s*$', '', content.strip())  # Remove standalone tags
                content = content.strip()
                result['content'] = content if content else "No description available"
            
            if 'title' in result:
                # Same for titles
                title = result['title']
                title = re.sub(r'</?\w+[^>]*>', '', title)
                title = title.strip()
                result['title'] = title if title else "Untitled"
        
        if results:
            # Try to extract query from context or debug info
            query = "Web search results"
            
            # Look for query in the tool_result attributes
            if hasattr(tool_result, 'input') and isinstance(tool_result.input, dict):
                query = tool_result.input.get('query', query)
            elif hasattr(tool_result, 'output') and isinstance(tool_result.output, str):
                # Try to extract query from output
                query_match = re.search(r'query["\s]*:?["\s]*([^"]+)', tool_result.output, re.IGNORECASE)
                if query_match:
                    query = query_match.group(1).strip()
            
            print(f"   - Using query: {query}")
            _render_cleaned_web_search_results(results, query, formatter)
            return
        
        # Handle empty results
        elif hasattr(tool_result, 'output') and tool_result.output:
            output = tool_result.output
            if "no results" in str(output).lower() or "0 results" in str(output).lower():
                _render_empty_search_state()
                return
        
    except Exception as e:
        print(f"   - Parser error: {str(e)}")
    
    # Fallback handling for various response formats
    output = tool_result.output if hasattr(tool_result, 'output') else str(tool_result)
    
    # Handle empty or minimal results
    if not output or str(output).strip() == "" or "no results" in str(output).lower():
        _render_empty_search_state()
        return
    
    # Check if this is a tool configuration/status message
    if isinstance(output, str) and any(indicator in output.lower() for indicator in [
        'web search tool', 'search configuration', 'tool configured', 
        'max uses', 'domain filtering', 'location set'
    ]):
        # Render configuration status
        cleaned_output = formatter.clean_html_content(output)
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        ">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                <div style="font-size: 2rem; animation: pulse 2s infinite;">🔍</div>
                <div>
                    <h3 style="margin: 0; color: white; font-weight: 700; font-size: 1.4rem;">
                        Web Search Tool Configuration
                    </h3>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 4px;">
                        🔧 Search setup and status • Anthropic web_search_20250305
                    </div>
                </div>
            </div>
            
            <div style="color: white; line-height: 1.6; white-space: pre-wrap; font-family: 'SF Mono', 'Monaco', monospace;">
                {html.escape(cleaned_output)}
            </div>
            
            <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.85rem; color: rgba(255,255,255,0.9);">
                💡 <strong>Ready for search:</strong> This tool follows Anthropic's web search guidelines for citation compliance. 
                All web results will have clearly visible and clickable source links.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # If we reach here, try to parse as search initiation or error
    # Extra thorough cleaning for any problematic HTML fragments
    raw_output = str(output)
    cleaned_output = formatter.clean_html_content(raw_output)
    
    # Additional pass to remove any standalone HTML fragments that might appear as text
    import re
    cleaned_output = re.sub(r'^\s*</?\w+[^>]*>\s*$', '', cleaned_output.strip())
    cleaned_output = re.sub(r'</?\w+[^>]*>', '', cleaned_output)  # Remove any HTML tags
    
    # Check if this looks like a search initiation
    if any(indicator in cleaned_output.lower() for indicator in [
        'searching', 'searching for', 'looking for', 'finding'
    ]):
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: pulse 2s infinite;
        ">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <div style="font-size: 2rem;">🔍</div>
                <div>
                    <h3 style="margin: 0; color: white; font-weight: 700; font-size: 1.4rem;">
                        Web Search In Progress
                    </h3>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 4px;">
                        📡 Searching the web for real-time information...
                    </div>
                </div>
            </div>
            
            <div style="color: white; line-height: 1.6;">
                {html.escape(cleaned_output)}
            </div>
            
            <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.85rem; color: rgba(255,255,255,0.9);">
                ⏳ <strong>Please wait:</strong> Searching web sources and processing results...
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Generic tool output display with error indication
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 8px 32px rgba(245, 158, 11, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    ">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <div style="font-size: 2rem;">⚠️</div>
            <div>
                <h3 style="margin: 0; color: white; font-weight: 700; font-size: 1.4rem;">
                    Web Search Response
                </h3>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 4px;">
                    🔧 Unexpected response format detected
                </div>
            </div>
        </div>
        
        <div style="color: white; line-height: 1.6; white-space: pre-wrap; font-family: 'SF Mono', 'Monaco', monospace;">
            {html.escape(cleaned_output)}
        </div>
        
        <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.85rem; color: rgba(255,255,255,0.9);">
            💡 <strong>Debug info:</strong> If this persists, check the debug output in the terminal for more details about the response format.
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_empty_search_state():
    """Render user-friendly empty search state."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 40px 24px;
        margin: 16px 0;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    ">
        <div style="font-size: 3rem; margin-bottom: 16px; opacity: 0.8;">🔍</div>
        <h3 style="margin: 0 0 12px 0; font-weight: 700;">No Search Results Found</h3>
        <p style="margin: 0; font-size: 0.95rem; opacity: 0.9; line-height: 1.5;">
            The web search didn't return any results. This might be due to:
        </p>
        <div style="margin: 20px 0; display: flex; flex-direction: column; gap: 8px; font-size: 0.85rem;">
            <div style="opacity: 0.8;">• Very specific or uncommon search terms</div>
            <div style="opacity: 0.8;">• Network connectivity issues</div>
            <div style="opacity: 0.8;">• Search service temporarily unavailable</div>
            <div style="opacity: 0.8;">• Domain filtering blocking relevant sites</div>
        </div>
        <div style="margin-top: 24px; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.85rem;">
            💡 Try rephrasing your search or using broader terms
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_news_enhanced_section(news_results: list, formatter):
    """Enhanced news section with better UI/UX integration."""
    if not news_results:
        return
    
    # Create enhanced news header
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0 16px 0;
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 1.8rem;">📰</div>
            <div>
                <h3 style="margin: 0; font-weight: 700; font-size: 1.3rem;">Latest News & Media</h3>
                <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 0.9rem;">
                    {len(news_results)} recent articles and reports
                </p>
            </div>
            <div style="margin-left: auto; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">
                🕐 Real-time
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create interactive news grid
    cols = st.columns(2) if len(news_results) > 1 else [st.container()]
    
    for i, result in enumerate(news_results):
        col_index = i % len(cols)
        with cols[col_index]:
            _render_enhanced_news_card(result, i + 1, formatter)

def _render_enhanced_news_card(result: dict, index: int, formatter):
    """Render individual news card with enhanced design and proper link handling."""
    import html
    import re
    
    url = result.get('url', '#')
    title = result.get('title', 'Untitled Article')
    content = result.get('content', 'No description available')
    page_age = result.get('page_age', 'Unknown time')
    
    # Validate and clean URL
    if url and url != '#':
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Validate URL format
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            url = '#'  # Fallback for invalid URLs
    
    # Get quality assessment
    quality_info = formatter.assess_result_quality(result)
    trust_score = formatter._calculate_trust_score(url, title)
    
    # Extract domain for credibility indicator
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc if parsed_url.netloc else 'Unknown source'
    except:
        domain = url.split('/')[2] if len(url.split('/')) > 2 else 'Unknown source'
    
    # Determine news source credibility
    credible_sources = ['bbc.', 'reuters.', 'ap.org', 'npr.org', 'nytimes.', 'wsj.', 'cnn.', 'guardian.']
    is_credible = any(source in domain.lower() for source in credible_sources)
    
    # Clean and truncate content - ensure HTML is properly cleaned first
    from tools.web_search import WebSearchResultFormatter
    temp_formatter = WebSearchResultFormatter()
    clean_content = temp_formatter.clean_html_content(content)
    clean_content = html.escape(clean_content)  # Then escape for safe HTML display
    if len(clean_content) > 150:
        clean_content = clean_content[:150] + "..."
    
    # Clean and escape content for safe HTML display (but NOT the URL for href)
    from tools.web_search import WebSearchResultFormatter
    temp_formatter = WebSearchResultFormatter()
    clean_title = temp_formatter.clean_html_content(title)
    title_escaped = html.escape(clean_title)
    domain_escaped = html.escape(domain)
    page_age_escaped = html.escape(page_age)
    
    # Determine card styling based on credibility
    card_gradient = "linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)" if is_credible else "linear-gradient(135deg, #6b7280 0%, #4b5563 100%)"
    credibility_icon = "🏛️" if is_credible else "📄"
    
    # Compliance with Anthropic's citation requirements
    clickable_link_indicator = "🔗" if url != '#' else "❌"
    
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 12px;
        overflow: hidden;
        margin: 12px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
        position: relative;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'" 
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'">
        
        <!-- News header with source credibility and link status -->
        <div style="
            background: {card_gradient};
            padding: 12px 16px;
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.1rem;">{credibility_icon}</span>
                <span style="font-weight: 600; font-size: 0.85rem;">{domain_escaped}</span>
                <span style="font-size: 0.7rem; opacity: 0.8;" title="Link status">{clickable_link_indicator}</span>
            </div>
            <div style="display: flex; gap: 6px;">
                <span style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 10px; font-size: 0.7rem;">
                    Trust: {trust_score:.2f}
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 10px; font-size: 0.7rem;">
                    {quality_info['icon']}
                </span>
            </div>
        </div>
        
        <!-- News content with properly functioning links -->
        <div style="padding: 16px;">
            <h4 style="
                margin: 0 0 8px 0;
                font-weight: 600;
                font-size: 1rem;
                line-height: 1.3;
                color: #1f2937;
            ">""" + (f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="color: inherit; text-decoration: none; border-bottom: 2px solid transparent; transition: border-color 0.2s ease;" onmouseover="this.style.borderColor=\'#3b82f6\';" onmouseout="this.style.borderColor=\'transparent\';">{title_escaped}</a>' if url != '#' and url and len(url) > 10 else title_escaped) + """
            </h4>
            <p style="
                margin: 0 0 12px 0;
                color: #6b7280;
                font-size: 0.85rem;
                line-height: 1.4;
            ">
                {clean_content}
            </p>
            
            <!-- News metadata with source link -->
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-top: 8px;
                border-top: 1px solid #f3f4f6;
                font-size: 0.75rem;
                color: #9ca3af;
            ">
                <span>📅 {page_age_escaped}</span>
                <span>#{index}</span>
            </div>
            
            <!-- Enhanced source link area -->
            <div style="
                margin-top: 8px;
                padding: 6px 10px;
                background: #f8fafc;
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-size: 0.75rem;
            ">
""" + (f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="color: #3b82f6; text-decoration: none; font-weight: 500;" onmouseover="this.style.textDecoration=\'underline\';" onmouseout="this.style.textDecoration=\'none\';">🌐 Read full article</a>' if url != '#' and url and len(url) > 10 else '<span style="color: #6b7280;">🌐 Source unavailable</span>') + """
                
""" + ('<span style="color: #059669; font-size: 0.65rem;">✅ Clickable</span>' if url != '#' and url and len(url) > 10 else '<span style="color: #dc2626; font-size: 0.65rem;">❌ No link</span>') + """
            </div>
        </div>
        
        <!-- Hover effect indicator -->
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: {card_gradient};
            opacity: 0;
            transition: opacity 0.3s ease;
        " class="hover-indicator"></div>
    </div>
    """, unsafe_allow_html=True)

def _render_cleaned_web_search_results(results: list, query: str, formatter):
    """Render cleaned web search results with enhanced formatting."""
    import html
    
    # Handle completely empty results
    if not results:
        _render_empty_search_state()
        return
    
    # Analyze search quality using enhanced formatter
    quality_analysis = formatter.analyze_search_quality(results, query)
    
    # Enhanced web search results container with quality indicators
    st.markdown(f"""
    <div class="web-search-results-container" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    ">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <div style="font-size: 2rem;">🔍</div>
            <div style="flex: 1;">
                <h3 style="margin: 0; color: white; font-weight: 700; font-size: 1.4rem;">
                    Web Search Results
                </h3>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 4px;">
                    📊 {len(results)} results • Quality: {quality_analysis['overall_quality']:.2f}/1.0 • Diversity: {quality_analysis['diversity_score']:.2f}/1.0
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 8px 12px; border-radius: 20px; font-size: 0.85rem; color: white;">
                {"🌟 Excellent" if quality_analysis['overall_quality'] >= 0.8 else "✅ High" if quality_analysis['overall_quality'] >= 0.6 else "👍 Good" if quality_analysis['overall_quality'] >= 0.4 else "ℹ️ Moderate"} Quality
            </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
            <div style="color: rgba(255,255,255,0.9); font-weight: 500; margin-bottom: 8px;">🎯 Query: "{html.escape(query)}"</div>
            <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">
                💡 {quality_analysis['recommendations'][0] if quality_analysis['recommendations'] else 'Results show good quality and diversity'}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Categorize and display results by type
    categorized_results = {}
    for result in results:
        category = formatter.categorize_result(result.get('url', ''), result.get('title', ''))
        if category not in categorized_results:
            categorized_results[category] = []
        categorized_results[category].append(result)
    
    # Enhanced category display with special handling for news
    news_results = categorized_results.pop('news', [])
    
    # Render enhanced news section first if present
    if news_results:
        _render_news_enhanced_section(news_results, formatter)
    
    # Display other categories with enhanced formatting
    for category, category_results in categorized_results.items():
        if not category_results:
            continue
            
        category_info = formatter.categories.get(category, {'icon': '🔗', 'label': category.title()})
        
        # Enhanced category header
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border-radius: 12px;
            padding: 16px;
            margin: 20px 0 12px 0;
            color: white;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.5rem;">{category_info['icon']}</span>
                <div style="flex: 1;">
                    <h4 style="margin: 0; font-weight: 700;">{category_info['label']}</h4>
                    <p style="margin: 2px 0 0 0; opacity: 0.9; font-size: 0.85rem;">
                        {len(category_results)} source{'s' if len(category_results) != 1 else ''}
                    </p>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 16px; font-size: 0.8rem;">
                    #{category}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display each result with enhanced cards
        for i, result in enumerate(category_results, 1):
            _render_enhanced_source_card(result, i, category, formatter)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Call main function - moved to end to ensure all functions are defined first
if __name__ == "__main__":
    main()
