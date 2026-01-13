"""Cursor Integration for Advanced Consultation MCP Server.

This module provides easy access to Advanced Consultation tools from Cursor.
You can import this and use it directly, or use it as a CLI tool.
"""

import sys
from pathlib import Path
from typing import Optional, List
import subprocess


class AdvancedConsultation:
    """Simple interface for Advanced Consultation in Cursor."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize with project root.
        
        Args:
            project_root: Project root directory (default: current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.scripts_dir = Path(__file__).parent
        
    def capture_initial_request(
        self,
        consultation_name: str,
        request: str,
        context_files: Optional[List[str]] = None
    ) -> dict:
        """Capture initial request (Stage 0).
        
        Args:
            consultation_name: Name of the consultation
            request: Initial consultation request/question
            context_files: Optional list of context file paths
            
        Returns:
            Dictionary with status and consultation folder name
        """
        script = self.scripts_dir / "00_Capture_Initial_Request.py"
        args = [
            sys.executable,
            str(script),
            "--consultation", consultation_name,
            "--request", request,
            "--root", str(self.project_root)
        ]
        
        if context_files:
            args.extend(["--context"] + context_files)
        
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=60  # 1 minute timeout
            )
            
            # Extract consultation folder from output
            consultation_folder = None
            for line in result.stdout.split("\n"):
                if "001_" in line or "002_" in line or "003_" in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith("001_") or part.startswith("002_") or part.startswith("003_"):
                            consultation_folder = part
                            break
                    if consultation_folder:
                        break
            
            if not consultation_folder:
                # Try to find the most recent folder
                consultations_dir = self.project_root / "Advanced_Consultations"
                if consultations_dir.exists():
                    folders = sorted([d.name for d in consultations_dir.iterdir() if d.is_dir()], reverse=True)
                    if folders:
                        consultation_folder = folders[0]
            
            return {
                "success": result.returncode == 0,
                "consultation_folder": consultation_folder,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "consultation_folder": None,
                "output": None,
                "error": "Stage 0 timed out after 1 minute"
            }
        except Exception as e:
            return {
                "success": False,
                "consultation_folder": None,
                "output": None,
                "error": str(e)
            }
    
    def start_consultation(
        self,
        consultation_name: str,
        question: str,
        context_files: Optional[List[str]] = None
    ) -> dict:
        """Start a new consultation (Stage 1).
        
        Args:
            consultation_name: Name of the consultation
            question: Initial consultation question
            context_files: Optional list of context file paths
            
        Returns:
            Dictionary with status and consultation folder name
        """
        script = self.scripts_dir / "01_Understand_Context_Create_Prompt.py"
        args = [
            sys.executable,
            str(script),
            "--consultation", consultation_name,
            "--question", question,
            "--root", str(self.project_root)
        ]
        
        if context_files:
            args.extend(["--context"] + context_files)
        
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=600  # 10 minutes
            )
            
            # Extract consultation folder from output
            consultation_folder = None
            for line in result.stdout.split("\n"):
                if "001_" in line or "002_" in line or "003_" in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith("001_") or part.startswith("002_") or part.startswith("003_"):
                            consultation_folder = part
                            break
                    if consultation_folder:
                        break
            
            if not consultation_folder:
                # Try to find the most recent folder
                consultations_dir = self.project_root / "Advanced_Consultations"
                if consultations_dir.exists():
                    folders = sorted([d.name for d in consultations_dir.iterdir() if d.is_dir()], reverse=True)
                    if folders:
                        consultation_folder = folders[0]
            
            return {
                "success": result.returncode == 0,
                "consultation_folder": consultation_folder,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "consultation_folder": None,
                "output": None,
                "error": "Stage 1 timed out after 10 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "consultation_folder": None,
                "output": None,
                "error": str(e)
            }
    
    def fetch_response(self, consultation_folder: str) -> dict:
        """Fetch Gemini 3 Pro response (Stage 2).
        
        Args:
            consultation_folder: Name of consultation folder (e.g., "001_My_Consultation")
            
        Returns:
            Dictionary with status and output
        """
        script = self.scripts_dir / "02_Fetch_Gemini_Response.py"
        args = [
            sys.executable,
            str(script),
            "--consultation-folder", consultation_folder,
            "--root", str(self.project_root)
        ]
        
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=900  # 15 minutes
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": "Stage 2 timed out after 15 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }
    
    def extract_recommendations(self, consultation_folder: str) -> dict:
        """Extract recommendations (Stage 3).
        
        Args:
            consultation_folder: Name of consultation folder (e.g., "001_My_Consultation")
            
        Returns:
            Dictionary with status and output
        """
        script = self.scripts_dir / "03_Extract_Detailed_Recommendations.py"
        args = [
            sys.executable,
            str(script),
            "--consultation-folder", consultation_folder,
            "--root", str(self.project_root)
        ]
        
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=600  # 10 minutes
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": "Stage 3 timed out after 10 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }
    
    def run_full_consultation(
        self,
        consultation_name: str,
        question: str,
        context_files: Optional[List[str]] = None
    ) -> dict:
        """Run all three stages automatically.
        
        Args:
            consultation_name: Name of the consultation
            question: Initial consultation question
            context_files: Optional list of context file paths
            
        Returns:
            Dictionary with status and consultation folder name
        """
        script = self.scripts_dir / "run_full_consultation.py"
        args = [
            sys.executable,
            str(script),
            "--consultation", consultation_name,
            "--question", question,
            "--root", str(self.project_root)
        ]
        
        if context_files:
            args.extend(["--context"] + context_files)
        
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=3600  # 60 minutes
            )
            
            # Extract consultation folder from output
            consultation_folder = None
            for line in result.stdout.split("\n"):
                if "001_" in line or "002_" in line or "003_" in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith("001_") or part.startswith("002_") or part.startswith("003_"):
                            consultation_folder = part
                            break
                    if consultation_folder:
                        break
            
            if not consultation_folder:
                consultations_dir = self.project_root / "Advanced_Consultations"
                if consultations_dir.exists():
                    folders = sorted([d.name for d in consultations_dir.iterdir() if d.is_dir()], reverse=True)
                    if folders:
                        consultation_folder = folders[0]
            
            return {
                "success": result.returncode == 0,
                "consultation_folder": consultation_folder,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "consultation_folder": None,
                "output": None,
                "error": "Full consultation timed out after 60 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "consultation_folder": None,
                "output": None,
                "error": str(e)
            }
    
    def list_consultations(self) -> List[str]:
        """List all available consultations.
        
        Returns:
            List of consultation folder names
        """
        consultations_dir = self.project_root / "Advanced_Consultations"
        if not consultations_dir.exists():
            return []
        
        folders = sorted([d.name for d in consultations_dir.iterdir() if d.is_dir()])
        return folders


def main():
    """CLI interface for Cursor integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Consultation Cursor Integration")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start consultation (Stage 1)')
    start_parser.add_argument('name', help='Consultation name')
    start_parser.add_argument('question', help='Consultation question')
    start_parser.add_argument('--context', nargs='*', help='Context files')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch response (Stage 2)')
    fetch_parser.add_argument('folder', help='Consultation folder name')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract recommendations (Stage 3)')
    extract_parser.add_argument('folder', help='Consultation folder name')
    
    # Full command
    full_parser = subparsers.add_parser('full', help='Run full consultation')
    full_parser.add_argument('name', help='Consultation name')
    full_parser.add_argument('question', help='Consultation question')
    full_parser.add_argument('--context', nargs='*', help='Context files')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List consultations')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    consultation = AdvancedConsultation()
    
    if args.command == 'start':
        result = consultation.start_consultation(args.name, args.question, args.context)
        if result['success']:
            print(f"✅ Stage 1 complete!")
            print(f"Consultation folder: {result['consultation_folder']}")
            print("\n" + result['output'])
        else:
            print(f"❌ Stage 1 failed: {result.get('error', 'Unknown error')}")
            if result.get('output'):
                print(result['output'])
    
    elif args.command == 'fetch':
        result = consultation.fetch_response(args.folder)
        if result['success']:
            print(f"✅ Stage 2 complete!")
            print("\n" + result['output'])
        else:
            print(f"❌ Stage 2 failed: {result.get('error', 'Unknown error')}")
            if result.get('output'):
                print(result['output'])
    
    elif args.command == 'extract':
        result = consultation.extract_recommendations(args.folder)
        if result['success']:
            print(f"✅ Stage 3 complete!")
            print("\n" + result['output'])
        else:
            print(f"❌ Stage 3 failed: {result.get('error', 'Unknown error')}")
            if result.get('output'):
                print(result['output'])
    
    elif args.command == 'full':
        result = consultation.run_full_consultation(args.name, args.question, args.context)
        if result['success']:
            print(f"✅ Full consultation complete!")
            print(f"Consultation folder: {result['consultation_folder']}")
            print("\n" + result['output'])
        else:
            print(f"❌ Full consultation failed: {result.get('error', 'Unknown error')}")
            if result.get('output'):
                print(result['output'])
    
    elif args.command == 'list':
        consultations = consultation.list_consultations()
        if consultations:
            print(f"\n📋 Available Consultations ({len(consultations)} total):\n")
            for folder in consultations:
                print(f"  - {folder}")
        else:
            print("No consultations found.")


if __name__ == "__main__":
    main()

