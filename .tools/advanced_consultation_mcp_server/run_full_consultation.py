"""Run all three consultation stages in sequence.

This is a convenience script that runs all three stages of the consultation
workflow automatically.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_stage(stage_number: int, script_args: list, verbose: bool = True):
    """Run a consultation stage script.
    
    Args:
        stage_number: Stage number (0, 1, 2, or 3)
        script_args: Arguments to pass to the script
        verbose: Whether to print verbose output
        
    Returns:
        True if successful, False otherwise
    """
    stage_names = {
        '0': 'Capture_Initial_Request',
        '1': 'Understand_Context_Create_Prompt',
        '2': 'Fetch_Gemini_Response',
        '3': 'Extract_Detailed_Recommendations'
    }
    script_name = f"{stage_number:02d}_{stage_names[str(stage_number)]}.py"
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ Stage {stage_number} script not found: {script_path}")
        return False
    
    cmd = [sys.executable, str(script_path)] + script_args
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Running Stage {stage_number}: {script_name}")
        print(f"{'='*60}")
    
    try:
        # Extract project root from script_args if present
        project_root = None
        if "--root" in script_args:
            root_idx = script_args.index("--root")
            if root_idx + 1 < len(script_args):
                # Convert to Path to handle Windows paths properly
                project_root = str(Path(script_args[root_idx + 1]).resolve())

        result = subprocess.run(cmd, check=True, capture_output=not verbose, cwd=project_root)
        if result.returncode != 0:
            print(f"❌ Stage {stage_number} failed with return code {result.returncode}")
            if not verbose and result.stderr:
                print(result.stderr.decode())
            return False
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Stage {stage_number} failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running Stage {stage_number}: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run all three consultation stages in sequence"
    )
    parser.add_argument(
        "--consultation",
        "-c",
        required=True,
        help="Name of the consultation"
    )
    parser.add_argument(
        "--question",
        "-q",
        required=True,
        help="Initial consultation question"
    )
    parser.add_argument(
        "--context",
        nargs="*",
        help="Optional context files to reference"
    )
    parser.add_argument(
        "--root",
        "-r",
        type=Path,
        default=Path.cwd(),
        help="Project root directory"
    )
    parser.add_argument(
        "--consultations-dir",
        type=Path,
        help="Base directory for consultations"
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop execution if any stage fails (default: continue)"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"ADVANCED CONSULTATION - FULL WORKFLOW")
    print(f"{'='*60}")
    print(f"Consultation: {args.consultation}")
    print(f"Question: {args.question}")
    print(f"{'='*60}\n")
    
    # Build Stage 0 arguments (Capture Initial Request)
    stage0_args = [
        "--consultation", args.consultation,
        "--request", args.question
    ]
    if args.context:
        stage0_args.extend(["--context"] + args.context)
    if args.root != Path.cwd():
        stage0_args.extend(["--root", str(args.root)])
    if args.consultations_dir:
        stage0_args.extend(["--consultations-dir", str(args.consultations_dir)])
    
    # Run Stage 0
    if not run_stage(0, stage0_args):
        print("\n[FAIL] Stage 0 failed. Cannot continue.")
        sys.exit(1)
    
    # Find the created consultation folder
    if args.consultations_dir:
        consultations_base = args.consultations_dir
    else:
        consultations_base = args.root / "Advanced_Consultations"
    
    if not consultations_base.exists():
        print(f"\n[FAIL] Consultations directory not found: {consultations_base}")
        sys.exit(1)
    
    consultation_folders = [
        d for d in consultations_base.iterdir()
        if d.is_dir() and args.consultation.lower().replace(" ", "_") in d.name.lower()
    ]
    
    if not consultation_folders:
        print(f"\n[FAIL] Could not find consultation folder for: {args.consultation}")
        sys.exit(1)
    
    consultation_folder = consultation_folders[-1]  # Get the most recent one
    
    print(f"\n[OK] Stage 0 complete. Consultation folder: {consultation_folder.name}\n")
    
    # Build Stage 1 arguments (now reads from 00_Initial_Request.md)
    stage1_args = [
        "--consultation-folder", consultation_folder.name
    ]
    if args.root != Path.cwd():
        stage1_args.extend(["--root", str(args.root)])
    if args.consultations_dir:
        stage1_args.extend(["--consultations-dir", str(args.consultations_dir)])
    
    # Run Stage 1
    if not run_stage(1, stage1_args):
        if args.stop_on_error:
            print("\n[FAIL] Stage 1 failed. Stopping.")
            sys.exit(1)
        else:
            print("\n[WARN] Stage 1 failed. Continuing to Stage 2...")
    else:
        print(f"\n[OK] Stage 1 complete.\n")
    
    # Build Stage 2 arguments
    stage2_args = [
        "--consultation-folder", consultation_folder.name
    ]
    if args.root != Path.cwd():
        stage2_args.extend(["--root", str(args.root)])
    if args.consultations_dir:
        stage2_args.extend(["--consultations-dir", str(args.consultations_dir)])
    
    # Run Stage 2
    if not run_stage(2, stage2_args):
        if args.stop_on_error:
            print("\n[FAIL] Stage 2 failed. Stopping.")
            sys.exit(1)
        else:
            print("\n[WARN] Stage 2 failed. Continuing to Stage 3...")
    else:
        print(f"\n[OK] Stage 2 complete.\n")
    
    # Build Stage 3 arguments
    stage3_args = [
        "--consultation-folder", consultation_folder.name
    ]
    if args.root != Path.cwd():
        stage3_args.extend(["--root", str(args.root)])
    if args.consultations_dir:
        stage3_args.extend(["--consultations-dir", str(args.consultations_dir)])
    
    # Run Stage 3
    if not run_stage(3, stage3_args):
        if args.stop_on_error:
            print("\n[FAIL] Stage 3 failed.")
            sys.exit(1)
        else:
            print("\n[WARN] Stage 3 failed.")
    else:
        print(f"\n[OK] Stage 3 complete.\n")
    
    print(f"\n{'='*60}")
    print(f"[SUCCESS] CONSULTATION WORKFLOW COMPLETE")
    print(f"{'='*60}")
    print(f"\nAll files saved to: {consultation_folder}")
    print(f"  0. 00_Initial_Request.md")
    print(f"  1. 01_Initial_User_System_Prompt.md")
    print(f"  2. 02_Context_Files.md")
    print(f"  3. 03_Original_Raw_Output_from_Gemini3Pro.md")
    print(f"  4. 04_Recommendations.md\n")


if __name__ == "__main__":
    main()

