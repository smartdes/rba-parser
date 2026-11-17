"""
Extracts raw transaction rows from a multi-page M-PESA PDF statement
into a structured tabular CSV format.
"""

import argparse
import os
import sys
from typing import List
import pandas as pd
import pdfplumber

COLUMNS = [
    "receipt_no",
    "completion_time",
    "details",
    "status",
    "paid_in",
    "withdrawn",
    "balance",
]


def extract_transactions(
    pdf_path: str,
    password: str = "",
    output_csv: str = "raw_statement.csv",
) -> pd.DataFrame:
    """Parses tabular statement records from the provided PDF file."""
    if not os.path.exists(pdf_path):
        print(f"Error: Statement file '{pdf_path}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting transactions from: {pdf_path}")
    extracted_rows: List[List[str]] = []

    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            total_pages = len(pdf.pages)
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables() or []
                for table in tables:
                    for row in table:
                        # Skip summary cards or malformed non-7-column tables
                        if not row or len(row) != 7:
                            continue

                        first_cell = (row[0] or "").strip()
                        # Skip repeated table headers
                        if first_cell.startswith("Receipt"):
                            continue
                        # Skip empty rows
                        if not first_cell:
                            continue

                        extracted_rows.append(row)

                print(f"Processed Page {page_num}/{total_pages} - Collected {len(extracted_rows)} rows")

    except pdfplumber.pdfminer.pdfdocument.PDFPasswordIncorrect:
        print("Error: The password provided for this PDF statement is incorrect.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error while processing PDF: {exc}", file=sys.stderr)
        sys.exit(1)

    df = pd.DataFrame(extracted_rows, columns=COLUMNS)

    # Flatten embedded line breaks within text cells
    for col in ["receipt_no", "details", "status"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("\n", " ", regex=False).str.strip()

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"\nExtraction complete: {len(df)} transactions exported to '{output_csv}'")
    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract tabular transaction data from an M-PESA statement PDF."
    )
    parser.add_argument(
        "--pdf",
        default=os.environ.get("MPESA_PDF", "MPESA_Statement.pdf"),
        help="Path to M-PESA PDF statement (default: MPESA_Statement.pdf or $MPESA_PDF)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("MPESA_PASSWORD", ""),
        help="Password to unlock the PDF statement (default: $MPESA_PASSWORD)",
    )
    parser.add_argument(
        "--output",
        default="raw_statement.csv",
        help="Destination path for raw extracted CSV (default: raw_statement.csv)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    df_result = extract_transactions(
        pdf_path=args.pdf,
        password=args.password,
        output_csv=args.output,
    )
    if not df_result.empty:
        print("\nFirst 5 transactions:")
        print(df_result.head(5).to_string())
