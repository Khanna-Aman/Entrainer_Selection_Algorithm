# 📝 Using Advanced Consultation in Cursor

Since you're using Cursor with Gemini 3 Pro, you can use the Advanced Consultation scripts directly - no MCP server or Claude Desktop needed!

---

## 🚀 Quick Start in Cursor

### Option 1: Run Scripts Directly (Simplest)

Just run the scripts directly from the command line in Cursor:

```bash
# Stage 0: Capture initial request
python Advanced_Consultation_MCP_Server/00_Capture_Initial_Request.py \
  --consultation "My Consultation Name" \
  --request "Your question here?"

# Stage 1: Create structured prompt (reads from Stage 0)
python Advanced_Consultation_MCP_Server/01_Understand_Context_Create_Prompt.py \
  --consultation-folder "001_My_Consultation_Name"

# Stage 2: Get response
python Advanced_Consultation_MCP_Server/02_Fetch_Gemini_Response.py \
  --consultation-folder "001_My_Consultation_Name"

# Stage 3: Extract recommendations
python Advanced_Consultation_MCP_Server/03_Extract_Detailed_Recommendations.py \
  --consultation-folder "001_My_Consultation_Name"
```

Or run all four stages at once:

```bash
python Advanced_Consultation_MCP_Server/run_full_consultation.py \
  --consultation "My Consultation Name" \
  --question "Your question here?"
```

---

### Option 2: Ask Me (AI Assistant) to Help

You can simply ask me in Cursor:

```
"Start a new consultation called 'Database Decision' asking 'Should I use PostgreSQL or MongoDB?'"
```

I'll help you run the scripts and guide you through each stage!

---

## 📂 Where Files Are Saved

All consultations are saved in:

```
<project_root>/
└── Advanced_Consultations/
    └── 001_<Consultation Name>/
        ├── 00_Initial_Request.md                  # User's initial request (Stage 0)
        ├── 01_Initial_User_System_Prompt.md        # Generated prompt (Stage 1)
        ├── 02_Context_Files.md                    # Context files list
        ├── 03_Original_Raw_Output_from_Gemini3Pro.md  # Raw response (Stage 2)
        └── 04_Recommendations.md                 # Recommendations (Stage 3)
```

---

## 🎯 Typical Workflow

1. **Capture initial request** using Stage 0 or ask me to start a consultation
2. **Review the captured request** in `00_Initial_Request.md`
3. **Run Stage 1** to generate structured prompt (or it runs automatically)
4. **Review the generated prompt** in `01_Initial_User_System_Prompt.md`
5. **Optionally add context files** to `02_Context_Files.md`
6. **Run Stage 2** to get Gemini 3 Pro's comprehensive response
7. **Run Stage 3** to extract structured recommendations
8. **Review recommendations** in `04_Recommendations.md`

---

## 💡 Tips for Using in Cursor

- **Ask me to run scripts**: Just tell me what consultation you want to run
- **I can read results**: I can read and summarize the generated files
- **Iterative refinement**: You can modify `02_Context_Files.md` and re-run Stage 2
- **Multiple consultations**: Each gets its own numbered folder automatically

---

## ⚙️ Configuration

Make sure you have:

1. **Google Cloud credentials** set up:
   ```bash
   gcloud auth application-default login
   ```

2. **Environment variables** (if needed):
   ```bash
   $env:GOOGLE_CLOUD_PROJECT = "vk-genai"
   $env:GOOGLE_CLOUD_LOCATION = "global"
   ```

3. **Dependencies** installed:
   ```bash
   pip install google-genai tenacity
   ```

---

## ❓ Need Help?

Just ask me in Cursor! I can:
- Run consultations for you
- Explain the results
- Help troubleshoot issues
- Guide you through the workflow

**Example:**
- "Start a consultation about database architecture"
- "What recommendations did we get from the last consultation?"
- "Run Stage 2 for the consultation in folder 001_Database_Decision"

That's it! Simple and direct. No Claude Desktop needed! 🎉

