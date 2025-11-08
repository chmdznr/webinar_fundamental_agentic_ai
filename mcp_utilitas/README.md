# MCP Server: Utilitas

Simple utility tools server demonstrating basic MCP functionality.

## Tools Provided

### 1. `get_waktu_saat_ini()`
Returns the current system date and time.

**Parameters:** None

**Returns:** Current datetime in ISO 8601 format (YYYY-MM-DD HH:MM:SS)

**Example:**
```python
result = get_waktu_saat_ini()
# Returns: "2025-01-08 10:30:45"
```

### 2. `kalkulator_sederhana(ekspresi: str)`
Evaluates simple mathematical expressions safely.

**Parameters:**
- `ekspresi` (str): Math expression to calculate (e.g., "2+2", "5*10", "100/4")

**Returns:** Calculation result or error message

**Supported Operations:**
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Exponentiation: `**`
- Parentheses: `()`

**Allowed Functions:**
- `abs()`, `round()`, `min()`, `max()`, `pow()`

**Examples:**
```python
result = kalkulator_sederhana("2+2")
# Returns: "4"

result = kalkulator_sederhana("10*5")
# Returns: "50"

result = kalkulator_sederhana("100/4")
# Returns: "25.0"

result = kalkulator_sederhana("2**8")
# Returns: "256"
```

## Security

The calculator tool uses `eval()` in a sandboxed environment:
- `__builtins__` are restricted
- Only whitelisted functions are available
- No access to file system or network
- Prevents code injection attacks

## Running the Server

```bash
# From the mcp_utilitas directory
python server.py
```

The server will start and listen for MCP protocol connections.

### Transport Options

`server.py` accepts a few CLI flags so you can decide how the transport should run:

```
python server.py \
  --transport sse \
  --host 127.0.0.1 \
  --port 8081
```

- `--transport stdio` (default): used by `agent/orchestrator_proper_mcp.py`, the server runs as a stdio subprocess.
- `--transport sse`: starts an HTTP/SSE endpoint suitable for remote clients (e.g., `agent/orchestrator_remote_mcp.py` or the `scripts/run_remote_demo.sh` workflow). `--host` and `--port` let you choose the bind address.

The automation script `./scripts/run_remote_demo.sh` uses the SSE mode on ports `8081/8082` by default.

## Testing Tools

You can test the tools using the MCP inspector or by connecting an agent client.

### Manual Testing (Python)
```python
from server import get_waktu_saat_ini, kalkulator_sederhana

# Test time tool
print(get_waktu_saat_ini())

# Test calculator
print(kalkulator_sederhana("2+2"))
print(kalkulator_sederhana("100/4"))
```

## Educational Notes

This server demonstrates:
- **Tool declarations** with FastMCP decorators
- **Clear docstrings** for LLM understanding
- **Type hints** for parameter validation
- **Error handling** for robust execution
- **Security best practices** for eval() usage

These simple tools show the foundation of MCP tool creation before moving to more complex database operations.
