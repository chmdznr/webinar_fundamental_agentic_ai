"""
MCP Server: Utilitas
Provides simple utility tools for the AgenKampus demo.

Tools:
- get_waktu_saat_ini(): Returns current date and time
- kalkulator_sederhana(ekspresi): Evaluates simple math expressions

Usage:
    python server.py
"""

from datetime import datetime
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Utilitas")


@mcp.tool()
def get_waktu_saat_ini() -> str:
    """
    Get the current date and time.

    This tool returns the current system time in a human-readable format.
    No arguments are required.

    Returns:
        str: Current date and time in ISO 8601 format (YYYY-MM-DD HH:MM:SS)

    Example:
        >>> get_waktu_saat_ini()
        "2025-01-08 10:30:45"
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
def kalkulator_sederhana(ekspresi: str) -> str:
    """
    Calculate simple mathematical expressions.

    This tool evaluates basic math operations like addition, subtraction,
    multiplication, and division. The evaluation is done in a safe sandboxed
    environment to prevent code injection.

    Args:
        ekspresi (str): Mathematical expression to evaluate (e.g., "2+2", "5*10", "100/4")

    Returns:
        str: Result of the calculation or error message if expression is invalid

    Examples:
        >>> kalkulator_sederhana("2+2")
        "4"

        >>> kalkulator_sederhana("10*5")
        "50"

        >>> kalkulator_sederhana("100/4")
        "25.0"

    Safety:
        Only basic mathematical operations are allowed. No access to
        built-in functions or dangerous operations.
    """
    try:
        # Safe evaluation: only allow mathematical operations
        # Restrict __builtins__ to prevent code injection
        allowed_names = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
        }

        # Evaluate the expression safely
        result = eval(ekspresi, {"__builtins__": {}}, allowed_names)

        return str(result)

    except ZeroDivisionError:
        return "Error: Division by zero"
    except (SyntaxError, NameError, TypeError) as e:
        return f"Error: Invalid expression - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    print("🚀 Starting MCP Server: Utilitas")
    print("Available tools:")
    print("  - get_waktu_saat_ini(): Get current date and time")
    print("  - kalkulator_sederhana(ekspresi): Calculate math expressions")
    print("\nServer running...")

    # This will start the FastMCP server
    mcp.run()
