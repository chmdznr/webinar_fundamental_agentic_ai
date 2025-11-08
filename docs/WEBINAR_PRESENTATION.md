# Webinar: Fundamental Agentic AI
## Membangun AI Agent dengan MCP dan RAG-for-Tools

**Durasi:** 60 menit
**Target:** Pemula yang ingin memahami Agentic AI
**Project:** AgenKampus - Demo Sistem AI Agent untuk Data Akademik

---

## 📋 Agenda

1. **[00:00-05:00]** Pengenalan Konsep Agentic AI
2. **[05:00-15:00]** Database & MCP Servers
3. **[15:00-25:00]** RAG-for-Tools System
4. **[25:00-45:00]** Live Demo: Agent in Action
5. **[45:00-55:00]** Behind the Scenes
6. **[55:00-60:00]** Q&A

---

## 🎯 Learning Objectives

Setelah webinar ini, peserta akan:
- Memahami arsitektur Agentic AI (Agent, Tools, MCP, RAG)
- Mengerti mengapa MCP penting untuk keamanan
- Dapat membedakan AI yang "hanya chat" vs AI yang "bisa action"
- Memahami cara RAG membantu AI menemukan tools yang tepat
- Dapat membuild sistem Agentic AI sederhana

---

## [00:00-05:00] Pengenalan: Apa itu Agentic AI?

### 🎬 Opening

**Pertanyaan Pembuka:**
> "Siapa yang pernah pakai ChatGPT? Raise your hand!"
> "Tapi... apakah ChatGPT bisa langsung query database kalian? Bisa jalankan Python script? Bisa kirim email?"

**Jawaban:** TIDAK! ChatGPT hanya bisa "ngobrol". Dia tidak bisa "action".

**Agentic AI = AI yang bisa MENGAMBIL TINDAKAN (Action)**

### 📊 Slide: Architecture Diagram

**Tampilkan diagram:**
```
User: "Siapa dosen pembimbing Agus?"
       ↓
┌──────────────────────────────────────┐
│    Agent (Brain) - GPT-4o-mini       │
│  "Saya perlu tool get_dosen_pembimbing" │
└─────┬────────────────────────────┬───┘
      │                            │
 Step 1: RAG               Step 2: Execute
      ▼                            ▼
┌─────────────┐          ┌──────────────────┐
│  RAG System │          │   MCP Servers    │
│  Find Tools │          │  ┌────────────┐  │
└─────────────┘          │  │ Akademik   │  │
                         │  │ - SQL Query │  │
                         │  └─────┬──────┘  │
                         └────────┼─────────┘
                                  ▼
                         ┌──────────────────┐
                         │  kampus.db       │
                         │  (SQLite)        │
                         └──────────────────┘
```

### 🗣️ Talking Points

**4 Komponen Utama:**

1. **Agent (Otak)**
   - GPT-4o-mini dari OpenAI
   - Mengambil keputusan: "Tool mana yang harus dipakai?"
   - Reasoning & planning

2. **MCP (Security Bridge)**
   - Model Context Protocol
   - AI TIDAK pernah langsung akses database
   - AI hanya boleh panggil tools yang sudah didefinisikan
   - **Analogi:** AI seperti karyawan baru, MCP seperti aturan perusahaan

3. **Tools (Pekerja)**
   - Function konkret yang melakukan pekerjaan
   - Contoh: `get_waktu_saat_ini()`, `get_dosen_pembimbing()`
   - Tools ditulis oleh MANUSIA (bukan AI!)

4. **RAG-for-Tools (Pustakawan)**
   - Bayangkan punya 1000 tools
   - RAG cari yang relevan pakai semantic search
   - Agent hanya lihat 3-5 tools paling relevan

### ⚡ Key Message

> **"AI never touches database directly. Humans write the SQL, AI just decides WHEN to use it."**

**Ini adalah kunci keamanan MCP!**

---

## [05:00-15:00] Database & MCP Servers

### 🎬 Demo 1: Database Structure

**1. Buka DB Browser untuk SQLite**

```bash
# Show kampus.db
open database/kampus.db
```

**Tampilkan 4 tabel:**
- `dosen` - Data dosen (id, nama_dosen, nidn)
- `mahasiswa` - Data mahasiswa (id, nama, nim, id_dospem)
- `mata_kuliah` - Data matakuliah (id, nama_mk, kode_mk, sks)
- `transkrip` - Nilai mahasiswa (id, id_mhs, id_mk, nilai)

**Sample Query Manual:**
```sql
SELECT d.nama_dosen
FROM mahasiswa m
JOIN dosen d ON m.id_dospem = d.id
WHERE m.nama_mahasiswa = 'Agus Setiawan';
```

**Result:** `Dr. Budi Santoso`

### 🎬 Demo 2: MCP Server Code

**Buka file:** `mcp_akademik/server.py`

**Highlight Kode:**

```python
@mcp.tool()
def get_dosen_pembimbing(nama_mahasiswa: str) -> str:
    """
    Use this tool to find the academic advisor (dosen pembimbing)
    of a student.

    Args:
        nama_mahasiswa: Full name of the student

    Returns:
        Name of the academic advisor
    """
    query = """
        SELECT d.nama_dosen
        FROM mahasiswa m
        JOIN dosen d ON m.id_dospem = d.id
        WHERE m.nama_mahasiswa = ?
    """
    result = db.execute_query(query, (nama_mahasiswa,), fetch_one=True)
```

### 🗣️ Talking Points

**3 Hal Penting:**

1. **Docstring yang Jelas**
   - AI membaca docstring untuk memahami fungsi tool
   - Harus deskriptif: "Use this tool to..."
   - Jelaskan parameters dan return value

2. **Parameterized SQL** ⚠️
   ```python
   # ✅ AMAN - Parameterized
   cursor.execute("WHERE nama = ?", (nama_mahasiswa,))

   # ❌ BAHAYA - SQL Injection!
   cursor.execute(f"WHERE nama = '{nama_mahasiswa}'")
   ```

   **Mengapa berbahaya?**
   ```python
   nama_mahasiswa = "'; DROP TABLE mahasiswa; --"
   # Bisa hapus seluruh tabel!
   ```

3. **SQL Ditulis oleh MANUSIA**
   - AI tidak pernah generate SQL sendiri
   - AI hanya memanggil function yang sudah ada
   - Ini adalah **defense in depth**

### 🎬 Demo 3: MCP Utilitas

**Buka file:** `mcp_utilitas/server.py`

**Show simple tools:**

```python
@mcp.tool()
def get_waktu_saat_ini() -> str:
    """Get the current date and time in Jakarta timezone."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

**Emphasize:**
- Tool bisa apapun: waktu, kalkulator, API calls, dll
- MCP adalah **protokol standar** untuk definisi tools
- FastMCP membuat ini sangat mudah

### ⚡ Key Message

> **"SQL written by humans, not AI. This is security by design."**

---

## [15:00-25:00] RAG-for-Tools System

### 🎬 Demo 1: The Scaling Problem

**Tanya audience:**
> "Kalau kalian punya 1000 tools, apakah AI harus baca semua deskripsi 1000 tools setiap kali user bertanya?"

**Jawaban:** TIDAK! Itu akan:
- Melebihi token limit (context window)
- Lambat (banyak text yang diproses)
- Mahal (token = uang)
- AI bingung (information overload)

**Solusi:** RAG-for-Tools!

### 🎬 Demo 2: Run RAG Demo

**Terminal:**
```bash
cd rag
python tool_retriever.py
```

**Expected Output:**
```
🚀 Initializing ToolRetriever...
📚 Loading tool descriptions from tool_descriptions.json
   Loaded 4 tools
🤖 Loading embedding model: all-MiniLM-L6-v2
   ✓ Embedding model ready (dimension: 384)
💾 Initializing ChromaDB at chroma_db
📝 Indexing tools (first run)...
   Generating embeddings...
   Adding to ChromaDB...
   ✓ Indexed 4 tools successfully

================================================================================
🔍 RAG TOOL RETRIEVAL DEMO
================================================================================

📝 Query: "What time is it now?"
--------------------------------------------------------------------------------

   1. get_waktu_saat_ini (Similarity: 0.823)
      Server: Utilitas
      Description: Use this tool to get the current date and time...

   2. kalkulator_sederhana (Similarity: 0.124)
      Server: Utilitas
      Description: Use this tool to calculate...
```

### 🗣️ Talking Points

**Cara Kerja RAG:**

1. **Indexing (Setup Awal):**
   ```python
   # Load tool descriptions
   tools = load_json("tool_descriptions.json")

   # Convert to embeddings (vectors)
   text = "Get current date and time Jakarta timezone..."
   embedding = model.encode(text)
   # Result: [0.12, -0.34, 0.56, ..., 0.23]  (384 numbers)

   # Store in ChromaDB
   chromadb.add(embeddings, metadata=tools)
   ```

2. **Retrieval (Setiap Query):**
   ```python
   # User query
   query = "Jam berapa sekarang?"

   # Convert query to embedding
   query_embedding = model.encode(query)

   # Find similar tools using cosine similarity
   results = chromadb.query(query_embedding, top_k=3)

   # Return: get_waktu_saat_ini (score: 0.82)
   ```

3. **Similarity Score:**
   - 0.0 = Completely different
   - 1.0 = Identical
   - Threshold biasanya > 0.3

### 🎬 Demo 3: Bilingual Search

**Show tool_descriptions.json:**

```json
{
  "name": "get_dosen_pembimbing",
  "keywords": [
    "advisor", "supervisor", "dosen", "pembimbing", "dospem",
    "academic", "thesis", "skripsi"
  ],
  "examples": [
    "Who is the advisor of Agus?",
    "Siapa dosen pembimbing Agus?",
    "Find thesis supervisor for student"
  ]
}
```

**Explain:**
- Keywords include English + Indonesian
- Examples show different ways to ask
- Semantic search works across languages

**Live test:**
```
Query: "Who is the advisor?"        → get_dosen_pembimbing (0.85)
Query: "Siapa pembimbing akademik?" → get_dosen_pembimbing (0.83)
```

### ⚡ Key Message

> **"RAG scales to 1000+ tools. Agent only sees top 3 relevant tools."**

**Performance:**
- 4 tools: ~60ms per query
- 1000 tools: Still ~60ms per query ✅
- Cost: Embedding model runs locally (FREE!)

---

## [25:00-45:00] Live Agent Demo

### 🎬 Setup

**Terminal:**
```bash
cd agent
python orchestrator.py
```

**Show startup logs:**
```
🚀 AgenKampus Agent Orchestrator
================================

Configuration:
- Model: gpt-4o-mini
- Temperature: 0.0 (deterministic)
- RAG Top-K: 3 tools
- Verbose: True

✓ RAG System initialized
✓ MCP Tools loaded: 5 tools
  - get_waktu_saat_ini
  - kalkulator_sederhana
  - get_dosen_pembimbing
  - get_mata_kuliah_mahasiswa
  - list_all_students

Ready for queries!
```

### 🎬 Demo Scenario 1: Time Query (Simple)

**Input:**
```
👤 You: Jam berapa sekarang?
```

**Show verbose logs:**
```
🔍 RAG Retrieval:
   1. get_waktu_saat_ini (0.89)
   2. kalkulator_sederhana (0.12)
   3. list_all_students (0.08)

🤖 Agent Decision:
   Selected tool: get_waktu_saat_ini
   Reasoning: User asking for current time

🛠️ Tool Execution:
   Calling: get_waktu_saat_ini()
   Result: "2025-01-08 15:45:23"

🤖 Agent: Waktu saat ini adalah 2025-01-08 15:45:23
```

**Explain:**
- RAG found correct tool (similarity 0.89)
- Agent decided to use it
- Tool executed and returned result
- Agent formatted response in Indonesian

### 🎬 Demo Scenario 2: Advisor Query (Database)

**Input:**
```
👤 You: Siapa dosen pembimbing Agus Setiawan?
```

**Show verbose logs:**
```
🔍 RAG Retrieval:
   1. get_dosen_pembimbing (0.91)
   2. get_mata_kuliah_mahasiswa (0.45)
   3. list_all_students (0.32)

🤖 Agent Decision:
   Selected tool: get_dosen_pembimbing
   Parameters: {"nama_mahasiswa": "Agus Setiawan"}

🛠️ Tool Execution:
   Calling: get_dosen_pembimbing("Agus Setiawan")
   SQL Query: SELECT d.nama_dosen FROM mahasiswa m JOIN dosen d...
   Result: "Dr. Budi Santoso"

🤖 Agent: Dosen pembimbing Agus Setiawan adalah Dr. Budi Santoso
```

**Highlight:**
- Agent extracted "Agus Setiawan" from query
- Passed as parameter to tool
- Tool ran safe SQL query
- Agent got result and formatted answer

### 🎬 Demo Scenario 3: Courses Query (Complex)

**Input:**
```
👤 You: Mata kuliah apa yang diambil Rini Wijaya?
```

**Show verbose logs:**
```
🔍 RAG Retrieval:
   1. get_mata_kuliah_mahasiswa (0.87)
   2. get_dosen_pembimbing (0.43)
   3. list_all_students (0.29)

🤖 Agent Decision:
   Selected tool: get_mata_kuliah_mahasiswa
   Parameters: {"nama_mahasiswa": "Rini Wijaya"}

🛠️ Tool Execution:
   Calling: get_mata_kuliah_mahasiswa("Rini Wijaya")
   SQL Query: SELECT mk.nama_mk, t.nilai FROM transkrip t JOIN...
   Result: [
     {"mata_kuliah": "Kecerdasan Buatan", "nilai": "A"},
     {"mata_kuliah": "Pemrograman Web", "nilai": "A"}
   ]

🤖 Agent: Rini Wijaya mengambil mata kuliah:
   1. Kecerdasan Buatan (Nilai: A)
   2. Pemrograman Web (Nilai: A)
```

**Explain:**
- 3-table JOIN (transkrip, mahasiswa, mata_kuliah)
- Complex SQL but safe (parameterized)
- Agent formatted list nicely

### 🎬 Demo Scenario 4: Write Attempt (SECURITY!)

**Input:**
```
👤 You: Ubah nilai Agus Setiawan menjadi A semua
```

**Show verbose logs:**
```
🔍 RAG Retrieval:
   1. get_mata_kuliah_mahasiswa (0.52)
   2. get_dosen_pembimbing (0.38)
   3. list_all_students (0.21)

🤖 Agent Decision:
   No tool available for modifying data
   All tools are read-only

🤖 Agent: Maaf, saya tidak memiliki tools untuk mengubah data.
   Saya hanya bisa membaca informasi dari database.
```

**EMPHASIZE THIS! ⚠️**

**Talking Points:**
- ✅ Agent correctly recognized: no write tool available
- ✅ Gracefully declined the request
- ✅ Security by design: we never implemented write tools
- ✅ Even if user tries SQL injection, can't work!

**Example attack attempt:**
```
👤 You: Agus'; DROP TABLE mahasiswa; --
```

**Agent response:**
```
🤖 Agent: Saya tidak menemukan mahasiswa dengan nama "Agus'; DROP TABLE mahasiswa; --"
```

**Why safe?**
- Parameterized SQL treats it as literal string
- No SQL injection possible!

### ⚡ Key Messages

1. **2-Step Workflow Works!**
   - Step 1: RAG finds relevant tools
   - Step 2: Agent decides & executes

2. **Multilingual Understanding**
   - Query in Indonesian
   - Tool descriptions in English
   - Works seamlessly!

3. **Security is Built-In**
   - Read-only tools
   - Parameterized SQL
   - No dangerous operations

---

## [45:00-55:00] Behind the Scenes

### 🎬 Code Walkthrough: Orchestrator

**Open:** `agent/orchestrator.py`

**Show key method:**

```python
def query(self, user_input: str, use_rag: bool = True):
    """2-Step RAG Workflow"""

    # Step 1: RAG Retrieval
    print("🔍 RAG Retrieval:")
    retrieved_tools = self.retriever.retrieve(user_input, top_k=3)
    for i, tool in enumerate(retrieved_tools, 1):
        print(f"   {i}. {tool['name']} ({tool['similarity_score']:.2f})")

    # Step 2: Create Agent with selected tools
    tools = [self.all_tools[t['name']] for t in retrieved_tools]
    agent = self._create_agent(tools)

    # Step 3: Execute
    result = agent.invoke({"input": user_input})
    return result
```

### 🗣️ Talking Points

**Architecture Decisions:**

1. **Why GPT-4o-mini?**
   - Fast (~500-1000ms)
   - Cheap (~$0.0002 per query)
   - Good enough for tool selection
   - Alternative: GPT-4o (better but 10x more expensive)

2. **Why Temperature = 0?**
   - Deterministic responses
   - Same query → same answer
   - Good for production systems
   - Temperature > 0 for creative tasks

3. **Why Top-K = 3?**
   - Balance: enough options vs context size
   - Too few (K=1): might miss correct tool
   - Too many (K=10): information overload
   - Sweet spot: K=3-5

4. **Why LangChain?**
   - Battle-tested agent framework
   - Handles tool calling (OpenAI function calling)
   - Error handling built-in
   - Alternative: Custom loop (more control, more work)

### 🎬 Show: Cost Analysis

**Slide: Performance Metrics**

```
Typical Query Performance:
┌─────────────────────────┬──────────┬────────┐
│ Component               │ Time     │ Cost   │
├─────────────────────────┼──────────┼────────┤
│ RAG Retrieval           │ ~60ms    │ $0     │
│ LLM Decision (GPT-4o-m) │ ~800ms   │ $0.0002│
│ Tool Execution          │ ~10ms    │ $0     │
├─────────────────────────┼──────────┼────────┤
│ Total per Query         │ ~870ms   │ $0.0002│
└─────────────────────────┴──────────┴────────┘

1000 queries = ~$0.20
```

**Emphasize:**
- Very cheap for educational use
- RAG runs locally (FREE!)
- Only LLM calls cost money

### 🎬 Show: Scalability

**Slide: How it Scales**

```
Number of Tools vs Performance:
┌────────────┬──────────────┬──────────┐
│ Tools      │ RAG Time     │ Cost     │
├────────────┼──────────────┼──────────┤
│ 10 tools   │ ~60ms        │ Same     │
│ 100 tools  │ ~60ms        │ Same     │
│ 1000 tools │ ~80ms        │ Same     │
└────────────┴──────────────┴──────────┘
```

**Why constant time?**
- Vector search is O(log n) with indexing
- ChromaDB uses HNSW algorithm
- Agent always sees same number of tools (top-K)

### ⚡ Key Message

> **"This architecture scales. Add 1000 tools, performance stays the same."**

---

## [55:00-60:00] Q&A & Next Steps

### 🎬 Common Questions (Prepare Answers)

**Q1: Bisakah pakai LLM lokal seperti Llama?**
- ✅ Bisa! Change OpenAI → Ollama/LMStudio
- Perlu tuning: local models kurang bagus di tool calling
- Tradeoff: FREE tapi accuracy turun

**Q2: Bagaimana handle errors?**
- Try-catch di tool execution
- Return error message ke agent
- Agent decide: retry atau inform user
- Example in `mcp_akademik/database.py`

**Q3: Bisa untuk production?**
- ⚠️ Ini demo, bukan production-ready
- Perlu tambah: authentication, rate limiting, logging, monitoring
- Database: SQLite → PostgreSQL
- Caching layer untuk speed

**Q4: Bagaimana tambah tools baru?**
1. Tambah function di MCP server
2. Update `tool_descriptions.json`
3. Re-run `tool_retriever.py` (re-index)
4. Done!

**Q5: Apakah aman untuk sensitive data?**
- ⚠️ LLM calls keluar ke OpenAI
- Data mahasiswa dikirim ke API
- Untuk production: self-hosted LLM atau Azure OpenAI (data residency)
- Atau: anonymize data before sending

### 🎬 Next Steps for Students

**Slide: What to Try Next**

**Level 1: Modify Existing**
```python
# Add new tool
@mcp.tool()
def calculate_gpa(nama_mahasiswa: str) -> float:
    """Calculate student's GPA"""
    # Your implementation here
```

**Level 2: Add Features**
- Tool untuk jadwal kuliah
- Tool untuk cek ruangan kosong
- Tool untuk search mahasiswa by criteria

**Level 3: Build New System**
- E-commerce agent (product search, price check)
- Email assistant (read, summarize, draft replies)
- Code review agent (analyze PR, suggest improvements)

**Level 4: Production Hardening**
- Add authentication
- Implement rate limiting
- Add usage analytics
- Deploy to cloud

### 🎬 Resources

**Slide: Learn More**

**Documentation:**
- LangChain: https://python.langchain.com/
- MCP Protocol: https://modelcontextprotocol.io/
- ChromaDB: https://docs.trychroma.com/
- FastMCP: https://github.com/jlowin/fastmcp

**Repositories:**
- This project: https://github.com/chmdznr/webinar_fundamental_agentic_ai
- Clone and experiment!

**Community:**
- LangChain Discord
- MCP Discord
- Reddit: r/LangChain

### 🎬 Closing

**Final Slide: Key Takeaways**

1. **Agentic AI = AI that takes ACTION**
   - Not just chat, but real work

2. **MCP = Security by Design**
   - AI never touches database directly
   - Humans define safe tools

3. **RAG = Scalability**
   - Find relevant tools from thousands
   - Constant time performance

4. **2-Step Workflow Works**
   - RAG → Find tools
   - Agent → Decide & execute

5. **You Can Build This!**
   - Clone the repo
   - Follow README
   - Experiment & learn

**Thank you!**

---

## 📝 Presenter Notes

### Setup Checklist (Before Webinar)

**30 Minutes Before:**
- [ ] Test internet connection
- [ ] Open all terminals/windows needed
- [ ] Run `conda activate agenkampus`
- [ ] Test database: `python database/setup_database.py`
- [ ] Test RAG: `python rag/tool_retriever.py`
- [ ] Test agent: `python scripts/test_demo_scenarios.py --quick`
- [ ] Open DB Browser with kampus.db
- [ ] Open VS Code with key files
- [ ] Check microphone & screen sharing

**Backup Plans:**
- Have recorded demos ready (in case live demo fails)
- Print key code snippets
- Have architecture diagram as image (in case drawing fails)

### Timing Tips

- **Stay on schedule!** Use timer
- If running late: Skip "Behind the Scenes" section
- Priority: Live demo > Code walkthrough > Theory
- Save 5-10 minutes for Q&A (most valuable!)

### Engagement Tips

- **Ask questions** to keep audience engaged
- "Who has used ChatGPT?" → raises hands
- "Guess the similarity score!" → interaction
- Pause after key points for questions

### Common Demo Failures & Recovery

**If database not found:**
```bash
cd database && python setup_database.py
```

**If RAG not indexed:**
```bash
cd rag && rm -rf chroma_db && python tool_retriever.py
```

**If agent errors:**
- Check .env has OPENAI_API_KEY
- Check OpenAI API has credits
- Fall back to recorded demo

### Pro Tips

1. **Explain WHILE coding/demoing** (not after)
2. **Use analogies**: MCP = company rules, RAG = librarian
3. **Contrast with examples**: Safe vs dangerous code
4. **Show, don't just tell**: Live demos beat slides
5. **Relate to their experience**: "Like using npm install"

Good luck! 🚀
