# 🧠 Advanced Consultation MCP Server

**Version:** 1.0  
**Purpose:** A three-stage consultation workflow that leverages Gemini 3 Pro for deep analysis, structured consultation, and recommendation extraction.

---

## 🎯 Overview

This MCP Server provides an advanced consultation system that goes beyond simple Q&A. It uses a three-stage approach with **Gemini 3 Pro ONLY** (following the exact configuration from `01_Gemini3_Pro.txt`):

1. **Understand Context** - Gemini 3 Pro analyzes your initial question and creates detailed, structured prompts
2. **Fetch Comprehensive Response** - Uses the structured prompt with context files to get a deep, comprehensive response from Gemini 3 Pro
3. **Extract Recommendations** - Parses the response using Gemini 3 Pro and extracts actionable recommendations in a structured format

### Model Configuration

All scripts use **Gemini 3 Pro** (`gemini-3-pro-preview`) with the following configuration (from `01_Gemini3_Pro.txt`):
- **Model**: `gemini-3-pro-preview` (via Gemini3ProWrapper)
- **Temperature**: `0` (deterministic responses)
- **Thinking Level**: `HIGH` (deep thinking mode)
- **Tools**: Google Search enabled
- **Safety Settings**: All OFF
- **Max Output Tokens**: 65535
- **Top P**: 0.95

---

## 📂 Folder Structure

Each consultation creates its own folder with a numbered prefix:

```
Project Root/
├── Advanced_Consultation_MCP_Server/             # Scripts folder
│   ├── README.md                                  # This file
│   ├── 00_Capture_Initial_Request.py              # Stage 0: Capture initial request
│   ├── 01_Understand_Context_Create_Prompt.py    # Stage 1: Prompt Generation
│   ├── 02_Fetch_Gemini_Response.py               # Stage 2: Response Fetching
│   ├── 03_Extract_Detailed_Recommendations.py    # Stage 3: Recommendation Extraction
│   └── run_full_consultation.py                  # Convenience script
│
└── Advanced_Consultations/                       # All consultations stored here (in project root)
    └── 001_<Consultation Name>/                  # Individual consultation folder
        ├── 00_Initial_Request.md                  # User's initial request (Stage 0)
        ├── 01_Initial_User_System_Prompt.md      # Generated prompt from Stage 1
        ├── 02_Context_Files.md                   # List of context files (may be empty)
        ├── 03_Original_Raw_Output_from_Gemini3Pro.md  # Raw response from Stage 2
        └── 04_Recommendations.md                 # Extracted recommendations from Stage 3
```

---

## 🔄 Workflow

### Stage 0: Capture Initial Request

**Script:** `00_Capture_Initial_Request.py`

**Purpose:** Captures the user's initial consultation request before processing.

**Input:**
- Consultation name
- Initial request/question
- Optional context files

**Output:**
- `001_<Consultation Name>/00_Initial_Request.md`
  - Raw, unprocessed user request
  - Context files referenced
  - Timestamp and metadata

**Process:**
1. Creates consultation folder
2. Saves user's initial request verbatim
3. Records context files if provided
4. Ready for Stage 1 processing

---

### Stage 1: Understand Context & Create Prompt

**Script:** `01_Understand_Context_Create_Prompt.py`

**Purpose:** Uses Gemini 3 Pro to understand the big picture and create a detailed, structured prompt.

**Input:**
- Consultation folder (from Stage 0) OR consultation name + question
- Reads from `00_Initial_Request.md` if folder exists
- Optional context files

**Output:**
- `001_<Consultation Name>/01_Initial_User_System_Prompt.md`
  - System prompt with detailed instructions
  - User prompt with structured query
  - Context understanding and big picture analysis

**Process:**
1. Reads initial request from Stage 0 (or uses provided question)
2. Sends to Gemini 3 Pro with thinking mode enabled
3. Asks Gemini to understand context, big picture, and create optimal prompts
4. Saves structured prompt file

---

### Stage 2: Fetch Gemini Response

**Script:** `02_Fetch_Gemini_Response.py`

**Purpose:** Uses the generated prompt from Stage 1 to get a comprehensive response from Gemini 3 Pro.

**Input:**
- Consultation folder path (from Stage 1)
- `00_Initial_Request.md` (from Stage 0)
- `01_Initial_User_System_Prompt.md` (from Stage 1)
- `02_Context_Files.md` (file list - may be empty)

**Output:**
- `03_Original_Raw_Output_from_Gemini3Pro.md` - Raw, unprocessed response

**Process:**
1. Reads the prompt from `01_Initial_User_System_Prompt.md`
2. Reads `02_Context_Files.md` and parses file list
3. Loads all context files and includes in request
4. Calls Gemini 3 Pro with the structured prompt + context
5. Saves raw response

**Note:** `02_Context_Files.md` format:
```markdown
## Context Files

- path/to/file1.md
- path/to/file2.py
- folder/subfolder/file3.txt
```

If empty, no context files are included.

---

### Stage 3: Extract Recommendations

**Script:** `03_Extract_Detailed_Recommendations.py`

**Purpose:** Analyzes the raw Gemini response and extracts specific recommendations and feedback as structured list items.

**Input:**
- Consultation folder path
- `03_Original_Raw_Output_from_Gemini3Pro.md` (from Stage 2)

**Output:**
- `04_Recommendations.md` - Structured list of recommendations

**Process:**
1. Reads raw output from Stage 2
2. Sends to Gemini 3 Pro to extract recommendations
3. Formats as structured markdown list
4. Saves recommendations file

---

## 🚀 Usage

### Quick Start

```bash
# Stage 0: Capture initial request
python Advanced_Consultation_MCP_Server/00_Capture_Initial_Request.py --consultation "Database Architecture Decision" --request "Should I use PostgreSQL or MongoDB for this project?"

# Stage 1: Create structured prompt (reads from Stage 0)
python Advanced_Consultation_MCP_Server/01_Understand_Context_Create_Prompt.py --consultation-folder "001_Database_Architecture_Decision"

# Stage 2: Fetch comprehensive response
python Advanced_Consultation_MCP_Server/02_Fetch_Gemini_Response.py --consultation-folder "001_Database_Architecture_Decision"

# Stage 3: Extract recommendations
python Advanced_Consultation_MCP_Server/03_Extract_Detailed_Recommendations.py --consultation-folder "001_Database_Architecture_Decision"
```

### With Context Files

```bash
# Stage 0: Capture request with context files
python Advanced_Consultation_MCP_Server/00_Capture_Initial_Request.py --consultation "Database Decision" --request "..." --context "Initial Approach.md" "Re-Usable Components/04_LLM_Levers/README.md"

# Stage 1: Create structured prompt (reads from Stage 0)
python Advanced_Consultation_MCP_Server/01_Understand_Context_Create_Prompt.py --consultation-folder "001_Database_Decision"

# Stage 2 will automatically use context files from Stage 0
python Advanced_Consultation_MCP_Server/02_Fetch_Gemini_Response.py --consultation-folder "001_Database_Decision"
```

---

## 🔧 Configuration

### Environment Variables

- `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID (default: "vk-genai")
- `GOOGLE_CLOUD_LOCATION` - Google Cloud region (default: "global")
- `GEMINI_MODEL` - Gemini model to use (default: "gemini-3-pro-preview")
  - **Note**: All Advanced Consultation scripts use **Gemini 3 Pro ONLY** (`gemini-3-pro-preview`)
  - Changing this environment variable will affect the model used (not recommended)

### Dependencies

```bash
pip install google-genai tenacity
```

---

## 💡 Improvement Suggestions

### 1. **Iterative Refinement**
- Add a Stage 4 that allows refining prompts based on initial recommendations
- Loop back to Stage 1 with feedback from Stage 3

### 2. **Context File Auto-Discovery**
- Automatically scan project for relevant files based on consultation topic
- Use embeddings to find semantically related files

### 3. **Multi-Model Comparison**
- Run same consultation across multiple models (Gemini 3 Pro, Claude, etc.)
- Compare and synthesize recommendations

### 4. **Recommendation Prioritization**
- Add urgency/priority scoring to recommendations
- Categorize by: Quick Wins, Strategic, Technical Debt, etc.

### 5. **Consultation Templates**
- Pre-built templates for common consultation types:
  - Architecture decisions
  - Code review
  - Performance optimization
  - Security audit

### 6. **Integration with Decision Log**
- Auto-link to Two-Mind Protocol decision log
- Track which recommendations were implemented
- Audit trail for decision-making

### 7. **Visualization**
- Generate diagrams from recommendations
- Create mind maps of decision trees
- Timeline visualization of consultation workflow

### 8. **Collaborative Features**
- Share consultations with team members
- Comment threads on recommendations
- Voting/consensus on recommendations

### 9. **Cost Tracking**
- Track token usage per consultation
- Cost estimates before running
- Budget alerts

### 10. **Caching & Reuse**
- Cache similar consultations
- Reuse prompts for similar questions
- Version control for prompt templates

### 11. **Export Formats**
- Export recommendations to JIRA, Linear, GitHub Issues
- Generate presentations from consultation results
- PDF reports with formatting

### 12. **Advanced Analysis**
- Sentiment analysis on recommendations
- Risk scoring
- Impact assessment (low/medium/high)
- Dependency mapping between recommendations

### 13. **MCP Tool Integration**
- Expose as MCP tools for Claude Desktop
- Integrate with existing Two-Mind Protocol MCP Server
- API endpoints for programmatic access

### 14. **Prompt Library**
- Build a library of successful prompts
- A/B test different prompt styles
- Learn from best-performing consultations

### 15. **Multi-Stage Feedback Loop**
- Stage 3 feeds back into Stage 1 for refinement
- Human-in-the-loop approval between stages
- Branch consultations based on recommendations

---

## 📝 File Formats

### `00_Initial_Request.md`

```markdown
# Initial Consultation Request

**Consultation:** <Name>
**Captured:** YYYY-MM-DD HH:MM:SS
**Stage:** 0 - Initial Request Capture

## 📝 Initial Request

[User's raw, unprocessed request/question]

## 📎 Context Files Referenced

- path/to/file1.md
- path/to/file2.py
```

### `01_Initial_User_System_Prompt.md`

```markdown
# Consultation: <Name>

**Generated:** YYYY-MM-DD HH:MM:SS
**Model:** gemini-3-pro-preview

## System Prompt

[Detailed system instructions created by Gemini]

## User Prompt

[Structured user query created by Gemini]

## Context Understanding

[Gemini's analysis of the big picture and context]
```

### `02_Context_Files.md`

```markdown
## Context Files

- path/to/file1.md
- path/to/file2.py
- folder/subfolder/file3.txt
```

### `03_Original_Raw_Output_from_Gemini3Pro.md`

Raw, unprocessed response from Gemini 3 Pro (verbatim).

### `04_Recommendations.md`

```markdown
# Recommendations

## High Priority

1. [Recommendation 1]
2. [Recommendation 2]

## Medium Priority

1. [Recommendation 3]

## Low Priority

1. [Recommendation 4]

## Additional Notes

[Additional feedback and considerations]
```

---

## 🔗 Integration

### With Two-Mind Protocol

This system integrates with the Two-Mind Protocol MCP Server:
- Consultations can be linked to decisions
- Recommendations feed into decision approval workflow
- Automatic logging to `.gemini/consultations/`

### With Backlog System

- Recommendations can be converted to backlog items
- Link consultations to feature files
- Track implementation of recommendations

---

## 📚 Related

- [Two-Mind Protocol](../Re-Usable Components/01_Two_Mind_Protocol/README.md)
- [MCP Server](../Re-Usable Components/03_MCP_Server/README.md)
- [LLM Wrappers](../Re-Usable Components/04_LLM_Levers/README.md)

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| Consultation folder not found | Ensure Stage 1 completed successfully |
| Context files not loading | Check file paths in `02_Context_Files.md` are relative to project root |
| Gemini API errors | Verify Google Cloud credentials and project settings |
| Recommendations empty | Check if raw output contains structured recommendations |

---

## 🖥️ Using in Cursor (Recommended)

**You're using Cursor, so you can use these scripts directly!** No MCP server or Claude Desktop needed.

### Quick Start

1. **Simple approach**: Just ask me (the AI assistant) to run consultations for you
2. **Command line**: Use the scripts directly
3. **Helper script**: Use `cursor_helper.py` for a simpler interface

See **[CURSOR_USAGE.md](CURSOR_USAGE.md)** for complete instructions on using in Cursor.

### Helper Script (Optional)

Use `cursor_helper.py` for a simpler interface:

```bash
# Start a consultation
python cursor_helper.py start "Database Decision" "Should I use PostgreSQL or MongoDB?"

# Continue (Stage 2)
python cursor_helper.py continue 001_Database_Decision

# Extract recommendations (Stage 3)
python cursor_helper.py extract 001_Database_Decision

# List all consultations
python cursor_helper.py list
```

---

## 🔌 MCP Server Integration

The Advanced Consultation system can be used as an MCP server for various AI assistants.

### Available Tools

| Tool | Description |
|------|-------------|
| `capture_initial_request` | Stage 0 - Capture user's initial request |
| `start_advanced_consultation` | Stage 1 - Generate structured prompt |
| `fetch_consultation_response` | Stage 2 - Get Gemini 3 Pro response |
| `extract_consultation_recommendations` | Stage 3 - Extract recommendations |
| `run_full_consultation` | Run all stages automatically |
| `list_consultations` | List past consultations |

### VSCode Integration

Add to `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "advanced-consultation": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "advanced_consultation_mcp.server"],
      "cwd": "${workspaceFolder}/Advanced_Consultation_MCP_Server/mcp_server",
      "env": {
        "ADVANCED_CONSULTATION_PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/Advanced_Consultation_MCP_Server/mcp_server"
      }
    }
  }
}
```

### Augment Code Integration

1. Open Augment Code Settings (gear icon in Augment panel)
2. In the MCP section, click **Import from JSON**
3. Paste this configuration:

```json
{
  "mcpServers": {
    "advanced-consultation": {
      "command": "python -m advanced_consultation_mcp.server",
      "env": {
        "PYTHONPATH": "/path/to/your/project/.tools/advanced_consultation_mcp_server/mcp_server",
        "ADVANCED_CONSULTATION_PROJECT_ROOT": "/path/to/your/project"
      }
    }
  }
}
```

### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "advanced-consultation": {
      "command": "python",
      "args": ["-m", "advanced_consultation_mcp.server"],
      "cwd": "/path/to/your/project/.tools/advanced_consultation_mcp_server/mcp_server",
      "env": {
        "PYTHONPATH": "/path/to/your/project/.tools/advanced_consultation_mcp_server/mcp_server",
        "ADVANCED_CONSULTATION_PROJECT_ROOT": "/path/to/your/project"
      }
    }
  }
}
```

### Testing the Server

```bash
cd Advanced_Consultation_MCP_Server/mcp_server
python -c "from advanced_consultation_mcp.server import server, list_tools; import asyncio; tools = asyncio.run(list_tools()); print(f'Loaded {len(tools)} tools'); [print(f'  - {t.name}') for t in tools]"
```

See [SETUP_AND_TEST.md](SETUP_AND_TEST.md) for detailed setup and testing instructions.

