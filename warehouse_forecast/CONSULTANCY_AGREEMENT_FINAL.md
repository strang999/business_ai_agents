# CONSULTANCY AGREEMENT
## AI Engineering Services - Warehouse Forecasting PoC

**Agreement Date:** January 9, 2026  
**Effective Date:** Upon signature and receipt of deposit  
**Engagement Type:** Proof of Concept
**Start Date:** The business day after Consultant confirms receipt of the Deposit, unless otherwise agreed in writing.
---

## PARTIES

**CONSULTANT:**  
Name: Anton Shumeiko  
Title: Senior AI Engineer  
Email: shumeiko.aanton@gmail.com  
Location: Porto, Portugal

**CLIENT:**  
Company: Cybernetis.ai  
Address: [Client Address]  
Contact: [Client Contact Name]  
Email: [Client Email]

---

## 1. SCOPE OF SERVICES

### 1.1 Proof of Concept Deliverables

**Duration:** Up to 7 calendar days from Start Date  
**Working Time:** Provided on business days  
**Estimated Effort:** 20-30 hours total  
**Availability:** Up to 4 hours per business day  
**Delivery:** May occur earlier than Day 7

**Deliverables:**

1. **JSON Ingestion & Schema Mapping**
   - Data loader for warehouse JSON files
   - Schema validation and mapping
   - Basic data quality checks

2. **Chronos Inference Pipeline**
   - Working forecast generation system
   - 30-day prediction horizon
   - Probabilistic outputs with confidence intervals

3. **Forecast Output & Validation Report**
   - Sample forecasts for key products
   - Short validation report: MAPE, RMSE metrics
   - Failure case analysis
   - Data quality assessment

4. **Demo & Repository**
   - Live system demonstration
   - Code repository with run instructions
   - Docker deployment setup (demo-ready)

5. **Dashboard Prototype**
   - Single demo page
   - Up to 3 charts: forecast trends, historical data, error metrics
   - Basic filters: date range, product selector
   - Export forecast results (CSV)
   - Status: Demo-ready (not production BI system)

6. **Go/No-Go Recommendation**
   - Production feasibility assessment
   - Roadmap to production deployment
   - Risk analysis
   - Cost estimate for Phase 2

**Performance Target (non-binding):**
- Aim for MAPE <15% on validation split
- Subject to data quality and model performance

**Acceptance Process:**
- Deliverables submitted to Client
- Client has 3 business days to review
- Material defects must be documented in writing with specifics
- Consultant has 2 business days to remedy documented defects
- No written rejection with specific defects = deemed accepted
- Payment due upon submission (see Section 2.1)

### 1.2 Optional Phase 2 (If PoC Approved)

**Duration:** 2-3 weeks  
**Price:** $5,500 (see Section 2.2)

**Capabilities Added:**
- Natural language forecast explanations
- Context-aware alerting system
- Production-grade deployment
- Complete documentation
- User training (up to 4 hours)

**Includes:**
- One deployment environment (provided by Client)
- Integration and setup

**Excludes:**
- 24/7 operations support
- SLA guarantees
- Ongoing monitoring (available on retainer)
- Multi-environment deployments

**Approval Required:** Client reviews PoC before authorizing Phase 2

### 1.3 Out of Scope

**NOT included in PoC:**
- Production deployment
- SLA commitments
- 24/7 monitoring or support
- Model fine-tuning on proprietary data
- Production-grade BI dashboard
- Hardware procurement or IT infrastructure
- ERP system integration
- Multi-user training programs

**Data Quality Assumptions:**
- Client provides clean, structured JSON data
- Minimum 3 months historical data
- <20% missing values per product
- If significant cleaning required (>5 hours): billable at $90/hr with prior approval

**Change Requests:**
- Out-of-scope work requires written change request
- May affect timeline and fees
- Requires mutual written agreement

**Client Dependencies:**
- Timeline assumes timely data access and feedback
- Minor delays (<3 days): Extend deadline day-for-day
- Major delays (>3 days): Consultant may reschedule to mutually agreed dates
- Delays do not affect deposit (remains non-refundable)

---

## 2. COMPENSATION

### 2.1 PoC Pricing

**Fixed Price: $2,500**

**Payment Schedule:**

**1) Deposit: $1,000 (40%)**
- Due: Upon contract signing
- Status: **Non-refundable once work begins**
- Covers: First 11 hours of work (at $90/hr equivalent)

**2) Final Payment: $1,500 (60%)**
- Due: Upon submission of deliverables
- Deadline: Net 7 from submission date
- Late payments: 1.5% per month
- **Holdback:** Client may withhold up to 10% ($150) of Final Payment solely for documented material defects reported within the Acceptance Process
- Withheld amount due immediately upon remedy of defects

**Hours Included:** Up to 30 hours total

**Overage Policy:**
- Hours beyond 30 require written pre-approval
- Rate: $90/hour
- Billed separately upon completion

### 2.2 Phase 2 Pricing (If Approved)

**Fixed Price: $5,500**
- Payment: 40% ($2,200) at start
- Payment: 60% ($3,300) upon completion
- Same payment terms as PoC

### 2.3 Expenses

No additional expenses anticipated for remote work.

---

## 3. TIMELINE

### PoC Timeline

| Day | Activity | Output |
|-----|----------|--------|
| 1-2 | Setup & data integration | Pipeline running |
| 3-4 | Forecasting & validation | Metrics calculated |
| 5-6 | Demo prep & documentation | Repository ready |
| 7 | Delivery & presentation | All deliverables submitted |

**Delivery:** Within 7 calendar days, may be earlier  
**Presentation:** 1-hour demo (video call)

---

## 4. INTELLECTUAL PROPERTY

### 4.1 Ownership

**Background IP:**
- Consultant retains ownership of pre-existing tools, templates, libraries, utilities, know-how, and generic components developed independently of this engagement
- Includes: agent framework scaffolding, evaluation harness, Docker templates, general ML utilities

**Project IP:**
- Upon full payment, Client owns the specific PoC implementation created for Client's data and requirements
- Includes: custom code, configurations, documentation, reports specific to this project

**License:**
- Consultant grants Client a perpetual, worldwide, royalty-free license to use any Background IP embedded in the deliverables solely as necessary to use the Project IP

**Consultant Retains:**
- Right to anonymized case study (no client data/names)
- Portfolio reference (with client approval)

### 4.2 Open Source

System uses:
- Amazon Chronos-2 (Apache 2.0)
- LangGraph (MIT)
- PyTorch (BSD)

Client receives rights per respective licenses.

---

## 5. CONFIDENTIALITY

### 5.1 Confidential Information

Consultant acknowledges access to:
- Warehouse inventory data
- Business processes
- Strategic plans

### 5.2 Obligations

Consultant agrees to:
- Keep all information confidential
- Not disclose to third parties
- Use data solely for this project
- Delete data upon termination

### 5.3 Security Measures

Consultant will implement reasonable technical and organizational measures appropriate to the risk, including:
- Access controls
- Encrypted storage where available
- Secure deletion protocols
- No cloud uploads without Client's written approval
- No external API calls without Client's written approval

**Duration:** 5 years post-termination

---

## 6. WARRANTIES & LIABILITIES

### 6.1 Consultant Warranties

- Professional services
- Original or licensed code
- No IP infringement
- Industry best practices

### 6.2 No Performance Guarantees

Consultant makes **best effort** but does NOT guarantee:
- Specific MAPE levels (estimates only)
- Business outcomes
- System uptime post-handoff

PoC is validation exercise, not production commitment.

### 6.3 Limitation of Liability

**Maximum liability:** Total fees paid  
**No liability for:** Consequential damages, business losses, third-party claims  
**Exceptions:** Gross negligence, willful misconduct, confidentiality breach

---

## 7. TERMINATION

### 7.1 Early Termination

Either party may terminate with 3 days' written notice.

**Payment Upon Termination:**
- **Deposit ($1,000):** Non-refundable (covers first 11 hours of work at $90/hr equivalent)
- **Additional Hours:** Hours worked beyond initial 11 hours billed at $90/hr
- **Cap:** Total payment capped at $2,500 fixed fee
- **Deliverables:** Client receives work completed to date

**Example:**
- Deposit paid: $1,000 (covers first 11 hours)
- Total hours worked: 20 hours
- Additional hours: 20 - 11 = 9 hours
- Additional due: 9h × $90/h = $810
- Total owed: $1,000 + $810 = $1,810

**Suspension for Non-Payment:**
- Consultant may suspend work immediately if payment overdue by >7 days

### 7.2 Completion

- No refunds for completed work
- Client decides: Phase 2 / Pause / Stop
- No obligation to continue
- Phase 2: Code transfer upon final payment + 2-week email support

---

## 8. WORKING RELATIONSHIP

### 8.1 Independent Contractor

- Not employee
- Controls own methods
- Provides own equipment
- Responsible for regulatory compliance

### 8.2 Communication

- Daily progress updates (Slack/email)
- Availability: 4 hours/day business hours
- Response time: 4-6 hours
- No 24/7 on-call

### 8.3 Tools & Access

**Consultant provides:** Dev environment, Docker, repository  
**Client provides:** Data access, feedback, decisions

---

## 9. PAYMENT METHODS

**Accepted:**
- Wise/Revolut (preferred)
- Bank transfer
- PayPal (+3% fee)

**Currency:** USD

**Invoicing:**
- Deposit: Invoiced upon signing
- Final Payment: Invoiced upon submission of deliverables
- Overage: Invoiced upon completion

---

## 10. LEGAL

### 10.1 Governing Law

**Primary:**
- **Governing Law:** Portuguese law
- **Jurisdiction:** Courts of Lisbon, Portugal

**Alternative (if dispute >$10,000):**
- UNCITRAL arbitration rules
- Seat: Lisbon, Portugal
- Language: English
- Arbitrator: 1

**Injunctive Relief:** Either party may seek court orders for IP/confidentiality breaches

### 10.2 GDPR Compliance

**Consultant = Data Processor**  
**Client = Data Controller**

**Obligations:**
- Process data only as instructed
- Implement security measures (Section 5.3)
- Notify breaches without undue delay and within 48 hours of discovery
- Delete data within 7 days post-termination

**Breach Definition:**
- Unauthorized access to Client data on Consultant systems
- Loss/theft of devices with Client data
- Accidental disclosure to third parties

**Client Responsibility:**
- Regulatory reporting to authorities per GDPR (within 72 hours)
- Data subject notifications if required
- Consultant provides reasonable assistance

**Processing Location:** EU (Portugal)

### 10.3 Cross-Border

**Consultant:** Ukrainian citizen, Portugal location  
**Client:** United States company  
**Services:** Remote (EU-based)

**Tax Compliance:**
- Each party responsible for own tax obligations
- Consultant provides tax forms if requested (W-8BEN, etc.)
- Any legally required withholding handled by Client per applicable law
- Client pays gross amount unless withholding mandated

**Invoice Requirements:**
- Consultant name and contact
- Invoice number and date
- Description of services
- Total in USD
- Payment method and details

### 10.4 Entire Agreement

This constitutes entire understanding. Amendments in writing (email acceptable).

---

## 11. SIGNATURES

**CONSULTANT:**

Signature: ___________________________  
Name: Anton Shumeiko  
Date: _____________  
Location: Porto, Portugal

**CLIENT:**

Signature: ___________________________  
Name: [Client Representative]  
Title: [Title]  
Date: _____________  
Location: [USA]

---

**Agreement Version:** 3.0 (Production Ready)  
**Last Updated:** January 9, 2026  
**Status:** Ready for Execution

---

## NEXT STEPS

**Upon Signing:**
1. Client receives Invoice #001 for Deposit ($1,000)
2. Payment via Wise/Revolut to: (details to be provided)
3. Work begins upon receipt of deposit
4. Start Date = Date of deposit receipt

---

*AI Engineering Services Agreement - Warehouse Forecasting PoC*
