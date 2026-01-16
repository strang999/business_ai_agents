# Trading Prediction Agent - Архітектура

## 🎯 Мета
Створити AI-агента для прогнозування в трейдингу на основі локальних LLM моделей та спеціалізованих forecast моделей.

---

## 🛠️ Tech Stack

### Core Framework
- **LangGraph** - для побудови state machine агента
- **LangChain** - для інтеграцій та чейнів
- **Python 3.11+**

### Models
#### LLM (Local)
- **Qwen2.5-14B-Instruct** - для аналізу ринку та reasoning
- **DeepSeek-Coder-7B** - для технічного аналізу
- **Llama 3.1 8B** - легка модель для швидких рішень

#### Prediction Models
- **TimeGPT** (Nixtla) - foundation model для часових рядів
- **N-BEATS** / **N-HiTS** - neural forecast
- **Prophet** (Meta) - baseline forecasting

### Data Stack
- **TimescaleDB** / **PostgreSQL** - зберігання часових рядів
- **ChromaDB** / **Qdrant** - векторна БД для RAG
- **Redis** - кешування та state management

### Trading Data
- **CCXT** - підключення до криптобірж
- **yfinance** - stock market data
- **Alpha Vantage** / **Polygon.io** - market data APIs
- **NewsAPI** / **Sentiment Analysis** - новини та настрої

---

## 🏗️ Архітектура агента (LangGraph State Machine)

```
[START] 
   ↓
[1. Data Collection] ← Збір даних з ринку
   ↓
[2. Data Processing] ← Feature engineering
   ↓
[3. LLM Analysis] ← Аналіз локальною моделлю
   ↓
[4. Prediction] ← Прогноз (TimeGPT/N-BEATS)
   ↓
[5. Risk Assessment] ← Оцінка ризиків
   ↓
[6. Decision Making] ← Фінальне рішення
   ↓
[END] → Output: {action, confidence, reasoning}
```

### Nodes Detail

#### Node 1: Data Collector
```python
def collect_market_data(state):
    """
    - OHLCV data (Open, High, Low, Close, Volume)
    - Technical indicators (RSI, MACD, Bollinger Bands)
    - News sentiment
    - Order book depth (опціонально)
    """
    return {
        "market_data": {...},
        "indicators": {...},
        "sentiment": {...}
    }
```

#### Node 2: Feature Engineer
```python
def process_features(state):
    """
    - Normalization
    - Time-based features (hour, day, week patterns)
    - Lagged features
    - Rolling statistics
    """
    return {"features": processed_df}
```

#### Node 3: LLM Analyst (Qwen/DeepSeek)
```python
def llm_analysis(state):
    """
    Prompt до локальної моделі:
    - Аналіз поточної ринкової ситуації
    - Виявлення патернів
    - Генерація гіпотез про рух ціни
    """
    llm = Ollama(model="qwen2.5:14b")
    analysis = llm.invoke(prompt)
    return {"llm_insights": analysis}
```

#### Node 4: Prediction Model
```python
def predict_price(state):
    """
    Використання TimeGPT або N-BEATS:
    - Прогноз цін на different timeframes (1h, 4h, 1d)
    - Confidence intervals
    - Multiple scenarios
    """
    forecast = timegpt.forecast(data, horizon=24)
    return {"prediction": forecast}
```

#### Node 5: Risk Assessor
```python
def assess_risk(state):
    """
    - Position sizing (Kelly Criterion / Fixed %)
    - Stop-loss placement
    - Risk/Reward ratio
    - Portfolio exposure
    """
    return {"risk_metrics": {...}}
```

#### Node 6: Decision Maker
```python
def make_decision(state):
    """
    Combines:
    - LLM insights
    - Model predictions
    - Risk metrics
    
    Output:
    - Action: BUY/SELL/HOLD
    - Confidence: 0-100%
    - Reasoning: текстове пояснення
    - Citations: посилання на дані
    """
    return {
        "action": "BUY",
        "confidence": 78,
        "reasoning": "...",
        "stop_loss": 0.45,
        "take_profit": 0.52
    }
```

---

## 🔄 LangGraph Implementation

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

class TradingState(TypedDict):
    symbol: str
    market_data: dict
    features: dict
    llm_insights: str
    prediction: dict
    risk_metrics: dict
    decision: dict

# Create graph
workflow = StateGraph(TradingState)

# Add nodes
workflow.add_node("collect_data", collect_market_data)
workflow.add_node("process_features", process_features)
workflow.add_node("llm_analysis", llm_analysis)
workflow.add_node("predict", predict_price)
workflow.add_node("assess_risk", assess_risk)
workflow.add_node("decide", make_decision)

# Add edges
workflow.set_entry_point("collect_data")
workflow.add_edge("collect_data", "process_features")
workflow.add_edge("process_features", "llm_analysis")
workflow.add_edge("llm_analysis", "predict")
workflow.add_edge("predict", "assess_risk")
workflow.add_edge("assess_risk", "decide")
workflow.add_edge("decide", END)

# Compile
app = workflow.compile()
```

---

## 📊 Які моделі використати?

### 1. **LLM (Local)**
**Рекомендація: Qwen2.5-14B-Instruct**
- ✅ Чудова якість reasoning
- ✅ Підтримка довгого контексту (32K tokens)
- ✅ Швидка на GPU (RTX 3090/4090)
- ✅ Безкоштовна

**Альтернативи:**
- DeepSeek-Coder-7B (для технічного аналізу)
- Llama 3.1 8B (легша, швидша)
- Mistral 7B (добрий баланс)

### 2. **Forecasting Models**

**Option A: TimeGPT (Nixtla)**
- Foundation model для часових рядів
- Zero-shot forecasting
- API або self-hosted
- SOTA results на benchmark датасетах

**Option B: N-BEATS / N-HiTS**
- Neural architecture для forecasting
- Інтерпретабельні результати
- Швидке навчання
- Open-source

**Option C: Prophet (Meta)**
- Baseline модель
- Проста у використанні
- Добре працює з seasonality
- Швидка

---

## 🎯 Мінімальний MVP

### Phase 1: Core Pipeline (1-2 тижні)
- [ ] Збір даних з CCXT (1 криптопара)
- [ ] Feature engineering (10 базових індикаторів)
- [ ] LLM analyst (Qwen2.5 через Ollama)
- [ ] Simple LSTM forecast або Prophet
- [ ] Basic decision logic
- [ ] Console output

### Phase 2: Enhancements (2-3 тижні)
- [ ] Додати TimeGPT/N-BEATS
- [ ] Risk management module
- [ ] Memory (ChromaDB для RAG)
- [ ] Backtesting framework
- [ ] Web UI (Streamlit/Gradio)

### Phase 3: Production (1-2 місяці)
- [ ] Multiple assets
- [ ] Real-time monitoring
- [ ] Alert system
- [ ] Performance tracking
- [ ] API endpoints

---

## 💡 Переваги цього підходу

### LangGraph замість простого LangChain:
✅ **State Management** - зрозуміле управління станом агента
✅ **Conditional Logic** - можна додати умови (наприклад, "якщо volatility > 5%, skip prediction")
✅ **Циклічні флоу** - агент може повертатися до попередніх кроків
✅ **Human-in-the-loop** - легко додати точки для ручного підтвердження
✅ **Debugging** - візуалізація графа, простіше дебажити

### Локальні моделі замість API:
✅ **Privacy** - дані не йдуть назовні
✅ **Cost** - безкоштовно після setup
✅ **Speed** - швидко на власному GPU
✅ **Customization** - можна дотренувати на своїх даних

---

## 🚀 Quick Start Example

```bash
# 1. Install dependencies
pip install langgraph langchain ollama ccxt pandas ta newsapi-python

# 2. Run Ollama with Qwen
ollama pull qwen2.5:14b

# 3. Install TimeGPT or Prophet
pip install nixtla prophet

# 4. Run agent
python trading_agent.py --symbol BTC/USDT
```

---

## 📚 Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Nixtla TimeGPT](https://docs.nixtla.io/)
- [CCXT Documentation](https://docs.ccxt.com/)
- [Qwen2.5 Model Card](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct)

---

## ⚠️ Важливі notes для кола

1. **Не обіцяй 100% accuracy** - trading prediction це probabilistic
2. **Наголошуй на risk management** - це критично
3. **Mention backtesting** - будь-яка стратегія має бути протестована
4. **Regulatory compliance** - якщо це для клієнтів, треба дотримуватись правил
5. **Latency matters** - для HFT треба інша архітектура

---

## 🎤 Talking Points для кола

**"Я вже робив подібний підхід в ZIRA, але для trading prediction:"**

1. **Architecture**: "Використав LangGraph для побудови multi-step agent pipeline. Це дає змогу мати чіткий state machine з умовними переходами."

2. **Models**: "Комбінація локальних LLM (Qwen2.5) для reasoning + спеціалізовані forecast моделі (TimeGPT/N-BEATS) для прогнозів цін."

3. **Data Pipeline**: "CCXT для real-time даних з бірж, feature engineering з технічними індикаторами, та sentiment analysis з новин."

4. **Risk Management**: "Обов'язковий модуль для position sizing, stop-loss placement, та portfolio exposure tracking."

5. **Backtesting**: "Будь-яка торгова стратегія має бути протестована на історичних даних перед production."

6. **Key Differentiator**: "Локальні моделі = privacy, cost efficiency, та можливість кастомізації під конкретного клієнта."
