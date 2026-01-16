"""
Agent 5: Alert Generator

Responsibilities:
1. Analyze metrics for issues
2. Create prioritized alerts (HIGH/MEDIUM/LOW)
3. Generate actionable recommendations
4. Format for different outputs

INPUT: From Agent 4
  - metrics: Per-series metrics
  - constraint_violations: List of violations

OUTPUT: For Agent 6
  - alerts: List of structured alerts
  - alert_summary: Count by severity
"""

import logging
from typing import Dict, List, Any

from config import ALERT_THRESHOLDS
from state import WarehouseState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertGenerator:
    """Generate actionable alerts from forecasts"""
    
    def __init__(self):
        self.thresholds = ALERT_THRESHOLDS
    
    def create_alert(
        self,
        alert_type: str,
        series_id: str,
        warehouse: str,
        product: str,
        days_remaining: int,
        current_level: float,
        forecast_level: float,
        confidence: float = 0.85
    ) -> Dict[str, Any]:
        """
        Create structured alert
        
        Returns:
            Alert dict with type, severity, action, etc.
        """
        # Determine severity
        if days_remaining <= self.thresholds['critical_days']:
            severity = 'HIGH'
        elif days_remaining <= 7:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'
        
        # Generate action
        if alert_type == 'WAREHOUSE_OVERFLOW':
            action = f"Increase distribution from {warehouse} or reduce production of {product}"
        elif alert_type == 'INGREDIENT_SHORTAGE':
            action = f"Reorder {product} for {warehouse} immediately (lead time: 7-14 days)"
        else:
            action = "Review and take appropriate action"
        
        return {
            'id': f"{alert_type}_{series_id}",
            'type': alert_type,
            'severity': severity,
            'warehouse': warehouse,
            'product': product,
            'days_remaining': days_remaining,
            'current_level': round(current_level, 2),
            'forecast_level': round(forecast_level, 2),
            'confidence': confidence,
            'action': action,
            'deadline': f"{days_remaining} days"
        }
    
    def run(self, state: WarehouseState) -> Dict:
        """
        Main execution: generate alerts
        
        Args:
            state: Current pipeline state
            
        Returns:
            State updates with alerts
        """
        logger.info("=" * 60)
        logger.info("AGENT 5: ALERT GENERATOR - Starting")
        logger.info("=" * 60)
        
        metrics = state.get('metrics', {})
        
        if not metrics:
            logger.error("❌ No metrics from Agent 4")
            return {
                "errors": state.get('errors', []) + ["No metrics"],
                "status": "failed"
            }
        
        alerts = []
        
        for series_id, metric in metrics.items():
            # Overflow alerts
            if metric['days_until_full']:
                if metric['days_until_full'] <= self.thresholds['warehouse_overflow_days']:
                    alerts.append(self.create_alert(
                        alert_type='WAREHOUSE_OVERFLOW',
                        series_id=series_id,
                        warehouse=metric['warehouse'],
                        product=metric['product'],
                        days_remaining=metric['days_until_full'],
                        current_level=metric['current_level'],
                        forecast_level=metric['forecast_30d'],
                        confidence=0.85
                    ))
            
            # Shortage alerts
            if metric['days_until_shortage']:
                if metric['days_until_shortage'] <= self.thresholds['ingredient_shortage_days']:
                    alerts.append(self.create_alert(
                        alert_type='INGREDIENT_SHORTAGE',
                        series_id=series_id,
                        warehouse=metric['warehouse'],
                        product=metric['product'],
                        days_remaining=metric['days_until_shortage'],
                        current_level=metric['current_level'],
                        forecast_level=metric['forecast_30d'],
                        confidence=0.90
                    ))
        
        # Sort by severity (HIGH first)
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        alerts.sort(key=lambda x: (priority_order[x['severity']], x['days_remaining']))
        
        # Summary
        alert_summary = {
            'HIGH': len([a for a in alerts if a['severity'] == 'HIGH']),
            'MEDIUM': len([a for a in alerts if a['severity'] == 'MEDIUM']),
            'LOW': len([a for a in alerts if a['severity'] == 'LOW']),
        }
        
        logger.info(f"✅ Generated {len(alerts)} alerts")
        logger.info(f"   HIGH: {alert_summary['HIGH']}")
        logger.info(f"   MEDIUM: {alert_summary['MEDIUM']}")
        logger.info(f"   LOW: {alert_summary['LOW']}")
        
        state_update = {
            "alerts": alerts,
            "alert_summary": alert_summary,
            "errors": state.get('errors', []),
            "warnings": state.get('warnings', []),
            "status": "success"
        }
        
        logger.info("=" * 60)
        logger.info("AGENT 5: ALERT GENERATOR - ✅ Completed")
        logger.info("=" * 60)
        
        return state_update


def alert_generator_node(state: WarehouseState) -> Dict:
    """LangGraph node for Agent 5"""
    generator = AlertGenerator()
    return generator.run(state)
