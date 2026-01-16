# Warehouse Forecasting System

**Local multivariate time series forecasting** using Chronos-2 and LangGraph

## Features

✅ **6-Agent Architecture** using LangGraph  
✅ **Chronos-2 Forecasting** with RTX 3070 optimization  
✅ **NDA Compliant** - 100% local processing  
✅ **Business Rules** - Days until full/empty calculations  
✅ **Prioritized Alerts** - HIGH/MEDIUM/LOW severity  
✅ **Multivariate Forecasting** - Cross-warehouse learning  

---

## Project Structure

```
warehouse_forecast/
├── agent_1_data_loader.py       # Load JSON + schema
├── agent_2_feature_engineer.py  # Transform to time series
├── agent_3_chronos_forecaster.py # Run predictions
├── agent_4_business_rules.py    # Apply constraints
├── agent_5_alert_generator.py   # Create alerts
├── agent_6_report_builder.py    # Generate outputs
├── main.py                      # LangGraph pipeline
├── config.py                    # Configuration
├── state.py                     # State definition
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

---

## Installation

### 1. Create Environment

```bash
conda create -n warehouse python=3.10
conda activate warehouse
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install PyTorch with CUDA  (for GPU)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

###4. Verify GPU

```bash
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

---

## Usage

### Basic Run

```bash
python main.py
```

### Custom Horizon

```bash
python main.py --horizon 60
```

### Filter Warehouses

```bash
python main.py --warehouses WH_01,WH_02
```

### All Options

```bash
python main.py --help
```

---

## Data Setup

Place your data files in:

```
data/Test data/
├── 1CDailyBalances.json        # Required
├── 1CIDProducts.json           # Required
├── 1CProductComposition.json   # Required
├── 1CProduction.json           # Optional
├── 1CSupplierOrders.json       # Optional
└── 1CIDProductInSalesChannel.json # Optional
```

Place schema documentation in:

```
data/DATA_SCHEMA.md              # Recommended
```

---

## Output

Results are saved to `output/` directory:

- `forecasts_TIMESTAMP.json` - All predictions
- `alerts_TIMESTAMP.json` - Prioritized alerts
- `metrics_TIMESTAMP.json` - Business metrics
- `summary_TIMESTAMP.txt` - Human-readable report

---

## Pipeline Flow

```
1. Data Loader
   ↓ (raw_data, schema)
2. Feature Engineer
   ↓ (time_series, groups)
3. Chronos Forecaster
   ↓ (forecasts)
4. Business Rules
   ↓ (metrics, violations)
5. Alert Generator
   ↓ (alerts)
6. Report Builder
   → Output files
```

---

## Configuration

Edit `config.py` to customize:

- **Model**: chronos-t5-(tiny/small/base)
- **VRAM**: batch size, dtype, quantization
- **Business Rules**: capacity, min stock, thresholds
- **Forecast**: horizon, quantiles

---

## Hardware Requirements

**Minimum:**
- CPU: 4+ cores
- RAM: 16GB
- Disk: 5GB

**Recommended:**
- GPU: RTX 3070 (8GB VRAM) or better
- RAM: 24GB
- Disk: 10GB

**Chronos Model Sizes:**

| Model | VRAM  | Accuracy | Speed |
|-------|-------|----------|-------|
| tiny  | 1-2GB | ~12% MAPE | 0.5s |
| small | 3-4GB | ~9% MAPE | 1-2s |
| base  | 6-8GB | ~7% MAPE | 2-3s |

---

## Troubleshooting

### OOM Error (Out of Memory)

```python
# In config.py, change:
MODEL_CONFIG = {
    "name": "amazon/chronos-t5-tiny",  # Use smaller model
    "batch_size": 10,  # Reduce batch size
}
```

### Slow Performance

- Use GPU instead of CPU
- Reduce batch size if OOM
- Use smaller model (tiny vs small)

### No Data Found

- Check `data/Test data/` path
- Ensure JSON files are UTF-8 encoded
- Verify BOM encoding (utf-8-sig)

---

## Development

Run individual agents for testing:

```bash
python agent_1_data_loader.py
python agent_2_feature_engineer.py
python agent_3_chronos_forecaster.py
```

---

## Next Steps

- [x] Basic 6-agent pipeline
- [ ] Vector DB for schema RAG
- [ ] LLM explanations (Ollama)
- [ ] Backtesting framework
- [ ] Docker deployment
- [ ] Web dashboard

---

## License

NDA-protected. For internal use only.
