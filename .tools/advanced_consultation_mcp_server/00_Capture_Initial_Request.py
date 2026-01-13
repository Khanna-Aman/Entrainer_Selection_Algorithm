"""Stage 0: Capture Initial Request.

This is the pre-step that captures the user's initial consultation request
and saves it to 00_Initial_Request.md before Stage 1 processes it.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import helper functions
# Updated path: both folders are now siblings in References/
sys.path.insert(0, str(Path(__file__).parent.parent / "04_LLM_Levers"))
from llm_wrappers.gemini3_pro_wrapper import Gemini3ProWrapper


def create_consultation_folder(consultation_name: str, base_path: Path = None, project_root: Path = None) -> Path:
    """Create a consultation folder with numbered prefix.
    
    Args:
        consultation_name: Name of the consultation (will be sanitized)
        base_path: Base path for consultations (default: project_root/Advanced_Consultations/)
        project_root: Project root directory (default: current directory)
        
    Returns:
        Path to the created consultation folder
    """
    if base_path is None:
        project_root = project_root or Path.cwd()
        base_path = project_root / "Advanced_Consultations"
    
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Sanitize consultation name
    safe_name = "".join(c for c in consultation_name if c.isalnum() or c in (" ", "-", "_"))
    safe_name = safe_name.replace(" ", "_").strip("_")
    
    # Find next available number
    existing_folders = [d for d in base_path.iterdir() if d.is_dir() and d.name.split("_", 1)[0].isdigit()]
    if existing_folders:
        max_num = max(int(d.name.split("_", 1)[0]) for d in existing_folders)
        next_num = max_num + 1
    else:
        next_num = 1
    
    folder_name = f"{next_num:03d}_{safe_name}"
    consultation_folder = base_path / folder_name
    consultation_folder.mkdir(parents=True, exist_ok=True)
    
    return consultation_folder


def save_initial_request(consultation_folder: Path, consultation_name: str, initial_request: str, 
                        context_files: list = None) -> Path:
    """Save the initial request to 00_Initial_Request.md.
    
    Args:
        consultation_folder: Path to consultation folder
        consultation_name: Name of the consultation
        initial_request: User's initial consultation request/question
        context_files: Optional list of context file paths
        
    Returns:
        Path to the saved request file
    """
    output_file = consultation_folder / "00_Initial_Request.md"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    context_section = ""
    if context_files:
        context_section = "\n## 📎 Context Files Referenced\n\n"
        for cf in context_files:
            context_section += f"- `{cf}`\n"
        context_section += "\n"
    
    content = f"""# Initial Consultation Request

**Consultation:** {consultation_name}
**Captured:** {timestamp}
**Stage:** 0 - Initial Request Capture

---

## 📝 Initial Request

{initial_request}

{context_section}---

## 📋 Next Steps

1. Review this initial request
2. Run Stage 1: `python 01_Understand_Context_Create_Prompt.py --consultation-folder "{consultation_folder.name}"`
   - Stage 1 will use this request to generate a detailed, structured prompt
   - Or use: `python run_full_consultation.py --consultation-folder "{consultation_folder.name}"` to continue automatically

---

## 📝 Notes

This is the raw, unprocessed request from the user. Stage 1 will analyze this and create a comprehensive structured prompt for Gemini 3 Pro consultation.
"""
    
    output_file.write_text(content, encoding="utf-8")
    # Try to get relative path, fallback to absolute if not possible
    try:
        rel_path = output_file.relative_to(Path.cwd())
        print(f"[OK] Initial request saved to: {rel_path}")
    except ValueError:
        print(f"[OK] Initial request saved to: {output_file}")
    
    return output_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Stage 0: Capture Initial Consultation Request"
    )
    parser.add_argument(
        "--consultation",
        "-c",
        required=True,
        help="Name of the consultation (e.g., 'Database Architecture Decision')"
    )
    parser.add_argument(
        "--request",
        required=True,
        help="Initial consultation request/question"
    )
    parser.add_argument(
        "--context",
        nargs="*",
        help="Optional context files to reference (paths relative to project root)"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--consultations-dir",
        type=Path,
        help="Base directory for consultations (default: <project_root>/Advanced_Consultations/)"
    )
    
    args = parser.parse_args()
    
    # Create consultation folder
    consultation_folder = create_consultation_folder(
        args.consultation,
        base_path=args.consultations_dir,
        project_root=args.root
    )
    
    print(f"\n{'='*60}")
    print(f"STAGE 0: CAPTURE INITIAL REQUEST")
    print(f"{'='*60}")
    print(f"Consultation: {args.consultation}")
    print(f"Folder: {consultation_folder.name}")
    print(f"{'='*60}\n")
    
    # Save initial request
    request_file = save_initial_request(
        consultation_folder,
        args.consultation,
        args.request,
        context_files=args.context
    )
    
    print(f"\n{'='*60}")
    print("[SUCCESS] Stage 0 Complete!")
    print(f"{'='*60}")
    print(f"\nInitial request saved to: {request_file.name}")
    print(f"\nNext steps:")
    print(f"1. Review: {consultation_folder / '00_Initial_Request.md'}")
    print(f"2. Run Stage 1: python 01_Understand_Context_Create_Prompt.py --consultation-folder \"{consultation_folder.name}\"")
    print(f"   Or run full workflow: python run_full_consultation.py --consultation-folder \"{consultation_folder.name}\"\n")


if __name__ == "__main__":
    main()

