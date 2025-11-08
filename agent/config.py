"""
Configuration for the Agent Orchestrator.

All settings centralized here for easy modification.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"  # Fast, cheap, reliable function calling
TEMPERATURE = 0.0  # Deterministic for demo consistency

# RAG Configuration
RAG_TOP_K = 3  # Number of tools to retrieve
RAG_SCORE_THRESHOLD = 0.0  # Minimum similarity score (0.0 = no filtering)

# Agent Configuration
AGENT_MAX_ITERATIONS = 5  # Maximum steps before giving up
AGENT_VERBOSE = True  # Show agent thinking process (educational!)

# System Prompt
SYSTEM_PROMPT = """You are AgenKampus, an intelligent academic assistant.

You have access to various tools through a secure MCP (Model Context Protocol) interface.
You CANNOT directly access the database - you can only use the provided tools.

**Important Guidelines:**
1. Always use tools when you need information - don't make up answers
2. If a user asks about database content, use the appropriate tool
3. If no suitable tool exists, politely explain what you cannot do
4. Be helpful, accurate, and concise in your responses

**Security Note:**
You only have READ access to the academic database. You CANNOT:
- Modify student grades
- Add or delete students
- Change advisor assignments
- Alter any database records

If a user asks you to modify data, politely explain that you don't have tools for write operations.
"""

# Validate configuration
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found! "
        "Please set it in the .env file at the project root."
    )

# Display configuration (for debugging)
def show_config():
    """Print current configuration."""
    print("="*80)
    print("🔧 AGENT CONFIGURATION")
    print("="*80)
    print(f"OpenAI Model: {OPENAI_MODEL}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"RAG Top-K: {RAG_TOP_K}")
    print(f"RAG Score Threshold: {RAG_SCORE_THRESHOLD}")
    print(f"Max Iterations: {AGENT_MAX_ITERATIONS}")
    print(f"Verbose Mode: {AGENT_VERBOSE}")
    print(f"API Key: {'✓ Configured' if OPENAI_API_KEY else '✗ Missing'}")
    print("="*80)


if __name__ == "__main__":
    show_config()
