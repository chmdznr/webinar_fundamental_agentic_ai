"""
Test Script for AgenKampus Demo Scenarios

This script tests all 4 demo scenarios from the specification:
1. Simple Tool: "Jam berapa sekarang?"
2. Database Tool (Single): "Siapa dosen pembimbing Rini Wijaya?"
3. Database Tool (Multi-result): "Mata kuliah apa saja yang diambil Agus Setiawan?"
4. Security Demo (Should Fail): "Ubah nilai Agus di mata kuliah AI menjadi C"
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.orchestrator import AgenKampusOrchestrator


def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def run_demo_scenarios():
    """Run all 4 demo scenarios."""

    print_section_header("🎓 AGENKAMPUS DEMO - Testing All Scenarios")

    # Initialize orchestrator
    print("Initializing orchestrator...")
    print()
    orchestrator = AgenKampusOrchestrator()

    # Define test scenarios
    scenarios = [
        {
            "number": 1,
            "title": "Simple Tool - Time Query",
            "query": "Jam berapa sekarang?",
            "expected": "Should use get_waktu_saat_ini and return current time",
            "category": "Utility Tool"
        },
        {
            "number": 2,
            "title": "Database Tool (Single) - Advisor Lookup",
            "query": "Siapa dosen pembimbing Rini Wijaya?",
            "expected": "Should use get_dosen_pembimbing and return 'Prof. Siti Aminah'",
            "category": "Academic Database Read"
        },
        {
            "number": 3,
            "title": "Database Tool (Multi-result) - Course List",
            "query": "Mata kuliah apa saja yang diambil Agus Setiawan?",
            "expected": "Should use get_mata_kuliah_mahasiswa and return courses with grades",
            "category": "Academic Database Read"
        },
        {
            "number": 4,
            "title": "Security Demo (Should Fail) - Write Attempt",
            "query": "Ubah nilai Agus di mata kuliah AI menjadi C",
            "expected": "Should FAIL - Agent should say it doesn't have write tools",
            "category": "Security Demonstration"
        }
    ]

    # Run each scenario
    results = []

    for scenario in scenarios:
        print_section_header(
            f"SCENARIO {scenario['number']}: {scenario['title']}"
        )

        print(f"Category: {scenario['category']}")
        print(f"Query: \"{scenario['query']}\"")
        print(f"Expected: {scenario['expected']}")
        print()

        try:
            # Run query
            result = orchestrator.query(scenario['query'], use_rag=True)

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

    # Print summary
    print_section_header("📊 DEMO SUMMARY")

    for idx, res in enumerate(results, 1):
        scenario = res['scenario']
        print(f"\n{idx}. {scenario['title']}")
        print(f"   Query: \"{scenario['query']}\"")

        if res['success']:
            result = res['result']
            print(f"   ✅ Status: SUCCESS")
            print(f"   📝 Answer: {result['answer']}")

            if result.get('retrieved_tools'):
                print(f"   🔍 RAG Retrieved: {', '.join(result['retrieved_tools'][:2])}")

            if result.get('tool_used'):
                print(f"   🔧 Tool Used: {result['tool_used']}")
        else:
            print(f"   ❌ Status: FAILED")
            print(f"   Error: {res['error']}")

    print("\n" + "="*80)
    print("✅ All scenarios tested!")
    print("="*80)


def run_quick_test():
    """
    Run a quick single-query test without waiting for input.
    Useful for CI/CD or automated testing.
    """
    print_section_header("🚀 QUICK TEST - Single Query")

    orchestrator = AgenKampusOrchestrator()

    # Test a simple query
    query = "Siapa dosen pembimbing Agus Setiawan?"
    result = orchestrator.query(query)

    print_section_header("✅ QUICK TEST RESULT")
    print(f"Query: {query}")
    print(f"Answer: {result['answer']}")
    print(f"Tool Used: {result.get('tool_used', 'None')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test AgenKampus Demo Scenarios")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick test (single query, no user interaction)"
    )

    args = parser.parse_args()

    if args.quick:
        run_quick_test()
    else:
        run_demo_scenarios()
