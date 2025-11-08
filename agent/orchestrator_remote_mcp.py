"""
Remote-aware MCP Orchestrator for AgenKampus.

This version reads MCP server definitions from a YAML file so each server can run
remotely (e.g., FastMCP over SSE/HTTP) or locally (spawned via stdio). It keeps
the RAG-for-Tools workflow identical to the original orchestration flow.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

# Add project root for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag.tool_retriever import ToolRetriever


CONFIG_ENV_VAR = "MCP_SERVERS_CONFIG"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "mcp_servers.yaml"


class RemoteMCPOrchestrator:
    """
    Agent orchestrator that connects to MCP servers defined in a YAML config.

    Supports both remote (SSE/HTTP) and local (stdio) transports per server.
    """

    def __init__(self):
        load_dotenv()

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))
        self.rag_top_k = int(os.getenv("RAG_TOP_K", "3"))
        self.verbose = os.getenv("AGENT_VERBOSE", "true").lower() == "true"
        self.max_iterations = int(os.getenv("AGENT_MAX_ITERATIONS", "5"))

        self.server_configs = self._load_server_configs()

        print("🚀 Initializing AgenKampus Remote MCP Orchestrator")
        print("=" * 70)
        print(f"Model: {self.model_name}")
        print(f"Temperature: {self.temperature}")
        print(f"RAG Top-K: {self.rag_top_k}")
        print(f"Verbose: {self.verbose}")
        print(f"Server config file: {self._config_path()}")

        # Initialize RAG system
        print("\n📚 Initializing RAG Retriever...")
        self.retriever = ToolRetriever()
        print("   ✓ RAG ready")

        # Connection/session tracking
        self.transport_contexts: Dict[str, Any] = {}
        self.session_contexts: Dict[str, Any] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.all_tools: Dict[str, Tool] = {}

    def _config_path(self) -> Path:
        """Return resolved config path."""
        path_str = os.getenv(CONFIG_ENV_VAR, str(DEFAULT_CONFIG_PATH))
        return Path(path_str).expanduser().resolve()

    def _load_server_configs(self) -> List[Dict[str, Any]]:
        """Load and validate server definitions from YAML configuration."""
        config_path = self._config_path()
        if not config_path.exists():
            raise FileNotFoundError(
                f"MCP server config not found at {config_path}. "
                f"Create it or set {CONFIG_ENV_VAR} to the correct path."
            )

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        servers = data.get("servers", [])
        if not servers:
            raise ValueError(f"No servers defined in {config_path}")

        return servers

    async def _connect_sse(self, server_cfg: Dict[str, Any]):
        """Connect to remote MCP server via SSE transport."""
        url = server_cfg.get("url")
        if not url:
            raise ValueError(f"SSE transport for {server_cfg.get('name')} requires 'url'")

        headers = server_cfg.get("headers")
        timeout = float(server_cfg.get("timeout", 5))
        sse_timeout = float(server_cfg.get("sse_read_timeout", 60 * 5))

        ctx = sse_client(
            url=url,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_timeout,
        )
        read, write = await ctx.__aenter__()
        return ctx, read, write

    async def _connect_stdio(self, server_cfg: Dict[str, Any]):
        """Spawn local MCP server via stdio (same behavior as proper MCP)."""
        command = server_cfg.get("command", sys.executable)
        args = server_cfg.get("args")
        if not args:
            raise ValueError(
                f"Stdio transport for {server_cfg.get('name')} requires 'args' (server script path)"
            )

        env = server_cfg.get("env")
        params = StdioServerParameters(command=command, args=args, env=env)
        ctx = stdio_client(params)
        read, write = await ctx.__aenter__()
        return ctx, read, write

    async def connect_mcp_servers(self):
        """Connect to all MCP servers defined in the config file."""
        if self.sessions:
            return  # Already connected

        print("\n🔌 Connecting to MCP servers defined in config...")

        for server_cfg in self.server_configs:
            name = server_cfg.get("name", "unnamed")
            transport = server_cfg.get("transport", "sse").lower()
            print(f"\n  Connecting to '{name}' via {transport.upper()}... ", end="")

            try:
                if transport == "sse":
                    ctx, read, write = await self._connect_sse(server_cfg)
                elif transport == "stdio":
                    ctx, read, write = await self._connect_stdio(server_cfg)
                else:
                    raise ValueError(f"Unsupported transport '{transport}' for server '{name}'")

                self.transport_contexts[name] = ctx

                session_ctx = ClientSession(read, write)
                session = await session_ctx.__aenter__()

                self.session_contexts[name] = session_ctx
                self.sessions[name] = session

                await session.initialize()
                tools_response = await session.list_tools()

                print(f"✓ connected ({len(tools_response.tools)} tools)")

                self._register_tools_from_session(name, session, tools_response.tools)

            except Exception as exc:
                print(f"\n  ⚠️  Failed to connect to '{name}': {exc}")
                raise

        print(f"\n✅ Total tools available: {len(self.all_tools)}")

    def _register_tools_from_session(self, server_name: str, session: ClientSession, mcp_tools):
        """Wrap MCP tools from a session as LangChain tools."""

        def make_wrapper(sess: ClientSession, tool_info):
            schema = tool_info.inputSchema or {}
            required_props = schema.get("required", [])
            properties = schema.get("properties", {})

            async def async_wrapper(arguments):
                payload = self._prepare_tool_arguments(arguments, required_props, properties)

                result = await sess.call_tool(tool_info.name, payload)
                if result.content:
                    # Return concatenated text parts
                    return "\n".join(part.text for part in result.content if hasattr(part, "text") and part.text)
                return ""

            def sync_wrapper(_):
                raise RuntimeError(
                    f"Tool '{tool_info.name}' from server '{server_name}' "
                    "must be called asynchronously via coroutine."
                )

            return async_wrapper, sync_wrapper

        for tool in mcp_tools:
            async_func, sync_func = make_wrapper(session, tool)

            lc_tool = Tool(
                name=tool.name,
                description=tool.description or f"MCP tool from {server_name}",
                func=sync_func,
                coroutine=async_func,
            )

            self.all_tools[tool.name] = lc_tool
            print(f"      - Registered tool: {tool.name}")

    @staticmethod
    def _prepare_tool_arguments(
        arguments: Any,
        required_props: List[str],
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize LangChain tool arguments to match MCP schema expectations.

        Drops extra keys when a tool takes no parameters and maps positional
        inputs to the first required property when present.
        """
        # If the tool declares no properties, always send an empty payload.
        if not properties and not required_props:
            return {}

        if isinstance(arguments, dict):
            if not properties:
                # Tool expects required props but schema omitted properties; fallback to first required.
                if required_props:
                    first = required_props[0]
                    return {first: arguments.get(first)}
                return {}

            filtered = {k: v for k, v in arguments.items() if k in properties}
            if filtered:
                return filtered

            # No intersection; fallback to first required prop if available.
            if required_props:
                first = required_props[0]
                return {first: arguments.get(first)}
            return {}

        if isinstance(arguments, str):
            if required_props:
                return {required_props[0]: arguments}
            return {}

        if arguments is None:
            return {}

        # Fallback for other scalar types.
        if required_props:
            return {required_props[0]: arguments}

        return {}

    async def disconnect_mcp_servers(self):
        """Cleanly disconnect from all MCP sessions/transports."""
        for name, session_ctx in self.session_contexts.items():
            try:
                await session_ctx.__aexit__(None, None, None)
                print(f"  🔌 Closed session for {name}")
            except Exception as exc:
                print(f"  ⚠️  Error closing session for {name}: {exc}")

        for name, transport_ctx in self.transport_contexts.items():
            try:
                await transport_ctx.__aexit__(None, None, None)
                print(f"  🔌 Closed transport for {name}")
            except Exception as exc:
                print(f"  ⚠️  Error closing transport for {name}: {exc}")

        self.session_contexts.clear()
        self.transport_contexts.clear()
        self.sessions.clear()
        self.all_tools.clear()

    def _create_agent(self, tools: List[Tool]) -> AgentExecutor:
        """Create LangChain agent with provided tools."""
        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.openai_api_key,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are AgenKampus, a helpful academic assistant.
Always use the provided MCP tools to retrieve information. If no tool fits,
politely explain the limitation. Respond in Indonesian when users use Indonesian."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=self.verbose,
            max_iterations=self.max_iterations,
            handle_parsing_errors=True,
        )

    async def query(self, user_input: str, use_rag: bool = True) -> Dict[str, Any]:
        """Process a query using RAG + remote MCP tool execution."""
        await self.connect_mcp_servers()

        print(f"\n{'=' * 80}\nQuery: {user_input}\n{'=' * 80}")

        if use_rag:
            retrieved = self.retriever.retrieve(user_input, top_k=self.rag_top_k)
            print("\n🔍 RAG Retrieval Results:")
            for idx, tool_info in enumerate(retrieved, 1):
                score = tool_info.get("similarity_score", 0.0)
                print(f"  {idx}. {tool_info['name']} (score: {score:.3f})")

            tool_names = [tool["name"] for tool in retrieved]
            selected_tools = [
                self.all_tools[name]
                for name in tool_names
                if name in self.all_tools
            ]

            if not selected_tools:
                print("  ⚠️  No overlapping tools between RAG results and MCP registrations. Using all tools.")
                selected_tools = list(self.all_tools.values())
        else:
            selected_tools = list(self.all_tools.values())

        agent_executor = self._create_agent(selected_tools)

        try:
            result = await agent_executor.ainvoke({"input": user_input})
            answer = result.get("output", "")
            # print(f"\n✅ Answer: {answer}")
            return {
                "success": True,
                "answer": answer,
                "intermediate_steps": result.get("intermediate_steps", []),
            }
        except Exception as exc:
            print(f"\n❌ Error during query execution: {exc}")
            return {
                "success": False,
                "error": str(exc),
            }

    async def run_interactive(self):
        """Interactive CLI."""
        print("\n" + "=" * 70)
        print("🎓 AgenKampus Remote MCP Interactive Mode")
        print("=" * 70)
        print("Type 'exit' to quit.\n")

        await self.connect_mcp_servers()

        try:
            while True:
                user_input = input("👤 You: ").strip()
                if user_input.lower() in {"exit", "quit", "q"}:
                    break
                if not user_input:
                    continue

                result = await self.query(user_input)
                if result["success"]:
                    print(f"🤖 Agent: {result['answer']}")
                else:
                    print(f"❌ Error: {result['error']}")
        finally:
            await self.disconnect_mcp_servers()


async def main():
    orchestrator = RemoteMCPOrchestrator()
    await orchestrator.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
