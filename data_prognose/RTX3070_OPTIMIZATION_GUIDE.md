# 🎯 RTX 3070 (8GB VRAM) - Optimization Strategies for Chronos-2

## Problem: Chronos-2-Small може не поміститись в 8GB VRAM

**5 Concrete Solutions** (від найкращого до fallback)

---

## ✅ Option 1: Model Quantization (RECOMMENDED)

**Concept:** Compress model weights from float32/bfloat16 → int8/int4

### INT8 Quantization (Loses ~0-2% accuracy)

```python
from chronos import ChronosPipeline
import torch
from transformers import BitsAndBytesConfig

# Configure 8-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
    llm_int8_has_fp16_weight=False
)

# Load Chronos-2-Small with quantization
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="auto",
    quantization_config=quantization_config,
    torch_dtype=torch.float16  # Use fp16 for computations
)

# Expected VRAM: ~3-4GB (vs 6-7GB normal)
# Speed: Similar to normal
# Accuracy: -1 to -2% MAPE
```

**Pros:**
- ✅ 50% less VRAM
- ✅ Minimal accuracy loss
- ✅ Same inference speed
- ✅ Still use "small" model (better than tiny)

**Cons:**
- ⚠️ Requires `bitsandbytes` library
- ⚠️ Linux/WSL only (Windows native has issues)

**Installation:**
```bash
pip install bitsandbytes
# If Windows: Use WSL2 or Docker
```

---

### INT4 Quantization (Loses ~3-5% accuracy)

```python
# Even more aggressive compression
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="auto",
    quantization_config=quantization_config
)

# Expected VRAM: ~2-3GB
# Accuracy: -3 to -5% MAPE
```

**When to use:**
- If INT8 still OOM
- Can tolerate 10-12% MAPE instead of 8-9%

---

## ✅ Option 2: Use Smaller Model (Chronos-2-Tiny)

**Fallback:** If quantization too complex, use smaller model

```python
# Tiny model - guaranteed to fit!
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-tiny",
    device_map="cuda",
    torch_dtype=torch.bfloat16
)

# Expected VRAM: ~1-2GB
# Speed: 2x faster than small
# Accuracy: ~12-15% MAPE (vs 8-9% for small)
```

**Comparison Table:**

| Model | VRAM | Speed | Accuracy (MAPE) | Fits RTX 3070? |
|-------|------|-------|-----------------|----------------|
| tiny | 1-2GB | 0.5s | 12-15% | ✅ Always |
| mini | 2-3GB | 0.8s | 10-12% | ✅ Always |
| small | 6-7GB | 1.5s | 8-9% | ⚠️ Tight |
| small + INT8 | 3-4GB | 1.5s | 9-10% | ✅ Should fit |
| small + INT4 | 2-3GB | 1.5s | 11-13% | ✅ Always |

**Recommendation:**
```python
# Start here - best guarantee
model_size = "tiny"  # or "mini" if you want better accuracy

# If tiny works, try upgrading:
model_size = "small" with INT8 quantization
```

---

## ✅ Option 3: CPU Offloading (Hybrid GPU+CPU)

**Concept:** Keep part of model on GPU, part on CPU (RAM)

```python
from accelerate import init_empty_weights, load_checkpoint_and_dispatch

# Load with automatic offloading
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="auto",  # Automatically splits across GPU + CPU
    max_memory={
        0: "7GB",    # GPU 0: Use max 7GB VRAM
        "cpu": "20GB"  # CPU: Use up to 20GB RAM
    },
    offload_folder="offload",  # Temp storage for offloaded params
    torch_dtype=torch.bfloat16
)

# Expected VRAM: 7GB (stays under limit)
# Expected RAM: 5-10GB additional
# Speed: 2-3x slower (CPU parts are bottleneck)
```

**Pros:**
- ✅ Can use full small model
- ✅ No accuracy loss
- ✅ Automatic splitting

**Cons:**
- ❌ 2-3x slower inference
- ⚠️ Needs 20GB+ system RAM
- ⚠️ Disk I/O overhead

**When to use:**
- You have 24GB RAM (you do!)
- Speed not critical (batch jobs overnight)
- Need best accuracy

---

## ✅ Option 4: Process in Batches (Sequential Forecasting)

**Concept:** Don't forecast all warehouses at once

```python
class BatchedForecaster:
    def __init__(self, model, max_series_per_batch=5):
        self.model = model
        self.max_batch = max_series_per_batch
        
    def forecast_all_warehouses(self, warehouses_data):
        all_forecasts = []
        
        # Process in small batches
        for i in range(0, len(warehouses_data), self.max_batch):
            batch = warehouses_data[i:i + self.max_batch]
            
            # Forecast just this batch
            forecasts = self.model.forecast_multivariate(batch)
            all_forecasts.append(forecasts)
            
            # Free GPU memory
            torch.cuda.empty_cache()
        
        return all_forecasts

# Usage
forecaster = BatchedForecaster(pipeline, max_series_per_batch=3)
results = forecaster.forecast_all_warehouses(all_20_warehouses)

# Each batch uses less VRAM
# Total time: batch_size * num_batches
```

**Pros:**
- ✅ Works with any model size
- ✅ Guaranteed to fit
- ✅ No accuracy loss

**Cons:**
- ❌ Slower (sequential processing)
- ⚠️ Loses some cross-warehouse learning

**When to use:**
- Many warehouses (20+)
- Batch jobs (not real-time)
- Complement to other strategies

---

## ✅ Option 5: Fallback to Statistical Models

**If all else fails:** Use classical time series models

### Prophet (Meta) - CPU Only

```python
from prophet import Prophet
import pandas as pd

class ProphetForecaster:
    def __init__(self):
        self.models = {}
        
    def forecast_warehouse(self, warehouse_data, horizon=30):
        # Prepare data
        df = pd.DataFrame({
            'ds': warehouse_data['dates'],
            'y': warehouse_data['inventory_levels']
        })
        
        # Fit Prophet
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False  # Only 3 months data
        )
        model.fit(df)
        
        # Forecast
        future = model.make_future_dataframe(periods=horizon)
        forecast = model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

# Usage
prophet = ProphetForecaster()
forecast = prophet.forecast_warehouse(wh_01_data, horizon=30)

# VRAM: 0GB (CPU only)
# Accuracy: ~15-20% MAPE (worse than Chronos, but works)
# Speed: Very fast (seconds)
```

**Pros:**
- ✅ No GPU needed
- ✅ Fast to run
- ✅ Interpretable
- ✅ Handles seasonality well

**Cons:**
- ❌ Univariate only (no multivariate benefits)
- ❌ Lower accuracy than Chronos
- ❌ Can't use correlations from JSON

---

## 🎯 Decision Tree: Which Option to Choose?

```
Start here
    ↓
┌─────────────────────────────────────┐
│ Try Chronos-2-Tiny first           │
│ VRAM: 1-2GB | Accuracy: 12-15%     │
└─────────────────┬───────────────────┘
                  ↓
        ┌─────────────────┐
        │  Good enough?   │
        └────┬─────────┬──┘
             │ NO      │ YES → Done! ✅
             ↓         │
┌────────────────────┐ │
│ Try INT8 + Small   │ │
│ VRAM: 3-4GB        │ │
│ Accuracy: 9-10%    │ │
└────────┬───────────┘ │
         ↓             ↓
    ┌─────────┐        
    │ Fits?   │        
    └──┬───┬──┘        
   YES │   │ NO       
       │   ↓          
       │ ┌────────────────┐
       │ │ CPU Offload    │
       │ │ or Batching    │
       │ └────────────────┘
       ↓
   Done! ✅
```

---

## 📊 Recommended Strategy for Your Case

### Primary: Chronos-2-Tiny

```python
# warehouse_forecasting/src/config.py

MODEL_CONFIG = {
    # Start conservative
    "model_name": "amazon/chronos-t5-tiny",
    "device": "cuda",
    "dtype": torch.bfloat16,
    
    # Performance settings
    "batch_size": 1,  # Process one forecast at a time
    "num_samples": 100,  # For confidence intervals
    
    # Fallback if OOM
    "fallback_to_cpu": True
}
```

### Upgrade Path: INT8 Small

```python
# If tiny works but accuracy not good enough
MODEL_CONFIG = {
    "model_name": "amazon/chronos-t5-small",
    "device": "cuda",
    "quantization": "int8",  # Enable quantization
    "dtype": torch.float16,
    
    "batch_size": 1,
    "num_samples": 100
}
```

### Ultimate Fallback: Prophet

```python
# If all Chronos options fail
USE_PROPHET = True  # Falls back to statistical model
```

---

## 💻 Implementation: Smart Model Loader

```python
# src/model_loader.py

import torch
from chronos import ChronosPipeline
from transformers import BitsAndBytesConfig

class SmartModelLoader:
    """
    Tries multiple strategies to load model on RTX 3070 8GB
    """
    
    def __init__(self, preferred_model="small"):
        self.preferred = preferred_model
        self.loaded_model = None
        self.strategy_used = None
        
    def load_with_fallback(self):
        strategies = [
            self._try_int8_small,
            self._try_tiny,
            self._try_cpu_offload_small,
            self._try_mini
        ]
        
        for strategy in strategies:
            try:
                print(f"Trying: {strategy.__name__}...")
                model = strategy()
                
                # Test inference
                self._test_inference(model)
                
                print(f"✅ Success with {strategy.__name__}")
                self.loaded_model = model
                self.strategy_used = strategy.__name__
                return model
                
            except RuntimeError as e:
                if "out of memory" in str(e):
                    print(f"❌ OOM with {strategy.__name__}")
                    torch.cuda.empty_cache()
                    continue
                else:
                    raise
        
        # All failed
        raise RuntimeError("Could not load any model variant!")
    
    def _try_int8_small(self):
        """Strategy 1: Small model with INT8"""
        config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0
        )
        
        return ChronosPipeline.from_pretrained(
            "amazon/chronos-t5-small",
            device_map="auto",
            quantization_config=config,
            torch_dtype=torch.float16
        )
    
    def _try_tiny(self):
        """Strategy 2: Tiny model (no quantization)"""
        return ChronosPipeline.from_pretrained(
            "amazon/chronos-t5-tiny",
            device_map="cuda",
            torch_dtype=torch.bfloat16
        )
    
    def _try_cpu_offload_small(self):
        """Strategy 3: Small with CPU offload"""
        return ChronosPipeline.from_pretrained(
            "amazon/chronos-t5-small",
            device_map="auto",
            max_memory={0: "7GB", "cpu": "20GB"},
            torch_dtype=torch.bfloat16
        )
    
    def _try_mini(self):
        """Strategy 4: Mini model"""
        return ChronosPipeline.from_pretrained(
            "amazon/chronos-t5-mini",
            device_map="cuda",
            torch_dtype=torch.bfloat16
        )
    
    def _test_inference(self, model):
        """Quick test to ensure model works"""
        test_data = torch.randn(10, 100)  # 10 series, 100 timesteps
        _ = model.predict(test_data, prediction_length=10)

# Usage
loader = SmartModelLoader(preferred_model="small")
model = loader.load_with_fallback()

print(f"Loaded using: {loader.strategy_used}")
```

---

## 🔍 Memory Profiling

```python
# Check actual VRAM usage
def profile_model_memory():
    import torch
    
    # Before loading
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    
    # Load model
    model = ChronosPipeline.from_pretrained(...)
    
    # Check memory
    allocated = torch.cuda.memory_allocated() / 1024**3  # GB
    reserved = torch.cuda.memory_reserved() / 1024**3
    max_allocated = torch.cuda.max_memory_allocated() / 1024**3
    
    print(f"Allocated: {allocated:.2f} GB")
    print(f"Reserved: {reserved:.2f} GB")
    print(f"Peak: {max_allocated:.2f} GB")
    
    return max_allocated < 7.5  # Safe margin on 8GB

# Run before production
is_safe = profile_model_memory()
```

---

## 📋 Final Recommendation

```python
# config.yaml

model:
  # Primary strategy
  primary:
    name: "chronos-t5-tiny"
    device: "cuda"
    quantization: null
    expected_vram: "1-2GB"
    expected_accuracy: "12-15% MAPE"
  
  # If need better accuracy
  upgrade:
    name: "chronos-t5-small"
    device: "cuda"
    quantization: "int8"
    expected_vram: "3-4GB"
    expected_accuracy: "9-10% MAPE"
  
  # Ultimate fallback
  fallback:
    name: "prophet"
    device: "cpu"
    expected_vram: "0GB"
    expected_accuracy: "15-20% MAPE"
```

---

## ✅ Summary

**You have 5 options:**

1. **✅ INT8 Quantization** - Best choice (3-4GB, ~9% MAPE)
2. **✅ Tiny Model** - Safest (1-2GB, ~13% MAPE)
3. **⚠️ CPU Offload** - Slowest but works
4. **⚠️ Batching** - For many warehouses
5. **❌ Prophet** - Last resort (CPU, ~17% MAPE)

**Start with Tiny, upgrade to INT8 Small if needed!** 🎯

---

**Memory будет ОК з цими стратегіями!** 💪
