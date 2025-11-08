"""
AgenKampus Agent Orchestrator - Proper MCP Implementation

This is the PROPER way to implement MCP with real client/server communication.
Compare this with orchestrator.py to see the difference between:
- Direct import (simple but not true MCP)
- MCP protocol (production-ready with remote server support)

Key differences:
1. Servers run as separate processes
2. Communication via MCP protocol (stdio/HTTP/SSE)
3. Supports remote MCP servers
4. True client/server architecture
5. Async/await for proper event handling

Usage:
    # Make sure servers are installed and accessible
    python orchestrator_proper_mcp.py

Requirements:
    - mcp package (for client/server communication)
    - asyncio for async operations
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

# MCP imports for proper client/server communication
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Import RAG system
from rag.tool_retriever import ToolRetriever


class ProperMCPOrchestrator:
    """
    Agent orchestrator with PROPER MCP implementation.

    This version connects to MCP servers via the official MCP protocol,
    allowing for true client/server separation and remote server support.
    """

    def __init__(self):
        """Initialize the orchestrator with MCP client connections."""
        print("🚀 Initializing AgenKampus Orchestrator (Proper MCP)")
        print("=" * 60)

        # Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.model_name = "gpt-4o-mini"
        self.temperature = 0.0
        self.rag_top_k = 3
        self.verbose = True

        print(f"\nConfiguration:")
        print(f"  Model: {self.model_name}")
        print(f"  Temperature: {self.temperature}")
        print(f"  RAG Top-K: {self.rag_top_k}")
        print(f"  Verbose: {self.verbose}")

        # Initialize RAG system
        print("\n📚 Initializing RAG System...")
        self.retriever = ToolRetriever()
        print("  ✓ RAG System ready")

        # MCP server connections (will be initialized async)
        self.mcp_sessions = {}
        self.all_tools = {}

        print("\n🔌 MCP Servers will be connected on demand")
        print("=" * 60)

    async def connect_mcp_servers(self):
        """
        Connect to MCP servers via proper MCP protocol.

        This establishes real client/server connections using stdio transport.
        Servers run as separate processes and communicate via JSON-RPC.
        """
        print("\n🔌 Connecting to MCP Servers...")

        # Define MCP servers to connect to
        servers = {
            "utilitas": {
                "command": sys.executable,  # Python executable
                "args": [str(project_root / "mcp_utilitas" / "server.py")],
            },
            "akademik": {
                "command": sys.executable,
                "args": [str(project_root / "mcp_akademik" / "server.py")],
            }
        }

        # Connect to each server
        for server_name, server_config in servers.items():
            try:
                print(f"\n  Connecting to {server_name}...")

                # Create server parameters for stdio transport
                server_params = StdioServerParameters(
                    command=server_config["command"],
                    args=server_config["args"],
                    env=None  # Inherit current environment
                )

                # Connect to the server via stdio
                read, write = await stdio_client(server_params)

                # Create MCP session
                session = ClientSession(read, write)

                # Initialize the session
                await session.initialize()

                # Store the session
                self.mcp_sessions[server_name] = session

                # List available tools from this server
                tools_response = await session.list_tools()
                server_tools = tools_response.tools

                print(f"  ✓ Connected to {server_name}")
                print(f"    Tools available: {len(server_tools)}")

                # Register tools from this server
                for tool_info in server_tools:
                    tool_name = tool_info.name

                    # Create wrapper function for this tool
                    async def call_tool_wrapper(
                        arguments: Dict[str, Any],
                        session=session,
                        tool_name=tool_name
                    ):
                        """Wrapper to call MCP tool via protocol."""
                        result = await session.call_tool(tool_name, arguments)
                        return result.content[0].text if result.content else ""

                    # Register as LangChain tool
                    self.all_tools[tool_name] = Tool(
                        name=tool_name,
                        description=tool_info.description or f"Tool: {tool_name}",
                        func=lambda args, wrapper=call_tool_wrapper: asyncio.run(
                            wrapper(args)
                        ),
                    )

                    print(f"      - {tool_name}")

            except Exception as e:
                print(f"  ⚠️  Failed to connect to {server_name}: {e}")
                print(f"      Make sure {server_config['args'][0]} exists and is executable")

        print(f"\n  ✓ Total tools loaded: {len(self.all_tools)}")

    async def disconnect_mcp_servers(self):
        """Disconnect from all MCP servers."""
        print("\n🔌 Disconnecting from MCP Servers...")

        for server_name, session in self.mcp_sessions.items():
            try:
                # Close the session
                await session.__aexit__(None, None, None)
                print(f"  ✓ Disconnected from {server_name}")
            except Exception as e:
                print(f"  ⚠️  Error disconnecting from {server_name}: {e}")

        self.mcp_sessions.clear()

    def _create_agent(self, tools: List[Tool]) -> AgentExecutor:
        """
        Create a LangChain agent with given tools.

        Args:
            tools: List of LangChain Tool objects

        Returns:
            AgentExecutor configured with the tools
        """
        # Create LLM
        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.openai_api_key,
        )

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant for AgenKampus.
            You have access to tools to help answer questions about students, lecturers, and courses.

            Always use the appropriate tool to get information from the database.
            Be concise and clear in your responses.
            If you cannot answer a question with the available tools, say so politely.

            Respond in Indonesian when the user asks in Indonesian.
            """),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # Create agent
        agent = create_tool_calling_agent(llm, tools, prompt)

        # Create agent executor
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=self.verbose,
            max_iterations=5,
            handle_parsing_errors=True,
        )

    async def query(self, user_input: str, use_rag: bool = True) -> Dict[str, Any]:
        """
        Process a user query using the 2-step RAG workflow with proper MCP.

        Args:
            user_input: User's question or query
            use_rag: Whether to use RAG for tool selection (default: True)

        Returns:
            Dictionary containing the query result and metadata
        """
        print(f"\n{'='*60}")
        print(f"Query: {user_input}")
        print(f"{'='*60}")

        # Make sure MCP servers are connected
        if not self.mcp_sessions:
            await self.connect_mcp_servers()

        # Step 1: RAG Retrieval (if enabled)
        if use_rag:
            print("\n🔍 Step 1: RAG Tool Retrieval")
            retrieved_tools = self.retriever.retrieve(user_input, top_k=self.rag_top_k)

            print(f"  Top {len(retrieved_tools)} relevant tools:")
            for i, tool_info in enumerate(retrieved_tools, 1):
                print(f"    {i}. {tool_info['name']} "
                      f"(similarity: {tool_info['similarity_score']:.3f})")

            # Filter to only retrieved tools
            tool_names = [t["name"] for t in retrieved_tools]
            selected_tools = [
                self.all_tools[name]
                for name in tool_names
                if name in self.all_tools
            ]

            if not selected_tools:
                print("  ⚠️  No matching tools found, using all tools")
                selected_tools = list(self.all_tools.values())
        else:
            print("\n  RAG disabled, using all available tools")
            selected_tools = list(self.all_tools.values())

        # Step 2: Agent Execution
        print(f"\n🤖 Step 2: Agent Execution")
        print(f"  Agent has access to {len(selected_tools)} tools")

        agent_executor = self._create_agent(selected_tools)

        try:
            result = agent_executor.invoke({"input": user_input})

            print(f"\n✅ Query completed successfully")
            return {
                "success": True,
                "query": user_input,
                "answer": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
            }

        except Exception as e:
            print(f"\n❌ Error during query execution: {e}")
            return {
                "success": False,
                "query": user_input,
                "error": str(e),
            }

    async def run_interactive(self):
        """
        Run the orchestrator in interactive mode.

        Users can input queries and see the agent's responses in real-time.
        Type 'exit' or 'quit' to stop.
        """
        print("\n" + "="*60)
        print("🎓 AgenKampus Interactive Mode (Proper MCP)")
        print("="*60)
        print("\nAsk questions about students, lecturers, or courses.")
        print("Type 'exit' or 'quit' to stop.\n")

        # Connect to MCP servers
        await self.connect_mcp_servers()

        try:
            while True:
                try:
                    # Get user input
                    user_input = input("\n👤 You: ").strip()

                    # Check for exit commands
                    if user_input.lower() in ["exit", "quit", "q"]:
                        print("\n👋 Goodbye!")
                        break

                    # Skip empty input
                    if not user_input:
                        continue

                    # Process query
                    result = await self.query(user_input)

                    # Display result
                    if result["success"]:
                        print(f"\n🤖 Agent: {result['answer']}")
                    else:
                        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")

                except KeyboardInterrupt:
                    print("\n\n👋 Interrupted. Goodbye!")
                    break
                except Exception as e:
                    print(f"\n❌ Unexpected error: {e}")

        finally:
            # Disconnect from MCP servers
            await self.disconnect_mcp_servers()


async def main():
    """Main entry point for the proper MCP orchestrator."""
    try:
        # Create orchestrator
        orchestrator = ProperMCPOrchestrator()

        # Run in interactive mode
        await orchestrator.run_interactive()

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version (async requires 3.7+)
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher required for async support")
        sys.exit(1)

    # Run the async main function
    asyncio.run(main())
