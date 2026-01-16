"""
Agent 4: Business Rules Validator

Responsibilities:
1. Apply business constraints to forecasts
2. Calculate key metrics (days until full/empty)
3. Validate against capacity limits
4. Flag constraint violations
5. Prepare data for alert generation

INPUT: From Agent 3
  - forecasts: {series_id: {mean, q10, q50, q90}}
  - series_metadata: Warehouse/product info

OUTPUT: For Agent 5
  - metrics: {series_id: {days_until_full, days_until_shortage, ...}}
  - constraint_violations: List of issues
"""

import numpy as np
from typing import Dict, List, Any
import logging

from config import WAREHOUSE_CAPACITY, MIN_STOCK_LEVELS, ALERT_THRESHOLDS
from state import WarehouseState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessRulesValidator:
    """Validate forecasts against business rules"""
    
    def __init__(self):
        self.warehouse_capacity = WAREHOUSE_CAPACITY
        self.min_stock = MIN_STOCK_LEVELS
        self.thresholds = ALERT_THRESHOLDS
    
    def calculate_days_until_full(
        self,
        forecast_mean: List[float],
        capacity: float = 1000
    ) -> int | None:
        """
        Calculate days until warehouse hits capacity
        
        Args:
            forecast_mean: Predicted values
            capacity: Maximum capacity
            
        Returns:
            Days until >=95% full, or None if never reaches
        """
        threshold = capacity * 0.95
        
        for day, value in enumerate(forecast_mean):
            if value >= threshold:
                return day + 1  # 1-indexed
        
        return None  # Never hits capacity in forecast horizon
    
    def calculate_days_until_shortage(
        self,
        forecast_mean: List[float],
        min_level: float = 50
    ) -> int | None:
        """
        Calculate days until shortage
        
        Args:
            forecast_mean: Predicted values
            min_level: Minimum acceptable level
            
        Returns:
            Days until shortage, or None if sufficient
        """
        for day, value in enumerate(forecast_mean):
            if value <= min_level:
                return day + 1
        
        return None
    
    def run(self, state: WarehouseState) -> Dict:
        """
        Main execution: validate forecasts
        
        Args:
            state: Current pipeline state
            
        Returns:
            State updates with metrics
        """
        logger.info("=" * 60)
        logger.info("AGENT 4: BUSINESS RULES VALIDATOR - Starting")
        logger.info("=" * 60)
        
        forecasts = state.get('forecasts', {})
        series_metadata = state.get('series_metadata', {})
        time_series = state.get('time_series', {})
        
        if not forecasts:
            logger.error("❌ No forecasts from Agent 3")
            return {
                "errors": state.get('errors', []) + ["No forecasts"],
                "status": "failed"
            }
        
        metrics = {}
        violations = []
        applied_rules = []
        
        for series_id, forecast in forecasts.items():
            # Get current level
            current_level = time_series[series_id][-1] if series_id in time_series else 0
            
            # Extract warehouse and product
            metadata = series_metadata.get(series_id, {})
            warehouse = metadata.get('warehouse', 'UNKNOWN')
            product = metadata.get('product', 'UNKNOWN')
            
            # Get capacity (default or specific)
            capacity = self.warehouse_capacity.get(warehouse, 
                                                   self.warehouse_capacity.get('default', 1000))
            
            # Get min stock (default or specific)
            min_stock = self.min_stock.get(product,
                                          self.min_stock.get('default', 50))
            
            # Calculate metrics
            days_until_full = self.calculate_days_until_full(forecast['mean'], capacity)
            days_until_shortage = self.calculate_days_until_shortage(forecast['mean'], min_stock)
            
            metrics[series_id] = {
                'warehouse': warehouse,
                'product': product,
                'current_level': current_level,
                'forecast_30d': forecast['mean'][-1],  # Last forecasted value
                'capacity': capacity,
                'min_stock': min_stock,
                'days_until_full': days_until_full,
                'days_until_shortage': days_until_shortage,
                'fill_rate_current': current_level / capacity if capacity > 0 else 0,
                'trend': 'increasing' if forecast['mean'][-1] > current_level else 'decreasing',
            }
            
            # Check violations
            if days_until_full and days_until_full <= self.thresholds['warehouse_overflow_days']:
                violations.append(f"{series_id}: Overflow risk in {days_until_full} days")
            
            if days_until_shortage and days_until_shortage <= self.thresholds['ingredient_shortage_days']:
                violations.append(f"{series_id}: Shortage risk in {days_until_shortage} days")        
        logger.info(f"✅ Validated {len(metrics)} forecasts")
        logger.info(f"⚠️  Found {len(violations)} violations")
        
        state_update = {
            "validated_forecasts": forecasts,
            "metrics": metrics,
            "constraint_violations": violations,
            "applied_rules": ['capacity_check', 'min_stock_check'],
            "errors": state.get('errors', []),
            "warnings": state.get('warnings', []),
            "status": "success"
        }
        
        logger.info("=" * 60)
        logger.info("AGENT 4: BUSINESS RULES - ✅ Completed")
        logger.info(f"  - Metrics calculated: {len(metrics)}")
        logger.info(f"  - Violations found: {len(violations)}")
        logger.info("=" * 60)
        
        return state_update


def business_rules_node(state: WarehouseState) -> Dict:
    """LangGraph node for Agent 4"""
    validator = BusinessRulesValidator()
    return validator.run(state)
