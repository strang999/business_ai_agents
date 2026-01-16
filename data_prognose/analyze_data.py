"""
Data Structure Analyzer for Warehouse Forecasting
Examines all JSON files to understand schema and relationships
"""

import json
import pandas as pd
from pathlib import Path
from pprint import pprint

DATA_PATH = Path("data/Test data")

def load_json(filename):
    """Load JSON with proper encoding"""
    with open(DATA_PATH / filename, 'rb') as f:
        content = f.read()
    return json.loads(content.decode('utf-8-sig'))

def analyze_structure():
    """Analyze all data files"""
    
    files = [
        "1CIDProducts.json",
        "1CIDProductInSalesChannel.json",
        "1CProductComposition.json",
        "1CProduction.json",
        "1CDailyBalances.json",
        "1CSupplierOrders.json"
    ]
    
    print("=" * 80)
    print("WAREHOUSE DATA STRUCTURE ANALYSIS")
    print("=" * 80)
    
    for filename in files:
        print(f"\n{'='*80}")
        print(f"📄 FILE: {filename}")
        print("=" * 80)
        
        data = load_json(filename)
        
        print(f"\n📊 Type: {type(data)}")
        print(f"📊 Total Records: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")
        
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            print(f"\n🔑 Fields in first record:")
            for key, value in first_item.items():
                value_type = type(value).__name__
                value_sample = str(value)[:50] if not isinstance(value, (dict, list)) else f"({value_type})"
                print(f"   - {key:30s} : {value_type:10s} | {value_sample}")
            
            print(f"\n📝 Sample Record (first):")
            pprint(first_item, width=120, compact=True)
            
            # Check for date fields
            date_fields = [k for k in first_item.keys() if 'date' in k.lower() or 'period' in k.lower()]
            if date_fields:
                print(f"\n📅 Date Fields Found: {date_fields}")
            
            # Check for quantity fields
            qty_fields = [k for k in first_item.keys() if 'qty' in k.lower() or 'quantity' in k.lower() or 'balance' in k.lower()]
            if qty_fields:
                print(f"\n📦 Quantity Fields Found: {qty_fields}")
        
        print("\n")

if __name__ == "__main__":
    analyze_structure()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("""
    1. ✅ Understand data structure
    2. ⏭️  Identify time series (DailyBalances)
    3. ⏭️  Identify products and warehouses
    4. ⏭️  Extract 3-month subset
    5. ⏭️  Design LangGraph agent architecture
    """)
