# Trading Agent - Architecture & Flow

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING AGENT SYSTEM                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                            │
│  • Trading Pair (BTC/USDT, ETH/USDT, etc.)                  │
│  • Timeframe (15m, 1h, 4h, 1d, 1w)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   LANGGRAPH PIPELINE                         │
│                  (State Machine Flow)                        │
└─────────────────────────────────────────────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       │  TradingState (Shared State)   │
       └───────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼

┌──────────┐    ┌──────────┐    ┌──────────────┐
│   Data   │    │ Analysis │    │  Decision    │
│ Ingestion│───▶│ Pipeline │───▶│   Making     │
└──────────┘    └──────────┘    └──────────────┘
```

---

## 🔄 LangGraph Pipeline Flow

```
                    [START]
                       │
                       ▼
        ╔══════════════════════════════╗
        ║   Node 1: Data Collection    ║
        ║   ─────────────────────────  ║
        ║   • Fetch OHLCV data         ║
        ║   • Calculate indicators     ║
        ║   • Get sentiment data       ║
        ╚══════════════════════════════╝
                       │
                       ▼
        ╔══════════════════════════════╗
        ║  Node 2: Technical Analysis  ║
        ║  ──────────────────────────  ║
        ║  LLM: Qwen/DeepSeek          ║
        ║  • Analyze indicators        ║
        ║  • Identify patterns         ║
        ║  • Determine trend           ║
        ╚══════════════════════════════╝
                       │
                       ▼
        ╔══════════════════════════════╗
        ║ Node 3: Fundamental Analysis ║
        ║ ───────────────────────────  ║
        ║ LLM: Market Analyst          ║
        ║ • News sentiment             ║
        ║ • Fear & Greed index         ║
        ║ • Market psychology          ║
        ╚══════════════════════════════╝
                       │
                       ▼
        ╔══════════════════════════════╗
        ║  Node 4: Market Context      ║
        ║  ─────────────────────────   ║
        ║  LLM: Strategist             ║
        ║  • Market phase              ║
        ║  • Volatility level          ║
        ║  • Trading conditions        ║
        ╚══════════════════════════════╝
                       │
                       ▼
        ╔══════════════════════════════╗
        ║   Node 5: Price Prediction   ║
        ║   ────────────────────────   ║
        ║   Model: LLM / TimeGPT       ║
        ║   • Forecast prices          ║
        ║   • Confidence intervals     ║
        ║   • Trend direction          ║
        ╚══════════════════════════════╝
                       │
                       ▼
        ╔══════════════════════════════╗
        ║  Node 6: Risk Assessment     ║
        ║  ──────────────────────────  ║
        ║  • Calculate stop-loss       ║
        ║  • Calculate take-profit     ║
        ║  • Position sizing           ║
        ║  • Risk/reward ratio         ║
        ╚══════════════════════════════╝
                       │
                       ▼
        ╔══════════════════════════════╗
        ║  Node 7: Decision Making     ║
        ║  ──────────────────────────  ║
        ║  LLM: Chief Trading Officer  ║
        ║  • Synthesize all analysis   ║
        ║  • Make BUY/SELL/HOLD        ║
        ║  • Provide reasoning         ║
        ╚══════════════════════════════╝
                       │
                       ▼
                    [END]
                       │
                       ▼
        ┌──────────────────────────────┐
        │      FINAL OUTPUT            │
        │  • Decision + Confidence     │
        │  • Entry/Exit points         │
        │  • Risk parameters           │
        │  • Detailed reasoning        │
        │  • Downloadable report       │
        └──────────────────────────────┘
```

---

## 🧠 State Management

### TradingState Object

```python
TradingState {
    # Input
    symbol: "BTC/USDT"
    timeframe: "4h"
    
    # Data (Node 1)
    market_data: {...}         # OHLCV
    indicators: {...}          # RSI, MACD, etc.
    sentiment: {...}           # News, social
    
    # Analysis (Nodes 2-4)
    technical_analysis: "..."  # LLM analysis
    fundamental_analysis: "..." # LLM insights
    market_context: "..."      # Market phase
    
    # Prediction (Node 5)
    price_prediction: {...}    # Forecast
    trend_prediction: "..."    # Direction
    
    # Risk (Node 6)
    risk_assessment: {...}     # Stop-loss, etc.
    position_sizing: {...}     # Size recommendation
    
    # Output (Node 7)
    decision: "BUY"           # Final call
    confidence: 78.5          # Percentage
    reasoning: "..."          # Explanation
    stop_loss: 44000
    take_profit: 46500
}
```

This state flows through all nodes, each adding their analysis!

---

## 🎯 Agent Roles

### 1. 📊 Data Collector
- **Role:** Market Data Engineer
- **Task:** Fetch real-time data
- **Output:** OHLCV + Indicators + Sentiment

### 2. 📉 Technical Analyst
- **Role:** Chart Pattern Expert
- **Model:** DeepSeek-Chat
- **Task:** Analyze technical indicators
- **Output:** Technical outlook

### 3. 📰 Fundamental Analyst
- **Role:** Market Psychologist
- **Model:** DeepSeek-Chat
- **Task:** Analyze news and sentiment
- **Output:** Fundamental view

### 4. 🌐 Market Strategist
- **Role:** Big Picture Thinker
- **Model:** DeepSeek-Chat
- **Task:** Understand market phase
- **Output:** Context and conditions

### 5. 🎯 Prediction Engine
- **Role:** Quantitative Analyst
- **Model:** LLM / TimeGPT
- **Task:** Forecast future prices
- **Output:** Price targets + confidence

### 6. ⚖️ Risk Manager
- **Role:** Risk Officer
- **Model:** DeepSeek-Chat
- **Task:** Calculate risk parameters
- **Output:** Stop-loss, position size

### 7. ✅ Chief Trading Officer
- **Role:** Final Decision Maker
- **Model:** DeepSeek-Chat
- **Task:** Synthesize everything
- **Output:** BUY/SELL/HOLD + reasoning

---

## 🔌 Data Sources (Production Ready)

### Current (MVP)
✅ Mock data generation
✅ Simulated indicators

### Future Integration
- [ ] **CCXT** - Crypto exchange data
- [ ] **yfinance** - Stock market data
- [ ] **TradingView** - Charts and indicators
- [ ] **NewsAPI** - Real-time news
- [ ] **Twitter API** - Social sentiment
- [ ] **Coinglass** - Liquidation data
- [ ] **Glassnode** - On-chain metrics

---

## 🤖 Model Architecture

### LLM Layer (Current)
```
DeepSeek-Chat (via OpenRouter)
├── Technical Analyst
├── Fundamental Analyst
├── Market Strategist
├── Prediction Engine (basic)
├── Risk Manager
└── Decision Maker
```

### Future: Specialized Models
```
Hybrid Architecture
├── LLM (Reasoning)
│   └── DeepSeek / Qwen / Llama
├── Forecasting (Predictions)
│   ├── TimeGPT (foundation model)
│   ├── N-BEATS (neural forecast)
│   └── Custom LSTM/Transformer
└── NLP (Sentiment)
    ├── FinBERT (financial sentiment)
    └── Twitter embeddings
```

---

## 📊 Decision Making Logic

```
                ┌─────────────┐
                │ All Analysis│
                └──────┬──────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Technical │  │Fundamental│  │  Risk    │
  │ Bullish? │  │ Positive? │  │ Accept?  │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │             │             │
       └─────────────┼─────────────┘
                     ▼
            ┌────────────────┐
            │  Voting Logic  │
            │ (Weighted Sum) │
            └────────┬───────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    [BUY]        [HOLD]       [SELL]
        │            │            │
        └────────────┼────────────┘
                     ▼
            ┌─────────────────┐
            │ Confidence Score│
            │    (0-100%)     │
            └─────────────────┘
```

---

## 🎨 UI Components

### Streamlit App Structure

```
HomePage
├── Header (Title + Description)
├── Sidebar
│   ├── Trading Pair Selector
│   ├── Timeframe Selector
│   └── Future Features List
├── Main Panel
│   ├── Run Analysis Button
│   ├── Progress Bar
│   ├── Step-by-Step Output
│   └── Final Results
│       ├── Decision Summary (Metrics)
│       ├── Risk Parameters
│       ├── Analysis Tabs
│       │   ├── Final Reasoning
│       │   ├── Technical
│       │   ├── Fundamental
│       │   ├── Market Context
│       │   └── Prediction
│       └── Download Report Button
```

---

## 🔐 Security & Privacy

### Current
- ✅ API keys in .env (not committed)
- ✅ Local execution (no external data leaks)

### Future
- [ ] Encrypted API key storage
- [ ] Rate limiting
- [ ] User authentication
- [ ] Audit logging
- [ ] Data encryption at rest

---

## 📈 Scalability Plan

### Phase 1: Single User (Current)
- Local Streamlit app
- One symbol at a time
- DeepSeek via OpenRouter

### Phase 2: Multi-Asset
- Analyze multiple pairs
- Portfolio view
- Comparison mode

### Phase 3: Production API
- REST API endpoints
- WebSocket updates
- Multiple concurrent users
- Redis caching

### Phase 4: Enterprise
- Multi-tenancy
- Custom model fine-tuning
- White-label deployment
- SLA guarantees

---

## ⚡ Performance Metrics

### Target Latency
- Data Collection: < 2s
- Technical Analysis: < 5s
- Fundamental Analysis: < 5s
- Prediction: < 3s
- Total Pipeline: < 20s

### Cost Optimization
- Cache market data (5 min TTL)
- Batch multiple requests
- Use cheaper models where possible
- Rate limit user requests

---

## 🧪 Testing Strategy

### Unit Tests
- [ ] Individual node functions
- [ ] Utility functions
- [ ] Data validation

### Integration Tests
- [ ] Full pipeline execution
- [ ] State transitions
- [ ] Error handling

### Backtesting
- [ ] Historical data validation
- [ ] Prediction accuracy
- [ ] Risk metrics verification

---

## 📚 Key Design Decisions

### Why LangGraph?
✅ State machine clarity
✅ Easy debugging
✅ Visual flow
✅ Conditional logic support
✅ Human-in-the-loop ready

### Why Multi-Agent?
✅ Separation of concerns
✅ Specialized expertise
✅ Easier to improve individual components
✅ Better reasoning through specialization

### Why Local LLMs (Future)?
✅ Privacy
✅ Cost efficiency at scale
✅ Customization
✅ No API rate limits

---

**Last Updated:** 2026-01-08
**Version:** 1.0 (MVP)
