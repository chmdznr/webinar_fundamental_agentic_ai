"""
Automation helper to exercise the remote MCP orchestrator.

This script loads `agent/orchestrator_remote_mcp.py`, runs a handful of demo
queries, and prints the outcomes—useful for smoke-testing when MCP servers run
on remote ports/hosts defined in `agent/mcp_servers.yaml`.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List

# Ensure project root is on sys.path (script resides in scripts/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.orchestrator_remote_mcp import RemoteMCPOrchestrator

DEFAULT_QUERIES = [
    "Jam berapa sekarang?",
    "Siapa dosen pembimbing Rini Wijaya?",
    "Mata kuliah apa saja yang diambil Agus Setiawan?",
    "Ubah nilai Agus di mata kuliah AI menjadi C",
]


async def run_queries(queries: List[str], use_rag: bool = True):
    orchestrator = RemoteMCPOrchestrator()

    try:
        for idx, query in enumerate(queries, 1):
            print(f"\n=== Scenario {idx}: {query} ===")
            result = await orchestrator.query(query, use_rag=use_rag)
            if result["success"]:
                # print(f"Result: {result['answer']}\n")
                continue
            else:
                print(f"Error: {result['error']}\n")
    finally:
        await orchestrator.disconnect_mcp_servers()


def main():
    parser = argparse.ArgumentParser(
        description="Test AgenKampus remote MCP orchestrator with predefined queries."
    )
    parser.add_argument(
        "--no-rag",
        action="store_true",
        help="Disable RAG filtering (use all registered tools).",
    )
    parser.add_argument(
        "--query",
        action="append",
        help="Custom query to run (can be specified multiple times).",
    )

    args = parser.parse_args()
    queries = args.query if args.query else DEFAULT_QUERIES

    asyncio.run(run_queries(queries, use_rag=not args.no_rag))


if __name__ == "__main__":
    main()
