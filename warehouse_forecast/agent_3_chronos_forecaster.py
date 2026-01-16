"""
Agent 3: Chronos Forecaster

Responsibilities:
1. Load Chronos-2 model (optimized for RTX 3070 8GB)
2. Run multivariate forecasting on time series
3. Generate probabilistic predictions (quantiles)
4. Handle batch processing to avoid OOM
5. Return forecasts with confidence intervals

CRITICAL: Memory optimization for 8GB VRAM
- Use bfloat16 precision
- Batch processing (50 series at a time)
- Optional INT8 quantization if OOM

INPUT: From Agent 2
  - time_series: Dict of {series_id: [values]}
  - series_metadata: Info about each series
  - groups: Group attention structure

OUTPUT: For Agent 4 (Business Rules)
  - forecasts: Dict of {series_id: {mean, q10, q50, q90}}
  - model_used: Which model was loaded
  - inference_time: Performance metrics
"""

import torch
import numpy as np
from typing import Dict, List, Any
import time
import logging

from chronos import ChronosPipeline

from config import MODEL_CONFIG, FORECAST_HORIZON, QUANTILE_LEVELS
from state import WarehouseState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChronosForecaster:
    """Wrapper around Chronos-2 for warehouse forecasting"""
    
    def __init__(
        self,
        model_name: str = MODEL_CONFIG['name'],
        device: str = MODEL_CONFIG['device'],
        dtype: str = MODEL_CONFIG['dtype'],
        batch_size: int = MODEL_CONFIG['batch_size']
    ):
        self.model_name = model_name
        self.device = device
        self.dtype = dtype
        self.batch_size = batch_size
        self.pipeline = None
        
    def load_model(self):
        """
        Load Chronos-2 model with memory optimization
        
        Strategies for RTX 3070 8GB:
        1. Use bfloat16 (saves 50% memory vs float32)        2. Batch processing
        3. If OOM → use smaller model or INT8 quantization
        """
        logger.info(f"📥 Loading model: {self.model_name}")
        logger.info(f"   Device: {self.device}")
        logger.info(f"   Dtype: {self.dtype}")
        
        try:
            torch_dtype = getattr(torch, self.dtype)
            
            self.pipeline = ChronosPipeline.from_pretrained(
                self.model_name,
                device_map=self.device,
                torch_dtype=torch_dtype
            )
            
            # Check VRAM usage
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1024**3
                reserved = torch.cuda.memory_reserved() / 1024**3
                logger.info(f"✅ Model loaded")
                logger.info(f"   VRAM allocated: {allocated:.2f} GB")
                logger.info(f"   VRAM reserved: {reserved:.2f} GB")
                
                if reserved > 7.5:
                    logger.warning(f"⚠️  High VRAM usage ({reserved:.2f} GB / 8 GB)")
                    logger.warning(f"   Consider using smaller model or INT8 quantization")
            else:
                logger.info(f"✅ Model loaded on CPU")
            
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                logger.error(f"❌ OOM Error! Model too large for 8GB VRAM")
                logger.error(f"   Suggestions:")
                logger.error(f"   1. Use chronos-2-tiny instead of small")
                logger.error(f"   2. Enable INT8 quantization")
                logger.error(f"   3. Use CPU (slower but works)")
                raise
            else:
                raise
    
    def forecast_batch(
        self,
        series_batch: List[List[float]],
        horizon: int = FORECAST_HORIZON
    ) -> List[Dict[str, List[float]]]:
        """
        Forecast a batch of time series
        
        Args:
            series_batch: List of time series (each is list of floats)
            horizon: Days ahead to forecast
            
        Returns:
            List of forecast dicts with quantiles
        """
        if not self.pipeline:
            raise ValueError("Model not loaded! Call load_model() first")
        
        # Convert to tensor
        # Pad series to same length if needed
        max_len = max(len(s) for s in series_batch)
        
        padded_series = []
        for series in series_batch:
            if len(series) < max_len:
                # Pad with first value
                padding = [series[0]] * (max_len - len(series))
                padded = padding + series
            else:
                padded = series
            padded_series.append(padded)
        
        context = torch.tensor(padded_series, dtype=torch.float32)
        
        # Forecast
        forecast = self.pipeline.predict(
            context,
            prediction_length=horizon,
            num_samples=100  # For probabilistic forecasting
        )
        
        # Extract quantiles
        batch_forecasts = []
        
        for i in range(len(series_batch)):
            series_forecast = forecast[i]  # [num_samples, horizon]
            
            forecast_dict = {
                'mean': series_forecast.mean(dim=0).tolist(),
                'q10': series_forecast.quantile(0.10, dim=0).tolist(),
                'q50': series_forecast.quantile(0.50, dim=0).tolist(),
                'q90': series_forecast.quantile(0.90, dim=0).tolist(),
            }
            
            batch_forecasts.append(forecast_dict)
        
        return batch_forecasts
    
    def forecast_all(
        self,
        time_series: Dict[str, List[float]],
        horizon: int = FORECAST_HORIZON
    ) -> Dict[str, Dict[str, List[float]]]:
        """
        Forecast all time series with batch processing
        
        Args:
            time_series: Dict of {series_id: [values]}
            horizon: Days ahead
            
        Returns:
            Dict of {series_id: {mean, q10, q50, q90}}
        """
        logger.info(f"🔮 Forecasting {len(time_series)} series...")
        logger.info(f"   Horizon: {horizon} days")
        logger.info(f"   Batch size: {self.batch_size}")
        
        all_forecasts = {}
        series_ids = list(time_series.keys())
        series_values = list(time_series.values())
        
        num_batches = (len(series_ids) + self.batch_size - 1) // self.batch_size
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(series_ids))
            
            batch_ids = series_ids[start_idx:end_idx]
            batch_series = series_values[start_idx:end_idx]
            
            logger.info(f"   Processing batch {batch_idx + 1}/{num_batches} ({len(batch_ids)} series)...")
            
            try:
                batch_forecasts = self.forecast_batch(batch_series, horizon)
                
                for series_id, forecast in zip(batch_ids, batch_forecasts):
                    all_forecasts[series_id] = forecast
                
                # Free GPU memory
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    logger.error(f"❌ OOM in batch {batch_idx + 1}")
                    logger.error(f"   Try reducing batch_size from {self.batch_size}")
                    raise
                else:
                    raise
        
        logger.info(f"✅ Forecasted {len(all_forecasts)} series")
        
        return all_forecasts
    
    def run(self, state: WarehouseState) -> Dict:
        """
        Main execution: load model and forecast
        
        Args:
            state: Current pipeline state
            
        Returns:
            State updates for Forecaster
        """
        logger.info("=" * 60)
        logger.info("AGENT 3: CHRONOS FORECASTER - Starting")
        logger.info("=" * 60)
        
        time_series = state.get('time_series', {})
        
        if not time_series:
            logger.error("❌ No time series provided from Agent 2")
            return {
                "errors": state.get('errors', []) + ["No time series from Agent 2"],
                "status": "failed"
            }
        
        try:
            # Load model
            start_time = time.time()
            self.load_model()
            load_time = time.time() - start_time
            
            logger.info(f"⏱️  Model load time: {load_time:.2f}s")
            
            # Forecast
            horizon = state.get('forecast_horizon', FORECAST_HORIZON)
            
            inference_start = time.time()
            forecasts = self.forecast_all(time_series, horizon)
            inference_time = time.time() - inference_start
            
            # Get peak VRAM
            memory_used = 0.0
            if torch.cuda.is_available():
                memory_used = torch.cuda.max_memory_allocated() / 1024**3
            
            state_update = {
                "forecasts": forecasts,
                "model_used": self.model_name,
                "model_config": {
                    "device": self.device,
                    "dtype": self.dtype,
                    "batch_size": self.batch_size
                },
                "inference_time_seconds": inference_time,
                "memory_used_gb": memory_used,
                "errors": state.get('errors', []),
                "warnings": state.get('warnings', []),
                "status": "success"
            }
            
            logger.info("=" * 60)
            logger.info("AGENT 3: CHRONOS FORECASTER - ✅ Completed")
            logger.info(f"  - Forecasts generated: {len(forecasts)}")
            logger.info(f"  - Horizon: {horizon} days")
            logger.info(f"  - Inference time: {inference_time:.2f}s")
            logger.info(f"  - Avg time per series: {inference_time / len(forecasts):.3f}s")
            logger.info(f"  - Peak VRAM: {memory_used:.2f} GB")
            logger.info("=" * 60)
            
            return state_update
            
        except Exception as e:
            logger.error(f"❌ Forecasting failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "errors": state.get('errors', []) + [str(e)],
                "status": "failed"
            }


# LangGraph node wrapper
def chronos_forecaster_node(state: WarehouseState) -> Dict:
    """
    LangGraph node for Agent 3
    
    Args:
        state: Current pipeline state
        
    Returns:
        State updates from forecaster
    """
    forecaster = ChronosForecaster()
    return forecaster.run(state)


if __name__ == "__main__":
    # Test forecaster with mock data
    print("Testing Chronos Forecaster...")
    
    # Create mock state
    mock_state = {
        'time_series': {
            'WH_01_PROD_A': [100, 105, 110, 108, 112, 115] * 10,  # 60 days
            'WH_01_PROD_B': [200, 195, 190, 185, 180, 175] * 10,
        },
        'forecast_horizon': 10,
        'errors': [],
        'warnings': []
    }
    
    forecaster = ChronosForecaster(
        model_name="amazon/chronos-t5-tiny",  # Use tiny for fast testing
        batch_size=2
    )
    
    result = forecaster.run(mock_state)
    
    print(f"\nStatus: {result['status']}")
    print(f"Forecasts: {len(result.get('forecasts', {}))}")
    print(f"Inference time: {result.get('inference_time_seconds', 0):.2f}s")
    print(f"Memory used: {result.get('memory_used_gb', 0):.2f} GB")
    
    # Show sample forecast
    if result.get('forecasts'):
        first_id = list(result['forecasts'].keys())[0]
        first_forecast = result['forecasts'][first_id]
        print(f"\nSample forecast ({first_id}):")
        print(f"  Mean (first 5): {first_forecast['mean'][:5]}")
        print(f"  Q10 (first 5): {first_forecast['q10'][:5]}")
        print(f"  Q90 (first 5): {first_forecast['q90'][:5]}")
