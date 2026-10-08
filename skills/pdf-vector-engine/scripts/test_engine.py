#!/usr/bin/env python3
"""
Test Suite for PDF Vector Engine
Executes unit and integration tests across stream quantization,
calibration, merging, and Ralph verification.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import pikepdf
except ImportError:
    pikepdf = None

from compress import quantize_token, compress_vector_stream, process_single_pdf
from calibrate import calibrate_file
from merge import merge_pdfs
from verify import verify_file


MINIMAL_PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
    b"4 0 obj\n<< /Length 21 >>\nstream\n10 10 m 100 100 l S\nendstream\nendobj\n"
    b"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n"
    b"0000000117 00000 n \n0000000204 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\n"
    b"startxref\n275\n%%EOF\n"
)


class TestPDFVectorEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_quantize_token(self):
        # r2dec: 2 decimals (0.01 pt)
        self.assertEqual(quantize_token("44.490002", "r2dec"), "44.49")
        self.assertEqual(quantize_token("100.000000", "r2dec"), "100")
        self.assertEqual(quantize_token("0.254123", "r2dec"), "0.25")

        # r025: 0.25 pt
        self.assertEqual(quantize_token("10.120000", "r025"), "10")
        self.assertEqual(quantize_token("10.260000", "r025"), "10.25")
        self.assertEqual(quantize_token("10.740000", "r025"), "10.75")

        # r05: 0.5 pt
        self.assertEqual(quantize_token("10.490000", "r05"), "10.5")
        self.assertEqual(quantize_token("10.200000", "r05"), "10")

    def test_02_compress_vector_stream(self):
        raw_stream = (
            b"44.490002 100.760002 m\n"
            b"44.529999 100.820000 44.580002 100.870003 44.639999 100.910004 c\n"
            b"h\n"
            b"f\n"
        )
        compressed = compress_vector_stream(raw_stream, mode="r2dec")
        self.assertIn(b"44.49 100.76 m", compressed)
        self.assertIn(b"44.53 100.82", compressed)
        self.assertLess(len(compressed), len(raw_stream))

    def test_03_create_and_calibrate_pdf(self):
        test_pdf_path = self.work_dir / "test_doc.pdf"
        if pikepdf is not None:
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page(page_size=(595.28, 841.89))
            page["/Contents"] = pikepdf.Stream(pdf, b"10 10 m 100 100 l S\n")
            pdf.save(test_pdf_path)
        else:
            with open(test_pdf_path, "wb") as f:
                f.write(MINIMAL_PDF_BYTES)

        orig_size = os.path.getsize(test_pdf_path)
        self.assertGreater(orig_size, 0)

        # Calibrate to exact byte window [10000, 20000]
        calibrated_pdf_path = self.work_dir / "calibrated.pdf"
        ok = calibrate_file(test_pdf_path, calibrated_pdf_path, min_bytes=10000, max_bytes=20000)
        self.assertTrue(ok)
        new_size = os.path.getsize(calibrated_pdf_path)
        self.assertTrue(10000 <= new_size <= 20000)

        if pikepdf is not None:
            with pikepdf.Pdf.open(calibrated_pdf_path) as p:
                self.assertEqual(len(p.pages), 1)

    def test_04_merge_pdfs(self):
        if pikepdf is None:
            self.skipTest("pikepdf not installed in environment")

        # Create 2 test PDFs
        pdf1_path = self.work_dir / "doc1.pdf"
        pdf2_path = self.work_dir / "doc2.pdf"

        p1 = pikepdf.Pdf.new()
        p1.add_blank_page()
        p1.save(pdf1_path)

        p2 = pikepdf.Pdf.new()
        p2.add_blank_page()
        p2.add_blank_page()
        p2.save(pdf2_path)

        merged_path = self.work_dir / "merged.pdf"
        ok = merge_pdfs([pdf1_path, pdf2_path], merged_path, optimize=True)
        self.assertTrue(ok)

        with pikepdf.Pdf.open(merged_path) as mp:
            self.assertEqual(len(mp.pages), 3)

    def test_05_ralph_verification_loop(self):
        pdf_path = self.work_dir / "doc_verify.pdf"
        if pikepdf is not None:
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            page["/Contents"] = pikepdf.Stream(pdf, b"0 0 100 100 re f\n")
            pdf.save(pdf_path)
        else:
            with open(pdf_path, "wb") as f:
                f.write(MINIMAL_PDF_BYTES)

        calibrated_path = self.work_dir / "doc_verify_calib.pdf"
        calibrate_file(pdf_path, calibrated_path, min_bytes=5000, max_bytes=10000)

        ok = verify_file(pdf_path, calibrated_path, min_bytes=5000, max_bytes=10000)
        self.assertTrue(ok)


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPDFVectorEngine)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
