"""
Quick Validation - Fast accuracy check with sampling

Instead of forecasting ALL products (slow), sample top products
and validate accuracy faster.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import logging

from agent_1_data_loader import WarehouseDataLoader
from agent_2_feature_engineer import WarehouseFeatureEngineer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def quick_validation():
    """Fast validation with sampling"""
    
    logger.info("=" * 80)
    logger.info("QUICK VALIDATION - Sampled Products")
    logger.info("=" * 80)
    
    # Load data
    loader = WarehouseDataLoader()
    balances = loader.load_json('1CDailyBalances.json')
    balances = loader.extract_3_months(balances)
    
    logger.info(f"\nTotal data: {len(balances)} days")
    
    # Split 70/30
    split_idx = int(len(balances) * 0.7)
    train_balances = balances[:split_idx]
    test_balances = balances[split_idx:]
    
    logger.info(f"Train: {len(train_balances)} days")
    logger.info(f"Test: {len(test_balances)} days")
    
    # Create features
    engineer = WarehouseFeatureEngineer()
    
    # Train data
    train_df = engineer.flatten_balances(train_balances)
    train_series, train_metadata = engineer.create_time_series(train_df)
    
    # Test data (actual values)
    test_df = engineer.flatten_balances(test_balances)
    test_series, test_metadata = engineer.create_time_series(test_df)
    
    logger.info(f"\nTrain series: {len(train_series)}")
    logger.info(f"Test series: {len(test_series)}")
    
    # Sample top 10 products by volume
    volumes = {sid: np.mean(values) for sid, values in train_series.items()}
    top_10 = sorted(volumes.items(), key=lambda x: x[1], reverse=True)[:10]
    
    logger.info(f"\nSampling top 10 products by volume:")
    for sid, vol in top_10:
        logger.info(f"  {sid}: {vol:.0f}")
    
    # Simple forecast: naive (last value repeated)
    logger.info(f"\nGenerating naive forecasts...")
    
    results = {}
    for series_id, _ in top_10:
        if series_id not in train_series or series_id not in test_series:
            continue
        
        # Naive forecast: last value
        last_value = train_series[series_id][-1]
        forecast_length = len(test_series[series_id])
        naive_forecast = [last_value] * forecast_length
        
        actual = test_series[series_id]
        
        # Calculate MAPE
        actual_arr = np.array(actual)
        forecast_arr = np.array(naive_forecast)
        
        mask = actual_arr != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((actual_arr[mask] - forecast_arr[mask]) / actual_arr[mask])) * 100
        else:
            mape = np.nan
        
        # RMSE
        rmse = np.sqrt(np.mean((actual_arr - forecast_arr) ** 2))
        
        results[series_id] = {
            'mape': mape,
            'rmse': rmse,
            'actual_mean': np.mean(actual),
            'forecast_mean': np.mean(naive_forecast)
        }
        
        logger.info(f"\n{series_id}:")
        logger.info(f"  MAPE: {mape:.2f}%")
        logger.info(f"  RMSE: {rmse:.2f}")
        logger.info(f"  Actual mean: {np.mean(actual):.0f}")
        logger.info(f"  Forecast mean: {np.mean(naive_forecast):.0f}")
    
    # Overall
    avg_mape = np.mean([r['mape'] for r in results.values() if not np.isnan(r['mape'])])
    logger.info(f"\n{'='*80}")
    logger.info(f"OVERALL NAIVE BASELINE:")
    logger.info(f"  Average MAPE: {avg_mape:.2f}%")
    logger.info(f"  (Chronos should beat this!)")
    logger.info(f"{'='*80}")
    
    return results


if __name__ == "__main__":
    results = quick_validation()
    print("\n✅ Quick validation completed!")
    print(f"Naive baseline MAPE: ~{np.mean([r['mape'] for r in results.values() if not np.isnan(r['mape'])]):.1f}%")
    print("Chronos model should achieve 8-12% MAPE for good performance")
