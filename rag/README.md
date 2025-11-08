# RAG-for-Tools: The Librarian Component

This directory implements **RAG-for-Tools** - using Retrieval-Augmented Generation to help the AI agent discover which tools to use.

## The Problem

Imagine you have 1,000 tools available to your AI agent:

❌ **Without RAG:**
- Agent sees ALL 1,000 tool descriptions in every request
- Token limit exceeded → Request fails
- Or: Costs $$$$ per query
- Or: Agent gets confused by too many options

✅ **With RAG:**
- User asks: "What time is it?"
- RAG searches 1,000 tools → Returns top 3: `get_time`, `get_datetime`, `check_clock`
- Agent only sees these 3 relevant tools → Fast, cheap, accurate decision
- Agent picks `get_time` and executes it

## Architecture

```
User Query: "Siapa dosen pembimbing Agus?"
       ↓
┌──────────────────────────────────────┐
│   Embed Query (HuggingFace model)    │
│   → Vector: [0.12, -0.34, 0.56, ...] │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│        ChromaDB Vector Search        │
│   Find tools with similar vectors    │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│         Retrieved Tools (Top 3)      │
│  1. get_dosen_pembimbing (0.87)      │
│  2. get_mata_kuliah_mahasiswa (0.45) │
│  3. list_all_students (0.32)         │
└──────────────┬───────────────────────┘
               ↓
         Agent receives only
       these 3 relevant tools
```

## Components

### 1. `tool_descriptions.json`
Metadata for all available tools:
- **name**: Tool identifier
- **server**: Which MCP server provides it
- **description**: What the tool does
- **category**: Tool classification
- **keywords**: Search terms (English + Indonesian)
- **parameters**: Expected inputs
- **examples**: Sample queries

**Example:**
```json
{
  "name": "get_dosen_pembimbing",
  "server": "Akademik",
  "description": "Find the academic advisor of a student...",
  "keywords": ["advisor", "dosen", "pembimbing", "dospem"],
  "examples": ["Who is the advisor of Agus?"]
}
```

### 2. `tool_retriever.py`
The RAG implementation:

**Key Components:**
- **SentenceTransformer**: Converts text to vectors (embeddings)
- **ChromaDB**: Vector database for semantic search
- **ToolRetriever**: Main class orchestrating retrieval

**Main Methods:**
- `retrieve(query, top_k=3)`: Find relevant tools for a query
- `_index_tools()`: Initialize vector database (one-time)
- `demo_retrieval()`: Test with example queries

### 3. `chroma_db/` (generated)
Persistent storage for ChromaDB:
- Tool embeddings (vectors)
- Metadata
- Indices for fast search

This directory is created on first run.

## How It Works

### Step 1: Indexing (One-Time Setup)

```python
# On first run:
retriever = ToolRetriever()

# 1. Load tool_descriptions.json
tools = load_json("tool_descriptions.json")

# 2. Create rich searchable text
for tool in tools:
    text = f"{tool['description']} {tool['keywords']} {tool['examples']}"

# 3. Generate embeddings
embeddings = SentenceTransformer.encode(texts)

# 4. Store in ChromaDB
chromadb.add(embeddings, metadata=tools)
```

### Step 2: Retrieval (Every Query)

```python
# User query
query = "Siapa dosen pembimbing Rini?"

# 1. Embed the query
query_vector = SentenceTransformer.encode(query)

# 2. Find similar tool vectors
results = chromadb.query(query_vector, top_k=3)

# 3. Return tool metadata
tools = [
    {"name": "get_dosen_pembimbing", "similarity": 0.87},
    {"name": "get_mata_kuliah_mahasiswa", "similarity": 0.45},
    {"name": "list_all_students", "similarity": 0.32}
]
```

### Step 3: Agent Uses Results

```python
# Agent receives only top 3 tools
# Agent decides: "get_dosen_pembimbing" is most relevant
# Agent calls: get_dosen_pembimbing("Rini Wijaya")
# Result: "Prof. Siti Aminah"
```

## Embedding Model

**Model:** `all-MiniLM-L6-v2` from HuggingFace

**Why this model?**
- ✅ **Fast:** 384-dimensional vectors (vs 1536 for OpenAI)
- ✅ **Free:** Runs 100% locally, no API calls
- ✅ **Good enough:** Semantic similarity accuracy > 80%
- ✅ **Small:** ~80MB model download
- ✅ **Multilingual-ish:** Works reasonably with Indonesian

**Alternatives:**
- `paraphrase-multilingual-MiniLM-L12-v2` - Better multilingual support
- `all-mpnet-base-v2` - Higher accuracy, slower
- OpenAI embeddings - Best accuracy, costs money

## Testing the RAG System

### Run the Demo

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
      Category: utility
      Description: Use this tool to get the current date and time...

   2. kalkulator_sederhana (Similarity: 0.124)
      Server: Utilitas
      Category: utility
      Description: Use this tool to calculate simple mathematical expressions...

📝 Query: "Who is the advisor of Agus Setiawan?"
--------------------------------------------------------------------------------

   1. get_dosen_pembimbing (Similarity: 0.891)
      Server: Akademik
      Category: academic
      Description: Use this tool to find the academic advisor (dosen pembimbing)...

   2. get_mata_kuliah_mahasiswa (Similarity: 0.456)
      Server: Akademik
      Category: academic
      Description: Use this tool to get the complete list of courses...
```

### Programmatic Usage

```python
from tool_retriever import ToolRetriever

# Initialize
retriever = ToolRetriever()

# Retrieve tools
tools = retriever.retrieve("What courses did Agus take?", top_k=3)

for tool in tools:
    print(f"{tool['name']}: {tool['similarity_score']:.3f}")
    # get_mata_kuliah_mahasiswa: 0.887
    # get_dosen_pembimbing: 0.423
    # list_all_students: 0.201
```

## Educational Notes

### Why RAG-for-Tools?

**Traditional Approach:**
```python
# Agent has ALL tools in context
tools = [tool1, tool2, ..., tool1000]
prompt = f"You have these tools: {tools}\nUser: {query}"
# Problem: 100,000+ tokens!
```

**RAG Approach:**
```python
# Agent has only RELEVANT tools
relevant = rag.retrieve(query, top_k=3)
prompt = f"You have these tools: {relevant}\nUser: {query}"
# Solution: 1,000 tokens ✓
```

### Similarity Scoring

**How are scores calculated?**

1. **Text → Vector:**
   - "get current time" → `[0.12, -0.34, 0.56, ..., 0.23]` (384 numbers)

2. **Cosine Similarity:**
   ```
   similarity = (query_vector · tool_vector) / (|query_vector| × |tool_vector|)
   ```
   Result: 0.0 (completely different) to 1.0 (identical)

3. **Threshold Filtering:**
   - Only return tools with similarity > 0.3 (configurable)

### Multilingual Support

The system handles both English and Indonesian:

**English Query:**
```python
retrieve("Who is the advisor?")
→ get_dosen_pembimbing (0.85)
```

**Indonesian Query:**
```python
retrieve("Siapa pembimbing akademik?")
→ get_dosen_pembimbing (0.83)
```

**Why it works:**
- Keywords include both languages
- Semantic embeddings capture meaning across languages
- Examples provide query variations

## Performance

**Indexing (One-Time):**
- 4 tools: ~2 seconds
- 100 tools: ~5 seconds
- 1,000 tools: ~30 seconds

**Retrieval (Per Query):**
- Query embedding: ~50ms
- ChromaDB search: ~10ms
- Total: ~60ms

**Scaling:**
- 10,000 tools: Still <100ms per query
- Disk usage: ~1MB per 1,000 tools

## Troubleshooting

### "Model not found" Error

First run downloads the model (~80MB):
```bash
# Manual download (if needed)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Poor Retrieval Results

Improve by:
1. Adding more keywords to `tool_descriptions.json`
2. Adding more example queries
3. Using a better embedding model
4. Tuning `score_threshold` parameter

### ChromaDB Errors

Reset the database:
```bash
rm -rf chroma_db/
python tool_retriever.py  # Re-index
```

## Next Steps

This RAG system will be integrated into the Agent Orchestrator:

```python
# In agent/orchestrator.py
from rag.tool_retriever import ToolRetriever

retriever = ToolRetriever()
query = user_input()

# Step 1: RAG retrieves relevant tools
relevant_tools = retriever.retrieve(query, top_k=3)

# Step 2: Agent decides which to use
agent = create_agent(llm, tools=relevant_tools)
result = agent.run(query)
```

This two-step workflow is the core of RAG-for-Tools! 🎯
