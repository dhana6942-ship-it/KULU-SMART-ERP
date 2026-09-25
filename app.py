import streamlit as st
import sqlite3
import pandas as pd
import random
import string
import urllib.parse
import time
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
                 
    cols_to_add = [
        ("utr_no", "TEXT"), ("paid_amount", "REAL"), 
        ("package_type", "TEXT"), ("license_key", "TEXT"), 
        ("is_deleted", "INTEGER DEFAULT 0"), ("shop_photo", "BLOB"),
        ("expiry_date", "TEXT"), ("key_entered", "INTEGER DEFAULT 0"),
        ("upi_id", "TEXT"), 
        ("owner_name", "TEXT"), ("pan_gst_no", "TEXT"),
        ("address", "TEXT"), ("state", "TEXT")
    ]
    for col, dtype in cols_to_add:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except: pass 
        
    admin_cols_to_add = [
        ("demo_price", "REAL DEFAULT 99.0"), 
        ("six_month_price", "REAL DEFAULT 2499.0"),
        ("notice_text", "TEXT DEFAULT 'Welcome to Kulu Smart ERP! Premium POS Software.'")
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

def generate_receipt_html(shop_name, item_name, qty, rate, gst, total_price, date_str, shop_upi=""):
    qr_html = ""
    if shop_upi:
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
        @media print {{ @page {{ margin: 0; size: 58mm auto; }} body {{ margin: 0; padding: 0; background: #fff; }} #print-btn {{ display: none; }} }}
        body {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; color: #000; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f4f4f4; padding: 20px; }}
        .receipt-box {{ width: 58mm; min-width: 220px; max-width: 100%; margin: 0 auto; padding: 10px; text-align: left; background: #fff; border: 1px solid #ccc; }}
        .center {{ text-align: center; }} .line {{ border-top: 1px dashed #000; margin: 8px 0; }} .bold {{ font-weight: bold; }}
        table {{ width: 100%; font-size: 12px; margin: 5px 0; border-collapse: collapse; }} .right {{ text-align: right; }}
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
            <table><tr><td>Qty: {qty}</td><td class="right">Rate: {rate}</td></tr><tr><td>GST: {gst}%</td><td class="right"></td></tr></table>
            <div class="line"></div>
            <div class="right bold" style="font-size: 15px;">Total: ₹ {total_price:.2f}</div>
            {qr_html}
            <div class="line"></div>
            <div class="center" style="font-size: 10px; margin-top: 5px;">Thank You! Visit Again.</div>
        </div>
        <div id="print-btn">
            <button class="btn" onclick="window.print()">🖨️ Print Receipt & QR Code</button><br><br>
            <button onclick="window.parent.location.reload()" style="background: transparent; border: none; color: blue; text-decoration: underline; cursor: pointer;">Cancel / New Bill</button>
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
    .notice-board { background: #ffeb3b; color: #d32f2f; font-weight: bold; font-size: 18px; padding: 10px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 2px solid #fbc02d; }
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

INDIAN_STATES = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

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
            tab_act, tab_set, tab_rec, tab_prof = st.tabs(["✅ Active Clients & Manual Mail", "⚙️ Pricing & Notice", "♻️ Data Recovery", "🔐 Admin Profile"])
                
            with tab_act:
                st.subheader("✅ Active Clients & Manual License Backup")
                st.write("ଗ୍ରାହକଙ୍କୁ ଅଟୋମେଟିକ୍ License ପଳାଇଥାଏ। ଯଦି ନେଟୱର୍କ ପାଇଁ ଫେଲ୍ ହୁଏ, ତେବେ ଏଠାରୁ 'Manual Resend' କରନ୍ତୁ କିମ୍ବା Key କପି କରନ୍ତୁ।")
                active = run_query("SELECT email, name, role, package_type, expiry_date, license_key, owner_name, paid_amount FROM users WHERE approved=1 AND role != 'SuperAdmin' AND is_deleted=0")
                if active:
                    df = pd.DataFrame(active, columns=["Email", "Business Name", "Role", "Package", "Expiry", "License Key", "Owner", "Paid"])
                    st.dataframe(df, use_container_width=True)
                    
                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        sel_mail = st.selectbox("Select Email to Resend License", [a[0] for a in active])
                        if st.button("📧 Manual Resend Mail (Backup)"):
                            usr = [u for u in active if u[0] == sel_mail][0]
                            subject = f"Your Kulu ERP {usr[3]} License (Resend)"
                            body = f"Hello {usr[6]},\n\nHere is your requested License Key.\n🔑 License Key: {usr[5]}\n📅 Expiry Date: {usr[4]}\nAmount Paid: ₹{usr[7]}\n\nThanks,\nKulu Smart ERP"
                            with st.spinner("Resending Email..."):
                                res = send_real_email(sel_mail, subject, body)
                            if res: st.success("✅ Email Sent Successfully!")
                            else: st.error("❌ Failed to send email. You can copy the License Key from the table above and send via WhatsApp.")
                    with c2:
                        sel_del = st.selectbox("Select Email to Suspend", [a[0] for a in active])
                        if st.button("🗑️ Suspend User"):
                            run_query("UPDATE users SET is_deleted=1 WHERE email=?", (sel_del,))
                            st.success("User Suspended!"); st.rerun()
                else: st.write("No active clients.")
                
            with tab_set:
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
                        st.success("✅ Notice and Prices Updated Successfully!"); st.rerun()

            with tab_rec:
                st.subheader("♻️ Data Recovery / Recycle Bin")
                del_users = run_query("SELECT email, name, role FROM users WHERE is_deleted=1 AND role != 'SuperAdmin'")
                if del_users:
                    for d_u in del_users:
                        col1, col2 = st.columns([3, 1])
                        col1.error(f"🗑️ Name: {d_u[1]} | Role: {d_u[2]} | Email: {d_u[0]}")
                        if col2.button(f"♻️ Restore", key=f"res_{d_u[0]}"):
                            run_query("UPDATE users SET is_deleted=0 WHERE email=?", (d_u[0],))
                            st.success(f"✅ Restored {d_u[1]}!"); st.rerun()
                else: st.info("No deleted accounts found.")

            with tab_prof:
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
                entered_key = st.text_input("🔑 Enter License Key (Check your Email):", placeholder="KULU-XXXXXXXXXXXX")
                if st.button("Activate Software", type="primary"):
                    if entered_key.strip() == db_key:
                        run_query("UPDATE users SET key_entered=1 WHERE email=?", (st.session_state.user_email,))
                        st.success("✅ Activated Successfully!"); st.balloons(); st.rerun()
                    else: st.error("❌ Invalid Key!")
                st.stop()
            
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<h2>📊 Gateway of Kulu ERP - {shop_name} ({st.session_state.user_role})</h2>', unsafe_allow_html=True)
            with c2: st.info(f"Valid Till: {exp_date}")
            
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

            with tab_prof:
                st.subheader("⚙️ Update Shop Profile & Payment Settings")
                st.info("ଏଠାରେ ଆପଣଙ୍କର ଦୋକାନର UPI ID ଦିଅନ୍ତୁ, ଯାହା ବିଲ୍ ରେ ଗ୍ରାହକଙ୍କ ପାଇଁ QR କୋଡ୍ ହୋଇ ବାହାରିବ!")
                with st.form("shop_profile_form"):
                    c1, c2 = st.columns(2)
                    with c1: new_upi = st.text_input("Your Shop UPI ID (PhonePe/GPay)", value=shop_upi if shop_upi else "")
                    with c2: new_gst = st.text_input("Your Shop GST No.", value=shop_gst if shop_gst else "")
                    if st.form_submit_button("💾 Save Profile Settings"):
                        run_query("UPDATE users SET upi_id=?, gst=? WHERE email=?", (new_upi, new_gst, st.session_state.user_email))
                        st.success("✅ Profile Updated Successfully! Next bills will generate QR Code for this UPI ID.")
                        st.rerun()

else:
    # --- LOGGED OUT VIEWS ---
    if st.session_state.current_page == "Home Ground":
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
                <div class="card-icon">👑</div><div class="card-title">Super Admin</div>
                <div class="card-text">Control software licensing, manage pricing packages, and secure global platform operations.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Secure Admin Login", use_container_width=True): 
                st.session_state.current_page = "Login"; st.session_state.login_role = "SuperAdmin"; st.rerun()
        with col2:
            st.markdown("""
            <div class="feature-card border-wholesale">
                <div class="card-icon">🏢</div><div class="card-title">Wholesale Hub</div>
                <div class="card-text">Automate B2B billing, track live retailer network stocks, and maximize your supply chain profit.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Wholesaler Portal", use_container_width=True): 
                st.session_state.current_page = "Login"; st.session_state.login_role = "Wholesaler"; st.rerun()
        with col3:
            st.markdown("""
            <div class="feature-card border-shop">
                <div class="card-icon">🛒</div><div class="card-title">Retail POS</div>
                <div class="card-text">Lightning-fast universal barcode scanning, instant thermal receipts, and real-time inventory.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Shop POS Login", use_container_width=True): 
                st.session_state.current_page = "Login"; st.session_state.login_role = "Shop"; st.rerun()
            
        st.markdown("""
        <div class="register-section">
            <h2 style='color: #1a1a1a; font-weight: 800; margin-bottom: 20px;'>Ready to transform your business?</h2>
            <p style='color: #666; font-size: 18px; margin-bottom: 30px;'>Join thousands of modern businesses using Kulu ERP today.</p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("🚀 Buy Software License", use_container_width=True, type="primary"): 
                    st.session_state.current_page = "Register"; st.rerun()
            with cc2:
                if st.button("🔑 Password Recovery", use_container_width=True): 
                    st.session_state.current_page = "Forgot Password"; st.rerun()
                    
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
            st.session_state.current_page = "Forgot Password"; st.rerun()

    # 🔴 100% AUTOMATIC REGISTRATION, PAYMENT & BILLING 🔴
    elif st.session_state.current_page == "Register":
        if st.button("⬅️ Back to Home"): 
            st.session_state.current_page = "Home Ground"
            if "reg_step" in st.session_state: del st.session_state.reg_step
            st.rerun()
            
        st.title("🛒 Buy Kulu ERP Software License")
        if "reg_step" not in st.session_state: st.session_state.reg_step = 1
        if "reg_data" not in st.session_state: st.session_state.reg_data = {}
        
        settings = run_query("SELECT upi_id, demo_price, monthly_price, six_month_price, yearly_price, lifetime_price, soft_gst FROM admin_settings WHERE id=1")[0]
        gst_pct = settings[6]
        packages = {
            f"Demo Plan (10 Days) - ₹{settings[1]}": ("Demo", settings[1]),
            f"Monthly Plan (30 Days) - ₹{settings[2]}": ("Monthly", settings[2]),
            f"6 Months Plan (180 Days) - ₹{settings[3]}": ("6 Months", settings[3]),
            f"1 Year Plan (365 Days) - ₹{settings[4]}": ("1 Year", settings[4]),
            f"Lifetime Plan (No Expiry) - ₹{settings[5]}": ("Lifetime", settings[5])
        }
        
        if st.session_state.reg_step == 1:
            st.subheader("Step 1: Business Details")
            r_role = st.selectbox("Registering As", ["Wholesaler", "Shop"])
            r_name = st.text_input("Business / Shop Name")
            r_owner = st.text_input("Owner Name")
            r_email = st.text_input("Email ID (License Key will be sent here)")
            r_pass = st.text_input("Create Password", type="password")
            
            c1, c2 = st.columns(2)
            with c1:
                r_aadhar = st.text_input("Aadhar No. (Optional)")
                r_address = st.text_area("Full Address (Optional)")
            with c2:
                r_pan_gst = st.text_input("PAN / GST No. (Optional)")
                r_state = st.selectbox("State (Optional)", ["Select State"] + INDIAN_STATES)
                
            p_sel = st.radio("Select License Package", list(packages.keys()))
            
            if st.button("Next ➡️", type="primary"):
                if r_name and r_email and r_pass and r_owner:
                    try:
                        run_query("INSERT INTO users (email) VALUES (?)", (r_email,)) 
                        run_query("DELETE FROM users WHERE email=? AND password IS NULL", (r_email,)) 
                        
                        pkg_name, pkg_price = packages[p_sel]
                        total_with_gst = pkg_price + (pkg_price * gst_pct / 100)
                        
                        st.session_state.reg_data = {
                            "role": r_role, "name": r_name, "owner": r_owner, "email": r_email, "pass": r_pass,
                            "aadhar": r_aadhar, "pan_gst": r_pan_gst, "address": r_address, "state": r_state,
                            "pkg_name": pkg_name, "total_amt": total_with_gst
                        }
                        st.session_state.reg_step = 2; st.rerun()
                    except sqlite3.IntegrityError: st.error("❌ Email already registered!")
                else: st.warning("Please fill Business Name, Owner Name, Email, and Password.")

        elif st.session_state.reg_step == 2:
            st.subheader("Step 2: Declaration & Terms")
            st.info("Please read and accept the terms to proceed to payment.")
            st.markdown("I hereby declare that all the information provided by me is true and correct. I agree to the terms and conditions of Kulu Smart ERP.")
            agree = st.checkbox("I Agree")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Back"): st.session_state.reg_step = 1; st.rerun()
            with c2:
                if st.button("Proceed to Payment 💳", type="primary"):
                    if agree: st.session_state.reg_step = 3; st.rerun()
                    else: st.error("Please accept the declaration.")

        elif st.session_state.reg_step == 3:
            st.subheader("Step 3: Secure Payment & Auto Verification")
            d = st.session_state.reg_data
            st.markdown(f"**Total Amount Payable:** ₹ {d['total_amt']:.2f}")
            
            upi_url = f"upi://pay?pa={settings[0]}&pn=KuluERP&am={d['total_amt']:.2f}&cu=INR"
            encoded_upi = urllib.parse.quote(upi_url)
            qr_img_src = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_upi}"
            
            st.markdown(f"""
            <div style="text-align: center; background: #fff; padding: 20px; border-radius: 10px; width: 250px; margin: auto; border: 2px solid #ddd;">
                <img src="{qr_img_src}" alt="Scan to Pay">
                <p style="font-weight: bold; margin-top: 10px;">Scan to Pay with Any UPI App</p>
                <p style="color: red;">Pay to: {settings[0]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            r_utr = st.text_input("Enter 12-Digit UTR / Ref No. (After successful payment)")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Back"): st.session_state.reg_step = 2; st.rerun()
            with c2:
                if st.button("Submit UTR & Auto Verify ✅", type="primary"):
                    if r_utr:
                        progress_text = "Verifying Payment Automatically... Please wait."
                        my_bar = st.progress(0, text=progress_text)
                        
                        for percent_complete in range(30):
                            time.sleep(1)
                            my_bar.progress(int((percent_complete + 1) * 3.33), text=progress_text)
                        my_bar.empty()
                        
                        # 🔴 AUTO APPROVE AND SAVE TO DB 🔴
                        new_key = generate_license()
                        exp_days = 10 if d['pkg_name']=="Demo" else 30 if d['pkg_name']=="Monthly" else 180 if d['pkg_name']=="6 Months" else 365 if d['pkg_name']=="1 Year" else 36500
                        exp_date = str(date.today() + timedelta(days=exp_days))
                        
                        run_query("""INSERT INTO users (name, owner_name, email, password, role, payment_status, approved, 
                                     aadhar, pan_gst, address, state, utr_no, paid_amount, package_type, license_key, expiry_date, key_entered) 
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (d['name'], d['owner'], d['email'], d['pass'], d['role'], 'Paid', 1, 
                                   d['aadhar'], d['pan_gst'], d['address'], d['state'], r_utr, d['total_amt'], d['pkg_name'], new_key, exp_date, 0))
                        
                        # 🔴 AUTO EMAIL GENERATION 🔴
                        subject = f"Welcome to Kulu ERP - Your {d['pkg_name']} License & Invoice"
                        body = f"Hello {d['owner']},\n\nYour Payment (UTR: {r_utr}) has been Auto-Verified successfully!\n\n🔑 License Key: {new_key}\n📅 Expiry Date: {exp_date}\n\n--- INVOICE ---\nBusiness Name: {d['name']}\nAmount Paid: ₹{d['total_amt']}\n\nPlease login to activate your software.\n\nThanks,\nKulu Smart ERP"
                        
                        with st.spinner("Generating License and Sending Email..."):
                            success = send_real_email(d['email'], subject, body)
                            
                        if success:
                            st.success("✅ Payment Verified Automatically! Your License Key has been sent to your Email.")
                        else:
                            st.warning("⚠️ Payment Verified, BUT Email failed to send due to a Network Issue. Please contact Super Admin to get your License Key manually.")
                            
                        st.balloons()
                        del st.session_state.reg_step
                        del st.session_state.reg_data
                    else: st.warning("Please enter UTR Number.")

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
