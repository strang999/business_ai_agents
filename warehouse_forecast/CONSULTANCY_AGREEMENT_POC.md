# CONSULTANCY AGREEMENT
## AI Engineering Services - Warehouse Forecasting PoC

**Agreement Date:** January 9, 2026  
**Effective Date:** [Start Date]  
**Engagement Type:** Proof of Concept (1 week) with optional production extension

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

### 1.1 Proof of Concept (Phase 1)

**Duration:** ~1 week (5-6 business days)

**Deliverables:**
- Working forecast system with client's warehouse data
- Accuracy validation report (MAPE, RMSE, confidence intervals)
- Sample 30-day forecasts for top 50 products
- Interactive dashboard prototype
- Technical findings document
- ROI projection based on actual results
- Production roadmap recommendation

**Success Criteria:**
- System processes data without errors
- MAPE <15% on validation set
- Dashboard functional and demonstrates value

### 1.2 Optional Phase 2 (If PoC Successful)

**Duration:** +2-3 weeks (pending approval after PoC)

**Additional Deliverables (Phase 2):**
- RAG (Retrieval-Augmented Generation) integration
- Vector database (ChromaDB) for schema knowledge
- Context-aware alerting system
- Natural language explanations (LLM-powered)
- Continuous learning & feedback loop
- Full production deployment
- Complete documentation & training

**Approval Required:** Client reviews PoC results before authorizing Phase 2

### 1.3 Out of Scope

**NOT included in base agreement:**
- Hardware procurement or server setup
- ERP system integration (beyond JSON/CSV export)
- 24/7 production support
- Custom model training (uses pretrained Chronos-2)

---

## 2. COMPENSATION

### 2.1 PoC Pricing Options

**Option A: Fixed Price**
- **PoC Total: $2,500**
  - Payment: 40% ($1,000) upon contract signing
  - Payment: 60% ($1,500) upon delivery & presentation
  - Includes all deliverables listed in Section 1.1
  - Up to 30 hours of work included

**Option B: Hybrid Model**
- **Setup Fee: $1,200** (due upon contract signing)
  - Covers: Architecture design, data integration, initial prototype
- **Refinement Rate: $90/hour**
  - Billed for additional iterations and adjustments
  - Estimated: 10-15 hours
  - **Total Estimated: $2,100 - $2,550**
  - Invoiced upon completion

**Option C: Time & Materials**
- **Hourly Rate: $90/hour**
  - Estimated hours: 20-30 hours total
  - **Total Estimated: $1,800 - $2,700**
  - Invoice submitted at PoC completion
  - Payment due within 7 business days

### 2.2 Phase 2 Pricing (If Approved)

**Full Production Deployment:**
- **Fixed Price: $5,500 (discussable in case of long-term engagement)**
  - Payment: 40% ($2,200) at start
  - Payment: 60% ($3,300) upon completion
- **Alternative: $85/hour**
  - Estimated: 60-80 hours
  - Total: $5,100 - $6,800

### 2.3 What's Included

All options include:
- Working forecast system
- Accuracy validation report
- Interactive dashboard prototype
- 30-day forecast samples
- Technical findings document
- ROI projection
- Production roadmap
- Final presentation (1 hour)

### 2.4 Expenses

No additional expenses anticipated for remote work.

---

## 3. TIMELINE & MILESTONES

### Phase 1 (PoC) - Week 1

| Day | Activity | Deliverable |
|-----|----------|-------------|
| 1-2 | Setup & data integration | System running |
| 3-4 | Forecasting & validation | Accuracy results |
| 5-6 | Dashboard & analysis | Prototype ready |
| 7 | Presentation | Decision package |

**Checkpoint:** End of Week 1
- Review PoC results
- Decide: Proceed to Phase 2 / Pause / Stop

### Phase 2 (Optional) - Weeks 2-4

| Week | Focus | Milestone |
|------|-------|-----------|
| 2 | RAG setup, vector DB | Schema intelligence |
| 3 | LLM integration, explanations | Smart alerts |
| 4 | Production hardening, docs | Full deployment |

**Final Delivery:** End of Week 4 (if Phase 2 approved)

---

## 4. INTELLECTUAL PROPERTY

### 4.1 During PoC

**Consultant retains:**
- Source code ownership
- System architecture
- Implementation expertise

**Client receives:**
- All forecast outputs and reports
- Dashboard access
- Analysis and recommendations
- Right to use outputs for business decisions

### 4.2 Upon Phase 2 Completion (If Executed)

**Client owns:**
- Full source code
- All documentation
- Configuration files
- Deployment scripts
- Trained models (if any)

**Consultant retains:**
- Right to anonymized case study (no client data/names)
- Generic utilities developed independently
- Portfolio reference (with permission)

### 4.3 Open Source

System uses open-source components:
- Amazon Chronos-2 (Apache 2.0)
- LangGraph (MIT License)
- PyTorch (BSD License)

Client receives full rights to use/modify per respective licenses.

---

## 5. CONFIDENTIALITY

### 5.1 Confidential Information

Consultant acknowledges access to:
- Warehouse inventory data
- Business processes
- Product information
- Strategic plans

### 5.2 Obligations

Consultant agrees to:
- Keep all information strictly confidential
- Not disclose to third parties
- Use data solely for this project
- Return/destroy data upon termination

### 5.3 NDA Compliance

**Technical Measures:**
- All processing on-premises or approved infrastructure
- No cloud upload without explicit permission
- Docker isolation
- No telemetry or external API calls
- Local LLM only (if Phase 2)

**Duration:** 5 years post-termination

---

## 6. WARRANTIES & LIABILITIES

### 6.1 Consultant Warranties

- Professional, workmanlike services
- Original code or properly licensed
- No IP infringement
- Industry best practices

### 6.2 Client Warranties

- Data accuracy and completeness
- Right to use data for forecasting
- Timely feedback and approvals

### 6.3 Limitation of Liability

**Maximum liability:** Total fees paid under this agreement

**No liability for:**
- Consequential damages
- Business losses beyond direct fees
- Third-party claims

**Exceptions:**
- Gross negligence
- Willful misconduct
- Confidentiality breach

### 6.4 No Performance Guarantees

Consultant makes **best effort** but does NOT guarantee:
- Specific MAPE levels (targets are estimates)
- Particular business outcomes or ROI
- System uptime post-handoff

**PoC is validation exercise, not production commitment.**

---

## 7. TERMINATION

### 7.1 Early Termination

Either party may terminate with 3 days' written notice.

**Upon termination:**
- Consultant delivers work completed to date
- Client pays for hours worked (if T&M) or pro-rata (if fixed)
- Client receives outputs generated so far
- No penalty for early stop

### 7.2 Natural Completion

**After PoC:**
- Client decides to proceed to Phase 2 or stop
- No obligation to continue if PoC unsatisfactory
- Partial refund if MAPE >20% (at consultant discretion)

**After Phase 2:**
- Full code transfer upon final payment
- 2-week email support for clarifications
- Handoff complete

---

## 8. WORKING RELATIONSHIP

### 8.1 Independent Contractor

Consultant is **independent contractor**, not employee:
- Controls own work methods
- Provides own equipment
- Responsible for own regulatory compliance
- No employee benefits

### 8.2 Communication

**During PoC:**
- Daily progress updates via Slack/email
- Quick call if blockers (15-30 min)
- Final presentation (1 hour)

**Availability:**
- Standard business hours (flexible timezone)
- Response within 4-6 hours business days
- No 24/7 on-call

### 8.3 Tools & Access

**Consultant provides:**
- Development environment
- Docker setup
- Code repository

**Client provides:**
- Data access (secure folder/drive)
- Test environment (if needed)
- Feedback and decisions

---

## 9. PAYMENT METHODS

**Accepted:**
- Wise/Revolut (preferred)
- Bank transfer
- PayPal (if necessary, +3% fee)
- Cryptocurrency (if mutually agreed)

**Currency:** USD or EUR (specify in invoice)

**Invoicing:**
- PoC: Single invoice at completion (Options A/C) or split (Option B)
- Phase 2: Bi-weekly or upon milestones

---

## 10. GENERAL PROVISIONS

### 10.1 Entire Agreement

This agreement constitutes entire understanding between parties.

### 10.2 Amendments

Changes must be in writing (email acceptable).

### 10.3 Governing Law

International commercial law / International arbitration (UNCITRAL rules)

### 10.4 Dispute Resolution

1. Good faith discussion (7 days)
2. Mediation (if needed)
3. Arbitration (binding)

### 10.5 Language

Agreement in English. If translated, English version prevails.

---

## 11. GDPR & DATA PROTECTION COMPLIANCE

### 11.1 Data Processing Roles

**Consultant acts as Data Processor:**
- Processes Client warehouse data solely for forecasting services
- Does not determine purposes or means of processing
- Follows Client instructions for data handling

**Client acts as Data Controller:**
- Determines purposes and means of data processing
- Responsible for lawful basis and data subject rights

### 11.2 Data Processing Agreement (DPA)

**Processing Activities:**
- Access to warehouse inventory data
- Storage on Consultant secure devices (encrypted)
- Processing via AI models (local, no cloud)
- Temporary retention during engagement only

**Security Measures:**
- Data encrypted at rest (AES-256)
- Docker containerization for isolation
- No transmission to third parties
- No sub-processors without written approval
- Secure deletion upon project completion

### 11.3 GDPR Compliance Obligations

**Consultant commits to:**
- Process data only as instructed by Client
- Ensure confidentiality of persons accessing data
- Implement appropriate technical measures
- Assist Client with data subject requests if needed
- Notify Client of any data breach within 24 hours
- Delete or return all data upon termination

**Data Retention:**
- Active engagement: Encrypted local storage only
- Post-termination: Complete deletion within 7 days

**Data Transfers:**
- No transfer outside EU without explicit consent
- Processing occurs in EU (Portugal)
- Client acknowledges EU data processing location

### 11.4 Data Breach Protocol

**In case of breach:**
1. Consultant notifies Client immediately (within 24 hours)
2. Provides details: nature, categories affected
3. Cooperates on breach mitigation
4. Documents incident for regulatory reporting

---

## 12. CROSS-BORDER PROVISIONS

### 12.1 Jurisdictions

**Consultant:** Ukrainian citizen, located in Portugal  
**Client:** United States company  
**Services:** Remote (EU-based)

**Applicable Law:**
- EU GDPR for data processing
- International commercial law for contract

### 12.2 Payment & Invoicing

**Consultant:**
- Independent contractor (self-employed)
- Issues professional invoices for services
- Handles own regulatory compliance

**Client:**
- Pays gross invoice amount in USD
- No withholding required (independent contractor)

**Invoice Requirements:**
- Consultant name and contact details
- Invoice number and date  
- Description of services and hours
- Total amount in USD
- Payment method: Wise/Revolut preferred

---

## 13. SIGNATURES

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

**Agreement Version:** 1.2  
**Last Updated:** January 9, 2026  
**Governing Law:** International commercial law / International arbitration (UNCITRAL rules)  
**Data Processing:** EU GDPR compliant

---

*Professional AI Engineering Services Agreement*
