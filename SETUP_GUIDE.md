# Quick Setup Guide for New Laptop

This guide will help you set up and run this AI agents project on a new laptop quickly.

## Prerequisites

- **Python 3.10+** (recommended: Python 3.11)
- **Git** installed
- **API Keys** for the services you plan to use

## Step 1: Clone the Repository

```bash
git clone https://github.com/strang999/business_ai_agents.git
cd business_ai_agents
```

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv myenv

# Activate it
# On macOS/Linux:
source myenv/bin/activate

# On Windows:
myenv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Install additional CrewAI tools
pip install 'crewai[tools]'
```

## Step 4: Configure Environment Variables

Create a `.env` file in the root directory with your API keys:

```env
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
COMPOSIO_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
SERPER_API_KEY=...
```

**Important:** Never commit the `.env` file to git. Use `.env.example` as a template.

## Step 5: Run the Project

### Option A: Use the Unified Launcher

```bash
python launcher.py
```

### Option B: Run Individual Projects

#### Lead Generation

```bash
streamlit run lead_gen/app.py
```

#### Startup Validator

```bash
streamlit run startup_validator/app.py
```

#### Deep Research

```bash
streamlit run deep_research/app.py
```

#### Data Prognose (Time Series Forecasting)

```bash
cd data_prognose
streamlit run app.py
```

#### Warehouse Forecast

```bash
cd warehouse_forecast
python main.py
```

#### AI Mentor (Full-stack app)

```bash
cd ai-mentor/apps/api
pip install -r requirements.txt
python main.py
```

## Project Structure

- **`agents/`** - Collection of various AI agents (sales, marketing, research, etc.)
- **`ai-mentor/`** - Full-stack AI mentoring application (Python + Next.js)
- **`data_prognose/`** - Time series forecasting with Chronos models
- **`warehouse_forecast/`** - Multi-agent warehouse forecasting system
- **`trading_agent/`** - Trading agent architecture documentation
- **`lead_gen/`** - Lead generation system
- **`startup_validator/`** - Startup idea validation system
- **`deep_research/`** - Deep research engine
- **`social_media/`** - Content calendar generator
- **`real_estate/`** - Real estate intelligence system
- **`sales_qualifier/`** - AI sales receptionist

## Troubleshooting

### Missing Dependencies

If you encounter import errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
pip install -r requirements_lock.txt  # For exact versions
```

### API Key Issues

- Verify your API keys are correctly set in the `.env` file
- Check that the `.env` file is in the root directory
- Ensure there are no extra spaces or quotes around the keys

### Port Already in Use

If Streamlit says port 8501 is in use:

```bash
streamlit run app.py --server.port 8502
```

## Additional Setup for Specific Projects

### Data Prognose

See `data_prognose/QUICKSTART.md` for detailed setup instructions.

### Warehouse Forecast

See `warehouse_forecast/INSTALL.md` for installation guide.

### AI Mentor

Requires Node.js for the frontend:

```bash
cd ai-mentor/apps/web
npm install
npm run dev
```

## Notes

- The `.gitignore` is configured to exclude sensitive files, output files, and virtual environments
- Generated output files (JSON results, CSVs) are not tracked in git
- Database files in `db/` are excluded from version control

## Quick Reference

| Project            | Command                                    | Port |
| ------------------ | ------------------------------------------ | ---- |
| Launcher           | `python launcher.py`                       | CLI  |
| Lead Gen           | `streamlit run lead_gen/app.py`            | 8501 |
| Startup Validator  | `streamlit run startup_validator/app.py`   | 8501 |
| Deep Research      | `streamlit run deep_research/app.py`       | 8501 |
| Data Prognose      | `cd data_prognose && streamlit run app.py` | 8501 |
| Warehouse Forecast | `cd warehouse_forecast && python main.py`  | CLI  |

## Support

For detailed documentation on each project, check the README files in their respective directories.
