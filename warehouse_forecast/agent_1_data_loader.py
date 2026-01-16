"""
Agent 1: Data Loader

Responsibilities:
1. Load JSON data files (DailyBalances, Products, ProductComposition, etc.)
2. Parse DATA_SCHEMA.md for business rules
3. Extract last 3 months of data
4. Validate data quality
5. Return structured data for Feature Engineer

CRITICAL: Handle BOM encoding (utf-8-sig) for JSON files
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import logging

from config import DATA_DIR, SCHEMA_PATH
from state import WarehouseState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WarehouseDataLoader:
    """Loads and validates warehouse data from JSON files"""
    
    def __init__(self, data_dir: str = DATA_DIR, schema_path: str = SCHEMA_PATH):
        self.data_dir = Path(data_dir)
        self.schema_path = Path(schema_path)
        
        # JSON file names
        self.files = {
            'balances': '1CDailyBalances.json',
            'products': '1CIDProducts.json',
            'composition': '1CProductComposition.json',
            'production': '1CProduction.json',
            'supplier_orders': '1CSupplierOrders.json',
            'sales_channels': '1CIDProductInSalesChannel.json',
        }
    
    def load_json(self, filename: str) -> Any:
        """
        Load JSON file with proper BOM encoding handling
        
        Args:
            filename: Name of JSON file
            
        Returns:
            Parsed JSON data (usually list or dict)
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Handle BOM (Byte Order Mark)
            data = json.loads(content.decode('utf-8-sig'))
            
            logger.info(f"✅ Loaded {filename}: {len(data) if isinstance(data, list) else 'N/A'} records")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse {filename}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error loading {filename}: {e}")
            raise
    
    def load_schema_docs(self) -> Tuple[str, Dict[str, Any]]:
        """
        Load and parse DATA_SCHEMA.md
        
        Returns:
            Tuple of (full_text, parsed_metadata)
        """
        if not self.schema_path.exists():
            logger.warning(f"⚠️  Schema file not found: {self.schema_path}")
            return "", {}
        
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_text = f.read()
            
            # Parse metadata (basic extraction)
            # TODO: More sophisticated parsing with regex/LLM
            metadata = self._parse_schema_metadata(schema_text)
            
            logger.info(f"✅ Loaded schema documentation ({len(schema_text)} chars)")
            return schema_text, metadata
            
        except Exception as e:
            logger.error(f"❌ Error loading schema: {e}")
            return "", {}
    
    def _parse_schema_metadata(self, schema_text: str) -> Dict[str, Any]:
        """
        Extract business rules from schema markdown
        
        This is a simple version - can be enhanced with:
        - Regex patterns for capacities, thresholds
        - Section extraction
        - LLM-based parsing
        
        Args:
            schema_text: Full markdown text
            
        Returns:
            Dict of parsed metadata
        """
        metadata = {
            'has_schema': True,
            'schema_length': len(schema_text),
            # TODO: Extract specific rules
            # - warehouse_capacity: {...}
            # - min_stock_levels: {...}
            # - lead_times: {...}
            # - relationships: {...}
        }
        
        return metadata
    
    def extract_3_months(self, balances: List[Dict]) -> List[Dict]:
        """
        Extract last 3 months of data from daily balances
        
        Args:
            balances: List of daily balance records
            
        Returns:
            Filtered list with only last 3 months
        """
        if not balances:
            return []
        
        # Find date range
        dates = [datetime.fromisoformat(b['Date'].replace('Z', '')) for b in balances]
        latest_date = max(dates)
        cutoff_date = latest_date - timedelta(days=90)
        
        logger.info(f"📅 Date range: {min(dates).date()} to {latest_date.date()}")
        logger.info(f"📅 Extracting last 3 months: from {cutoff_date.date()}")
        
        # Filter
        filtered = [
            b for b in balances
            if datetime.fromisoformat(b['Date'].replace('Z', '')) >= cutoff_date
        ]
        
        logger.info(f"📊 Filtered: {len(balances)} → {len(filtered)} records")
        
        return filtered
    
    def validate_data(self, raw_data: Dict[str, Any]) -> List[str]:
        """
        Validate loaded data quality
        
        Args:
            raw_data: Dictionary of loaded data
            
        Returns:
            List of validation errors (empty if all OK)
        """
        errors = []
        
        # Check balances
        if 'balances' not in raw_data or not raw_data['balances']:
            errors.append("No balance data found")
        else:
            # Check structure
            first_balance = raw_data['balances'][0]
            if 'Date' not in first_balance:
                errors.append("Balance records missing 'Date' field")
            if 'Warehouses' not in first_balance:
                errors.append("Balance records missing 'Warehouses' field")
        
        # Check products
        if 'products' not in raw_data or not raw_data['products']:
            errors.append("No product data found")
        else:
            first_product = raw_data['products'][0]
            if 'IDProduct' not in first_product:
                errors.append("Product records missing 'IDProduct' field")
        
        # Check minimum data requirements
        if 'balances' in raw_data:
            num_days = len(raw_data['balances'])
            if num_days < 30:
                errors.append(f"Insufficient data: only {num_days} days (need at least 30)")
        
        if errors:
            logger.error(f"❌ Validation failed: {len(errors)} errors")
            for error in errors:
                logger.error(f"   - {error}")
        else:
            logger.info("✅ Data validation passed")
        
        return errors
    
    def run(self, use_schema: bool = True) -> Dict:
        """
        Main execution: load all data and return state update
        
        Args:
            use_schema: Whether to load schema documentation
            
        Returns:
            Dictionary to update WarehouseState
        """
        logger.info("=" * 60)
        logger.info("AGENT 1: DATA LOADER - Starting")
        logger.info("=" * 60)
        
        # Load all JSON files
        raw_data = {}
        
        try:
            raw_data['balances'] = self.load_json(self.files['balances'])
            raw_data['products'] = self.load_json(self.files['products'])
            raw_data['composition'] = self.load_json(self.files['composition'])
            raw_data['production'] = self.load_json(self.files['production'])
            raw_data['supplier_orders'] = self.load_json(self.files['supplier_orders'])
            raw_data['sales_channels'] = self.load_json(self.files['sales_channels'])
        except Exception as e:
            logger.error(f"❌ Failed to load data: {e}")
            return {
                "errors": [str(e)],
                "status": "failed"
            }
        
        # Extract 3 months
        raw_data['balances'] = self.extract_3_months(raw_data['balances'])
        
        # Validate
        validation_errors = self.validate_data(raw_data)
        
        # Load schema if requested
        schema_docs = ""
        schema_metadata = {}
        
        if use_schema:
            schema_docs, schema_metadata = self.load_schema_docs()
        
        # Prepare state update
        state_update = {
            "raw_data": raw_data,
            "data_loaded_at": datetime.now().isoformat(),
            "schema_docs": schema_docs if use_schema else None,
            "schema_metadata": schema_metadata if use_schema else None,
            "errors": validation_errors,
            "warnings": [],
            "status": "success" if not validation_errors else "partial"
        }
        
        logger.info("=" * 60)
        logger.info(f"AGENT 1: DATA LOADER - {'✅ Completed' if not validation_errors else '⚠️  Completed with warnings'}")
        logger.info(f"  - Balances: {len(raw_data.get('balances', []))} days")
        logger.info(f"  - Products: {len(raw_data.get('products', []))} items")
        logger.info(f"  - Schema loaded: {'Yes' if schema_docs else 'No'}")
        logger.info("=" * 60)
        
        return state_update


# LangGraph node wrapper
def data_loader_node(state: WarehouseState) -> Dict:
    """
    LangGraph node for Agent 1
    
    Args:
        state: Current pipeline state
        
    Returns:
        State updates from data loader
    """
    loader = WarehouseDataLoader()
    use_schema = state.get('use_schema', True)
    
    return loader.run(use_schema=use_schema)


if __name__ == "__main__":
    # Test the loader
    print("Testing Data Loader...")
    
    loader = WarehouseDataLoader()
    result = loader.run(use_schema=True)
    
    print(f"\nStatus: {result['status']}")
    print(f"Errors: {len(result['errors'])}")
    
    if result['raw_data']:
        print(f"\nData Summary:")
        print(f"  Balances: {len(result['raw_data']['balances'])} records")
        print(f"  Products: {len(result['raw_data']['products'])} records")
        
        # Show sample
        if result['raw_data']['balances']:
            print(f"\nSample Balance Record:")
            print(result['raw_data']['balances'][0])
