# 🚀 Quick Start Guide

Get the Advanced Consultation MCP Server running in 5 minutes!

---

## Step 1: Install (2 minutes)

```bash
# Navigate to MCP server directory
cd Advanced_Consultation_MCP_Server/mcp_server

# Install the package
pip install -e .

# Install dependencies (if not already installed)
pip install mcp pydantic google-genai tenacity
```

---

## Step 2: Configure Claude Desktop (1 minute)

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`

**macOS:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this configuration (update the `cwd` path to your project):

```json
{
  "mcpServers": {
    "advanced-consultation": {
      "command": "python",
      "args": ["-m", "advanced_consultation_mcp.server"],
      "cwd": "/path/to/your/project/.tools/advanced_consultation_mcp_server/mcp_server"
    }
  }
}
```

**Important:** 
- Update the `cwd` path to match your actual project location
- Use forward slashes `/` or escaped backslashes `\\` on Windows
- Ensure the path points to the `mcp_server` directory

---

## Step 3: Restart Claude Desktop (30 seconds)

1. Close Claude Desktop completely
2. Reopen Claude Desktop
3. Check for MCP indicator in Claude Desktop

---

## Step 4: Test (1 minute)

In Claude Desktop, try:

```
List all consultations using the list_consultations tool
```

Or start a test consultation:

```
Start a new advanced consultation named "Test" with the question "What is API design?"
```

---

## ✅ You're Done!

The MCP server is now integrated and ready to use!

---

## 🔍 Troubleshooting

**MCP server not showing?**
- Check JSON syntax (no trailing commas)
- Verify `cwd` path is correct
- Restart Claude Desktop completely
- Check Claude Desktop logs for errors

**Script errors?**
- Ensure scripts are in `Advanced_Consultation_MCP_Server/` directory
- Verify Python can find the scripts
- Check Google Cloud credentials are configured

**Need more help?**
- See [SETUP_AND_TEST.md](SETUP_AND_TEST.md) for detailed instructions
- Check [README.md](README.md) for full documentation

---

## 📚 Next Steps

- Run a full consultation via MCP tools
- Review generated files in `Advanced_Consultations/` folder
- Integrate into your workflow

Happy consulting! 🎉

