💰 Transaction Manager
A simple, interactive Streamlit application to track, manage, and view your personal financial transactions. It uses SQLite for persistent storage and supports credit/debit entries, balance calculations, and CSV export of transaction history.
🚀 Features
💸 Add Transactions: Log credits or debits with descriptions and dates.
📈 Running Balance: Automatically calculates your running balance after each transaction.
📜 Transaction History: View all past transactions in a formatted table.
📥 Export to CSV: Download your transaction history as a CSV file.
🗃️ SQLite Backend: Lightweight local database to store transactions.

/n
📦 Installation
Clone the repository:
git clone https://github.com/r3frf/APPWRK-IT-SOLUTIONS-Private-Ltd
cd transaction-manager
/\n
Create a virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
/\n
Install dependencies:
pip install Sqlite
pip install streamlit
▶️ Running the App
streamlit run main.py
The app will open in your default browser. If not, visit the URL provided in the terminal (usually http://localhost:8501).
/\n
🧾 File Structure
 /\n
├── app.py             # Main Streamlit app file
├── transactions.db    # SQLite database (created automatically)
└── README.md          # This file
