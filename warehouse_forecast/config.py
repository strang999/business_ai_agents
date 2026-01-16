# Warehouse Forecasting Configuration

# Data paths
DATA_DIR = "data/Test data"
SCHEMA_PATH = "data/DATA_SCHEMA.md"
OUTPUT_DIR = "output"

# Model settings
MODEL_CONFIG = {
    "name": "amazon/chronos-t5-small",  # Upgraded from tiny (better accuracy)
    "device": "cuda" if torch.cuda.is_available() else "cpu",  # Auto-detect
    "dtype": "bfloat16",  # or "int8" for quantization
    "batch_size": 50,  # Process 50 series at a time (memory optimization)
}

import torch  # Need for cuda check

# Forecasting parameters
FORECAST_HORIZON = 30  # days ahead
QUANTILE_LEVELS = [0.10, 0.50, 0.90]  # 10%, 50%, 90% confidence

# Business rules (will be overridden by DATA_SCHEMA.md if available)
WAREHOUSE_CAPACITY = {
    "default": 1000,  # units
    # Specific warehouses can override
}

MIN_STOCK_LEVELS = {
    "default": 50,  # units
    # Specific products can override
}

# Alert thresholds
ALERT_THRESHOLDS = {
    "warehouse_overflow_days": 7,  # Alert if full in < 7 days
    "ingredient_shortage_days": 14,  # Alert if empty in < 14 days
    "critical_days": 3,  # HIGH priority if < 3 days
}

# Validation split
VALIDATION_CONFIG = {
    "train_months": 2,  # Use first 2 months for context
    "test_months": 1,   # Use last month for validation
    "min_series_length": 30,  # Minimum days of data required
}

# Vector DB for schema RAG
VECTORDB_CONFIG = {
    "persist_directory": "./chroma_db",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 500,
    "chunk_overlap": 50,
}

# LLM for explanations (optional - Ollama)
LLM_CONFIG = {
    "enabled": False,  # Set to True if Ollama is available
    "model": "qwen2.5:7b",
    "temperature": 0.3,
}

# Logging
LOG_LEVEL = "INFO"
SAVE_CHECKPOINTS = True
