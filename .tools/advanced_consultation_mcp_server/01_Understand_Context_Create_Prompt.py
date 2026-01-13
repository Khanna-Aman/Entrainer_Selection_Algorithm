"""Stage 1: Understand Context and Create Detailed Prompt.

Uses Gemini 3 Pro ONLY to analyze the initial consultation request and create
a detailed, structured prompt that captures the big picture and context.

Configuration follows 01_Gemini3_Pro.txt:
- Model: gemini-3-pro-preview (via Gemini3ProWrapper)
- Temperature: 0 (deterministic)
- Thinking level: HIGH
- Tools: Google Search enabled
- Safety settings: All OFF
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import LLM wrappers
# Updated path: both folders are now siblings in References/
sys.path.insert(0, str(Path(__file__).parent.parent / "04_LLM_Levers"))
from llm_wrappers.gemini3_pro_wrapper import Gemini3ProWrapper


def find_or_create_consultation_folder(consultation_name: str, base_path: Path = None, project_root: Path = None) -> Path:
    """Find existing consultation folder or create new one.
    
    Args:
        consultation_name: Name of the consultation (will be sanitized)
        base_path: Base path for consultations (default: project_root/Advanced_Consultations/)
        project_root: Project root directory (default: current directory)
        
    Returns:
        Path to the consultation folder
    """
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


def generate_prompt_generation_request(initial_question: str, context_files: list = None) -> str:
    """Create the prompt for Gemini to generate the structured consultation prompt.
    
    Args:
        initial_question: The initial consultation question
        context_files: Optional list of context file paths
        
    Returns:
        System prompt for prompt generation
    """
    context_info = ""
    if context_files:
        context_info = f"\n\nContext files available (you may reference these):\n"
        for cf in context_files:
            context_info += f"- {cf}\n"
    
    system_prompt = """You are an expert at creating detailed, structured prompts for complex technical consultations.

Your task is to analyze an initial consultation request and create a comprehensive, well-structured prompt that:

1. **Understands the Big Picture**: Analyze the underlying context, goals, and constraints
2. **Creates System Instructions**: Generate detailed system prompt instructions that guide the AI consultant's approach
3. **Structures the User Query**: Transform the initial question into a structured, comprehensive query
4. **Identifies Key Areas**: Break down the consultation into key areas that need analysis

The output should be saved in a specific markdown format with clear sections.
"""
    
    user_prompt = f"""I need your help creating a detailed consultation prompt.

**Initial Consultation Request:**
{initial_question}
{context_info}

**Your Task:**

1. **Analyze the Big Picture**: 
   - What is the underlying context and goals?
   - What are the key constraints and considerations?
   - What domains/areas does this consultation touch?

2. **Create System Instructions**:
   - Write detailed system prompt instructions for the AI consultant
   - Define the consultant's role and expertise areas
   - Specify how to approach the analysis
   - Include any methodology or frameworks to use

3. **Structure the User Query**:
   - Transform the initial question into a comprehensive, structured query
   - Break down into specific sub-questions if needed
   - Ensure all important aspects are covered

4. **Provide Context Understanding**:
   - Summarize your understanding of the big picture
   - Highlight key areas that need analysis
   - Note any assumptions or constraints

**Output Format:**

Please provide your response in the following markdown format:

```markdown
## System Prompt

[Your detailed system instructions here - this should be comprehensive and guide the consultant's entire approach]

## User Prompt

[Your structured user query here - this should be detailed and cover all aspects]

## Context Understanding

[Your analysis of the big picture, key areas, constraints, and considerations]
```

Be thorough and detailed. The prompt you create will be used for a comprehensive consultation with Gemini 3 Pro."""
    
    return system_prompt, user_prompt


def save_generated_prompt(consultation_folder: Path, system_prompt: str, user_prompt: str, 
                          context_understanding: str, consultation_name: str) -> Path:
    """Save the generated prompt to the consultation folder.
    
    Args:
        consultation_folder: Path to consultation folder
        system_prompt: Generated system prompt
        user_prompt: Generated user prompt
        context_understanding: Context understanding section
        consultation_name: Name of the consultation
        
    Returns:
        Path to the saved prompt file
    """
    output_file = consultation_folder / "01_Initial_User_System_Prompt.md"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# Consultation: {consultation_name}

**Generated:** {timestamp}
**Model:** gemini-3-pro-preview
**Stage:** 1 - Prompt Generation

---

## System Prompt

{system_prompt}

---

## User Prompt

{user_prompt}

---

## Context Understanding

{context_understanding}

---

## Next Steps

1. Review and edit this prompt if needed
2. Update `02_Context_Files.md` with any additional context files (if needed)
3. Run Stage 2: `python 02_Fetch_Gemini_Response.py --consultation-folder "{consultation_folder.name}"`
"""
    
    output_file.write_text(content, encoding="utf-8")
    try:
        rel_path = output_file.relative_to(Path.cwd())
        print(f"[OK] Prompt saved to: {rel_path}")
    except ValueError:
        print(f"[OK] Prompt saved to: {output_file}")
    
    return output_file


def create_context_files_template(consultation_folder: Path):
    """Create an empty 02_Context_Files.md template.
    
    Args:
        consultation_folder: Path to consultation folder
    """
    context_file = consultation_folder / "02_Context_Files.md"
    
    content = """## Context Files

<!-- Add file paths here, one per line, relative to project root -->
<!-- Example: -->
<!-- - Initial Approach.md -->
<!-- - Re-Usable Components/04_LLM_Levers/README.md -->

"""
    
    context_file.write_text(content, encoding="utf-8")
    print(f"[OK] Context files template created: {context_file.name}")


def find_consultation_folder(consultation_folder_name: str, base_path: Path = None, project_root: Path = None) -> Path:
    """Find existing consultation folder by name.
    
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


def load_initial_request(consultation_folder: Path) -> tuple[str, list]:
    """Load initial request from 00_Initial_Request.md if it exists.
    
    Args:
        consultation_folder: Path to consultation folder
        
    Returns:
        Tuple of (initial_request, context_files) or (None, []) if file doesn't exist
    """
    request_file = consultation_folder / "00_Initial_Request.md"
    
    if not request_file.exists():
        return None, []
    
    content = request_file.read_text(encoding="utf-8")
    
    # Extract initial request
    import re
    request_match = re.search(r'## 📝 Initial Request\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    initial_request = request_match.group(1).strip() if request_match else None
    
    # Extract context files
    context_match = re.search(r'## 📎 Context Files Referenced\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    context_files = []
    if context_match:
        context_section = context_match.group(1)
        context_files = re.findall(r'^-\s*`(.+?)`', context_section, re.MULTILINE)
    
    return initial_request, context_files


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Stage 1: Understand Context and Create Detailed Prompt"
    )
    parser.add_argument(
        "--consultation",
        "-c",
        help="Name of the consultation (e.g., 'Database Architecture Decision') - required if not using --consultation-folder"
    )
    parser.add_argument(
        "--consultation-folder",
        "-f",
        help="Name or path of existing consultation folder (from Stage 0) - if provided, reads from 00_Initial_Request.md"
    )
    parser.add_argument(
        "--question",
        "-q",
        help="Initial consultation question (required if not using --consultation-folder)"
    )
    parser.add_argument(
        "--context",
        nargs="*",
        help="Optional context files to reference (paths relative to project root)"
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
    
    # Determine if we're using existing folder or creating new
    if args.consultation_folder:
        # Stage 0 was run - read from existing folder
        consultations_base = args.consultations_dir or args.root / "Advanced_Consultations"
        consultation_folder = find_consultation_folder(args.consultation_folder, consultations_base, args.root)
        
        # Load initial request
        initial_request, context_files_from_file = load_initial_request(consultation_folder)
        
        if not initial_request:
            print("[WARN] 00_Initial_Request.md not found or empty. Using provided arguments.")
            if not args.question:
                print("[FAIL] Error: --question required when 00_Initial_Request.md not found")
                sys.exit(1)
            initial_request = args.question
            context_files = args.context or []
        else:
            # Use context files from Stage 0, or override with provided ones
            context_files = args.context if args.context else context_files_from_file
        
        consultation_name = consultation_folder.name.split("_", 1)[1] if "_" in consultation_folder.name else consultation_folder.name
        
    elif args.consultation and args.question:
        # Create new consultation folder (backward compatibility)
        consultation_folder = find_or_create_consultation_folder(
            args.consultation,
            base_path=args.consultations_dir,
            project_root=args.root
        )
        initial_request = args.question
        context_files = args.context or []
        consultation_name = args.consultation
    else:
        print("[FAIL] Error: Must provide either --consultation-folder OR (--consultation and --question)")
        parser.print_help()
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"STAGE 1: UNDERSTAND CONTEXT & CREATE PROMPT")
    print(f"{'='*60}")
    print(f"Consultation: {consultation_name}")
    print(f"Folder: {consultation_folder.name}")
    if args.consultation_folder:
        print(f"Reading from: 00_Initial_Request.md")
    print(f"{'='*60}\n")
    
    # Generate prompt generation request
    system_prompt, user_prompt = generate_prompt_generation_request(
        initial_request,
        context_files=context_files
    )
    
    # Initialize Gemini wrapper
    wrapper = Gemini3ProWrapper(project_root=args.root)
    
    print("[INFO] Calling Gemini 3 Pro to generate structured prompt...\n")
    
    # Call Gemini 3 Pro to generate the prompt
    # Using exact configuration from 01_Gemini3_Pro.txt:
    # - Model: gemini-3-pro-preview (default in wrapper)
    # - Temperature: 0 (deterministic)
    # - Thinking level: HIGH
    # - Google Search tools enabled
    try:
        response = wrapper.run(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            thinking_level="HIGH",
            temperature=0,  # Match 01_Gemini3_Pro.txt: deterministic responses
            timeout_seconds=600  # 10 minutes for complex analysis
        )
        
        # Parse the response to extract sections
        # Try to extract sections from markdown
        import re
        
        system_match = re.search(r'## System Prompt\s*\n(.*?)(?=\n## |\Z)', response, re.DOTALL)
        user_match = re.search(r'## User Prompt\s*\n(.*?)(?=\n## |\Z)', response, re.DOTALL)
        context_match = re.search(r'## Context Understanding\s*\n(.*?)(?=\n## |\Z)', response, re.DOTALL)
        
        if system_match and user_match:
            extracted_system = system_match.group(1).strip()
            extracted_user = user_match.group(1).strip()
            extracted_context = context_match.group(1).strip() if context_match else response.strip()
        else:
            # Fallback: use response as-is, split intelligently
            print("[WARN] Could not parse structured sections, using response as-is")
            extracted_system = response
            extracted_user = args.question
            extracted_context = "See full response above"
        
        # Save the generated prompt
        save_generated_prompt(
            consultation_folder,
            extracted_system,
            extracted_user,
            extracted_context,
            args.consultation
        )
        
        # Create context files template
        create_context_files_template(consultation_folder)
        
        print(f"\n{'='*60}")
        print("[OK] Stage 1 Complete!")
        print(f"{'='*60}")
        print(f"\nNext steps:")
        print(f"1. Review: {consultation_folder / '01_Initial_User_System_Prompt.md'}")
        print(f"2. Add context files to: {consultation_folder / '02_Context_Files.md'}")
        print(f"3. Run Stage 2: python 02_Fetch_Gemini_Response.py --consultation-folder \"{consultation_folder.name}\"\n")
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

