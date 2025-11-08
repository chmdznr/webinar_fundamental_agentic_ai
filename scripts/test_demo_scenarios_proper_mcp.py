"""
Test Script for AgenKampus Demo Scenarios - Proper MCP Implementation

This script tests all 4 demo scenarios using the PROPER MCP implementation
with real client/server communication via MCP protocol.

Scenarios:
1. Simple Tool: "Jam berapa sekarang?"
2. Database Tool (Single): "Siapa dosen pembimbing Rini Wijaya?"
3. Database Tool (Multi-result): "Mata kuliah apa saja yang diambil Agus Setiawan?"
4. Security Demo (Should Fail): "Ubah nilai Agus di mata kuliah AI menjadi C"
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.orchestrator_proper_mcp import ProperMCPOrchestrator


def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


async def run_demo_scenarios():
    """Run all 4 demo scenarios with proper MCP implementation."""

    print_section_header("🎓 AGENKAMPUS DEMO - Testing All Scenarios (Proper MCP)")

    # Initialize orchestrator
    print("Initializing orchestrator with MCP protocol...")
    print()
    orchestrator = ProperMCPOrchestrator()

    # Connect to MCP servers
    await orchestrator.connect_mcp_servers()

    # Define test scenarios
    scenarios = [
        {
            "number": 1,
            "title": "Simple Tool - Time Query",
            "query": "Jam berapa sekarang?",
            "expected": "Should use get_waktu_saat_ini via MCP protocol and return current time",
            "category": "Utility Tool (MCP)"
        },
        {
            "number": 2,
            "title": "Database Tool (Single) - Advisor Lookup",
            "query": "Siapa dosen pembimbing Rini Wijaya?",
            "expected": "Should use get_dosen_pembimbing via MCP protocol and return 'Prof. Siti Aminah'",
            "category": "Academic Database Read (MCP)"
        },
        {
            "number": 3,
            "title": "Database Tool (Multi-result) - Course List",
            "query": "Mata kuliah apa saja yang diambil Agus Setiawan?",
            "expected": "Should use get_mata_kuliah_mahasiswa via MCP protocol and return courses with grades",
            "category": "Academic Database Read (MCP)"
        },
        {
            "number": 4,
            "title": "Security Demo (Should Fail) - Write Attempt",
            "query": "Ubah nilai Agus di mata kuliah AI menjadi C",
            "expected": "Should FAIL - Agent should say it doesn't have write tools",
            "category": "Security Demonstration (MCP)"
        }
    ]

    # Run each scenario
    results = []

    try:
        for scenario in scenarios:
            print_section_header(
                f"SCENARIO {scenario['number']}: {scenario['title']}"
            )

            print(f"Category: {scenario['category']}")
            print(f"Query: \"{scenario['query']}\"")
            print(f"Expected: {scenario['expected']}")
            print()

            try:
                # Run query (async)
                result = await orchestrator.query(scenario['query'], use_rag=True)

                # Store results
                results.append({
                    "scenario": scenario,
                    "success": True,
                    "result": result
                })

            except Exception as e:
                print(f"\n❌ ERROR: {str(e)}\n")
                results.append({
                    "scenario": scenario,
                    "success": False,
                    "error": str(e)
                })

            # Wait before next scenario
            print("\n" + "-"*80)
            print("Press Enter to continue to next scenario...")
            input()

    finally:
        # Always disconnect from MCP servers
        await orchestrator.disconnect_mcp_servers()

    # Print summary
    print_section_header("📊 DEMO SUMMARY (Proper MCP)")

    for idx, res in enumerate(results, 1):
        scenario = res['scenario']
        print(f"\n{idx}. {scenario['title']}")
        print(f"   Query: \"{scenario['query']}\"")

        if res['success']:
            result = res['result']
            print(f"   ✅ Status: SUCCESS")
            print(f"   📝 Answer: {result['answer']}")

            if result.get('intermediate_steps'):
                print(f"   🔧 Tools Executed: {len(result['intermediate_steps'])} calls via MCP")
        else:
            print(f"   ❌ Status: FAILED")
            print(f"   Error: {res['error']}")

    print("\n" + "="*80)
    print("✅ All scenarios tested via proper MCP protocol!")
    print("="*80)


async def run_quick_test():
    """
    Run a quick single-query test without waiting for input.
    Useful for CI/CD or automated testing.
    """
    print_section_header("🚀 QUICK TEST - Single Query (Proper MCP)")

    orchestrator = ProperMCPOrchestrator()

    try:
        # Connect to MCP servers
        await orchestrator.connect_mcp_servers()

        # Test a simple query
        query = "Siapa dosen pembimbing Agus Setiawan?"
        result = await orchestrator.query(query)

        print_section_header("✅ QUICK TEST RESULT (Proper MCP)")
        print(f"Query: {query}")
        print(f"Answer: {result['answer']}")
        print(f"MCP Protocol: ✓ Used")

    finally:
        # Disconnect from MCP servers
        await orchestrator.disconnect_mcp_servers()


def main():
    """Main entry point with argument parsing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test AgenKampus Demo Scenarios with Proper MCP Implementation"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick test (single query, no user interaction)"
    )

    args = parser.parse_args()

    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher required for async support")
        sys.exit(1)

    # Run appropriate test mode
    if args.quick:
        asyncio.run(run_quick_test())
    else:
        asyncio.run(run_demo_scenarios())


if __name__ == "__main__":
    main()
