# MCP Server: Akademik

Academic database access server demonstrating safe database integration through MCP protocol.

## Key Concept: Security Through MCP

**The AI agent NEVER directly accesses the database.**

Instead:
1. Agent calls MCP tools (this server)
2. Server executes pre-defined, safe SQL queries
3. Server returns results to agent
4. Agent cannot write SQL or modify data

This architecture prevents:
- SQL injection attacks
- Unauthorized data modification
- Accidental database corruption

## Tools Provided

### 1. `get_dosen_pembimbing(nama_mahasiswa: str)`
Find a student's academic advisor.

**SQL Query:** 2-table JOIN (mahasiswa ← dosen)

**Parameters:**
- `nama_mahasiswa` (str): Student's full name (case-sensitive)

**Returns:** Advisor name or error message

**Examples:**
```python
result = get_dosen_pembimbing("Agus Setiawan")
# Returns: "Dosen pembimbing Agus Setiawan: Dr. Budi Santoso"

result = get_dosen_pembimbing("Rini Wijaya")
# Returns: "Dosen pembimbing Rini Wijaya: Prof. Siti Aminah"
```

### 2. `get_mata_kuliah_mahasiswa(nama_mahasiswa: str)`
Get all courses taken by a student with grades.

**SQL Query:** 3-table JOIN (mahasiswa → transkrip → mata_kuliah)

**Parameters:**
- `nama_mahasiswa` (str): Student's full name (case-sensitive)

**Returns:** List of courses and grades, or error message

**Examples:**
```python
result = get_mata_kuliah_mahasiswa("Agus Setiawan")
# Returns: "Mata kuliah Agus Setiawan: Kecerdasan Buatan (A), Basis Data Lanjut (B)"

result = get_mata_kuliah_mahasiswa("Rini Wijaya")
# Returns: "Mata kuliah Rini Wijaya: Kecerdasan Buatan (A), Pemrograman Web (A)"
```

### 3. `list_all_students()`
Get list of all registered students.

**SQL Query:** Simple SELECT

**Parameters:** None

**Returns:** Comma-separated list of student names

**Example:**
```python
result = list_all_students()
# Returns: "Mahasiswa terdaftar: Agus Setiawan, Rini Wijaya"
```

## Database Connection

The `database.py` module provides:
- Safe connection management
- Parameterized query execution (prevents SQL injection)
- Error handling and logging
- Connection testing

**Example:**
```python
from database import get_db

db = get_db()
result = db.execute_query(
    "SELECT nama_dosen FROM dosen WHERE id = ?",
    (1,),
    fetch_one=True
)
```

## Security Features

### 1. Parameterized Queries
All queries use `?` placeholders and tuple binding:
```python
query = "SELECT * FROM mahasiswa WHERE nama_mahasiswa = ?"
result = db.execute_query(query, (nama_mahasiswa,))
```

**NOT:**
```python
# DANGEROUS - DO NOT DO THIS!
query = f"SELECT * FROM mahasiswa WHERE nama_mahasiswa = '{nama_mahasiswa}'"
```

### 2. Read-Only Access
All tools use `SELECT` queries only. No:
- `INSERT` (cannot add data)
- `UPDATE` (cannot modify data)
- `DELETE` (cannot remove data)
- `DROP` (cannot delete tables)

### 3. MCP Abstraction Layer
The AI agent:
- ✅ Can call `get_dosen_pembimbing("Agus")`
- ❌ Cannot write custom SQL queries
- ❌ Cannot see database schema directly
- ❌ Cannot access database credentials

## Running the Server

```bash
# Make sure database exists first
cd ../database
python setup_database.py

# Then start the server
cd ../mcp_akademik
python server.py
```

Output:
```
🔍 Testing database connection...
✅ Database connection successful!

🚀 Starting MCP Server: Akademik
Available tools:
  - get_dosen_pembimbing(nama_mahasiswa): Find student's advisor
  - get_mata_kuliah_mahasiswa(nama_mahasiswa): Get student's courses
  - list_all_students(): List all registered students

Database: /path/to/database/kampus.db

Server running...
```

### Transport Options

Just like the Utilitas server, this script accepts CLI flags so you can decide how it should listen:

```
python server.py \
  --transport sse \
  --host 127.0.0.1 \
  --port 8082
```

- `--transport stdio` (default) pairs nicely with `agent/orchestrator_proper_mcp.py`, which spawns the server as a subprocess.
- `--transport sse` exposes the tools over HTTP/SSE so remote clients (for example `agent/orchestrator_remote_mcp.py` or `scripts/run_remote_demo.sh`) can interact with it.

The automation script starts Utilitas on `8081` and Akademik on `8082`, so feel free to reuse those defaults or change the values and update `agent/mcp_servers.yaml`.

## Testing Tools

### Manual Testing
```python
from server import get_dosen_pembimbing, get_mata_kuliah_mahasiswa, list_all_students

# Test advisor lookup
print(get_dosen_pembimbing("Agus Setiawan"))
print(get_dosen_pembimbing("Rini Wijaya"))

# Test course lookup
print(get_mata_kuliah_mahasiswa("Agus Setiawan"))
print(get_mata_kuliah_mahasiswa("Rini Wijaya"))

# Test student list
print(list_all_students())

# Test error handling
print(get_dosen_pembimbing("Unknown Student"))
```

### Expected Results
```
Dosen pembimbing Agus Setiawan: Dr. Budi Santoso
Dosen pembimbing Rini Wijaya: Prof. Siti Aminah
Mata kuliah Agus Setiawan: Kecerdasan Buatan (A), Basis Data Lanjut (B)
Mata kuliah Rini Wijaya: Kecerdasan Buatan (A), Pemrograman Web (A)
Mahasiswa terdaftar: Agus Setiawan, Rini Wijaya
Mahasiswa 'Unknown Student' tidak ditemukan dalam database
```

## Demo Scenarios

### Scenario 1: Find Advisor (Success)
**User:** "Siapa dosen pembimbing Rini Wijaya?"
**Tool Call:** `get_dosen_pembimbing("Rini Wijaya")`
**Result:** "Dosen pembimbing Rini Wijaya: Prof. Siti Aminah"

### Scenario 2: Get Courses (Success)
**User:** "Mata kuliah apa saja yang diambil Agus Setiawan?"
**Tool Call:** `get_mata_kuliah_mahasiswa("Agus Setiawan")`
**Result:** "Mata kuliah Agus Setiawan: Kecerdasan Buatan (A), Basis Data Lanjut (B)"

### Scenario 3: Unauthorized Write (Fail - As Expected!)
**User:** "Ubah nilai Agus di mata kuliah AI menjadi C"
**Tool Call:** *Agent searches for write tools*
**Result:** "Maaf, saya tidak memiliki tool untuk mengubah nilai"

✅ **This proves MCP security works!** The agent cannot modify data.

## Educational Notes

This server demonstrates:
- **MCP as security layer** between AI and database
- **Parameterized queries** for SQL injection prevention
- **Read-only constraints** enforced by tool design
- **JOIN operations** for relational data retrieval
- **Error handling** for robust production code
- **Clear tool descriptions** for LLM understanding

Compare with traditional approach:
- ❌ AI generates SQL directly → SQL injection risk
- ❌ AI has full database access → data corruption risk
- ❌ No audit trail → compliance issues

With MCP:
- ✅ AI calls predefined tools → safe operations only
- ✅ All queries logged → full audit trail
- ✅ Read-only by design → data integrity guaranteed
