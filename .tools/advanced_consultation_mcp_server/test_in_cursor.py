"""Test Advanced Consultation in Cursor.

This script tests the Advanced Consultation integration directly in Cursor.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cursor_integration import AdvancedConsultation


def test_integration():
    """Test the Advanced Consultation integration."""
    print("="*60)
    print("TESTING ADVANCED CONSULTATION IN CURSOR")
    print("="*60)
    
    # Initialize
    consultation = AdvancedConsultation()
    
    # Test 1: List consultations
    print("\n📋 Test 1: List existing consultations")
    print("-" * 60)
    consultations = consultation.list_consultations()
    if consultations:
        print(f"Found {len(consultations)} consultation(s):")
        for folder in consultations:
            print(f"  - {folder}")
    else:
        print("No existing consultations found.")
    
    # Test 2: Start a test consultation
    print("\n🚀 Test 2: Start a test consultation")
    print("-" * 60)
    
    test_name = "Cursor Integration Test"
    test_question = "What are the key considerations when integrating an MCP server into a development workflow?"
    
    print(f"Consultation Name: {test_name}")
    print(f"Question: {test_question}")
    print("\n⏳ Starting Stage 1 (this may take 5-10 minutes)...")
    
    result = consultation.start_consultation(test_name, test_question)
    
    if result['success']:
        print(f"\n[SUCCESS] Stage 1 completed successfully!")
        consultation_folder = result['consultation_folder']
        if consultation_folder:
            print(f"[INFO] Consultation folder: {consultation_folder}")
            
            # Check if files were created
            consultations_dir = Path.cwd() / "Advanced_Consultations" / consultation_folder
            if consultations_dir.exists():
                print(f"\n[INFO] Files created:")
                files = [
                    "01_Initial_User_System_Prompt.md",
                    "02_Context_Files.md"
                ]
                for file in files:
                    file_path = consultations_dir / file
                    if file_path.exists():
                        print(f"  [OK] {file}")
                    else:
                        print(f"  [FAIL] {file} (not found)")
            
            print(f"\n[SUCCESS] Integration test PASSED!")
            print(f"\nNext steps:")
            print(f"  1. Review: Advanced_Consultations/{consultation_folder}/01_Initial_User_System_Prompt.md")
            print(f"  2. Optionally add context files to: Advanced_Consultations/{consultation_folder}/02_Context_Files.md")
            print(f"  3. Run Stage 2: consultation.fetch_response('{consultation_folder}')")
            
            return consultation_folder
        else:
            print("\n⚠️  Consultation started but folder name not found")
            print("\nOutput:")
            print(result.get('output', 'No output'))
            return None
    else:
        print(f"\n❌ Stage 1 failed!")
        if result.get('error'):
            print(f"Error: {result['error']}")
        if result.get('output'):
            print(f"\nOutput:")
            print(result['output'])
        return None


def test_quick_check():
    """Quick check to verify setup without running full consultation."""
    print("="*60)
    print("QUICK SETUP CHECK")
    print("="*60)
    
    # Check if scripts exist
    scripts_dir = Path(__file__).parent
    required_scripts = [
        "01_Understand_Context_Create_Prompt.py",
        "02_Fetch_Gemini_Response.py",
        "03_Extract_Detailed_Recommendations.py",
        "run_full_consultation.py"
    ]
    
    print("\n[CHECK] Checking scripts...")
    all_exist = True
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"  [OK] {script}")
        else:
            print(f"  [FAIL] {script} (not found)")
            all_exist = False
    
    # Check if dependencies are importable
    print("\n[CHECK] Checking dependencies...")
    try:
        import google.genai
        print("  [OK] google-genai")
    except ImportError:
        print("  [FAIL] google-genai (not installed)")
        print("     Install with: pip install google-genai")
        all_exist = False
    
    try:
        import tenacity
        print("  [OK] tenacity")
    except ImportError:
        print("  [FAIL] tenacity (not installed)")
        print("     Install with: pip install tenacity")
        all_exist = False
    
    # Check Advanced_Consultations directory
    consultations_dir = Path.cwd() / "Advanced_Consultations"
    if consultations_dir.exists():
        print(f"\n[INFO] Advanced_Consultations/ directory exists")
    else:
        print(f"\n[INFO] Advanced_Consultations/ directory will be created automatically")
    
    if all_exist:
        print("\n[SUCCESS] All checks passed! Ready to use.")
        return True
    else:
        print("\n[FAIL] Some checks failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Advanced Consultation in Cursor")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick setup check only (no API calls)"
    )
    parser.add_argument(
        "--skip-test",
        action="store_true",
        help="Skip the actual consultation test"
    )
    
    args = parser.parse_args()
    
    # Always run quick check first
    if not test_quick_check():
        print("\n[FAIL] Setup check failed. Please fix the issues before running tests.")
        sys.exit(1)
    
    if args.quick:
        print("\n[SUCCESS] Quick check complete!")
        sys.exit(0)
    
    if args.skip_test:
        print("\n[SUCCESS] Setup verified. Skipping consultation test.")
        sys.exit(0)
    
    # Run full test
    print("\n" + "="*60)
    response = input("\n[WARNING] This will start a real consultation (uses API credits). Continue? (y/N): ").strip().lower()
    
    if response != 'y':
        print("\n[SUCCESS] Test skipped. Setup verified and ready!")
        sys.exit(0)
    
    consultation_folder = test_integration()
    
    if consultation_folder:
        print("\n" + "="*60)
        print("[SUCCESS] INTEGRATION TEST SUCCESSFUL!")
        print("="*60)
        print(f"\nThe Advanced Consultation system is working correctly in Cursor!")
        print(f"\nYou can now use it directly:")
        print(f"  1. Import: from cursor_integration import AdvancedConsultation")
        print(f"  2. Use: consultation = AdvancedConsultation()")
        print(f"  3. Start: consultation.start_consultation('Name', 'Question')")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] TEST FAILED")
        print("="*60)
        print("\nPlease check the error messages above and try again.")
        sys.exit(1)

