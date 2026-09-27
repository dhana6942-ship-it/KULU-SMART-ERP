import hashlib
import random
import smtplib
import string
import sqlite3
import time
import urllib.parse
from datetime import date, timedelta
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 0. SECURITY & EMAIL SYSTEM
# ==========================================
def hash_pass(password):
    return hashlib.sha256(str(password).encode()).hexdigest()

def send_real_email(receiver_email, subject, body_text):
    sender_email = "dhana6942@gmail.com"
    app_password = "zvhddripvstjwyef" 
    msg = MIMEText(body_text)
    msg['Subject'] = subject
    msg['From'] = f"Kulu Smart ERP <{sender_email}>"
    msg['To'] = receiver_email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# ==========================================
# 1. DATABASE SETUP (TOTAL 7 TABLES)
# ==========================================
def init_db():
    conn = sqlite3.connect('kulu_erp_system.db', timeout=20)
    conn.execute('PRAGMA journal_mode=WAL;')
    c = conn.cursor()
    
    # 1. Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, payment_status TEXT, approved INTEGER)''')
    
    # 2. Admin Settings Table
    c.execute('''CREATE TABLE IF NOT EXISTS admin_settings (id INTEGER PRIMARY KEY, upi_id TEXT, monthly_price REAL, yearly_price REAL, lifetime_price REAL, soft_gst REAL)''')
    
    # 3. Inventory Table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, shop_email TEXT, item_name TEXT, purchase_price REAL, selling_price REAL, stock INTEGER, gst_rate REAL, barcode TEXT)''')
    
    # 4. Transactions Table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, shop_email TEXT, date TEXT, item_name TEXT, qty INTEGER, total_price REAL, profit REAL, is_gst INTEGER, trans_type TEXT)''')

    # 5. Store Profiles
    c.execute('''CREATE TABLE IF NOT EXISTS store_profiles (id INTEGER PRIMARY KEY, shop_email TEXT UNIQUE, shop_name TEXT, contact_person TEXT, phone TEXT, address TEXT)''')

    # 6. Medical Wholesaler Table
    c.execute('''CREATE TABLE IF NOT EXISTS medical_wholesaler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_email TEXT,
        item_name TEXT,
        box_count INTEGER,
        strips_per_box INTEGER,
        tablets_per_strip INTEGER,
        purchase_price_box REAL,
        selling_price_box REAL,
        gst_rate REAL,
        barcode TEXT,
        updated_date TEXT
    )''')

    # 7. Medical Store Table
    c.execute('''CREATE TABLE IF NOT EXISTS medical_store (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_email TEXT,
        item_name TEXT,
        strips_count INTEGER,
        tablets_per_strip INTEGER,
        purchase_price_strip REAL,
        selling_price_strip REAL,
        gst_rate REAL,
        barcode TEXT,
        updated_date TEXT
    )''')
    
    cols_to_add = [
        ("utr_no", "TEXT"), ("paid_amount", "REAL"), ("package_type", "TEXT"), ("license_key", "TEXT"), 
        ("is_deleted", "INTEGER DEFAULT 0"), ("shop_photo", "BLOB"), ("expiry_date", "TEXT"), ("key_entered", "INTEGER DEFAULT 0"),
        ("upi_id", "TEXT"), ("owner_name", "TEXT"), ("pan_gst_no", "TEXT"), ("address", "TEXT"), ("state", "TEXT"),
        ("aadhar", "TEXT"), ("pan", "TEXT"), ("gst", "TEXT"), ("mobile", "TEXT")
    ]
    for col, dtype in cols_to_add:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except: pass 
        
    admin_cols_to_add = [
        ("demo_price", "REAL DEFAULT 99.0"), ("monthly_price", "REAL DEFAULT 499.0"), 
        ("six_month_price", "REAL DEFAULT 2499.0"), ("yearly_price", "REAL DEFAULT 4999.0"), 
        ("lifetime_price", "REAL DEFAULT 9999.0"), ("notice_text", "TEXT DEFAULT 'WELCOME TO KULU SMART ERP! PREMIUM POS SOFTWARE.'"), 
        ("home_banner", "BLOB")
    ]
    for col, dtype in admin_cols_to_add:
        try: c.execute(f"ALTER TABLE admin_settings ADD COLUMN {col} {dtype}")
        except: pass

    try: c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
    except: pass
    try: c.execute("ALTER TABLE transactions ADD COLUMN trans_type TEXT DEFAULT 'Sale'")
    except: pass
    
    tx_cols = [("customer_name", "TEXT"), ("customer_mobile", "TEXT"), ("invoice_no", "TEXT"), ("rate", "REAL"), ("gst_pct", "REAL"), ("gst_amt", "REAL DEFAULT 0")]
    for col, dtype in tx_cols:
        try: c.execute(f"ALTER TABLE transactions ADD COLUMN {col} {dtype}")
        except: pass

    admin_hash = hash_pass('admin123')
    c.execute("INSERT OR IGNORE INTO users (name, email, password, role, payment_status, approved, is_deleted) VALUES (?, ?, ?, ?, ?, ?, ?)", ('Super Admin', 'dhana6942@gmail.com', admin_hash, 'SuperAdmin', 'Paid', 1, 0))
    try:
        c.execute("UPDATE users SET role='SuperAdmin', password=?, approved=1, payment_status='Paid', is_deleted=0 WHERE email='dhana6942@gmail.com'", (admin_hash,))
    except: pass
    c.execute("INSERT OR IGNORE INTO admin_settings (id, upi_id, monthly_price, yearly_price, lifetime_price, soft_gst) VALUES (1, 'kulusutar@ybl', 499, 4999, 9999, 18)")
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=()):
    conn = sqlite3.connect('kulu_erp_system.db', timeout=20)
    conn.execute('PRAGMA journal_mode=WAL;')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    data = c.fetchall()
    conn.close()
    return data

def generate_license(): return "KULU-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

# 🔴 SALES RECEIPT HTML 🔴
def generate_receipt_html(shop_name, item_name, qty, rate, gst_pct, gst_amt, total_price, date_str, shop_upi="", cust_name="", cust_mob="", inv_no="", base_amt=0):
    qr_html = ""
    if shop_upi:
        safe_shop_name = urllib.parse.quote(shop_name)
        upi_url = f"upi://pay?pa={shop_upi}&pn={safe_shop_name}&am={total_price:.2f}&cu=INR"
        qr_img_src = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={urllib.parse.quote(upi_url)}"
        qr_html = f"""<div class="center" style="margin-top: 15px;"><img src="{qr_img_src}" alt="Scan to Pay" width="90" height="90" style="border: 2px solid #000; padding: 2px;"><div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Scan to Pay ₹ {total_price:.2f}</div></div>"""
    cust_info = f"""<div class="line"></div><div style="font-size: 11px; margin-bottom: 5px;"><b>Customer:</b> {cust_name.upper()}<br><b>Mob:</b> {cust_mob}</div>""" if cust_name or cust_mob else ""
    inv_info = f"<div class='center' style='font-size: 10px; margin-bottom: 5px;'>Inv No: {inv_no}</div>" if inv_no else ""
    gst_html = f"<tr><td>Base Amount:</td><td class='right'>₹ {base_amt:.2f}</td></tr><tr><td>GST ({gst_pct}%):</td><td class='right'>(+) ₹ {gst_amt:.2f}</td></tr>" if gst_pct > 0 else ""
    return f"""<html><head><style>@media print {{ @page {{ margin: 0; size: 58mm auto; }} body {{ margin: 0; padding: 0; background: #fff; }} #print-btn {{ display: none; }} }} body {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; color: #000; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f4f4f4; padding: 20px; }} .receipt-box {{ width: 58mm; min-width: 220px; max-width: 100%; margin: 0 auto; padding: 10px; text-align: left; background: #fff; border: 1px solid #ccc; }} .center {{ text-align: center; }} .line {{ border-top: 1px dashed #000; margin: 8px 0; }} .bold {{ font-weight: bold; }} table {{ width: 100%; font-size: 12px; margin: 5px 0; border-collapse: collapse; }} .right {{ text-align: right; }} .btn {{ padding: 10px 20px; font-size: 16px; font-weight: bold; cursor: pointer; background: #28a745; color: white; border: none; border-radius: 5px; margin-top: 20px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }}</style></head><body><div class="receipt-box"><div class="center bold" style="font-size: 16px;">{shop_name.upper()}</div><div class="center" style="font-size: 10px; margin-bottom: 5px;">Invoice / Cash Memo</div>{inv_info}<div class="center" style="font-size: 11px;">Date: {date_str}</div>{cust_info}<div class="line"></div><div><span class="bold">Item:</span> {item_name.upper()}</div><table><tr><td>Qty: {qty}</td><td class="right">Rate: ₹ {rate:.2f}</td></tr>{gst_html}</table><div class="line"></div><div class="right bold" style="font-size: 15px;">Total: ₹ {total_price:.2f}</div>{qr_html}<div class="line"></div><div class="center" style="font-size: 10px; margin-top: 5px;">Thank You! Visit Again.</div></div><div id="print-btn"><button class="btn" onclick="window.print()">🖨️ Print Receipt & QR Code</button><br><br></div></body></html>"""

# ==========================================
# 2. PAGE CONFIG & UI CSS
# ==========================================
st.set_page_config(page_title="Kulu Smart ERP", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stAppDeployButton, [data-testid="stAppDeployButton"], [data-testid="manage-app-button"] {display: none !important; visibility: hidden !important;}
    .stButton > button {
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
    }
    .stButton > button:hover {
        transform: translateY(-5px) scale(1.02) !important;
        box-shadow: 0 15px 25px rgba(0,0,0,0.15) !important;
    }
    .hero-container { 
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); 
        padding: 90px 20px; border-radius: 25px; color: white; text-align: center; 
        margin-bottom: 30px; box-shadow: 0 25px 50px rgba(0,0,0,0.3); border: 2px solid rgba(255,255,255,0.1); 
    }
    .hero-title { font-size: 60px; font-weight: 900; margin-bottom: 15px; letter-spacing: 3px; text-transform: uppercase; text-shadow: 3px 3px 10px rgba(0,0,0,0.5); }
    .hero-subtitle { font-size: 24px; font-weight: 300; opacity: 0.9; letter-spacing: 1.5px; }
    .notice-board { 
        background: linear-gradient(90deg, #ffeb3b, #fbc02d); color: #d32f2f; 
        font-weight: bold; font-size: 19px; padding: 12px; border-radius: 10px; 
        margin-bottom: 30px; box-shadow: 0 8px 15px rgba(0,0,0,0.1); border: 2px solid #f9a825; 
    }
    .feature-card { 
        background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
        padding: 40px 25px; border-radius: 20px; text-align: center; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.08); border: 1px solid rgba(0,0,0,0.05); 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); margin-bottom: 20px; height: 100%; 
    }
    .feature-card:hover { transform: translateY(-15px) scale(1.02); box-shadow: 0 25px 45px rgba(0,0,0,0.15); }
    .border-admin { border-top: 8px solid #ff0844; } 
    .border-wholesale { border-top: 8px solid #0052D4; } 
    .border-shop { border-top: 8px solid #11998e; }
    .border-med-ws { border-top: 8px solid #9c27b0; }
    .border-med-st { border-top: 8px solid #ff9800; }
    .card-icon { font-size: 65px; margin-bottom: 20px; filter: drop-shadow(3px 5px 8px rgba(0,0,0,0.15)); transition: transform 0.3s ease; }
    .card-title { font-size: 24px; font-weight: 800; color: #1a1a1a; margin-bottom: 12px; text-transform: uppercase;}
    .card-text { font-size: 15px; color: #555; line-height: 1.6; font-weight: 500; margin-bottom: 20px; }
    .register-section { 
        background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%); 
        padding: 50px 30px; border-radius: 20px; text-align: center; 
        margin-top: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.08); 
        border: 1px solid rgba(0,0,0,0.05); 
    }
    .footer { text-align: center; margin-top: 60px; padding-top: 25px; border-top: 1px solid #eaeaea; color: #999; font-size: 15px; font-weight: 600; letter-spacing: 1px; padding-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_page" not in st.session_state: st.session_state.current_page = "Home Ground"
if "login_role" not in st.session_state: st.session_state.login_role = None

INDIAN_STATES = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

# ==========================================
# 3. LOGGED IN PORTAL WORKFLOW
# ==========================================
if st.session_state.logged_in:
    head_c1, head_c2, head_c3 = st.columns([6, 2, 2])
    with head_c1:
        st.markdown(f"#### 👤 Logged in: **{st.session_state.user_email}** ({st.session_state.user_role})")
    with head_c2:
        if st.button("🏠 Home Page", key="top_home_btn", use_container_width=True):
            st.session_state.current_page = "Home Ground"
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.user_role = None
            st.rerun()
    with head_c3:
        if st.button("🚪 Logout", key="top_logout_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.user_role = None
            st.session_state.current_page = "Home Ground"
            st.rerun()

    st.markdown("---")

    st.sidebar.markdown(f"### ⚙️ {st.session_state.user_role} Portal")
    if st.sidebar.button("🏠 Go to Home Ground", use_container_width=True):
        st.session_state.current_page = "Home Ground"
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.rerun()
    if st.sidebar.button("🚪 Direct Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.session_state.current_page = "Home Ground"
        st.rerun()

    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Navigation", ["Gateway of ERP", "Logout"])
    if menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.session_state.current_page = "Home Ground"
        st.rerun()
        
    elif menu == "Gateway of ERP":
        if st.session_state.user_role == "SuperAdmin":
            admin_data = run_query("SELECT shop_photo FROM users WHERE email=?", (st.session_state.user_email,))[0]
            c1, c2 = st.columns([4, 1])
            with c1: st.title("👑 Super Admin Control Panel")
            with c2: 
                if admin_data[0]: st.image(admin_data[0], width=100)
                
            tab_act, tab_set, tab_rec, tab_prof = st.tabs(["✅ Active Clients", "⚙️ Pricing & Banner", "♻️ Data Recovery", "🔐 Admin Profile"])
                
            with tab_act:
                active = run_query("SELECT email, name, role, package_type, expiry_date, license_key, owner_name, paid_amount FROM users WHERE approved=1 AND role != 'SuperAdmin' AND is_deleted=0")
                if active:
                    st.dataframe(pd.DataFrame(active, columns=["Email", "Business Name", "Role", "Package", "Expiry", "License Key", "Owner", "Paid"]), use_container_width=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        sel_mail = st.selectbox("Select Email to Resend License", [a[0] for a in active])
                        if st.button("📧 Manual Resend Mail"):
                            usr = [u for u in active if u[0] == sel_mail][0]
                            if send_real_email(sel_mail, f"Your Kulu ERP {usr[3]} License (Resend)", f"Here is your requested License Key.\n🔑 License Key: {usr[5]}\n📅 Expiry Date: {usr[4]}\nAmount Paid: ₹{usr[7]}\n\nThanks,\nKulu Smart ERP"): st.success("✅ Email Sent!")
                            else: st.error("❌ Failed to send email.")
                    with c2:
                        sel_del = st.selectbox("Select Email to Suspend / Delete", [a[0] for a in active])
                        if st.button("🗑️ Suspend / Delete User"): 
                            run_query("UPDATE users SET is_deleted=1 WHERE email=?", (sel_del,))
                            st.success(f"User {sel_del} suspended successfully!"); st.rerun()
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
                        run_query("UPDATE admin_settings SET upi_id=?, demo_price=?, monthly_price=?, six_month_price=?, yearly_price=?, lifetime_price=?, soft_gst=?, notice_text=? WHERE id=1", (n_upi, n_demo, n_mon, n_six, n_yr, n_life, n_gst, n_notice)); st.success("✅ Updated!"); st.rerun()

            with tab_rec:
                del_users = run_query("SELECT email, name, role FROM users WHERE is_deleted=1 AND role != 'SuperAdmin'")
                if del_users:
                    for d_u in del_users:
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.error(f"{d_u[1]} ({d_u[0]}) - Role: {d_u[2]}")
                        if c2.button("♻️ Restore", key=f"res_{d_u[0]}"): 
                            run_query("UPDATE users SET is_deleted=0 WHERE email=?", (d_u[0],))
                            st.success("Account Restored!"); st.rerun()
                        if c3.button("❌ Permanent Delete", key=f"pdel_{d_u[0]}"): 
                            run_query("DELETE FROM users WHERE email=?", (d_u[0],))
                            st.warning("Account Permanently Deleted!"); st.rerun()
                else: st.info("No deleted accounts found in Recycle Bin.")

            with tab_prof:
                st.subheader("🛡️ Admin Profile & Database Backup")
                try:
                    with open('kulu_erp_system.db', 'rb') as f:
                        st.download_button("💾 Download Full Database Backup (.db)", f, file_name="kulu_erp_system_backup.db", type="primary")
                except Exception as e:
                    st.error("Backup file not found.")

                curr_admin = run_query("SELECT email, mobile, password FROM users WHERE email=?", (st.session_state.user_email,))[0]
                new_email = st.text_input("New Email ID", value=curr_admin[0])
                new_pass = st.text_input("New Password (will be encrypted)", type="password")
                if st.button("Update Profile"):
                    new_hash = hash_pass(new_pass) if new_pass else curr_admin[2]
                    run_query("UPDATE users SET email=?, password=? WHERE email=?", (new_email, new_hash, st.session_state.user_email))
                    st.session_state.user_email = new_email; st.success("Updated!"); st.rerun()

        elif st.session_state.user_role == "MedWholesale":
            st.title(f"🏢 Medical Wholesale Portal ({st.session_state.user_email})")
            tab_add, tab_view = st.tabs(["📥 Add Wholesale Medicine", "📦 Live Stock"])
            with tab_add:
                with st.form("med_ws_form"):
                    m_name = st.text_input("Medicine Name")
                    m_box = st.number_input("Boxes Count", min_value=1, value=10)
                    m_spb = st.number_input("Strips Per Box", min_value=1, value=200)
                    m_p_box = st.number_input("Buy Rate / Box (₹)", min_value=0.0, value=1000.0)
                    m_s_box = st.number_input("Sell Rate / Box (₹)", min_value=0.0, value=1200.0)
                    if st.form_submit_button("Save Wholesale Medicine"):
                        if m_name:
                            run_query("INSERT INTO medical_wholesaler (shop_email, item_name, box_count, strips_per_box, tablets_per_strip, purchase_price_box, selling_price_box, gst_rate, updated_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                      (st.session_state.user_email, m_name.strip().upper(), m_box, m_spb, 10, m_p_box, m_s_box, 12.0, str(date.today())))
                            st.success("✅ Saved to Wholesale Database!"); st.rerun()
            with tab_view:
                m_data = run_query("SELECT item_name, box_count, strips_per_box, purchase_price_box, selling_price_box FROM medical_wholesaler WHERE shop_email=?", (st.session_state.user_email,))
                if m_data: st.dataframe(pd.DataFrame(m_data, columns=["Medicine", "Boxes", "Strips/Box", "Buy/Box", "Sell/Box"]), use_container_width=True)

        elif st.session_state.user_role == "MedStore":
            st.title(f"💊 Medical Store Portal ({st.session_state.user_email})")
            tab_add, tab_view = st.tabs(["📥 Add Store Medicine", "📦 Pharmacy Live Stock"])
            with tab_add:
                with st.form("med_st_form"):
                    s_name = st.text_input("Medicine Name")
                    s_strips = st.number_input("Strips Count", min_value=1, value=50)
                    s_tps = st.number_input("Tablets per Strip", min_value=1, value=10)
                    s_p_strip = st.number_input("Buy Rate / Strip (₹)", min_value=0.0, value=40.0)
                    s_s_strip = st.number_input("Sell Rate / Strip (₹)", min_value=0.0, value=60.0)
                    if st.form_submit_button("Save Store Medicine"):
                        if s_name:
                            run_query("INSERT INTO medical_store (shop_email, item_name, strips_count, tablets_per_strip, purchase_price_strip, selling_price_strip, gst_rate, updated_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                      (st.session_state.user_email, s_name.strip().upper(), s_strips, s_tps, s_p_strip, s_s_strip, 12.0, str(date.today())))
                            st.success("✅ Saved to Store Database!"); st.rerun()
            with tab_view:
                st_data = run_query("SELECT item_name, strips_count, tablets_per_strip, purchase_price_strip, selling_price_strip FROM medical_store WHERE shop_email=?", (st.session_state.user_email,))
                if st_data: st.dataframe(pd.DataFrame(st_data, columns=["Medicine", "Strips", "Tablets/Strip", "Buy/Strip", "Sell/Strip"]), use_container_width=True)

        else:
            # ORIGINAL GROCERY / GENERAL SHOP
            st.title(f"📊 Dashboard ({st.session_state.user_role})")
            inv_data = run_query("SELECT item_name, stock, purchase_price, selling_price FROM inventory WHERE shop_email=?", (st.session_state.user_email,))
            if inv_data: st.dataframe(pd.DataFrame(inv_data, columns=["Item", "Stock", "Buy Rate", "Sell Rate"]), use_container_width=True)
            else: st.info("No items in stock. Add items from purchase.")

# ==========================================
# 4. HOME GROUND (TOTAL 7 BUTTONS) & FULL REGISTRATION FORM
# ==========================================
else:
    if st.session_state.current_page == "Home Ground":
        settings = run_query("SELECT notice_text, home_banner FROM admin_settings WHERE id=1")[0]
        st.markdown(f"""<div class="notice-board"><marquee behavior="scroll" direction="left" scrollamount="8">📢 {str(settings[0]).upper() if settings[0] else "WELCOME TO KULU SMART ERP!"}</marquee></div>""", unsafe_allow_html=True)
        if settings[1]: st.image(settings[1], use_container_width=True)
        else: st.markdown("""<div class="hero-container"><div class="hero-title">🚀 KULU SMART ERP & POS</div><div class="hero-subtitle">NEXT-GEN CLOUD BILLING, BARCODE & INVENTORY</div></div>""", unsafe_allow_html=True)
        
        # ROW 1: ORIGINAL 3 BUTTONS
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""<div class="feature-card border-admin"><div class="card-icon">👑</div><div class="card-title">Super Admin</div><div class="card-text">Control software licensing and global system settings.</div></div>""", unsafe_allow_html=True)
            if st.button("Secure Admin Login", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "SuperAdmin"
                st.rerun()
        with col2:
            st.markdown("""<div class="feature-card border-wholesale"><div class="card-icon">🏢</div><div class="card-title">Wholesale Hub</div><div class="card-text">Manage massive B2B sales and track retailer network.</div></div>""", unsafe_allow_html=True)
            if st.button("Wholesaler Portal", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "Wholesaler"
                st.rerun()
        with col3:
            st.markdown("""<div class="feature-card border-shop"><div class="card-icon">🛒</div><div class="card-title">Retail POS</div><div class="card-text">Lightning fast barcode billing & smart inventory tools.</div></div>""", unsafe_allow_html=True)
            if st.button("Shop POS Login", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "Shop"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ROW 2: 2 NEW MEDICINE BUTTONS
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown("""<div class="feature-card border-med-ws"><div class="card-icon">🏢</div><div class="card-title">Medicine Wholesaler</div><div class="card-text">Wholesale medicine cartons, boxes, packets & GST tracking.</div></div>""", unsafe_allow_html=True)
            if st.button("Medicine Wholesale Portal", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "MedWholesale"
                st.rerun()
        with m_col2:
            st.markdown("""<div class="feature-card border-med-st"><div class="card-icon">💊</div><div class="card-title">Medicine Store</div><div class="card-text">Counter medicine billing, strip & tablet POS calculations.</div></div>""", unsafe_allow_html=True)
            if st.button("Medicine Store Login", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "MedStore"
                st.rerun()
            
        # BOTTOM 2 BUTTONS
        st.markdown("""<div class="register-section"><h2 style='color: #1a1a1a; font-weight: 800; margin-bottom: 20px;'>READY TO TRANSFORM YOUR BUSINESS?</h2><p style='color: #666; font-size: 18px; margin-bottom: 30px;'>Join thousands of businesses using Kulu Smart ERP today.</p>""", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='footer'>© 2026 Kulu Smart Solutions Global. Engineered for Excellence.</div>", unsafe_allow_html=True)

    # 🟢 DIRECT LOGIN (NO OTP)
    elif st.session_state.current_page == "Login":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title(f"🔐 {st.session_state.login_role if st.session_state.login_role else ''} Login")
        l_email = st.text_input("Email Address (User ID)")
        l_pass = st.text_input("Secure Password", type="password")
        
        if st.button("Login", type="primary"):
            hash_attempt = hash_pass(l_pass)
            user = run_query("SELECT name, role, approved, is_deleted FROM users WHERE email=? AND password=?", (l_email.strip().lower(), hash_attempt))
            if user:
                if user[0][3] == 1: st.error("❌ Your account is Suspended. Please contact Admin.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user[0][1]
                    st.session_state.user_email = l_email.strip().lower()
                    st.rerun()
            else: st.error("Invalid Email or Password.")

    # 🟢 FULL REGISTRATION FORM RESTORED (ALL FIELDS INTACT)
    elif st.session_state.current_page == "Register":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🛒 Buy Kulu ERP License")
        settings = run_query("SELECT upi_id, demo_price, monthly_price, six_month_price, yearly_price, lifetime_price, soft_gst FROM admin_settings WHERE id=1")[0]
        packages = {
            f"Demo Plan (10 Days) - ₹{settings[1]}": ("Demo", settings[1]),
            f"Monthly Plan (1 Month) - ₹{settings[2]}": ("Monthly", settings[2]),
            f"6 Months Plan (6 Months) - ₹{settings[3]}": ("6 Months", settings[3]),
            f"1 Year Plan (1 Year) - ₹{settings[4]}": ("1 Year", settings[4]),
            f"Lifetime Plan (No Expiry) - ₹{settings[5]}": ("Lifetime", settings[5])
        }
        
        with st.form("reg_form"):
            r_role = st.selectbox("Register As", ["Shop", "Wholesaler", "MedStore", "MedWholesale"])
            raw_r_name = st.text_input("Business Name")
            raw_r_owner = st.text_input("Owner Name")
            r_mob = st.text_input("Mobile Number")
            r_email = st.text_input("Email ID (Used for Login)")
            r_pass = st.text_input("Password", type="password")
            
            c1, c2 = st.columns(2)
            with c1:
                r_aadhar = st.text_input("Aadhaar Number")
                raw_r_pan = st.text_input("PAN / GST Number")
            with c2:
                r_state = st.selectbox("State", INDIAN_STATES)
                raw_r_addr = st.text_area("Full Business Address")
                
            p_sel = st.radio("Select Package", list(packages.keys()))
            if st.form_submit_button("Next ➡️"):
                if raw_r_name and r_email and r_pass and r_mob:
                    pkg_name, pkg_price = packages[p_sel]
                    total_with_gst = pkg_price + (pkg_price * settings[6] / 100)
                    st.session_state.reg_data = {
                        "role": r_role,
                        "name": str(raw_r_name).strip().upper(),
                        "owner": str(raw_r_owner).strip().upper(),
                        "mobile": str(r_mob).strip(),
                        "email": str(r_email).strip().lower(),
                        "pass": str(r_pass),
                        "aadhar": str(r_aadhar).strip(),
                        "pan": str(raw_r_pan).strip().upper(),
                        "state": str(r_state),
                        "address": str(raw_r_addr).strip().upper(),
                        "pkg_name": pkg_name,
                        "total_amt": total_with_gst
                    }
                    st.session_state.current_page = "Payment"
                    st.rerun()
                else:
                    st.warning("⚠️ Please fill all required fields (Business Name, Email, Password, Mobile).")

    # 🟢 PAYMENT & UTR SUBMIT -> SHOW SUCCESS -> CLICK 'DONE' TO GO DIRECTLY TO LOGIN
    elif st.session_state.current_page == "Payment":
        # JADI PAYMENT SUCCESS HEISARICHI, TEBE KHALI SUCCESS SCREEN + 'DONE' BUTTON DEKHEIBA
        if "payment_done" in st.session_state:
            p_res = st.session_state.payment_done
            st.success("🎉 Payment Successfully Verified!")
            st.balloons()
            st.markdown(f"""
                <div style="background: #e8f5e9; border: 2px solid #2e7d32; padding: 25px; border-radius: 15px; margin: 25px 0; text-align: center;">
                    <h2 style="color: #2e7d32; margin-top:0;">✅ Payment Successful & License Activated!</h2>
                    <p style="font-size: 16px;"><b>Registered Business:</b> {p_res['name']}</p>
                    <p style="font-size: 16px;"><b>Login Email:</b> {p_res['email']}</p>
                    <div style="background: #fff; display: inline-block; padding: 12px 25px; border-radius: 8px; border: 2px dashed #d32f2f; margin: 15px 0;">
                        <span style="font-size: 14px; color: #555;">YOUR LICENSE KEY:</span><br>
                        <span style="font-size: 24px; font-weight: bold; color: #d32f2f;">{p_res['key']}</span>
                    </div>
                    <p style="font-size: 15px;"><b>📅 License Valid Till:</b> {p_res['exp']}</p>
                    <p style="font-size: 13px; color: #666;">(A confirmation email with your license key has also been dispatched)</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 🟢 DONE BUTTON: QLIK KALE DIRECT LOGIN SCREEN KU NEI ASIBA 🟢
            if st.button("✅ Done (Go to Login)", type="primary", use_container_width=True):
                # Clean up session and go straight to login
                target_role = p_res.get('role', 'Shop')
                del st.session_state.payment_done
                if "reg_data" in st.session_state:
                    del st.session_state.reg_data
                st.session_state.login_role = target_role
                st.session_state.current_page = "Login"
                st.rerun()

        # JADI PAYMENT HEINAHI, TEBE QR CODE AU UTR SUBMIT FORM DEKHEIBA
        else:
            d = st.session_state.reg_data
            admin_set = run_query("SELECT upi_id FROM admin_settings WHERE id=1")[0]
            admin_upi = admin_set[0] if admin_set[0] else "kulusutar@ybl"
            
            st.subheader("Step 3: Secure Payment")
            st.write(f"Total Amount to Pay: **₹ {d['total_amt']:.2f}**")
            
            safe_name = urllib.parse.quote("Kulu Smart ERP")
            upi_link = f"upi://pay?pa={admin_upi}&pn={safe_name}&am={d['total_amt']:.2f}&cu=INR"
            qr_src = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={urllib.parse.quote(upi_link)}"
            
            st.markdown(f"""
                <div style="text-align: center; background: #fff; padding: 20px; border-radius: 15px; border: 2px dashed #007bff; width: fit-content; margin: 0 auto 20px auto;">
                    <img src="{qr_src}" width="160" height="160" style="border-radius: 10px;">
                    <p style="margin-top: 10px; font-weight: bold; color: #333;">Scan & Pay via any UPI App</p>
                    <p style="color: #666; font-size: 14px;">UPI ID: <b>{admin_upi}</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            r_utr = st.text_input("Enter 12-Digit UTR No. / Transaction ID")
            if st.button("Submit & Verify UTR", type="primary", use_container_width=True):
                if r_utr.strip():
                    with st.spinner("⏳ Verifying UTR & Activating License..."):
                        time.sleep(2)
                    
                    new_key = generate_license()
                    days_map = {"Demo": 10, "Monthly": 30, "6 Months": 180, "1 Year": 365, "Lifetime": 36500}
                    exp_days = days_map.get(d['pkg_name'], 30)
                    exp_date = str(date.today() + timedelta(days=exp_days))
                    hash_new_pass = hash_pass(d['pass'])
                    
                    # DATABASE UPSERT
                    existing = run_query("SELECT id FROM users WHERE email=?", (d['email'],))
                    if existing:
                        run_query("""UPDATE users SET password=?, role=?, payment_status='Paid', approved=1, 
                                     utr_no=?, paid_amount=?, package_type=?, license_key=?, expiry_date=?, 
                                     key_entered=1, is_deleted=0, name=?, owner_name=?, mobile=?, aadhar=?, 
                                     pan=?, address=?, state=? WHERE email=?""",
                                  (hash_new_pass, d['role'], r_utr, d['total_amt'], d['pkg_name'], new_key, exp_date,
                                   d['name'], d['owner'], d['mobile'], d['aadhar'], d['pan'], d['address'], d['state'], d['email']))
                    else:
                        run_query("""INSERT INTO users (name, owner_name, email, password, role, payment_status, 
                                     approved, utr_no, paid_amount, package_type, license_key, expiry_date, 
                                     key_entered, mobile, aadhar, pan, address, state, is_deleted) 
                                     VALUES (?, ?, ?, ?, ?, 'Paid', 1, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, 0)""",
                                  (d['name'], d['owner'], d['email'], hash_new_pass, d['role'], r_utr, d['total_amt'],
                                   d['pkg_name'], new_key, exp_date, d['mobile'], d['aadhar'], d['pan'], d['address'], d['state']))
                    
                    send_real_email(d['email'], "Your Kulu ERP License Key", 
                                    f"Hello {d['name']},\n\nPayment Verified Successfully!\n🔑 License Key: {new_key}\n📅 Valid Till: {exp_date}\n\nThanks,\nKulu Smart ERP")
                    
                    st.session_state.payment_done = {
                        "name": d['name'],
                        "key": new_key,
                        "exp": exp_date,
                        "email": d['email'],
                        "role": d['role']
                    }
                    st.rerun()
                else:
                    st.error("⚠️ Please enter a valid 12-Digit UTR No.")

    elif st.session_state.current_page == "Forgot Password":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🔑 Password Recovery")
        f_email = st.text_input("Enter Registered Email ID")
        f_pass = st.text_input("Enter New Password", type="password")
        if st.button("Reset Password", type="primary"):
            if f_email and f_pass:
                user = run_query("SELECT id FROM users WHERE email=?", (f_email.strip().lower(),))
                if user:
                    run_query("UPDATE users SET password=? WHERE email=?", (hash_pass(f_pass), f_email.strip().lower()))
                    st.success("✅ Password updated successfully! Please login.")
                else: st.error("❌ Email ID not found.")
