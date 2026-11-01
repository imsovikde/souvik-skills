# Verification Rubric and Operational Templates

This reference establishes the mandatory audit schemas and structured report tables required for every legal analysis, complaint, and draft produced under the Indian Legal Verification protocol.

---

## 1. Factual Claim Inventory Table

Every factual assertion must appear in the Claim Inventory prior to drafting.

| Claim ID | Factual Assertion / Event Description | Date & Time | Stated Amount / Identifier | Source Document / Exhibit | Status (`Verified` / `Unconfirmed`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | Unauthorised ATM withdrawal transaction | 2024-09-12 14:22 IST | Rs 10,000.00 | Bank Account Statement, Page 2, Line 14 | Verified |
| **CLM-02** | Customer formal written dispute lodged via email | 2024-09-13 09:15 IST | Complaint Ref #492810 | Outbox Email Transcript & Delivery Receipt | Verified |
| **CLM-03** | Branch automated SMS ticket closure without investigation | 2024-09-18 18:05 IST | Ticket #492810 closed | SMS text record from sender VM-HDFCBK | Verified |
| **CLM-04** | Escalation letter delivered to Principal Nodal Officer | 2024-09-22 11:30 IST | Speed Post Tracking #ED83910284IN | India Post Tracking Delivery Confirmation | Verified |

### Enumeration Rule
If the draft contains a statement such as "The Complainant relies upon the following 4 communications:", the inventory recount must verify exactly 4 entries. Any count mismatch blocks delivery.

---

## 2. Primary Source Citation Verification Table

Every legal instrument, circular, or precedent must be catalogued in this table.

| Citation ID | Instrument Title & Issuing Authority | Number & Issue Date | Version in Force on Event Date | Exact Section / Clause | Verbatim Passage Proving Proposition | Positive Meaning (What it Actually Says) | Negative Boundary (What it Does NOT Say) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CIT-01** | Customer Protection - Limiting Liability in Unauthorised Transactions (RBI) | DBR.No.Leg.BC.78/09.07.005/2017-18 dated July 6, 2017 | Active and in force | Paragraph 6(b) | "Third party breach where the deficiency lies neither with the bank nor with the customer... and customer notifies bank within three working days..." | Confers absolute zero liability upon customer if notified within three working days. | Does NOT apply if customer notified on or after the fourth working day (which falls under Paragraph 7). |
| **CIT-02** | Reserve Bank of India - Integrated Ombudsman Scheme, 2021 (RBI) | CEPD. PR. No. S802/13.01.001/2021-2022 dated Nov 12, 2021 | Active and in force | Clause 11(1)(b) | "the complainant had not received any reply within a period of 30 days after the Regulated Entity received the representation..." | Confers locus standi to approach Ombudsman after 30 days lapse. | Does NOT permit filing prior to the expiration of the full 30-day window. |
| **CIT-03** | Consumer Protection Act, 2019 (Parliament of India) | Act No. 35 of 2019, notified August 9, 2019 | Active; effective July 20, 2020 | Section 2(7)(a) | "does not include a person who obtains such goods for resale or for any commercial purpose..." | Excludes commercial transactions from consumer forum protection. | Does NOT exclude individuals who purchase goods exclusively for livelihood through self-employment. |

---

## 3. Entity & Counterparty Record Audit Schema

| Communication ID | Counterparty Name | Direction (`Inbound` / `Outbound`) | Timestamp | Exact Text of Closure / Reply | Grievance Addressed | Grievance Remaining Unaddressed | Verified Official Contact Used |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **COMM-01** | HDFC Bank Support | Outbound | 2024-09-13 09:15 | Customer complaint detailing card skimming | Dispute registered | Liability determination | `support@hdfcbank.com` |
| **COMM-02** | HDFC Bank Support | Inbound | 2024-09-18 18:05 | "Ticket closed as transaction done with valid PIN" | Asserts PIN entry | Did not address CCTV footage request | `noreply@hdfcbank.com` (Do not use in To:) |
| **COMM-03** | Principal Nodal Officer | Outbound | 2024-09-22 11:30 | Formal escalation under RBI Circular | Reversal requested | Unanswered (Awaiting 30 days) | `pno@hdfcbank.com` |

---

## 4. Systematic 10-Point Clause Audit Checklist

Run sequentially for every citation in the draft:

| Test ID | Audit Question | Pass Condition | Mandatory Evidence Required |
| :--- | :--- | :--- | :--- |
| **TST-01** | Instrument Existence | PASS | Exact title, issuing body, notification number, and gazette date confirmed. |
| **TST-02** | Temporal Validity | PASS | Provision was in force on the date of transaction and is active today. |
| **TST-03** | Subject Matter Alignment | PASS | Clause title specifically covers the legal issue in dispute. |
| **TST-04** | Ceiling vs Entitlement | PASS | Cap is pleaded as a discretionary maximum, not a liquidated debt. |
| **TST-05** | Discretion vs Right | PASS | Discretionary powers pleaded as "may"; rights pleaded as "shall". |
| **TST-06** | List Inclusion | PASS | Factual instrument falls squarely inside statutory definitions. |
| **TST-07** | Threshold Calculation | PASS | Mathematical calculation demonstrated in the text. |
| **TST-08** | Proved Institutional Policy | PASS | Counterparty obligation established from contract or policy. |
| **TST-09** | Day-Count Arithmetic | PASS | Working days vs calendar days calculated with Day 0 excluded. |
| **TST-10** | Parallel Bar Verification | PASS | Forum rules checked; no conflicting simultaneous suit pending. |

---

## 5. Mechanical Gate Audit Matrix

The script `scripts/verification_gate.py` runs these deterministic checks:

| Check Item | Defect Pattern | Action on Detection |
| :--- | :--- | :--- |
| **Banned Dashes** | Em dash (`\u2014`) or En dash (`\u2013`) | **BLOCK**: Replace with comma, hyphen (`-`), or period. |
| **Tracking URLs** | Query strings containing `utm_*`, `gclid`, `fbclid`, `ref` | **BLOCK**: Strip query parameters down to clean canonical URL. |
| **Hidden Link Targets** | Markdown links where destination URL is not in visible text | **BLOCK**: Format as `[Text](URL) (URL)` to display clean URL. |
| **Unofficial Domains** | Legal citations pointing to commercial blogs or aggregators | **BLOCK**: Replace with official government portal (`.gov.in`, `.rbi.org.in`, `.sci.gov.in`). |
| **Count Mismatch** | Stated numeral does not equal count of following enumerated items | **BLOCK**: Recount list and synchronize numeral with actual items. |
| **Vague Citations** | Phrases like "as per law" or "under RBI circular" without number | **BLOCK**: Supply exact circular number and clause, or strike. |
| **PII in Footer** | Full PAN, Aadhaar, account number, or personal mobile in footer | **BLOCK**: Redact PII from footers and analysis copies. |
| **Secret Tokens** | Tokens matching `sk-...`, `ghp_...`, `AKIA...`, `AIza...` | **BLOCK**: Purge tokens immediately. |

---

## 6. Binding Gate Outcomes

### Outcome: BLOCK
When any gate assertion fails:
- Do NOT deliver the draft as ready to send.
- Deliver only:
  1. The Failure List with exact line numbers;
  2. The Mechanistic Root Cause for each failure;
  3. The Precise Correction required to achieve compliance.

### Outcome: REVIEW
When factual claims lack documentary proof but are flagged as unverified:
- Deliver the draft with unverified items bracketed and highlighted.
- Do NOT certify the draft as verified.
- Disclose all missing documents needed from the user.

### Outcome: PASS
When 100% of claims are verified against primary records, all citations verified against opened official sources, and the mechanical gate exits with code 0:
- Deliver the complete final draft in the message.
- Deliver the Claim Inventory Summary.
- Deliver the Citation Verification Table.
- Deliver the Mechanical Gate Verification Report showing zero defects.

---

## 7. Scope & Delivery Honesty Declaration

Every delivered draft must conclude with this standardized declaration:

```markdown
### Verification & Delivery Audit Summary
- **Total Factual Claims Inventoried**: [N] (100% mapped to record)
- **Total Legal Citations Verified**: [M] (100% opened from primary sources)
- **Mechanical Gate Exit Code**: 0 (PASS - Zero defects, zero banned dashes, clean URLs)
- **Statutory Notice & Jurisdiction Status**: Verified compliant
- **Disclosure**: This verification establishes factual mapping and statutory citation accuracy. It does not constitute a guarantee of judicial or regulatory acceptance, nor does it replace independent licensed legal counsel.
```
