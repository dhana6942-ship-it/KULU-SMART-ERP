import streamlit as st
import sqlite3
import pandas as pd
import random

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_db():
    conn = sqlite3.connect('kulu_erp_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, 
                 payment_status TEXT, approved INTEGER, aadhar TEXT, pan TEXT, gst TEXT, mobile TEXT)''')
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN aadhar TEXT")
        c.execute("ALTER TABLE users ADD COLUMN pan TEXT")
        c.execute("ALTER TABLE users ADD COLUMN gst TEXT")
        c.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
    except:
        pass

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
# 2. PAGE CONFIG & CUSTOM CSS (Unique Look)
# ==========================================
st.set_page_config(page_title="Kulu ERP Master", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .card-admin { background-color: #ffebee; padding: 20px; border-radius: 10px; border-top: 5px solid #f44336; text-align: center; }
    .card-whole { background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-top: 5px solid #2196f3; text-align: center; }
    .card-shop { background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-top: 5px solid #4caf50; text-align: center; }
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #333; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SESSION STATES
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_role" not in st.session_state: st.session_state.user_role = None
if "user_name" not in st.session_state: st.session_state.user_name = None

if "forgot_step" not in st.session_state: st.session_state.forgot_step = 1

# ==========================================
# 4. SIDEBAR MENU
# ==========================================
if not st.session_state.logged_in:
    menu = st.sidebar.radio("Navigation", ["Home Ground", "Unified Login", "Register (Buy Software)", "Forgot Password"])
else:
    menu = st.sidebar.radio("Navigation", ["My Dashboard", "Logout"])

# ==========================================
# 5. HOME GROUND (The Unique Table Layout)
# ==========================================
if menu == "Home Ground" and not st.session_state.logged_in:
    st.markdown('<div class="main-title">🏢 Kulu Smart ERP & Billing System</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-admin"><h3>👑 Super Admin</h3><p>Manage software clients, approve payments, and track earnings.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card-whole"><h3>🏢 Wholesaler</h3><p>Control 100+ retail shops, track global inventory & balance sheets.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card-shop"><h3>🏪 Retail Shop</h3><p>Generate smart GST/Non-GST bills and manage daily local stock.</p></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.info("👈 **To start working, go to 'Unified Login' from the sidebar and enter your unique Email ID.**")

# ==========================================
# 6. UNIFIED LOGIN (Smart Routing)
# ==========================================
elif menu == "Unified Login":
    st.title("🔐 Secure Login Portal")
    st.write("Enter your Unique Email ID. The system will auto-detect your role.")
    
    l_email = st.text_input("Email (Unique ID)")
    l_pass = st.text_input("Password", type="password")
    
    if st.button("🚀 Login"):
        if l_email and l_pass:
            user = run_query("SELECT name, role, approved FROM users WHERE email=? AND password=?", (l_email, l_pass))
            if user:
                if user[0][2] == 1: # Approved
                    st.session_state.logged_in = True
                    st.session_state.user_name = user[0][0]
                    st.session_state.user_role = user[0][1]
                    st.session_state.user_email = l_email
                    st.success(f"Welcome back, {user[0][0]}!")
                    st.rerun()
                else:
                    st.error("❌ Your account is pending Super Admin payment verification.")
            else:
                st.error("❌ Invalid Email or Password.")
        else:
            st.warning("Please enter both Email and Password.")

# ==========================================
# 7. FORGOT PASSWORD (Universal)
# ==========================================
elif menu == "Forgot Password":
    st.title("🔑 Reset Password (All Users)")
    
    if st.session_state.forgot_step == 1:
        f_email = st.text_input("Enter your Registered Email")
        if st.button("Send Reset OTP"):
            check = run_query("SELECT email FROM users WHERE email=?", (f_email,))
            if check:
                st.session_state.forgot_otp = str(random.randint(100000, 999999))
                st.session_state.forgot_email = f_email
                st.session_state.forgot_step = 2
                st.rerun()
            else:
                st.error("❌ Email not found in our system.")
                
    elif st.session_state.forgot_step == 2:
        st.success(f"📧 EMAIL SENT! (Mock Test OTP: **{st.session_state.forgot_otp}** )")
        e_otp = st.text_input("Enter 6-digit OTP")
        if st.button("Verify OTP"):
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
                st.success("✅ Password updated! Go to Login.")
                st.session_state.forgot_step = 1
            else:
                st.warning("Password cannot be empty.")

# ==========================================
# 8. REGISTRATION (Same as before)
# ==========================================
elif menu == "Register (Buy Software)":
    st.title("🛒 Buy Kulu ERP Software")
    # Form layout for registration...
    with st.form("reg_form"):
        r_role = st.selectbox("Role", ["Wholesaler", "Shop"])
        r_name = st.text_input("Business Name")
        r_email = st.text_input("Email")
        r_pass = st.text_input("Password", type="password")
        r_mobile = st.text_input("Mobile")
        submit = st.form_submit_button("Register & Pay")
        
        if submit:
            if r_name and r_email and r_pass:
                try:
                    run_query("INSERT INTO users (name, email, password, role, payment_status, approved, mobile) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (r_name, r_email, r_pass, r_role, 'Pending', 0, r_mobile))
                    st.success("Registration Saved! Please contact Super Admin with ₹4999 payment to activate.")
                except:
                    st.error("Email already exists.")

# ==========================================
# 9. DYNAMIC ROLE-BASED DASHBOARDS
# ==========================================
elif menu == "My Dashboard" and st.session_state.logged_in:
    
    st.markdown(f"### 👋 Welcome, {st.session_state.user_name} ({st.session_state.user_role})")
    st.markdown("---")
    
    # ---------------- SUPER ADMIN ----------------
    if st.session_state.user_role == "SuperAdmin":
        st.title("👑 Super Admin Control Panel")
        pending_users = run_query("SELECT name, email, role, mobile FROM users WHERE approved=0 AND role != 'SuperAdmin'")
        if pending_users:
            st.dataframe(pd.DataFrame(pending_users, columns=["Name", "Email", "Role", "Mobile"]))
            app_email = st.selectbox("Select User to Verify Payment", [u[1] for u in pending_users])
            if st.button("✅ Verify Payment & Activate Account"):
                run_query("UPDATE users SET approved=1, payment_status='Paid' WHERE email=?", (app_email,))
                st.success(f"{app_email} is now Active!")
                st.rerun()
        else:
            st.info("No pending approvals.")

    # ---------------- WHOLESALER ----------------
    elif st.session_state.user_role == "Wholesaler":
        st.title("🏢 Wholesaler Master Terminal")
        tab1, tab2 = st.tabs(["Global Network Stock", "Dues & Balance Sheet"])
        with tab1: st.info("Multi-shop inventory will sync here.")
        with tab2: st.info("Pending shop balances will display here.")

    # ---------------- RETAIL SHOP ----------------
    elif st.session_state.user_role == "Shop":
        st.title("🏪 Retail Shop Billing & Inventory")
        tab1, tab2 = st.tabs(["New GST/Non-GST Bill", "My Inventory"])
        with tab1: st.info("Auto GST calculation & PDF generation module.")
        with tab2: st.info("Add products and update stock module.")

# ==========================================
# 10. LOGOUT
# ==========================================
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.rerun()
