"""
Main Pipeline: Warehouse Forecasting System

Orchestrates all 6 agents using LangGraph:
1. Data Loader
2. Feature Engineer
3. Chronos Forecaster
4. Business Rules
5. Alert Generator
6. Report Builder

Usage:
  python main.py

  # With custom horizon
  python main.py --horizon 60

  # Filter specific warehouses

  python main.py --warehouses WH_01,WH_02
"""

import uuid
from datetime import datetime
from typing import Dict
import argparse
import logging

from langgraph.graph import StateGraph, END

from state import WarehouseState
from agent_1_data_loader import data_loader_node
from agent_2_feature_engineer import feature_engineer_node
from agent_3_chronos_forecaster import chronos_forecaster_node
from agent_4_business_rules import business_rules_node
from agent_5_alert_generator import alert_generator_node
from agent_6_report_builder import report_builder_node

from config import FORECAST_HORIZON

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_warehouse_forecast_pipeline() -> StateGraph:
    """
    Create LangGraph pipeline with all 6 agents
    
    Returns:
        Compiled StateGraph
    """
    logger.info("🏗️  Building pipeline...")
    
    # Create graph
    workflow = StateGraph(WarehouseState)
    
    # Add nodes (agents)
    workflow.add_node("load_data", data_loader_node)
    workflow.add_node("engineer_features", feature_engineer_node)
    workflow.add_node("forecast", chronos_forecaster_node)
    workflow.add_node("validate", business_rules_node)
    workflow.add_node("generate_alerts", alert_generator_node)
    workflow.add_node("build_report", report_builder_node)
    
    # Define edges (execution flow)
    workflow.set_entry_point("load_data")
    workflow.add_edge("load_data", "engineer_features")
    workflow.add_edge("engineer_features", "forecast")
    workflow.add_edge("forecast", "validate")
    workflow.add_edge("validate", "generate_alerts")
    workflow.add_edge("generate_alerts", "build_report")
    workflow.add_edge("build_report", END)
    
    # Compile
    app = workflow.compile()
    
    logger.info("✅ Pipeline built successfully")
    logger.info("   Nodes: 6 agents")
    logger.info("   Flow: Data → Features → Forecast → Validate → Alerts → Report")
    
    return app


def run_forecast(
    horizon: int = FORECAST_HORIZON,
    warehouses_filter: list = None,
    products_filter: list = None,
    use_schema: bool = True
):
    """
    Run complete forecasting pipeline
    
    Args:
        horizon: Days to forecast
        warehouses_filter: List of warehouse IDs or None for all
        products_filter: List of product IDs or None for all
        use_schema: Whether to use DATA_SCHEMA.md
        
    Returns:
        Final state with all results
    """
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║" + " " * 20 + "WAREHOUSE FORECASTING SYSTEM" + " " * 30 + "║")
    logger.info("╚" + "═" * 78 + "╝")
    
    # Create initial state
    initial_state = {
        "run_id": str(uuid.uuid4()),
        "started_at": datetime.now().isoformat(),
        "forecast_horizon": horizon,
        "warehouses_filter": warehouses_filter or ["ALL"],
        "products_filter": products_filter or ["ALL"],
        "use_schema": use_schema,
        "generate_explanations": False,  # Can enable later with Ollama
        "errors": [],
        "warnings": [],
        "status": "running"
    }
    
    logger.info(f"📋 Run ID: {initial_state['run_id']}")
    logger.info(f"📅 Forecast Horizon: {horizon} days")
    logger.info(f"🏭 Warehouses: {', '.join(initial_state['warehouses_filter'])}")
    logger.info(f"📦 Products: {', '.join(initial_state['products_filter'])}")
    logger.info("")
    
    # Build pipeline
    app = create_warehouse_forecast_pipeline()
    
    # Execute
    logger.info("🚀 Starting pipeline execution...")
    logger.info("")
    
    try:
        result = app.invoke(initial_state)
        
        logger.info("")
        logger.info("╔" + "═" * 78 + "╗")
        logger.info("║" + " " * 28 + "PIPELINE COMPLETED" + " " * 32 + "║")
        logger.info("╚" + "═" * 78 + "╝")
        
        # Calculate total time
        start_time = datetime.fromisoformat(result['started_at'])
        end_time = datetime.fromisoformat(result.get('completed_at', datetime.now().isoformat()))
        total_time = (end_time - start_time).total_seconds()
        
        logger.info(f"⏱️  Total execution time: {total_time:.2f}s")
        logger.info(f"📊 Status: {result.get('status', 'unknown').upper()}")
        
        if result.get('errors'):
            logger.error(f"❌ Errors: {len(result['errors'])}")
            for error in result['errors']:
                logger.error(f"   - {error}")
        
        if result.get('warnings'):
            logger.warning(f"⚠️  Warnings: {len(result['warnings'])}")
        
        logger.info("")
        logger.info("📂 Output files:")
        for filepath in result.get('output_files', []):
            logger.info(f"   - {filepath}")
        
        logger.info("")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run warehouse forecasting pipeline")
    parser.add_argument("--horizon", type=int, default=FORECAST_HORIZON,
                       help=f"Forecast horizon in days (default: {FORECAST_HORIZON})")
    parser.add_argument("--warehouses", type=str, default=None,
                       help="Comma-separated warehouse IDs (default: ALL)")
    parser.add_argument("--products", type=str, default=None,
                       help="Comma-separated product IDs (default: ALL)")
    parser.add_argument("--no-schema", action="store_true",
                       help="Skip loading DATA_SCHEMA.md")
    
    args = parser.parse_args()
    
    # Parse filters
    warehouses_filter = args.warehouses.split(',') if args.warehouses else None
    products_filter = args.products.split(',') if args.products else None
    
    # Run
    result = run_forecast(
        horizon=args.horizon,
        warehouses_filter=warehouses_filter,
        products_filter=products_filter,
        use_schema=not args.no_schema
    )
    
    print("\n" + "=" * 80)
    print("🎉 Forecasting completed successfully!")
    print("=" * 80)
