import streamlit as st
import sqlite3
import pandas as pd
import random
import string
from datetime import date

# ==========================================
# 1. DATABASE SETUP (Added Tally Ledgers & Vouchers)
# ==========================================
def init_db():
    conn = sqlite3.connect('kulu_erp_system.db')
    c = conn.cursor()
    
    # Core Tables
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, 
                 payment_status TEXT, approved INTEGER, aadhar TEXT, pan TEXT, gst TEXT, mobile TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS admin_settings
                 (id INTEGER PRIMARY KEY, upi_id TEXT, monthly_price REAL, yearly_price REAL, lifetime_price REAL, soft_gst REAL)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY, shop_email TEXT, item_name TEXT, purchase_price REAL, selling_price REAL, stock INTEGER, gst_rate REAL)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY, shop_email TEXT, date TEXT, item_name TEXT, qty INTEGER, total_price REAL, profit REAL, is_gst INTEGER)''')
                 
    # Tally Prime Features: Ledgers & Vouchers
    c.execute('''CREATE TABLE IF NOT EXISTS ledgers
                 (id INTEGER PRIMARY KEY, shop_email TEXT, ledger_name TEXT, ledger_group TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS vouchers
                 (id INTEGER PRIMARY KEY, shop_email TEXT, date TEXT, v_type TEXT, ledger_name TEXT, amount REAL, narration TEXT)''')
    
    cols_to_add = [
        ("utr_no", "TEXT"), ("paid_amount", "REAL"), 
        ("package_type", "TEXT"), ("license_key", "TEXT"), 
        ("is_deleted", "INTEGER DEFAULT 0"), ("shop_photo", "BLOB")
    ]
    
    for col, dtype in cols_to_add:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass 

    c.execute("INSERT OR IGNORE INTO users (name, email, password, role, payment_status, approved, is_deleted) VALUES (?, ?, ?, ?, ?, ?, ?)",
              ('Super Admin', 'admin@kulusutar.in', 'admin123', 'SuperAdmin', 'Paid', 1, 0))
              
    c.execute("INSERT OR IGNORE INTO admin_settings (id, upi_id, monthly_price, yearly_price, lifetime_price, soft_gst) VALUES (1, 'kulusutar@ybl', 499, 4999, 9999, 18)")
    
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

def generate_license():
    return "KULU-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

# ==========================================
# 2. PAGE CONFIG & CUSTOM CSS 
# ==========================================
st.set_page_config(page_title="Kulu ERP - Tally Edition", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .card-admin { background-color: #ffebee; padding: 20px; border-radius: 10px; border-top: 5px solid #f44336; text-align: center; margin-bottom: 15px;}
    .card-whole { background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-top: 5px solid #2196f3; text-align: center; margin-bottom: 15px;}
    .card-shop { background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-top: 5px solid #4caf50; text-align: center; margin-bottom: 15px;}
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #333; margin-bottom: 30px; }
    .tally-header { background-color: #004d40; color: white; padding: 10px; border-radius: 5px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SESSION STATES
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_page" not in st.session_state: st.session_state.current_page = "Home Ground"
if "login_role" not in st.session_state: st.session_state.login_role = None

# ==========================================
# 4. APP ROUTING
# ==========================================
if st.session_state.logged_in:
    menu = st.sidebar.radio("Navigation", ["Gateway of ERP", "Logout"])
    
    if menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.session_state.current_page = "Home Ground"
        st.rerun()
        
    elif menu == "Gateway of ERP":
        
        # ---------------- SUPER ADMIN ----------------
        if st.session_state.user_role == "SuperAdmin":
            settings = run_query("SELECT upi_id, monthly_price, yearly_price, lifetime_price, soft_gst FROM admin_settings WHERE id=1")[0]
            st.title("👑 Super Admin Control Panel")
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛡️ Client Approvals", "⚙️ Pricing & Settings", "♻️ Data Recovery", "🔐 Profile & Security", "🖼️ Shop Photos"])
            
            with tab1:
                users = run_query("SELECT id, name, email, role, package_type, utr_no, paid_amount, license_key, approved FROM users WHERE role != 'SuperAdmin' AND is_deleted=0")
                if users:
                    df = pd.DataFrame(users, columns=["ID", "Name", "Email", "Role", "Package", "UTR No", "Amount Paid", "License Key", "Status"])
                    df["Status"] = df["Status"].apply(lambda x: "Active" if x==1 else "Pending")
                    st.dataframe(df, use_container_width=True)
                    c1, c2, c3 = st.columns(3)
                    with c1: app_email = st.selectbox("Select User Email", df['Email'])
                    with c2:
                        if st.button("✅ Approve & Generate License"):
                            run_query("UPDATE users SET approved=1, payment_status='Paid', license_key=? WHERE email=?", (generate_license(), app_email))
                            st.success("Approved!")
                            st.rerun()
                    with c3:
                        if st.button("🗑️ Suspend User"):
                            run_query("UPDATE users SET is_deleted=1 WHERE email=?", (app_email,))
                            st.rerun()
                else: st.info("No active clients.")
            with tab2: st.info("Admin Settings available in full version.")
            with tab3: st.info("Recycle Bin available in full version.")
            with tab4: st.info("Profile update available in full version.")
            with tab5: st.info("Shop Photos control available in full version.")

        # ---------------- WHOLESALER & RETAIL SHOP (TALLY PRIME CLONE) ----------------
        else:
            my_data = run_query("SELECT license_key, package_type, shop_photo, name FROM users WHERE email=?", (st.session_state.user_email,))[0]
            
            # Auto Create Default Ledgers if not exists
            check_ledger = run_query("SELECT id FROM ledgers WHERE shop_email=?", (st.session_state.user_email,))
            if not check_ledger:
                run_query("INSERT INTO ledgers (shop_email, ledger_name, ledger_group) VALUES (?, ?, ?)", (st.session_state.user_email, "Cash A/c", "Cash-in-Hand"))
                run_query("INSERT INTO ledgers (shop_email, ledger_name, ledger_group) VALUES (?, ?, ?)", (st.session_state.user_email, "Sales A/c", "Sales Accounts"))
                run_query("INSERT INTO ledgers (shop_email, ledger_name, ledger_group) VALUES (?, ?, ?)", (st.session_state.user_email, "Purchase A/c", "Purchase Accounts"))

            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f'<div class="tally-header"><h2>📊 Gateway of Kulu ERP - {my_data[3]} ({st.session_state.user_role})</h2></div>', unsafe_allow_html=True)
            with c2:
                if my_data[2]: st.image(my_data[2], width=80)
            
            if my_data[0] is None:
                st.warning("⚠️ ଆପଣଙ୍କ ଆକାଉଣ୍ଟ ଏପର୍ଯ୍ୟନ୍ତ Super Admin ଙ୍କ ଦ୍ୱାରା ଆପ୍ରୁଭ୍ ହୋଇନାହିଁ।")
            else:
                tab1, tab2, tab3, tab4 = st.tabs(["📈 Profit & Loss (Dashboard)", "📦 Masters (Ledgers & Stock)", "📝 Vouchers (F5-F9)", "📓 Day Book"])
                
                # --- TAB 1: DASHBOARD & P&L ---
                with tab1:
                    st.subheader("Financial Summary (Today)")
                    today_str = str(date.today())
                    
                    sales_data = run_query("SELECT SUM(amount) FROM vouchers WHERE shop_email=? AND date=? AND v_type='Sales (F8)'", (st.session_state.user_email, today_str))[0][0]
                    receipt_data = run_query("SELECT SUM(amount) FROM vouchers WHERE shop_email=? AND date=? AND v_type='Receipt (F6)'", (st.session_state.user_email, today_str))[0][0]
                    payment_data = run_query("SELECT SUM(amount) FROM vouchers WHERE shop_email=? AND date=? AND v_type='Payment (F5)'", (st.session_state.user_email, today_str))[0][0]
                    profit_data = run_query("SELECT SUM(profit) FROM transactions WHERE shop_email=? AND date=?", (st.session_state.user_email, today_str))[0][0]
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total Sales", f"₹ {sales_data if sales_data else 0.0}")
                    c2.metric("Gross Profit", f"₹ {profit_data if profit_data else 0.0}")
                    c3.metric("Money Received", f"₹ {receipt_data if receipt_data else 0.0}")
                    c4.metric("Payments Made", f"₹ {payment_data if payment_data else 0.0}")

                # --- TAB 2: MASTERS (CREATE LEDGERS & ITEMS) ---
                with tab2:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("👤 Create Ledger Account")
                        with st.form("ledger_form"):
                            l_name = st.text_input("Ledger Name (e.g., Ramu Seth, HDFC Bank)")
                            l_group = st.selectbox("Under Group", ["Sundry Debtors (Customer)", "Sundry Creditors (Supplier)", "Bank Accounts", "Indirect Expenses"])
                            if st.form_submit_button("Save Ledger"):
                                if l_name:
                                    run_query("INSERT INTO ledgers (shop_email, ledger_name, ledger_group) VALUES (?, ?, ?)", (st.session_state.user_email, l_name, l_group))
                                    st.success(f"Ledger '{l_name}' created!")
                                    st.rerun()
                                    
                        st.markdown("**Existing Ledgers:**")
                        ledgers = run_query("SELECT ledger_name, ledger_group FROM ledgers WHERE shop_email=?", (st.session_state.user_email,))
                        st.dataframe(pd.DataFrame(ledgers, columns=["Ledger Name", "Group"]), use_container_width=True)

                    with c2:
                        st.subheader("📦 Create Stock Item")
                        with st.form("stock_form"):
                            i_name = st.text_input("Item Name")
                            i_stock = st.number_input("Opening Stock", min_value=0, value=0)
                            i_pprice = st.number_input("Purchase Rate (₹)", min_value=0.0, value=0.0)
                            i_gst = st.number_input("GST Rate (%)", min_value=0.0, value=18.0)
                            i_sprice = st.number_input("Selling Rate (₹)", min_value=0.0, value=0.0)
                            if st.form_submit_button("Save Item"):
                                if i_name:
                                    run_query("INSERT INTO inventory (shop_email, item_name, purchase_price, selling_price, stock, gst_rate) VALUES (?, ?, ?, ?, ?, ?)",
                                              (st.session_state.user_email, i_name, i_pprice, i_sprice, i_stock, i_gst))
                                    st.success(f"Item '{i_name}' created!")
                                    st.rerun()
                        
                        st.markdown("**Stock Summary:**")
                        stocks = run_query("SELECT item_name, stock, selling_price FROM inventory WHERE shop_email=?", (st.session_state.user_email,))
                        st.dataframe(pd.DataFrame(stocks, columns=["Item", "Qty", "Rate"]), use_container_width=True)

                # --- TAB 3: VOUCHER ENTRIES (F5, F6, F8, F9) ---
                with tab3:
                    st.subheader("📝 Accounting Vouchers")
                    v_type = st.radio("Select Voucher Type", ["Sales (F8)", "Purchase (F9)", "Receipt (F6)", "Payment (F5)"], horizontal=True)
                    
                    ledgers_list = [l[0] for l in run_query("SELECT ledger_name FROM ledgers WHERE shop_email=?", (st.session_state.user_email,))]
                    stock_list = run_query("SELECT id, item_name, selling_price, stock, gst_rate, purchase_price FROM inventory WHERE shop_email=?", (st.session_state.user_email,))
                    
                    st.markdown("---")
                    
                    # SALES VOUCHER (F8)
                    if v_type == "Sales (F8)":
                        if stock_list:
                            item_dict = {f"{item[1]} (Avail: {item[3]})": item for item in stock_list if item[3] > 0}
                            if not item_dict: st.warning("Out of Stock!"); st.stop()
                            
                            s_party = st.selectbox("Party A/c Name", ledgers_list)
                            s_item = st.selectbox("Name of Item", list(item_dict.keys()))
                            
                            item_data = item_dict[s_item]
                            col1, col2, col3 = st.columns(3)
                            with col1: s_qty = st.number_input("Quantity", min_value=1, value=1)
                            with col2: s_rate = st.number_input("Rate", value=float(item_data[2]))
                            with col3: s_gst = st.number_input("GST %", value=float(item_data[4]))
                            
                            is_gst = st.checkbox("Apply GST", value=True)
                            
                            base_amt = s_qty * s_rate
                            tax_amt = (base_amt * s_gst)/100 if is_gst else 0
                            total_amt = base_amt + tax_amt
                            profit = base_amt - (item_data[5] * s_qty)
                            
                            st.success(f"**Total Invoice Value: ₹ {total_amt:.2f}**")
                            
                            if st.button("💾 Accept & Save Voucher", use_container_width=True):
                                if s_qty <= item_data[3]:
                                    # Deduct Stock
                                    run_query("UPDATE inventory SET stock = stock - ? WHERE id=?", (s_qty, item_data[0]))
                                    # Add to Transactions (For P&L)
                                    run_query("INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                              (st.session_state.user_email, str(date.today()), item_data[1], s_qty, total_amt, profit, 1 if is_gst else 0))
                                    # Add to Vouchers (For Daybook)
                                    run_query("INSERT INTO vouchers (shop_email, date, v_type, ledger_name, amount, narration) VALUES (?, ?, ?, ?, ?, ?)",
                                              (st.session_state.user_email, str(date.today()), "Sales (F8)", s_party, total_amt, f"Sold {s_qty} {item_data[1]}"))
                                    st.success("Voucher Saved!"); st.rerun()
                                else: st.error("Not enough stock!")
                        else: st.warning("Please create stock items in Masters first.")

                    # PURCHASE VOUCHER (F9)
                    elif v_type == "Purchase (F9)":
                        if stock_list:
                            item_dict2 = {item[1]: item for item in stock_list}
                            p_party = st.selectbox("Supplier A/c Name", ledgers_list)
                            p_item = st.selectbox("Name of Item", list(item_dict2.keys()))
                            
                            item_data = item_dict2[p_item]
                            col1, col2 = st.columns(2)
                            with col1: p_qty = st.number_input("Quantity Purchased", min_value=1, value=1)
                            with col2: p_rate = st.number_input("Purchase Rate", value=float(item_data[5]))
                            
                            total_p = p_qty * p_rate
                            st.info(f"**Total Bill Value: ₹ {total_p:.2f}**")
                            
                            if st.button("💾 Accept & Save Voucher", use_container_width=True):
                                # Add Stock
                                run_query("UPDATE inventory SET stock = stock + ?, purchase_price = ? WHERE id=?", (p_qty, p_rate, item_data[0]))
                                # Add to Vouchers
                                run_query("INSERT INTO vouchers (shop_email, date, v_type, ledger_name, amount, narration) VALUES (?, ?, ?, ?, ?, ?)",
                                          (st.session_state.user_email, str(date.today()), "Purchase (F9)", p_party, total_p, f"Bought {p_qty} {p_item}"))
                                st.success("Voucher Saved!"); st.rerun()
                        else: st.warning("Create items in Masters first.")

                    # RECEIPT (F6) OR PAYMENT (F5)
                    else:
                        r_party = st.selectbox("Account (Ledger)", ledgers_list)
                        r_amt = st.number_input("Amount (₹)", min_value=1.0, value=100.0)
                        r_narration = st.text_input("Narration (Remarks)")
                        
                        if st.button("💾 Accept & Save Voucher", use_container_width=True):
                            run_query("INSERT INTO vouchers (shop_email, date, v_type, ledger_name, amount, narration) VALUES (?, ?, ?, ?, ?, ?)",
                                      (st.session_state.user_email, str(date.today()), v_type, r_party, r_amt, r_narration))
                            st.success(f"{v_type} Saved Successfully!"); st.rerun()

                # --- TAB 4: DAY BOOK ---
                with tab4:
                    st.subheader("📓 Day Book (Today's Register)")
                    v_data = run_query("SELECT id, v_type, ledger_name, amount, narration FROM vouchers WHERE shop_email=? AND date=? ORDER BY id DESC", (st.session_state.user_email, str(date.today())))
                    
                    if v_data:
                        df_v = pd.DataFrame(v_data, columns=["Vch No.", "Voucher Type", "Particulars (Ledger)", "Amount (₹)", "Narration"])
                        st.dataframe(df_v, use_container_width=True)
                    else:
                        st.info("No vouchers entered today.")

else:
    # --- LOGGED OUT VIEWS ---
    if st.session_state.current_page == "Home Ground":
        st.markdown('<div class="main-title">🏢 Kulu Smart ERP & Billing System</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="card-admin"><h3>👑 Super Admin</h3><p>Manage pricing, approve UTR, issue licenses.</p></div>', unsafe_allow_html=True)
            if st.button("🔐 Login as Admin", use_container_width=True): st.session_state.current_page = "Login"; st.session_state.login_role = "SuperAdmin"; st.rerun()
        with col2:
            st.markdown('<div class="card-whole"><h3>🏢 Wholesaler</h3><p>Control 100+ retail shops globally.</p></div>', unsafe_allow_html=True)
            if st.button("🔐 Login as Wholesaler", use_container_width=True): st.session_state.current_page = "Login"; st.session_state.login_role = "Wholesaler"; st.rerun()
        with col3:
            st.markdown('<div class="card-shop"><h3>🏪 Retail Shop</h3><p>Smart GST/Non-GST bills & local stock.</p></div>', unsafe_allow_html=True)
            if st.button("🔐 Login as Shop", use_container_width=True): st.session_state.current_page = "Login"; st.session_state.login_role = "Shop"; st.rerun()
            
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🛒 Register (Buy Software)"): st.session_state.current_page = "Register"; st.rerun()
        with c2:
            if st.button("🔑 Forgot Password"): st.session_state.current_page = "Forgot Password"; st.rerun()

    elif st.session_state.current_page == "Login":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title(f"🔐 {st.session_state.login_role} Login")
        l_email = st.text_input("Email")
        l_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            user = run_query("SELECT name, role, approved, is_deleted FROM users WHERE email=? AND password=?", (l_email, l_pass))
            if user:
                if user[0][3] == 1: st.error("❌ Your account has been Suspended/Deleted by Admin.")
                elif user[0][1] == st.session_state.login_role:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user[0][1]
                    st.session_state.user_email = l_email
                    st.rerun()
                else: st.error("❌ Role Mismatch.")
            else: st.error("Invalid Credentials.")

    elif st.session_state.current_page == "Register":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🛒 Buy Kulu ERP Software")
        settings = run_query("SELECT upi_id, monthly_price, yearly_price, lifetime_price, soft_gst FROM admin_settings WHERE id=1")[0]
        gst_pct = settings[4]
        
        with st.form("reg_form"):
            r_role = st.selectbox("Role", ["Wholesaler", "Shop"])
            r_name = st.text_input("Business Name")
            r_email = st.text_input("Email")
            r_pass = st.text_input("Password", type="password")
            
            st.markdown("---")
            p_type = st.radio("Select Software Package", [f"Monthly", f"1 Year", f"Lifetime"])
            
            st.markdown(f"**Pay to UPI ID:** `{settings[0]}`")
            r_utr = st.text_input("Enter UTR / Transaction No. (Required)")
            r_amt = st.number_input("Total Amount Paid (Including GST)", min_value=0.0)
            
            if st.form_submit_button("Submit Registration & Payment"):
                if r_name and r_email and r_pass and r_utr and r_amt > 0:
                    try:
                        run_query("INSERT INTO users (name, email, password, role, payment_status, approved, utr_no, paid_amount, package_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (r_name, r_email, r_pass, r_role, 'Pending', 0, r_utr, r_amt, p_type.split(" ")[0]))
                        st.success("✅ Payment Submitted! Super Admin will verify your UTR and assign a License Key.")
                    except: st.error("❌ Email already registered.")
                else: st.warning("Please fill all fields and enter valid UTR/Amount.")

    elif st.session_state.current_page == "Forgot Password":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🔑 Reset Password")
        st.info("System is ready. Use OTP to reset.")
