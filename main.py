"""
Main pipeline runner for M-PESA Statement Parser.
Executes the full pipeline:
  1. PDF Table Extraction (extract_statement.py)
  2. Data Cleaning & Categorization (clean_statement.py)
  3. Mathematical Reconciliation (check_totals.py)
"""

import argparse
import os
import sys

from extract_statement import extract_transactions
from clean_statement import clean_statement
from check_totals import verify_statement


def run_pipeline(
    pdf_path: str,
    password: str = "",
    raw_csv: str = "raw_statement.csv",
    clean_csv: str = "clean_statement.csv",
    expected_in: float = None,
    expected_out: float = None,
) -> None:
    """Executes the extraction, cleaning, and reconciliation steps."""
    print("=" * 70)
    print("M-PESA STATEMENT PARSER & FINANCIAL CATEGORIZER")
    print("=" * 70)

    # Step 1: Extraction
    print("\n[STEP 1/3] Extracting transactions from PDF...")
    extract_transactions(pdf_path=pdf_path, password=password, output_csv=raw_csv)

    # Step 2: Cleaning and Categorization
    print("\n[STEP 2/3] Cleaning and categorizing transactions...")
    clean_statement(input_csv=raw_csv, output_csv=clean_csv)

    # Step 3: Reconciliation and Verification
    print("\n[STEP 3/3] Auditing balances and reconciling totals...")
    reconciled = verify_statement(
        csv_path=clean_csv,
        expected_paid_in=expected_in,
        expected_paid_out=expected_out,
    )

    print("\n" + "=" * 70)
    if reconciled:
        print("PIPELINE COMPLETED SUCCESSFULLY: All balances reconciled.")
    else:
        print("PIPELINE FINISHED WITH NOTICES: Review discrepancies above.")
    print("=" * 70)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="End-to-end M-PESA PDF statement parsing and categorization pipeline."
    )
    parser.add_argument(
        "--pdf",
        default=os.environ.get("MPESA_PDF", "MPESA_Statement.pdf"),
        help="Path to M-PESA PDF statement (default: MPESA_Statement.pdf or $MPESA_PDF)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("MPESA_PASSWORD", ""),
        help="PDF statement unlock password (default: $MPESA_PASSWORD)",
    )
    parser.add_argument(
        "--raw-output",
        default="raw_statement.csv",
        help="Path for raw extracted CSV (default: raw_statement.csv)",
    )
    parser.add_argument(
        "--clean-output",
        default="clean_statement.csv",
        help="Path for cleaned output CSV (default: clean_statement.csv)",
    )
    parser.add_argument(
        "--expected-in",
        type=float,
        default=None,
        help="Target total paid in from statement summary (optional)",
    )
    parser.add_argument(
        "--expected-out",
        type=float,
        default=None,
        help="Target total paid out from statement summary (optional)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        pdf_path=args.pdf,
        password=args.password,
        raw_csv=args.raw_output,
        clean_csv=args.clean_output,
        expected_in=args.expected_in,
        expected_out=args.expected_out,
    )
