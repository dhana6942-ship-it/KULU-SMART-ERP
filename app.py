import streamlit as st
import sqlite3
import pandas as pd
import random

# ==========================================
# 1. DATABASE SETUP (Permanent Storage & Updates)
# ==========================================
def init_db():
    conn = sqlite3.connect('kulu_erp_system.db')
    c = conn.cursor()
    
    # Create Table with New Fields
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, 
                 payment_status TEXT, approved INTEGER, aadhar TEXT, pan TEXT, gst TEXT, mobile TEXT)''')
    
    # Auto-Update older table if columns are missing
    try:
        c.execute("ALTER TABLE users ADD COLUMN aadhar TEXT")
        c.execute("ALTER TABLE users ADD COLUMN pan TEXT")
        c.execute("ALTER TABLE users ADD COLUMN gst TEXT")
        c.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
    except:
        pass # Columns already exist

    # Create Inventory and Transactions tables
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY, shop_email TEXT, item_name TEXT, purchase_price REAL, selling_price REAL, stock INTEGER, gst_rate REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY, shop_email TEXT, date TEXT, item_name TEXT, qty INTEGER, total_price REAL, profit REAL, is_gst INTEGER)''')
    
    # Default Super Admin
    c.execute("INSERT OR IGNORE INTO users (name, email, password, role, payment_status, approved) VALUES (?, ?, ?, ?, ?, ?)",
              ('Super Admin', 'admin@kulusutar.in', 'admin123', 'SuperAdmin', 'Paid', 1))
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=()):
    conn = sqlite3.connect('kulu_erp_system.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    data = c.fetchall()
    conn.close()
    return data

# ==========================================
# 2. SESSION STATES FOR OTP & LOGIN
# ==========================================
st.set_page_config(page_title="Kulu ERP & Billing System", layout="wide")

if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_role" not in st.session_state: st.session_state.user_role = None

# Registration States
if "reg_step" not in st.session_state: st.session_state.reg_step = 1
if "reg_otp" not in st.session_state: st.session_state.reg_otp = ""
if "reg_data" not in st.session_state: st.session_state.reg_data = {}

# Forgot Password States
if "forgot_step" not in st.session_state: st.session_state.forgot_step = 1
if "forgot_email" not in st.session_state: st.session_state.forgot_email = ""
if "forgot_otp" not in st.session_state: st.session_state.forgot_otp = ""

# Sidebar
if st.session_state.user_email is None:
    menu = st.sidebar.radio("Navigation Menu", ["Login", "Buy Software (Register)", "Forgot Password"])
else:
    menu = st.sidebar.radio("Navigation Menu", ["Dashboard", "Logout"])

# ==========================================
# 3. REGISTRATION (Email OTP & Wholesaler Details)
# ==========================================
if menu == "Buy Software (Register)":
    st.title("🛒 Buy Kulu ERP Software")
    st.info("Register via Email OTP to access your Wholesale & Retail business software.")

    if st.session_state.reg_step == 1:
        st.subheader("Step 1: Business Details")
        r_role = st.selectbox("Select Software Version", ["Wholesaler (Manage multiple shops)", "Retail Shop (Manage single shop)"])
        r_name = st.text_input("Business / Owner Name")
        r_email = st.text_input("Email Address")
        r_mobile = st.text_input("Mobile Number")
        r_pass = st.text_input("Create Password", type="password")
        
        r_aadhar = ""
        r_pan = ""
        r_gst = ""
        if "Wholesaler" in r_role:
            st.markdown("**Wholesaler KYC Details:**")
            col1, col2, col3 = st.columns(3)
            with col1: r_aadhar = st.text_input("Aadhar Number")
            with col2: r_pan = st.text_input("PAN Number")
            with col3: r_gst = st.text_input("GST Number (Optional)")
            
        if st.button("Send Email OTP"):
            if r_name and r_email and r_mobile and r_pass:
                # Check if email exists
                check = run_query("SELECT email FROM users WHERE email=?", (r_email,))
                if check:
                    st.error("❌ This Email is already registered!")
                else:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.reg_otp = otp
                    st.session_state.reg_data = {
                        "name": r_name, "email": r_email, "mobile": r_mobile, "pass": r_pass, 
                        "role": "Wholesaler" if "Wholesaler" in r_role else "Shop",
                        "aadhar": r_aadhar, "pan": r_pan, "gst": r_gst
                    }
                    st.session_state.reg_step = 2
                    st.rerun()
            else:
                st.warning("⚠️ Please fill all required fields!")

    elif st.session_state.reg_step == 2:
        st.subheader("Step 2: Email OTP Verification")
        # Mock Email Sending Alert (For local testing)
        st.success(f"📧 EMAIL SENT! (Mock Test OTP: **{st.session_state.reg_otp}** ) - Check your inbox!")
        
        entered_otp = st.text_input("Enter 6-digit OTP sent to your email")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Verify OTP"):
                if entered_otp == st.session_state.reg_otp:
                    d = st.session_state.reg_data
                    run_query('''INSERT INTO users (name, email, password, role, payment_status, approved, aadhar, pan, gst, mobile) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (d['name'], d['email'], d['pass'], d['role'], 'Pending', 0, d['aadhar'], d['pan'], d['gst'], d['mobile']))
                    st.success("✅ Email Verified & Registered Successfully!")
                    st.session_state.reg_step = 3
                    st.rerun()
                else:
                    st.error("❌ Invalid OTP. Try again.")
        with col2:
            if st.button("Cancel & Go Back"):
                st.session_state.reg_step = 1
                st.rerun()

    elif st.session_state.reg_step == 3:
        st.subheader("💳 Step 3: Complete Payment")
        st.write("Scan the QR code below and pay **₹4,999** for Lifetime Access.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150)
        st.info("After payment, Super Admin will verify and activate your account. You can login once approved.")
        if st.button("Done"):
            st.session_state.reg_step = 1
            st.rerun()

# ==========================================
# 4. LOGIN PAGE
# ==========================================
elif menu == "Login":
    st.title("🔐 Login to Kulu ERP")
    l_email = st.text_input("Email")
    l_pass = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = run_query("SELECT name, role, approved FROM users WHERE email=? AND password=?", (l_email, l_pass))
        if user:
            if user[0][2] == 1: # Approved
                st.session_state.user_email = l_email
                st.session_state.user_role = user[0][1]
                st.rerun()
            else:
                st.error("❌ Your account is pending Super Admin payment verification.")
        else:
            st.error("❌ Invalid Email or Password.")

# ==========================================
# 5. FORGOT PASSWORD FLOW
# ==========================================
elif menu == "Forgot Password":
    st.title("🔑 Reset Password")
    
    if st.session_state.forgot_step == 1:
        st.write("Enter your registered email address to receive an OTP.")
        f_email = st.text_input("Registered Email")
        if st.button("Send Reset OTP"):
            check = run_query("SELECT email FROM users WHERE email=?", (f_email,))
            if check:
                otp = str(random.randint(100000, 999999))
                st.session_state.forgot_otp = otp
                st.session_state.forgot_email = f_email
                st.session_state.forgot_step = 2
                st.rerun()
            else:
                st.error("❌ Email not found in our database.")
                
    elif st.session_state.forgot_step == 2:
        st.success(f"📧 EMAIL SENT! (Mock Test OTP: **{st.session_state.forgot_otp}** )")
        e_otp = st.text_input("Enter 6-digit OTP")
        if st.button("Verify"):
            if e_otp == st.session_state.forgot_otp:
                st.session_state.forgot_step = 3
                st.rerun()
            else:
                st.error("❌ Invalid OTP.")
                
    elif st.session_state.forgot_step == 3:
        new_pass = st.text_input("Enter New Password", type="password")
        if st.button("Update Password"):
            if new_pass:
                run_query("UPDATE users SET password=? WHERE email=?", (new_pass, st.session_state.forgot_email))
                st.success("✅ Password updated successfully! Please go to Login.")
                st.session_state.forgot_step = 1
            else:
                st.warning("Password cannot be empty.")

# ==========================================
# 6. LOGOUT
# ==========================================
elif menu == "Logout":
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.rerun()

# ==========================================
# 7. MAIN DASHBOARDS
# ==========================================
elif menu == "Dashboard":
    if st.session_state.user_role == "SuperAdmin":
        st.title("👑 Super Admin Control Panel")
        st.write("Welcome, Master Admin. Manage clients and earnings here.")
        
        st.subheader("Pending Software Approvals")
        pending_users = run_query("SELECT id, name, email, role, mobile, aadhar, pan, gst FROM users WHERE approved=0 AND role != 'SuperAdmin'")
        if pending_users:
            df_pending = pd.DataFrame(pending_users, columns=["ID", "Name", "Email", "Role", "Mobile", "Aadhar", "PAN", "GST"])
            st.dataframe(df_pending)
            
            app_email = st.selectbox("Select User to Verify Payment & Approve", df_pending['Email'])
            if st.button("✅ Verify Payment & Activate Account"):
                run_query("UPDATE users SET approved=1, payment_status='Paid' WHERE email=?", (app_email,))
                st.success(f"User {app_email} activated successfully!")
                st.rerun()
        else:
            st.info("No pending approvals.")

    elif st.session_state.user_role == "Wholesaler":
        st.title("🏢 Wholesaler Dashboard")
        st.write("Welcome! Here you can manage your 100 retail shops, track overall stock, and check balances.")
        st.info("Development Phase: The multi-shop inventory and balance sheet modules will be added here next.")

    elif st.session_state.user_role == "Shop":
        st.title("🏪 Retail Shop Billing System")
        st.write("Welcome! This is your daily sales, billing, and inventory terminal.")
        st.info("Development Phase: Add product to stock, GST billing, and daily profit report modules will be added here next.")
