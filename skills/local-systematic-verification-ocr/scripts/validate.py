#!/usr/bin/env python3
"""
scripts/validate.py - Mechanical format validator for local-systematic-verification-ocr.

Enforces zero-network, zero-LLM deterministic checks:
1. Balanced $...$ and $$...$$ LaTeX math delimiters.
2. Balanced curly braces {...} within math regions.
3. Consistent table column counts per table block.
4. Sequential question numbering when **Q<number>. headings are present.
5. Detection of unauthorized ASCII-art diagrams or box-drawing lines.

Exit Codes:
  0: PASS (All mechanical checks green)
  1: REVIEW (Non-critical format warnings, sequence anomalies, or suspicious ASCII art)
  2: BLOCK (Syntax defects: unbalanced delimiters, mismatched table columns, broken braces)
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple


class ValidationResult:
    def __init__(self):
        self.block_flags: List[Dict[str, Any]] = []
        self.review_flags: List[Dict[str, Any]] = []
        self.info_messages: List[str] = []

    def block(self, line_no: int, message: str, context: str = ""):
        self.block_flags.append({"line": line_no, "message": message, "context": context})

    def review(self, line_no: int, message: str, context: str = ""):
        self.review_flags.append({"line": line_no, "message": message, "context": context})

    def info(self, message: str):
        self.info_messages.append(message)

    @property
    def verdict(self) -> str:
        if self.block_flags:
            return "BLOCK"
        elif self.review_flags:
            return "REVIEW"
        return "PASS"

    @property
    def exit_code(self) -> int:
        if self.block_flags:
            return 2
        elif self.review_flags:
            return 1
        return 0


def strip_escaped_dollars(text: str) -> str:
    """Replace literal \\$ with temporary placeholder to avoid false delimiter triggers."""
    return re.sub(r'(?<!\\)\\(\$)', '\x00DOLLAR\x00', text)


def validate_math_delimiters_and_braces(content: str, result: ValidationResult):
    """
    Validates balanced $$ and $ delimiters across the document and verifies
    that curly braces within each delimited math environment are balanced.
    """
    lines = content.splitlines()

    # Track multi-line display math blocks ($$)
    in_display_math = False
    display_math_start_line = 0
    display_math_buffer = []

    for idx, line in enumerate(lines, start=1):
        clean_line = strip_escaped_dollars(line)
        
        # Check $$ occurrences
        parts = clean_line.split("$$")
        num_double_dollars = len(parts) - 1

        if num_double_dollars > 0:
            for _ in range(num_double_dollars):
                if not in_display_math:
                    in_display_math = True
                    display_math_start_line = idx
                    display_math_buffer = []
                else:
                    in_display_math = False
                    # Check balanced braces in display math block
                    block_text = "\n".join(display_math_buffer)
                    check_balanced_braces(block_text, display_math_start_line, "$$", result)
                    display_math_buffer = []

        if in_display_math:
            display_math_buffer.append(line)
            continue

        # In non-display math lines, validate inline math ($)
        # Avoid checking lines inside code blocks (```)
        if line.strip().startswith("```"):
            continue

        # Find all single dollars not part of $$
        # Replace $$ first
        no_double = clean_line.replace("$$", "  ")
        single_dollar_positions = [m.start() for m in re.finditer(r'(?<!\$)\$(?!\$)', no_double)]

        if len(single_dollar_positions) % 2 != 0:
            result.block(
                idx,
                f"Unbalanced inline math delimiter ($): found {len(single_dollar_positions)} unescaped '$' characters on line",
                line.strip()
            )
        else:
            # Check balanced braces inside each inline math pair
            for i in range(0, len(single_dollar_positions), 2):
                start_pos = single_dollar_positions[i] + 1
                end_pos = single_dollar_positions[i + 1]
                inline_math = no_double[start_pos:end_pos]
                check_balanced_braces(inline_math, idx, "$", result)

    if in_display_math:
        result.block(
            display_math_start_line,
            "Unclosed display math environment ($$): reached end of document without closing $$",
            ""
        )


def check_balanced_braces(math_text: str, line_no: int, env_type: str, result: ValidationResult):
    """Verifies that curly braces { } inside LaTeX math regions are strictly balanced."""
    open_count = 0
    escaped = False
    for char in math_text:
        if escaped:
            escaped = False
            continue
        if char == '\\':
            escaped = True
            continue
        if char == '{':
            open_count += 1
        elif char == '}':
            open_count -= 1
            if open_count < 0:
                result.block(
                    line_no,
                    f"Unexpected closing brace '}}' in {env_type} math environment",
                    math_text.strip()[:80]
                )
                return

    if open_count > 0:
        result.block(
            line_no,
            f"Unclosed opening brace '{{' ({open_count} missing '}}') in {env_type} math environment",
            math_text.strip()[:80]
        )


def validate_tables(content: str, result: ValidationResult):
    """
    Validates that every Markdown table block has consistent column counts across all rows.
    """
    lines = content.splitlines()
    in_table = False
    table_start_line = 0
    expected_cols = 0
    current_table_lines = []

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        is_table_row = stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 1

        if is_table_row:
            if not in_table:
                in_table = True
                table_start_line = idx
                current_table_lines = []
                # Count columns by splitting on pipe and stripping outer empty entries
                raw_cells = [c.strip() for c in stripped.split("|")[1:-1]]
                expected_cols = len(raw_cells)
                current_table_lines.append((idx, stripped, expected_cols))
            else:
                # Check if it is a separator line (|---|---|)
                is_separator = re.match(r'^\|(?:\s*:?-+:?\s*\|)+$', stripped)
                raw_cells = [c.strip() for c in stripped.split("|")[1:-1]]
                actual_cols = len(raw_cells)
                if not is_separator:
                    if actual_cols != expected_cols:
                        result.block(
                            idx,
                            f"Table column mismatch: expected {expected_cols} columns (from header at line {table_start_line}), but line has {actual_cols} columns",
                            stripped
                        )
                current_table_lines.append((idx, stripped, actual_cols))
        else:
            if in_table:
                in_table = False
                expected_cols = 0

    if in_table and expected_cols > 0:
        result.info(f"Verified table ending at EOF (started line {table_start_line})")


def validate_question_sequence(content: str, result: ValidationResult):
    """
    Verifies that question numbers formatted as **Q<number>. are strictly sequential without gaps or regressions.
    """
    pattern = re.compile(r'\*\*Q(\d+)\.')
    found_questions: List[Tuple[int, int]] = []

    for idx, line in enumerate(content.splitlines(), start=1):
        match = pattern.search(line)
        if match:
            q_num = int(match.group(1))
            found_questions.append((idx, q_num))

    if not found_questions:
        result.info("No **Q<number>. headings found (question sequence check skipped)")
        return

    result.info(f"Detected {len(found_questions)} numbered question headings (**Q{found_questions[0][1]}. through **Q{found_questions[-1][1]}.)")

    expected_q = found_questions[0][1]
    for line_no, q_num in found_questions:
        if q_num != expected_q:
            result.review(
                line_no,
                f"Question sequence anomaly: expected Q{expected_q}, found Q{q_num}",
                f"**Q{q_num}."
            )
            expected_q = q_num + 1
        else:
            expected_q += 1


def validate_ascii_art(content: str, result: ValidationResult):
    """
    Detects potential ASCII-art diagrams, drawings, or pseudo-graphic sequences that violate the verbal description contract.
    """
    lines = content.splitlines()
    in_code_block = False

    ascii_patterns = [
        re.compile(r'(\+[-=]{3,}\+)|(\| {3,}\|)'),       # Box drawing lines
        re.compile(r'[\\/]{2,}|[|]{3,}'),                 # Diagonal / vertical line clusters
        re.compile(r'(\/\\[_ ]+\\\/)'),                  # Geometric ASCII shapes
        re.compile(r'(<---[-=]+>)|(=====>)'),             # Excessive arrow drawings
        re.compile(r'[\+\|]{2,}[-=\s]{2,}[\+\|]{2,}')     # Grid frames
    ]

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Exclude Markdown table rows
        if stripped.startswith("|") and stripped.endswith("|"):
            continue

        # Exclude horizontal rules
        if stripped in ("---", "***", "___", "- - -", "* * *"):
            continue

        for pat in ascii_patterns:
            if pat.search(stripped):
                result.review(
                    idx,
                    "Possible ASCII-art diagram detected. Per Level 7 and Output Contract, diagrams must be preserved as images with captions and described in words, never drawn as ASCII art.",
                    stripped[:80]
                )
                break


def validate_document(filepath: Path) -> ValidationResult:
    result = ValidationResult()
    if not filepath.exists():
        result.block(0, f"File does not exist: {filepath}")
        return result

    content = filepath.read_text(encoding="utf-8", errors="replace")
    
    result.info(f"Validating: {filepath.name} ({len(content)} characters, {len(content.splitlines())} lines)")
    validate_math_delimiters_and_braces(content, result)
    validate_tables(content, result)
    validate_question_sequence(content, result)
    validate_ascii_art(content, result)

    return result


def print_report(filepath: Path, result: ValidationResult):
    print("=" * 70)
    print("  LOCAL-SYSTEMATIC-VERIFICATION-OCR: FORMAT VALIDATION REPORT")
    print("=" * 70)
    print(f"Target File: {filepath}")
    print(f"Overall Verdict: {result.verdict}")
    print(f"Exit Code: {result.exit_code}")
    print("-" * 70)

    if result.info_messages:
        print("[INFO / TELEMETRY]")
        for msg in result.info_messages:
            print(f"  * {msg}")
        print()

    if result.block_flags:
        print(f"[BLOCK FLAGS: {len(result.block_flags)} CRITICAL ISSUE(S)]")
        for flag in result.block_flags:
            print(f"  Line {flag['line']}: {flag['message']}")
            if flag['context']:
                print(f"    Context: {flag['context']}")
        print()

    if result.review_flags:
        print(f"[REVIEW FLAGS: {len(result.review_flags)} WARNING(S)]")
        for flag in result.review_flags:
            print(f"  Line {flag['line']}: {flag['message']}")
            if flag['context']:
                print(f"    Context: {flag['context']}")
        print()

    if result.verdict == "PASS":
        print("[SUCCESS] All format criteria strictly satisfied. No syntax defects detected.")
    elif result.verdict == "REVIEW":
        print("[ACTION REQUIRED] Review flags present. Visually confirm source crop before proceeding.")
    else:
        print("[CRITICAL] Blocking syntax defects found. Must be resolved before shipping.")
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate.py <path_to_markdown_file>")
        sys.exit(2)

    target_path = Path(sys.argv[1])
    result = validate_document(target_path)
    print_report(target_path, result)
    sys.exit(result.exit_code)


if __name__ == "__main__":
    main()
