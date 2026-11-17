"""
Integrity verification and reconciliation utility for cleaned M-PESA statements.
Audits totals, validates mathematical consistency between running balances
and transaction amounts, and flags anomalies.
"""

import argparse
import os
import sys
from typing import Optional
import pandas as pd


def verify_statement(
    csv_path: str = "clean_statement.csv",
    expected_paid_in: Optional[float] = None,
    expected_paid_out: Optional[float] = None,
) -> bool:
    """Verifies that the transactions in the cleaned statement reconcile accurately."""
    if not os.path.exists(csv_path):
        print(f"Error: Statement file '{csv_path}' not found.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"Verifying {total_rows} transactions in: {csv_path}")

    if total_rows == 0:
        print("Warning: Dataset is empty.")
        return True

    # 1. Compute totals
    actual_paid_in = float(df["paid_in"].sum())
    actual_paid_out = float(df["withdrawn"].sum())
    net_movement = actual_paid_in - actual_paid_out

    print(f"\nTotal Paid In  : KES {actual_paid_in:,.2f}")
    if expected_paid_in is not None:
        diff_in = actual_paid_in - expected_paid_in
        status_in = "MATCH" if abs(diff_in) < 0.01 else f"MISMATCH (diff: {diff_in:+,.2f})"
        print(f"  Target Paid In: KES {expected_paid_in:,.2f} -> {status_in}")

    print(f"Total Paid Out : KES {actual_paid_out:,.2f}")
    if expected_paid_out is not None:
        diff_out = actual_paid_out - expected_paid_out
        status_out = "MATCH" if abs(diff_out) < 0.01 else f"MISMATCH (diff: {diff_out:+,.2f})"
        print(f"  Target Paid Out: KES {expected_paid_out:,.2f} -> {status_out}")

    print(f"Net Cash Flow  : KES {net_movement:,.2f}")

    # 2. Running balance change check
    # In a statement sorted newest first:
    # df.iloc[0] is the most recent transaction, df.iloc[-1] is the oldest.
    newest_balance = float(df.iloc[0]["balance"])
    oldest_balance = float(df.iloc[-1]["balance"])
    oldest_movement = float(df.iloc[-1]["paid_in"] - df.iloc[-1]["withdrawn"])
    opening_balance = oldest_balance - oldest_movement
    balance_delta = newest_balance - opening_balance

    print("\n--- Balance Audit ---")
    print(f"Calculated Opening Balance: KES {opening_balance:,.2f}")
    print(f"Closing Statement Balance : KES {newest_balance:,.2f}")
    print(f"Total Balance Change      : KES {balance_delta:,.2f}")
    print(f"Sum of Net Movements      : KES {net_movement:,.2f}")

    reconciliation_gap = round(balance_delta - net_movement, 2)
    if abs(reconciliation_gap) < 0.01:
        print("Reconciliation Status: VERIFIED (0.00 discrepancy)")
    else:
        print(f"Reconciliation Status: DISCREPANCY of KES {reconciliation_gap:,.2f}")

    # 3. Anomaly checks
    zero_movement_rows = int(((df["paid_in"] == 0) & (df["withdrawn"] == 0)).sum())
    missing_numbers = int(df["paid_in"].isna().sum() + df["withdrawn"].isna().sum())

    print("\n--- Data Health ---")
    print(f"Transactions with zero movement: {zero_movement_rows}")
    print(f"Non-numeric or null amounts    : {missing_numbers}")

    is_valid = abs(reconciliation_gap) < 0.01
    return is_valid


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify statement math integrity and reconcile totals."
    )
    parser.add_argument(
        "--input",
        default="clean_statement.csv",
        help="Path to clean statement CSV (default: clean_statement.csv)",
    )
    parser.add_argument(
        "--expected-in",
        type=float,
        default=None,
        help="Expected total paid-in from Safaricom statement summary table (optional)",
    )
    parser.add_argument(
        "--expected-out",
        type=float,
        default=None,
        help="Expected total paid-out from Safaricom statement summary table (optional)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    success = verify_statement(
        csv_path=args.input,
        expected_paid_in=args.expected_in,
        expected_paid_out=args.expected_out,
    )
    sys.exit(0 if success else 1)
