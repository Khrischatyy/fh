#!/usr/bin/env python3
"""
Pydantic AI MCP Chat Agent
==========================

Simple terminal chat interface using Pydantic AI with MCP server integration.

This agent connects to the FastAPI MCP server and has access to all 88 API endpoints
as tools. It uses Anthropic Claude with streaming responses for a better UX.

Usage:
    python mcp_chat.py

Environment Variables:
    ANTHROPIC_API_KEY: Your Anthropic API key (required)

Commands:
    exit, quit, :q - Exit the chat
    Ctrl+C - Exit the chat
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

# Load environment variables from root .env file
# In Docker, env vars are already loaded via env_file in docker-compose
# But we'll try to load .env just in case for local testing
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Try loading from root (for Docker container)
    load_dotenv()

# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp/mcp")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = os.getenv("CHAT_MODEL", "anthropic:claude-sonnet-4-0")

# System prompt for the agent
SYSTEM_PROMPT = """You are a helpful AI assistant with access to a comprehensive studio booking API.

You have access to the following capabilities through MCP tools:
- User authentication and management
- Studio/company information
- Room and address details
- Booking management
- Payment processing
- Operating hours and schedules
- Geographic data (countries, cities)

When using tools:
1. Be clear about what information you're retrieving
2. Format responses in a readable way
3. Handle errors gracefully
4. Ask for clarification if needed

Be conversational, helpful, and concise."""


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 70)
    print("  Pydantic AI MCP Chat Agent")
    print("  Connected to: FastAPI MCP Server (88 tools available)")
    print("  Model: Claude Sonnet 4.0")
    print("=" * 70)
    print("\nType your message and press Enter. Type 'exit', 'quit', or ':q' to end.")
    print("-" * 70)


async def chat_loop(agent: Agent, mcp_server: MCPServerStreamableHTTP):
    """
    Main chat loop with streaming responses and message history.

    Args:
        agent: The Pydantic AI agent
        mcp_server: The MCP server connection
    """
    print_banner()

    # Initialize message history for conversation context
    message_history = []

    while True:
        # Get user input
        try:
            user_input = input("\n🧑 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye! 👋")
            break

        # Exit conditions
        if user_input.lower() in ["exit", "quit", ":q", "q"]:
            print("\nGoodbye! 👋")
            break

        # Skip empty inputs
        if not user_input:
            continue

        try:
            print("\n🤖 Assistant: ", end="", flush=True)

            # Stream the response for better UX
            async with agent.run_stream(
                user_input, message_history=message_history
            ) as result:
                async for text in result.stream_text(delta=True):
                    print(text, end="", flush=True)

            print()  # New line after response

            # Update message history with all messages from this run
            message_history = result.all_messages()

            # Show usage stats if available (optional)
            try:
                usage = result.usage()
                if usage:
                    print(
                        f"\n💡 Tokens: {usage.total_tokens} "
                        f"(input: {usage.input_tokens}, output: {usage.output_tokens})"
                    )
            except Exception:
                pass  # Ignore if usage stats not available

        except KeyboardInterrupt:
            print("\n\n⏸️  Response interrupted. Type your next message or 'exit' to quit.")
            continue

        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            print("Please try again or type 'exit' to quit.")


async def test_connection(mcp_server: MCPServerStreamableHTTP):
    """
    Test the MCP server connection and list available tools.

    Args:
        mcp_server: The MCP server connection

    Returns:
        True if connection successful, False otherwise
    """
    try:
        print("\n🔍 Testing MCP server connection...")
        tools = await mcp_server.list_tools()
        print(f"✅ Connected successfully! {len(tools)} tools available.")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        print(f"\nMake sure the MCP server is running at: {MCP_SERVER_URL}")
        return False


async def main():
    """
    Entry point with proper MCP server lifecycle management.
    """
    # Check for API key
    if not ANTHROPIC_API_KEY:
        print("\n❌ Error: ANTHROPIC_API_KEY not found in environment variables.")
        print(
            f"\nPlease ensure your .env file at {env_path} contains:"
        )
        print("ANTHROPIC_API_KEY=your-api-key-here")
        sys.exit(1)

    # Initialize MCP server connection
    mcp_server = MCPServerStreamableHTTP(MCP_SERVER_URL)

    # Create agent with MCP tools
    agent = Agent(
        MODEL,
        toolsets=[mcp_server],
        system_prompt=SYSTEM_PROMPT,
        retries=2,  # Retry failed requests
    )

    # Use async context manager for proper connection handling
    try:
        async with mcp_server:
            # Test connection first
            if not await test_connection(mcp_server):
                sys.exit(1)

            # Start chat loop
            await chat_loop(agent, mcp_server)

    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
