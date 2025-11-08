# AgenKampus Implementation Design

**Date:** 2025-01-08
**Project:** Webinar Fundamental Agentic AI - "AgenKampus" Demo
**Timeline:** 1 week
**Target:** Educational demo for beginners (1 hour presentation)

## 1. Overview

Building a minimal but realistic Agentic AI stack demonstrating:
- **Agent (Brain):** Intelligent manager powered by OpenAI GPT-4o-mini
- **MCP (Bridge):** Secure protocol ensuring AI never directly touches database
- **Tools (Workers):** Actual workers performing real tasks
- **RAG-for-Tools (Librarian):** ChromaDB to retrieve relevant tools from large toolset

## 2. Technology Stack

**Confirmed Choices:**
- **LLM:** OpenAI GPT-4o-mini (reliable function calling, excellent docs)
- **Orchestration:** LangChain (production-grade agent framework)
- **MCP Servers:** FastMCP (Python-based MCP implementation)
- **Vector DB:** ChromaDB (file-based, no server needed)
- **Relational DB:** SQLite (single file, portable)
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (local, fast, free)
- **Environment:** Python 3.12 in conda env `agenkampus`
- **Package Manager:** `uv` for fast installs

## 3. Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                         User Query                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Orchestrator (LangChain)                 │
│                  - GPT-4o-mini Brain                        │
│                  - 2-Step RAG Workflow                      │
└──────┬────────────────────────────────────────────┬─────────┘
       │                                            │
       │ Step 1: Retrieve Tools                    │ Step 2: Execute
       ▼                                            ▼
┌──────────────────┐                    ┌─────────────────────┐
│  Tool Retriever  │                    │    MCP Servers      │
│   (ChromaDB)     │                    │  ┌───────────────┐  │
│  - Embeddings    │                    │  │  Utilitas     │  │
│  - Similarity    │                    │  │  - get_time   │  │
│    Search        │                    │  │  - calculator │  │
└──────────────────┘                    │  └───────────────┘  │
                                        │  ┌───────────────┐  │
                                        │  │  Akademik     │  │
                                        │  │  - get_dosen  │  │
                                        │  │  - get_matkul │  │
                                        │  └───────┬───────┘  │
                                        └──────────┼──────────┘
                                                   │
                                                   ▼
                                        ┌─────────────────────┐
                                        │   SQLite DB         │
                                        │   (kampus.db)       │
                                        └─────────────────────┘
```

### Workflow (Most Complex Scenario)
1. User asks: "Siapa dosen pembimbing Agus?"
2. Agent receives query
3. Agent → RAG: "Find tools matching 'dosen pembimbing'"
4. RAG → ChromaDB: Similarity search → Returns `get_dosen_pembimbing`
5. Agent decides to call `get_dosen_pembimbing(nama_mahasiswa="Agus")`
6. Agent → MCP Server Akademik: Execute tool
7. MCP Server → SQLite: Safe SQL query with JOIN
8. SQLite → MCP Server: Return "Dr. Budi Santoso"
9. MCP Server → Agent: Return result
10. Agent → User: "Dosen pembimbing Agus adalah Dr. Budi Santoso"

## 4. Project Structure

```
webinar_fundamental_agentic_ai/
├── environment.yml              # Conda environment spec
├── requirements.txt             # Python dependencies
├── .env                        # API keys (existing)
├── README.md                   # Main documentation
│
├── database/
│   ├── kampus.db               # SQLite database (generated)
│   ├── setup_database.py       # Database initialization
│   ├── schema.sql              # SQL schema
│   └── README.md
│
├── mcp_utilitas/
│   ├── server.py               # FastMCP server
│   ├── tools.py                # Tool implementations
│   ├── requirements.txt
│   └── README.md
│
├── mcp_akademik/
│   ├── server.py               # FastMCP server
│   ├── tools.py                # Tool implementations
│   ├── database.py             # DB connection
│   ├── requirements.txt
│   └── README.md
│
├── rag/
│   ├── tool_retriever.py       # ChromaDB + embeddings
│   ├── tool_descriptions.json  # Tool metadata
│   ├── chroma_db/              # ChromaDB storage (generated)
│   └── README.md
│
├── agent/
│   ├── orchestrator.py         # Main LangChain agent
│   ├── config.py               # Configuration
│   ├── requirements.txt
│   └── README.md
│
└── scripts/
    ├── run_all_servers.sh      # Launch all servers
    ├── test_demo_flow.py       # Test scenarios
    └── demo_interactive.py     # Interactive CLI
```

## 5. Database Schema (SQLite)

### Tables

**dosen**
- `id` INTEGER PRIMARY KEY
- `nama_dosen` TEXT
- `nidn` TEXT UNIQUE

**mahasiswa**
- `id` INTEGER PRIMARY KEY
- `nama_mahasiswa` TEXT
- `nim` TEXT UNIQUE
- `id_dospem` INTEGER (FK → dosen.id)

**mata_kuliah**
- `id` INTEGER PRIMARY KEY
- `nama_matkul` TEXT
- `sks` INTEGER

**transkrip**
- `id_mahasiswa` INTEGER (FK → mahasiswa.id)
- `id_matkul` INTEGER (FK → mata_kuliah.id)
- `nilai_huruf` TEXT

### Dummy Data
- **Dosen:** Dr. Budi Santoso, Prof. Siti Aminah
- **Mahasiswa:** Agus Setiawan (dospem: Dr. Budi), Rini Wijaya (dospem: Prof. Siti)
- **Mata Kuliah:** Kecerdasan Buatan, Basis Data Lanjut, Pemrograman Web
- **Transkrip:** Agus (AI: A, DB: B), Rini (AI: A, Web: A)

## 6. MCP Server Specifications

### MCP Server #1: Utilitas

**Port:** 3001
**Tools:**

1. `get_waktu_saat_ini()`
   - Description: "Get current date and time. No arguments required."
   - Returns: ISO 8601 formatted datetime string
   - Implementation: `datetime.now()`

2. `kalkulator_sederhana(ekspresi: str)`
   - Description: "Calculate simple math expressions like '2+2' or '5*10'. Takes string input."
   - Returns: Calculation result or error message
   - Implementation: Safe `eval()` with restricted builtins

### MCP Server #2: Akademik

**Port:** 3002
**Tools:**

1. `get_dosen_pembimbing(nama_mahasiswa: str)`
   - Description: "Find the academic advisor (dospem) of a student. Requires full student name."
   - SQL: `SELECT d.nama_dosen FROM mahasiswa m JOIN dosen d ON m.id_dospem = d.id WHERE m.nama_mahasiswa = ?`
   - Returns: Advisor name or "Student not found"

2. `get_mata_kuliah_mahasiswa(nama_mahasiswa: str)`
   - Description: "Get list of all courses taken by a student. Requires full student name."
   - SQL: `SELECT mk.nama_matkul, t.nilai_huruf FROM mahasiswa m JOIN transkrip t ON m.id = t.id_mahasiswa JOIN mata_kuliah mk ON t.id_matkul = mk.id WHERE m.nama_mahasiswa = ?`
   - Returns: List of courses with grades or "Student not found"

## 7. RAG-for-Tools Implementation

### Tool Descriptions (for Indexing)

**Format:** JSON array with metadata
```json
[
  {
    "name": "get_waktu_saat_ini",
    "description": "Use this tool to get the current date and time...",
    "category": "utility",
    "keywords": ["time", "date", "current", "now", "waktu", "tanggal"]
  },
  ...
]
```

### ChromaDB Setup
- **Collection:** `tool_descriptions`
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Persistence:** `rag/chroma_db/` directory
- **Retrieval:** Top 3 most similar tools by cosine similarity

### Integration with Agent
1. Agent receives user query
2. Query embedded using same model
3. ChromaDB returns top 3 relevant tools
4. Agent has access to only these 3 tools (not all 4)
5. Agent decides which tool to execute

## 8. Agent Orchestrator (LangChain)

### Components
- **LLM:** OpenAI GPT-4o-mini via `ChatOpenAI`
- **Agent Type:** `create_openai_functions_agent` (native function calling)
- **Tools:** Dynamically loaded from RAG retriever
- **Memory:** ConversationBufferMemory (for multi-turn demo)
- **Logging:** Verbose mode for educational visibility

### Configuration
```python
# agent/config.py
OPENAI_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0  # Deterministic for demo
MAX_ITERATIONS = 5
VERBOSE = True
```

### Execution Flow
```python
# Simplified pseudocode
query = user_input()
relevant_tools = rag_retriever.retrieve(query, top_k=3)
agent = create_agent(llm=openai, tools=relevant_tools)
response = agent.run(query)
print(response)
```

## 9. Demo Scenarios (Testing Checklist)

### Scenario 1: Simple Tool
- **Query:** "Jam berapa sekarang?"
- **Expected:** RAG finds `get_waktu_saat_ini`, agent executes, returns time
- **Purpose:** Demonstrate basic tool calling

### Scenario 2: Database Tool (Single)
- **Query:** "Siapa dosen pembimbing Rini Wijaya?"
- **Expected:** RAG finds `get_dosen_pembimbing` and `get_mata_kuliah_mahasiswa`, agent chooses correct one (`get_dosen_pembimbing`), returns "Prof. Siti Aminah"
- **Purpose:** Demonstrate RAG selection + database access

### Scenario 3: Database Tool (Multi-result)
- **Query:** "Mata kuliah apa saja yang diambil Agus Setiawan?"
- **Expected:** RAG finds tools, agent chooses `get_mata_kuliah_mahasiswa`, returns list with grades
- **Purpose:** Demonstrate complex SQL query results

### Scenario 4: Security Demo (CRITICAL)
- **Query:** "Ubah nilai Agus di mata kuliah AI menjadi C"
- **Expected:** Agent fails gracefully: "I don't have tools to modify grades"
- **Purpose:** **Prove MCP security** - Agent cannot write to database, only read

## 10. Implementation Timeline

### Day 1-2: Foundation (8-12 hours)
- [x] Setup conda environment
- [ ] Database: Schema + data + setup script
- [ ] MCP Utilitas: Server + 2 tools + tests
- [ ] MCP Akademik: Server + 2 tools + SQL + tests
- [ ] Integration test: Both servers running

### Day 3-4: Agent & RAG (8-12 hours)
- [ ] RAG: ChromaDB setup + tool indexing
- [ ] RAG: Retrieval logic + testing
- [ ] Agent: Basic LangChain setup (no RAG)
- [ ] Agent: Integrate RAG retriever
- [ ] Agent: 2-step workflow implementation
- [ ] Verbose logging for demo

### Day 5-6: Testing & Polish (6-10 hours)
- [ ] Test all 4 demo scenarios
- [ ] Error handling & edge cases
- [ ] Demo script creation
- [ ] Terminal setup & workflow testing
- [ ] Record backup demo video

### Day 7: Buffer & Documentation (4-6 hours)
- [ ] README for each component
- [ ] Main README with setup instructions
- [ ] Troubleshooting guide
- [ ] Presentation slides prep

## 11. Success Criteria

- ✅ All 4 demo scenarios work reliably
- ✅ Verbose logging clearly shows RAG → Tool Selection → Execution
- ✅ Security scenario properly demonstrates read-only constraint
- ✅ Code is clean, well-commented, and beginner-friendly
- ✅ Setup instructions tested on clean environment
- ✅ Demo runs smoothly without manual intervention

## 12. Educational Focus Points

For the 1-hour webinar, emphasize:

1. **MCP as Security Layer** (15 min)
   - Show diagram: Agent → MCP → Database
   - Contrast with: Agent → Direct SQL (dangerous!)
   - Demo Scenario 4 to prove read-only access

2. **RAG-for-Tools Concept** (15 min)
   - Explain: "What if we had 1000 tools?"
   - Show ChromaDB similarity search logs
   - Demonstrate how agent gets filtered toolset

3. **Agent Decision Making** (15 min)
   - Show verbose logs of agent "thinking"
   - Highlight: RAG returns 2 tools, agent picks correct one
   - Explain function calling vs traditional prompting

4. **Live Demo** (10 min)
   - Run all 4 scenarios live
   - Show terminal outputs side-by-side (agent + servers)

5. **Q&A** (5 min)

## 13. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LangChain version conflicts | Pin all versions in requirements.txt |
| ChromaDB embedding errors | Test embeddings separately first |
| MCP connection issues | Test servers standalone before integration |
| Demo fails live | Pre-record backup video, test run 5+ times |
| Student setup problems | Provide Docker fallback or detailed troubleshooting |

## 14. Future Enhancements (Post-Demo)

If students want to extend:
- Add more tools (e.g., `get_jadwal_kuliah`)
- Implement write tools with confirmation workflow
- Add Streamlit UI for non-technical demo
- Deploy MCP servers to cloud
- Add conversation memory persistence
- Implement tool usage analytics

---

**Next Steps:** Begin implementation following this design.
