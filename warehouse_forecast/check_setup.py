"""
Quick test script to verify all dependencies and data
"""

print("=" * 60)
print("DEPENDENCY CHECK")
print("=" * 60)

# 1. PyTorch
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    print(f"   CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
except ImportError as e:
    print(f"❌ PyTorch: NOT INSTALLED")
    print(f"   Install: pip install torch")

# 2. Chronos
try:
    from chronos import ChronosPipeline
    print(f"✅ Chronos: Installed")
except ImportError:
    print(f"❌ Chronos: NOT INSTALLED")
    print(f"   Install: pip install chronos-forecasting")

# 3. LangGraph
try:
    from langgraph.graph import StateGraph
    print(f"✅ LangGraph: Installed")
except ImportError:
    print(f"❌ LangGraph: NOT INSTALLED")
    print(f"   Install: pip install langgraph")

# 4. Pandas
try:
    import pandas as pd
    print(f"✅ Pandas: {pd.__version__}")
except ImportError:
    print(f"❌ Pandas: NOT INSTALLED")

# 5. Numpy
try:
    import numpy as np
    print(f"✅ Numpy: {np.__version__}")
except ImportError:
    print(f"❌ Numpy: NOT INSTALLED")

print("\n" + "=" * 60)
print("DATA CHECK")
print("=" * 60)

# Check data files
from pathlib import Path

data_dir = Path("data/Test data")
files_to_check = [
    "1CDailyBalances.json",
    "1CIDProducts.json",
    "1CProductComposition.json"
]

if data_dir.exists():
    print(f"✅ Data directory: {data_dir}")
    
    for filename in files_to_check:
        filepath = data_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / 1024 / 1024
            print(f"✅ {filename}: {size_mb:.1f} MB")
        else:
            print(f"❌ {filename}: NOT FOUND")
else:
    print(f"❌ Data directory not found: {data_dir}")
    print(f"   Create: mkdir -p 'data/Test data'")
    print(f"   Copy files from trading_agent/data/Test data/")

# Check schema
schema_path = Path("data/DATA_SCHEMA.md")
if schema_path.exists():
    print(f"✅ Schema: {schema_path}")
else:
    print(f"⚠️  Schema not found (optional): {schema_path}")

print("\n" + "=" * 60)
print("READY TO RUN" if data_dir.exists() else "SETUP REQUIRED")
print("=" * 60)
