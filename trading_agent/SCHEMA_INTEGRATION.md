# 📚 Using DATA_SCHEMA.md in the Forecasting Pipeline

## How We'll Use Schema Documentation

### 1. ✅ In LangGraph State (Metadata)

```python
class WarehouseState(TypedDict):
    # ... existing fields ...
    
    # NEW: Schema documentation
    schema_docs: str  # Full markdown content
    schema_metadata: Dict[str, Any]  # Parsed business rules
    field_descriptions: Dict[str, str]  # Field explanations
```

**Usage in Agent 1 (Data Loader):**

```python
def data_loader_node(state: WarehouseState) -> Dict:
    """Load data + schema documentation"""
    
    # Load schema docs
    with open('data/DATA_SCHEMA.md', 'r', encoding='utf-8') as f:
        schema_docs = f.read()
    
    # Parse critical info
    schema_metadata = parse_schema_docs(schema_docs)
    # Example output:
    # {
    #   'warehouse_capacity': {'WH_01': 1000, 'WH_02': 1500},
    #   'min_stock_levels': {'ChemicalA': 50, 'ChemicalB': 100},
    #   'lead_times': {'Supplier1': 7, 'Supplier2': 14},
    #   'relationships': {
    #       'ProductA': ['IngredientX', 'IngredientY'],
    #   }
    # }
    
    return {
        "schema_docs": schema_docs,
        "schema_metadata": schema_metadata,
        "raw_data": {...}
    }
```

---

### 2. ✅ In Vector Database (for RAG)

**Why:** If agent needs to answer questions or explain predictions

```python
# vector_db_setup.py

from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def setup_schema_vectordb():
    """Create vector DB from DATA_SCHEMA.md"""
    
    # Load schema
    with open('data/DATA_SCHEMA.md', 'r') as f:
        schema_text = f.read()
    
    # Split into chunks
    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(schema_text)
    
    # Create embeddings (local, no API!)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Create vector store
    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    return vectordb
```

**Usage in Agent 4 (Business Rules):**

```python
def business_rules_node(state: WarehouseState) -> Dict:
    """Validate forecasts using schema knowledge"""
    
    # Load vector DB
    vectordb = Chroma(
        persist_directory="./chroma_db",
        embedding_function=HuggingFaceEmbeddings(...)
    )
    
    # Query for relevant rules
    for series_id, forecast in state['forecasts'].items():
        warehouse, product = series_id.split('_')
        
        # RAG: Get relevant constraints
        query = f"What is the capacity of {warehouse}? What are minimum stock levels for {product}?"
        docs = vectordb.similarity_search(query, k=3)
        
        # Extract constraints from docs
        capacity = extract_capacity(docs)
        min_stock = extract_min_stock(docs)
        
        # Apply to forecast validation
        if forecast['mean'][-1] > capacity * 0.95:
            # Generate alert
            pass
```

---

### 3. ✅ For Data Validation

```python
def validate_loaded_data(raw_data, schema_metadata):
    """Validate data against schema"""
    
    errors = []
    
    # Check required fields
    required_fields = schema_metadata.get('required_fields', [])
    for field in required_fields:
        if field not in raw_data:
            errors.append(f"Missing required field: {field}")
    
    # Check data types
    field_types = schema_metadata.get('field_types', {})
    for field, expected_type in field_types.items():
        if field in raw_data:
            actual_type = type(raw_data[field]).__name__
            if actual_type != expected_type:
                errors.append(f"{field}: expected {expected_type}, got {actual_type}")
    
    # Check value ranges
    value_ranges = schema_metadata.get('value_ranges', {})
    for field, (min_val, max_val) in value_ranges.items():
        if field in raw_data:
            value = raw_data[field]
            if not (min_val <= value <= max_val):
                errors.append(f"{field} value {value} outside range [{min_val}, {max_val}]")
    
    return errors
```

---

### 4. ✅ For Feature Engineering

```python
def feature_engineer_node(state: WarehouseState) -> Dict:
    """Use schema to create smart features"""
    
    schema = state['schema_metadata']
    
    # Use relationship info from schema
    product_composition = schema.get('product_composition', {})
    
    for product, ingredients in product_composition.items():
        # Create composite features
        # If ProductA = 70% IngredientX + 30% IngredientY
        # Then forecast ProductA based on X and Y availability
        
        composite_series = []
        for ingredient, percentage in ingredients:
            ingredient_series = state['time_series'][ingredient]
            composite_series.append(
                [val * percentage for val in ingredient_series]
            )
        
        # Add as covariate
        state['covariates'][f'{product}_composition'] = composite_series
    
    return state
```

---

### 5. ✅ For Alert Explanations (NEW AGENT!)

**Add Agent 7: Explanation Generator**

```python
def explanation_generator_node(state: WarehouseState) -> Dict:
    """Generate human-readable explanations using schema"""
    
    from langchain.llms import Ollama
    from langchain.prompts import PromptTemplate
    
    # Local LLM for explanations
    llm = Ollama(model="qwen2.5:7b")
    
    # Get schema context
    vectordb = load_vectordb()
    
    explanations = []
    
    for alert in state['alerts']:
        # RAG: Get relevant schema info
        query = f"Explain {alert['warehouse']} and {alert['product']} relationship"
        schema_context = vectordb.similarity_search(query, k=2)
        
        # Generate explanation
        prompt = PromptTemplate(
            template="""
            Based on this schema information:
            {schema_context}
            
            Explain this alert to a non-technical user:
            {alert}
            
            Provide:
            1. What this means in simple terms
            2. Why it's happening (based on data patterns)
            3. What action should be taken
            4. Cite relevant schema info
            """,
            input_variables=["schema_context", "alert"]
        )
        
        explanation = llm(prompt.format(
            schema_context=schema_context,
            alert=alert
        ))
        
        explanations.append({
            'alert_id': alert['id'],
            'explanation': explanation,
            'schema_citations': schema_context
        })
    
    return {"alert_explanations": explanations}
```

---

## 📊 Complete Updated Flow

```
Data + Schema Documentation
         ↓
┌────────────────────────────────────┐
│ Agent 1: Data Loader               │
│ ✅ Load DATA_SCHEMA.md             │
│ ✅ Parse business rules            │
│ ✅ Load JSON data                  │
│ ✅ Validate data against schema    │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Agent 2: Feature Engineer          │
│ ✅ Use schema relationships        │
│ ✅ Create composite features       │
│ ✅ Add domain knowledge covariates │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Agent 3: Chronos Forecaster        │
│ (Same - no schema needed)          │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Agent 4: Business Rules            │
│ ✅ Query vector DB for constraints │
│ ✅ Apply schema-defined limits     │
│ ✅ Calculate metrics from schema   │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Agent 5: Alert Generator           │
│ ✅ Use schema to prioritize        │
│ ✅ Add schema-based context        │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Agent 6: Report Builder            │
│ (Same)                             │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 🆕 Agent 7: Explanation Generator  │
│ ✅ RAG with schema vector DB       │
│ ✅ Generate human-readable reports │
│ ✅ Cite schema documentation       │
└────────────────────────────────────┘
```

---

## 🗄️ Storage Architecture

```
trading_agent/
├── data/
│   ├── DATA_SCHEMA.md          ← Source of truth
│   └── Test data/*.json
│
├── chroma_db/                  ← Vector store (auto-created)
│   ├── index/
│   └── chroma.sqlite3          (persisted embeddings)
│
├── state/
│   └── current_state.json      ← LangGraph state snapshot
│
└── output/
    ├── forecasts.json
    ├── alerts_with_explanations.json  ← NEW!
    └── report_with_citations.html     ← NEW!
```

---

## 💾 Persistence Strategy

### Option 1: Save State to Disk (Simple)

```python
import json
from datetime import datetime

def save_state(state: WarehouseState):
    """Persist state to disk"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Convert to serializable format
    state_dict = dict(state)
    
    # Save
    with open(f'state/state_{timestamp}.json', 'w') as f:
        json.dump(state_dict, f, indent=2)
    
    # Also save latest
    with open('state/latest_state.json', 'w') as f:
        json.dump(state_dict, f, indent=2)
```

### Option 2: Use LangGraph Checkpointer (Better)

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Create graph with checkpointing
checkpoint = SqliteSaver.from_conn_string("checkpoints.db")

app = workflow.compile(checkpointer=checkpoint)

# Run with thread ID for persistence
config = {"configurable": {"thread_id": "warehouse_forecast_v1"}}
result = app.invoke(initial_state, config=config)

# Later: Resume from checkpoint
result = app.invoke({}, config=config)  # Continues from last state
```

---

## ✅ Implementation Checklist

**Phase 1: Schema Integration**
- [ ] Parse DATA_SCHEMA.md → extract business rules
- [ ] Create vector DB from schema (Chroma + HuggingFace embeddings)
- [ ] Add schema fields to WarehouseState
- [ ] Implement schema validation in Agent 1

**Phase 2: RAG Setup**
- [ ] Install: `pip install chromadb sentence-transformers`
- [ ] Create vector DB on first run
- [ ] Implement similarity search in Agent 4
- [ ] Test retrieval quality

**Phase 3: Explanation Agent**
- [ ] Create Agent 7 node
- [ ] Install Ollama + Qwen model
- [ ] Implement explanation prompts
- [ ] Generate human-readable alerts

**Phase 4: Persistence**
- [ ] Setup LangGraph checkpointer (SQLite)
- [ ] Save state after each run
- [ ] Add state recovery on startup

---

## 🚀 Quick Start

```python
# 1. First run: Create vector DB
from setup_vectordb import setup_schema_vectordb
setup_schema_vectordb()  # Creates ./chroma_db/

# 2. Run pipeline with schema
result = app.invoke({
    "forecast_horizon": 30,
    "use_schema": True,       # NEW!
    "generate_explanations": True  # NEW!
})

# 3. Check results
print(result['alert_explanations'])
# [{
#   'alert_id': 'WH_01_OVERFLOW',
#   'explanation': 'Based on schema, WH_01 has max capacity 1000 units...',
#   'schema_citations': ['Section 2: Warehouse Capacities']
# }]
```

---

## 💡 Summary

**Так, schema буде використовуватись в:**

1. ✅ **LangGraph State** - як metadata для всіх agents
2. ✅ **Vector DB (Chroma)** - для RAG queries
3. ✅ **Data Validation** - check data quality
4. ✅ **Feature Engineering** - use relationships
5. ✅ **Business Rules** - apply constraints
6. ✅ **Explanations** - generate human-readable alerts
7. ✅ **Persistence** - save with state checkpoints

**Next step:** Parse DATA_SCHEMA.md і інтегрувати в Agent 1! 🎯
