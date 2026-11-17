import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, datetime
import uuid

# -------------------- APP CONFIGURATION --------------------
st.set_page_config(
    page_title="PennyWise - Personal Finance Assistant",
    page_icon="💰",
    layout="wide"
)

DATA_FILE = Path("transactions.csv")

CATEGORIES = {
    "Income": ["Salary", "Pocket Money", "Freelance", "Investment", "Other Income"],
    "Expense": ["Food", "Travel", "Shopping", "Education", "Bills", "Entertainment",
                "Health", "Rent", "Other Expense"]
}

# -------------------- DATA FUNCTIONS --------------------
def load_transactions():
    """Load saved transactions. Return an empty table if no file exists."""
    columns = ["id", "date", "type", "category", "description", "amount"]
    if DATA_FILE.exists():
        try:
            df = pd.read_csv(DATA_FILE)
            for column in columns:
                if column not in df.columns:
                    df[column] = ""
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            return df[columns]
        except Exception:
            st.error("Could not read transactions.csv. Please check or restore the file.")
    return pd.DataFrame(columns=columns)


def save_transactions(df):
    """Save all transactions to a local CSV file."""
    df.to_csv(DATA_FILE, index=False)


def money(value):
    return f"₹{value:,.2f}"


if "transactions" not in st.session_state:
    st.session_state.transactions = load_transactions()

if "budget" not in st.session_state:
    st.session_state.budget = 10000.0

df = st.session_state.transactions.copy()
if not df.empty:
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

# -------------------- SIDEBAR --------------------
st.sidebar.title("💰 PennyWise")
st.sidebar.caption("Your simple personal finance assistant")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Ask PennyWise", "Add Transaction", "Transaction History", "Budget"]
)
st.sidebar.divider()
st.sidebar.info("Your data is stored locally in transactions.csv on your computer.")

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.title("📊 Financial Dashboard")
    st.write("Welcome to PennyWise! Here's an overview of your finances.")

    today = date.today()
    month_df = df[
        pd.to_datetime(df["date"], errors="coerce").dt.to_period("M")
        == pd.Period(today, freq="M")
    ] if not df.empty else df

    income = df.loc[df["type"] == "Income", "amount"].sum() if not df.empty else 0
    expenses = df.loc[df["type"] == "Expense", "amount"].sum() if not df.empty else 0
    balance = income - expenses

    month_expenses = (
        month_df.loc[month_df["type"] == "Expense", "amount"].sum()
        if not month_df.empty else 0
    )
    savings_rate = ((income - expenses) / income * 100) if income > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Income", money(income))
    c2.metric("Total Expenses", money(expenses))
    c3.metric("Current Balance", money(balance))
    c4.metric("Savings Rate", f"{savings_rate:.1f}%")

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Expenses by Category")
        expense_data = df[df["type"] == "Expense"] if not df.empty else df
        if not expense_data.empty:
            category_totals = expense_data.groupby("category")["amount"].sum()
            st.bar_chart(category_totals)
        else:
            st.info("Add an expense to see your spending chart.")

    with right:
        st.subheader("Income vs Expenses")
        comparison = pd.DataFrame({
            "Amount (₹)": [income, expenses]
        }, index=["Income", "Expenses"])
        st.bar_chart(comparison)
        st.caption("Figures represent all recorded transactions.")

    st.divider()
    st.subheader("Recent Transactions")
    if not df.empty:
        recent = df.sort_values("date", ascending=False).head(5)
        display = recent[["date", "type", "category", "description", "amount"]].copy()
        display["amount"] = display["amount"].apply(money)
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Select 'Add Transaction' to get started.")

# -------------------- ASK THE ASSISTANT --------------------
elif page == "Ask PennyWise":
    st.title("💬 Ask PennyWise")
    st.write("Ask simple questions about your recorded finances.")

    question = st.text_input(
        "Your question",
        placeholder="Example: How much did I spend this month?"
    )

    if st.button("Ask", use_container_width=True):
        q = question.lower().strip()

        total_income = df.loc[df["type"] == "Income", "amount"].sum() if not df.empty else 0
        total_expenses = df.loc[df["type"] == "Expense", "amount"].sum() if not df.empty else 0
        current_balance = total_income - total_expenses

        if not q:
            st.warning("Please type a question first.")
        elif any(word in q for word in ["income", "earned", "earning", "salary"]):
            st.success(f"Your total recorded income is {money(total_income)}.")
        elif any(word in q for word in ["expense", "expenses", "spent", "spending"]):
            st.success(f"Your total recorded expenses are {money(total_expenses)}.")
        elif any(word in q for word in ["balance", "left", "remaining money", "have"]):
            st.success(f"Your current recorded balance is {money(current_balance)}.")
        elif any(word in q for word in ["saving", "savings"]):
            rate = (current_balance / total_income * 100) if total_income > 0 else 0
            st.success(f"Your recorded savings are {money(current_balance)}. Your savings rate is {rate:.1f}%.")
        elif any(word in q for word in ["category", "where", "most"]):
            expense_rows = df[df["type"] == "Expense"] if not df.empty else df
            if expense_rows.empty:
                st.info("There are no expenses recorded yet.")
            else:
                totals = expense_rows.groupby("category")["amount"].sum()
                top_category = totals.idxmax()
                st.success(f"Your highest spending category is {top_category}, with {money(totals.max())} recorded.")
        elif any(word in q for word in ["budget", "limit"]):
            spent_now = 0.0
            if not df.empty:
                dates_now = pd.to_datetime(df["date"], errors="coerce")
                this_month = df[dates_now.dt.to_period("M") == pd.Period(date.today(), freq="M")]
                spent_now = this_month.loc[this_month["type"] == "Expense", "amount"].sum()
            remaining_now = st.session_state.budget - spent_now
            st.success(f"This month's spending is {money(spent_now)}. Your set budget is {money(st.session_state.budget)}. " +
                       (f"You have {money(remaining_now)} left." if remaining_now >= 0 else f"You are over budget by {money(abs(remaining_now))}."))
        elif any(word in q for word in ["hello", "hi", "hey"]):
            st.success("Hello! I'm PennyWise. I can help you understand your income, expenses, balance, savings and budget.")
        else:
            st.info("I couldn't match that question yet. Try asking about your income, expenses, balance, savings, highest spending category or budget.")

    with st.expander("Example questions"):
        st.markdown(
            "- How much income have I recorded?\\n"
            "- How much have I spent?\\n"
            "- What is my current balance?\\n"
            "- What is my savings rate?\\n"
            "- Which category do I spend the most on?\\n"
            "- How much of my budget is left?"
        )

# -------------------- ADD TRANSACTION --------------------
elif page == "Add Transaction":
    st.title("➕ Add a Transaction")
    st.write("Record money received or money spent.")

    
    transaction_type = st.selectbox("Transaction Type", ["Expense", "Income"])

    with st.form("transaction_form", clear_on_submit=True):
        category = st.selectbox("Category", CATEGORIES[transaction_type])
        amount = st.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f")
        description = st.text_input("Description", placeholder="Example: Lunch, monthly salary...")
        transaction_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Save Transaction", use_container_width=True)


        if submitted:
            if amount <= 0:
                st.error("Please enter an amount greater than zero.")
            else:
                new_row = pd.DataFrame([{
                    "id": str(uuid.uuid4()),
                    "date": transaction_date,
                    "type": transaction_type,
                    "category": category,
                    "description": description.strip() or category,
                    "amount": float(amount)
                }])
                updated = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
                st.session_state.transactions = updated
                save_transactions(updated)
                st.success("Transaction saved successfully!")
                st.rerun()

# -------------------- TRANSACTION HISTORY --------------------
elif page == "Transaction History":
    st.title("📜 Transaction History")
    if df.empty:
        st.info("No transactions have been recorded yet.")
    else:
        filter_type = st.selectbox("Filter by Type", ["All", "Income", "Expense"])
        filtered = df.copy()
        if filter_type != "All":
            filtered = filtered[filtered["type"] == filter_type]

        display = filtered[["date", "type", "category", "description", "amount"]].copy()
        display["amount"] = display["amount"].apply(money)
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.subheader("Delete a Transaction")
        options = {
            f'{row["date"]} | {row["type"]} | {row["description"]} | {money(row["amount"])}':
            row["id"]
            for _, row in filtered.iterrows()
        }
        if options:
            selected_label = st.selectbox("Choose transaction", list(options.keys()))
            if st.button("Delete Selected Transaction", type="secondary"):
                transaction_id = options[selected_label]
                updated = st.session_state.transactions[
                    st.session_state.transactions["id"] != transaction_id
                ].copy()
                st.session_state.transactions = updated
                save_transactions(updated)
                st.success("Transaction deleted.")
                st.rerun()

# -------------------- BUDGET --------------------
elif page == "Budget":
    st.title("🎯 Monthly Budget Planner")
    st.write("Set a monthly spending limit and track your expenses against it.")

    budget = st.number_input(
        "Monthly Budget (₹)",
        min_value=0.0,
        value=float(st.session_state.budget),
        step=500.0
    )
    st.session_state.budget = budget

    today = date.today()
    if not df.empty:
        dates = pd.to_datetime(df["date"], errors="coerce")
        current_month = df[dates.dt.to_period("M") == pd.Period(today, freq="M")]
        spent = current_month.loc[current_month["type"] == "Expense", "amount"].sum()
    else:
        spent = 0.0

    remaining = budget - spent
    a, b, c = st.columns(3)
    a.metric("Monthly Budget", money(budget))
    b.metric("Spent This Month", money(spent))
    c.metric("Remaining", money(remaining))

    if budget > 0:
        progress = min(spent / budget, 1.0)
        st.progress(progress)
        if spent > budget:
            st.error(f"You have exceeded your budget by {money(spent - budget)}.")
        else:
            st.success(f"You have used {progress * 100:.1f}% of your monthly budget.")
    else:
        st.warning("Set a budget greater than zero to track your spending.")

# -------------------- FOOTER --------------------
st.sidebar.divider()
st.sidebar.caption("PennyWise | A beginner-friendly Python mini-project")
st.caption("PennyWise is an educational expense-tracking project. It does not connect to bank accounts or provide professional financial advice.")
