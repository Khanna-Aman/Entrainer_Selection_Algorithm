# Advanced Consultation MCP Server - LLM Configuration Analysis

## Summary
All scripts use **Gemini 3 Pro** (`gemini-3-pro-preview`) exclusively via the `Gemini3ProWrapper` class. The wrapper provides consistent configuration across all stages.

## LLM Configuration Table

| File Name | LLM Model | Temperature | Max Tokens | Top P | Thinking Level | Timeout (seconds) | Tools | Safety Settings |
|-----------|-----------|-------------|------------|-------|----------------|-------------------|-------|-----------------|
| `00_Capture_Initial_Request.py` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| `01_Understand_Context_Create_Prompt.py` | gemini-3-pro-preview | 0 | 65535 | 0.95 | HIGH | 600 (10 min) | Google Search | All OFF |
| `02_Fetch_Gemini_Response.py` | gemini-3-pro-preview | 0 | 65535 | 0.95 | HIGH | 900 (15 min) | Google Search | All OFF |
| `03_Extract_Detailed_Recommendations.py` | gemini-3-pro-preview | 0 | 65535 | 0.95 | HIGH | 600 (10 min) | Google Search | All OFF |
| `run_full_consultation.py` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| `mcp_server/advanced_consultation_mcp/server.py` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

## Detailed Configuration

### Default Configuration (from `Gemini3ProWrapper`)
All LLM calls use the following configuration from `Re-Usable Components/04_LLM_Levers/llm_wrappers/gemini3_pro_wrapper.py`:

- **Model**: `gemini-3-pro-preview` (configurable via `GEMINI_MODEL` environment variable, defaults to `gemini-3-pro-preview`)
- **Max Output Tokens**: `65535` (hardcoded in wrapper)
- **Top P**: `0.95` (hardcoded in wrapper)
- **Google Search Tools**: Enabled (hardcoded in wrapper)
- **Safety Settings**: All categories set to `OFF` (hardcoded in wrapper)
  - `HARM_CATEGORY_HATE_SPEECH`: OFF
  - `HARM_CATEGORY_DANGEROUS_CONTENT`: OFF
  - `HARM_CATEGORY_SEXUALLY_EXPLICIT`: OFF
  - `HARM_CATEGORY_HARASSMENT`: OFF

### Script-Specific Settings

#### `01_Understand_Context_Create_Prompt.py`
- **Purpose**: Stage 1 - Analyze initial request and generate structured prompt
- **Temperature**: `0` (deterministic responses)
- **Thinking Level**: `HIGH`
- **Timeout**: `600 seconds` (10 minutes)
- **Code Location**: Lines 409-415

```413:414:Advanced_Consultation_MCP_Server/01_Understand_Context_Create_Prompt.py
            temperature=0,  # Match 01_Gemini3_Pro.txt: deterministic responses
            timeout_seconds=600  # 10 minutes for complex analysis
```

#### `02_Fetch_Gemini_Response.py`
- **Purpose**: Stage 2 - Fetch comprehensive response using generated prompt
- **Temperature**: `0` (deterministic responses)
- **Thinking Level**: `HIGH`
- **Timeout**: `900 seconds` (15 minutes)
- **Code Location**: Lines 276-283

```281:282:Advanced_Consultation_MCP_Server/02_Fetch_Gemini_Response.py
            temperature=0,  # Match 01_Gemini3_Pro.txt: deterministic responses
            timeout_seconds=900  # 15 minutes for comprehensive responses
```

#### `03_Extract_Detailed_Recommendations.py`
- **Purpose**: Stage 3 - Extract structured recommendations from raw response
- **Temperature**: `0` (deterministic responses)
- **Thinking Level**: `HIGH`
- **Timeout**: `600 seconds` (10 minutes)
- **Code Location**: Lines 290-296

```294:295:Advanced_Consultation_MCP_Server/03_Extract_Detailed_Recommendations.py
            temperature=0,  # Match 01_Gemini3_Pro.txt: deterministic responses
            timeout_seconds=600  # 10 minutes
```

## Notes

1. **Model Consistency**: All scripts use the same model (`gemini-3-pro-preview`) and wrapper (`Gemini3ProWrapper`), ensuring consistent behavior across stages.

2. **Deterministic Responses**: Temperature is set to `0` in all stages to ensure deterministic, reproducible responses.

3. **High Thinking Level**: All stages use `thinking_level="HIGH"` for deep analysis capabilities.

4. **Maximum Token Output**: All stages use the maximum supported output tokens (`65535`) to allow for comprehensive responses.

5. **No Direct LLM Calls**: The following scripts do not make direct LLM calls:
   - `00_Capture_Initial_Request.py` - Only handles file I/O
   - `run_full_consultation.py` - Orchestrator script that calls other stages
   - `mcp_server/advanced_consultation_mcp/server.py` - MCP server that invokes stage scripts

6. **Configuration Source**: The wrapper configuration follows the specifications from `01_Gemini3_Pro.txt` as referenced in code comments.

7. **Environment Variable Override**: The model name can be overridden via the `GEMINI_MODEL` environment variable, though all documentation recommends using `gemini-3-pro-preview`.



