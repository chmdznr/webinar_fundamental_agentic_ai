# 🎓 AgenKampus: Educational Agentic AI Demo

**A minimalist but realistic demonstration of Agentic AI with MCP and RAG-for-Tools**

Built for: Webinar Fundamental Agentic AI
Duration: 1-hour demo
Target Audience: Beginners

## 🎯 What You'll Learn

This project demonstrates **four key concepts**:

1. **Agent (Brain)** - AI that makes decisions and uses tools (powered by OpenAI GPT-4o-mini)
2. **MCP (Security Bridge)** - Model Context Protocol ensures AI never directly touches your database
3. **Tools (Workers)** - Actual functions that do real work (time, calculator, database queries)
4. **RAG-for-Tools (Librarian)** - Semantic search to find relevant tools (ChromaDB + embeddings)

## 🏗️ Architecture

```
User: "Siapa dosen pembimbing Agus?"
       ↓
┌──────────────────────────────────────────────┐
│         Agent Orchestrator (Brain)           │
│                OpenAI GPT-4o-mini            │
└─────┬────────────────────────────────────┬───┘
      │                                    │
      │ Step 1: Find Tools                 │ Step 2: Execute Tool
      ▼                                    ▼
┌──────────────────────┐        ┌──────────────────────┐
│   RAG Retriever      │        │    MCP Servers       │
│   (ChromaDB)         │        │  ┌────────────────┐  │
│   - Embeddings       │        │  │ Utilitas       │  │
│   - Similarity       │        │  │ - time         │  │
│     Search           │        │  │ - calculator   │  │
└──────────────────────┘        │  └────────────────┘  │
                                │  ┌────────────────┐  │
                                │  │ Akademik       │  │
                                │  │ - get_advisor  │  │
                                │  │ - get_courses  │  │
                                │  └────────┬───────┘  │
                                └───────────┼──────────┘
                                            │
                                            ▼
                                ┌──────────────────────┐
                                │   SQLite Database    │
                                │     (kampus.db)      │
                                └──────────────────────┘
```

## 📦 Project Structure

```
webinar_fundamental_agentic_ai/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env                         # API keys (OpenAI, etc.)
│
├── database/                    # SQLite database layer
│   ├── kampus.db               # Academic data (auto-generated)
│   ├── schema.sql              # Table definitions
│   ├── setup_database.py       # Database initialization
│   └── README.md
│
├── mcp_utilitas/               # MCP Server #1: Utility tools
│   ├── server.py               # FastMCP server
│   └── README.md
│
├── mcp_akademik/               # MCP Server #2: Academic tools
│   ├── server.py               # FastMCP server
│   ├── database.py             # Safe database access
│   └── README.md
│
├── rag/                        # RAG-for-Tools implementation
│   ├── tool_retriever.py       # ChromaDB + semantic search
│   ├── tool_descriptions.json  # Tool metadata
│   ├── chroma_db/              # Vector database (auto-generated)
│   └── README.md
│
├── agent/                      # Agent Orchestrator
│   ├── orchestrator.py         # Main agent (direct imports)
│   ├── orchestrator_proper_mcp.py  # True MCP over stdio
│   ├── orchestrator_remote_mcp.py  # YAML-driven remote MCP
│   ├── mcp_servers.yaml        # Default remote server config
│   ├── config.py               # Configuration
│   └── README.md
│
├── scripts/                    # Helper scripts
│   ├── test_demo_scenarios.py          # Test all 4 demo scenarios (simple agent)
│   ├── test_demo_scenarios_proper_mcp.py # Exercise proper MCP orchestrator
│   ├── test_remote_mcp.py              # Smoke-test remote MCP orchestration
│   └── run_remote_demo.sh              # Start SSE servers + run remote test
│
└── docs/
    └── plans/
        └── 2025-01-08-agenkampus-design.md  # Design document
```

## 🚀 Quick Start (5 Minutes)

### 1. Setup Environment

```bash
# Create conda environment
conda create -n agenkampus python=3.12 -y
conda activate agenkampus

# Install dependencies (using uv for speed)
pip install uv
uv pip install -r requirements.txt
```

### 2. Setup Database

```bash
cd database
python setup_database.py
cd ..
```

**Expected Output:**
```
Creating database at kampus.db
Executing schema...
✅ Database setup complete!
```

### 3. Verify .env File

Make sure your `.env` file has:
```env
OPENAI_API_KEY=sk-proj-...your-key-here...
```

### 4. Test RAG System

```bash
python rag/tool_retriever.py
```

**Expected:** Embeddings loaded, 4 tools indexed, demo queries working ✅

### 5. Test Agent System

```bash
python scripts/test_demo_scenarios.py --quick
```

**Expected:** Agent answers "Siapa dosen pembimbing Agus?" correctly ✅

## 🎬 Running the Demo

### Interactive Mode

```bash
cd agent
python orchestrator.py
```

Then try these queries:

```
👤 You: Jam berapa sekarang?
🤖 Agent: Waktu saat ini adalah 2025-01-08 15:45:23

👤 You: Siapa dosen pembimbing Agus Setiawan?
🤖 Agent: Dosen pembimbing Agus Setiawan adalah Dr. Budi Santoso

👤 You: Mata kuliah apa yang diambil Rini Wijaya?
🤖 Agent: Rini Wijaya mengambil: Kecerdasan Buatan (A), Pemrograman Web (A)

👤 You: Ubah nilai Agus menjadi C
🤖 Agent: Maaf, saya tidak memiliki tools untuk mengubah data...
```

### Test All 4 Scenarios (Local Imports)

```bash
python scripts/test_demo_scenarios.py
```

This will run all demo scenarios with detailed output.

### Remote MCP Demo (SSE)

When you want to prove that the agent can talk to **real remote MCP servers**, use the remote orchestrator workflow:

```bash
conda activate agenkampus
./scripts/run_remote_demo.sh            # installs deps, launches both servers (SSE), runs tests
# or pass extra args to the test harness, e.g.
./scripts/run_remote_demo.sh --no-rag --query "Jam berapa sekarang?"
```

The script will:
1. Install dependencies via `uv pip install -r requirements.txt`
2. Launch `mcp_utilitas/server.py` on `127.0.0.1:8081` and `mcp_akademik/server.py` on `127.0.0.1:8082` using SSE transport
3. Run `scripts/test_remote_mcp.py`, which in turn drives `agent/orchestrator_remote_mcp.py`

Remote endpoints are configured through `agent/mcp_servers.yaml`. Update the URLs/ports (or point `MCP_SERVERS_CONFIG` to a different file) when your servers live on other machines.

## 📚 Component Details

### Database Layer (`database/`)

**Tables:**
- `dosen` - Lecturers (2 entries)
- `mahasiswa` - Students (2 entries)
- `mata_kuliah` - Courses (3 entries)
- `transkrip` - Grades (4 entries)

**Sample Data:**
- **Students:** Agus Setiawan, Rini Wijaya
- **Advisors:** Dr. Budi Santoso, Prof. Siti Aminah
- **Courses:** Kecerdasan Buatan, Basis Data Lanjut, Pemrograman Web

[Full Documentation →](database/README.md)

### MCP Servers (`mcp_utilitas/` & `mcp_akademik/`)

**Utilitas Tools:**
- `get_waktu_saat_ini()` - Returns current datetime
- `kalkulator_sederhana(expr)` - Safe math calculator

**Akademik Tools:**
- `get_dosen_pembimbing(nama)` - Find student's advisor (2-table JOIN)
- `get_mata_kuliah_mahasiswa(nama)` - Get student's courses (3-table JOIN)
- `list_all_students()` - List all students

**Key Security Feature:** All database queries use parameterized SQL (no injection risk!)

[MCP Utilitas →](mcp_utilitas/README.md) | [MCP Akademik →](mcp_akademik/README.md)

### RAG System (`rag/`)

**Purpose:** Find relevant tools using semantic search

**Components:**
- **ChromaDB:** Vector database for tool descriptions
- **SentenceTransformer:** `all-MiniLM-L6-v2` for embeddings
- **Tool Retriever:** Semantic search engine

**How It Works:**
1. Index tool descriptions as vectors
2. User query → Convert to vector
3. Find top-K most similar tool vectors
4. Return only relevant tools to agent

**Performance:** ~60ms per query, supports 1000+ tools

[Full Documentation →](rag/README.md)

### Agent Orchestrator (`agent/`)

**Purpose:** The "Brain" that coordinates everything

**2-Step Workflow:**
1. **RAG Step:** Retrieve top 3 relevant tools
2. **Agent Step:** LLM decides which to use and executes

**Implementations available:**

- `orchestrator.py` — simple direct-import version (best for quick demos)
- `orchestrator_proper_mcp.py` — full MCP stdio client that spawns the servers as subprocesses, now with graceful shutdown
- `orchestrator_remote_mcp.py` — new YAML-driven client that connects to remote MCP servers over SSE/HTTP (used by `scripts/run_remote_demo.sh`)

See `agent/README.md` for when to choose each approach and how to customize `mcp_servers.yaml`.

**Cost:** ~$0.0002 per query

[Full Documentation →](agent/README.md)

## 🎓 Educational Highlights

### 1. Why MCP is Secure

**Traditional Approach (DANGEROUS):**
```python
# AI generates SQL directly
user: "Show me all students"
ai_generates: "SELECT * FROM mahasiswa"
database.execute(ai_generated_sql)  # 😱 SQL INJECTION RISK!
```

**MCP Approach (SAFE):**
```python
# AI calls predefined tool
user: "Show me all students"
ai_calls: list_all_students()
# Tool has pre-written, safe SQL
# AI never writes SQL directly ✅
```

### 2. Why RAG-for-Tools Matters

**Without RAG:**
- Agent sees ALL 1000 tools in every request
- Token limit exceeded → crashes
- Or costs $$$$ per query

**With RAG:**
- Agent sees only top 3 relevant tools
- Fast, cheap, accurate
- Scales to thousands of tools

### 3. The 2-Step Workflow

```python
# User asks
query = "Siapa dosen pembimbing Agus?"

# Step 1: RAG finds relevant tools
tools = rag.retrieve(query, top_k=3)
# → [get_dosen_pembimbing, get_mata_kuliah, list_students]

# Step 2: Agent decides which to use
agent = create_agent(llm, tools=tools)
answer = agent.run(query)
# → Agent: "I'll use get_dosen_pembimbing"
# → Tool: Returns "Dr. Budi Santoso"
# → Agent: "Dosen pembimbing Agus adalah Dr. Budi Santoso"
```

## 🧪 Testing

### Quick Test (Single Query)

```bash
python scripts/test_demo_scenarios.py --quick
```

### Full Test (All 4 Scenarios)

```bash
python scripts/test_demo_scenarios.py
```

**The 4 Scenarios:**
1. ✅ Time query → Uses `get_waktu_saat_ini`
2. ✅ Advisor query → Uses `get_dosen_pembimbing` → "Dr. Budi"
3. ✅ Courses query → Uses `get_mata_kuliah_mahasiswa` → Lists courses
4. ✅ Write attempt → **FAILS** → "I don't have write tools" (Security!)

## 📊 Performance Metrics

**Typical Query:**
- RAG Retrieval: ~60ms
- LLM Decision: ~500-1000ms
- Tool Execution: ~5-50ms
- **Total: ~600-1100ms**

**Cost (OpenAI GPT-4o-mini):**
- Per query: ~$0.0001-0.0003
- 1000 queries: ~$0.10-0.30

**Scaling:**
- 4 tools: Works ✅
- 100 tools: Works ✅
- 1000 tools: Works ✅
- RAG keeps it fast regardless of tool count!

## 🔧 Troubleshooting

### "OpenAI API key not found"

```bash
# Check .env file exists
cat .env

# Should contain:
# OPENAI_API_KEY=sk-proj-...

# If missing, create it:
echo 'OPENAI_API_KEY=your-key-here' > .env
```

### "Database not found"

```bash
cd database
python setup_database.py
```

### "Model not found" (HuggingFace)

First run downloads ~80MB model:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Reset Everything

```bash
# Delete generated files
rm -rf database/kampus.db
rm -rf rag/chroma_db

# Regenerate
cd database && python setup_database.py
cd ../rag && python tool_retriever.py
```

## 🎤 Webinar Presentation

### 📊 Presentation Slides

**Interactive HTML Slides:** [docs/slides.html](docs/slides.html)
- Open in browser (Chrome, Firefox, Safari)
- Navigate: Arrow keys or click
- Fullscreen: Press `F` key
- Overview: Press `ESC` key
- Print to PDF: Add `?print-pdf` to URL


### Quick Demo Flow

1. **[00:00-05:00]** Introduction - Explain Agentic AI concepts
2. **[05:00-15:00]** Database & MCP Servers - Show security patterns
3. **[15:00-25:00]** RAG System - Demonstrate tool retrieval
4. **[25:00-45:00]** Live Agent Demo - Run all 4 scenarios
5. **[45:00-55:00]** Behind the Scenes - Code walkthrough
6. **[55:00-60:00]** Q&A and next steps

## 📖 Further Reading

- [Design Document](docs/plans/2025-01-08-agenkampus-design.md)
- [Database README](database/README.md)
- [MCP Utilitas README](mcp_utilitas/README.md)
- [MCP Akademik README](mcp_akademik/README.md)
- [RAG README](rag/README.md)
- [Agent README](agent/README.md)

## 🎯 Next Steps

After the demo, students can:

1. **Add More Tools**
   - `get_jadwal_kuliah()` - Get class schedule
   - `search_mahasiswa()` - Search by criteria
   - `calculate_gpa()` - Calculate GPA

2. **Improve RAG**
   - Use better embedding models
   - Add tool categories
   - Implement hybrid search (semantic + keyword)

3. **Add UI**
   - Streamlit dashboard
   - Web interface with FastAPI
   - Chat history

4. **Deploy**
   - Containerize with Docker
   - Deploy to cloud (AWS, GCP, Azure)
   - Add authentication

5. **Production Hardening**
   - Add tool usage analytics
   - Implement rate limiting
   - Add caching layer
   - Monitor LLM costs

## 👥 Credits

Built for: Adinesia Webinar Series
Instructor: Achmad Zaenuri
Date: November 2025
Tech Stack: Python, LangChain, OpenAI, ChromaDB, FastMCP, SQLite

## 📄 License

Educational purposes only. Not for production use without proper security review.

---

**Questions?** Open an issue or contact the instructor!

**Ready to start?** → `conda create -n agenkampus python=3.12 -y` 🚀
