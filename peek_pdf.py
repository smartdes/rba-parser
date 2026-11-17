"""
Utility script to quickly inspect the table layout and structure
of an M-PESA PDF statement before full extraction.
"""

import argparse
import os
import sys
import pdfplumber


def inspect_statement(pdf_path: str, password: str = "", max_preview_rows: int = 6) -> None:
    """Inspects the first page of the PDF statement and prints table previews."""
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'", file=sys.stderr)
        sys.exit(1)

    print(f"Opening statement: {pdf_path}")
    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages: {total_pages}")

            if total_pages == 0:
                print("Warning: PDF contains no pages.")
                return

            first_page = pdf.pages[0]
            tables = first_page.extract_tables()
            print(f"Tables detected on page 1: {len(tables)}")

            for idx, table in enumerate(tables):
                print(f"\n--- Table {idx}: {len(table)} rows ---")
                for row in table[:max_preview_rows]:
                    print(row)

    except pdfplumber.pdfminer.pdfdocument.PDFPasswordIncorrect:
        print("Error: The password supplied for this PDF is incorrect.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error reading PDF: {exc}", file=sys.stderr)
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect the layout and tables of an M-PESA PDF statement."
    )
    parser.add_argument(
        "--pdf",
        default=os.environ.get("MPESA_PDF", "MPESA_Statement.pdf"),
        help="Path to the M-PESA PDF statement (default: MPESA_Statement.pdf or $MPESA_PDF)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("MPESA_PASSWORD", ""),
        help="Password to unlock the PDF statement (default: $MPESA_PASSWORD)",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=6,
        help="Number of preview rows to display per table (default: 6)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    inspect_statement(pdf_path=args.pdf, password=args.password, max_preview_rows=args.rows)
