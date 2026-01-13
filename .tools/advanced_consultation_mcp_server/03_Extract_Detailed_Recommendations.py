"""Stage 3: Extract Detailed Recommendations.

Analyzes the raw Gemini 3 Pro response from Stage 2 and extracts specific
recommendations and feedback as structured list items using Gemini 3 Pro ONLY.

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


def load_raw_output(raw_output_file: Path) -> str:
    """Load the raw output from Stage 2.
    
    Args:
        raw_output_file: Path to 03_Original_Raw_Output_from_Gemini3Pro.md
        
    Returns:
        Raw response content
    """
    if not raw_output_file.exists():
        raise FileNotFoundError(f"Raw output file not found: {raw_output_file}")
    
    content = raw_output_file.read_text(encoding="utf-8")
    
    # Extract the Raw Response section
    response_match = re.search(r'## Raw Response\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if response_match:
        return response_match.group(1).strip()
    
    # Fallback: return full content if section not found
    return content.strip()


def generate_extraction_prompt(raw_response: str) -> tuple[str, str]:
    """Generate the prompt for extracting recommendations.
    
    Args:
        raw_response: Raw response from Stage 2
        
    Returns:
        Tuple of (system_prompt, user_prompt) for extraction
    """
    system_prompt = """You are an expert at analyzing AI consultation responses and extracting structured, actionable recommendations.

Your task is to:
1. Identify all recommendations, suggestions, and actionable items from the consultation response
2. Categorize them by priority (High, Medium, Low)
3. Extract key feedback and insights
4. Format everything as a clear, structured markdown document

Focus on extracting:
- Specific actionable recommendations
- Strategic guidance
- Technical suggestions
- Risk warnings or considerations
- Best practices mentioned
- Any prioritized items
"""
    
    user_prompt = f"""Please analyze the following consultation response and extract all recommendations, feedback, and actionable items.

**Consultation Response:**

{raw_response}

**Your Task:**

Extract and structure the following:

1. **High Priority Recommendations** - Critical actions, urgent items, major decisions needed
2. **Medium Priority Recommendations** - Important but not urgent, should be addressed soon
3. **Low Priority Recommendations** - Nice-to-have improvements, future considerations
4. **Key Insights** - Important observations, patterns, or considerations
5. **Additional Notes** - Context, caveats, or supplementary information

**Output Format:**

Provide your analysis in the following markdown format:

```markdown
# Recommendations

## High Priority

1. [Recommendation 1 with explanation]
2. [Recommendation 2 with explanation]

## Medium Priority

1. [Recommendation 1 with explanation]
2. [Recommendation 2 with explanation]

## Low Priority

1. [Recommendation 1 with explanation]

## Key Insights

- [Insight 1]
- [Insight 2]

## Additional Notes

[Any additional context, caveats, or considerations]
```

Be thorough and extract ALL recommendations and actionable items, even if they seem minor.
Prioritize based on:
- **High**: Critical decisions, security issues, performance blockers, breaking changes
- **Medium**: Important improvements, architectural considerations, significant optimizations
- **Low**: Nice-to-have features, minor optimizations, future enhancements"""
    
    return system_prompt, user_prompt


def save_recommendations(output_file: Path, recommendations: str, duration: float):
    """Save the extracted recommendations.
    
    Args:
        output_file: Path to save 04_Recommendations.md
        recommendations: Extracted recommendations content
        duration: Extraction duration in seconds
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Try to extract the structured content if it's wrapped in markdown code blocks
    # Sometimes Gemini returns code blocks, sometimes not
    if "```markdown" in recommendations:
        # Extract content from markdown code block
        match = re.search(r'```markdown\s*\n(.*?)\n```', recommendations, re.DOTALL)
        if match:
            recommendations = match.group(1).strip()
    elif "```" in recommendations:
        # Extract from generic code block
        match = re.search(r'```\s*\n(.*?)\n```', recommendations, re.DOTALL)
        if match:
            recommendations = match.group(1).strip()
    
    content = f"""# Recommendations

**Extracted:** {timestamp}
**Duration:** {duration:.2f} seconds
**Model:** gemini-3-pro-preview
**Stage:** 3 - Recommendation Extraction

---

{recommendations}

---

## Consultation Workflow Complete

This consultation has completed all three stages:
1. ✅ **Stage 1**: Context understanding and prompt generation
2. ✅ **Stage 2**: Comprehensive Gemini 3 Pro response
3. ✅ **Stage 3**: Recommendation extraction (this file)

Review the recommendations above and proceed with implementation as appropriate.
"""
    
    output_file.write_text(content, encoding="utf-8")
    try:
        rel_path = output_file.relative_to(Path.cwd())
        print(f"[OK] Recommendations saved to: {rel_path}")
    except ValueError:
        print(f"[OK] Recommendations saved to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Stage 3: Extract Detailed Recommendations"
    )
    parser.add_argument(
        "--consultation-folder",
        "-f",
        required=True,
        help="Name or path of consultation folder"
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
    print(f"STAGE 3: EXTRACT DETAILED RECOMMENDATIONS")
    print(f"{'='*60}")
    print(f"Consultation Folder: {consultation_folder.name}")
    print(f"{'='*60}\n")
    
    # Load raw output from Stage 2
    raw_output_file = consultation_folder / "03_Original_Raw_Output_from_Gemini3Pro.md"
    raw_response = load_raw_output(raw_output_file)
    
    print(f"[INFO] Loaded raw response ({len(raw_response)} characters)\n")
    
    # Generate extraction prompt
    system_prompt, user_prompt = generate_extraction_prompt(raw_response)
    
    # Initialize Gemini wrapper
    wrapper = Gemini3ProWrapper(project_root=args.root)
    
    print("[INFO] Calling Gemini 3 Pro to extract recommendations...\n")
    print("="*60)
    
    # Call Gemini 3 Pro to extract recommendations
    # Using exact configuration from 01_Gemini3_Pro.txt:
    # - Model: gemini-3-pro-preview (default in wrapper)
    # - Temperature: 0 (deterministic)
    # - Thinking level: HIGH (for thorough extraction)
    # - Google Search tools enabled
    import time
    start_time = time.time()
    
    try:
        response = wrapper.run(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            thinking_level="HIGH",  # Use HIGH thinking for thorough extraction
            temperature=0,  # Match 01_Gemini3_Pro.txt: deterministic responses
            timeout_seconds=600  # 10 minutes
        )
        
        duration = time.time() - start_time
        
        print("\n" + "="*60)
        
        # Save recommendations
        output_file = consultation_folder / "04_Recommendations.md"
        save_recommendations(output_file, response, duration)
        
        print(f"\n{'='*60}")
        print("[OK] Stage 3 Complete!")
        print(f"{'='*60}")
        print(f"\nRecommendations saved to: {output_file.name}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"\n[SUCCESS] Consultation workflow complete!")
        print(f"\nAll files available in: {consultation_folder.name}/")
        print(f"  1. 01_Initial_User_System_Prompt.md")
        print(f"  2. 02_Context_Files.md")
        print(f"  3. 03_Original_Raw_Output_from_Gemini3Pro.md")
        print(f"  4. 04_Recommendations.md\n")
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

