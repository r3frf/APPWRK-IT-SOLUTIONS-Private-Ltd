import streamlit as st
import sqlite3
from datetime import datetime
import os
from datetime import datetime

# Get today's date in YYYY-MM-DD format
today_date = datetime.today().strftime('%Y-%m-%d')

# Set page configuration
st.set_page_config(
    page_title="Transaction Manager",
    page_icon="💰",
    layout="centered"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    
    # Create transactions table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            amount REAL,
            type TEXT,
            running_balance REAL
        )
    ''')
    
    # Check if we need to add initial transactions
    c.execute("SELECT COUNT(*) FROM transactions")
    if c.fetchone()[0] == 0:
        # Add initial credit of 5000
        c.execute('''
            INSERT INTO transactions (date, description, amount, type, running_balance)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime('%Y-%m-%d'), 'Initial deposit', 5000.00, 'Credit', 5000.00))
        
        # Add debit of 500
        c.execute('''
            INSERT INTO transactions (date, description, amount, type, running_balance)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime('%Y-%m-%d'), 'First expense', -500.00, 'Debit', 4500.00))
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Calculate current balance
def get_current_balance():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    # Get the latest balance based on date order, not ID order
    c.execute("SELECT running_balance FROM transactions ORDER BY date DESC, id DESC LIMIT 1")
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return 0.0

# Get all transactions from database
def get_all_transactions():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    # Order by date in descending order, then by ID in descending order (for transactions on the same date)
    c.execute("SELECT id, date, description, amount, type, running_balance FROM transactions ORDER BY date DESC, id DESC")
    transactions = c.fetchall()
    conn.close()
    return transactions

# Function to add a new transaction
def add_transaction(date, description, amount, transaction_type):
    # For debit transactions, make the amount negative
    if transaction_type == "Debit":
        amount = -abs(amount)
    else:  # Credit transactions are positive
        amount = abs(amount)
    
    # Get current date for sorting
    transaction_date = date
    
    # Calculate new running balance
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    
    # Get the current balance by sorting all transactions by date and ID
    c.execute("SELECT running_balance FROM transactions ORDER BY date DESC, id DESC LIMIT 1")
    result = c.fetchone()
    current_balance = result[0] if result else 0.0
    
    # Calculate new balance
    new_balance = current_balance + amount
    
    # Insert new transaction
    c.execute('''
        INSERT INTO transactions (date, description, amount, type, running_balance)
        VALUES (?, ?, ?, ?, ?)
    ''', (transaction_date, description, amount, transaction_type, new_balance))
    
    # Update running balances for all transactions
    # This is required because inserting a transaction with an earlier date
    # affects the running balances of all subsequent transactions
    
    # First, get all transactions ordered by date and ID
    c.execute("SELECT id, date, amount FROM transactions ORDER BY date ASC, id ASC")
    all_transactions = c.fetchall()
    
    # Recalculate running balances
    running_balance = 0.0
    for tx_id, tx_date, tx_amount in all_transactions:
        running_balance += tx_amount
        c.execute("UPDATE transactions SET running_balance = ? WHERE id = ?", (running_balance, tx_id))
    
    conn.commit()
    conn.close()
    return True

# Format transaction data for display in a table
def format_transactions_for_table(transactions):
    # Convert to format suitable for st.table
    formatted_data = []
    for tx in transactions:
        id_val, date, desc, amount, tx_type, running_bal = tx
        
        # Format amount with $ and handle negative values for display
        formatted_amount = f"${abs(amount):.2f}"
        
        # Determine transaction type based on amount
        display_type = "Credit" if amount >= 0 else "Debit"
        
        # Format running balance
        formatted_balance = f"${running_bal:.2f}"
        
        formatted_data.append({
            "Date": date,
            "Description": desc,
            "Amount": formatted_amount,
            "Type": display_type,
            "Running Balance": formatted_balance
        })
    
    return formatted_data

# Export transactions to CSV
def export_transactions_to_csv():
    transactions = get_all_transactions()
    formatted_data = format_transactions_for_table(transactions)
    
    # Create CSV content - header row first
    csv_content = "Date,Description,Amount,Type,Running Balance\n"
    
    # Add data rows - newest transactions are already at the top from get_all_transactions()
    for tx in formatted_data:
        csv_content += f"{tx['Date']},{tx['Description']},{tx['Amount']},{tx['Type']},{tx['Running Balance']}\n"
    
    return csv_content

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Function for navigation
def navigate_to(page):
    st.session_state.page = page

# Home page
def home_page():
    st.title("Transaction Manager")
    
    # Display current balance
    current_balance = get_current_balance()
    st.metric("Current Balance", f"${current_balance:.2f}")
    
    # Navigation button to add transaction page
    st.button("Add Transaction", on_click=navigate_to, args=('add_transaction',), 
              type="primary", use_container_width=True)
    
    # Navigation button to view history page
    st.button("View Transaction History", on_click=navigate_to, args=('view_history',), 
              use_container_width=True)

# Add transaction page
def add_transaction_page():
    st.title("Add New Transaction")
    
    # Form for adding a new transaction
    with st.form("transaction_form"):
        transaction_type = st.selectbox("Transaction Type", 
                               ["Credit", "Debit"])
        date = st.date_input("Date", datetime.now())
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
        
        
        # Form submission
        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            if add_transaction(date.strftime('%Y-%m-%d'), description, amount, transaction_type):
                st.success("Transaction added successfully!")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        st.button("Back to Home", on_click=navigate_to, args=('home',), use_container_width=True)
    with col2:
        st.button("View History", on_click=navigate_to, args=('view_history',), use_container_width=True)

# View transaction history page
def view_history_page():
    st.title("Transaction History")
    
    # Get transactions from database
    transactions = get_all_transactions()
    
    if transactions:
        # Format transactions for display
        formatted_data = format_transactions_for_table(transactions)
        
        # Display as a table - transactions are already in newest-first order
        st.table(formatted_data)
        
        # Add download button for CSV export
        csv_data = export_transactions_to_csv()
        st.download_button(
            label="Download Transaction History",
            data=csv_data,
            file_name="transaction_history.csv",
            mime="text/csv",
        )
    else:
        st.info("No transactions yet.")
    
    # Back button
    st.button("Back to Home", on_click=navigate_to, args=('home',))

# Main app logic - determine which page to show
if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'add_transaction':
    add_transaction_page()
elif st.session_state.page == 'view_history':
    view_history_page()

# Footer
st.markdown("---")
st.caption("Transaction Manager App © 2025")