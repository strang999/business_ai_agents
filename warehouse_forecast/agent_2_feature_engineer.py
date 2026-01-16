"""
Agent 2: Feature Engineer

Responsibilities:
1. Transform nested JSON (Date → Warehouses → Products) into flat time series
2. Create one time series per warehouse-product combination
3. Compute derived features (velocity, fill rate, etc.)
4. Setup group attention structure for Chronos multivariate forecasting
5. Normalize and prepare data for model input

INPUT: From Agent 1
  - raw_data['balances']: Nested daily balance records
  - raw_data['products']: Product catalog
  - raw_data['composition']: Product composition (ingredients)

OUTPUT: For Agent 3 (Chronos Forecaster)
  - time_series: Dict of {series_id: [values]}
  - series_metadata: Info about each series
  - groups: Which series should share attention
  - feature_stats: Statistics for normalization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

from state import WarehouseState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WarehouseFeatureEngineer:
    """Transform raw warehouse data into time series for forecasting"""
    
    def __init__(self):
        self.min_series_length = 30  # Minimum days of data required
    
    def flatten_balances(self, balances: List[Dict]) -> pd.DataFrame:
        """
        Convert nested structure to flat DataFrame
        
        Structure:
        Input:  [{Date, Warehouses: [{IDWarehouse, Products: [{IDProduct, Balance, EndingBalance}]}]}]
        Output: DataFrame with columns [date, warehouse, product, balance]
        
        Args:
            balances: List of daily balance records
            
        Returns:
            Flattened DataFrame
        """
        logger.info("📊 Flattening nested balance data...")
        
        rows = []
        
        for day in balances:
            date = day['Date']
            
            for warehouse in day.get('Warehouses', []):
                wh_id = warehouse.get('IDWarehouse', 'UNKNOWN')
                
                for product in warehouse.get('Products', []):
                    prod_id = product.get('IDProduct', 'UNKNOWN')
                    
                    # Use EndingBalance if available, else Balance
                    balance = product.get('EndingBalance', product.get('Balance', 0))
                    
                    rows.append({
                        'date': date,
                        'warehouse': wh_id,
                        'product': prod_id,
                        'balance': balance
                    })
        
        df = pd.DataFrame(rows)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['warehouse', 'product', 'date'])
        
        logger.info(f"✅ Flattened: {len(rows)} records")
        logger.info(f"   Unique warehouses: {df['warehouse'].nunique()}")
        logger.info(f"   Unique products: {df['product'].nunique()}")
        logger.info(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        
        return df
    
    def create_time_series(self, df: pd.DataFrame) -> Tuple[Dict[str, List[float]], Dict[str, Dict]]:
        """
        Create one time series per warehouse-product pair
        
        Args:
            df: Flattened balance DataFrame
            
        Returns:
            Tuple of (time_series_dict, metadata_dict)
        """
        logger.info("🔧 Creating time series...")
        
        time_series = {}
        metadata = {}
        
        # Group by warehouse and product
        for (wh, prod), group in df.groupby(['warehouse', 'product']):
            series_id = f"{wh}_{prod}"
            
            # Sort by date and extract values
            group = group.sort_values('date')
            values = group['balance'].tolist()
            
            # Skip if too short
            if len(values) < self.min_series_length:
                logger.warning(f"⚠️  Skipping {series_id}: only {len(values)} days (min {self.min_series_length})")
                continue
            
            time_series[series_id] = values
            
            metadata[series_id] = {
                'warehouse': wh,
                'product': prod,
                'length': len(values),
                'start_date': group['date'].min().isoformat(),
                'end_date': group['date'].max().isoformat(),
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
        
        logger.info(f"✅ Created {len(time_series)} time series")
        
        return time_series, metadata
    
    def compute_velocity(self, series: List[float]) -> float:
        """
        Compute inventory velocity (average daily change)
        
        Args:
            series: Time series values
            
        Returns:
            Average daily change
        """
        if len(series) < 2:
            return 0.0
        
        changes = np.diff(series)
        return np.mean(changes)
    
    def compute_fill_rate(self, current_level: float, capacity: float = 1000) -> float:
        """
        Compute fill rate as percentage
        
        Args:
            current_level: Current inventory level
            capacity: Maximum capacity
            
        Returns:
            Fill rate (0-1)
        """
        if capacity <= 0:
            return 0.0
        
        return min(current_level / capacity, 1.0)
    
    def create_groups(self, metadata: Dict[str, Dict]) -> Dict[str, List[int]]:
        """
        Create group attention structure for Chronos multivariate forecasting
        
        Groups enable cross-learning:
        - Warehouse groups: All products in same warehouse learn from each other
        - Product groups: Same product across warehouses
        
        Args:
            metadata: Time series metadata
            
        Returns:
            Dict of {group_name: [series_indices]}
        """
        logger.info("🏗️  Creating group attention structure...")
        
        groups = {
            'warehouses': {},
            'products': {}
        }
        
        # Create index mapping
        series_ids = list(metadata.keys())
        
        # Group by warehouse
        for idx, series_id in enumerate(series_ids):
            wh = metadata[series_id]['warehouse']
            if wh not in groups['warehouses']:
                groups['warehouses'][wh] = []
            groups['warehouses'][wh].append(idx)
        
        # Group by product
        for idx, series_id in enumerate(series_ids):
            prod = metadata[series_id]['product']
            if prod not in groups['products']:
                groups['products'][prod] = []
            groups['products'][prod].append(idx)
        
        logger.info(f"✅ Created groups:")
        logger.info(f"   Warehouse groups: {len(groups['warehouses'])}")
        logger.info(f"   Product groups: {len(groups['products'])}")
        
        return groups
    
    def normalize_series(self, time_series: Dict[str, List[float]]) -> Tuple[Dict[str, List[float]], Dict[str, Dict]]:
        """
        Normalize time series for better model performance
        
        Uses z-score normalization: (x - mean) / std
        
        Args:
            time_series: Raw time series
            
        Returns:
            Tuple of (normalized_series, normalization_params)
        """
        logger.info("📏 Normalizing time series...")
        
        normalized = {}
        norm_params = {}
        
        for series_id, values in time_series.items():
            mean = np.mean(values)
            std = np.std(values)
            
            # Avoid division by zero
            if std == 0:
                std = 1.0
                logger.warning(f"⚠️  {series_id}: zero std, using 1.0")
            
            normalized_values = [(v - mean) / std for v in values]
            
            normalized[series_id] = normalized_values
            norm_params[series_id] = {'mean': mean, 'std': std}
        
        logger.info(f"✅ Normalized {len(normalized)} series")
        
        return normalized, norm_params
    
    def run(self, state: WarehouseState) -> Dict:
        """
        Main execution: transform data for forecasting
        
        Args:
            state: Current pipeline state
            
        Returns:
            State updates for Feature Engineer
        """
        logger.info("=" * 60)
        logger.info("AGENT 2: FEATURE ENGINEER - Starting")
        logger.info("=" * 60)
        
        raw_data = state.get('raw_data', {})
        
        if not raw_data or 'balances' not in raw_data:
            logger.error("❌ No data provided from Agent 1")
            return {
                "errors": state.get('errors', []) + ["No data from Agent 1"],
                "status": "failed"
            }
        
        try:
            # Step 1: Flatten nested structure
            df = self.flatten_balances(raw_data['balances'])
            
            # Step 2: Create time series
            time_series, metadata = self.create_time_series(df)
            
            if not time_series:
                logger.error("❌ No valid time series created")
                return {
                    "errors": state.get('errors', []) + ["No valid time series"],
                    "status": "failed"
                }
            
            # Step 3: Create groups for multivariate attention
            groups = self.create_groups(metadata)
            
            # Step 4: Normalize (optional - Chronos can handle raw values)
            # For now, skip normalization and let Chronos handle it
            # normalized, norm_params = self.normalize_series(time_series)
            
            # Compute statistics
            feature_stats = {
                'num_series': len(time_series),
                'total_length': sum(len(v) for v in time_series.values()),
                'avg_length': np.mean([len(v) for v in time_series.values()]),
                'num_warehouses': len(groups['warehouses']),
                'num_products': len(groups['products']),
            }
            
            state_update = {
                "time_series": time_series,
                "series_metadata": metadata,
                "groups": groups,
                "feature_stats": feature_stats,
                "warnings": state.get('warnings', []),
                "errors": state.get('errors', []),
                "status": "success"
            }
            
            logger.info("=" * 60)
            logger.info("AGENT 2: FEATURE ENGINEER - ✅ Completed")
            logger.info(f"  - Time series created: {len(time_series)}")
            logger.info(f"  - Warehouse groups: {len(groups['warehouses'])}")
            logger.info(f"  - Product groups: {len(groups['products'])}")
            logger.info(f"  - Avg series length: {feature_stats['avg_length']:.1f} days")
            logger.info("=" * 60)
            
            return state_update
            
        except Exception as e:
            logger.error(f"❌ Feature engineering failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "errors": state.get('errors', []) + [str(e)],
                "status": "failed"
            }


# LangGraph node wrapper
def feature_engineer_node(state: WarehouseState) -> Dict:
    """
    LangGraph node for Agent 2
    
    Args:
        state: Current pipeline state
        
    Returns:
        State updates from feature engineer
    """
    engineer = WarehouseFeatureEngineer()
    return engineer.run(state)


if __name__ == "__main__":
    # Test with sample data
    print("Testing Feature Engineer...")
    
    # Create mock state from Agent 1
    mock_state = {
        'raw_data': {
            'balances': [
                {
                    'Date': '2024-01-01T00:00:00',
                    'Warehouses': [
                        {
                            'IDWarehouse': 'WH_01',
                            'Products': [
                                {'IDProduct': 'PROD_A', 'EndingBalance': 100},
                                {'IDProduct': 'PROD_B', 'EndingBalance': 200}
                            ]
                        }
                    ]
                },
                {
                    'Date': '2024-01-02T00:00:00',
                    'Warehouses': [
                        {
                            'IDWarehouse': 'WH_01',
                            'Products': [
                                {'IDProduct': 'PROD_A', 'EndingBalance': 110},
                                {'IDProduct': 'PROD_B', 'EndingBalance': 190}
                            ]
                        }
                    ]
                }
            ] * 40,  # Repeat to get 80 days
            'products': [],
            'composition': []
        },
        'errors': [],
        'warnings': []
    }
    
    engineer = WarehouseFeatureEngineer()
    result = engineer.run(mock_state)
    
    print(f"\nStatus: {result['status']}")
    print(f"Time series created: {len(result.get('time_series', {}))}")
    print(f"Feature stats: {result.get('feature_stats', {})}")
