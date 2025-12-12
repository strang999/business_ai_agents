# Business AI Solutions Suite

A comprehensive collection of production-ready AI agents designed to automate critical business workflows. This suite leverages state-of-the-art LLMs (DeepSeek-V3, Claude 3.5 Sonnet, GPT-4o) and agentic frameworks (CrewAI, LangGraph) to deliver tangible ROI.

## 🚀 Solutions Suite

### 1. 🎯 Lead Acquisition Engine (`lead_gen`)
**Stack:** Streamlit, Firecrawl, DeepSeek-V3
**Function:** Autonomous high-intent lead generation system. Scrapes social platforms (e.g., Quora) for intent signals, extracts verified user profiles using DeepSeek-V3, and aggregates data for sales outreach.
**Output:** CSV / Google Sheets integration.

### 2. 🚀 Startup Validator (`startup_validator`)
**Stack:** CrewAI, Streamlit, SerperDevTool, DeepSeek-V3
**Function:** A multi-agent system comprising a Market Analyst, Ecosystem Expert, Business Strategist, and Investment Analyst. It autonomously validates business ideas, performs competitive analysis, and generates professional investment memos.

### 3. 🧠 Deep Research System (`deep_research`)
**Stack:** LangGraph, Streamlit, DeepSeek-V3
**Function:** An iterative research engine that plans, gathers, synthesizes, and reviews complex topics. Designed for generating high-depth reports and white papers without human intervention.

### 4. 📅 Content Strategy Engine (`social_media`)
**Stack:** CrewAI, Claude 3.5 Sonnet
**Function:** End-to-end social media management. Generates strategic 7-day content calendars tailored to industry trends and brand voice.

### 5. 🏠 Real Estate Intelligence (`real_estate`)
**Stack:** Python CLI / Streamlit
**Function:** Dual-interface property assistant. Includes a CLI-based WhatsApp simulator for natural language property queries and a visual dashboard for market trend analysis.

### 6. 📞 Sales Qualifier (`sales_qualifier`)
**Stack:** Python CLI
**Function:** AI-driven receptionist ("Sarah") capable of handling inbound inquiries, qualifying leads via natural conversation simulation, and logging data to CRM systems.

---

## 🛠️ Deployment & Setup

### Prerequisites
- Python 3.10+
- Verified API Keys for target LLM providers (OpenAI, Anthropic, OpenRouter) and utilities (Firecrawl, Serper).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/business_ai_agents.git
   cd business_ai_agents
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=sk-...
   FIRECRAWL_API_KEY=fc-...
   COMPOSIO_API_KEY=...
   ANTHROPIC_API_KEY=sk-ant-...
   SERPER_API_KEY=...
   ```

### Execution

**Unified Launcher:**
Access all agents via the central CLI dashboard:
```bash
python launcher.py
```

**Individual Execution:**
```bash
# Lead Acquisition
streamlit run lead_gen/app.py

# Startup Validator
streamlit run startup_validator/app.py

# Deep Research
streamlit run deep_research/app.py
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
