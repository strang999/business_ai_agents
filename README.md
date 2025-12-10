# AI Agent Portfolio

This directory contains a collection of production-ready AI agents.

## 🚀 Available Agents

### 1. 🎯 Lead Finder
**Location:** `lead_gen/app.py`
**Type:** Streamlit App
**Description:** Finds high-intent leads on Quora using Firecrawl (Search) and **DeepSeek-V3** (Extraction) for maximum intelligence at low cost. Exports to CSV and Google Sheets.
**Usage:** `streamlit run lead_gen/app.py`

### 2. 🏠 Real Estate Assistant
**Location:** `real_estate/bot.py` (CLI) & `real_estate/agent.py` (Streamlit)
**Type:** CLI Bot & Streamlit App
**Description:** 
- **CLI Bot:** A simulated WhatsApp bot that asks for user preferences and finds properties.
- **Streamlit App:** A full dashboard for searching properties and analyzing location trends.
**Usage:** 
- CLI: `python real_estate/bot.py`
- UI: `streamlit run real_estate/agent.py`

### 3. 📅 Content Calendar Creator
**Location:** `social_media/app.py`
**Type:** Streamlit App
**Description:** Generates a strategic 7-day social media content calendar using CrewAI and Claude 3.7 Sonnet.
**Usage:** `streamlit run social_media/app.py`

### 4. 📞 Sales Qualifier
**Location:** `sales_qualifier/agent.py`
**Type:** CLI Agent
**Description:** An AI receptionist ("Sarah") that qualifies inbound leads via a simulated phone conversation and saves them to a CRM.
**Usage:** `python sales_qualifier/agent.py`

### 5. 🚀 Startup Idea Validator
**Location:** `startup_validator/app.py`
**Type:** Streamlit App (CrewAI)
**Description:** A team of 4 AI agents (Analyst, Ecosystem Expert, Strategist, Investor) that validate startup ideas and generate reports.
**Usage:** `streamlit run startup_validator/app.py`

### 6. 🧠 Deep Research Agent
**Location:** `deep_research/app.py`
**Type:** Streamlit App (LangGraph)
**Description:** A stateful agent workflow that Plans, Researches, Writes, Reviews, and Revises content iteratively using a graph architecture.
**Usage:** `streamlit run deep_research/app.py`

## 🛠️ Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in a `.env` file:
   ```
   OPENAI_API_KEY=sk-...
   FIRECRAWL_API_KEY=fc-...
   COMPOSIO_API_KEY=...
   ANTHROPIC_API_KEY=sk-ant-...
   SERPER_API_KEY=...
   ```

3. Run the launcher to explore all agents:
   ```bash
   python launcher.py
   ```
