# Trading Prediction Agent 📈

Professional AI-powered trading analysis system using **LangGraph** for multi-step market analysis and trade predictions.

## 🎯 Features

### 7-Step Analysis Pipeline

1. **📊 Data Collection** - Market data, technical indicators, sentiment
2. **📉 Technical Analysis** - Chart patterns, indicators, support/resistance
3. **📰 Fundamental Analysis** - News sentiment, market psychology
4. **🌐 Market Context** - Overall market conditions and phase
5. **🎯 Price Prediction** - AI-powered price forecasting
6. **⚖️ Risk Assessment** - Position sizing, stop-loss, take-profit
7. **✅ Decision Making** - Final BUY/SELL/HOLD recommendation

### Key Capabilities

- ✅ Multi-agent architecture with specialized roles
- ✅ LangGraph state machine for reliable execution
- ✅ Comprehensive risk management
- ✅ Detailed reasoning and citations
- ✅ Professional Streamlit UI
- ✅ Downloadable analysis reports
- ✅ Real-time streaming of analysis steps

## 🛠️ Tech Stack

### Core Framework
- **LangGraph** - State machine orchestration
- **LangChain** - LLM integrations
- **Streamlit** - Web interface

### AI Models
- **DeepSeek-Chat** (via OpenRouter) - Multi-step reasoning
- **Future:** TimeGPT, N-BEATS for specialized forecasting

### Data Sources (Ready for Integration)
- **CCXT** - Cryptocurrency exchange APIs
- **yfinance** - Stock market data
- **TA-Lib** - Technical analysis indicators

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to trading_agent directory
cd trading_agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENAI_API_KEY=sk-or-v1-your-key-here
```

### 3. Run the Agent

```bash
# Start Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How to Use

1. **Select Trading Pair** - Choose from BTC/USDT, ETH/USDT, etc.
2. **Select Timeframe** - Pick analysis timeframe (15m, 1h, 4h, 1d, 1w)
3. **Run Analysis** - Click "Run Analysis" button
4. **Review Results** - See decision, confidence, and detailed reasoning
5. **Download Report** - Export full analysis as markdown

## 📊 Sample Output

```
Decision: 🟢 BUY
Confidence: 78.5%
Current Price: $45,000.00

Risk Management:
├─ Stop Loss: $44,000
├─ Take Profit: $46,500
└─ Position Size: 2%

Reasoning:
- Strong bullish momentum on 4h chart
- RSI showing healthy levels (55.3)
- Positive sentiment with ETF inflows
- Risk/reward ratio: 1:3
```

## 🏗️ Architecture

### LangGraph Flow

```
[START]
   ↓
[Data Collection] ← Fetch market data, indicators, sentiment
   ↓
[Technical Analysis] ← LLM analyzes charts and indicators
   ↓
[Fundamental Analysis] ← LLM analyzes news and sentiment
   ↓
[Market Context] ← Overall market conditions
   ↓
[Prediction] ← AI price forecasting
   ↓
[Risk Assessment] ← Calculate stop-loss, position sizing
   ↓
[Decision Maker] ← Final BUY/SELL/HOLD decision
   ↓
[END] → Output with reasoning
```

### State Management

Each node in the graph updates a shared `TradingState` that flows through:
- Market data and indicators
- Analysis from multiple AI agents
- Predictions and risk metrics
- Final decision with reasoning

## 🔧 Configuration Options

### Supported Trading Pairs (MVP)
- BTC/USDT
- ETH/USDT
- SOL/USDT
- BNB/USDT

### Timeframes
- 15m (Short-term scalping)
- 1h (Intraday trading)
- 4h (Swing trading)
- 1d (Daily trends)
- 1w (Long-term positions)

## 🚀 Production Roadmap

### Phase 1: MVP (Current) ✅
- [x] 7-step LangGraph pipeline
- [x] LLM-based analysis
- [x] Streamlit UI
- [x] Mock data simulation
- [x] Risk management logic
- [x] Report generation

### Phase 2: Live Data Integration
- [ ] CCXT integration for real-time data
- [ ] Live technical indicators calculation
- [ ] News API for sentiment
- [ ] Historical data storage (TimescaleDB)

### Phase 3: Advanced Models
- [ ] TimeGPT for time-series forecasting
- [ ] N-BEATS neural forecasting
- [ ] Custom LSTM/Transformer models
- [ ] Ensemble predictions

### Phase 4: Trading Features
- [ ] Backtesting framework
- [ ] Paper trading simulation
- [ ] Performance tracking
- [ ] Alert system (Telegram/Email)
- [ ] Portfolio management

### Phase 5: Enterprise
- [ ] Multi-asset support
- [ ] REST API endpoints
- [ ] WebSocket real-time updates
- [ ] User authentication
- [ ] Database for trade history

## 📁 Project Structure

```
trading_agent/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── README.md          # This file
└── (future additions)
    ├── nodes/         # Individual agent nodes
    ├── models/        # ML models (TimeGPT, etc.)
    ├── data/          # Data collectors and processors
    ├── utils/         # Helper functions
    └── tests/         # Unit tests
```

## 🎤 Key Differentiators

### Why This Approach?

1. **Multi-Agent Architecture** - Each step is a specialized agent
2. **LangGraph Reliability** - State machine ensures predictable flow
3. **Comprehensive Analysis** - Technical + Fundamental + Sentiment
4. **Risk-First Approach** - Always calculates stop-loss and position sizing
5. **Explainable AI** - Detailed reasoning for every decision
6. **Production Ready** - Easy to extend with real APIs

### Advantages Over Simple LLM Prompts

- ✅ Structured analysis pipeline
- ✅ Reproducible results
- ✅ Easy to debug and monitor
- ✅ Modular - swap any node/model
- ✅ Scalable to multiple assets

## 🎯 Use Cases

1. **Personal Trading** - Get AI-powered analysis before trades
2. **Portfolio Management** - Analyze multiple positions
3. **Research Tool** - Deep market analysis
4. **Learning** - Understand technical/fundamental analysis
5. **Backtesting** - Test strategies on historical data (coming soon)

## ⚠️ Disclaimer

**IMPORTANT:** This is an AI-powered analysis tool for educational and research purposes.

- ❌ NOT financial advice
- ❌ NOT guaranteed to be profitable
- ❌ NOT a replacement for human judgment
- ✅ Always do your own research (DYOR)
- ✅ Only invest what you can afford to lose
- ✅ Consult professional financial advisors

Trading cryptocurrencies and other financial instruments carries significant risk.

## 🤝 Contributing

This is a professional demonstration project. To adapt for your needs:

1. Replace mock data with real API calls (CCXT, yfinance)
2. Add specialized forecasting models (TimeGPT, Prophet)
3. Implement backtesting framework
4. Add your own technical indicators
5. Customize risk management rules

## 📚 Resources

### LangGraph
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)

### Trading APIs
- [CCXT Documentation](https://docs.ccxt.com/)
- [yfinance](https://github.com/ranaroussi/yfinance)
- [TA-Lib Python](https://github.com/TA-Lib/ta-lib-python)

### Forecasting Models
- [Nixtla TimeGPT](https://docs.nixtla.io/)
- [Meta Prophet](https://facebook.github.io/prophet/)
- [N-BEATS Paper](https://arxiv.org/abs/1905.10437)

## 📞 Support

For questions or issues:
- Check the code comments in `app.py`
- Review LangGraph documentation
- Ensure `.env` file is configured correctly

## 📜 License

MIT License - Free to use and modify for your projects.

---

**Built with ❤️ using LangGraph, LangChain, and Streamlit**

*Professional AI Agent Architecture for Trading Analysis*
