# Plan: Skylix Bulk Lead Validator Agent

## 🎯 Objective
Build an AI agent system capable of processing a large Excel/CSV database (e.g., 500+ rows) to validate and enrich lead information.

**Input:** Excel file with `Company Name`, `City` (optional), `Industry` (optional).
**Output:** Enriched Excel with:
- ✅ **Website Status** (Active/Inactive)
- 📸 **Instagram URL**
- 📍 **Google Maps Link**
- ⭐ **Review Count & Rating**

## 🏗️ Architecture

We will build a **Streamlit App** (`bulk_validator/app.py`) with a "Batch Processing Pipeline".

### The Workflow (Per Row)
1.  **Search Phase (Serper API):**
    *   The agent performs a targeted Google search: `"{Company Name} {City} official website instagram google maps reviews"`
2.  **Extraction Phase (LLM - GPT-4o-mini):**
    *   Instead of fragile regex, we feed the top 5 search snippets to a cheap, fast LLM.
    *   **Prompt:** "Analyze these search results. Extract the Official Website, Instagram Profile, Google Maps URL, and Rating/Reviews. Return JSON."
3.  **Validation Phase (Optional Python Script):**
    *   Ping the website URL (HTTP GET) to ensure it returns status 200 (Site is live).

### ⚡ Performance Strategy
*   **Parallel Execution:** Processing 500 items sequentially would take ~1 hour (assuming 5s per item).
*   **Solution:** We will use Python's `ThreadPoolExecutor` to run **10-20 agents in parallel**.
*   **Estimated Time:** ~3-5 minutes for 500 items.

## 💰 Cost Estimation (for 500 leads)

| Resource | Usage Estimate | Unit Cost | Total Cost |
| :--- | :--- | :--- | :--- |
| **Google Search (Serper)** | ~1,500 queries (3 per lead max, often 1 is enough with smart prompting) | $50 / 50k queries | **~$1.50** (or Free tier) |
| **LLM (GPT-4o-mini)** | ~1M context tokens (Search results are verbose) | $0.15 / 1M tokens | **~$0.15** |
| **Total** | | | **~ $1.65** |

*Note: This is significantly cheaper than human VAs or premium data enrichment tools (ZoomInfo/Apollo).*

## 🛠️ Tech Stack
*   **UI:** Streamlit (for easy file upload & progress bar)
*   **Data:** Pandas (Excel read/write)
*   **Search:** SerperDevTool (Google Search API)
*   **Intelligence:** LangChain + OpenAI (GPT-4o-mini)
*   **Concurrency:** Python `concurrent.futures`

## 🚀 Implementation Steps
1.  Create `skylix_portfolio/bulk_validator/` directory.
2.  Build `app.py` with file uploader.
3.  Implement the `process_lead(row)` function with Search + LLM extraction.
4.  Add multi-threading for speed.
5.  Add "Download Enriched Excel" button.
