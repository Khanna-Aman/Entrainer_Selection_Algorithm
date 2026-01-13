"""Advanced Consultation MCP Server - Main entry point.

This MCP server exposes tools for the three-stage Advanced Consultation workflow:
1. Understand Context & Create Prompt
2. Fetch Gemini Response
3. Extract Recommendations

All consultations use Gemini 3 Pro only with configuration from 01_Gemini3_Pro.txt.

Usage:
  # Run directly
  python -m advanced_consultation_mcp.server

  # Or via the installed command
  advanced-consultation-mcp
"""

import asyncio
import subprocess
import sys
import os
import json
import logging
from pathlib import Path
from typing import Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, ResourceTemplate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("advanced-consultation-mcp")

# Initialize the MCP server
server = Server("advanced-consultation-mcp")

# Project root (defaults to current working directory or environment variable)
PROJECT_ROOT: Optional[Path] = None


def get_project_root() -> Path:
    """Get or initialize the project root."""
    global PROJECT_ROOT
    if PROJECT_ROOT is None:
        # Check environment variable first
        env_root = os.environ.get("ADVANCED_CONSULTATION_PROJECT_ROOT")
        if env_root:
            PROJECT_ROOT = Path(env_root)
        else:
            PROJECT_ROOT = Path.cwd()
        logger.info(f"Project root set to: {PROJECT_ROOT}")
    return PROJECT_ROOT


def set_project_root(root: Path):
    """Set the project root directory."""
    global PROJECT_ROOT
    PROJECT_ROOT = root
    logger.info(f"Project root updated to: {PROJECT_ROOT}")


def run_stage_script(stage_number: int, args: list[str], project_root: Path) -> tuple[str, int]:
    """Run a consultation stage script.

    Args:
        stage_number: Stage number (0, 1, 2, or 3)
        args: Arguments to pass to the script
        project_root: Project root directory

    Returns:
        Tuple of (output, return_code)
    """
    # Scripts are in the parent directory of mcp_server
    # Structure: Advanced_Consultation_MCP_Server/scripts.py and Advanced_Consultation_MCP_Server/mcp_server/
    mcp_server_dir = Path(__file__).parent.parent
    scripts_dir = mcp_server_dir.parent
    stage_names = {
        0: "00_Capture_Initial_Request.py",
        1: "01_Understand_Context_Create_Prompt.py",
        2: "02_Fetch_Gemini_Response.py",
        3: "03_Extract_Detailed_Recommendations.py"
    }

    script_path = scripts_dir / stage_names[stage_number]

    if not script_path.exists():
        error_msg = f"Error: Script not found: {script_path}"
        logger.error(error_msg)
        return error_msg, 1

    # Build command - use "python" instead of sys.executable to avoid Windows Store Python restrictions
    python_cmd = "python"
    cmd = [python_cmd, str(script_path)] + args
    logger.info(f"Running Stage {stage_number}: {' '.join(cmd)}")
    logger.info(f"Script path: {script_path}")
    logger.info(f"Script exists: {script_path.exists()}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Project root exists: {project_root.exists()}")

    try:
        # Ensure project_root exists
        if not project_root.exists():
            error_msg = f"Error: Project root does not exist: {project_root}"
            logger.error(error_msg)
            return error_msg, 1

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=1800  # 30 minutes timeout
        )
        output = result.stdout + result.stderr
        logger.info(f"Stage {stage_number} completed with return code {result.returncode}")
        return output, result.returncode
    except subprocess.TimeoutExpired:
        error_msg = "Error: Script execution timed out after 30 minutes"
        logger.error(error_msg)
        return error_msg, 1
    except Exception as e:
        error_msg = f"Error: {str(e)}\nScript: {script_path}\nCWD: {project_root}"
        logger.error(error_msg, exc_info=True)
        return error_msg, 1


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="capture_initial_request",
            description="Stage 0: Capture the user's initial consultation request. Creates a consultation folder "
                       "and saves the raw request to 00_Initial_Request.md. This is the pre-step before Stage 1.",
            inputSchema={
                "type": "object",
                "properties": {
                    "consultation_name": {
                        "type": "string",
                        "description": "Name of the consultation (e.g., 'Database Architecture Decision')"
                    },
                    "request": {
                        "type": "string",
                        "description": "Initial consultation request/question"
                    },
                    "context_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of context file paths (relative to project root)"
                    }
                },
                "required": ["consultation_name", "request"]
            }
        ),
        Tool(
            name="start_advanced_consultation",
            description="Stage 1: Start Advanced Consultation. Uses Gemini 3 Pro to understand context and generate "
                       "a detailed, structured prompt. Reads from 00_Initial_Request.md if consultation folder exists, "
                       "or creates new consultation. Returns the consultation folder name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "consultation_folder": {
                        "type": "string",
                        "description": "Name of existing consultation folder (from Stage 0) - if provided, reads from 00_Initial_Request.md"
                    },
                    "consultation_name": {
                        "type": "string",
                        "description": "Name of the consultation (required if consultation_folder not provided)"
                    },
                    "question": {
                        "type": "string",
                        "description": "Initial consultation question (required if consultation_folder not provided)"
                    },
                    "context_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of context file paths (relative to project root)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="fetch_consultation_response",
            description="Stage 2: Fetch comprehensive response from Gemini 3 Pro using the generated "
                       "prompt from Stage 1 and any context files. Saves raw response for review.",
            inputSchema={
                "type": "object",
                "properties": {
                    "consultation_folder": {
                        "type": "string",
                        "description": "Name of the consultation folder (e.g., '001_Database_Architecture_Decision') "
                                     "or path to the folder from Advanced_Consultations/"
                    }
                },
                "required": ["consultation_folder"]
            }
        ),
        Tool(
            name="extract_consultation_recommendations",
            description="Stage 3: Extract structured recommendations from the raw Gemini 3 Pro response. "
                       "Analyzes the response and creates a prioritized list of recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "consultation_folder": {
                        "type": "string",
                        "description": "Name of the consultation folder (e.g., '001_Database_Architecture_Decision') "
                                     "or path to the folder from Advanced_Consultations/"
                    }
                },
                "required": ["consultation_folder"]
            }
        ),
        Tool(
            name="run_full_consultation",
            description="Run all three stages of Advanced Consultation in sequence. "
                       "Starts with Stage 1, then automatically runs Stages 2 and 3.",
            inputSchema={
                "type": "object",
                "properties": {
                    "consultation_name": {
                        "type": "string",
                        "description": "Name of the consultation (e.g., 'Database Architecture Decision')"
                    },
                    "question": {
                        "type": "string",
                        "description": "Initial consultation question or request"
                    },
                    "context_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of context file paths (relative to project root)"
                    }
                },
                "required": ["consultation_name", "question"]
            }
        ),
        Tool(
            name="list_consultations",
            description="List all available consultations in Advanced_Consultations/ folder.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "capture_initial_request":
        return await _handle_capture_request(arguments)
    elif name == "start_advanced_consultation":
        return await _handle_start_consultation(arguments)
    elif name == "fetch_consultation_response":
        return await _handle_fetch_response(arguments)
    elif name == "extract_consultation_recommendations":
        return await _handle_extract_recommendations(arguments)
    elif name == "run_full_consultation":
        return await _handle_run_full_consultation(arguments)
    elif name == "list_consultations":
        return await _handle_list_consultations(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _handle_capture_request(args: dict) -> list[TextContent]:
    """Handle capture_initial_request tool call."""
    consultation_name = args.get("consultation_name", "")
    request = args.get("request", "")
    context_files = args.get("context_files", [])
    
    if not consultation_name or not request:
        return [TextContent(type="text", text="[FAIL] Error: consultation_name and request are required")]
    
    project_root = get_project_root()
    
    # Build arguments for Stage 0
    script_args = [
        "--consultation", consultation_name,
        "--request", request,
        "--root", str(project_root)
    ]
    
    if context_files:
        script_args.extend(["--context"] + context_files)
    
    # Run Stage 0
    output, return_code = run_stage_script(0, script_args, project_root)
    
    if return_code != 0:
        return [TextContent(type="text", text=f"[FAIL] Stage 0 failed:\n{output}")]
    
    # Extract consultation folder name from output
    consultation_folder = None
    for line in output.split("\n"):
        if "001_" in line or "002_" in line or "003_" in line:
            parts = line.split()
            for part in parts:
                if part.startswith("001_") or part.startswith("002_") or part.startswith("003_"):
                    consultation_folder = part
                    break
            if consultation_folder:
                break
    
    if not consultation_folder:
        # Fallback: try to find the folder
        consultations_dir = project_root / "Advanced_Consultations"
        if consultations_dir.exists():
            folders = sorted([d.name for d in consultations_dir.iterdir() if d.is_dir()], reverse=True)
            if folders:
                consultation_folder = folders[0]
    
    result = f"[OK] **Stage 0 Complete**\n\n"
    result += f"**Consultation:** {consultation_name}\n"
    if consultation_folder:
        result += f"**Folder:** {consultation_folder}\n"
    result += f"\n**Output:**\n```\n{output}\n```\n\n"
    result += f"**Next Steps:**\n"
    result += f"1. Review the captured request: `Advanced_Consultations/{consultation_folder}/00_Initial_Request.md`\n"
    result += f"2. Run Stage 1 using `start_advanced_consultation` with consultation_folder: `{consultation_folder}`"
    
    return [TextContent(type="text", text=result)]


async def _handle_start_consultation(args: dict) -> list[TextContent]:
    """Handle start_advanced_consultation tool call."""
    consultation_folder = args.get("consultation_folder")
    consultation_name = args.get("consultation_name", "")
    question = args.get("question", "")
    context_files = args.get("context_files", [])
    
    project_root = get_project_root()
    
    # Build arguments
    if consultation_folder:
        # Use existing folder (from Stage 0)
        script_args = [
            "--consultation-folder", consultation_folder,
            "--root", str(project_root)
        ]
    elif consultation_name and question:
        # Create new consultation (backward compatibility)
        script_args = [
            "--consultation", consultation_name,
            "--question", question,
            "--root", str(project_root)
        ]
        if context_files:
            script_args.extend(["--context"] + context_files)
    else:
        return [TextContent(type="text", text="[FAIL] Error: Must provide either consultation_folder OR (consultation_name and question)")]
    
    # Run Stage 1
    output, return_code = run_stage_script(1, script_args, project_root)
    
    if return_code != 0:
        return [TextContent(type="text", text=f"[FAIL] Stage 1 failed:\n{output}")]
    
    # Extract consultation folder name from output
    # The folder name is typically printed in the output
    consultation_folder = None
    for line in output.split("\n"):
        if "Folder:" in line or "001_" in line:
            parts = line.split()
            for part in parts:
                if part.startswith("001_") or part.startswith("002_") or part.startswith("003_"):
                    consultation_folder = part
                    break
            if consultation_folder:
                break
    
    if not consultation_folder:
        # Fallback: try to find the folder
        consultations_dir = project_root / "Advanced_Consultations"
        if consultations_dir.exists():
            folders = sorted([d.name for d in consultations_dir.iterdir() if d.is_dir()], reverse=True)
            if folders:
                consultation_folder = folders[0]
    
    result = f"✅ **Stage 1 Complete**\n\n"
    result += f"**Consultation:** {consultation_name}\n"
    if consultation_folder:
        result += f"**Folder:** {consultation_folder}\n"
    result += f"\n**Output:**\n```\n{output}\n```\n\n"
    result += f"**Next Steps:**\n"
    result += f"1. Review the generated prompt: `Advanced_Consultations/{consultation_folder}/01_Initial_User_System_Prompt.md`\n"
    result += f"2. Optionally add context files to: `Advanced_Consultations/{consultation_folder}/02_Context_Files.md`\n"
    result += f"3. Run Stage 2 using `fetch_consultation_response` with consultation_folder: `{consultation_folder}`"
    
    return [TextContent(type="text", text=result)]


async def _handle_fetch_response(args: dict) -> list[TextContent]:
    """Handle fetch_consultation_response tool call."""
    consultation_folder = args.get("consultation_folder", "")
    
    if not consultation_folder:
        return [TextContent(type="text", text="❌ Error: consultation_folder is required")]
    
    project_root = get_project_root()
    
    # Build arguments
    script_args = [
        "--consultation-folder", consultation_folder,
        "--root", str(project_root)
    ]
    
    # Run Stage 2
    output, return_code = run_stage_script(2, script_args, project_root)
    
    if return_code != 0:
        return [TextContent(type="text", text=f"[FAIL] Stage 2 failed:\n{output}")]
    
    result = f"[OK] **Stage 2 Complete**\n\n"
    result += f"**Consultation Folder:** {consultation_folder}\n"
    result += f"\n**Output:**\n```\n{output}\n```\n\n"
    result += f"**Next Steps:**\n"
    result += f"1. Review raw response: `Advanced_Consultations/{consultation_folder}/03_Original_Raw_Output_from_Gemini3Pro.md`\n"
    result += f"2. Run Stage 3 using `extract_consultation_recommendations` with consultation_folder: `{consultation_folder}`"
    
    return [TextContent(type="text", text=result)]


async def _handle_extract_recommendations(args: dict) -> list[TextContent]:
    """Handle extract_consultation_recommendations tool call."""
    consultation_folder = args.get("consultation_folder", "")
    
    if not consultation_folder:
        return [TextContent(type="text", text="[FAIL] Error: consultation_folder is required")]
    
    project_root = get_project_root()
    
    # Build arguments
    script_args = [
        "--consultation-folder", consultation_folder,
        "--root", str(project_root)
    ]
    
    # Run Stage 3
    output, return_code = run_stage_script(3, script_args, project_root)
    
    if return_code != 0:
        return [TextContent(type="text", text=f"[FAIL] Stage 3 failed:\n{output}")]
    
    result = f"[OK] **Stage 3 Complete**\n\n"
    result += f"**Consultation Folder:** {consultation_folder}\n"
    result += f"\n**Output:**\n```\n{output}\n```\n\n"
    result += f"[SUCCESS] **Consultation Complete!**\n\n"
    result += f"**All Files:**\n"
    result += f"- `Advanced_Consultations/{consultation_folder}/00_Initial_Request.md`\n"
    result += f"- `Advanced_Consultations/{consultation_folder}/01_Initial_User_System_Prompt.md`\n"
    result += f"- `Advanced_Consultations/{consultation_folder}/02_Context_Files.md`\n"
    result += f"- `Advanced_Consultations/{consultation_folder}/03_Original_Raw_Output_from_Gemini3Pro.md`\n"
    result += f"- `Advanced_Consultations/{consultation_folder}/04_Recommendations.md`\n"
    
    return [TextContent(type="text", text=result)]


async def _handle_run_full_consultation(args: dict) -> list[TextContent]:
    """Handle run_full_consultation tool call."""
    consultation_name = args.get("consultation_name", "")
    question = args.get("question", "")
    context_files = args.get("context_files", [])
    
    if not consultation_name or not question:
        return [TextContent(type="text", text="[FAIL] Error: consultation_name and question are required")]
    
    project_root = get_project_root()
    
    # Use the run_full_consultation.py script
    mcp_server_dir = Path(__file__).parent.parent
    scripts_dir = mcp_server_dir.parent
    script_path = scripts_dir / "run_full_consultation.py"
    
    if not script_path.exists():
        return [TextContent(type="text", text=f"❌ Error: Script not found: {script_path}")]
    
    # Build arguments
    script_args = [
        "--consultation", consultation_name,
        "--question", question,
        "--root", str(project_root)
    ]
    
    if context_files:
        script_args.extend(["--context"] + context_files)
    
    # Run full consultation - use "python" to avoid Windows Store Python restrictions
    cmd = ["python", str(script_path)] + script_args
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=3600  # 60 minutes timeout for full consultation
        )
        
        if result.returncode != 0:
            return [TextContent(type="text", text=f"❌ Full consultation failed:\n{result.stdout}\n{result.stderr}")]
        
        output = result.stdout + result.stderr
        
        # Extract consultation folder name
        consultation_folder = None
        for line in output.split("\n"):
            if "Folder:" in line or "001_" in line or "002_" in line or "003_" in line:
                parts = line.split()
                for part in parts:
                    if part.startswith("001_") or part.startswith("002_") or part.startswith("003_"):
                        consultation_folder = part
                        break
                if consultation_folder:
                    break
        
        if not consultation_folder:
            consultations_dir = project_root / "Advanced_Consultations"
            if consultations_dir.exists():
                folders = sorted([d.name for d in consultations_dir.iterdir() if d.is_dir()], reverse=True)
                if folders:
                    consultation_folder = folders[0]
        
        result_text = f"🎉 **Full Consultation Complete!**\n\n"
        result_text += f"**Consultation:** {consultation_name}\n"
        if consultation_folder:
            result_text += f"**Folder:** {consultation_folder}\n"
        result_text += f"\n**Output:**\n```\n{output}\n```\n\n"
        result_text += f"**All Files Available:**\n"
        result_text += f"- `Advanced_Consultations/{consultation_folder}/01_Initial_User_System_Prompt.md`\n"
        result_text += f"- `Advanced_Consultations/{consultation_folder}/02_Context_Files.md`\n"
        result_text += f"- `Advanced_Consultations/{consultation_folder}/03_Original_Raw_Output_from_Gemini3Pro.md`\n"
        result_text += f"- `Advanced_Consultations/{consultation_folder}/04_Recommendations.md`"
        
        return [TextContent(type="text", text=result_text)]
        
    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="[FAIL] Error: Full consultation timed out after 60 minutes")]
    except Exception as e:
        return [TextContent(type="text", text=f"[FAIL] Error: {str(e)}")]


async def _handle_list_consultations(args: dict) -> list[TextContent]:
    """Handle list_consultations tool call."""
    project_root = get_project_root()
    consultations_dir = project_root / "Advanced_Consultations"
    
    if not consultations_dir.exists():
        return [TextContent(type="text", text="[INFO] No consultations found. Advanced_Consultations/ folder does not exist yet.")]
    
    folders = sorted([d for d in consultations_dir.iterdir() if d.is_dir()])
    
    if not folders:
        return [TextContent(type="text", text="[INFO] No consultations found in Advanced_Consultations/ folder.")]
    
    result = f"[INFO] **Available Consultations** ({len(folders)} total)\n\n"
    
    for folder in folders:
        result += f"- **{folder.name}**\n"
        # Check which files exist
        files = []
        if (folder / "00_Initial_Request.md").exists():
            files.append("[OK] Stage 0")
        if (folder / "01_Initial_User_System_Prompt.md").exists():
            files.append("[OK] Stage 1")
        if (folder / "03_Original_Raw_Output_from_Gemini3Pro.md").exists():
            files.append("[OK] Stage 2")
        if (folder / "04_Recommendations.md").exists():
            files.append("[OK] Stage 3")
        
        if files:
            result += f"  - {', '.join(files)}\n"
        else:
            result += f"  - [PENDING] Incomplete\n"
    
    return [TextContent(type="text", text=result)]


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available consultation resources."""
    resources = []
    project_root = get_project_root()
    consultations_dir = project_root / "Advanced_Consultations"

    if consultations_dir.exists():
        for folder in sorted(consultations_dir.iterdir()):
            if folder.is_dir():
                # Add the recommendations file as a resource
                rec_file = folder / "04_Recommendations.md"
                if rec_file.exists():
                    resources.append(Resource(
                        uri=f"consultation://{folder.name}/recommendations",
                        name=f"{folder.name} - Recommendations",
                        description=f"Extracted recommendations from consultation {folder.name}",
                        mimeType="text/markdown"
                    ))

                # Add the raw output as a resource
                raw_file = folder / "03_Original_Raw_Output_from_Gemini3Pro.md"
                if raw_file.exists():
                    resources.append(Resource(
                        uri=f"consultation://{folder.name}/raw_output",
                        name=f"{folder.name} - Raw Output",
                        description=f"Raw Gemini 3 Pro response from consultation {folder.name}",
                        mimeType="text/markdown"
                    ))

    return resources


@server.read_resource()
async def read_resource(uri) -> str:
    """Read a consultation resource."""
    # Handle both string and AnyUrl objects
    uri_str = str(uri)

    # Parse URI: consultation://<folder_name>/<file_type>
    if not uri_str.startswith("consultation://"):
        raise ValueError(f"Unknown resource URI: {uri_str}")

    path = uri_str[len("consultation://"):]
    parts = path.split("/")

    if len(parts) != 2:
        raise ValueError(f"Invalid consultation URI format: {uri_str}")

    folder_name, file_type = parts
    project_root = get_project_root()
    consultations_dir = project_root / "Advanced_Consultations" / folder_name

    file_map = {
        "recommendations": "04_Recommendations.md",
        "raw_output": "03_Original_Raw_Output_from_Gemini3Pro.md",
        "prompt": "01_Initial_User_System_Prompt.md",
        "request": "00_Initial_Request.md",
        "context": "02_Context_Files.md"
    }

    if file_type not in file_map:
        raise ValueError(f"Unknown file type: {file_type}")

    file_path = consultations_dir / file_map[file_type]

    if not file_path.exists():
        raise FileNotFoundError(f"Consultation file not found: {file_path}")

    return file_path.read_text(encoding="utf-8")


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Advanced Consultation MCP Server...")
    logger.info(f"Python: {sys.executable}")
    logger.info(f"CWD: {Path.cwd()}")

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server initialized, running...")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main_sync():
    """Synchronous entry point for command line usage."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()

