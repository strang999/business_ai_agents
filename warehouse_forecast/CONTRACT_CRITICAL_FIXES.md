# CRITICAL FIXES - Paste These Sections

## FIX 1: Duration Alignment (Section 1.1)

**Replace line:**
~~Duration: ~1 week (5-6 business days)~~

**With:**
```
Duration: 1 calendar week (7 days)
Working days: 5-6 business days
Delivery: Day 7 or earlier
```

---

## FIX 2: Invoicing Consistency (Section 2.1)

**Replace payment section:**

```markdown
### 2.1 PoC Pricing

**Fixed Price: $2,500**

**Payment Schedule:**
- **40% ($1,000) - Non-refundable deposit**
  - Due: Upon contract signing
  - Non-refundable once work begins
  
- **60% ($1,500) - Final payment**
  - Due: Upon submission of deliverables
  - Payment deadline: Net 7 from submission
  - Late payments: 1.5% per month

**Acceptance Period:**
- Client has 3 business days to review after submission
- If defects reported, Consultant has 2 business days to remedy
- If no written rejection with specific defects, deemed accepted
- Acceptance does not affect payment obligation

**Hours Included:** Up to 30 hours

**Overage:**
- Hours beyond 30 require written pre-approval
- Rate: $90/hour
- Invoiced separately upon completion
```

---

## FIX 3: Governing Law (Section 10.3)

**Remove contradiction. Replace with:**

```markdown
### 10.3 Governing Law

**Governing Law:** Portuguese law (Lisbon jurisdiction)
**Disputes:** UNCITRAL arbitration rules
**Seat:** Lisbon, Portugal
**Language:** English
**Arbitrator:** 1 arbitrator

**Injunctive Relief:** Either party may seek court orders for IP or confidentiality breaches.

**Note:** Parties acknowledge cross-border nature. Contract interpretation follows Portuguese law principles.
```

**DELETE from Section 12.1:**
~~"International commercial law for contract"~~

---

## FIX 4: Termination Clarity (Section 7.1 & 7.2)

**Replace both subsections:**

```markdown
### 7.1 Early Termination

Either party may terminate with 3 days' written notice.

**Upon Termination:**
- 40% deposit is non-refundable (covers setup costs)
- Client pays for hours delivered beyond deposit at $90/hour
- Payment capped at fixed fee total ($2,500)
- Consultant delivers work completed to date
- Client receives all outputs generated

**Example:**
- Deposit paid: $1,000 (non-refundable)
- Hours worked: 20 hours
- Additional due: 20h × $90/h = $1,800
- Total: $1,000 + $1,800 = $2,800 → capped at $2,500
- Client owes: $1,500 additional

### 7.2 Completion

**After PoC:**
- No refunds for completed work
- Client decides: Proceed to Phase 2 / Pause / Stop
- No obligation to continue

**After Phase 2:**
- Full code transfer upon final payment
- 2-week email support for questions
```

---

## FIX 5: Dashboard Definition (Section 1.1)

**Add to Deliverables section:**

```markdown
**Dashboard Specification:**
- Single page web interface
- 3 core charts: forecast trends, accuracy metrics, alert summary
- Filters: product selector, date range
- Export: CSV download capability
- Status: Demo-ready prototype (not production-grade)
```

---

## FIX 6: Data Quality Protection (Section 1.3 or new 1.4)

**Add new subsection:**

```markdown
### 1.4 Data Quality Assumptions

**Client Responsibilities:**
- Provide clean, structured data in agreed format
- Data completeness: minimum 3 months history
- Data quality: <20% missing values per product

**If Significant Cleaning Required:**
- Beyond 5 hours of data cleaning/preprocessing
- Consultant may request scope adjustment
- Options: extend timeline or bill extra hours at $90/hr
- Requires written agreement to proceed
```

---

## FIX 7: Client Delay Rights (Section 1.1 or 1.3)

**Add to "Client Dependencies":**

```markdown
**Timeline assumes timely data access and feedback.**

**Delay Protocol:**
- Minor delays (<3 days): Extend deadline day-for-day
- Major delays (>3 days): Consultant may reschedule project to mutually agreed dates
- Deposit remains non-refundable
- Client notified in writing of reschedule option
```

---

## FIX 8: Tax Withholding (Section 12.2)

**Replace line:**
~~No withholding required (independent contractor)~~

**With:**

```markdown
**Tax Compliance:**
- Each party responsible for own tax obligations
- Consultant may provide tax forms if requested (W-8BEN, etc.)
- Any legally required withholding handled by Client per applicable law
- Client pays gross invoice amount unless withholding mandated
```

---

## FIX 9: Data Breach Scope (Section 11.4)

**Add clarification:**

```markdown
### 11.4 Data Breach Protocol

**Breach Definition:**
- Suspected unauthorized access to Client data on Consultant systems
- Loss, theft, or compromise of devices containing Client data
- Accidental disclosure to third parties

**In case of breach:**
1. Consultant notifies Client within 24 hours of discovery
2. Provides details: nature, categories affected, estimated scope
3. Cooperates on breach mitigation
4. Documents incident

**Client Responsibilities:**
- Client is responsible for regulatory reporting as Data Controller
- Client determines notification to authorities/data subjects per GDPR
- Consultant provides reasonable assistance
```

---

## FIX 10: Phase 2 Scope Limits (Section 1.2)

**Add to Phase 2:**

```markdown
**Phase 2 Includes:**
- Development and integration work
- One deployment environment (provided by Client)
- Documentation and handoff training (up to 4 hours)

**Phase 2 Excludes:**
- 24/7 operations support
- SLA guarantees
- Ongoing monitoring (available on retainer)
- Multi-environment deployments
- Production incident response
```

---

## SUMMARY OF ALL FIXES:

✅ Duration: 1 calendar week (not "~1 week")
✅ Payment: Upon submission (not acceptance)
✅ Deposit: Non-refundable after start
✅ Governing law: Portuguese only (removed contradiction)
✅ Termination: Pro-rata at $90/hr capped at $2,500
✅ Overage: $90/hr with pre-approval
✅ Dashboard: Defined scope (3 charts, demo-ready)
✅ Data cleaning: >5 hours billable extra
✅ Delays >3 days: Right to reschedule
✅ Tax: Neutral compliance language
✅ Breach: Client responsible for reporting
✅ Phase 2: Excludes 24/7 ops/SLAs

---

## МОЯ РЕКОМЕНДАЦІЯ:

**НЕ переписуй весь контракт.** Клієнт побачить 10 версій і відмовиться.

**Зроби так:**
1. Підпиши як є (90% безпечно)
2. **Головний захист:** Тримай код до моменту підтвердження оплати 60%
3. Демо на своєму екрані або тестовому сервері
4. Docker image + deployment docs передаєш ТІЛЬКИ ПІСЛЯ payment confirmation

**Якщо хочеш update contract:**
- Застосуй тільки FIX 2 (Payment), FIX 4 (Termination), FIX 5 (Dashboard)
- Решта менш критично

**Твій вибір?**
