# PennyWise – Personal Finance Assistant (Ayush Chauhan, 2025kuad3036)

PennyWise is a beginner-friendly personal finance assistant built with Python, Streamlit and Pandas.

## Features
- Record income and expenses.
- Choose categories for transactions.
- View total income, expenses, balance and savings rate.
- View spending charts.
- Ask PennyWise questions about income, expenses, balance, savings and budget using simple keyword-based responses.
- Browse and delete transactions.
- Set a monthly budget and track spending.
- Store transaction data locally in `transactions.csv`.

## Requirements
- Python 3.9 or newer
- Internet connection for the initial package installation

## Run on Windows

1. Download or clone this repository.
2. Open the project folder.
3. Open Command Prompt or PowerShell in that folder.
4. Install the required packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Start the application:

   ```bash
   python -m streamlit run app.py
   ```

6. Streamlit will open the app in your browser. If it does not, open the local URL printed in the terminal (usually http://localhost:8501).

## Data storage
Transactions are saved in `transactions.csv` in the project folder. Keep this file if you want to preserve your entries. Do not upload personal financial data to a public GitHub repository.

## Technologies
- Python
- Streamlit
- Pandas
- CSV file storage

## Academic note
This is an educational mini-project demonstrating a rule-based, interactive personal finance assistant. It is not connected to bank accounts and does not provide professional financial advice.
