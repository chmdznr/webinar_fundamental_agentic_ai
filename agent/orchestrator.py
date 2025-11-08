"""
Agent Orchestrator for AgenKampus

This is the "Brain" - the intelligent manager that:
1. Receives user queries
2. Uses RAG to find relevant tools
3. Decides which tool to use
4. Executes the tool
5. Returns the answer

Architecture:
User Query → RAG Retriever → Agent (LLM) → Tool Execution → Response
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directories to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "mcp_utilitas"))
sys.path.insert(0, str(project_root / "mcp_akademik"))

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage

# Import RAG retriever
from rag.tool_retriever import ToolRetriever

# Import configuration
from agent.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    TEMPERATURE,
    RAG_TOP_K,
    SYSTEM_PROMPT,
    AGENT_MAX_ITERATIONS,
    AGENT_VERBOSE
)


class AgenKampusOrchestrator:
    """
    Main orchestrator that coordinates RAG retrieval and agent execution.

    This implements the 2-step workflow:
    1. RAG Step: Retrieve relevant tools for the query
    2. Agent Step: LLM decides which tool to use and executes it
    """

    def __init__(self):
        """Initialize the orchestrator with RAG and LLM."""
        print("🚀 Initializing AgenKampus Orchestrator...")
        print()

        # Initialize RAG retriever
        print("📚 Loading RAG Tool Retriever...")
        self.retriever = ToolRetriever()
        print()

        # Initialize LLM
        print(f"🤖 Connecting to OpenAI ({OPENAI_MODEL})...")
        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
        print("   ✓ Connected to OpenAI")
        print()

        # Import and wrap MCP tools
        print("🔧 Loading MCP Tools...")
        self.all_tools = self._load_all_tools()
        print(f"   ✓ Loaded {len(self.all_tools)} tools")
        print()

        print("="*80)
        print("✅ AgenKampus Orchestrator Ready!")
        print("="*80)
        print()

    def _load_all_tools(self) -> Dict[str, Tool]:
        """
        Load and wrap all MCP tools as LangChain Tools.

        Returns:
            Dictionary mapping tool names to LangChain Tool objects
        """
        tools = {}

        # Import tool functions from MCP servers
        try:
            # Utilitas tools
            from mcp_utilitas.server import get_waktu_saat_ini, kalkulator_sederhana

            tools["get_waktu_saat_ini"] = Tool(
                name="get_waktu_saat_ini",
                description="Get the current date and time. Returns current system time in ISO 8601 format. Use when user asks about time, date, or 'now'.",
                func=lambda _: get_waktu_saat_ini()
            )

            tools["kalkulator_sederhana"] = Tool(
                name="kalkulator_sederhana",
                description="Calculate simple mathematical expressions. Supports +, -, *, /, ** operations. Takes a string expression like '2+2' or '10*5'.",
                func=kalkulator_sederhana
            )

        except Exception as e:
            print(f"⚠️  Warning: Could not load Utilitas tools: {e}")

        try:
            # Akademik tools
            from mcp_akademik.server import (
                get_dosen_pembimbing,
                get_mata_kuliah_mahasiswa,
                list_all_students
            )

            tools["get_dosen_pembimbing"] = Tool(
                name="get_dosen_pembimbing",
                description="Find the academic advisor (dosen pembimbing) of a student. Requires full student name as input. Returns advisor name or error if not found.",
                func=get_dosen_pembimbing
            )

            tools["get_mata_kuliah_mahasiswa"] = Tool(
                name="get_mata_kuliah_mahasiswa",
                description="Get all courses taken by a student with grades. Requires full student name. Returns list of courses and letter grades.",
                func=get_mata_kuliah_mahasiswa
            )

            tools["list_all_students"] = Tool(
                name="list_all_students",
                description="Get list of all registered students in the database. No parameters needed. Use to discover available student names.",
                func=lambda _: list_all_students()
            )

        except Exception as e:
            print(f"⚠️  Warning: Could not load Akademik tools: {e}")

        return tools

    def _create_agent(self, tools: List[Tool]) -> AgentExecutor:
        """
        Create a LangChain agent with the given tools.

        Args:
            tools: List of LangChain Tool objects

        Returns:
            Configured AgentExecutor
        """
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create OpenAI Functions agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )

        # Create executor
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=AGENT_VERBOSE,
            max_iterations=AGENT_MAX_ITERATIONS,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )

        return executor

    def query(self, user_input: str, use_rag: bool = True) -> Dict[str, Any]:
        """
        Process a user query using the 2-step RAG workflow.

        Args:
            user_input: User's question or request
            use_rag: If True, use RAG to filter tools. If False, use all tools.

        Returns:
            Dictionary with:
                - 'answer': Final answer from agent
                - 'retrieved_tools': Tools retrieved by RAG (if use_rag=True)
                - 'tool_used': Name of tool that was executed (if any)
                - 'intermediate_steps': Agent's reasoning steps
        """
        print("="*80)
        print(f"📝 User Query: \"{user_input}\"")
        print("="*80)
        print()

        # Step 1: RAG Retrieval (optional)
        if use_rag:
            print("🔍 [RAG STEP] Retrieving relevant tools...")
            retrieved_tool_metadata = self.retriever.retrieve(
                user_input,
                top_k=RAG_TOP_K
            )

            if not retrieved_tool_metadata:
                print("   ⚠️  No relevant tools found!")
                return {
                    'answer': "I couldn't find any relevant tools to answer your question.",
                    'retrieved_tools': [],
                    'tool_used': None,
                    'intermediate_steps': []
                }

            # Get tool names
            retrieved_tool_names = [t['name'] for t in retrieved_tool_metadata]

            # Display retrieval results
            print(f"   Retrieved {len(retrieved_tool_names)} tools:")
            for idx, tool_meta in enumerate(retrieved_tool_metadata, 1):
                print(f"      {idx}. {tool_meta['name']} (similarity: {tool_meta['similarity_score']:.3f})")
            print()

            # Get actual Tool objects
            tools = [
                self.all_tools[name]
                for name in retrieved_tool_names
                if name in self.all_tools
            ]

        else:
            print("ℹ️  [NO RAG] Using all available tools...")
            tools = list(self.all_tools.values())
            retrieved_tool_names = list(self.all_tools.keys())
            print()

        # Step 2: Agent Execution
        print("🤖 [AGENT STEP] LLM deciding which tool to use...")
        print()

        agent_executor = self._create_agent(tools)

        try:
            result = agent_executor.invoke({"input": user_input})

            # Extract tool used from intermediate steps
            tool_used = None
            if result.get('intermediate_steps'):
                for step in result['intermediate_steps']:
                    if len(step) >= 1:
                        action = step[0]
                        if hasattr(action, 'tool'):
                            tool_used = action.tool

            print()
            print("="*80)
            print(f"✅ Answer: {result['output']}")
            print("="*80)

            return {
                'answer': result['output'],
                'retrieved_tools': retrieved_tool_names if use_rag else None,
                'tool_used': tool_used,
                'intermediate_steps': result.get('intermediate_steps', [])
            }

        except Exception as e:
            print()
            print("="*80)
            print(f"❌ Error: {str(e)}")
            print("="*80)

            return {
                'answer': f"An error occurred: {str(e)}",
                'retrieved_tools': retrieved_tool_names if use_rag else None,
                'tool_used': None,
                'intermediate_steps': []
            }

    def interactive_mode(self):
        """
        Run the agent in interactive mode for testing.

        User can type queries and see responses in real-time.
        Type 'exit', 'quit', or 'q' to stop.
        """
        print("\n" + "="*80)
        print("🎓 AGENKAMPUS - Interactive Mode")
        print("="*80)
        print("Ask me anything! Type 'exit', 'quit', or 'q' to stop.")
        print("="*80)
        print()

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if user_input.lower() in ['exit', 'quit', 'q', '']:
                    print("\n👋 Goodbye!")
                    break

                # Process query
                result = self.query(user_input, use_rag=True)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """
    Main entry point for the agent orchestrator.
    """
    # Initialize orchestrator
    orchestrator = AgenKampusOrchestrator()

    # Run in interactive mode
    orchestrator.interactive_mode()


if __name__ == "__main__":
    main()
