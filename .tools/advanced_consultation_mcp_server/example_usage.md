# Example Usage

## Quick Start

### Run All Stages at Once

```bash
python Advanced_Consultation_MCP_Server/run_full_consultation.py \
  --consultation "Database Architecture Decision" \
  --question "Should I use PostgreSQL or MongoDB for my new project? Consider scalability, ACID requirements, and developer experience."
```

### Run Stages Individually

#### Stage 0: Capture Initial Request

```bash
python Advanced_Consultation_MCP_Server/00_Capture_Initial_Request.py \
  --consultation "Database Architecture Decision" \
  --request "Should I use PostgreSQL or MongoDB for my new project?"
```

This will:
- Create folder: `Advanced_Consultations/001_Database_Architecture_Decision/` (in project root)
- Save: `00_Initial_Request.md` with your raw request

#### Stage 1: Create Prompt

```bash
python Advanced_Consultation_MCP_Server/01_Understand_Context_Create_Prompt.py \
  --consultation-folder "001_Database_Architecture_Decision"
```

This will:
- Read from: `00_Initial_Request.md` (from Stage 0)
- Generate: `01_Initial_User_System_Prompt.md`
- Create: `02_Context_Files.md` (template)

#### Stage 2: Fetch Response

```bash
# First, edit 02_Context_Files.md to add context files (optional)
# Then run:

python Advanced_Consultation_MCP_Server/02_Fetch_Gemini_Response.py \
  --consultation-folder "001_Database_Architecture_Decision"
```

This will:
- Read prompt from Stage 1
- Read context files from `02_Context_Files.md`
- Call Gemini 3 Pro with structured prompt
- Save: `03_Original_Raw_Output_from_Gemini3Pro.md`

#### Stage 3: Extract Recommendations

```bash
python Advanced_Consultation_MCP_Server/03_Extract_Detailed_Recommendations.py \
  --consultation-folder "001_Database_Architecture_Decision"
```

This will:
- Read raw output from Stage 2
- Extract structured recommendations
- Save: `04_Recommendations.md`

---

## With Context Files

### Step 1: Create Context Files List

Edit `02_Context_Files.md` in your consultation folder:

```markdown
## Context Files

- Initial Approach.md
- Re-Usable Components/04_LLM_Levers/README.md
- src/database/schema.py
```

### Step 2: Run Stage 2

Stage 2 will automatically load and include these files.

---

## Example Workflow

```bash
# 1. Start consultation
python run_full_consultation.py \
  --consultation "API Design Decision" \
  --question "What's the best REST API design pattern for a multi-tenant SaaS application?"

# 2. Review generated prompt in Advanced_Consultations/001_API_Design_Decision/01_Initial_User_System_Prompt.md

# 3. Add context files if needed
echo "- src/api/current_design.py" >> Advanced_Consultations/001_API_Design_Decision/02_Context_Files.md

# 4. Re-run Stage 2 if you added context files
python Advanced_Consultation_MCP_Server/02_Fetch_Gemini_Response.py \
  --consultation-folder "001_API_Design_Decision"

# 5. Review recommendations
cat Advanced_Consultations/001_API_Design_Decision/04_Recommendations.md
```

---

## Custom Project Root

If your project root is different:

```bash
python 01_Understand_Context_Create_Prompt.py \
  --consultation "My Consultation" \
  --question "My question?" \
  --root /path/to/project
```

---

## Multiple Consultations

Each consultation gets its own numbered folder:

- `001_Database_Decision/`
- `002_API_Design/`
- `003_Security_Audit/`
- etc.

The numbering is automatic and sequential.

