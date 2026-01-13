"""Stage 2: Fetch Gemini 3 Pro Response.

Uses the generated prompt from Stage 1 and context files to get a
comprehensive response from Gemini 3 Pro ONLY.

Configuration follows 01_Gemini3_Pro.txt:
- Model: gemini-3-pro-preview (via Gemini3ProWrapper)
- Temperature: 0 (deterministic)
- Thinking level: HIGH
- Tools: Google Search enabled
- Safety settings: All OFF
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import LLM wrappers
# Updated path: both folders are now siblings in References/
sys.path.insert(0, str(Path(__file__).parent.parent / "04_LLM_Levers"))
from llm_wrappers.gemini3_pro_wrapper import Gemini3ProWrapper
from llm_wrappers.prompt_parser import PromptParser


def find_consultation_folder(consultation_folder_name: str, base_path: Path = None, project_root: Path = None) -> Path:
    """Find consultation folder by name or path.
    
    Args:
        consultation_folder_name: Name of consultation folder (with or without number prefix)
        base_path: Base path for consultations (default: project_root/Advanced_Consultations/)
        project_root: Project root directory (default: current directory)
        
    Returns:
        Path to consultation folder
    """
    if base_path is None:
        project_root = project_root or Path.cwd()
        base_path = project_root / "Advanced_Consultations"
    
    # If full path provided
    if Path(consultation_folder_name).exists():
        return Path(consultation_folder_name)
    
    # Search in base path
    consultation_folder = base_path / consultation_folder_name
    if consultation_folder.exists():
        return consultation_folder
    
    # Try to find by partial name match
    matching_folders = [
        d for d in base_path.iterdir()
        if d.is_dir() and consultation_folder_name.lower() in d.name.lower()
    ]
    
    if matching_folders:
        if len(matching_folders) == 1:
            return matching_folders[0]
        else:
            print(f"Multiple matches found:")
            for i, folder in enumerate(matching_folders, 1):
                print(f"  {i}. {folder.name}")
            raise ValueError(f"Multiple consultation folders match '{consultation_folder_name}'")
    
    raise FileNotFoundError(f"Consultation folder not found: {consultation_folder_name}")


def load_prompt_file(prompt_file: Path) -> tuple[str, str]:
    """Load and parse the prompt file from Stage 1.
    
    Args:
        prompt_file: Path to 01_Initial_User_System_Prompt.md
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    content = prompt_file.read_text(encoding="utf-8")
    
    # Extract System Prompt section
    system_match = re.search(r'## System Prompt\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    system_prompt = system_match.group(1).strip() if system_match else ""
    
    # Extract User Prompt section
    user_match = re.search(r'## User Prompt\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    user_prompt = user_match.group(1).strip() if user_match else ""
    
    if not system_prompt or not user_prompt:
        raise ValueError("Could not parse System Prompt and User Prompt from prompt file")
    
    return system_prompt, user_prompt


def parse_context_files(context_files_file: Path, project_root: Path) -> str:
    """Parse and load context files from 02_Context_Files.md.
    
    Args:
        context_files_file: Path to 02_Context_Files.md
        project_root: Project root for resolving file paths
        
    Returns:
        Concatenated content of all context files
    """
    if not context_files_file.exists():
        print(f"[WARN] Context files file not found: {context_files_file}")
        print("   Continuing without context files...")
        return ""
    
    content = context_files_file.read_text(encoding="utf-8")
    
    # Extract file paths (lines starting with -)
    file_paths = re.findall(r'^-\s*(.+)$', content, re.MULTILINE)
    file_paths = [f.strip() for f in file_paths if f.strip() and not f.strip().startswith("<!--")]
    
    if not file_paths:
        print("[INFO] No context files specified in 02_Context_Files.md")
        return ""
    
    print(f"[INFO] Loading {len(file_paths)} context file(s)...")
    
    context_parts = []
    loaded_count = 0
    
    for file_path in file_paths:
        full_path = project_root / file_path
        if full_path.exists():
            try:
                file_content = full_path.read_text(encoding="utf-8")
                context_parts.append(f"\n=== FILE: {file_path} ===\n{file_content}\n=== END FILE ===\n")
                loaded_count += 1
                print(f"   [OK] Loaded: {file_path}")
            except Exception as e:
                print(f"   [WARN] Error reading {file_path}: {e}")
                context_parts.append(f"\n=== FILE: {file_path} ===\n[Error: {e}]\n=== END FILE ===\n")
        else:
            print(f"   [WARN] File not found: {file_path}")
            context_parts.append(f"\n=== FILE: {file_path} ===\n[File not found]\n=== END FILE ===\n")
    
    print(f"[OK] Loaded {loaded_count}/{len(file_paths)} context file(s)\n")
    
    return "".join(context_parts)


def save_raw_output(output_file: Path, response: str, duration: float, 
                   system_prompt: str, user_prompt: str, context_summary: str):
    """Save the raw Gemini response.
    
    Args:
        output_file: Path to save 03_Original_Raw_Output_from_Gemini3Pro.md
        response: Raw response from Gemini
        duration: Response duration in seconds
        system_prompt: System prompt used (for reference)
        user_prompt: User prompt used (for reference)
        context_summary: Summary of context files used
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# Original Raw Output from Gemini 3 Pro

**Generated:** {timestamp}
**Duration:** {duration:.2f} seconds
**Model:** gemini-3-pro-preview
**Stage:** 2 - Response Fetching

---

## System Prompt Used

```
{system_prompt[:500]}{'...[truncated]' if len(system_prompt) > 500 else ''}
```

---

## User Prompt Used

```
{user_prompt[:500]}{'...[truncated]' if len(user_prompt) > 500 else ''}
```

---

## Context Files Used

{context_summary if context_summary else "None"}

---

## Raw Response

{response}

---

## Next Steps

1. Review the raw response above
2. Run Stage 3: `python 03_Extract_Detailed_Recommendations.py --consultation-folder "{output_file.parent.name}"`
"""
    
    output_file.write_text(content, encoding="utf-8")
    try:
        rel_path = output_file.relative_to(Path.cwd())
        print(f"[OK] Raw output saved to: {rel_path}")
    except ValueError:
        print(f"[OK] Raw output saved to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Stage 2: Fetch Gemini 3 Pro Response"
    )
    parser.add_argument(
        "--consultation-folder",
        "-f",
        required=True,
        help="Name or path of consultation folder (from Stage 1)"
    )
    parser.add_argument(
        "--root",
        "-r",
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
    
    # Find consultation folder
    if args.consultations_dir:
        consultations_base = args.consultations_dir
    else:
        consultations_base = args.root / "Advanced_Consultations"
    consultation_folder = find_consultation_folder(args.consultation_folder, consultations_base, args.root)
    
    print(f"\n{'='*60}")
    print(f"STAGE 2: FETCH GEMINI 3 PRO RESPONSE")
    print(f"{'='*60}")
    print(f"Consultation Folder: {consultation_folder.name}")
    print(f"{'='*60}\n")
    
    # Load prompt from Stage 1
    prompt_file = consultation_folder / "01_Initial_User_System_Prompt.md"
    system_prompt, user_prompt = load_prompt_file(prompt_file)
    
    print("[INFO] Loaded prompt from Stage 1\n")
    
    # Load context files
    context_files_file = consultation_folder / "02_Context_Files.md"
    context_content = parse_context_files(context_files_file, args.root)
    
    # Initialize Gemini wrapper
    wrapper = Gemini3ProWrapper(project_root=args.root)
    
    print("[INFO] Calling Gemini 3 Pro with structured prompt...\n")
    print("="*60)
    
    # Call Gemini 3 Pro with structured prompt
    # Using exact configuration from 01_Gemini3_Pro.txt:
    # - Model: gemini-3-pro-preview (default in wrapper)
    # - Temperature: 0 (deterministic)
    # - Thinking level: HIGH
    # - Google Search tools enabled
    import time
    start_time = time.time()
    
    try:
        response = wrapper.run(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            context=context_content,
            thinking_level="HIGH",
            temperature=0,  # Match 01_Gemini3_Pro.txt: deterministic responses
            timeout_seconds=900  # 15 minutes for comprehensive responses
        )
        
        duration = time.time() - start_time
        
        print("\n" + "="*60)
        
        # Create context summary
        context_summary = ""
        if context_content:
            file_count = context_content.count("=== FILE:")
            context_summary = f"Loaded {file_count} context file(s)"
        
        # Save raw output
        output_file = consultation_folder / "03_Original_Raw_Output_from_Gemini3Pro.md"
        save_raw_output(
            output_file,
            response,
            duration,
            system_prompt,
            user_prompt,
            context_summary
        )
        
        print(f"\n{'='*60}")
        print("[OK] Stage 2 Complete!")
        print(f"{'='*60}")
        print(f"\nResponse saved to: {output_file.name}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"\nNext step:")
        print(f"  Run Stage 3: python 03_Extract_Detailed_Recommendations.py --consultation-folder \"{consultation_folder.name}\"\n")
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

