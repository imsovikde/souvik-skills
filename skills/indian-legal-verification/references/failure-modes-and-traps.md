# Legal Draft Failure Modes and Trap Catalog

This reference details the 13 recurring failure patterns in automated and unverified legal drafting under Indian law. Every agent must audit drafts against this catalog before certifying any filing or advice.

---

## Trap 1: Citing from Memory Instead of an Opened Primary Source

### The Failure Mechanism
The drafter generates a section number, circular title, or legal formula from parametric memory without retrieving the official text. The citation resembles a real provision but contains hallucinated sub-clauses, misstated penalties, or nonexistent procedural steps.

### Example Defect
Asserting that "under Section 138(2) of the Negotiable Instruments Act, the bank must refund dishonour charges within 7 days." Section 138 contains provisos (a), (b), and (c); it contains no sub-section (2), nor does it govern refund of bank charges.

### Mandatory Audit Check
Every provision cited must be paired with:
1. Formal title and issuing authority.
2. Official notification or circular number.
3. Exact issue date.
4. Verbatim text from an opened primary source.

### The Concrete Fix
Open [India Code](https://indiacode.gov.in/) (https://indiacode.gov.in/) or the regulator's portal. If the exact sub-clause text cannot be retrieved, strike the citation and state the requirement plainly as unverified.

---

## Trap 2: Clause Number Belonging to a Different Subject

### The Failure Mechanism
The drafter cites an authentic instrument but attributes a proposition to a clause or section that governs an entirely different topic.

### Example Defect
Citing "Clause 10 of the Reserve Bank of India - Integrated Ombudsman Scheme, 2021" to argue that a complaint must be filed within one year. Clause 10 governs "Grounds of Complaint" (deficiency in service); limitation is governed strictly by Clause 11(2).

### Mandatory Audit Check
Cross-reference the section heading and subject-matter scope against the factual proposition. The subject of the clause must match the proposition asserted.

### The Concrete Fix
Verify the structural table of contents of the statute or direction. Re-map the proposition to its genuine provision (e.g., Clause 11(2) for limitation under RB-IOS 2021).

---

## Trap 3: Superseded Scheme or Repealed Direction

### The Failure Mechanism
Citing an outdated, repealed, or superseded statutory scheme or regulatory circular.

### Example Defects
- Citing the Banking Ombudsman Scheme 2006 instead of the Reserve Bank of India - Integrated Ombudsman Scheme, 2021.
- Citing Section 420 IPC for a cheating incident that occurred in August 2024 (must be Section 318(4) BNS 2023).
- Citing Section 65B of the Indian Evidence Act, 1872 for an affidavit filed in late 2024 (governed by Section 63 BSA 2023).
- Citing the Consumer Protection Act, 1986 instead of the 2019 Act.

### Mandatory Audit Check
Check the date of the cause of action and check whether the statute has been repealed, amended, or consolidated. For criminal offences, check whether the event occurred prior to or after July 1, 2024.

### The Concrete Fix
Cite the active instrument in force on the cause-of-action date, noting repeal and savings provisions (e.g., Section 531 BNSS 2023).

---

## Trap 4: Ceiling, Recommendation, or Award Presented as an Entitlement

### The Failure Mechanism
Presenting a statutory maximum compensation ceiling, an ombudsman award cap, or an administrative recommendation as an automatic liquidated debt or customer entitlement.

### Example Defect
Demanding that "the bank must immediately pay the complainant Rs 30,00,000 as per Clause 15(3) of the RBI Integrated Ombudsman Scheme, 2021."

### The Real Law
Clause 15(3) provides a maximum discretionary ceiling for consequential damages that an Ombudsman may award after adjudicating loss. It is not an entitlement due upon filing a dispute.

### Mandatory Audit Check
Distinguish between:
- Liquidated statutory entitlements (e.g., failed transaction compensation of Rs 100/day under RBI TAT circular).
- Discretionary compensatory ceilings (e.g., up to Rs 30 lakh under RB-IOS 2021 or Rule 17 Insurance Ombudsman Rules).

### The Concrete Fix
Frame the claim as actual proven damages, requesting the forum to exercise its statutory discretion to award compensation up to the prescribed ceiling.

---

## Trap 5: Discretion Presented as a Right, or Right Presented as a Favour

### The Failure Mechanism
- Presenting a judicial or regulatory discretion as an absolute mandatory right.
- Presenting an absolute customer statutory right as a discretionary favour by the institution.

### Example Defects
- Asserting that "the Magistrate is bound to award 20% interim compensation under Section 143A of the Negotiable Instruments Act." (Section 143A uses the word "may" and is directory and discretionary, per Supreme Court ruling in *P. Mohanraj*).
- Describing shadow credit under RBI Circular DBR.No.Leg.BC.78/09.07.005/2017-18 Para 9 as a "goodwill gesture by the bank" when it is a mandatory regulatory obligation within 10 working days.

### Mandatory Audit Check
Inspect the operative statutory verb: "shall" (mandatory duty) versus "may" (discretionary power).

### The Concrete Fix
If discretionary, plead facts justifying the exercise of discretion. If mandatory, assert the statutory command directly without deferential phrasing.

---

## Trap 6: Document or Fact Outside the Clause's Own List

### The Failure Mechanism
Claiming that a provision applies to an item, instrument, or situation that does not appear in that clause's explicit statutory definitions.

### Example Defect
Asserting that an unauthorised debit via a cryptocurrency exchange wallet is governed by the zero-liability protections of RBI Circular DBR.No.Leg.BC.78/09.07.005/2017-18. The circular explicitly applies only to electronic banking transactions across authorised bank accounts and payment instruments.

### Mandatory Audit Check
Examine the definitions clause and scope clause of the instrument. Confirm that the specific transaction type or document is listed.

### The Concrete Fix
Verify whether the instrument covers the transaction. If unlisted, seek remedies under general contract law, consumer protection, or criminal statutes rather than misapplying sectoral circulars.

---

## Trap 7: Threshold Quoted Without Demonstration of Factual Calculation

### The Failure Mechanism
Asserting that a forum has jurisdiction or that a statutory threshold is satisfied without setting out the mathematical calculation proving compliance.

### Example Defects
- Filing an insolvency petition under Section 9 IBC without demonstrating that the operational debt exceeds the Rs 1,00,00,000 threshold (Section 4 IBC).
- Filing a consumer complaint before the State Commission claiming Rs 60,00,000 without showing how much consideration was actually paid.

### Mandatory Audit Check
Show the arithmetic:
- Consideration paid for goods/services (for Consumer Protection Act 2019 pecuniary jurisdiction).
- Total principal default amount excluding unadmitted penal interest (for IBC Section 4 threshold).

### The Concrete Fix
Provide an explicit calculation breakdown table in the draft establishing compliance with the statutory minimum or ceiling.

---

## Trap 8: Deadline Counted from the Wrong Starting Event

### The Failure Mechanism
Calculating a limitation period or notice cure period from an incorrect baseline event, or confusing calendar days with working days.

### Example Defects
- Counting the 30-day notice period under Section 138 NI Act from the date of the cheque bounce rather than the date of receipt of the bank return memo.
- Counting the 3-day notification window under RBI unauthorised transaction rules as 3 calendar days rather than 3 "working days of the bank".
- Counting the 1-month limitation period under Section 142(1)(b) NI Act from the date of notice dispatch rather than 15 days following notice receipt.

### Mandatory Audit Check
Identify:
1. The exact statutory trigger event (receipt vs dispatch vs knowledge).
2. The exact unit of measurement (calendar days, working days, months).
3. The day of exclusion (Section 12 Limitation Act 1963: the day from which period is to be reckoned shall be excluded).

### The Concrete Fix
Demonstrate the timeline step-by-step: Date of trigger event -> Day 0 -> End of cure period -> Cause of action date -> Last date of limitation.

---

## Trap 9: Simultaneous Filing Barring or Endangering Another Remedy

### The Failure Mechanism
Advising simultaneous filings across multiple forums where a filing in one forum legally excludes, bars, or prejudices remedies in another forum.

### Example Defects
- Filing an RBI Ombudsman complaint while simultaneously instituting a civil suit or consumer complaint. Under Clause 11(3)(b) of the RB-IOS 2021, the Ombudsman is mandated to reject any complaint that is pending before any court, tribunal, or arbitrator.
- Filing an Article 226 writ petition challenging SARFAESI measures without disclosing that a Section 17 DRT application has been filed or is available.

### Mandatory Audit Check
Audit whether the prospective forum contains a non-maintainability or election-of-remedies clause regarding parallel litigation.

### The Concrete Fix
Sequence remedies hierarchically:
1. Exhaust internal grievance redressal (30 days).
2. File regulatory/ombudsman complaint if eligible.
3. If rejected or involving complex disputed questions of fact, approach Consumer Commission, Commercial Court, or DRT.

---

## Trap 10: Commercial Matter Assumed to be a Consumer Dispute

### The Failure Mechanism
Filing a consumer complaint on behalf of a company, commercial trader, or business enterprise without establishing self-employment for livelihood.

### The Real Law
Section 2(7) of the Consumer Protection Act, 2019 explicitly excludes any person who buys goods or avails services for any commercial purpose. Under settled Supreme Court precedent (*Lilavati Kirtilal Mehta Medical Trust v. Unique Shanti Developers* (2020) 2 SCC 265; *Shrikant G. Mantri v. Punjab National Bank* (2022) 5 SCC 42), services availed for commercial profit cannot form the basis of a consumer complaint.

### Mandatory Audit Check
Examine the identity of the complainant:
- Individual consumer using personal account -> Consumer Commission maintainable.
- Commercial partnership, private limited company, or current account for business -> Consumer Commission non-maintainable unless exclusive self-employment for livelihood is specifically pleaded and proved.

### The Concrete Fix
Advise filing a Commercial Suit under the Commercial Courts Act 2015 or initiating arbitration/civil suit, rather than risking summary dismissal before the Consumer Commission.

---

## Trap 11: Writ Assumed to be Available Against a Private Body

### The Failure Mechanism
Advising the filing of an Article 226 writ petition before a High Court against a private bank, private insurer, or fintech company.

### The Real Law
Under the landmark Supreme Court ruling in *Federal Bank Ltd. v. Sagar Thomas* (2003) 10 SCC 733 and *St. Mary's Education Society v. Rajendra Prasad Bhargava* (2023) 4 SCC 498, a writ under Article 226 does not lie against a private entity in respect of contractual or commercial disputes, because the private entity is not discharging a public function or public duty.

### Mandatory Audit Check
Is the respondent an Article 12 State authority (e.g. State Bank of India, Life Insurance Corporation, nationalized banks) or a private entity (e.g. HDFC Bank, ICICI Bank, Axis Bank)? If private, does the challenged act relate to a statutory public duty?

### The Concrete Fix
If the entity is private and the dispute is commercial:
- Approach the RBI / IRDAI Ombudsman.
- Approach the Consumer Forum (if individual consumer).
- File a civil or commercial suit.
- Do not file an Article 226 writ petition.

---

## Trap 12: Electronic Record Claim Without Statutory Certificate Form

### The Failure Mechanism
Relying on computer printouts, emails, chat transcripts, or server logs in a formal legal complaint or court pleading without preparing the mandatory electronic evidence certificate.

### The Real Law
Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 (and previously Section 65B of the Indian Evidence Act, 1872) mandates that electronic records are admissible only when accompanied by a formal certificate satisfying the statutory criteria. The Schedule to the BSA specifies the mandatory certificate format (Part A and Part B).

### Mandatory Audit Check
Does the evidence rely on digital communications? If so, has a draft Certificate under Section 63 BSA been incorporated or scheduled?

### The Concrete Fix
Annex a draft Certificate under Section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023 identifying the device, confirming its lawful operation, and signed by the person managing the device.

---

## Trap 13: Facts Taken from Dictation, Memory, or Unverified Transcript

### The Failure Mechanism
Using transaction dates, reference IDs, monetary amounts, or party details from conversational memory or unverified summaries rather than the primary correspondence.

### Example Defect
Stating an unauthorised debit amount as Rs 45,000 based on a user message, when the bank statement shows three distinct debits of Rs 14,999, Rs 14,999, and Rs 15,000 on different dates.

### Mandatory Audit Check
Cross-check every factual token against primary documentation (bank passbook, statement of account, formal closure notice, postal tracking report).

### The Concrete Fix
Construct the Claim Inventory table with exact document citations and page numbers. Never draft an assertion that cannot be mapped to an attached document.
