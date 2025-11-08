# Agent Orchestrator: The Brain

This directory contains the main **Agent Orchestrator** - the intelligent "Brain" that coordinates everything.

## 📁 Two Implementations Available

This project includes **two versions** of the orchestrator:

1. **`orchestrator.py`** - Simple implementation (recommended for demos)
   - Direct function imports
   - Synchronous code
   - Beginner-friendly
   - Perfect for 1-hour webinar

2. **`orchestrator_proper_mcp.py`** - Proper MCP implementation (production-ready)
   - Real client/server protocol
   - Asynchronous code
   - Supports remote servers
   - Standards-compliant

**For detailed comparison:** See [MCP Implementation Comparison](../docs/MCP_IMPLEMENTATION_COMPARISON.md)

## Architecture

```
User: "Siapa dosen pembimbing Agus?"
       ↓
┌──────────────────────────────────────┐
│     Agent Orchestrator (Brain)       │
│                                      │
│  Step 1: RAG Retrieval               │
│  ┌────────────────────────────────┐  │
│  │ Query RAG: Find relevant tools │  │
│  │ → get_dosen_pembimbing (0.87)  │  │
│  │ → get_mata_kuliah (0.45)       │  │
│  │ → list_students (0.32)         │  │
│  └────────────────────────────────┘  │
│           ↓                          │
│  Step 2: Agent Decision              │
│  ┌────────────────────────────────┐  │
│  │ LLM analyzes: "User wants      │  │
│  │ advisor info, not courses"     │  │
│  │ Decision: Use tool #1          │  │
│  └────────────────────────────────┘  │
│           ↓                          │
│  Step 3: Tool Execution              │
│  ┌────────────────────────────────┐  │
│  │ Call: get_dosen_pembimbing()   │  │
│  │ Result: "Dr. Budi Santoso"     │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
       ↓
Answer: "Dosen pembimbing Agus Setiawan
         adalah Dr. Budi Santoso"
```

## Components

### 1. `config.py`
Configuration and settings:
- **OpenAI Model:** GPT-4o-mini (fast, cheap, reliable)
- **Temperature:** 0.0 (deterministic responses)
- **RAG Settings:** Top-K=3, threshold=0.0
- **System Prompt:** Agent instructions and constraints
- **Environment:** API key management

### 2. `orchestrator.py`
Main orchestrator class:

**Key Methods:**
- `__init__()`: Initialize RAG, LLM, and tools
- `query(user_input, use_rag=True)`: Process a user query
- `interactive_mode()`: CLI interface for testing
- `_load_all_tools()`: Wrap MCP functions as LangChain Tools
- `_create_agent()`: Build LangChain agent with tools

**2-Step Workflow:**
```python
# Step 1: RAG Retrieval
relevant_tools = retriever.retrieve(query, top_k=3)

# Step 2: Agent Execution
agent = create_agent(llm, tools=relevant_tools)
response = agent.run(query)
```

## How It Works

### Step 1: Initialization

```python
orchestrator = AgenKampusOrchestrator()

# 1. Load RAG retriever (ChromaDB + embeddings)
retriever = ToolRetriever()

# 2. Connect to OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# 3. Load MCP tools
tools = {
    "get_waktu_saat_ini": Tool(...),
    "kalkulator_sederhana": Tool(...),
    "get_dosen_pembimbing": Tool(...),
    "get_mata_kuliah_mahasiswa": Tool(...),
}
```

### Step 2: Query Processing

```python
result = orchestrator.query("Siapa dosen pembimbing Agus?")

# RAG Step:
retrieved = retriever.retrieve(query, top_k=3)
# → [get_dosen_pembimbing, get_mata_kuliah, list_students]

# Agent Step:
agent = create_agent(llm, tools=retrieved)
answer = agent.run(query)
# → LLM decides to use get_dosen_pembimbing
# → Tool executes: get_dosen_pembimbing("Agus Setiawan")
# → Returns: "Dr. Budi Santoso"

# Response:
# "Dosen pembimbing Agus Setiawan adalah Dr. Budi Santoso"
```

### Step 3: Tool Integration

Tools are wrapped from MCP server functions:

```python
# Import from MCP server
from mcp_akademik.server import get_dosen_pembimbing

# Wrap as LangChain Tool
tool = Tool(
    name="get_dosen_pembimbing",
    description="Find student's academic advisor...",
    func=get_dosen_pembimbing
)

# Agent can now call it
agent.run("Who is Agus's advisor?")
# → Agent: I'll use get_dosen_pembimbing("Agus Setiawan")
# → Tool: Returns "Dr. Budi Santoso"
# → Agent: "The advisor is Dr. Budi Santoso"
```

## Running the Agent

### Interactive Mode

```bash
cd agent
python orchestrator.py
```

**Example Session:**
```
🚀 Initializing AgenKampus Orchestrator...

📚 Loading RAG Tool Retriever...
   Loaded 4 tools
🤖 Connecting to OpenAI (gpt-4o-mini)...
   ✓ Connected to OpenAI
🔧 Loading MCP Tools...
   ✓ Loaded 4 tools

================================================================================
✅ AgenKampus Orchestrator Ready!
================================================================================

================================================================================
🎓 AGENKAMPUS - Interactive Mode
================================================================================
Ask me anything! Type 'exit', 'quit', or 'q' to stop.
================================================================================

👤 You: Jam berapa sekarang?
================================================================================
📝 User Query: "Jam berapa sekarang?"
================================================================================

🔍 [RAG STEP] Retrieving relevant tools...
   Retrieved 2 tools:
      1. get_waktu_saat_ini (similarity: 0.324)
      2. kalkulator_sederhana (similarity: 0.089)

🤖 [AGENT STEP] LLM deciding which tool to use...

> Entering new AgentExecutor chain...

Invoking: `get_waktu_saat_ini` with `{}`


2025-01-08 15:45:23Waktu saat ini adalah 2025-01-08 15:45:23.

> Finished chain.

================================================================================
✅ Answer: Waktu saat ini adalah 2025-01-08 15:45:23.
================================================================================

👤 You: Siapa dosen pembimbing Agus Setiawan?
================================================================================
📝 User Query: "Siapa dosen pembimbing Agus Setiawan?"
================================================================================

🔍 [RAG STEP] Retrieving relevant tools...
   Retrieved 3 tools:
      1. get_dosen_pembimbing (similarity: 0.432)
      2. get_mata_kuliah_mahasiswa (similarity: 0.189)
      3. list_all_students (similarity: 0.112)

🤖 [AGENT STEP] LLM deciding which tool to use...

> Entering new AgentExecutor chain...

Invoking: `get_dosen_pembimbing` with `{'nama_mahasiswa': 'Agus Setiawan'}`


Dosen pembimbing Agus Setiawan: Dr. Budi SantosoDosen pembimbing Agus Setiawan adalah Dr. Budi Santoso.

> Finished chain.

================================================================================
✅ Answer: Dosen pembimbing Agus Setiawan adalah Dr. Budi Santoso.
================================================================================

👤 You: exit
👋 Goodbye!
```

### Programmatic Usage

```python
from orchestrator import AgenKampusOrchestrator

# Initialize
agent = AgenKampusOrchestrator()

# Query with RAG (default)
result = agent.query("What courses did Rini take?")
print(result['answer'])
# → "Rini Wijaya took: Kecerdasan Buatan (A), Pemrograman Web (A)"

# Query without RAG (use all tools)
result = agent.query("Calculate 10*5", use_rag=False)
print(result['answer'])
# → "50"

# Inspect retrieval
result = agent.query("Who is Agus's advisor?")
print(result['retrieved_tools'])
# → ['get_dosen_pembimbing', 'get_mata_kuliah_mahasiswa', 'list_all_students']
print(result['tool_used'])
# → 'get_dosen_pembimbing'
```

## System Prompt

The agent operates under strict constraints:

```python
SYSTEM_PROMPT = """You are AgenKampus, an intelligent academic assistant.

You have access to various tools through a secure MCP interface.
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

If a user asks you to modify data, politely explain that you don't have tools
for write operations.
"""
```

## Educational Features

### Verbose Mode

Set `AGENT_VERBOSE = True` in config.py to see:

```
> Entering new AgentExecutor chain...

Invoking: `get_dosen_pembimbing` with `{'nama_mahasiswa': 'Agus Setiawan'}`

Dosen pembimbing Agus Setiawan: Dr. Budi SantosoDosen pembimbing Agus Setiawan adalah Dr. Budi Santoso.

> Finished chain.
```

This shows:
- **Tool selection:** Which tool the LLM chose
- **Parameters:** What arguments it passed
- **Tool result:** Raw output from the tool
- **Final answer:** Agent's formatted response

### RAG Transparency

See which tools were retrieved:

```
🔍 [RAG STEP] Retrieving relevant tools...
   Retrieved 3 tools:
      1. get_dosen_pembimbing (similarity: 0.432)
      2. get_mata_kuliah_mahasiswa (similarity: 0.189)
      3. list_all_students (similarity: 0.112)
```

This demonstrates:
- **Semantic search:** How RAG finds relevant tools
- **Similarity scores:** How "relevant" each tool is
- **Filtering:** Agent only sees top 3, not all 4 tools

### Intermediate Steps

Access full execution trace:

```python
result = agent.query("Who is Rini's advisor?")

for step in result['intermediate_steps']:
    action, observation = step
    print(f"Tool: {action.tool}")
    print(f"Input: {action.tool_input}")
    print(f"Output: {observation}")
```

## Error Handling

### No Relevant Tools

```
👤 You: What's the weather like?

🔍 [RAG STEP] Retrieving relevant tools...
   ⚠️  No relevant tools found!

✅ Answer: I couldn't find any relevant tools to answer your question.
```

### Tool Not Found

```
👤 You: Delete student records

🤖 [AGENT STEP] LLM deciding which tool to use...

✅ Answer: I don't have tools for deleting or modifying database records.
           I can only read information using these tools:
           - get_dosen_pembimbing
           - get_mata_kuliah_mahasiswa
           - list_all_students
```

### Invalid Parameters

```
👤 You: Who is the advisor of John Doe?

Invoking: `get_dosen_pembimbing` with `{'nama_mahasiswa': 'John Doe'}`

Mahasiswa 'John Doe' tidak ditemukan dalam database

✅ Answer: Student 'John Doe' was not found in the database.
```

## Performance

**Typical Query Flow:**

1. **RAG Retrieval:** ~60ms
   - Embed query: ~50ms
   - ChromaDB search: ~10ms

2. **LLM Decision:** ~500-1000ms
   - OpenAI API call (gpt-4o-mini)
   - Function calling decision

3. **Tool Execution:** ~5-50ms
   - Database query
   - Calculation

**Total:** ~600-1100ms per query

**Cost (OpenAI):**
- Input: ~100-300 tokens
- Output: ~50-100 tokens
- Cost: ~$0.0001-0.0003 per query (gpt-4o-mini)

## Configuration

Edit `config.py` to customize:

```python
# Use a more powerful model
OPENAI_MODEL = "gpt-4o"

# Allow non-deterministic responses
TEMPERATURE = 0.7

# Retrieve more tools
RAG_TOP_K = 5

# Filter low-similarity tools
RAG_SCORE_THRESHOLD = 0.3

# Allow more thinking steps
AGENT_MAX_ITERATIONS = 10

# Disable verbose logging
AGENT_VERBOSE = False
```

## Next Steps

The orchestrator is ready! Next:

1. **Test Demo Scenarios:** Run all 4 test cases
2. **Create Helper Scripts:** Automation for demos
3. **Main README:** Setup instructions

This completes the core AgenKampus implementation! 🎉
