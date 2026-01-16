# Installation Commands for Warehouse Forecasting

## What You Need to Install

### ❌ CRITICAL: Chronos Forecasting
```bash
pip install chronos-forecasting
```

### Optional (if you want LLM explanations):
```bash
# Install Ollama from: https://ollama.ai
# Then pull model:
ollama pull qwen2.5:7b
```

## No API Keys Needed! 🎉

✅ **Everything runs 100% locally:**
- Chronos-2: Local model (no API)
- PyTorch: Local GPU compute
- All data stays on your machine

✅ **Already have:**
- PyTorch (with CUDA)
- LangGraph
- Pandas, Numpy

## Quick Start After Installing Chronos

```bash
# 1. Install Chronos
pip install chronos-forecasting

# 2. Run setup check
python check_setup.py

# 3. Test Agent 1 (Data Loader)
python agent_1_data_loader.py

# 4. If Agent 1 works, run full pipeline:
python main.py
```

## Troubleshooting

### If Chronos install fails:
```bash
# Try with specific torch version
pip install torch==2.0.0 --index-url https://download.pytorch.org/whl/cu118
pip install chronos-forecasting
```

### If OOM (Out of Memory):
Edit `config.py`:
```python
MODEL_CONFIG = {
    "name": "amazon/chronos-t5-tiny",  # Use tiny instead of small
    "batch_size": 10,
}
```

## What I Can Auto-Install vs What You Need

**I can auto-run:**
- ✅ `pip install chronos-forecasting` (will propose command)
- ✅ All Python dependencies from requirements.txt

**You need manually (optional):**
- Ollama (for LLM explanations, optional)
- CUDA drivers (already have for RTX 3070)

Ready to proceed? 🚀
