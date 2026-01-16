# CONSULTANCY AGREEMENT
## AI Engineering Services - Warehouse Forecasting System

**Agreement Date:** January 9, 2026  
**Effective Date:** [Start Date]  
**Term:** 8 weeks (with option to extend)

---

## PARTIES

**CONSULTANT:**  
Name: [Your Full Name]  
Title: Senior AI Engineer - Autonomous Systems Specialist  
Address: [Your Address]  
Email: [Your Email]  
Tax ID/EIN: [Your Tax ID]

**CLIENT:**  
Company: [Client Company Name]  
Address: [Client Address]  
Contact: [Client Contact Name]  
Email: [Client Email]

---

## 1. SCOPE OF SERVICES

The Consultant shall provide professional AI engineering services to design, develop, and deploy a **Warehouse Inventory Forecasting System** as detailed in the Technical Proposal (attached as Exhibit A).

### 1.1 Deliverables

**Phase 1: Setup & Validation (Weeks 1-2)**
- Deployed Docker environment with Chronos-2 model
- Initial forecast generation on historical data
- Validation report with MAPE < 15%
- Tuned alert threshold configuration

**Phase 2: Integration (Weeks 3-4)**
- Production data source integration
- Automated daily scheduling (cron/Docker Compose)
- Email alert configuration
- Stakeholder training sessions (2x 2-hour sessions)
- User documentation

**Phase 3: Optimization (Weeks 5-6)**
- Fine-tuned business rules based on feedback
- Custom visualization dashboards
- GPU performance optimization
- Technical documentation (architecture, API, troubleshooting)

**Phase 4: Handoff & Support (Weeks 7-8)**
- Knowledge transfer (4 hours total)
- 2 weeks monitored production runs
- Bug fixes & adjustments
- Support runbook and maintenance guide
- Source code handover with full documentation

### 1.2 Out of Scope

The following are **NOT** included in this agreement:
- Hardware procurement or IT infrastructure setup
- Integration with third-party ERP systems (beyond standard JSON/CSV export)
- Fine-tuning Chronos model on proprietary data (uses pretrained zero-shot)
- 24/7 production support beyond 8-week term
- Mobile app development
- Real-time API endpoint (can be added as change order)

---

## 2. COMPENSATION

### 2.1 Rate Structure

**Senior AI Engineer Consulting Rate:**

| Rate Type | Amount | Notes |
|-----------|--------|-------|
| **Hourly Rate** | $175-225/hr | Based on US market rates for Senior AI Engineers |
| **Half-Day (4 hrs)** | $700-900 | Meetings, training, knowledge transfer |
| **Full-Day (8 hrs)** | $1,400-1,800 | Deep work, development, debugging |

**Recommended Rate for this Project:** **$200/hour**

### 2.2 Project Estimate

Based on **8-week engagement** with estimated hours:

| Phase | Estimated Hours | Cost @ $200/hr |
|-------|-----------------|----------------|
| Phase 1: Setup & Validation | 80 hours | $16,000 |
| Phase 2: Integration | 60 hours | $12,000 |
| Phase 3: Optimization | 60 hours | $12,000 |
| Phase 4: Handoff & Support | 40 hours | $8,000 |
| **Total Estimated** | **240 hours** | **$48,000** |

### 2.3 Payment Structure

**Option A: Time & Materials (Recommended)**
- Invoiced bi-weekly based on actual hours worked
- Detailed timesheet provided with each invoice
- Payment due within 15 days of invoice date
- Not-to-exceed (NTE) cap: $55,000

**Option B: Fixed Price**
- Total project cost: $50,000
- Payment milestones:
  - 30% ($15,000) upon signing
  - 30% ($15,000) after Phase 2 completion
  - 30% ($15,000) after Phase 3 completion
  - 10% ($5,000) upon final handoff

**Option C: Hybrid**
- Fixed price for Phases 1-3: $40,000
- T&M rate ($200/hr) for Phase 4 support
- Payment schedule: 40% upfront, 40% mid-project, 20% completion

### 2.4 Expenses

Reasonable expenses will be reimbursed separately:
- Cloud compute credits (if AWS/GCP testing needed): Est. $500
- Software licenses (if proprietary tools needed): Est. $200
- Travel (if on-site required): Actual costs

**Total Estimated Expenses:** $700

---

## 3. TIMELINE & MILESTONES

| Milestone | Target Date | Deliverable | Payment Trigger |
|-----------|-------------|-------------|-----------------|
| **Kickoff** | Week 0 | Signed agreement | 30% deposit |
| **M1: System Deployed** | End of Week 2 | Validated forecasts (MAPE < 15%) | 20% |
| **M2: Production Integration** | End of Week 4 | Automated daily runs | 25% |
| **M3: Optimization Complete** | End of Week 6 | GPU-optimized, documented | 15% |
| **M4: Handoff** | End of Week 8 | Full knowledge transfer | 10% final |

### 3.1 Change Orders

Any changes to scope will be documented via Change Order form:
- Estimated hours and cost
- Impact on timeline
- Requires mutual written approval (email accepted)

---

## 4. INTELLECTUAL PROPERTY

### 4.1 Client Ownership

Upon final payment, Client owns:
- All source code developed for this project
- Documentation and technical specifications
- Configuration files and deployment scripts
- Any custom trained models or datasets (if applicable)

### 4.2 Consultant Retained Rights

Consultant retains:
- Right to use anonymized case study for portfolio (no client names/data without permission)
- Generic code utilities developed independently
- Pre-existing intellectual property

### 4.3 Open Source Components

The system utilizes open-source software under permissive licenses (Apache 2.0, MIT, BSD):
- Amazon Chronos-2 (Apache 2.0)
- LangGraph (MIT)
- PyTorch (BSD)

Client receives full rights to use, modify, and distribute these components per their respective licenses.

---

## 5. CONFIDENTIALITY & NDA

### 5.1 Confidential Information

Consultant acknowledges access to Client's confidential information:
- Warehouse inventory data
- Business processes and strategies
- Financial information
- Product compositions and BOMs

### 5.2 Obligations

Consultant agrees to:
- Keep all confidential information strictly confidential
- Not disclose to third parties without written consent
- Use information solely for performance of services
- Return or destroy confidential information upon termination

### 5.3 Data Processing

**NDA Compliance:**
- All processing occurs on Client's premises or approved infrastructure
- No data transmitted to third-party cloud services without approval
- Docker deployment ensures data isolation
- No telemetry or external API calls

**Term:** Confidentiality obligations survive termination for 5 years.

---

## 6. WARRANTIES & LIABILITIES

### 6.1 Consultant Warranties

Consultant warrants that:
- Services will be performed in professional, workmanlike manner
- Code will be original work or properly licensed
- No infringement of third-party IP rights
- Compliance with applicable laws

### 6.2 Client Warranties

Client warrants that:
- Provided data is accurate and up-to-date
- Has rights to use data for forecasting purposes
- Will provide timely feedback and approvals

### 6.3 Limitation of Liability

**Consultant's liability is limited to:**
- Direct damages only (no consequential damages)
- Maximum liability: Total fees paid under this agreement

**Exceptions:**
- Gross negligence or willful misconduct
- Breach of confidentiality

### 6.4 No Guarantees

Consultant makes no guarantees regarding:
- Specific forecast accuracy levels (MAPE targets are estimates)
- Business outcomes or ROI
- System uptime after handoff (Client responsible for infrastructure)

---

## 7. TERMINATION

### 7.1 Termination for Convenience

Either party may terminate with 14 days' written notice.

**Upon termination:**
- Consultant delivers work completed to date
- Client pays for hours worked + expenses incurred
- Client receives source code in current state

### 7.2 Termination for Cause

Either party may terminate immediately if:
- Material breach not cured within 14 days of written notice
- Bankruptcy or insolvency
- Violation of confidentiality

### 7.3 Post-Termination Support

If Client terminates before completion:
- Consultant provides 2 hours transition support (at hourly rate)
- Documentation of work completed
- Handoff of code repository access

---

## 8. INDEPENDENT CONTRACTOR

### 8.1 Relationship

Consultant is an **independent contractor**, not an employee. Consultant:
- Controls methods and means of work
- Provides own equipment and tools
- Responsible for own taxes and benefits
- No authority to bind Client

### 8.2 Taxes

Consultant is responsible for:
- Self-employment taxes
- Income tax withholding
- Business licenses/permits

Client will issue Form 1099-NEC (US) for payments ≥ $600/year.

---

## 9. GENERAL PROVISIONS

### 9.1 Entire Agreement

This Agreement, including attached Exhibit A (Technical Proposal), constitutes the entire agreement and supersedes all prior discussions.

### 9.2 Amendments

Must be in writing and signed by both parties (email with signaturesmay be accepted).

### 9.3 Governing Law

This Agreement shall be governed by the laws of [State/Country], without regard to conflict of law provisions.

### 9.4 Dispute Resolution

**Step 1:** Good faith negotiations (30 days)  
**Step 2:** Mediation (if negotiations fail)  
**Step 3:** Binding arbitration (American Arbitration Association rules)

### 9.5 Force Majeure

Neither party liable for delays due to circumstances beyond reasonable control (natural disasters, pandemics, government actions).

### 9.6 Assignment

Neither party may assign this Agreement without written consent, except:
- Client may assign to successor entity (merger/acquisition)
- Consultant may subcontract specific tasks (remains responsible)

### 9.7 Notices

All notices via email to addresses listed above, with confirmation of receipt.

---

## 10. ACCEPTANCE

By signing below, both parties agree to the terms and conditions of this Consultancy Agreement.

**CONSULTANT:**

Signature: _________________________  
Name: [Your Full Name]  
Date: _____________

**CLIENT:**

Signature: _________________________  
Name: [Client Contact Name]  
Title: [Client Title]  
Date: _____________

---

## EXHIBIT A: Technical Proposal

See attached document "TECHNICAL_PROPOSAL.md" (incorporated by reference)

---

## EXHIBIT B: Rate Justification

### Senior AI Engineer Market Rates (US, 2026)

**Data Sources:**
- Glassdoor: Senior ML Engineer - $150-250/hr consulting
- Upwork: AI/ML Specialists - $100-300/hr
- Toptal: Top 3% AI Engineers - $200-350/hr
- Indeed: Contract AI Engineers - $160-220/hr

**Factors Justifying $200/hr:**
- **Specialization:** Time series forecasting with transformer models (niche)
- **Experience:** Senior level (5+ years) with production deployment expertise
- **Technology Stack:** Cutting-edge (Chronos-2, LangGraph, GPT integration)
- **Deliverables:** Full system (not just proof-of-concept)
- **Business Impact:** Projected $732K/year ROI
- **NDA Compliance:** Expertise in sensitive data handling

**Comparable Rates:**
- Junior AI Engineer: $80-120/hr
- Mid-level ML Engineer: $120-180/hr
- **Senior AI Engineer: $175-225/hr** ← This engagement
- Principal/Staff AI Engineer: $250-400/hr

---

**Agreement Version:** 1.0  
**Last Updated:** January 9, 2026

---

*This is a template. Please have reviewed by legal counsel before execution.*
