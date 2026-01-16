# Production Improvements Roadmap

## Completed ✅
- [x] Basic 6-agent pipeline
- [x] Data loading (JSON, schema)
- [x] Feature engineering (multivariate)
- [x] Chronos forecasting (CPU, tiny model)
- [x] Business rules & alerts
- [x] Report generation
- [x] CLI interface

## In Progress 🔄
- [/] Validation/backtesting framework

## Next Steps (Production-Ready)

### 1. GPU Support & Model Upgrade
**Priority: HIGH**
- [ ] Install CUDA PyTorch
- [ ] Upgrade to chronos-t5-small (better accuracy)
- [ ] Memory profiling for 8GB VRAM
- [ ] Fallback to tiny if OOM

### 2. Accuracy Validation
**Priority: HIGH**
- [ ] Complete backtesting script
- [ ] Calculate MAPE per product
- [ ] Identify best/worst forecasts
- [ ] Tune alert thresholds based on accuracy

### 3. Visualization Dashboard
**Priority: MEDIUM**
- [ ] Plotly interactive charts
- [ ] Warehouse fill rate trends
- [ ] Product depletion timeline
- [ ] Alert priority matrix
- [ ] Confidence interval bands

### 4. Performance Optimization
**Priority: MEDIUM**
- [ ] Batch processing optimization
- [ ] Caching for repeated runs
- [ ] Parallel forecasting
- [ ] Memory usage profiling

### 5. Production Deployment
**Priority: MEDIUM**
- [ ] Docker containerization
- [ ] Environment variables for config
- [ ] Logging to file
- [ ] Error notifications

### 6. Automation
**Priority: LOW**
- [ ] Scheduled daily runs
- [ ] Email alerts for HIGH priority
- [ ] API endpoint (FastAPI)
- [ ] Database storage (SQLite/Postgres)

### 7. Advanced Features
**Priority: LOW**
- [ ] Schema RAG (vector DB)
- [ ] LLM explanations (Ollama)
- [ ] Multi-horizon forecasts
- [ ] What-if scenarios

## Timeline
- Week 1: GPU + Validation + Small model
- Week 2: Viz + Performance
- Week 3: Docker + Automation
- Week 4: Advanced features

## Current Blockers
1. Validation script still running (12+ hours) - need to investigate
2. No GPU support yet (CPU only)
3. No visualizations yet
