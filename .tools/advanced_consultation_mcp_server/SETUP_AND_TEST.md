# 🔧 Advanced Consultation MCP Server - Setup & Testing Guide

This guide will help you set up and test the Advanced Consultation MCP Server.

---

## 📋 Prerequisites

1. **Python 3.10+** installed
2. **Google Cloud credentials** configured (for Gemini 3 Pro API)
3. **Claude Desktop** installed (or another MCP client)
4. **Dependencies** installed (see below)

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
# Navigate to the MCP server directory
cd Advanced_Consultation_MCP_Server/mcp_server

# Install the MCP server package
pip install -e .

# Install required dependencies for the consultation scripts
pip install google-genai tenacity
```

### Step 2: Verify Scripts Location

The MCP server expects the consultation scripts to be in the parent directory:

```
Advanced_Consultation_MCP_Server/
├── mcp_server/
│   └── advanced_consultation_mcp/
│       └── server.py
├── 01_Understand_Context_Create_Prompt.py
├── 02_Fetch_Gemini_Response.py
├── 03_Extract_Detailed_Recommendations.py
└── run_full_consultation.py
```

### Step 3: Configure Environment Variables

Set up Google Cloud credentials:

```bash
# Windows PowerShell
$env:GOOGLE_CLOUD_PROJECT = "vk-genai"
$env:GOOGLE_CLOUD_LOCATION = "global"

# Or add to your .env file or system environment
```

For Vertex AI authentication, ensure you're logged in:

```bash
gcloud auth application-default login
```

### Step 4: Configure Claude Desktop

Edit your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the following configuration:

```json
{
  "mcpServers": {
    "advanced-consultation": {
      "command": "python",
      "args": ["-m", "advanced_consultation_mcp.server"],
      "cwd": "C:\\_VK_Code\\00_2026_Priority\\20-Gemini-Wrapper-Interface\\Advanced_Consultation_MCP_Server\\mcp_server"
    }
  }
}
```

**Important:** Update the `cwd` path to match your actual project location.

### Step 5: Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP server.

---

## 🧪 Testing the MCP Server

### Test 1: Direct Script Test (Recommended First)

Before testing via MCP, test the scripts directly:

```bash
# Navigate to project root
cd C:\_VK_Code\00_2026_Priority\20-Gemini-Wrapper-Interface

# Test Stage 1
python Advanced_Consultation_MCP_Server/01_Understand_Context_Create_Prompt.py \
  --consultation "Test Consultation" \
  --question "What are the best practices for API design?"

# Check the output folder
dir Advanced_Consultations\001_Test_Consultation
```

### Test 2: MCP Server Standalone Test

Test the MCP server directly (without Claude Desktop):

```bash
cd Advanced_Consultation_MCP_Server/mcp_server
python -m advanced_consultation_mcp.server
```

You should see it waiting for input via stdin. Press Ctrl+C to exit.

### Test 3: MCP Inspector Test

Use the MCP Inspector tool to test the server:

```bash
# Install MCP Inspector (if not already installed)
npm install -g @modelcontextprotocol/inspector

# Run inspector
npx @modelcontextprotocol/inspector python -m advanced_consultation_mcp.server
```

This will open a web interface where you can test all the tools.

### Test 4: Test Script

Run the provided test script:

```bash
python Advanced_Consultation_MCP_Server/test_mcp_server.py
```

### Test 5: Claude Desktop Test

1. **Open Claude Desktop**
2. **Check MCP Status**: Look for "MCP" indicator in Claude Desktop
3. **Try a simple query**: 
   ```
   Use the list_consultations tool to see if there are any existing consultations
   ```
4. **Start a consultation**:
   ```
   Use start_advanced_consultation to create a new consultation named "Test API Design" 
   with the question "What are best practices for REST API design?"
   ```

---

## 🔍 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure you're in the correct directory and package is installed
cd Advanced_Consultation_MCP_Server/mcp_server
pip install -e .
```

### Issue: "Script not found" errors

**Solution:** 
- Ensure scripts are in `Advanced_Consultation_MCP_Server/` directory (parent of `mcp_server/`)
- Check file paths in the MCP server configuration

### Issue: Gemini API errors

**Solution:**
```bash
# Verify Google Cloud credentials
gcloud auth application-default login

# Check environment variables
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_CLOUD_LOCATION

# Test Gemini API directly
python -c "from google import genai; client = genai.Client(vertexai=True); print('OK')"
```

### Issue: MCP server not appearing in Claude Desktop

**Solutions:**
1. Check `claude_desktop_config.json` path is correct
2. Verify JSON syntax is valid (no trailing commas)
3. Restart Claude Desktop completely
4. Check Claude Desktop logs:
   - **Windows:** `%APPDATA%\Claude\logs\`
   - **macOS:** `~/Library/Logs/Claude/`

### Issue: Timeout errors

**Solution:**
- Stage 1 typically takes 5-10 minutes
- Stage 2 can take 10-15 minutes
- Stage 3 usually takes 5-10 minutes
- Full consultation can take 30-45 minutes total

If timeouts occur, you can run stages individually via MCP tools.

---

## 📝 Available MCP Tools

Once connected, you'll have access to these tools:

1. **`start_advanced_consultation`** - Stage 1: Create consultation and generate prompt
2. **`fetch_consultation_response`** - Stage 2: Get Gemini 3 Pro response
3. **`extract_consultation_recommendations`** - Stage 3: Extract recommendations
4. **`run_full_consultation`** - Run all three stages automatically
5. **`list_consultations`** - List all available consultations

---

## 🎯 Example Usage in Claude Desktop

Once the MCP server is connected, you can use it like this:

```
You: Start a new consultation called "Database Architecture Decision" 
     asking "Should I use PostgreSQL or MongoDB for my project?"

Claude: I'll start the consultation for you using the start_advanced_consultation tool...
[Tool executes Stage 1]

You: Now fetch the Gemini response for that consultation.

Claude: I'll fetch the response using the fetch_consultation_response tool...
[Tool executes Stage 2]

You: Extract the recommendations from the consultation.

Claude: I'll extract the recommendations using extract_consultation_recommendations...
[Tool executes Stage 3]
```

---

## ✅ Verification Checklist

- [ ] Dependencies installed (`pip install -e .` successful)
- [ ] Google Cloud credentials configured
- [ ] Environment variables set (GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION)
- [ ] Scripts exist in correct location
- [ ] Claude Desktop config updated
- [ ] Claude Desktop restarted
- [ ] MCP server appears in Claude Desktop
- [ ] Direct script test successful
- [ ] MCP tools accessible in Claude Desktop

---

## 📚 Next Steps

1. Try a simple consultation via Claude Desktop
2. Review the generated files in `Advanced_Consultations/` folder
3. Experiment with adding context files
4. Integrate with your workflow

For more details, see the main [README.md](README.md).

