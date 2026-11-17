"""
Cleans, normalizes, and categorizes raw M-PESA statement transactions.
Converts datetimes and numeric fields, assigns granular transaction
categories, and computes financial summary breakdowns.
"""

import argparse
import os
import sys
import pandas as pd


def categorize_transaction(details: str) -> str:
    """Classifies an M-PESA transaction based on standard transaction keywords."""
    d = str(details).lower()

    if "withdrawal charge" in d:
        return "Withdrawal Charge"
    if "customer withdrawal" in d:
        return "Agent Withdrawal"
    if "agent deposit" in d or "deposit of funds" in d:
        return "Agent Deposit"
    if (
        "overdraft of credit" in d
        or "od loan repayment" in d
        or "customer transfer fuliza" in d
        or "merchant payment fuliza" in d
    ):
        return "Fuliza / Overdraft"
    if "pay bill" in d:
        return "Paybill"
    if "merchant payment" in d or "buy goods" in d:
        return "Buy Goods (Till)"
    if "airtime" in d:
        return "Airtime"
    if "customer transfer" in d:
        return "Send Money"
    if "funds received" in d or "received from" in d:
        return "Received Money"
    if "salary payment" in d:
        return "Salary"
    if "charge" in d or "fee" in d:
        return "Charges"

    return "Others"


def clean_statement(
    input_csv: str = "raw_statement.csv",
    output_csv: str = "clean_statement.csv",
) -> pd.DataFrame:
    """Reads raw extracted CSV, sanitizes amounts/dates, assigns categories, and writes clean CSV."""
    if not os.path.exists(input_csv):
        print(f"Error: Input file '{input_csv}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading raw statement from: {input_csv}")
    df = pd.read_csv(input_csv, dtype=str).fillna("")

    # 1. Parse timestamps
    df["completion_time"] = pd.to_datetime(df["completion_time"], errors="coerce")

    # 2. Normalize numeric amounts
    for col in ["paid_in", "withdrawn", "balance"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
                .replace("", "0")
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # In M-PESA statements, outgoing amounts are often listed with negative signs.
    # Convert to absolute values for simplified analysis and reporting.
    if "withdrawn" in df.columns:
        df["withdrawn"] = df["withdrawn"].abs()

    # 3. Categorize transactions
    df["category"] = df["details"].apply(categorize_transaction)

    # 4. Sort newest first
    df = df.sort_values("completion_time", ascending=False).reset_index(drop=True)

    # 5. Export cleaned dataset
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    # 6. Generate summary output
    print(f"Saved cleaned statement to: {output_csv}")
    print("\n--- Summary Statistics ---")
    print(f"Total transactions: {len(df)}")
    print(f"Unparseable dates:  {df['completion_time'].isna().sum()}")
    print(f"Date range:         {df['completion_time'].min()} to {df['completion_time'].max()}")
    print(f"Total Paid In:      KES {df['paid_in'].sum():,.2f}")
    print(f"Total Paid Out:     KES {df['withdrawn'].sum():,.2f}")
    print(f"Net Movement:       KES {(df['paid_in'].sum() - df['withdrawn'].sum()):,.2f}")

    print("\n--- Breakdown By Category ---")
    summary = (
        df.groupby("category")[["paid_in", "withdrawn"]]
        .sum()
        .round(2)
        .assign(count=df.groupby("category").size())
        .sort_values("withdrawn", ascending=False)
    )
    print(summary.to_string())

    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean, categorize, and format raw M-PESA statement transactions."
    )
    parser.add_argument(
        "--input",
        default="raw_statement.csv",
        help="Path to raw input CSV (default: raw_statement.csv)",
    )
    parser.add_argument(
        "--output",
        default="clean_statement.csv",
        help="Path to destination cleaned CSV (default: clean_statement.csv)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    clean_statement(input_csv=args.input, output_csv=args.output)
