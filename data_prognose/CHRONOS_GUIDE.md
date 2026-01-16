# 🚀 Chronos Quick Reference

## What is Chronos?

**Chronos** is Amazon's **foundation model for time series forecasting** - basically "GPT for predictions"!

- Pre-trained on **billions** of time series
- **Zero-shot forecasting** - works out of the box, no training!
- From tiny (8M) to large (710M parameters)
- Can run **locally** or via **cloud API**

---

## ✅ YES - You Can Run It Locally!

### Hardware Options:

| Model Size | Params | Hardware | RAM | Best For |
|------------|--------|----------|-----|----------|
| **tiny** | 8M | CPU | 4GB | Quick tests, low resources |
| **mini** | 20M | CPU | 8GB | Balanced CPU usage |
| **small** | 46M | CPU/GPU | 8GB | Good quality, still fast |
| **base** ⭐ | 200M | GPU (RTX 3060+) | 16GB | **RECOMMENDED** |
| **large** | 710M | GPU (RTX 4090) | 32GB | Best accuracy |

**Your setup:** If you have RTX 3090/4090 → Use **base** or **large**

---

## 🖥️ Local Setup (3 steps)

### Step 1: Install
```bash
pip install chronos-forecasting torch
```

### Step 2: Python Code
```python
from chronos import ChronosPipeline
import torch

# Load model (downloads automatically first time)
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-base",  # or tiny/small/large
    device_map="auto",          # Uses GPU if available
    torch_dtype=torch.bfloat16
)

# Your price data
prices = [45000, 45100, 44900, ...]  # Historical prices

# Forecast
forecast = pipeline.predict(
    torch.tensor(prices),
    prediction_length=24,  # Predict next 24 periods
    num_samples=100        # For confidence intervals
)

# Results
mean_forecast = forecast.mean(dim=0).numpy()
print(f"Predicted next price: ${mean_forecast[-1]:,.2f}")
```

### Step 3: Done! 🎉

**First run:** Downloads model (~800MB for base)
**After that:** Instant loading from disk

---

## ☁️ Cloud-Based Option (No GPU Needed!)

### Option 1: HuggingFace Inference API

```python
import requests

# Get free API token from huggingface.co
API_URL = "https://api-inference.huggingface.co/models/amazon/chronos-t5-base"
headers = {"Authorization": f"Bearer hf_YourTokenHere"}

response = requests.post(API_URL, headers=headers, json={
    "inputs": [45000, 45100, 44900, ...],
    "parameters": {"prediction_length": 24}
})

forecast = response.json()
```

**Cost:** 
- Free tier: 1000 requests/month
- Paid: ~$0.001 per prediction
- No GPU needed on your machine!

### Option 2: AWS SageMaker (Enterprise)

For production deployment:
- Managed infrastructure
- Auto-scaling
- Cost: ~$0.70/hour (ml.g4dn.xlarge)
- Best for 24/7 services

---

## 🎯 For Your Trading Agent

### Integration (Drop-in replacement):

```python
# In app.py, replace prediction_node with:

from chronos_integration import chronos_prediction_node

# Use it in your graph
workflow.add_node("prediction", chronos_prediction_node)
```

### What You Get:

```python
{
    "current_price": 45000.00,
    "predicted_price": 45850.50,
    "change_percent": +1.89,
    "confidence_95": [44500, 46200],  # 95% sure it's in this range
    "trend": "BULLISH",
    "model": "Chronos-T5-Base"
}
```

---

## 📊 Chronos vs Others

| Feature | Chronos | TimeGPT | Prophet | N-BEATS |
|---------|---------|---------|---------|---------|
| **Training Required** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Local Inference** | ✅ Yes | ⚠️ Limited | ✅ Yes | ✅ Yes |
| **Cloud API** | ✅ Free/Paid | ✅ Paid | ❌ No | ❌ No |
| **Accuracy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed (GPU)** | Fast | Fast | Very Fast | Medium |
| **Setup Ease** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

---

## 🚀 Recommended Stack for Trading

### Best Option: Hybrid

```
Trading Agent Pipeline:
├── LLM Analysis: Qwen2.5-14B (local)
├── Price Forecast: Chronos-T5-Base (local) ⭐
├── Sentiment: FinBERT (local)
└── All 100% local, 100% private, $0 API costs!
```

### Without GPU: Cloud API

```
Trading Agent Pipeline:
├── LLM: DeepSeek-Chat (OpenRouter)
├── Forecast: Chronos (HuggingFace API) ⭐
├── Sentiment: FinBERT (CPU local)
└── Total cost: ~$0.02 per complete analysis
```

---

## 💡 Quick Demo

Run our example:

```bash
cd trading_agent
python chronos_integration.py
```

Choose option 1 for full forecast demo!

---

## 🎤 For Your Call

**Mention Chronos as:**

> "Для forecasting ми можемо використати **Chronos** - це Amazon's foundation model для часових рядів. 
> 
> Як GPT, але для predictions. Pre-trained на мільярдах time series.
> 
> **Zero-shot** - працює out of the box, no training needed.
> 
> Можна запустити **локально** (RTX 3090/4090) або через **HuggingFace API**.
> 
> Дає probabilistic forecasts з confidence intervals - критично для risk management!"

**Benefits:**
- ✅ No model training required
- ✅ Works immediately on any asset
- ✅ Confidence intervals for risk assessment
- ✅ Production-tested (Amazon)
- ✅ Flexible deployment (local or cloud)

---

## 📚 More Info

- **HuggingFace:** https://huggingface.co/amazon/chronos-t5-base
- **Paper:** https://arxiv.org/abs/2403.07815
- **Code:** `chronos_integration.py` in this project
- **Guide:** `LOCAL_MODELS_GUIDE.md` (updated with Chronos)

---

## ✅ Bottom Line

**Q: Can I run Chronos locally?**
**A:** YES! With RTX 3060+ GPU.

**Q: What if no GPU?**
**A:** Use HuggingFace API - free tier available, very cheap paid tier.

**Q: Best for trading?**
**A:** Chronos-T5-Base - perfect balance of accuracy and speed.

**Q: Better than Prophet/TimeGPT?**
**A:** 
- vs Prophet: Better accuracy, zero training
- vs TimeGPT: Can run fully local, no API costs after setup

---

**Recommended: Use Chronos-T5-Base locally if you have GPU, or via HuggingFace API if not!** 🚀
