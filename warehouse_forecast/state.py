"""
State definition for LangGraph warehouse forecasting pipeline

This defines the data structure that flows through all agent nodes.
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class WarehouseState(TypedDict, total=False):
    """
    Complete state for warehouse forecasting pipeline
    
    Flows through 6 agents:
    1. Data Loader
    2. Feature Engineer  
    3. Chronos Forecaster
    4. Business Rules Validator
    5. Alert Generator
    6. Report Builder
    """
    
    # ===== INPUT PARAMETERS =====
    forecast_horizon: int  # Days to forecast (default: 30)
    warehouses_filter: List[str]  # ["ALL"] or specific IDs
    products_filter: List[str]  # ["ALL"] or specific IDs
    use_schema: bool  # Whether to use DATA_SCHEMA.md
    generate_explanations: bool  # Whether to generate LLM explanations
    
    # ===== AGENT 1: Data Loader outputs =====
    raw_data: Dict[str, Any]  # {balances, products, composition, etc.}
    data_loaded_at: str  # ISO timestamp
    schema_docs: Optional[str]  # Content of DATA_SCHEMA.md
    schema_metadata: Optional[Dict[str, Any]]  # Parsed business rules
    field_descriptions: Optional[Dict[str, str]]  # Field explanations
    
    # ===== AGENT 2: Feature Engineer outputs =====
    time_series: Dict[str, List[float]]  # {series_id: [values]}
    series_metadata: Dict[str, Dict[str, Any]]  # {series_id: {warehouse, product, ...}}
    covariates: Optional[Dict[str, List[Any]]]  # External features
    groups: Dict[str, List[int]]  # {group_name: [series_indices]}
    feature_stats: Dict[str, Any]  # Statistics about features
    
    # ===== AGENT 3: Forecaster outputs =====
    forecasts: Dict[str, Dict[str, List[float]]]  
    # {series_id: {mean: [...], q10: [...], q50: [...], q90: [...]}}
    model_used: str  # e.g., "Chronos-2-Small"
    model_config: Dict[str, Any]  # Model configuration used
    inference_time_seconds: float
    memory_used_gb: float  # Peak VRAM usage
    
    # ===== AGENT 4: Business Rules outputs =====
    validated_forecasts: Dict[str, Any]  # Forecasts after validation
    metrics: Dict[str, Dict[str, Any]]  
    # {series_id: {days_until_full, days_until_shortage, current_level, etc.}}
    constraint_violations: List[str]  # List of violations
    applied_rules: List[str]  # Which rules were applied
    
    # ===== AGENT 5: Alert Generator outputs =====
    alerts: List[Dict[str, Any]]  
    # [{type, severity, warehouse, product, action, deadline, confidence}]
    alert_summary: Dict[str, int]  # {HIGH: 5, MEDIUM: 10, LOW: 2}
    
    # ===== AGENT 6: Report Builder outputs =====
    output_files: List[str]  # Paths to generated files
    summary_text: str  # Human-readable summary
    dashboard_url: Optional[str]  # Path to HTML dashboard
    
    # ===== OPTIONAL: Agent 7 (if explanations enabled) =====
    alert_explanations: Optional[List[Dict[str, Any]]]
    # [{alert_id, explanation, schema_citations}]
    
    # ===== ERROR HANDLING =====
    errors: List[str]  # List of errors encountered
    warnings: List[str]  # List of warnings
    status: str  # "success", "partial", "failed"
    
    # ===== METADATA =====
    run_id: str  # Unique run identifier
    started_at: str  # ISO timestamp
    completed_at: Optional[str]  # ISO timestamp
    execution_time_seconds: Optional[float]
