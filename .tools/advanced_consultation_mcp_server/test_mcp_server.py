"""Test script for Advanced Consultation MCP Server.

This script tests the MCP server tools directly without needing Claude Desktop.
"""

import asyncio
import sys
from pathlib import Path

# Add mcp_server to path
sys.path.insert(0, str(Path(__file__).parent / "mcp_server"))

from advanced_consultation_mcp.server import (
    _handle_start_consultation,
    _handle_fetch_response,
    _handle_extract_recommendations,
    _handle_list_consultations,
    get_project_root,
    set_project_root
)


async def test_list_consultations():
    """Test list_consultations tool."""
    print("\n" + "="*60)
    print("TEST 1: List Consultations")
    print("="*60)
    
    result = await _handle_list_consultations({})
    print(result[0].text)
    return True


async def test_start_consultation():
    """Test start_advanced_consultation tool."""
    print("\n" + "="*60)
    print("TEST 2: Start Advanced Consultation")
    print("="*60)
    
    args = {
        "consultation_name": "MCP Server Test",
        "question": "What are the key considerations when building an MCP server?",
        "context_files": []
    }
    
    print(f"Starting consultation: {args['consultation_name']}")
    print(f"Question: {args['question']}")
    
    result = await _handle_start_consultation(args)
    print(result[0].text)
    
    # Extract consultation folder from result
    consultation_folder = None
    for line in result[0].text.split("\n"):
        if "**Folder:**" in line:
            parts = line.split()
            for part in parts:
                if part.startswith("001_") or part.startswith("002_") or part.startswith("003_"):
                    consultation_folder = part
                    break
    
    if consultation_folder:
        print(f"\n✅ Consultation folder created: {consultation_folder}")
        return consultation_folder
    else:
        print("\n⚠️  Could not extract consultation folder from result")
        return None


async def test_fetch_response(consultation_folder: str):
    """Test fetch_consultation_response tool."""
    if not consultation_folder:
        print("\n⚠️  Skipping Stage 2 test - no consultation folder")
        return None
    
    print("\n" + "="*60)
    print("TEST 3: Fetch Consultation Response")
    print("="*60)
    print(f"Using consultation folder: {consultation_folder}")
    print("\n⏳ This may take 10-15 minutes...")
    
    args = {
        "consultation_folder": consultation_folder
    }
    
    result = await _handle_fetch_response(args)
    print(result[0].text)
    
    if "✅" in result[0].text:
        print(f"\n✅ Stage 2 completed successfully")
        return consultation_folder
    else:
        print(f"\n❌ Stage 2 failed")
        return None


async def test_extract_recommendations(consultation_folder: str):
    """Test extract_consultation_recommendations tool."""
    if not consultation_folder:
        print("\n⚠️  Skipping Stage 3 test - no consultation folder")
        return
    
    print("\n" + "="*60)
    print("TEST 4: Extract Recommendations")
    print("="*60)
    print(f"Using consultation folder: {consultation_folder}")
    print("\n⏳ This may take 5-10 minutes...")
    
    args = {
        "consultation_folder": consultation_folder
    }
    
    result = await _handle_extract_recommendations(args)
    print(result[0].text)
    
    if "✅" in result[0].text:
        print(f"\n✅ Stage 3 completed successfully")
    else:
        print(f"\n❌ Stage 3 failed")


async def main():
    """Run all tests."""
    print("="*60)
    print("ADVANCED CONSULTATION MCP SERVER - TEST SUITE")
    print("="*60)
    
    # Set project root
    project_root = Path.cwd()
    set_project_root(project_root)
    print(f"\nProject Root: {project_root}")
    
    # Test 1: List consultations
    try:
        await test_list_consultations()
    except Exception as e:
        print(f"\n❌ Test 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Start consultation
    consultation_folder = None
    try:
        consultation_folder = await test_start_consultation()
    except Exception as e:
        print(f"\n❌ Test 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Ask user if they want to continue with Stages 2 and 3
    # (These take a long time and use API credits)
    print("\n" + "="*60)
    print("⚠️  NOTE: Stages 2 and 3 require Gemini 3 Pro API calls")
    print("   These can take 15-25 minutes total and consume API credits.")
    print("="*60)
    
    response = input("\nContinue with Stages 2 and 3? (y/N): ").strip().lower()
    
    if response != 'y':
        print("\n✅ Tests complete (Stages 2 and 3 skipped)")
        print(f"\nYou can manually test Stages 2 and 3 later using:")
        print(f"  python 02_Fetch_Gemini_Response.py --consultation-folder \"{consultation_folder}\"")
        print(f"  python 03_Extract_Detailed_Recommendations.py --consultation-folder \"{consultation_folder}\"")
        return
    
    # Test 3: Fetch response
    try:
        consultation_folder = await test_fetch_response(consultation_folder)
    except Exception as e:
        print(f"\n❌ Test 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 4: Extract recommendations
    try:
        await test_extract_recommendations(consultation_folder)
    except Exception as e:
        print(f"\n❌ Test 4 failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETE")
    print("="*60)
    print(f"\nConsultation folder: {consultation_folder}")
    print(f"Files available in: Advanced_Consultations/{consultation_folder}/")
    print("\nYou can now test the MCP server with Claude Desktop!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

