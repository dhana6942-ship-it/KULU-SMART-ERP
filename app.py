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
        ("upi_id", "TEXT"), ("owner_name", "TEXT"), ("pan_gst_no", "TEXT"),
        ("address", "TEXT"), ("state", "TEXT")
    ]
    for col, dtype in cols_to_add:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except: pass 
        
    admin_cols_to_add = [
        ("demo_price", "REAL DEFAULT 99.0"), 
        ("six_month_price", "REAL DEFAULT 2499.0"),
        ("notice_text", "TEXT DEFAULT 'Welcome to Kulu Smart ERP! Premium POS Software.'"),
        ("home_banner", "BLOB")
    ]
    for col, dtype in admin_cols_to_add:
        try: c.execute(f"ALTER TABLE admin_settings ADD COLUMN {col} {dtype}")
        except: pass

    try: c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
    except: pass
    try: c.execute("ALTER TABLE transactions ADD COLUMN trans_type TEXT DEFAULT 'Sale'")
    except: pass
    
    tx_cols = [("customer_name", "TEXT"), ("customer_mobile", "TEXT"), ("invoice_no", "TEXT"), ("rate", "REAL"), ("gst_pct", "REAL")]
    for col, dtype in tx_cols:
        try: c.execute(f"ALTER TABLE transactions ADD COLUMN {col} {dtype}")
        except: pass 

    tx_cols2 = [("gst_amt", "REAL DEFAULT 0")]
    for col, dtype in tx_cols2:
        try: c.execute(f"ALTER TABLE transactions ADD COLUMN {col} {dtype}")
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

# 🔴 SIMPLIFIED GST RECEIPT GENERATOR 🔴
def generate_receipt_html(shop_name, item_name, qty, rate, gst_pct, gst_amt, total_price, date_str, shop_upi="", cust_name="", cust_mob="", inv_no="", base_amt=0):
    qr_html = ""
    if shop_upi:
        safe_shop_name = urllib.parse.quote(shop_name)
        upi_url = f"upi://pay?pa={shop_upi}&pn={safe_shop_name}&am={total_price:.2f}&cu=INR"
        encoded_upi = urllib.parse.quote(upi_url)
        qr_img_src = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={encoded_upi}"
        qr_html = f"""<div class="center" style="margin-top: 15px;"><img src="{qr_img_src}" alt="Scan to Pay" width="90" height="90" style="border: 2px solid #000; padding: 2px;"><div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Scan to Pay ₹ {total_price:.2f}</div></div>"""
        
    cust_info = ""
    if cust_name or cust_mob:
        cust_info = f"""<div class="line"></div><div style="font-size: 11px; margin-bottom: 5px;"><b>Customer:</b> {cust_name}<br><b>Mob:</b> {cust_mob}</div>"""
    inv_info = f"<div class='center' style='font-size: 10px; margin-bottom: 5px;'>Inv No: {inv_no}</div>" if inv_no else ""
    
    gst_html = ""
    if gst_pct > 0:
        gst_html = f"<tr><td>Base Amount:</td><td class='right'>₹ {base_amt:.2f}</td></tr><tr><td>GST ({gst_pct}%):</td><td class='right'>(+) ₹ {gst_amt:.2f}</td></tr>"
        
    return f"""
    <html><head><style>@media print {{ @page {{ margin: 0; size: 58mm auto; }} body {{ margin: 0; padding: 0; background: #fff; }} #print-btn {{ display: none; }} }} body {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; color: #000; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f4f4f4; padding: 20px; }} .receipt-box {{ width: 58mm; min-width: 220px; max-width: 100%; margin: 0 auto; padding: 10px; text-align: left; background: #fff; border: 1px solid #ccc; }} .center {{ text-align: center; }} .line {{ border-top: 1px dashed #000; margin: 8px 0; }} .bold {{ font-weight: bold; }} table {{ width: 100%; font-size: 12px; margin: 5px 0; border-collapse: collapse; }} .right {{ text-align: right; }} .btn {{ padding: 10px 20px; font-size: 16px; font-weight: bold; cursor: pointer; background: #28a745; color: white; border: none; border-radius: 5px; margin-top: 20px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }}</style></head>
    <body><div class="receipt-box"><div class="center bold" style="font-size: 16px;">{shop_name}</div><div class="center" style="font-size: 10px; margin-bottom: 5px;">Invoice / Cash Memo</div>{inv_info}<div class="center" style="font-size: 11px;">Date: {date_str}</div>{cust_info}<div class="line"></div><div><span class="bold">Item:</span> {item_name}</div><table><tr><td>Qty: {qty}</td><td class="right">Rate: ₹ {rate:.2f}</td></tr>{gst_html}</table><div class="line"></div><div class="right bold" style="font-size: 15px;">Total: ₹ {total_price:.2f}</div>{qr_html}<div class="line"></div><div class="center" style="font-size: 10px; margin-top: 5px;">Thank You! Visit Again.</div></div><div id="print-btn"><button class="btn" onclick="window.print()">🖨️ Print Receipt & QR Code</button><br><br></div></body></html>
    """

def generate_gst_report_html(df_gst, tot_gst, shop_name):
    rows = ""
    for _, r in df_gst.iterrows():
        rows += f"<tr><td>{r['Invoice']}</td><td>{r['Date']}</td><td>{r['Customer']}</td><td>₹{r['Base Value (₹)']:.2f}</td><td>{r['GST %']}%</td><td>₹{r['GST Amount (₹)']:.2f}</td><td>₹{r['Total Value (₹)']:.2f}</td></tr>"
        
    return f"""
    <html><head><style>body {{ font-family: Arial, sans-serif; padding: 20px; }} table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }} th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }} th {{ background-color: #f2f2f2; }} .header {{ text-align: center; margin-bottom: 30px; }} .summary {{ margin-top: 30px; padding: 15px; background: #eef9f1; border-radius: 8px; }} @media print {{ #print-btn {{ display: none; }} }}</style></head>
    <body>
        <div class="header"><h2>GST Sales & Liability Report</h2><h3>{shop_name}</h3><p>Report Generated on: {str(date.today())}</p></div>
        <button id="print-btn" onclick="window.print()" style="padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 5px;">🖨️ Print PDF for CA</button>
        <table><tr><th>Invoice No</th><th>Date</th><th>Customer</th><th>Base Value</th><th>GST Slab</th><th>GST Amount</th><th>Total Value</th></tr>{rows}</table>
        <div class="summary"><h3>Tax Liability Summary</h3><h4>Total GST Collected: ₹ {tot_gst:.2f}</h4></div>
    </body></html>
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
    .border-admin { border-top: 6px solid #FF416C; } .border-wholesale { border-top: 6px solid #4A00E0; } .border-shop { border-top: 6px solid #00b09b; }
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
        st.session_state.logged_in = False; st.session_state.user_email = None; st.session_state.user_role = None; st.session_state.current_page = "Home Ground"; st.rerun()
        
    elif menu == "Gateway of ERP":
        
        # ---------------- SUPER ADMIN ----------------
        if st.session_state.user_role == "SuperAdmin":
            admin_data = run_query("SELECT shop_photo FROM users WHERE email=?", (st.session_state.user_email,))[0]
            admin_photo = admin_data[0]
            
            c1, c2 = st.columns([4, 1])
            with c1: st.title("👑 Super Admin Control Panel")
            with c2: 
                if admin_photo: st.image(admin_photo, width=100)
                
            tab_act, tab_set, tab_rec, tab_prof = st.tabs(["✅ Active Clients", "⚙️ Pricing & Banner", "♻️ Data Recovery", "🔐 Admin Profile"])
                
            with tab_act:
                st.subheader("✅ Active Clients & Management")
                active = run_query("SELECT email, name, role, package_type, expiry_date, license_key, owner_name, paid_amount FROM users WHERE approved=1 AND role != 'SuperAdmin' AND is_deleted=0")
                if active:
                    df = pd.DataFrame(active, columns=["Email", "Business Name", "Role", "Package", "Expiry", "License Key", "Owner", "Paid"])
                    st.dataframe(df, use_container_width=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        sel_mail = st.selectbox("Select Email to Resend License", [a[0] for a in active])
                        if st.button("📧 Manual Resend Mail"):
                            usr = [u for u in active if u[0] == sel_mail][0]
                            subject = f"Your Kulu ERP {usr[3]} License (Resend)"
                            body = f"Hello {usr[6]},\n\nHere is your requested License Key.\n🔑 License Key: {usr[5]}\n📅 Expiry Date: {usr[4]}\nAmount Paid: ₹{usr[7]}\n\nThanks,\nKulu Smart ERP"
                            if send_real_email(sel_mail, subject, body): st.success("✅ Email Sent!")
                            else: st.error("❌ Failed to send email.")
                    with c2:
                        sel_del = st.selectbox("Select Email to Suspend", [a[0] for a in active])
                        if st.button("🗑️ Suspend User"):
                            run_query("UPDATE users SET is_deleted=1 WHERE email=?", (sel_del,)); st.success("Suspended!"); st.rerun()
                else: st.write("No active clients.")
                
            with tab_set:
                settings = run_query("SELECT upi_id, demo_price, monthly_price, six_month_price, yearly_price, lifetime_price, soft_gst, notice_text, home_banner FROM admin_settings WHERE id=1")[0]
                if settings[8]:
                    st.image(settings[8], use_container_width=True)
                    if st.button("🗑️ Delete Home Banner"): run_query("UPDATE admin_settings SET home_banner=NULL WHERE id=1"); st.rerun()
                new_banner = st.file_uploader("Upload New Home Banner", type=['jpg', 'png', 'jpeg'])
                if new_banner and st.button("💾 Save New Banner"): run_query("UPDATE admin_settings SET home_banner=? WHERE id=1", (new_banner.read(),)); st.success("Banner updated!"); st.rerun()
                
                with st.form("price_settings"):
                    n_notice = st.text_input("📢 Notice Board Text", value=settings[7])
                    c1, c2, c3 = st.columns(3)
                    with c1: n_upi = st.text_input("UPI ID", value=settings[0]); n_demo = st.number_input("Demo Price", value=float(settings[1]))
                    with c2: n_mon = st.number_input("Monthly Price", value=float(settings[2])); n_six = st.number_input("6 Months Price", value=float(settings[3]))
                    with c3: n_yr = st.number_input("1 Year Price", value=float(settings[4])); n_life = st.number_input("Lifetime Price", value=float(settings[5])); n_gst = st.number_input("GST %", value=float(settings[6]))
                    if st.form_submit_button("Update Prices"):
                        run_query("UPDATE admin_settings SET upi_id=?, demo_price=?, monthly_price=?, six_month_price=?, yearly_price=?, lifetime_price=?, soft_gst=?, notice_text=? WHERE id=1", (n_upi, n_demo, n_mon, n_six, n_yr, n_life, n_gst, n_notice))
                        st.success("✅ Updated Successfully!"); st.rerun()

            with tab_rec:
                st.subheader("♻️ Data Recovery")
                del_users = run_query("SELECT email, name, role FROM users WHERE is_deleted=1 AND role != 'SuperAdmin'")
                if del_users:
                    for d_u in del_users:
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.error(f"{d_u[1]} ({d_u[0]})")
                        if c2.button(f"♻️ Restore", key=f"res_{d_u[0]}"): run_query("UPDATE users SET is_deleted=0 WHERE email=?", (d_u[0],)); st.rerun()
                        if c3.button(f"❌ Delete", key=f"pdel_{d_u[0]}"): run_query("DELETE FROM users WHERE email=?", (d_u[0],)); st.rerun()
                else: st.info("No deleted accounts found.")

            with tab_prof:
                curr_admin = run_query("SELECT email, mobile, password FROM users WHERE email=?", (st.session_state.user_email,))[0]
                new_email = st.text_input("New Email ID", value=curr_admin[0])
                new_pass = st.text_input("New Password", type="password", value=curr_admin[2])
                if st.button("Update Profile"):
                    run_query("UPDATE users SET email=?, password=? WHERE email=?", (new_email, new_pass, st.session_state.user_email))
                    st.session_state.user_email = new_email; st.success("Updated!"); st.rerun()

        # ---------------- WHOLESALER & RETAIL SHOP ----------------
        else:
            my_data = run_query("SELECT license_key, package_type, shop_photo, name, key_entered, expiry_date, upi_id, gst, approved, state FROM users WHERE email=?", (st.session_state.user_email,))[0]
            db_key, pkg_type, shop_photo, shop_name, key_entered, exp_date, shop_upi, shop_gst, approved, shop_state = my_data
                
            if str(date.today()) > str(exp_date):
                st.error("❌ Your Software License has expired."); st.stop()
                
            if not key_entered:
                st.title("🔐 Software License Activation")
                entered_key = st.text_input("🔑 Enter License Key (Check your Email):", placeholder="KULU-XXXXXXXXXXXX")
                if st.button("Activate Software", type="primary"):
                    if entered_key.strip() == db_key: run_query("UPDATE users SET key_entered=1 WHERE email=?", (st.session_state.user_email,)); st.success("✅ Activated!"); st.balloons(); st.rerun()
                    else: st.error("❌ Invalid Key!")
                st.stop()
            
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<h2>📊 Gateway of Kulu ERP - {shop_name} ({st.session_state.user_role})</h2>', unsafe_allow_html=True)
            with c2: 
                if shop_photo: st.image(shop_photo, width=80)
                st.info(f"Valid Till: {exp_date}")
            
            if st.session_state.user_role == "Wholesaler":
                tab_dash, tab_purch, tab_sales, tab_hist, tab_gst_rep, tab_net, tab_prof = st.tabs(["📈 Dash", "📥 Purchase", "🧾 Sales POS", "🖨️ History", "📊 GST Reports", "🏪 Network", "⚙️ Settings"])
            else:
                tab_dash, tab_purch, tab_sales, tab_hist, tab_gst_rep, tab_prof = st.tabs(["📈 Dash", "📥 Purchase", "🧾 Sales POS", "🖨️ History", "📊 GST Reports", "⚙️ Settings"])
            
            with tab_dash:
                st.subheader("Financial Summary (Today)")
                today_str = str(date.today())
                sales_data = run_query("SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND date=? AND trans_type='Sale'", (st.session_state.user_email, today_str))[0][0]
                purch_data = run_query("SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND date=? AND trans_type='Purchase'", (st.session_state.user_email, today_str))[0][0]
                profit_data = run_query("SELECT SUM(profit) FROM transactions WHERE shop_email=? AND date=? AND trans_type='Sale'", (st.session_state.user_email, today_str))[0][0]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Sales", f"₹ {float(sales_data or 0):.2f}")
                c2.metric("Total Purchases", f"₹ {float(purch_data or 0):.2f}")
                c3.metric("Net Profit", f"₹ {float(profit_data or 0):.2f}")

            with tab_purch:
                st.subheader("📥 Add Inventory (Purchase)")
                c1, c2, c3 = st.columns(3)
                with c1: i_name = st.text_input("Product Name", key="p_name")
                with c2: i_qty = st.number_input("Qty", min_value=1, value=1, key="p_qty")
                with c3:
                    i_pprice = st.number_input("Buy Rate (₹)", min_value=0.0, step=10.0, key="p_pprice")
                    i_sprice = st.number_input("Sell Rate (₹)", min_value=0.0, value=float(i_pprice + (i_pprice*0.18)), step=10.0, key="p_sprice")
                    
                if st.button("💾 Save Purchase", use_container_width=True) and i_name:
                    run_query("INSERT INTO inventory (shop_email, item_name, purchase_price, selling_price, stock, gst_rate, barcode) VALUES (?, ?, ?, ?, ?, ?, ?)", (st.session_state.user_email, i_name, i_pprice, i_sprice, i_qty, 0, ""))
                    run_query("INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst, trans_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (st.session_state.user_email, str(date.today()), i_name, i_qty, i_pprice*i_qty, 0, 0, 'Purchase'))
                    st.success(f"✅ Purchase Saved!")

            with tab_sales:
                st.subheader("🧾 Sales POS (Manual GST Slab)")
                
                if "print_receipt" in st.session_state:
                    st.success("✅ Sale Recorded Successfully! Print your bill below.")
                    components.html(st.session_state.print_receipt, height=600)
                    st.markdown("---")
                    if st.button("➕ Create New Bill", type="primary"):
                        del st.session_state.print_receipt; st.rerun()
                else:
                    with st.expander("👤 Customer Details", expanded=True):
                        c1, c2 = st.columns(2)
                        with c1: cust_name = st.text_input("Customer Name")
                        with c2: cust_mob = st.text_input("Mobile Number")
                        
                    stock_items = run_query("SELECT id, item_name, selling_price, stock, purchase_price FROM inventory WHERE shop_email=? AND stock > 0", (st.session_state.user_email,))
                    if stock_items:
                        item_dict = {f"{item[1]} - ₹{item[2]}": item for item in stock_items}
                        sel_item = st.selectbox("Select Product", list(item_dict.keys()))
                        i_id, i_name, default_sprice, i_stock, i_pprice = item_dict[sel_item]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1: s_qty = st.number_input("Quantity", min_value=1, max_value=i_stock, value=1)
                        with col2: s_price = st.number_input("Rate (₹)", value=float(default_sprice))
                        with col3: 
                            gst_options = {"No GST (0%)": 0, "5% GST": 5, "12% GST": 12, "18% GST": 18, "28% GST": 28}
                            sel_gst_label = st.selectbox("Select GST Slab", list(gst_options.keys()))
                            s_gst_pct = gst_options[sel_gst_label]
                        
                        s_base = s_price * s_qty
                        
                        if s_gst_pct > 0:
                            gst_amt = (s_base * s_gst_pct) / 100
                            s_final_price = s_base + gst_amt
                            is_gst_bill = 1
                        else:
                            gst_amt = 0
                            s_final_price = s_base
                            is_gst_bill = 0
                            
                        profit = s_final_price - (i_pprice * s_qty)
                        
                        st.write(f"**Base Amount:** ₹{s_base:.2f} | **GST Amount:** ₹{gst_amt:.2f}")
                        st.write(f"### **Total Payable:** ₹ {s_final_price:.2f}")

                        if st.button("🛒 Generate Sale Bill & Print", type="primary"):
                            if s_qty <= i_stock:
                                inv_no = "INV-" + "".join(random.choices(string.digits, k=6))
                                run_query("UPDATE inventory SET stock = stock - ? WHERE id=?", (s_qty, i_id))
                                
                                run_query("""INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst, trans_type, customer_name, customer_mobile, invoice_no, rate, gst_pct, gst_amt) 
                                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                          (st.session_state.user_email, str(date.today()), i_name, s_qty, s_final_price, profit, is_gst_bill, 'Sale', cust_name, cust_mob, inv_no, s_price, s_gst_pct, gst_amt))
                                          
                                st.session_state.print_receipt = generate_receipt_html(
                                    shop_name, i_name, s_qty, s_price, s_gst_pct, gst_amt,
                                    s_final_price, str(date.today()), shop_upi, cust_name, cust_mob, inv_no, s_base
                                )
                                st.rerun()
                            else: st.error("Not enough stock!")

            with tab_hist:
                st.subheader("🖨️ Bill History & Reprint")
                history = run_query("SELECT invoice_no, date, customer_name, item_name, qty, rate, gst_pct, total_price, gst_amt, customer_mobile FROM transactions WHERE shop_email=? AND trans_type='Sale' ORDER BY id DESC LIMIT 50", (st.session_state.user_email,))
                if history:
                    history_clean = [h for h in history if h[0]]
                    if history_clean:
                        df_hist = pd.DataFrame(history_clean, columns=["Invoice No", "Date", "Customer", "Item", "Qty", "Rate", "GST %", "Total (₹)", "GST Amt", "Mob"])
                        st.dataframe(df_hist[["Invoice No", "Date", "Customer", "Item", "Total (₹)"]], use_container_width=True)
                        c1, c2 = st.columns([2, 1])
                        with c1: sel_inv = st.selectbox("🔍 Select Invoice to Reprint", [h[0] for h in history_clean])
                        with c2:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("🖨️ Reprint Selected Bill"):
                                bill = [h for h in history_clean if h[0] == sel_inv][0]
                                base_val = bill[5] * bill[4]
                                st.session_state.reprint_receipt = generate_receipt_html(shop_name, bill[3], bill[4], bill[5] or 0.0, bill[6] or 0.0, bill[8] or 0.0, bill[7], str(bill[1]), shop_upi, bill[2], bill[9], bill[0], base_val)
                                st.rerun()
                if "reprint_receipt" in st.session_state:
                    st.markdown("---")
                    st.success("✅ Bill Loaded for Reprint!")
                    components.html(st.session_state.reprint_receipt, height=600)
                    if st.button("❌ Close Reprint View"): del st.session_state.reprint_receipt; st.rerun()

            with tab_gst_rep:
                st.subheader("📊 GST Filing & Balance Sheet")
                st.write("ଏଠାରେ ଆପଣଙ୍କର ସମସ୍ତ GST ହିସାବ ଅଛି। ଆପଣ ଏହାକୁ Print କରି ନିଜର CA କୁ ଦେଇପାରିବେ।")
                
                gst_data = run_query("SELECT invoice_no, date, customer_name, total_price - gst_amt, gst_pct, gst_amt, total_price FROM transactions WHERE shop_email=? AND trans_type='Sale' AND is_gst=1", (st.session_state.user_email,))
                
                if gst_data:
                    df_gst = pd.DataFrame(gst_data, columns=["Invoice", "Date", "Customer", "Base Value (₹)", "GST %", "GST Amount (₹)", "Total Value (₹)"])
                    st.dataframe(df_gst, use_container_width=True)
                    
                    tot_gst = df_gst["GST Amount (₹)"].sum()
                    
                    st.metric("Total GST Collected (Payable)", f"₹ {tot_gst:.2f}")
                    st.markdown("---")
                    st.write("🖨️ **Print PDF for CA**")
                    pdf_html = generate_gst_report_html(df_gst, tot_gst, shop_name)
                    components.html(pdf_html, height=100)
                else:
                    st.info("No GST sales found yet.")

            if st.session_state.user_role == "Wholesaler":
                with tab_net:
                    st.subheader("🏪 Live Retailer Stock Tracking")
                    r_stocks = run_query("SELECT u.name, u.email, i.item_name, i.stock, i.selling_price FROM inventory i JOIN users u ON i.shop_email = u.email WHERE u.role = 'Shop' AND i.stock > 0")
                    if r_stocks: st.dataframe(pd.DataFrame(r_stocks, columns=["Retail Shop", "Email", "Product", "Stock", "Price (₹)"]), use_container_width=True)
                    else: st.info("No stock data.")

            with tab_prof:
                st.subheader("⚙️ Update Shop Profile & Settings")
                up_img = st.file_uploader("Upload Profile Photo", type=['jpg', 'png', 'jpeg'])
                if up_img and st.button("💾 Save Profile Photo"):
                    run_query("UPDATE users SET shop_photo=? WHERE email=?", (up_img.read(), st.session_state.user_email)); st.success("Photo updated!"); st.rerun()
                
                with st.form("shop_profile_form"):
                    c1, c2 = st.columns(2)
                    with c1: new_upi = st.text_input("Shop UPI ID", value=shop_upi if shop_upi else "")
                    with c2: new_gst = st.text_input("Shop GST No.", value=shop_gst if shop_gst else "")
                    if st.form_submit_button("💾 Save Settings"):
                        run_query("UPDATE users SET upi_id=?, gst=? WHERE email=?", (new_upi, new_gst, st.session_state.user_email)); st.success("✅ Profile Updated!"); st.rerun()

else:
    # --- LOGGED OUT VIEWS ---
    if st.session_state.current_page == "Home Ground":
        settings = run_query("SELECT notice_text, home_banner FROM admin_settings WHERE id=1")[0]
        notice_msg = settings[0] if settings[0] else "Welcome to Kulu Smart ERP!"
        banner_img = settings[1]
        
        st.markdown(f"""<div class="notice-board"><marquee behavior="scroll" direction="left" scrollamount="8">📢 {notice_msg}</marquee></div>""", unsafe_allow_html=True)
        if banner_img: st.image(banner_img, use_container_width=True)
        else: st.markdown("""<div class="hero-container"><div class="hero-title">🚀 Kulu Smart ERP & POS</div><div class="hero-subtitle">Next-Gen Cloud Billing, Barcode & Inventory</div></div>""", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""<div class="feature-card border-admin"><div class="card-icon">👑</div><div class="card-title">Super Admin</div></div>""", unsafe_allow_html=True)
            if st.button("Secure Admin Login", use_container_width=True): st.session_state.current_page = "Login"; st.session_state.login_role = "SuperAdmin"; st.rerun()
        with col2:
            st.markdown("""<div class="feature-card border-wholesale"><div class="card-icon">🏢</div><div class="card-title">Wholesale Hub</div></div>""", unsafe_allow_html=True)
            if st.button("Wholesaler Portal", use_container_width=True): st.session_state.current_page = "Login"; st.session_state.login_role = "Wholesaler"; st.rerun()
        with col3:
            st.markdown("""<div class="feature-card border-shop"><div class="card-icon">🛒</div><div class="card-title">Retail POS</div></div>""", unsafe_allow_html=True)
            if st.button("Shop POS Login", use_container_width=True): st.session_state.current_page = "Login"; st.session_state.login_role = "Shop"; st.rerun()
            
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("🚀 Buy License", use_container_width=True, type="primary"): st.session_state.current_page = "Register"; st.rerun()
            with cc2:
                if st.button("🔑 Password Recovery", use_container_width=True): st.session_state.current_page = "Forgot Password"; st.rerun()

    elif st.session_state.current_page == "Login":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title(f"🔐 {st.session_state.login_role} Login")
        l_email = st.text_input("Email Address")
        l_pass = st.text_input("Secure Password", type="password")
        if st.button("Login", type="primary"):
            user = run_query("SELECT name, role, approved, is_deleted FROM users WHERE email=? AND password=?", (l_email, l_pass))
            if user:
                if user[0][3] == 1: st.error("❌ Your account is Suspended.")
                elif user[0][1] == st.session_state.login_role:
                    st.session_state.logged_in = True; st.session_state.user_role = user[0][1]; st.session_state.user_email = l_email; st.rerun()
                else: st.error("❌ Role Mismatch.")
            else: st.error("Invalid Credentials.")

    elif st.session_state.current_page == "Register":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🛒 Buy Kulu ERP License")
        settings = run_query("SELECT upi_id, demo_price, monthly_price, six_month_price, yearly_price, lifetime_price, soft_gst FROM admin_settings WHERE id=1")[0]
        packages = {f"Demo Plan (10 Days) - ₹{settings[1]}": ("Demo", settings[1]), f"Lifetime Plan (No Expiry) - ₹{settings[5]}": ("Lifetime", settings[5])}
        
        with st.form("reg_form"):
            r_role = st.selectbox("Register As", ["Shop", "Wholesaler"])
            r_name = st.text_input("Business Name")
            r_email = st.text_input("Email ID")
            r_pass = st.text_input("Password", type="password")
            p_sel = st.radio("Select Package", list(packages.keys()))
            if st.form_submit_button("Next ➡️"):
                if r_name and r_email and r_pass:
                    pkg_name, pkg_price = packages[p_sel]
                    total_with_gst = pkg_price + (pkg_price * settings[6] / 100)
                    st.session_state.reg_data = {"role": r_role, "name": r_name, "owner": r_name, "email": r_email, "pass": r_pass, "pkg_name": pkg_name, "total_amt": total_with_gst}
                    st.session_state.current_page = "Payment"; st.rerun()

    elif st.session_state.current_page == "Payment":
        d = st.session_state.reg_data
        st.subheader("Step 3: Secure Payment")
        st.write(f"Total Amount: ₹ {d['total_amt']:.2f}")
        r_utr = st.text_input("Enter 12-Digit UTR No.")
        if st.button("Submit & Verify"):
            new_key = generate_license()
            exp_date = str(date.today() + timedelta(days=36500))
            run_query("""INSERT INTO users (name, owner_name, email, password, role, payment_status, approved, utr_no, paid_amount, package_type, license_key, expiry_date, key_entered) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (d['name'], d['owner'], d['email'], d['pass'], d['role'], 'Paid', 1, r_utr, d['total_amt'], d['pkg_name'], new_key, exp_date, 0))
            send_real_email(d['email'], "Your License Key", f"Key: {new_key}")
            st.success("✅ Payment Verified! Check Email for License Key."); st.balloons()
            
    elif st.session_state.current_page == "Forgot Password":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🔑 Reset Password")
        f_email = st.text_input("Registered Email")
        if st.button("Send OTP"):
            st.session_state.forgot_otp = "123456"; st.session_state.forgot_email = f_email
            send_real_email(f_email, "OTP", "OTP is 123456"); st.success("OTP Sent!")
