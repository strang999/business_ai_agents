# Production Deployment Guide

## Quick Start

### Local Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run forecast
python main.py --horizon 30
```

### Docker Deployment
```bash
# Build image
docker-compose build

# Run once
docker-compose up

# Run with scheduler (daily 9 AM)
docker-compose --profile scheduler up -d
```

---

## Environment Variables

Create `.env` file:

```bash
# Model configuration
MODEL_SIZE=small  # tiny, small, or base
DEVICE=cpu  # or cuda
FORECAST_HORIZON=30

# Email alerts (optional)
ENABLE_EMAIL_ALERTS=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=alerts@company.com
EMAIL_TO=admin@company.com
EMAIL_USERNAME=your_username
EMAIL_PASSWORD=your_password

# Paths
DATA_DIR=./data/Test data
OUTPUT_DIR=./output
```

---

## Production Checklist

### Before Deployment

- [ ] Install CUDA PyTorch for GPU support
  ```bash
  pip install torch --index-url https://download.pytorch.org/whl/cu118
  ```

- [ ] Test on GPU
  ```bash
  python -c "import torch; print(torch.cuda.is_available())"
  ```

- [ ] Run validation
  ```bash
  python quick_validate.py
  ```

- [ ] Check accuracy baseline (MAPE < 15%)

- [ ] Configure alert thresholds in `config.py`

- [ ] Set up email notifications (if needed)

### Deployment

- [ ] Build Docker image
- [ ] Configure volumes for data/output
- [ ] Set up log rotation
- [ ] Configure backup for output files
- [ ] Test scheduled runs
- [ ] Monitor first week of production runs

### Monitoring

- [ ] Check `output/errors.log` daily
- [ ] Review `output/performance_metrics.json`
- [ ] Validate forecast quality weekly
- [ ] Adjust thresholds based on feedback

---

## Scheduled Execution

### Using Cron (Linux/Mac)
```bash
# Add to crontab
0 9 * * * cd /path/to/warehouse_forecast && python main.py --horizon 60 >> output/cron.log 2>&1
```

### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9 AM
4. Action: Start Program
   - Program: `python`
   - Arguments: `main.py --horizon 60`
   - Start in: `D:\Apps\ZIRA\ai-agents\warehouse_forecast`

### Using Docker Scheduler
```bash
docker-compose --profile scheduler up -d
```

---

## Troubleshooting

### High MAPE (>20%)
- Try larger model (small → base)
- Increase training context
- Check data quality
- Adjust feature engineering

### OOM Errors
- Reduce batch_size in config.py
- Use smaller model (small → tiny)
- Enable INT8 quantization
- Process warehouses separately

### Slow Performance
- Enable GPU (5-10x speedup)
- Reduce num_samples in forecaster
- Use smaller model
- Parallel processing

### No Alerts Generated
- Check alert thresholds (too lenient?)
- Verify business rules
- Review capacity settings
- Inspect metrics manually

---

## Backup & Recovery

### Backup Schedule
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backups/forecast_$DATE.tar.gz output/
find backups/ -mtime +30 -delete  # Keep 30 days
```

### Restore
```bash
tar -xzf backups/forecast_20260109.tar.gz
```

---

## Security

### NDA Data Protection
- ✅ All data stays local (no cloud APIs)
- ✅ Docker volumes isolated
- ✅ .gitignore protects data files
- ✅ Logs exclude sensitive info

### Access Control
- Restrict Docker socket access
- Use read-only data volumes
- Encrypt output directory
- Secure email credentials

---

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Inference Time | < 5s | ~10s (CPU) |
| MAPE | < 12% | TBD |
| Alerts Precision | > 80% | TBD |
| Uptime | > 99% | N/A |

---

## Support

### Logs Location
- Errors: `output/errors.log`
- Performance: `output/performance_metrics.json`
- Run summaries: `output/summary_*.txt`

### Common Issues
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Contact
Internal team: forecast-support@company.com
