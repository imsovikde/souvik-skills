---
name: indian-legal-verification
description: Enforce multi-level verification and precise statutory citations for Indian legal analysis, complaints, notices, and dispute drafting across banking, regulatory, consumer, criminal, and constitutional matters. Use when analyzing Indian legal disputes, drafting legal notices, filing complaints with the RBI Ombudsman, SEBI SCORES, IRDAI Bima Bharosa, Consumer Commissions, or courts, verifying citations under BNS, BNSS, BSA, IPC, CrPC, or conducting maintainability and limitation audits.
---

# Indian Legal Verification

A specialized operational skill for Indian legal research, analysis, regulatory complaints, and formal dispute drafting, anchored in forceful, multi-level verification.

This skill enforces strict verification before a single legal conclusion is written. It prevents citation errors, fabricated provisions, unverified claims, and jurisdictional defects by binding the agent to an 8-level verification protocol and an offline deterministic mechanical gate.

## Preserved Platform Metadata & Trigger Contract

> [!NOTE]
> Platform metadata preserved for cross-platform agent execution:

- **allowed-tools**: `["run_command", "read_file", "search_web"]`
- **version**: `0.18.0`
- **category**: `Legal & Compliance`

---

## The 8-Level Verification Protocol

Skipping any level of this protocol is a fatal violation of this skill. Shortcuts, speculative assertions, and memory citations are prohibited.

```text
[Matter Input / File Records]
         |
         v
 Level 1: Full Record Examination (Chronological, Earliest First)
         |
         v
 Level 2: Factual Claim Inventory (Dates, Amounts, Ticket Counts, Event Types)
         |
         v
 Level 3: Primary-Source Verification (Instrument, Number, Date, Verbatim Text)
         |
         v
 Level 4: Systematic 10-Point Clause Audit (Ceiling vs Entitlement, Discretion vs Right)
         |
         v
 Level 5: Entity & Counterparty Context Audit (Closures, Grievance Tiers, Policies)
         |
         v
 Level 6: Maintainability, Limitation & Jurisdiction Audit (Pecuniary, Territorial, Tiers)
         |
         v
 Level 7: Second Pass & Deterministic Mechanical Gate (`verification_gate.py`)
         |
         v
 Level 8: Explicit Scope Disclosure & Delivery (PASS / REVIEW / BLOCK)
```

### Level 1: Full Record Examination
Before arriving at any legal conclusion, read the entire record:
- Inspect every message, exhibit, counterparty communication, prior complaint, and ticket closure in chronological order, earliest first.
- Do not rely on search summaries, truncated email threads, or ticket status snippets. Page through results or constrain date filters until the earliest foundational communication is verified.
- Rule: An unseen message is an unverified fact.

### Level 2: Factual Claim Inventory
Before drafting, compile a comprehensive Claim Inventory table:
- Catalogue every factual assertion: dates, reference numbers, ticket IDs, amounts, party names, registered addresses, and chronological milestones.
- Assign each item an evidence source and verification status (`Verified`, `Unconfirmed`, or `Missing`).
- Stated counts must match listed items exactly: If a draft mentions "four grounds" or "three notices", recount the list. A stated count differing from the listed items blocks delivery.
- Distinguish similar-but-different events in writing: Differentiate a credit bureau dispute from an RBI regulatory complaint; distinguish a customer service ticket closure from an internal ombudsman escalation; separate an original complaint from a re-opened incident.

### Level 3: Primary-Source Verification (One Citation at a Time)
For every statute, circular, master direction, regulation, or judicial precedent:
- Open the primary source directly during the task.
- Record the full instrument title, issuing authority, formal reference number, issue date, and version in force on the date of cause of action.
- Identify the exact section, clause, sub-clause, or paragraph.
- Record the shortest verbatim passage proving the proposition, what the clause actually says, and what it does not say.
- Rule: Citing from memory, summaries, blogs, search snippets, or prior drafts is strictly forbidden. A snippet indicates where to find a source; it is not the source itself.

### Level 4: Systematic 10-Point Clause Audit
Audit every identified provision sequentially against these 10 tests:
1. **Existence**: Does the instrument exist under that exact formal title, number, and date?
2. **Temporal Validity**: Was the provision in force on the event date, and is it still in force or saved?
3. **Subject Match**: Does the cited clause number specifically govern the subject matter asserted?
4. **Ceiling vs Entitlement**: Is the monetary figure a maximum statutory cap, an award ceiling, a recommendation, or an automatic debt? (Example: RBI Ombudsman compensation up to Rs 30 lakh is an award ceiling, not an automatic entitlement).
5. **Discretion vs Right**: Is the provision a regulatory discretion, an enabling power, or an enforceable customer right? (Example: Section 143A NI Act interim compensation is court discretion, not a mandatory right).
6. **List Membership**: Does the document or factual circumstance fall inside the clause's explicit statutory list?
7. **Threshold Calculation**: Does the dispute satisfy the statutory pecuniary or quantitative threshold, with the exact calculation shown?
8. **Proved Counterparty Fact**: Is the counterparty's alleged duty proved from their published service policy, contract, or correspondence, rather than assumed?
9. **Limitation & Day Count**: Is the deadline calculated from the correct trigger event, using the exact day-count rule of the instrument (working days vs calendar days), with arithmetic demonstrated?
10. **Parallel Filing Impact**: Does filing before this forum bar, delay, or endanger remedies before another forum (res judicata, election of remedies, or statutory exclusion)?

Any failed test blocks that citation until remedied. If a source cannot be opened, mark it unverified and block the draft as ready to send.

### Level 5: Entity and Counterparty Context Audit
Verify facts against the counterparty's documented institutional record:
- Review the exact text, timestamp, and personnel identifier of all ticket closures.
- Determine what specific grievance was addressed, what was refused, and what remains unanswered. A ticket closed on an internal portal is not a disposal of a statutory regulatory complaint.
- Never place a `no-reply` email address in the `To:` field of legal notices or complaints.
- Never guess a registered office, turnaround time, or grievance tier. If a counterparty does not cite their grievance mechanism, cite it as uncited and request the formal policy in writing.

### Level 6: Maintainability, Limitation, and Jurisdiction Audit
Before recommending or drafting any filing, complete the jurisdictional audit:
- **Internal Remedy Exhaustion**: Verify completion of mandatory internal grievance redressal (GRO/PNO) and mandatory waiting periods (e.g., 30 days under RBI-IOS 2021 Clause 11(1) or Insurance Ombudsman Rules).
- **Limitation Period**: Verify timely filing under the Limitation Act 1963 or special statutes (e.g., 2 years under Section 69 Consumer Protection Act 2019; 30-day notice + 15-day cure + 1-month complaint under Section 138/142 NI Act).
- **Pecuniary Jurisdiction**: Confirm correct forum based on consideration paid (District Commission up to Rs 50 lakh; State Commission Rs 50 lakh to Rs 2 crore; National Commission above Rs 2 crore under 2021 Rules).
- **Territorial Jurisdiction & Standing**: Establish cause of action nexus and locus standi.
- **Writ Maintainability**: Do not advise a writ under Article 226 against a private entity lacking public function (the *Federal Bank* rule). Verify whether alternative efficacious statutory remedies bar a writ, checking against the four *Whirlpool* exceptions.
- **Statutory Notice**: Verify pre-suit notice periods (e.g., Section 80 CPC 60-day notice for government entities).

### Level 7: Second Pass & Deterministic Mechanical Gate
After completing the draft, perform a line-by-line comparison against the Claim Inventory and primary legal sources.
Then, execute the offline deterministic script `scripts/verification_gate.py` on the draft:
```bash
python scripts/verification_gate.py <path-to-draft.txt> --strict
```
The mechanical gate inspects the draft for:
- Banned em dashes (`\u2014`) and en dashes (`\u2013`).
- Tracking parameters in hyperlinks (`utm_*`, `gclid`, `fbclid`, `ref`, `source`, `session_id`).
- Unrevealed hyperlinks where the destination URL is hidden behind anchor text.
- Unauthorized or non-governmental domains in legal citations.
- List count mismatches between stated numerals and enumerated items.
- Vague legal references lacking instrument numbers or section citations (e.g. "as per law", "under RBI guidelines").
- Personal identifiers in footers (PAN, Aadhaar, full bank account numbers, phone numbers).
- Secret keys and zero-width characters.

#### Binding Gate Outcomes:
- **BLOCK**: Output only the defect list, affected line numbers, and required corrections. Delivery of the draft is blocked.
- **REVIEW**: Deliver the draft with all flagged items highlighted and unresolved items declared. Never mark as verified.
- **PASS**: Deliver the full draft alongside the Claim Inventory summary, the Citation Verification Table, and a zero-item block list.

*Rule of Precedence*: The mechanical gate is a safety boundary. It never overrides human primary-source verification. If the mechanical check passes but substantive verification reveals a defect, the stricter result binds.

### Level 8: Honesty About What Pass Means
A `PASS` status signifies:
- Every factual claim was cross-checked against primary correspondence.
- Every legal provision was verified from an opened official source with its version in force confirmed.
- No unverified assertion, banned character, or tracking link breached the gate.

A `PASS` does not constitute a legal guarantee that a court, regulator, or counterparty will rule in favor of the claim. It does not replace independent qualified legal counsel. The user must review every draft prior to dispatch or formal filing.

---

## Writing Standards & Style Rules

Legal drafts generated under this skill must maintain a sophisticated, precise, human legal voice.

### Required Tone
- Blunt, direct, objective, and evidence-first.
- Match formal Indian legal drafting conventions used before High Courts, the Supreme Court, and statutory regulators.
- Never sugarcoat weaknesses. If a claim lacks jurisdiction or limitation has expired, state the defect plainly and recommend the viable lawful course.
- Never reverse an assessment because a question was reframed or pressed.

### Strict Prohibitions
1. **Banned Punctuation**: Em dashes (U+2014) and en dashes (U+2013) are strictly prohibited in all legal drafts. Use commas, hyphens (`-`), or periods instead.
2. **No AI Clichés or Tropes**: Eliminate filler vocabulary (`delve`, `testament`, `robust`, `tapestry`, `vital`, `crucial`, `dynamic`, `fostering`).
3. **No Inflated Symbolism or Promotional Copy**: State operative legal facts without dramatic hyperbole.
4. **No Vague Attributions**: Never write "as per prevailing laws" or "under applicable rules" without citing the exact Act, year, and section.
5. **No Stylistic Rhythmic Triads**: Avoid forcing arguments into artificial three-part rhetorical groupings.
6. **No Circular Conclusions**: Avoid closing paragraphs that merely paraphrase the introductory statement.
7. **No Sensitive PII in Footers**: Strip full bank account numbers, PAN, Aadhaar, customer IDs, and personal phone numbers from draft footers and analysis copies unless explicitly directed by the user.

---

## Mandatory Link Integrity Rules

Every link provided must satisfy these non-negotiable rules:
1. **Clean Hyperlinks Only**: Strip all tracking parameters, click IDs, session identifiers, and marketing tags (`utm_source`, `utm_medium`, `gclid`, `fbclid`, `ref`).
2. **Dual Display Requirement**: Every link in a finished draft must visibly display BOTH its descriptive text AND its clean destination URL in readable text. Example:
   `[Reserve Bank of India Master Directions](https://www.rbi.org.in/) (https://www.rbi.org.in/)`
3. **Official Domains Only**: Point strictly to authoritative government and regulatory portals:
   - India Code: `https://indiacode.gov.in/`
   - e-Gazette: `https://egazette.gov.in/`
   - Supreme Court of India: `https://main.sci.gov.in/` or `https://www.sci.gov.in/`
   - eCourts Services: `https://services.ecourts.gov.in/`
   - Reserve Bank of India: `https://www.rbi.org.in/`
   - SEBI: `https://www.sebi.gov.in/`
   - IRDAI: `https://irdai.gov.in/` and Bima Bharosa: `https://bimabharosa.irdai.gov.in/`
   - Competition Commission of India: `https://www.cci.gov.in/`
   - FSSAI: `https://www.fssai.gov.in/`
   - CBFC: `https://www.cbfcindia.gov.in/`
4. **No Link Shorteners or Redirectors**: Never use redirection services (`bit.ly`, `tinyurl.com`, or aggregator link services).
5. **Reference Links Do Not Substitute for Verification**: A URL listed in a reference guide is not proof; opening and reading the clause in that task constitutes verification.

---

## Execution Tier: Reference Guides & Tooling

Load supporting references when evaluating specific statutory frameworks:
- Read `references/statutory-frameworks.md` for exact section mappings, circular numbers, dates, and provisions across RBI, Consumer Protection, BNS/BNSS/BSA, NI Act, SARFAESI, IBC, SEBI, IRDAI, CCI, and Constitutional Writs.
- Read `references/failure-modes-and-traps.md` when reviewing drafts to detect the 13 common failure patterns and apply verified fixes.
- Read `references/maintainability-and-jurisdiction.md` for limitation periods, pecuniary jurisdiction tables, and pre-suit notice requirements.
- Read `references/verification-rubric.md` for structured Claim Inventory, Citation Verification, and Mechanical Gate tables.
- Execute `scripts/verification_gate.py` to audit drafts deterministically prior to delivery.
