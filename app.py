import streamlit as st
import sqlite3
import pandas as pd
import random
import string
import urllib.parse
from datetime import date, timedelta
import streamlit.components.v1 as components
import smtplib
from email.mime.text import MIMEText

# ==========================================
# 0. LIVE EMAIL SYSTEM (OTP & LICENSE KEY)
# ==========================================
def send_real_email(receiver_email, subject, body_text):
    sender_email = "dhana6942@gmail.com"
    app_password = "zvhddripvstjwyef" 
    
    msg = MIMEText(body_text)
    msg['Subject'] = subject
    msg['From'] = f"Kulu Smart ERP <{sender_email}>"
    msg['To'] = receiver_email
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_db():
    conn = sqlite3.connect('kulu_erp_system.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, 
                 payment_status TEXT, approved INTEGER, aadhar TEXT, pan TEXT, gst TEXT, mobile TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS admin_settings
                 (id INTEGER PRIMARY KEY, upi_id TEXT, monthly_price REAL, yearly_price REAL, lifetime_price REAL, soft_gst REAL)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY, shop_email TEXT, item_name TEXT, purchase_price REAL, selling_price REAL, stock INTEGER, gst_rate REAL, barcode TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY, shop_email TEXT, date TEXT, item_name TEXT, qty INTEGER, total_price REAL, profit REAL, is_gst INTEGER, trans_type TEXT)''')
                 
    # Add new columns gracefully
    cols_to_add = [
        ("utr_no", "TEXT"), ("paid_amount", "REAL"), 
        ("package_type", "TEXT"), ("license_key", "TEXT"), 
        ("is_deleted", "INTEGER DEFAULT 0"), ("shop_photo", "BLOB"),
        ("expiry_date", "TEXT"), ("key_entered", "INTEGER DEFAULT 0"),
        ("upi_id", "TEXT") # Shop's personal UPI ID for bills
    ]
    for col, dtype in cols_to_add:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except: pass 
        
    admin_cols_to_add = [
        ("demo_price", "REAL DEFAULT 99.0"), 
        ("six_month_price", "REAL DEFAULT 2499.0"),
        ("notice_text", "TEXT DEFAULT 'Welcome to Kulu Smart ERP! Helpdesk: +91-XXXXX'")
    ]
    for col, dtype in admin_cols_to_add:
        try: c.execute(f"ALTER TABLE admin_settings ADD COLUMN {col} {dtype}")
        except: pass

    try: c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
    except: pass
    try: c.execute("ALTER TABLE transactions ADD COLUMN trans_type TEXT DEFAULT 'Sale'")
    except: pass

    c.execute("INSERT OR IGNORE INTO users (name, email, password, role, payment_status, approved, is_deleted) VALUES (?, ?, ?, ?, ?, ?, ?)",
              ('Super Admin', 'dhana6942@gmail.com', 'admin123', 'SuperAdmin', 'Paid', 1, 0))
              
    try:
        c.execute("UPDATE users SET role='SuperAdmin', password='admin123', approved=1, payment_status='Paid', is_deleted=0 WHERE email='dhana6942@gmail.com'")
        c.execute("UPDATE users SET email='dhana6942@gmail.com', password='admin123' WHERE email='admin@kulusutar.in' AND role='SuperAdmin'")
    except: pass
              
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

# 🔴 AUTO GENERATE DYNAMIC PAYMENT QR CODE FOR BILL 🔴
def generate_receipt_html(shop_name, item_name, qty, rate, gst, total_price, date_str, shop_upi=""):
    qr_html = ""
    if shop_upi:
        # Generate UPI intent link with exact amount
        upi_url = f"upi://pay?pa={shop_upi}&pn={shop_name}&am={total_price:.2f}&cu=INR"
        encoded_upi = urllib.parse.quote(upi_url)
        qr_img_src = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={encoded_upi}"
        qr_html = f"""
        <div class="center" style="margin-top: 15px;">
            <img src="{qr_img_src}" alt="Scan to Pay" width="90" height="90" style="border: 2px solid #000; padding: 2px;">
            <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Scan to Pay ₹ {total_price:.2f}</div>
        </div>
        """
        
    return f"""
    <html>
    <head>
    <style>
        @media print {{
            @page {{ margin: 0; size: 58mm auto; }}
            body {{ margin: 0; padding: 0; background: #fff; }}
            #print-btn {{ display: none; }}
        }}
        body {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; color: #000; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f4f4f4; padding: 20px; }}
        .receipt-box {{ width: 58mm; min-width: 220px; max-width: 100%; margin: 0 auto; padding: 10px; text-align: left; background: #fff; border: 1px solid #ccc; }}
        .center {{ text-align: center; }}
        .line {{ border-top: 1px dashed #000; margin: 8px 0; }}
        .bold {{ font-weight: bold; }}
        table {{ width: 100%; font-size: 12px; margin: 5px 0; border-collapse: collapse; }}
        .right {{ text-align: right; }}
        .btn {{ padding: 10px 20px; font-size: 16px; font-weight: bold; cursor: pointer; background: #28a745; color: white; border: none; border-radius: 5px; margin-top: 20px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }}
    </style>
    </head>
    <body>
        <div class="receipt-box">
            <div class="center bold" style="font-size: 16px;">{shop_name}</div>
            <div class="center" style="font-size: 10px; margin-bottom: 5px;">Retail Invoice / Cash Memo</div>
            <div class="center" style="font-size: 11px;">Date: {date_str}</div>
            <div class="line"></div>
            <div><span class="bold">Item:</span> {item_name}</div>
            <table>
                <tr><td>Qty: {qty}</td><td class="right">Rate: {rate}</td></tr>
                <tr><td>GST: {gst}%</td><td class="right"></td></tr>
            </table>
            <div class="line"></div>
            <div class="right bold" style="font-size: 15px;">Total: ₹ {total_price:.2f}</div>
            {qr_html}
            <div class="line"></div>
            <div class="center" style="font-size: 10px; margin-top: 5px;">Thank You! Visit Again.</div>
        </div>
        
        <div id="print-btn">
            <button class="btn" onclick="window.print()">
                🖨️ Print Receipt & QR Code
            </button>
            <br><br>
            <button onclick="window.parent.location.reload()" style="background: transparent; border: none; color: blue; text-decoration: underline; cursor: pointer;">
                Cancel / New Bill
            </button>
        </div>
    </body>
    </html>
    """

# ==========================================
# 2. PAGE CONFIG & ULTRA PREMIUM CSS
# ==========================================
st.set_page_config(page_title="Kulu Smart ERP", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .hero-container { background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #141E30); background-size: 400% 400%; animation: gradientBG 12s ease infinite; padding: 80px 20px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
    @keyframes gradientBG { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }
    .hero-title { font-size: 55px; font-weight: 900; margin-bottom: 15px; letter-spacing: 2px; text-transform: uppercase; text-shadow: 2px 2px 8px rgba(0,0,0,0.4); }
    .hero-subtitle { font-size: 22px; font-weight: 300; opacity: 0.9; letter-spacing: 1px; }
    
    /* Notice Board Marquee */
    .notice-board { background: #ffeb3b; color: #d32f2f; font-weight: bold; font-size: 18px; padding: 10px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    .feature-card { background: #ffffff; padding: 40px 25px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #f0f0f0; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); margin-bottom: 20px; height: 100%; }
    .feature-card:hover { transform: translateY(-15px); box-shadow: 0 20px 40px rgba(0,0,0,0.15); }
    .border-admin { border-top: 6px solid #FF416C; }
    .border-wholesale { border-top: 6px solid #4A00E0; }
    .border-shop { border-top: 6px solid #00b09b; }
    .card-icon { font-size: 65px; margin-bottom: 20px; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.1)); }
    .card-title { font-size: 26px; font-weight: 800; color: #1a1a1a; margin-bottom: 12px; }
    .card-text { font-size: 16px; color: #666; line-height: 1.6; font-weight: 400; margin-bottom: 20px; }
    .register-section { background: rgba(255, 255, 255, 0.5); border: 1px solid #eaeaea; padding: 40px; border-radius: 20px; text-align: center; margin-top: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
    .footer { text-align: center; margin-top: 80px; padding-top: 25px; border-top: 1px solid #eaeaea; color: #a0a0a0; font-size: 14px; font-weight: 500; letter-spacing: 1px; }
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
            st.title("👑 Super Admin Control Panel")
            tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Client Mgmt", "⚙️ Pricing & Notice", "♻️ Data Recovery", "🔐 Admin Profile"])
            
            with tab1:
                st.subheader("All Registered Clients")
                users = run_query("SELECT email, name, role, package_type, paid_amount, expiry_date, is_deleted FROM users WHERE role != 'SuperAdmin'")
                if users:
                    df = pd.DataFrame(users, columns=["Email", "Name", "Role", "Package", "Amount Paid", "Expiry Date", "Status"])
                    df["Status"] = df["Status"].apply(lambda x: "Suspended/Deleted" if x==1 else "Active")
                    st.dataframe(df, use_container_width=True)
                    
                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        app_email = st.selectbox("Select User Email to Suspend", [u[0] for u in users if u[6] == 0])
                        if st.button("🗑️ Suspend User"):
                            run_query("UPDATE users SET is_deleted=1 WHERE email=?", (app_email,))
                            st.success("User Suspended!"); st.rerun()
                else: st.info("No clients yet.")
                
            with tab2:
                st.subheader("⚙️ Set Payment, Prices & Notice Board")
                settings = run_query("SELECT upi_id, demo_price, monthly_price, six_month_price, yearly_price, lifetime_price, soft_gst, notice_text FROM admin_settings WHERE id=1")[0]
                
                with st.form("price_settings"):
                    n_notice = st.text_input("📢 Notice Board Text (Displays running on Home Page)", value=settings[7])
                    st.markdown("---")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        n_upi = st.text_input("Your UPI ID (For Payment)", value=settings[0])
                        n_demo = st.number_input("Demo (10 Days) Price ₹", value=float(settings[1]))
                    with c2:
                        n_mon = st.number_input("Monthly (30 Days) Price ₹", value=float(settings[2]))
                        n_six = st.number_input("6 Months (180 Days) Price ₹", value=float(settings[3]))
                    with c3:
                        n_yr = st.number_input("1 Year (365 Days) Price ₹", value=float(settings[4]))
                        n_life = st.number_input("Lifetime Price ₹", value=float(settings[5]))
                        n_gst = st.number_input("GST Rate %", value=float(settings[6]))
                        
                    if st.form_submit_button("Update Prices & Notice"):
                        run_query("UPDATE admin_settings SET upi_id=?, demo_price=?, monthly_price=?, six_month_price=?, yearly_price=?, lifetime_price=?, soft_gst=?, notice_text=? WHERE id=1",
                                  (n_upi, n_demo, n_mon, n_six, n_yr, n_life, n_gst, n_notice))
                        st.success("✅ Notice and Prices Updated Successfully!")
                        st.rerun()

            # 🔴 DATA RECOVERY TAB FOR ADMIN 🔴
            with tab3:
                st.subheader("♻️ Data Recovery / Recycle Bin")
                st.write("Restore client accounts that were deleted or suspended.")
                del_users = run_query("SELECT email, name, role FROM users WHERE is_deleted=1 AND role != 'SuperAdmin'")
                if del_users:
                    for d_u in del_users:
                        col1, col2 = st.columns([3, 1])
                        col1.error(f"🗑️ Name: {d_u[1]} | Role: {d_u[2]} | Email: {d_u[0]}")
                        if col2.button(f"♻️ Restore Account", key=f"res_{d_u[0]}"):
                            run_query("UPDATE users SET is_deleted=0 WHERE email=?", (d_u[0],))
                            st.success(f"✅ Account {d_u[1]} Restored Successfully!"); st.rerun()
                else: st.info("No deleted accounts found in Recycle Bin.")

            with tab4:
                st.subheader("🔐 Update Admin Profile")
                curr_admin = run_query("SELECT email, mobile, password FROM users WHERE email=?", (st.session_state.user_email,))[0]
                if "admin_update_step" not in st.session_state: st.session_state.admin_update_step = 1
                if st.session_state.admin_update_step == 1:
                    col1, col2 = st.columns(2)
                    with col1: new_email = st.text_input("New Email ID", value=curr_admin[0])
                    with col2: new_pass = st.text_input("New Password", type="password", value=curr_admin[2])
                    if st.button("📩 Send OTP to Confirm"):
                        st.session_state.admin_otp = str(random.randint(100000, 999999))
                        st.session_state.update_data = {"email": new_email, "pass": new_pass}
                        with st.spinner("Sending OTP..."):
                            success = send_real_email(st.session_state.user_email, "Profile Update OTP", f"Your OTP is {st.session_state.admin_otp}")
                        if success: st.session_state.admin_update_step = 2; st.rerun()
                        else: st.error("Error sending email.")
                elif st.session_state.admin_update_step == 2:
                    e_otp = st.text_input("Enter 6-digit OTP")
                    if st.button("Verify & Save"):
                        if e_otp == st.session_state.admin_otp:
                            d = st.session_state.update_data
                            run_query("UPDATE users SET email=?, password=? WHERE email=?", (d['email'], d['pass'], st.session_state.user_email))
                            st.session_state.user_email = d['email']
                            st.session_state.admin_update_step = 1; st.success("Updated!"); st.rerun()
                        else: st.error("Wrong OTP!")

        # ---------------- WHOLESALER & RETAIL SHOP (LICENSE CHECK FIRST) ----------------
        else:
            my_data = run_query("SELECT license_key, package_type, shop_photo, name, key_entered, expiry_date, upi_id, gst FROM users WHERE email=?", (st.session_state.user_email,))[0]
            db_key, pkg_type, shop_photo, shop_name, key_entered, exp_date, shop_upi, shop_gst = my_data
            
            if str(date.today()) > str(exp_date):
                st.error("❌ Your Software License has expired.")
                st.info(f"Expiry Date: {exp_date} | Package: {pkg_type}")
                st.stop()
                
            if not key_entered:
                st.title("🔐 Software License Activation")
                st.warning("Please enter your License Key to activate the software.")
                entered_key = st.text_input("🔑 Enter License Key:", placeholder="KULU-XXXXXXXXXXXX")
                if st.button("Activate Software", type="primary"):
                    if entered_key.strip() == db_key:
                        run_query("UPDATE users SET key_entered=1 WHERE email=?", (st.session_state.user_email,))
                        st.success("✅ Activated Successfully!")
                        st.balloons(); st.rerun()
                    else: st.error("❌ Invalid Key!")
                st.stop()
            
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<h2>📊 Gateway of Kulu ERP - {shop_name} ({st.session_state.user_role})</h2>', unsafe_allow_html=True)
            with c2: st.info(f"Valid Till: {exp_date}")
            
            # SETTING TABS
            if st.session_state.user_role == "Wholesaler":
                tab_dash, tab_purch, tab_sales, tab_net, tab_prof = st.tabs(["📈 Dash", "📥 Purchase", "🧾 Sales", "🏪 Network", "⚙️ Settings"])
            else:
                tab_dash, tab_purch, tab_sales, tab_prof = st.tabs(["📈 Dash", "📥 Purchase", "🧾 Sales", "⚙️ Settings"])
            
            with tab_dash:
                st.subheader("Financial Summary (Today)")
                today_str = str(date.today())
                sales_data = run_query("SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND date=? AND trans_type='Sale'", (st.session_state.user_email, today_str))[0][0]
                purch_data = run_query("SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND date=? AND trans_type='Purchase'", (st.session_state.user_email, today_str))[0][0]
                profit_data = run_query("SELECT SUM(profit) FROM transactions WHERE shop_email=? AND date=? AND trans_type='Sale'", (st.session_state.user_email, today_str))[0][0]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Sales", f"₹ {sales_data if sales_data else 0.0}")
                c2.metric("Total Purchases", f"₹ {purch_data if purch_data else 0.0}")
                c3.metric("Net Profit", f"₹ {profit_data if profit_data else 0.0}")

            with tab_purch:
                st.subheader("📥 Add Inventory (Purchase)")
                c1, c2, c3 = st.columns(3)
                with c1:
                    i_bcode = st.text_input("||||| Scan Barcode (Optional)", key="p_bcode")
                    i_name = st.text_input("Product Name", key="p_name")
                with c2:
                    i_qty = st.number_input("Qty", min_value=1, value=1, key="p_qty")
                    i_gst = st.number_input("GST %", min_value=0.0, value=18.0, key="p_gst")
                with c3:
                    i_pprice = st.number_input("Buy Rate (₹)", min_value=0.0, step=10.0, key="p_pprice")
                    auto_sell = i_pprice + (i_pprice * i_gst / 100)
                    i_sprice = st.number_input("Sell Rate (₹)", min_value=0.0, value=float(auto_sell), step=10.0, key="p_sprice")
                    
                if st.button("💾 Save Purchase", use_container_width=True) and i_name:
                    existing = run_query("SELECT id FROM inventory WHERE barcode=? AND shop_email=?", (i_bcode, st.session_state.user_email)) if i_bcode else []
                    if existing and i_bcode != "":
                        run_query("UPDATE inventory SET stock = stock + ?, purchase_price=?, selling_price=?, gst_rate=? WHERE id=?", (i_qty, i_pprice, i_sprice, i_gst, existing[0][0]))
                    else:
                        run_query("INSERT INTO inventory (shop_email, item_name, purchase_price, selling_price, stock, gst_rate, barcode) VALUES (?, ?, ?, ?, ?, ?, ?)", (st.session_state.user_email, i_name, i_pprice, i_sprice, i_qty, i_gst, i_bcode))
                    run_query("INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst, trans_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (st.session_state.user_email, str(date.today()), i_name, i_qty, i_pprice*i_qty, 0, 0, 'Purchase'))
                    st.success(f"✅ Purchase Saved!")

            with tab_sales:
                st.subheader("🧾 Sales POS (Auto QR Bill)")
                scan_code = st.text_input("🔍 SCAN BARCODE HERE...", key="s_scan")
                stock_items = run_query("SELECT id, item_name, selling_price, stock, purchase_price, gst_rate, barcode FROM inventory WHERE shop_email=? AND stock > 0", (st.session_state.user_email,))
                
                if stock_items:
                    item_dict = {f"{item[1]} - ₹{item[2]}": item for item in stock_items}
                    default_index = 0
                    if scan_code:
                        for idx, item in enumerate(stock_items):
                            if str(item[6]) == str(scan_code): default_index = idx; st.success(f"Barcode Matched: {item[1]}"); break
                    
                    sel_item = st.selectbox("Select Product", list(item_dict.keys()), index=default_index)
                    i_id, i_name, default_sprice, i_stock, i_pprice, def_gst, _ = item_dict[sel_item]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1: s_qty = st.number_input("Quantity", min_value=1, max_value=i_stock, value=1)
                    with col2: s_price = st.number_input("Rate (₹)", value=float(default_sprice))
                    with col3: s_gst = st.number_input("GST %", value=float(def_gst))
                    
                    is_gst_bill = st.checkbox("Calculate GST", value=True)
                    s_base = s_price * s_qty
                    s_final_price = (s_base + (s_base * s_gst / 100)) if is_gst_bill else s_base
                    profit = s_final_price - (i_pprice * s_qty)
                    st.write(f"**Total Payable:** ₹ {s_final_price:.2f}")

                    if st.button("🛒 Generate Sale Bill & Print", type="primary"):
                        if s_qty <= i_stock:
                            run_query("UPDATE inventory SET stock = stock - ? WHERE id=?", (s_qty, i_id))
                            run_query("INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst, trans_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                      (st.session_state.user_email, str(date.today()), i_name, s_qty, s_final_price, profit, 1 if is_gst_bill else 0, 'Sale'))
                            st.success(f"✅ Sale Recorded! Total: ₹ {s_final_price:.2f}")
                            
                            # GENERATE HTML RECEIPT WITH AUTO DYNAMIC UPI QR
                            st.session_state.print_receipt = generate_receipt_html(shop_name, i_name, s_qty, s_price, s_gst if is_gst_bill else 0, s_final_price, str(date.today()), shop_upi)
                        else: st.error("Not enough stock!")
                
                if "print_receipt" in st.session_state:
                    st.markdown("---")
                    st.subheader("🖨️ Bill Preview (With Payment QR)")
                    components.html(st.session_state.print_receipt, height=600)

            if st.session_state.user_role == "Wholesaler":
                with tab_net:
                    st.subheader("🏪 Live Retailer Stock Tracking")
                    r_stocks = run_query("SELECT u.name, u.email, i.item_name, i.stock, i.selling_price FROM inventory i JOIN users u ON i.shop_email = u.email WHERE u.role = 'Shop' AND i.stock > 0")
                    if r_stocks: st.dataframe(pd.DataFrame(r_stocks, columns=["Retail Shop", "Email", "Product", "Stock", "Price (₹)"]), use_container_width=True)
                    else: st.info("No stock data.")

            # 🔴 NEW SHOP/WHOLESALER PROFILE & GST/UPI SETTINGS 🔴
            with tab_prof:
                st.subheader("⚙️ Update Shop Profile & Payment Settings")
                st.info("ଏଠାରେ ଆପଣଙ୍କର ଦୋକାନର UPI ID ଦିଅନ୍ତୁ, ଯାହା ବିଲ୍ ରେ QR କୋଡ୍ ହୋଇ ବାହାରିବ!")
                with st.form("shop_profile_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_upi = st.text_input("Your Shop UPI ID (PhonePe/GPay)", value=shop_upi if shop_upi else "")
                    with c2:
                        new_gst = st.text_input("Your Shop GST No.", value=shop_gst if shop_gst else "")
                    
                    if st.form_submit_button("💾 Save Profile Settings"):
                        run_query("UPDATE users SET upi_id=?, gst=? WHERE email=?", (new_upi, new_gst, st.session_state.user_email))
                        st.success("✅ Profile Updated Successfully! Next bills will generate QR Code for this UPI ID.")
                        st.rerun()

else:
    # --- LOGGED OUT VIEWS (ULTRA PREMIUM DESIGN) ---
    if st.session_state.current_page == "Home Ground":
        
        # 🔴 RUNNING NOTICE BOARD FROM SUPER ADMIN 🔴
        settings = run_query("SELECT notice_text FROM admin_settings WHERE id=1")[0]
        notice_msg = settings[0] if settings[0] else "Welcome to Kulu Smart ERP!"
        
        st.markdown(f"""
        <div class="notice-board">
            <marquee behavior="scroll" direction="left" scrollamount="8">📢 {notice_msg}</marquee>
        </div>
        <div class="hero-container">
            <div class="hero-title">🚀 Kulu Smart ERP & POS</div>
            <div class="hero-subtitle">The Next-Generation Cloud Billing, Barcode & Inventory Management System</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="feature-card border-admin">
                <div class="card-icon">👑</div>
                <div class="card-title">Super Admin</div>
                <div class="card-text">Control software licensing, manage pricing packages, and secure global platform operations.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Secure Admin Login", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "SuperAdmin"
                st.rerun()
                
        with col2:
            st.markdown("""
            <div class="feature-card border-wholesale">
                <div class="card-icon">🏢</div>
                <div class="card-title">Wholesale Hub</div>
                <div class="card-text">Automate B2B billing, track live retailer network stocks, and maximize your supply chain profit.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Wholesaler Portal", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "Wholesaler"
                st.rerun()
                
        with col3:
            st.markdown("""
            <div class="feature-card border-shop">
                <div class="card-icon">🛒</div>
                <div class="card-title">Retail POS</div>
                <div class="card-text">Lightning-fast universal barcode scanning, instant thermal receipts, and real-time inventory.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Shop POS Login", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "Shop"
                st.rerun()
            
        st.markdown("""
        <div class="register-section">
            <h2 style='color: #1a1a1a; font-weight: 800; margin-bottom: 20px;'>Ready to transform your business?</h2>
            <p style='color: #666; font-size: 18px; margin-bottom: 30px;'>Join thousands of modern businesses using Kulu ERP today. Get instant license key delivery via Email.</p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("🚀 Buy Software License", use_container_width=True, type="primary"): 
                    st.session_state.current_page = "Register"
                    st.rerun()
            with cc2:
                if st.button("🔑 Password Recovery", use_container_width=True): 
                    st.session_state.current_page = "Forgot Password"
                    st.rerun()
                    
        st.markdown("<div class='footer'>© 2026 Kulu Smart Solutions Global. Engineered for Excellence.</div>", unsafe_allow_html=True)

    elif st.session_state.current_page == "Login":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title(f"🔐 {st.session_state.login_role} Login")
        l_email = st.text_input("Email Address")
        l_pass = st.text_input("Secure Password", type="password")
        
        if st.button("Login Securely", type="primary"):
            user = run_query("SELECT name, role, approved, is_deleted FROM users WHERE email=? AND password=?", (l_email, l_pass))
            if user:
                if user[0][3] == 1: st.error("❌ Your account has been Suspended or Deleted by Admin.")
                elif user[0][1] == st.session_state.login_role:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user[0][1]
                    st.session_state.user_email = l_email
                    st.rerun()
                else: st.error("❌ Role Mismatch.")
            else: st.error("Invalid Credentials.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"🔑 Forgot Password ({st.session_state.login_role})", use_container_width=False):
            st.session_state.current_page = "Forgot Password"
            st.rerun()

    elif st.session_state.current_page == "Register":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🛒 Buy Kulu ERP Software License")
        st.info("Payment କଲା ମାତ୍ରେ ଲାଇସେନ୍ସ କି (License Key) ଆପଣଙ୍କ ଇମେଲ୍ କୁ ତୁରନ୍ତ ପଠାଯିବ।")
        
        settings = run_query("SELECT upi_id, demo_price, monthly_price, six_month_price, yearly_price, lifetime_price, soft_gst FROM admin_settings WHERE id=1")[0]
        gst_pct = settings[6]
        
        packages = {
            f"Demo Plan (10 Days) - ₹{settings[1]}": ("Demo", settings[1], 10),
            f"Monthly Plan (30 Days) - ₹{settings[2]}": ("Monthly", settings[2], 30),
            f"6 Months Plan (180 Days) - ₹{settings[3]}": ("6 Months", settings[3], 180),
            f"1 Year Plan (365 Days) - ₹{settings[4]}": ("1 Year", settings[4], 365),
            f"Lifetime Plan (No Expiry) - ₹{settings[5]}": ("Lifetime", settings[5], 36500)
        }
        
        with st.form("reg_form"):
            r_role = st.selectbox("Registering As", ["Wholesaler", "Shop"])
            r_name = st.text_input("Business Name")
            r_email = st.text_input("Email ID (License Key will be sent here)")
            r_pass = st.text_input("Create Password", type="password")
            
            p_sel = st.radio("Select License Package", list(packages.keys()))
            pkg_name, pkg_price, pkg_days = packages[p_sel]
            
            total_with_gst = pkg_price + (pkg_price * gst_pct / 100)
            st.markdown(f"**Total Amount to Pay (Incl. GST): ₹ {total_with_gst:.2f}**")
            
            st.markdown(f"### 💳 Payment Gateway (Pay to UPI: `{settings[0]}`)")
            r_utr = st.text_input("Enter UTR / Transaction No. (Required)")
            
            if st.form_submit_button("Submit Payment & Get License"):
                if r_name and r_email and r_pass and r_utr:
                    new_key = generate_license()
                    exp_date = str(date.today() + timedelta(days=pkg_days))
                    
                    try:
                        run_query("INSERT INTO users (name, email, password, role, payment_status, approved, utr_no, paid_amount, package_type, license_key, expiry_date, key_entered) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (r_name, r_email, r_pass, r_role, 'Paid', 1, r_utr, total_with_gst, pkg_name, new_key, exp_date, 0))
                        st.success("✅ Payment Successful! Your License Key has been generated.")
                        
                        subject = f"Your Kulu ERP {pkg_name} License Key"
                        body = f"ନମସ୍କାର {r_name},\n\nଆପଣଙ୍କର Kulu Smart ERP ପ୍ୟାକେଜ୍ ({pkg_name}) ସଫଳତାର ସହ ରେଜିଷ୍ଟର୍ ହୋଇଛି!\n\n🔑 ଆପଣଙ୍କ License Key: {new_key}\n📅 Expiry Date: {exp_date}\n\nଦୟାକରି ସଫ୍ଟୱେର୍ ରେ ଲଗଇନ୍ କରି ଏହି କି (Key) ବ୍ୟବହାର କରି ଆକ୍ଟିଭେଟ୍ କରନ୍ତୁ।\n\nଧନ୍ୟବାଦ!"
                        with st.spinner("Emailing your license key..."): send_real_email(r_email, subject, body)
                        st.balloons(); st.info("📧 ଲାଇସେନ୍ସ କି ଆପଣଙ୍କ ଇମେଲ୍ କୁ ପଠାଯାଇଛି। ଦୟାକରି ଲଗଇନ୍ ପେଜ୍ କୁ ଯାଇ ନିଜ ଆକାଉଣ୍ଟ ଖୋଲନ୍ତୁ।")
                    except sqlite3.IntegrityError: st.error("❌ ଏହି Email ପୂର୍ବରୁ ରେଜିଷ୍ଟର୍ ହୋଇସାରିଛି!")
                else: st.warning("Please fill all details to complete payment.")

    elif st.session_state.current_page == "Forgot Password":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🔑 Reset Password (OTP)")
        if "forgot_step" not in st.session_state: st.session_state.forgot_step = 1
        
        if st.session_state.forgot_step == 1:
            f_email = st.text_input("Enter your Registered Email")
            if st.button("Send Real OTP to Email"):
                if run_query("SELECT email FROM users WHERE email=?", (f_email,)):
                    st.session_state.forgot_otp = str(random.randint(100000, 999999))
                    st.session_state.forgot_email = f_email
                    with st.spinner("Sending OTP to your email... Please wait."):
                        success = send_real_email(f_email, "Password Reset OTP", f"Your OTP is {st.session_state.forgot_otp}")
                    if success: st.session_state.forgot_step = 2; st.rerun()
                    else: st.error("❌ Email ପଠାଇବାରେ ଅସୁବିଧା ହେଲା! ଦୟାକରି ଇଣ୍ଟରନେଟ୍ କିମ୍ବା ଆପ୍ ପାସୱାର୍ଡ ଚେକ୍ କରନ୍ତୁ।")
                else: st.error("❌ ଏହି Email ଆମ ସିଷ୍ଟମ୍ ରେ ନାହିଁ।")
                    
        elif st.session_state.forgot_step == 2:
            st.success(f"📧 ରିଅଲ୍ OTP ଆପଣଙ୍କ {st.session_state.forgot_email} କୁ ପଠାଯାଇଛି! (Check Inbox/Spam)")
            e_otp = st.text_input("Enter 6-digit OTP")
            if st.button("Verify OTP"):
                if e_otp == st.session_state.forgot_otp: st.session_state.forgot_step = 3; st.rerun()
                else: st.error("❌ ଭୁଲ୍ OTP!")
                    
        elif st.session_state.forgot_step == 3:
            new_pass = st.text_input("Enter New Password", type="password")
            if st.button("Update Password") and new_pass:
                run_query("UPDATE users SET password=? WHERE email=?", (new_pass, st.session_state.forgot_email))
                st.success("✅ Password updated! Click 'Back to Home' to Login.")
                st.session_state.forgot_step = 1
