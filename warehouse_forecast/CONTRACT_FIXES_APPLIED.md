# CRITICAL SECTIONS - Ready to Paste

## 1. SCOPE OF SERVICES (FIXED)

### 1.1 Proof of Concept (Phase 1)

**Duration:** ~1 week (5-6 business days)

**Estimated Effort:** 20-30 hours total  
**Availability:** Up to 4 hours per business day  
**Timeline:** Subject to timely data access and feedback

**Deliverables:**
- Working forecast pipeline (end-to-end execution)
- Validation report (MAPE, RMSE, data quality assessment)
- Sample 30-day forecasts for key products
- Interactive dashboard prototype
- Technical findings document
- High-level savings estimate (with documented assumptions)
- Production roadmap

**Performance Target (non-binding):**
- Aim for MAPE <15% on validation split, subject to data quality

**Delivery Criteria:**
- System executes end-to-end on agreed dataset
- Validation report includes metrics and failure analysis
- Forecast samples delivered
- Dashboard demonstrates functionality

**Acceptance:**
Client has 3 business days to review deliverables. If no written rejection with specific defects is provided, deliverables are deemed accepted. Acceptance is not contingent on specific MAPE values.

### 1.2 Optional Phase 2 (If PoC Approved)

**Duration:** +2-3 weeks

**Capabilities Added:**
- Natural language forecast explanations
- Context-aware alerting with business rules
- Historical pattern learning
- Full production deployment

**Approval Required:** Client reviews PoC results before authorizing Phase 2

### 1.3 Out of Scope

- Hardware procurement or IT infrastructure
- ERP system integration (beyond JSON/CSV)
- 24/7 production support
- Custom model training

**Change Requests:** Any work outside this scope requires written change request and may affect timeline and fees.

**Client Dependencies:** Timeline assumes timely data access and feedback. Delays extend deadlines day-for-day.

---

## 2. COMPENSATION (FIXED)

### 2.1 PoC Pricing

**Fixed Price: $2,500**
- Payment: 40% ($1,000) upon contract signing
- Payment: 60% ($1,500) upon delivery
- Includes all deliverables in Section 1.1
- Covers up to 30 hours of work

**What's Included:**
- Complete end-to-end system
- Accuracy validation
- Dashboard prototype
- Technical documentation
- Final presentation (1 hour)

**Payment Terms:**
- Final payment due Net 7 from delivery
- Late payments accrue 1.5% per month

### 2.2 Phase 2 Pricing (If Approved)

**Fixed Price: $5,500**
- Payment: 40% ($2,200) at start
- Payment: 60% ($3,300) upon completion

---

## 4. INTELLECTUAL PROPERTY (SIMPLIFIED)

### 4.1 Code Ownership

**Upon Final Payment:**
- Client owns all PoC source code
- Client owns all documentation
- Client owns all configurations
- Client owns all deliverables

**Consultant Retains:**
- Right to anonymized case study (no client data/names)
- Generic utilities developed independently
- Portfolio reference (with client approval)

### 4.2 Open Source Components

System uses:
- Amazon Chronos-2 (Apache 2.0)
- LangGraph (MIT)
- PyTorch (BSD)

Client receives rights per respective open-source licenses.

---

## 5. CONFIDENTIALITY (UPDATED)

### 5.3 NDA Compliance

**Security Measures:**
- Data encrypted at rest
- Docker containerization for isolation
- No cloud uploads without written client approval
- No external API calls without written client approval
- Secure deletion upon project completion

**Duration:** 5 years post-termination

---

## 7. TERMINATION (FIXED)

### 7.1 Early Termination

Either party may terminate with 3 days' written notice.

**Upon termination:**
- Consultant delivers work completed to date
- Client pays pro-rata portion of fixed fee
- Client receives all outputs generated
- No penalty for early stop

### 7.2 Completion

**After PoC:**
- Client decides to proceed to Phase 2 or stop
- No obligation to continue
- No refunds (work completed as agreed)

**After Phase 2:**
- Full code transfer upon final payment
- 2-week email support for questions
- Handoff complete

---

## 10. GENERAL PROVISIONS (UPDATED)

### 10.3 Governing Law

**Jurisdiction:** Portuguese law (Lisbon)  
**Disputes:** UNCITRAL arbitration rules  
**Arbitration Seat:** Lisbon, Portugal  
**Language:** English  
**Arbitrators:** 1 arbitrator

**Injunctive Relief:** Either party may seek court relief for confidentiality or IP breaches in competent courts.

### 10.4 Dispute Resolution

1. Good faith discussion (7 days)
2. Mediation (optional, if agreed)
3. Binding arbitration per Section 10.3

---

## 11. GDPR (NO CHANGES - KEEP AS IS)

[Current section is fine, no edits needed]

---

## 12. CROSS-BORDER (NO CHANGES - KEEP AS IS)

[Current section is fine, no edits needed]

---

# SUMMARY OF FIXES APPLIED:

✅ **Risk 1:** Success criteria → Delivery criteria (MAPE is target, not acceptance)  
✅ **Risk 2:** Removed refund language  
✅ **Risk 3:** Added Net 7 + late fee (1.5%/month)  
✅ **Risk 4:** Explicit 4hrs/day, 20-30 hours total  
✅ **Risk 5:** Governing law → Lisbon, UNCITRAL with seat  
✅ **Risk 6:** Security measures softened ("with approval")  
✅ **Risk 7:** IP simplified - client gets code on payment (no buyout needed)  

✅ **Missing A:** 3-day acceptance window added  
✅ **Missing B:** Change request clause added  
✅ **Missing C:** Client dependency clause added  

✅ **Bonus:** Phase 2 shortened to business outcomes  
✅ **Bonus:** ROI → "savings estimate with assumptions"
