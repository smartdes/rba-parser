# M-PESA Statement Parser & Financial Categorizer

A Python utility designed to parse, clean, categorize, and reconcile financial transactions from official Safaricom M-PESA PDF statements into structured tabular datasets (CSV).

---

## Overview

M-PESA statement PDFs provided by Safaricom contain multi-page tables, embedded line breaks, and password protection (typically using the user's National ID or Passport Number). Analyzing these transactions in spreadsheets or personal finance applications requires reliable extraction and data normalization.

This project automates:
1. **Password-protected PDF parsing**: Handles multi-page statements and suppresses redundant page headers.
2. **Data sanitization**: Flattens nested cell line breaks, converts timestamps to standard datetimes, and normalizes currency values.
3. **Transaction categorization**: Employs keyword-based rule classification tailored to Kenyan mobile money workflows (Paybill, Till/Buy Goods, Fuliza / Overdraft, Send/Receive Money, Airtime, and Agent operations).
4. **Financial reconciliation**: Mathematically audits running balances and net cash flows against statement totals.

---

## Features

- **Multi-page Table Extraction**: Leverages `pdfplumber` to accurately capture statement tables across multiple pages while ignoring summary metadata headers.
- **Rule-Based Categorization**:
  - `Paybill`: Merchant utility and bill payments.
  - `Buy Goods (Till)`: Retail and Point-of-Sale merchant payments.
  - `Fuliza / Overdraft`: Overdraft credit facilities and automatic repayments.
  - `Send Money`: Peer-to-peer customer transfers.
  - `Received Money`: Incoming peer transfers and remittances.
  - `Airtime`: Mobile airtime top-ups.
  - `Agent Deposit / Withdrawal`: Cash handling via authorized M-PESA agents.
  - `Charges`: Safaricom transaction fees and withdrawal excise tariffs.
  - `Salary`: Incoming payroll distributions.
- **Mathematical Integrity Audit**: Computes total deposits, withdrawals, net movements, and verifies opening vs. closing balance delta.
- **Zero Data Leakage by Design**: Pre-configured `.gitignore` prevents sensitive financial records (`.pdf`, `.csv`, `.xlsx`) and environment variables (`.env`) from being committed to Git.

---

## Project Structure

```text
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules for financial data and virtualenvs
├── README.md             # Project documentation and usage guide
├── requirements.txt      # Python package dependencies
├── peek_pdf.py           # Quick layout inspector for statement pages
├── extract_statement.py  # PDF table extraction pipeline
├── clean_statement.py    # Data cleaning and categorization module
├── check_totals.py       # Balance reconciliation and integrity verification
└── main.py               # Unified end-to-end pipeline runner
```

---

## Prerequisites & Installation

### 1. Requirements
- Python 3.9+
- A valid M-PESA PDF statement from Safaricom

### 2. Clone Repository & Create Virtual Environment

```bash
git clone https://github.com/<your-username>/mpesa-statement-parser.git
cd mpesa-statement-parser

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (cmd/PowerShell):
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Set up environment variables or pass flags via the command line.

### Option A: Using `.env` file
Copy the sample configuration file and populate your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
MPESA_PDF=MPESA_Statement.pdf
MPESA_PASSWORD=your_id_number_here
```

### Option B: Command Line Arguments
All scripts support direct CLI parameters (e.g., `--pdf path/to/file.pdf --password your_password`).

---

## Usage

### 1. End-to-End Pipeline (Recommended)
Run the entire extraction, cleaning, and reconciliation process in a single command:

```bash
python main.py
```

With custom flags:
```bash
python main.py --pdf "statements/June2024.pdf" --password "12345678" --expected-in 50000.00 --expected-out 42000.00
```

---

### 2. Individual Script Execution

#### Step A: Inspect Statement Tables
Preview the first page structure before performing full extraction:
```bash
python peek_pdf.py --pdf MPESA_Statement.pdf
```

#### Step B: Extract Raw Transactions
Extract tabular transactions from the PDF into a raw CSV:
```bash
python extract_statement.py --pdf MPESA_Statement.pdf --output raw_statement.csv
```

#### Step C: Clean and Categorize
Sanitize timestamps, numerical fields, and assign transaction categories:
```bash
python clean_statement.py --input raw_statement.csv --output clean_statement.csv
```

#### Step D: Verify Totals and Balances
Audit mathematical consistency between sequential balances and amounts:
```bash
python check_totals.py --input clean_statement.csv
```

---

## Privacy & Security

> **IMPORTANT**: M-PESA statements contain Personally Identifiable Information (PII) including full legal names, phone numbers, account balances, and transaction counterparts.
>
> - Never commit your `.pdf` statement files or generated `.csv` files to version control.
> - The included `.gitignore` file automatically excludes `*.pdf`, `*.csv`, `*.xlsx`, and `.env` files.
> - Keep your repository clean and share only source code.

---

## License

This project is licensed under the MIT License - see standard open-source terms.
