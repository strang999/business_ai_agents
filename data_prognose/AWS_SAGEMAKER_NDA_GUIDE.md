# AWS SageMaker vs Local Deployment for NDA-Protected Warehouse Forecasting

## 🎯 Critical Question: NDA Compliance with AWS

### ⚠️ NDA Constraint Analysis

**Your requirement:** "реальні данні юзера під НДА"

**AWS SageMaker CAN be NDA-compliant IF:**

✅ **Private VPC Deployment**
- Data stays in your AWS account
- No internet access (VPC isolated)
- Network isolation enabled
- Encryption at rest + in transit

✅ **AWS Business Associate Agreement (BAA)**
- For HIPAA/sensitive data
- Legal protection for data handling

✅ **Regional Compliance**
- EU data stays in EU (Frankfurt, Ireland)
- Ukraine data regulations compliance

❌ **NOT compliant if:**
- Using public SageMaker endpoints without VPC
- Data logs go to AWS CloudWatch without encryption
- Cross-region data transfer

---

## 📊 Cost Comparison: AWS vs Local

### Local (RTX 3070 8GB)

**One-time costs:**
- Hardware: $0 (already have)
- Setup time: 2-3 days

**Ongoing costs:**
- Electricity: ~$10/month
- Maintenance: Your time
- **Total: ~$120/year**

**Pros:**
- ✅ 100% data control
- ✅ No per-inference costs
- ✅ Perfect for NDA

**Cons:**
- ❌ Limited to 8GB VRAM
- ❌ Single point of failure
- ❌ No auto-scaling

---

### AWS SageMaker Options

#### Option 1: Real-time Inference (GPU)

**Instance: ml.g5.2xlarge**
- GPU: 24GB VRAM (NVIDIA A10G)
- Runs Chronos-2-Base or Large perfectly
- Latency: < 1 second

**Cost:**
- $1.52/hour = **$1,095/month** (24/7)
- Or $0.076/minute if scale-to-zero enabled

**Annual:** ~$13,140 (if 24/7)

**Pros:**
- ✅ Run large models (base/large)
- ✅ Best accuracy
- ✅ Low latency

**Cons:**
- ❌ Expensive if always on
- ❌ Need VPC for NDA compliance

---

#### Option 2: Serverless (CPU) ⭐ RECOMMENDED for NDA

**Configuration:**
- 6GB memory limit
- Runs Chronos-2-Small (CPU)
- Auto-scales to zero

**Cost:**
- **$0.0001 per second** of inference
- Example: 1000 forecasts/day × 2s = 2000s/day = **$6/month**
- Cold start: First request takes 30-60s (acceptable for batch)

**Annual:** ~$72 (very cheap!)

**Pros:**
- ✅ Very cost-effective
- ✅ Pay-per-use
- ✅ Can be VPC-isolated
- ✅ Auto-scales

**Cons:**
- ⚠️ CPU only (slower)
- ⚠️ Cold starts
- ⚠️ Limited to small model

---

#### Option 3: Batch Transform (CPU)

**Instance: ml.c5.4xlarge**
- 16 vCPU, 32GB RAM
- Perfect for overnight batch jobs
- Automatic shutdown after job

**Cost:**
- $0.952/hour
- Example: 1 hour/night = **$29/month**

**Annual:** ~$348

**Pros:**
- ✅ Cost-efficient for batch
- ✅ No always-on costs
- ✅ Can process thousands of warehouses
- ✅ VPC-compatible

**Cons:**
- ⚠️ Not real-time
- ⚠️ Setup overhead per job

---

## 🔐 NDA-Compliant AWS Architecture

### Recommended Setup: Private VPC + Serverless

```
┌─────────────────────────────────────────────────────┐
│  Your On-Premise Environment                        │
│  ┌──────────────────┐                              │
│  │ JSON Schema      │ ──┐                          │
│  │ 3-month Data     │   │                          │
│  └──────────────────┘   │                          │
└─────────────────────────┼──────────────────────────┘
                          │
                  Upload via S3 (encrypted)
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│  AWS Account (Your Private VPC)                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Private VPC (No Internet Access)            │  │
│  │                                               │  │
│  │  ┌────────────────┐  ┌──────────────────┐   │  │
│  │  │ S3 Bucket      │  │ SageMaker        │   │  │
│  │  │ (Encrypted)    │─▶│ Serverless       │   │  │
│  │  │                │  │ Endpoint         │   │  │
│  │  │ - schema.json  │  │                  │   │  │
│  │  │ - data.csv     │  │ Chronos-2-Small  │   │  │
│  │  └────────────────┘  └──────────────────┘   │  │
│  │         ▲                     │              │  │
│  │         │                     ▼              │  │
│  │         │            ┌──────────────────┐   │  │
│  │         └────────────│ Results          │   │  │
│  │                      │ (Encrypted S3)   │   │  │
│  │                      └──────────────────┘   │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  Network: NO internet access, VPC endpoints only   │
│  Encryption: AES-256 at rest, TLS 1.2 in transit  │
│  Logs: Disabled or encrypted in private S3        │
└─────────────────────────────────────────────────────┘
          │
          │ Download results (encrypted)
          ▼
┌─────────────────────────────────────────────────────┐
│  Your Environment                                    │
│  - Forecasts.json                                    │
│  - Alerts.json                                       │
└─────────────────────────────────────────────────────┘
```

### Security Checklist

```python
# terraform/sagemaker.tf

resource "aws_sagemaker_model" "chronos" {
  name               = "chronos-2-nda-compliant"
  execution_role_arn = aws_iam_role.sagemaker_execution.arn
  
  primary_container {
    image          = "chronos-2-cpu-image"
    model_data_url = "s3://your-private-bucket/model.tar.gz"
  }
  
  # Critical: Enable VPC isolation
  vpc_config {
    subnets         = [aws_subnet.private.id]
    security_groups = [aws_security_group.sagemaker_no_internet.id]
  }
  
  enable_network_isolation = true  # ✅ Blocks internet access
}

resource "aws_sagemaker_endpoint_configuration" "chronos" {
  name = "chronos-serverless-nda"
  
  production_variants {
    model_name = aws_sagemaker_model.chronos.name
    
    serverless_config {
      memory_size_in_mb = 6144
      max_concurrency   = 1
    }
  }
  
  # Encryption
  kms_key_id = aws_kms_key.sagemaker_encryption.id
}

# S3 bucket with encryption
resource "aws_s3_bucket" "data" {
  bucket = "warehouse-forecasting-nda-data"
  
  # ✅ Enable encryption
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.s3_encryption.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
  
  # ✅ Block public access
  public_access_block_config {
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }
  
  # ✅ Enable versioning (audit trail)
  versioning {
    enabled = true
  }
}
```

---

## 💰 Cost Analysis: 3 Scenarios

### Scenario A: Small Company (1000 forecasts/week)

| Option | Weekly Cost | Monthly Cost | Annual Cost |
|--------|-------------|--------------|-------------|
| **Local RTX 3070** | $2.50 | $10 | $120 |
| **AWS Serverless** | $0.40 | $1.60 | $19 |
| **AWS Batch** | $2.38 | $9.50 | $114 |
| **AWS Real-time (24/7)** | $253 | $1,095 | $13,140 |

**Winner:** AWS Serverless ($19/year) 🏆

---

### Scenario B: Medium Company (10,000 forecasts/week)

| Option | Weekly Cost | Monthly Cost | Annual Cost |
|--------|-------------|--------------|-------------|
| **Local RTX 3070** | $2.50 | $10 | $120 |
| **AWS Serverless** | $4.00 | $16 | $192 |
| **AWS Batch** | $9.52 | $38 | $456 |
| **AWS Real-time (scale-to-zero)** | $7.60 | $30.40 | $365 |

**Winner:** Local ($120/year) if reliable, AWS Serverless ($192) if need backup 🏆

---

### Scenario C: Large Company (100,000 forecasts/week)

| Option | Weekly Cost | Monthly Cost | Annual Cost |
|--------|-------------|--------------|-------------|
| **Local RTX 3070** | $2.50 | $10 | $120 |
| **AWS Serverless** | $40 | $160 | $1,920 |
| **AWS Batch (daily)** | $28.56 | $114 | $1,368 |
| **AWS Real-time** | $253 | $1,095 | $13,140 |

**Winner:** Local ($120) but needs clustered setup for reliability 🏆

---

## 🎯 Decision Matrix

```
Your Constraints:
├── NDA: Yes (sensitive data)
├── Budget: ?
├── Volume: How many forecasts/day?
├── Latency: Real-time or batch OK?
└── Reliability: Critical or can wait?
```

### Recommended Strategy by Scenario:

#### 1️⃣ **Prototype/POC** (Current Phase)

**Recommendation:** **Local RTX 3070** with Chronos-2-Tiny

**Why:**
- Zero infrastructure cost
- Fast iteration
- Full data control
- Validate accuracy first

**Timeline:** 2-3 weeks

---

#### 2️⃣ **Production MVP** (Next 1-2 months)

**Option A: Stay Local** if:
- ✅ <5,000 forecasts/day
- ✅ Acceptable to run on single machine
- ✅ Have backup plan if GPU fails

**Option B: AWS Serverless** if:
- ✅ Need reliability/redundancy
- ✅ Variable forecast volume
- ✅ Can spend $50-200/month
- ✅ Can setup VPC for NDA compliance

---

#### 3️⃣ **Enterprise Scale** (6+ months)

**Hybrid Approach:**

```
Primary: AWS Batch Transform
├── Daily overnight jobs
├── Process all warehouses
├── Cost: ~$100-300/month
├── VPC-isolated for NDA
└── Results → Download encrypted

Backup: Local RTX 3070
├── For ad-hoc forecasts
├── Development/testing
└── Emergency fallback
```

---

## 🔧 Implementation: AWS Serverless for NDA

### Step 1: Setup VPC-Isolated SageMaker

```python
# setup_aws_nda.py

import boto3
import json
from sagemaker import Session
from sagemaker.model import Model
from sagemaker.serverless import ServerlessInferenceConfig

# Configuration
REGION = "eu-central-1"  # Frankfurt (EU compliance)
VPC_ID = "vpc-xxxxx"  # Your private VPC
SUBNET_IDS = ["subnet-xxxx"]
SECURITY_GROUP_ID = "sg-xxxx"  # No internet access

session = Session(boto_session=boto3.Session(region_name=REGION))

# Create VPC-isolated model
chronos_model = Model(
    name="chronos-2-nda-warehouse",
    model_data="s3://your-bucket/chronos-2-small.tar.gz",
    image_uri="<chronos-2-cpu-image>",
    role="arn:aws:iam::xxxx:role/SageMaker-NDA-Role",
    vpc_config={
        'Subnets': SUBNET_IDS,
        'SecurityGroupIds': [SECURITY_GROUP_ID]
    },
    enable_network_isolation=True  # ✅ Critical for NDA!
)

# Deploy serverless endpoint
predictor = chronos_model.deploy(
    serverless_inference_config=ServerlessInferenceConfig(
        memory_size_in_mb=6144,
        max_concurrency=1
    ),
    endpoint_name="warehouse-forecast-nda"
)

print("✅ VPC-isolated endpoint deployed!")
```

---

### Step 2: Secure Data Upload

```python
# upload_data_encrypted.py

import boto3
from botocore.client import Config

# S3 client with encryption
s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

# Upload with server-side encryption
s3.upload_file(
    Filename='warehouse_data_3months.csv',
    Bucket='warehouse-nda-data',
    Key='input/data.csv',
    ExtraArgs={
        'ServerSideEncryption': 'aws:kms',
        'SSEKMSKeyId': 'arn:aws:kms:eu-central-1:xxxx:key/yyyy',
        'ACL': 'private'  # Not public
    }
)

print("✅ Data uploaded with KMS encryption")
```

---

### Step 3: Run Forecast (Same API as Local!)

```python
# forecast.py

payload = {
    "inputs": [
        {
            "target": warehouse_1_inventory,
            "item_id": "WH_01",
            "start": "2024-01-01T00:00:00"
        },
        # ... more warehouses
    ],
    "parameters": {
        "prediction_length": 30,
        "freq": "D",
        "quantile_levels": [0.1, 0.5, 0.9]
    }
}

# Call serverless endpoint
response = predictor.predict(payload)

# Same response format as local Chronos!
forecasts = response['predictions']
```

---

## 📋 Final Recommendation

### For Your Warehouse Project:

```yaml
MVP Phase (Now):
  deployment: LOCAL
  model: Chronos-2-Tiny (RTX 3070)
  cost: ~$0/month
  duration: 2-3 weeks
  goal: Validate accuracy, test pipeline

Production (In 2-3 months):
  primary: AWS Serverless (VPC-isolated)
  model: Chronos-2-Small
  cost: ~$20-100/month
  why: 
    - NDA compliant with VPC
    - No VRAM limitations
    - Auto-scaling
    - Backup/redundancy
  
  backup: Keep local for development
```

---

## ✅ Answers to Your Questions

**Q: Можна використати AWS?**
**A:** ✅ ТАК, але треба:
- Private VPC deployment
- Network isolation enabled
- KMS encryption
- No CloudWatch logging (or encrypted)
- Regional compliance (EU data in EU)

**Q: Чи це порушує NDA?**
**A:** ❌ НІ, якщо правильно налаштовано:
-  Data stays in your AWS account
- VPC-isolated (no internet)
- Encrypted at rest + in transit
- No AWS access to plaintext data

**Q: Скільки коштує?**
**A:** 
- Serverless: ~$20-100/month для типового навантаження
- Batch: ~$100-300/month для щоденних job
- Дешевше ніж місцевий GPU сервер ($500+/month)

**Q: Краще AWS чи локально?**
**A:**
- **MVP:** Локально (швидше, безкоштовно)
- **Production:** AWS Serverless (reliability, scalability)
- **Best:** Hybrid (AWS primary, local backup)

---

## 🚀 Next Steps

1. **This week:** Build MVP locally (RTX 3070 + Tiny)
2. **Week 2-3:** Validate accuracy, optimize
3. **Month 2:** Deploy to AWS Serverless (VPC)
4. **Month 3:** Production with hybrid setup

**Want me to create the AWS deployment code next?** 🎯
