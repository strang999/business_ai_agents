# 🤖 Local Models for Trading Prediction

Comprehensive guide to running local models for trading analysis instead of API-based LLMs.

---

## 🎯 Why Local Models?

### Advantages
- ✅ **Privacy** - Trading data never leaves your machine
- ✅ **Cost** - No API fees after initial setup
- ✅ **Speed** - No network latency, instant responses
- ✅ **Customization** - Fine-tune on your own trading data
- ✅ **No Rate Limits** - Run as many analyses as needed
- ✅ **Offline** - Works without internet

### Disadvantages
- ❌ Requires good GPU (RTX 3090/4090 or better)
- ❌ Initial setup complexity
- ❌ RAM requirements (16GB+ for larger models)
- ❌ Storage (models are 5-50GB each)

---

## 🦜 LLM Models for Reasoning & Analysis

### 1. **Qwen2.5-14B-Instruct** ⭐ RECOMMENDED

**Best for:** Technical and fundamental analysis

```bash
# Install Ollama
# Windows: Download from ollama.ai

# Pull model
ollama pull qwen2.5:14b

# Test
ollama run qwen2.5:14b "Analyze Bitcoin price action"
```

**Specs:**
- Size: ~9GB
- RAM: 16GB recommended
- GPU: RTX 3090/4090 (Q4 quantization)
- Speed: ~30 tokens/sec on RTX 4090
- Context: 32K tokens

**Why it's great:**
- ✅ Excellent reasoning for financial analysis
- ✅ Supports long context (can analyze lots of data)
- ✅ Fast inference
- ✅ Good at structured outputs
- ✅ Multilingual (English + others)

**Integration:**
```python
from langchain_community.llms import Ollama

llm = Ollama(
    model="qwen2.5:14b",
    temperature=0.3
)

response = llm.invoke("Analyze these indicators: RSI=55, MACD=positive...")
```

---

### 2. **DeepSeek-Coder-33B**

**Best for:** Technical analysis and pattern recognition

```bash
ollama pull deepseek-coder:33b
```

**Specs:**
- Size: ~19GB
- RAM: 32GB recommended
- GPU: RTX 4090 or A100
- Context: 16K tokens

**Why use it:**
- ✅ Excellent at analyzing structured data
- ✅ Great for technical indicators
- ✅ Can write trading strategies in code
- ✅ Strong reasoning capabilities

---

### 3. **Llama 3.1 8B Instruct** (Lighter Option)

**Best for:** Fast analysis on limited hardware

```bash
ollama pull llama3.1:8b
```

**Specs:**
- Size: ~4.7GB
- RAM: 8GB minimum
- GPU: RTX 3060 or better
- Speed: ~50 tokens/sec on RTX 4090

**Why use it:**
- ✅ Lightweight and fast
- ✅ Good for quick sentiment analysis
- ✅ Can run on consumer GPUs
- ✅ Meta's latest model

---

### 4. **Mistral 7B Instruct**

**Best for:** Balanced performance

```bash
ollama pull mistral:7b-instruct
```

**Specs:**
- Size: ~4.1GB
- RAM: 8GB
- GPU: RTX 3060+
- Context: 8K tokens

**Why use it:**
- ✅ Fast and efficient
- ✅ Good reasoning
- ✅ Low resource requirements

---

## 📈 Specialized Trading Models

### 1. **TimeGPT** (Nixtla) ⭐ BEST FOR FORECASTING

**What it is:** Foundation model for time series forecasting

**Installation:**
```bash
pip install nixtla
```

**Usage:**
```python
from nixtla import NixtlaClient

# Initialize (can run locally or via API)
nixtla = NixtlaClient(api_key="your-key")  # or local mode

# Forecast
forecast = nixtla.forecast(
    df=historical_prices,
    h=24,  # 24 hours ahead
    level=[80, 95]  # confidence intervals
)
```

**Specs:**
- Pre-trained on billions of time series
- Zero-shot forecasting (no training needed!)
- Gives confidence intervals
- Works for ANY time series

**Why it's amazing:**
- ✅ State-of-the-art accuracy
- ✅ No training needed
- ✅ Handles seasonality automatically
- ✅ Multiple horizons

**Local Alternative:**
```python
# Self-hosted TimeGPT (requires GPU cluster)
# For individual use, API is more practical
```

---

### 2. **Prophet** (Meta)

**What it is:** Additive forecasting model

**Installation:**
```bash
pip install prophet
```

**Usage:**
```python
from prophet import Prophet
import pandas as pd

# Prepare data
df = pd.DataFrame({
    'ds': dates,  # datetime
    'y': prices   # values
})

# Train
model = Prophet(
    daily_seasonality=True,
    weekly_seasonality=True,
    changepoint_prior_scale=0.05
)
model.fit(df)

# Forecast
future = model.make_future_dataframe(periods=24, freq='H')
forecast = model.predict(future)
```

**Why use it:**
- ✅ Easy to use
- ✅ Handles missing data
- ✅ Automatic seasonality detection
- ✅ Interpretable results
- ✅ Fast training

---

### 3. **N-BEATS** (Neural Basis Expansion)

**What it is:** Deep learning for time series

**Installation:**
```bash
pip install neuralforecast
```

**Usage:**
```python
from neuralforecast import NeuralForecast
from neuralforecast.models import NBEATS

# Initialize
nf = NeuralForecast(
    models=[NBEATS(
        input_size=168,  # 1 week of hourly data
        h=24,           # predict 24h ahead
        max_steps=500
    )],
    freq='H'
)

# Train
nf.fit(df=train_data)

# Predict
forecasts = nf.predict()
```

**Why use it:**
- ✅ SOTA accuracy on many benchmarks
- ✅ Interpretable (trend + seasonality decomposition)
- ✅ No manual feature engineering
- ✅ Fast inference

---

### 4. **Chronos** (Amazon) ⭐ NEW & POWERFUL

**What it is:** Pre-trained foundation model for time series (like GPT for forecasting!)

**Installation:**
```bash
pip install chronos-forecasting
```

**Usage - Local:**
```python
from chronos import ChronosPipeline
import torch

# Load model (first run downloads from HuggingFace)
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-base",
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

# Forecast
context = torch.tensor(historical_prices)
forecast = pipeline.predict(
    context,
    prediction_length=24,
    num_samples=100
)

# Get statistics
forecast_mean = forecast.mean(dim=0).numpy()
forecast_q90 = forecast.quantile(0.90, dim=0).numpy()
```

**Usage - Cloud (HuggingFace API):**
```python
import requests

API_URL = "https://api-inference.huggingface.co/models/amazon/chronos-t5-base"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

response = requests.post(API_URL, headers=headers, json={
    "inputs": historical_prices,
    "parameters": {"prediction_length": 24}
})

forecast = response.json()
```

**Model Sizes:**
- `chronos-t5-tiny` (8M params) - CPU, fast, good accuracy
- `chronos-t5-mini` (20M params) - CPU, better
- `chronos-t5-small` (46M params) - CPU/GPU
- `chronos-t5-base` (200M params) - ⭐ RECOMMENDED (GPU)
- `chronos-t5-large` (710M params) - Best accuracy (GPU required)

**Hardware Requirements:**
- **tiny/mini:** CPU only, 4-8GB RAM
- **base:** GPU recommended (RTX 3060+), 16GB RAM
- **large:** GPU required (RTX 4090/A100), 32GB RAM

**Why it's AMAZING:**
- ✅ **Zero-shot forecasting** - No training needed!
- ✅ Pre-trained on billions of time series
- ✅ Works on ANY time series (stocks, crypto, weather, etc.)
- ✅ Probabilistic forecasting (confidence intervals)
- ✅ SOTA accuracy on benchmarks
- ✅ Can run 100% locally OR cloud API
- ✅ From Amazon (production-tested)

**Integration Example:**
```python
# See chronos_integration.py for complete example!
result = trading_forecast_chronos("BTC/USDT", "1h")
print(f"Predicted price (24h): ${result['forecast_24h']:,.2f}")
print(f"Confidence: {result['confidence_95_lower']:,.2f} - {result['confidence_95_upper']:,.2f}")
```

**Deployment Options:**
1. **Local (Laptop/Desktop):** Free, private, requires GPU
2. **HuggingFace API:** $0.0001-0.001 per prediction, no GPU needed
3. **AWS SageMaker:** ~$0.70/hour, enterprise-grade

**For Trading:**
- ✅ Perfect for price forecasting
- ✅ Handles volatility well
- ✅ Gives confidence intervals (critical for risk!)
- ✅ Fast inference (< 1 second on GPU)

---

### 5. **Custom LSTM/GRU Models**

**What it is:** Build your own with TensorFlow/PyTorch

**Example (PyTorch):**
```python
import torch
import torch.nn as nn

class TradingLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        prediction = self.fc(lstm_out[:, -1, :])
        return prediction

# Train on your data
model = TradingLSTM(input_size=10, hidden_size=50, num_layers=2)
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.MSELoss()

# Training loop
for epoch in range(100):
    optimizer.zero_grad()
    output = model(X_train)
    loss = criterion(output, y_train)
    loss.backward()
    optimizer.step()
```

**Why build custom:**
- ✅ Complete control
- ✅ Can incorporate domain knowledge
- ✅ Fine-tune on your specific assets
- ✅ Add custom features (on-chain data, sentiment, etc.)

---

### 5. **Transformer Models (Custom)**

**Using HuggingFace:**
```python
from transformers import TimeSeriesTransformerForPrediction

model = TimeSeriesTransformerForPrediction.from_pretrained(
    "huggingface/time-series-transformer-tourism-monthly"
)

# Fine-tune on your trading data
```

---

## 🧠 Sentiment Analysis Models

### 1. **FinBERT**

**What it is:** BERT fine-tuned on financial text

```bash
pip install transformers
```

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

# Analyze news
text = "Bitcoin prices surge on ETF approval news"
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
outputs = model(**inputs)
predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

# Returns: [negative, neutral, positive] probabilities
```

**Why use it:**
- ✅ Trained on financial news
- ✅ Understands market terminology
- ✅ Fast inference
- ✅ Runs on CPU

---

## 🏗️ Recommended Architecture

### **Hybrid Approach** (Best of Both Worlds)

```
Trading Agent Pipeline
├── Data Collection (Python)
│   └── CCXT, yfinance
├── Technical Analysis (Local LLM)
│   └── Qwen2.5-14B via Ollama
├── Fundamental Analysis (Local LLM)
│   └── Qwen2.5-14B + FinBERT sentiment
├── Price Prediction (Specialized Model)
│   └── TimeGPT or N-BEATS
├── Risk Assessment (Local LLM)
│   └── Qwen2.5-14B
└── Decision Making (Local LLM)
    └── Qwen2.5-14B
```

---

## 💻 Hardware Requirements

### Minimum (for testing)
- CPU: 8-core modern processor
- RAM: 16GB
- GPU: RTX 3060 (12GB VRAM)
- Storage: 100GB SSD

**Can run:** Qwen2.5-7B, Llama 3.1 8B, Prophet, FinBERT

### Recommended (production)
- CPU: 16-core (Ryzen 9 / Intel i9)
- RAM: 32GB
- GPU: RTX 4090 (24GB VRAM)
- Storage: 500GB NVMe SSD

**Can run:** Qwen2.5-14B, DeepSeek-Coder-33B, N-BEATS, Custom models

### Optimal (enterprise)
- CPU: 32-core server CPU
- RAM: 128GB
- GPU: A100 (40GB/80GB) or H100
- Storage: 1TB+ NVMe

**Can run:** Any model, multiple concurrent analyses, fine-tuning

---

## 🚀 Quick Start: Local Setup

### Option 1: Ollama + Qwen (Easiest)

```bash
# 1. Install Ollama
# Download from ollama.ai

# 2. Pull model
ollama pull qwen2.5:14b

# 3. Test
ollama run qwen2.5:14b

# 4. Use in Python
pip install langchain-community
```

```python
from langchain_community.llms import Ollama

llm = Ollama(model="qwen2.5:14b")
response = llm.invoke("Your trading prompt here")
```

### Option 2: LM Studio (GUI Interface)

1. Download LM Studio: https://lmstudio.ai/
2. Click "Download" and search "Qwen2.5-14B"
3. Download quantized version (Q4_K_M recommended)
4. Click "Load" to run the model
5. Use local API endpoint

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen2.5-14b",
    base_url="http://localhost:1234/v1",
    api_key="not-needed"
)
```

### Option 3: HuggingFace Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-14B-Instruct",
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-14B-Instruct")

# Generate
messages = [{"role": "user", "content": "Analyze this trade..."}]
text = tokenizer.apply_chat_template(messages, tokenize=False)
inputs = tokenizer([text], return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=512)
response = tokenizer.decode(outputs[0])
```

---

## 📊 Model Comparison

| Model | Size | RAM | Speed | Use Case |
|-------|------|-----|-------|----------|
| **Qwen2.5-14B** | 9GB | 16GB | Fast | Analysis, Reasoning |
| **DeepSeek-Coder-33B** | 19GB | 32GB | Medium | Technical Analysis |
| **Llama 3.1 8B** | 4.7GB | 8GB | Very Fast | Quick Analysis |
| **Mistral 7B** | 4.1GB | 8GB | Very Fast | Balanced |
| **TimeGPT** | API/Cloud | - | Fast | Forecasting |
| **Prophet** | <100MB | 4GB | Very Fast | Simple Forecasting |
| **N-BEATS** | ~50MB | 8GB | Fast | Neural Forecasting |
| **FinBERT** | 440MB | 4GB | Very Fast | Sentiment |

---

## 🔄 Integration with Trading Agent

### Update `app.py` to use Ollama:

```python
from langchain_community.llms import Ollama

def get_llm(temperature: float = 0.3):
    """Get local LLM instance via Ollama"""
    return Ollama(
        model="qwen2.5:14b",
        temperature=temperature,
        # Optional: adjust parameters
        num_predict=512,  # max tokens
        top_k=40,
        top_p=0.9
    )
```

### For TimeGPT Forecasting:

```python
def predict_price_node(state: TradingState) -> Dict:
    """Use TimeGPT for actual forecasting"""
    from nixtla import NixtlaClient
    
    # Initialize
    nixtla = NixtlaClient(api_key=os.getenv("NIXTLA_API_KEY"))
    
    # Prepare data
    df = get_historical_prices(state['symbol'], state['timeframe'])
    
    # Forecast
    forecast = nixtla.forecast(
        df=df,
        h=24,  # 24 periods ahead
        level=[80, 95]  # confidence intervals
    )
    
    return {
        "price_prediction": {
            "predicted_price": forecast['TimeGPT'].iloc[-1],
            "confidence_80": forecast['TimeGPT-hi-80'].iloc[-1],
            "confidence_95": forecast['TimeGPT-hi-95'].iloc[-1]
        }
    }
```

---

## 📚 Training Your Own Model

### Step 1: Collect Data
```python
import ccxt
import pandas as pd

exchange = ccxt.binance()
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=1000)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
```

### Step 2: Feature Engineering
```python
import ta

# Add technical indicators
df['rsi'] = ta.momentum.rsi(df['close'])
df['macd'] = ta.trend.macd(df['close'])
df['bb_upper'] = ta.volatility.bollinger_hband(df['close'])
# ... add more
```

### Step 3: Train Model
```python
from neuralforecast import NeuralForecast
from neuralforecast.models import NBEATS

nf = NeuralForecast(
    models=[NBEATS(input_size=168, h=24)],
    freq='H'
)

nf.fit(df=df)
nf.save(path='models/btc_nbeats.pkl')
```

---

## 🎯 Best Practices

### 1. Model Selection
- Start with **Qwen2.5-14B** for LLM tasks
- Use **TimeGPT** or **Prophet** for forecasting
- Add **FinBERT** for sentiment

### 2. Resource Management
- Use quantized models (Q4) to save VRAM
- Cache LLM responses for repeated queries
- Batch process multiple analyses

### 3. Fine-Tuning
- Collect your own trading decisions
- Fine-tune on successful trades
- Regularly update with new data

### 4. Validation
- Always backtest predictions
- Track accuracy over time
- A/B test different models

---

## 🔮 Future: Fully Local Setup

```
Complete Local Stack (No APIs!)
├── LLM: Qwen2.5-14B (Ollama)
├── Forecasting: N-BEATS (trained on your data)
├── Sentiment: FinBERT (local)
├── Data: CCXT (direct exchange connection)
└── Storage: Local PostgreSQL
```

**Privacy:** ✅ 100% local
**Cost:** ✅ Zero after setup
**Speed:** ✅ Very fast
**Customization:** ✅ Full control

---

## 📞 Next Steps

1. **Install Ollama** - Get Qwen2.5-14B running
2. **Test locally** - Run a few analyses
3. **Add TimeGPT** - For better forecasting
4. **Collect data** - Build training dataset
5. **Fine-tune** - Create your custom model

---

**Last Updated:** 2026-01-08
**Recommended:** Qwen2.5-14B + TimeGPT + FinBERT
