import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. DATABASE SETUP (Permanent Storage)
# ==========================================
def init_db():
    conn = sqlite3.connect('kulu_erp_system.db')
    c = conn.cursor()
    # Users Table (SuperAdmin, Wholesaler, Shop)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, payment_status TEXT, approved INTEGER)''')
    # Inventory Table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY, shop_email TEXT, item_name TEXT, purchase_price REAL, selling_price REAL, stock INTEGER, gst_rate REAL)''')
    # Sales/Transactions Table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY, shop_email TEXT, date TEXT, item_name TEXT, qty INTEGER, total_price REAL, profit REAL, is_gst INTEGER)''')
    
    # Create Default Super Admin (You)
    c.execute("INSERT OR IGNORE INTO users (name, email, password, role, payment_status, approved) VALUES (?, ?, ?, ?, ?, ?)",
              ('Super Admin', 'admin@kulusutar.in', 'admin123', 'SuperAdmin', 'Paid', 1))
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def run_query(query, params=()):
    conn = sqlite3.connect('kulu_erp_system.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    data = c.fetchall()
    conn.close()
    return data

# ==========================================
# 3. UI & SESSION STATE
# ==========================================
st.set_page_config(page_title="Kulu ERP & Billing System", layout="wide")

if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# Sidebar Navigation
if st.session_state.user_email is None:
    menu = st.sidebar.radio("Menu", ["Login", "Buy Software (Register)"])
else:
    menu = st.sidebar.radio("Menu", ["Dashboard", "Logout"])

# ==========================================
# 4. LOGIN & REGISTRATION (SaaS Model)
# ==========================================
if menu == "Buy Software (Register)":
    st.title("🛒 Buy Kulu ERP Software")
    st.info("Start managing your Wholesale & Retail business today!")
    
    with st.form("register_form"):
        r_name = st.text_input("Business / Owner Name")
        r_email = st.text_input("Email Address")
        r_pass = st.text_input("Password", type="password")
        r_role = st.selectbox("Select Software Version", ["Wholesaler (Manage multiple shops)", "Retail Shop (Manage single shop)"])
        submit = st.form_submit_button("Proceed to Payment")
        
        if submit:
            if r_name and r_email and r_pass:
                try:
                    role_value = "Wholesaler" if "Wholesaler" in r_role else "Shop"
                    # Add to DB as Pending
                    run_query("INSERT INTO users (name, email, password, role, payment_status, approved) VALUES (?, ?, ?, ?, ?, ?)",
                              (r_name, r_email, r_pass, role_value, 'Pending', 0))
                    st.success("Registration Successful! Please complete your payment to activate.")
                    st.session_state.show_payment = True
                except sqlite3.IntegrityError:
                    st.error("This email is already registered!")
            else:
                st.warning("Please fill all fields.")

    # Payment Gateway Mockup
    if st.session_state.get("show_payment"):
        st.markdown("---")
        st.subheader("💳 Complete Payment")
        st.write("Scan the QR code below and pay **₹4,999** for Lifetime Access.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150)
        st.info("After payment, Super Admin will verify and activate your account within 1 hour.")

elif menu == "Login":
    st.title("🔐 Login to Kulu ERP")
    l_email = st.text_input("Email")
    l_pass = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = run_query("SELECT name, role, approved FROM users WHERE email=? AND password=?", (l_email, l_pass))
        if user:
            if user[0][2] == 1: # If approved
                st.session_state.user_email = l_email
                st.session_state.user_role = user[0][1]
                st.success(f"Welcome {user[0][0]}!")
                st.rerun()
            else:
                st.error("❌ Your account is pending Super Admin approval. Please wait for payment verification.")
        else:
            st.error("Invalid Email or Password.")

elif menu == "Logout":
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.rerun()

# ==========================================
# 5. DASHBOARDS (Role Based)
# ==========================================
elif menu == "Dashboard":
    
    # ---------------- SUPER ADMIN ----------------
    if st.session_state.user_role == "SuperAdmin":
        st.title("👑 Super Admin Control Panel")
        st.write("Welcome, Master Admin. Manage your software clients and earnings here.")
        
        st.subheader("Pending Software Approvals")
        pending_users = run_query("SELECT id, name, email, role FROM users WHERE approved=0")
        if pending_users:
            df_pending = pd.DataFrame(pending_users, columns=["ID", "Name", "Email", "Role"])
            st.table(df_pending)
            
            col1, col2 = st.columns(2)
            with col1:
                app_email = st.selectbox("Select User to Approve", df_pending['Email'])
            with col2:
                if st.button("✅ Verify Payment & Approve"):
                    run_query("UPDATE users SET approved=1, payment_status='Paid' WHERE email=?", (app_email,))
                    st.success(f"User {app_email} activated successfully!")
                    st.rerun()
        else:
            st.info("No pending approvals.")
            
        st.markdown("---")
        st.subheader("💰 Total Earnings")
        total_paid = run_query("SELECT COUNT(*) FROM users WHERE payment_status='Paid' AND role != 'SuperAdmin'")[0][0]
        st.metric(label="Total Software Sold", value=f"{total_paid} Clients", delta=f"₹ {total_paid * 4999}")

    # ---------------- WHOLESALER ----------------
    elif st.session_state.user_role == "Wholesaler":
        st.title("🏢 Wholesaler Master Dashboard")
        st.write("Control your 100 shops, view overall stock, and balance sheets.")
        
        tab1, tab2, tab3 = st.tabs(["Global Stock", "Balance Sheet & Dues", "Manage Shops"])
        with tab1:
            st.subheader("All Shops Inventory View")
            st.info("Data from all connected retail shops will appear here.")
            # We will add global inventory logic here next
        with tab2:
            st.subheader("Total Sales & Profit")
            st.info("Overall GST and Non-GST bills calculation will be displayed here.")
        with tab3:
            st.subheader("Add / Remove Retail Shops")
            st.button("Add New Retail Shop")

    # ---------------- RETAIL SHOP ----------------
    elif st.session_state.user_role == "Shop":
        st.title("🏪 Retail Shop Billing & Inventory")
        
        tab1, tab2, tab3 = st.tabs(["New Sale (Billing)", "My Inventory", "Daily Profit"])
        with tab1:
            st.subheader("Create New Bill")
            bill_type = st.radio("Bill Type", ["Auto GST Bill", "Non-GST Bill"], horizontal=True)
            st.text_input("Customer Name")
            st.selectbox("Select Item", ["Item 1", "Item 2"])
            st.number_input("Quantity", min_value=1)
            st.button("Generate & Print PDF Bill")
            
        with tab2:
            st.subheader("Manage Stock")
            st.button("Add New Product")
            
        with tab3:
            st.subheader("Today's Performance")
            st.metric(label="Total Sales", value="₹0.00")
            st.metric(label="Net Profit", value="₹0.00")
