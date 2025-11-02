#!/usr/bin/env python3
"""
Test script for MCP chat agent
Runs a simple automated test without interactive input
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

# Load environment variables
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


async def test_mcp_connection():
    """Test MCP server connection and agent"""
    print("\n" + "=" * 70)
    print("  MCP Chat Agent Test")
    print("=" * 70)

    # Check API key
    if not ANTHROPIC_API_KEY:
        print("\n❌ Error: ANTHROPIC_API_KEY not found")
        return False

    print(f"\n✓ API key found: {ANTHROPIC_API_KEY[:20]}...")
    print(f"✓ MCP server URL: {MCP_SERVER_URL}")
    print(f"✓ Model: {MODEL}")

    # Initialize MCP server
    mcp_server = MCPServerStreamableHTTP(MCP_SERVER_URL)

    try:
        async with mcp_server:
            # Test connection
            print("\n🔍 Testing MCP server connection...")
            tools = await mcp_server.list_tools()
            print(f"✅ Connected! {len(tools)} tools available")

            # Show first few tools
            print("\nFirst 5 tools:")
            for tool in tools[:5]:
                print(f"  - {tool.name}")

            # Create agent
            print("\n🤖 Creating Pydantic AI agent...")
            agent = Agent(
                MODEL,
                toolsets=[mcp_server],
                system_prompt="You are a helpful assistant.",
                retries=2,
            )
            print("✅ Agent created successfully")

            # Test simple query
            print("\n💬 Testing simple query...")
            result = await agent.run("Hello! Can you confirm you're working?")
            print(f"\n🤖 Response: {result.output}")

            # Show usage stats
            try:
                usage = result.usage()
                if usage:
                    print(f"\n💡 Usage: {usage.total_tokens} tokens")
            except:
                pass

            print("\n" + "=" * 70)
            print("✅ All tests passed!")
            print("=" * 70)
            print("\nYou can now run the interactive chat:")
            print("  docker compose -f dev.yml exec api python mcp_chat.py")
            print()

            return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_connection())
    sys.exit(0 if success else 1)
