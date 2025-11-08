"""
MCP Server: Utilitas
Provides simple utility tools for the AgenKampus demo.

Tools:
- get_waktu_saat_ini(): Returns current date and time
- kalkulator_sederhana(ekspresi): Evaluates simple math expressions

Usage:
    python server.py [--transport sse --host 127.0.0.1 --port 8081]
"""

import argparse
from datetime import datetime
# SSE transport helper dependencies are loaded lazily inside run_server()
from fastmcp import FastMCP

# Initialize FastMCP server (host/port overrides applied at runtime)
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


def parse_args():
    """Parse CLI options for transport/host/port."""
    parser = argparse.ArgumentParser(description="Run MCP Utilitas server.")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse"],
        help="Transport mechanism. Use 'sse' for remote HTTP/SSE servers.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind when using SSE.")
    parser.add_argument("--port", type=int, default=8081, help="Port to bind when using SSE.")
    return parser.parse_args()


def run_server(transport: str, host: str, port: int):
    """Run FastMCP server using either stdio or SSE transport."""
    if transport == "sse":
        from starlette.applications import Starlette
        from starlette.responses import Response
        from starlette.routing import Route, Mount
        from mcp.server.sse import SseServerTransport
        import uvicorn

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
                await mcp._mcp_server.run(
                    streams[0],
                    streams[1],
                    mcp._mcp_server.create_initialization_options(),
                )
            return Response()

        app = Starlette(
            debug=mcp.settings.debug,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=mcp.settings.log_level,
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    args = parse_args()

    print("🚀 Starting MCP Server: Utilitas")
    print("Available tools:")
    print("  - get_waktu_saat_ini(): Get current date and time")
    print("  - kalkulator_sederhana(ekspresi): Calculate math expressions")
    print(f"\nTransport: {args.transport.upper()}")

    run_server(args.transport, args.host, args.port)
