"""Helper script for using Advanced Consultation in Cursor.

This provides a simple command-line interface for running consultations
directly from Cursor without needing MCP server setup.
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main entry point for cursor helper."""
    parser = argparse.ArgumentParser(
        description="Advanced Consultation Helper for Cursor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture initial request (Stage 0)
  python cursor_helper.py capture "Database Decision" "Should I use PostgreSQL or MongoDB?"
  
  # Start consultation (Stage 1 - reads from Stage 0)
  python cursor_helper.py start 001_Database_Decision
  
  # Continue existing consultation (Stage 2)
  python cursor_helper.py continue 001_Database_Decision
  
  # Extract recommendations (Stage 3)
  python cursor_helper.py extract 001_Database_Decision
  
  # Run full consultation (all stages)
  python cursor_helper.py full "Database Decision" "Should I use PostgreSQL or MongoDB?"
  
  # List all consultations
  python cursor_helper.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Start command (Stage 1)
    start_parser = subparsers.add_parser('start', help='Start a new consultation (Stage 1)')
    start_parser.add_argument('name', help='Consultation name')
    start_parser.add_argument('question', help='Consultation question')
    start_parser.add_argument('--context', nargs='*', help='Context files (optional)')
    
    # Continue command (Stage 2)
    continue_parser = subparsers.add_parser('continue', help='Continue consultation (Stage 2)')
    continue_parser.add_argument('folder', help='Consultation folder name (e.g., 001_My_Consultation)')
    
    # Extract command (Stage 3)
    extract_parser = subparsers.add_parser('extract', help='Extract recommendations (Stage 3)')
    extract_parser.add_argument('folder', help='Consultation folder name (e.g., 001_My_Consultation)')
    
    # Full command (all stages)
    full_parser = subparsers.add_parser('full', help='Run full consultation (all stages)')
    full_parser.add_argument('name', help='Consultation name')
    full_parser.add_argument('question', help='Consultation question')
    full_parser.add_argument('--context', nargs='*', help='Context files (optional)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all consultations')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Get script directory
    script_dir = Path(__file__).parent
    
    if args.command == 'capture':
        # Run Stage 0
        import subprocess
        cmd = [
            sys.executable,
            str(script_dir / "00_Capture_Initial_Request.py"),
            "--consultation", args.name,
            "--request", args.request
        ]
        if args.context:
            cmd.extend(["--context"] + args.context)
        subprocess.run(cmd)
    
    elif args.command == 'start':
        # Run Stage 1 (reads from Stage 0)
        import subprocess
        cmd = [
            sys.executable,
            str(script_dir / "01_Understand_Context_Create_Prompt.py"),
            "--consultation-folder", args.folder
        ]
        subprocess.run(cmd)
    
    elif args.command == 'continue':
        # Run Stage 2
        import subprocess
        cmd = [
            sys.executable,
            str(script_dir / "02_Fetch_Gemini_Response.py"),
            "--consultation-folder", args.folder
        ]
        subprocess.run(cmd)
    
    elif args.command == 'extract':
        # Run Stage 3
        import subprocess
        cmd = [
            sys.executable,
            str(script_dir / "03_Extract_Detailed_Recommendations.py"),
            "--consultation-folder", args.folder
        ]
        subprocess.run(cmd)
    
    elif args.command == 'full':
        # Run full consultation
        import subprocess
        cmd = [
            sys.executable,
            str(script_dir / "run_full_consultation.py"),
            "--consultation", args.name,
            "--question", args.question
        ]
        if args.context:
            cmd.extend(["--context"] + args.context)
        subprocess.run(cmd)
    
    elif args.command == 'list':
        # List consultations
        consultations_dir = Path.cwd() / "Advanced_Consultations"
        if not consultations_dir.exists():
            print("No consultations found. Advanced_Consultations/ folder does not exist.")
            return
        
        folders = sorted([d for d in consultations_dir.iterdir() if d.is_dir()])
        if not folders:
            print("No consultations found.")
            return
        
        print(f"\n📋 Available Consultations ({len(folders)} total):\n")
        for folder in folders:
            print(f"  {folder.name}")
            # Check which stages are complete
            files = []
            if (folder / "01_Initial_User_System_Prompt.md").exists():
                files.append("Stage 1 ✅")
            if (folder / "03_Original_Raw_Output_from_Gemini3Pro.md").exists():
                files.append("Stage 2 ✅")
            if (folder / "04_Recommendations.md").exists():
                files.append("Stage 3 ✅")
            
            if files:
                print(f"    → {', '.join(files)}")
            print()


if __name__ == "__main__":
    main()

