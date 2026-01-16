"""
Agent 6: Report Builder

Responsibilities:
1. Save forecasts to JSON
2. Save alerts to JSON
3. Generate summary text
4. Create output files

INPUT: All previous agents' outputs
OUTPUT: Files and summary
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from config import OUTPUT_DIR
from state import WarehouseState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportBuilder:
    """Generate outputs and reports"""
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_json(self, data: Any, filename: str) -> str:
        """Save data to JSON file"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved: {filepath}")
        return str(filepath)
    
    def generate_summary(self, state: WarehouseState) -> str:
        """Generate text summary"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary = f"""
═══════════════════════════════════════════════════════════════
    WAREHOUSE FORECAST REPORT
═══════════════════════════════════════════════════════════════

Generated: {timestamp}
Run ID: {state.get('run_id', 'N/A')}

-------------------------------------------------------------------
DATA SUMMARY
-------------------------------------------------------------------
Total Time Series:     {state.get('feature_stats', {}).get('num_series', 0)}
Warehouses:            {state.get('feature_stats', {}).get('num_warehouses', 0)}
Products:              {state.get('feature_stats', {}).get('num_products', 0)}
Date Range:            {state.get('data_loaded_at', 'N/A')}

-------------------------------------------------------------------
FORECASTING
-------------------------------------------------------------------
Model Used:            {state.get('model_used', 'N/A')}
Forecast Horizon:      {state.get('forecast_horizon', 30)} days
Forecasts Generated:   {len(state.get('forecasts', {}))}
Inference Time:        {state.get('inference_time_seconds', 0):.2f}s
Peak VRAM Usage:       {state.get('memory_used_gb', 0):.2f} GB

-------------------------------------------------------------------
ALERTS {'⚠️' if state.get('alerts') else '✅'}
-------------------------------------------------------------------
Total Alerts:          {len(state.get('alerts', []))}
  - HIGH Priority:     {state.get('alert_summary', {}).get('HIGH', 0)}
  - MEDIUM Priority:   {state.get('alert_summary', {}).get('MEDIUM', 0)}
  - LOW Priority:      {state.get('alert_summary', {}).get('LOW', 0)}

"""
        
        # Add top alerts
        alerts = state.get('alerts', [])
        if alerts:
            summary += "-------------------------------------------------------------------\n"
            summary += "TOP 5 ALERTS\n"
            summary += "-------------------------------------------------------------------\n"
            
            for i, alert in enumerate(alerts[:5], 1):
                summary += f"""
[{alert['severity']}] {alert['type']}
  Warehouse: {alert['warehouse']}
  Product:   {alert['product']}
  Days Left: {alert['days_remaining']}
  Action:    {alert['action']}
"""
        
        summary += "\n═══════════════════════════════════════════════════════════════\n"
        
        return summary
    
    def run(self, state: WarehouseState) -> Dict:
        """
        Main execution: create outputs
        
        Args:
            state: Complete pipeline state
            
        Returns:
            State updates with file paths
        """
        logger.info("=" * 60)
        logger.info("AGENT 6: REPORT BUILDER - Starting")
        logger.info("=" * 60)
        
        # Generate timestamp for files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_files = []
        
        # Save forecasts
        if state.get('forecasts'):
            forecast_file = f"forecasts_{timestamp}.json"
            filepath = self.save_json(state['forecasts'], forecast_file)
            output_files.append(filepath)
        
        # Save alerts
        if state.get('alerts'):
            alert_file = f"alerts_{timestamp}.json"
            filepath = self.save_json(state['alerts'], alert_file)
            output_files.append(filepath)
        
        # Save metrics
        if state.get('metrics'):
            metrics_file = f"metrics_{timestamp}.json"
            filepath = self.save_json(state['metrics'], metrics_file)
            output_files.append(filepath)
        
        # Generate summary
        summary_text = self.generate_summary(state)
        
        # Save summary
        summary_file = f"summary_{timestamp}.txt"
        summary_path = self.output_dir / summary_file
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        output_files.append(str(summary_path))
        
        logger.info(f"✅ Created {len(output_files)} output files")
        
        state_update = {
            "output_files": output_files,
            "summary_text": summary_text,
            "completed_at": datetime.now().isoformat(),
            "errors": state.get('errors', []),
            "warnings": state.get('warnings', []),
            "status": "success"
        }
        
        logger.info("=" * 60)
        logger.info("AGENT 6: REPORT BUILDER - ✅ Completed")
        logger.info(f"  - Output files: {len(output_files)}")
        logger.info("=" * 60)
        
        # Print summary
        print(summary_text)
        
        return state_update


def report_builder_node(state: WarehouseState) -> Dict:
    """LangGraph node for Agent 6"""
    builder = ReportBuilder()
    return builder.run(state)
