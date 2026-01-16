# ⚡ QUICKSTART - Trading Agent

Get the trading agent running in 5 minutes!

---

## 🚀 3-Step Setup

### Step 1: Install Dependencies (1 min)

```bash
# Navigate to project
cd trading_agent

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Configure API Key (1 min)

```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your OpenRouter API key:
# OPENAI_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
```

**Get OpenRouter API Key:**
1. Go to https://openrouter.ai/
2. Sign up / Log in
3. Go to "Keys" section
4. Create new key
5. Copy to `.env` file

### Step 3: Run! (1 min)

```bash
# Option 1: Use launcher
python run.py

# Option 2: Direct
streamlit run app.py
```

**That's it!** 🎉

Browser will open at `http://localhost:8501`

---

## 🎯 First Analysis

1. **Select Trading Pair:** BTC/USDT
2. **Choose Timeframe:** 4h
3. **Click:** "Run Analysis"
4. **Wait:** ~30 seconds for 7-step analysis
5. **Review:** Decision, confidence, risk parameters

---

## 🤖 Using Local Models (Optional)

Want to run 100% locally without API costs?

### Install Ollama

**Windows:**
```bash
# Download from ollama.ai and install
# Then pull model:
ollama pull qwen2.5:14b
```

### Update app.py

Change the `get_llm()` function:

```python
# Before (uses API)
from langchain_openai import ChatOpenAI
def get_llm(temperature=0.3):
    return ChatOpenAI(
        model="deepseek/deepseek-chat",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )

# After (uses local Ollama)
from langchain_community.llms import Ollama
def get_llm(temperature=0.3):
    return Ollama(
        model="qwen2.5:14b",
        temperature=temperature
    )
```

**Benefits:**
- ✅ Free (no API costs)
- ✅ Private (data stays local)
- ✅ Fast (no network latency)

---

## 📊 Understanding the Output

### Decision Summary
```
Decision: 🟢 BUY
Confidence: 78.5%
Current Price: $45,000.00
24h Change: +1.12%
```

- **Decision:** BUY/SELL/HOLD recommendation
- **Confidence:** How certain the agent is (0-100%)
- **Price:** Current market price
- **Change:** 24-hour price movement

### Risk Management
```
Stop Loss: $44,000
Take Profit: $46,500
Position Size: 2%
```

- **Stop Loss:** Exit if price goes down (limit loss)
- **Take Profit:** Target exit for profit
- **Position Size:** How much of portfolio to risk

### Analysis Tabs
- **Final Reasoning:** Complete decision explanation
- **Technical:** Chart analysis, indicators, patterns
- **Fundamental:** News sentiment, market psychology
- **Market Context:** Overall market conditions
- **Prediction:** Price forecast with reasoning

---

## 🔧 Troubleshooting

### "OPENAI_API_KEY not found"
**Fix:** Make sure `.env` file exists and contains:
```
OPENAI_API_KEY=sk-or-v1-your-key-here
```

### "Module not found"
**Fix:** Install dependencies:
```bash
pip install -r requirements.txt
```

### "Streamlit command not found"
**Fix:** Install streamlit:
```bash
pip install streamlit
```

### Slow response / Timeout
**Fix:** 
1. Check internet connection
2. Verify API key is valid
3. Try local model (Ollama) instead

### "Error during analysis"
**Fix:**
1. Check API key balance on OpenRouter
2. Verify symbol format (e.g., "BTC/USDT")
3. Look at error details in expanded section

---

## 🎓 Next Steps

### Learn More
- Read [`README.md`](README.md) - Full documentation
- Read [`ARCHITECTURE.md`](ARCHITECTURE.md) - System design
- Read [`LOCAL_MODELS_GUIDE.md`](LOCAL_MODELS_GUIDE.md) - Local setup

### Customize
- Modify prompts in `app.py`
- Add new technical indicators in `utils.py`
- Change UI layout in Streamlit sections

### Extend
- Add real data (CCXT integration)
- Implement backtesting
- Create alert system
- Build REST API

---

## 📞 Need Help?

**Check these files:**
- `PROJECT_SUMMARY.md` - What we built
- `PRESENTATION.md` - Key talking points
- `TODO.md` - Roadmap and features

**Common Questions:**

**Q: Can I use GPT-4 instead of DeepSeek?**
A: Yes! Change model name in `get_llm()`:
```python
model="openai/gpt-4-turbo"
```

**Q: How do I add more trading pairs?**
A: Edit the sidebar section in `app.py`:
```python
symbol = st.selectbox(
    "Trading Pair",
    ["BTC/USDT", "ETH/USDT", "YOUR/PAIR"],
)
```

**Q: Can it trade automatically?**
A: Not yet. Current version is decision support only. Auto-trading requires CCXT integration and risk controls.

**Q: Is this financial advice?**
A: No! This is an AI tool for analysis. Always do your own research.

---

## ✅ Verification Checklist

Make sure everything works:

- [ ] Dependencies installed (`pip list | grep streamlit`)
- [ ] `.env` file created with API key
- [ ] Streamlit app starts without errors
- [ ] Can select trading pair and timeframe
- [ ] "Run Analysis" button works
- [ ] All 7 steps complete successfully
- [ ] Results display correctly
- [ ] Can download report

**All checked?** You're ready! 🚀

---

## 🎯 For Your Demo Call

**Before the call:**
1. Test run the analysis once
2. Have browser ready at localhost:8501
3. Open `PRESENTATION.md` for talking points
4. Prepare to show `app.py` code

**During demo:**
1. Show UI and explain inputs (30 sec)
2. Run analysis and show progress (60 sec)
3. Explain each step as it completes (90 sec)
4. Show final results and reasoning (60 sec)
5. Open code to show architecture (60 sec)

**Total demo time:** ~5 minutes

---

## 🔥 Pro Tips

1. **Speed Up:** Use lighter model (llama3.1:8b) for faster demos
2. **Wow Factor:** Run on multiple timeframes simultaneously
3. **Technical Depth:** Show the graph construction code
4. **Risk Focus:** Emphasize stop-loss and position sizing
5. **Flexibility:** Mention can use ANY LLM (GPT-4, Claude, local)

---

**Ready to impress!** 🎤

Move fast, break nothing, ship features. 🚀
