#!/usr/bin/env python3
# ====================================================================
# GEMINI_OFFLINE_ADAPTER: Environment Detection & Offline Tests
# Executes 100% locally and offline.
# ====================================================================
"""
Automated Test Suite for Indian Legal Verification Gate
Tests trap cases and clean drafts across all 8 failure dimensions.
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from verification_gate import audit_draft_text

class TestIndianLegalVerificationGate(unittest.TestCase):

    def test_trap_1_count_mismatch(self):
        """Trap 1: Stated numeral does not match actual count of enumerated list items."""
        draft = """
The Complainant relies upon the following four documents:
1. Bank statement dated 12.09.2024.
2. Written complaint receipt dated 13.09.2024.
3. Principal Nodal Officer escalation dated 22.09.2024.
"""
        verdict, defects = audit_draft_text(draft)
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any(d["code"] == "COUNT_MISMATCH" for d in defects))

    def test_trap_2_banned_em_dash(self):
        """Trap 2: Em dash character (U+2014) is present in legal draft."""
        # Using unicode escape so the test file itself does not contain the literal character
        em_dash_char = "\u2014"
        draft = f"The bank failed to reverse the charges {em_dash_char} violating RBI Master Directions."
        verdict, defects = audit_draft_text(draft)
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any(d["code"] == "BANNED_DASH" for d in defects))

    def test_trap_3_ceiling_as_entitlement(self):
        """Trap 3: Ombudsman discretionary compensation cap presented as entitlement."""
        draft = """
Under the RBI Integrated Ombudsman Scheme 2021, the complainant is entitled to Rs 30,00,000
for consequential loss as an automatic debt due from the bank.
"""
        verdict, defects = audit_draft_text(draft)
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any(d["code"] == "CEILING_AS_ENTITLEMENT" for d in defects))

    def test_trap_4_discretion_as_right(self):
        """Trap 4: Discretionary Section 143A NI Act relief presented as mandatory court duty."""
        draft = """
The learned Trial Court is bound to award interim compensation under Section 143A of the Negotiable Instruments Act.
"""
        verdict, defects = audit_draft_text(draft)
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any(d["code"] == "DISCRETION_AS_RIGHT" for d in defects))

    def test_trap_5_tracking_link(self):
        """Trap 5: Hyperlink contains marketing tracking parameters."""
        draft = """
Please refer to the [RBI Circular](https://www.rbi.org.in/scripts/BS_CircularIndexDisplay.aspx?Id=11040&utm_source=legal_campaign&utm_medium=email) (https://www.rbi.org.in/scripts/BS_CircularIndexDisplay.aspx?Id=11040).
"""
        verdict, defects = audit_draft_text(draft)
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any(d["code"] == "TRACKING_LINK" for d in defects))

    def test_trap_6_vague_citation(self):
        """Trap 6: Vague attribution 'as per law' without instrument number or section."""
        draft = """
The opposite party is liable to pay interest on the delayed refund as per law within 15 days.
"""
        verdict, defects = audit_draft_text(draft)
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any(d["code"] == "VAGUE_CITATION" for d in defects))

    def test_trap_7_hidden_url_target(self):
        """Trap 7: Hyperlink hides URL destination behind anchor text."""
        draft = """
Access the statutory portal at [eCourts Portal](https://services.ecourts.gov.in/).
"""
        verdict, defects = audit_draft_text(draft)
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any(d["code"] == "HIDDEN_URL" for d in defects))

    def test_trap_8_footer_pii(self):
        """Trap 8: Unmasked PAN detected in footer section."""
        lines = ["Statement of legal grounds and relief sought."] * 10
        lines.append("Complainant PAN: ABCDE1234F")
        lines.append("Date: 01.11.2024")
        draft = "\n".join(lines)
        verdict, defects = audit_draft_text(draft)
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any(d["code"] == "FOOTER_PII" for d in defects))

    def test_clean_draft_pass(self):
        """Clean Draft: Fully verified draft with clean URLs, exact counts, and valid citations."""
        draft = """
LEGAL NOTICE DEMANDING STATUTORY SHADOW REVERSAL

To,
The Branch Manager,
HDFC Bank Limited,
Fort Branch, Mumbai, Maharashtra 400001.

Subject: Formal demand for shadow credit reversal under RBI Circular DBR.No.Leg.BC.78/09.07.005/2017-18 dated July 6, 2017.

Sir,

Under instructions from my client, I hereby place the following three facts on record:
1. On 12.09.2024 at 14:22 IST, an unauthorised electronic transaction of Rs 10,000 occurred on Account No. ending in 4921.
2. On 13.09.2024 at 09:15 IST, within three working days, my client notified the bank via formal dispute reference #492810.
3. Under Paragraph 6(b) and Paragraph 9 of RBI Circular DBR.No.Leg.BC.78/09.07.005/2017-18, the bank is mandated to provide shadow credit reversal within 10 working days of customer notification.

The official directive can be verified at [Reserve Bank of India](https://www.rbi.org.in/) (https://www.rbi.org.in/).

Please credit the amount within 7 days of receipt of this notice, failing which my client shall proceed before the Banking Ombudsman under Clause 11 of the Reserve Bank of India - Integrated Ombudsman Scheme, 2021.

Advocate for the Complainant
Mumbai, Maharashtra.
"""
        verdict, defects = audit_draft_text(draft)
        self.assertEqual(verdict, "PASS")
        self.assertEqual(len(defects), 0)

if __name__ == "__main__":
    unittest.main()
