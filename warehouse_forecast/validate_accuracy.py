"""
Backtest Validation Script

Tests forecast accuracy by:
1. Split data: First 60 days (train) vs Last 30 days (test)
2. Forecast 30 days using first 60 days
3. Compare predicted vs actual for each warehouse-product
4. Calculate MAPE, RMSE, MAE per product
5. Show detailed results
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import logging

from agent_1_data_loader import WarehouseDataLoader
from agent_2_feature_engineer import WarehouseFeatureEngineer
from agent_3_chronos_forecaster import ChronosForecaster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForecastValidator:
    """Validate forecast accuracy against actual data"""
    
    def __init__(self):
        self.loader = WarehouseDataLoader()
        self.engineer = WarehouseFeatureEngineer()
        
    def split_train_test(self, balances, train_days=60, test_days=30):
        """
        Split data into train and test
        
        Args:
            balances: All balance records
            train_days: Days for training context
            test_days: Days to forecast and validate
            
        Returns:
            (train_balances, test_balances)
        """
        if len(balances) < train_days + test_days:
            logger.warning(f"Not enough data: {len(balances)} days (need {train_days + test_days})")
            # Use what we have
            split_point = len(balances) - test_days
            if split_point < 30:
                split_point = 30  # Minimum for train
        else:
            split_point = train_days
        
        train = balances[:split_point]
        test = balances[split_point:split_point + test_days]
        
        logger.info(f"Split: {len(train)} train days, {len(test)} test days")
        
        return train, test
    
    def extract_actual_values(self, test_balances):
        """
        Extract actual values from test period
        
        Returns:
            Dict of {series_id: [actual_values]}
        """
        df = self.engineer.flatten_balances(test_balances)
        
        actual = {}
        for (wh, prod), group in df.groupby(['warehouse', 'product']):
            series_id = f"{wh}_{prod}"
            values = group.sort_values('date')['balance'].tolist()
            actual[series_id] = values
        
        return actual
    
    def calculate_metrics(self, actual, predicted):
        """
        Calculate accuracy metrics
        
        Args:
            actual: List of actual values
            predicted: List of predicted values (mean)
            
        Returns:
            Dict with MAPE, RMSE, MAE
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # Ensure same length
        min_len = min(len(actual), len(predicted))
        actual = actual[:min_len]
        predicted = predicted[:min_len]
        
        # MAPE (Mean Absolute Percentage Error)
        # Avoid division by zero
        mask = actual != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        else:
            mape = np.nan
        
        # RMSE (Root Mean Squared Error)
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # MAE (Mean Absolute Error)
        mae = np.mean(np.abs(actual - predicted))
        
        # Directional accuracy (trend)
        if len(actual) > 1:
            actual_trend = actual[-1] > actual[0]
            pred_trend = predicted[-1] > predicted[0]
            trend_correct = actual_trend == pred_trend
        else:
            trend_correct = None
        
        return {
            'mape': mape,
            'rmse': rmse,
            'mae': mae,
            'trend_correct': trend_correct,
            'actual_mean': np.mean(actual),
            'predicted_mean': np.mean(predicted),
            'actual_last': actual[-1] if len(actual) > 0 else None,
            'predicted_last': predicted[-1] if len(predicted) > 0 else None,
        }
    
    def run_validation(self):
        """
        Main validation: backtest forecasts
        
        Returns:
            Dict with detailed results per product
        """
        logger.info("=" * 80)
        logger.info("FORECAST VALIDATION - BACKTESTING")
        logger.info("=" * 80)
        
        # Load all data
        logger.info("\n1. Loading data...")
        raw_data = self.loader.load_json(self.loader.files['balances'])
        raw_data = self.loader.extract_3_months(raw_data)
        
        logger.info(f"   Total data: {len(raw_data)} days")
        
        # Split train/test
        logger.info("\n2. Splitting train/test...")
        train_balances, test_balances = self.split_train_test(raw_data)
        
        # Extract actual values from test period
        logger.info("\n3. Extracting actual test values...")
        actual_values = self.extract_actual_values(test_balances)
        logger.info(f"   Found {len(actual_values)} series in test period")
        
        # Create features from train data only
        logger.info("\n4. Creating features from train data...")
        state = {'raw_data': {'balances': train_balances, 'products': [], 'composition': []}}
        feature_result = self.engineer.run(state)
        
        if feature_result['status'] != 'success':
            logger.error("Feature engineering failed!")
            return None
        
        train_series = feature_result['time_series']
        logger.info(f"   Created {len(train_series)} training series")
        
        # Forecast using train data
        logger.info("\n5. Generating forecasts...")
        forecast_horizon = min(len(test_balances), 30)  # Limit to available test data
        logger.info(f"   Forecasting {forecast_horizon} days ahead")
        
        # Simple forecast without full agent
        try:
            from chronos import ChronosPipeline
            import torch
            
            logger.info("   Loading Chronos model...")
            pipeline = ChronosPipeline.from_pretrained(
                "amazon/chronos-t5-tiny",
                device_map="cpu",  # Use CPU to avoid CUDA issues
                torch_dtype=torch.float32
            )
            logger.info("   Model loaded successfully")
            
            # Forecast each series
            forecasts = {}
            logger.info(f"   Forecasting {len(train_series)} series...")
            
            for idx, (series_id, series_values) in enumerate(train_series.items()):
                if (idx + 1) % 10 == 0:
                    logger.info(f"      Progress: {idx + 1}/{len(train_series)}")
                
                try:
                    # Convert to tensor
                    context = torch.tensor([series_values], dtype=torch.float32)
                    
                    # Forecast
                    forecast = pipeline.predict(
                        context,
                        prediction_length=forecast_horizon,
                        num_samples=20  # Reduced for speed
                    )
                    
                    # Extract mean
                    mean_forecast = forecast[0].mean(dim=0).tolist()
                    
                    forecasts[series_id] = {
                        'mean': mean_forecast
                    }
                    
                except Exception as e:
                    logger.warning(f"      Failed to forecast {series_id}: {e}")
                    continue
            
            logger.info(f"   Successfully forecasted {len(forecasts)} series")
            
        except Exception as e:
            logger.error(f"Forecasting failed: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Compare predicted vs actual
        logger.info("\n6. Calculating accuracy metrics...")
        results = {}
        
        for series_id in train_series.keys():
            if series_id not in actual_values:
                continue
            
            if series_id not in forecasts:
                continue
            
            actual = actual_values[series_id]
            predicted = forecasts[series_id]['mean']
            
            metrics = self.calculate_metrics(actual, predicted)
            
            # Extract warehouse and product
            parts = series_id.split('_', 1)
            warehouse = parts[0] if len(parts) > 0 else 'UNKNOWN'
            product = parts[1] if len(parts) > 1 else 'UNKNOWN'
            
            results[series_id] = {
                'warehouse': warehouse,
                'product': product,
                'metrics': metrics,
                'actual': actual,
                'predicted': predicted,
                'length': len(actual)
            }
        
        logger.info(f"   Validated {len(results)} products")
        
        # Print detailed results
        self.print_results(results)
        
        # Save results
        self.save_results(results)
        
        return results
    
    def print_results(self, results):
        """Print detailed validation results"""
        logger.info("\n" + "=" * 80)
        logger.info("DETAILED VALIDATION RESULTS")
        logger.info("=" * 80)
        
        if not results:
            logger.warning("No results to display")
            return
        
        # Calculate overall metrics
        all_mapes = [r['metrics']['mape'] for r in results.values() if not np.isnan(r['metrics']['mape'])]
        all_rmses = [r['metrics']['rmse'] for r in results.values()]
        all_maes = [r['metrics']['mae'] for r in results.values()]
        trend_correct = [r['metrics']['trend_correct'] for r in results.values() if r['metrics']['trend_correct'] is not None]
        
        logger.info(f"\n📊 OVERALL METRICS (across {len(results)} products):")
        logger.info(f"   Average MAPE: {np.mean(all_mapes):.2f}%")
        logger.info(f"   Median MAPE:  {np.median(all_mapes):.2f}%")
        logger.info(f"   Average RMSE: {np.mean(all_rmses):.2f}")
        logger.info(f"   Average MAE:  {np.mean(all_maes):.2f}")
        if trend_correct:
            logger.info(f"   Trend Accuracy: {np.mean(trend_correct) * 100:.1f}%")
        
        # Best and worst products
        sorted_by_mape = sorted(
            [(sid, r['metrics']['mape']) for sid, r in results.items() if not np.isnan(r['metrics']['mape'])],
            key=lambda x: x[1]
        )
        
        logger.info(f"\n✅ TOP 5 BEST FORECASTS (lowest MAPE):")
        for i, (series_id, mape) in enumerate(sorted_by_mape[:5], 1):
            r = results[series_id]
            logger.info(f"   {i}. {series_id}")
            logger.info(f"      MAPE: {mape:.2f}%, RMSE: {r['metrics']['rmse']:.2f}")
            logger.info(f"      Actual: {r['metrics']['actual_last']:.0f}, Predicted: {r['metrics']['predicted_last']:.0f}")
        
        logger.info(f"\n❌ TOP 5 WORST FORECASTS (highest MAPE):")
        for i, (series_id, mape) in enumerate(sorted_by_mape[-5:][::-1], 1):
            r = results[series_id]
            logger.info(f"   {i}. {series_id}")
            logger.info(f"      MAPE: {mape:.2f}%, RMSE: {r['metrics']['rmse']:.2f}")
            logger.info(f"      Actual: {r['metrics']['actual_last']:.0f}, Predicted: {r['metrics']['predicted_last']:.0f}")
        
        # Per-warehouse summary
        warehouses = set(r['warehouse'] for r in results.values())
        logger.info(f"\n🏭 PER-WAREHOUSE ACCURACY:")
        for wh in sorted(warehouses):
            wh_results = {k: v for k, v in results.items() if v['warehouse'] == wh}
            wh_mapes = [r['metrics']['mape'] for r in wh_results.values() if not np.isnan(r['metrics']['mape'])]
            if wh_mapes:
                logger.info(f"   {wh}: Avg MAPE = {np.mean(wh_mapes):.2f}% ({len(wh_results)} products)")
    
    def save_results(self, results):
        """Save validation results to JSON"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = output_dir / f"validation_results_{timestamp}.json"
        
        # Convert numpy types to native Python
        serializable = {}
        for series_id, data in results.items():
            serializable[series_id] = {
                'warehouse': data['warehouse'],
                'product': data['product'],
                'metrics': {
                    k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                    for k, v in data['metrics'].items()
                },
                'actual': [float(x) for x in data['actual']],
                'predicted': [float(x) for x in data['predicted']],
                'length': data['length']
            }
        
        with open(filepath, 'w') as f:
            json.dump(serializable, f, indent=2)
        
        logger.info(f"\n💾 Results saved to: {filepath}")


if __name__ == "__main__":
    validator = ForecastValidator()
    results = validator.run_validation()
    
    if results:
        print("\n✅ Validation completed! Check output/validation_results_*.json for details")
    else:
        print("\n❌ Validation failed")
