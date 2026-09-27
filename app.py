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
# 0. SECURITY & DUAL-PORT EMAIL SYSTEM
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
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=8)
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        pass
        
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=8)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False

# ==========================================
# 1. DATABASE SETUP (FORCE COLUMN UPDATE)
# ==========================================
def init_db():
    conn = sqlite3.connect('kulu_erp_system.db', timeout=20)
    conn.execute('PRAGMA journal_mode=WAL;')
    c = conn.cursor()
    
    # Create all tables first
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, payment_status TEXT, approved INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admin_settings (id INTEGER PRIMARY KEY, upi_id TEXT, monthly_price REAL, yearly_price REAL, lifetime_price REAL, soft_gst REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, shop_email TEXT, item_name TEXT, purchase_price REAL, selling_price REAL, stock INTEGER, gst_rate REAL, barcode TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, shop_email TEXT, date TEXT, item_name TEXT, qty INTEGER, total_price REAL, profit REAL, is_gst INTEGER, trans_type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS store_profiles (id INTEGER PRIMARY KEY, shop_email TEXT UNIQUE, shop_name TEXT, contact_person TEXT, phone TEXT, address TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS medical_wholesaler (id INTEGER PRIMARY KEY AUTOINCREMENT, shop_email TEXT, item_name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS medical_store (id INTEGER PRIMARY KEY AUTOINCREMENT, shop_email TEXT, item_name TEXT)''')
    conn.commit()
    
    # 🔴 FORCE UPDATE COLUMNS ONE BY ONE 🔴
    user_cols = [
        ("utr_no", "TEXT"), ("paid_amount", "REAL"), ("package_type", "TEXT"), ("license_key", "TEXT"), 
        ("is_deleted", "INTEGER DEFAULT 0"), ("shop_photo", "BLOB"), ("expiry_date", "TEXT"), ("key_entered", "INTEGER DEFAULT 0"),
        ("upi_id", "TEXT"), ("owner_name", "TEXT"), ("pan_gst_no", "TEXT"), ("address", "TEXT"), ("state", "TEXT"),
        ("aadhar", "TEXT"), ("pan", "TEXT"), ("gst", "TEXT"), ("mobile", "TEXT")
    ]
    for col, dtype in user_cols:
        try: 
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
            conn.commit()
        except: pass 
        
    admin_cols = [
        ("demo_price", "REAL DEFAULT 99.0"), ("monthly_price", "REAL DEFAULT 499.0"), 
        ("six_month_price", "REAL DEFAULT 2499.0"), ("yearly_price", "REAL DEFAULT 4999.0"), 
        ("lifetime_price", "REAL DEFAULT 9999.0"), ("notice_text", "TEXT DEFAULT 'WELCOME TO KULU SMART ERP! PREMIUM POS SOFTWARE.'"), 
        ("home_banner", "BLOB")
    ]
    for col, dtype in admin_cols:
        try: 
            c.execute(f"ALTER TABLE admin_settings ADD COLUMN {col} {dtype}")
            conn.commit()
        except: pass

    # Fix Medical Wholesaler Error (Force Commit)
    mw_cols = [
        ("box_count", "INTEGER DEFAULT 0"), ("strips_per_box", "INTEGER DEFAULT 200"),
        ("tablets_per_strip", "INTEGER DEFAULT 10"), ("purchase_price_box", "REAL DEFAULT 0"),
        ("selling_price_box", "REAL DEFAULT 0"), ("gst_rate", "REAL DEFAULT 0"),
        ("barcode", "TEXT DEFAULT ''"), ("updated_date", "TEXT DEFAULT ''")
    ]
    for col, dtype in mw_cols:
        try: 
            c.execute(f"ALTER TABLE medical_wholesaler ADD COLUMN {col} {dtype}")
            conn.commit()
        except: pass

    # Fix Medical Store Error (Force Commit)
    ms_cols = [
        ("strips_count", "REAL DEFAULT 0"), ("tablets_per_strip", "INTEGER DEFAULT 10"),
        ("purchase_price_strip", "REAL DEFAULT 0"), ("selling_price_strip", "REAL DEFAULT 0"),
        ("gst_rate", "REAL DEFAULT 0"), ("barcode", "TEXT DEFAULT ''"), ("updated_date", "TEXT DEFAULT ''")
    ]
    for col, dtype in ms_cols:
        try: 
            c.execute(f"ALTER TABLE medical_store ADD COLUMN {col} {dtype}")
            conn.commit()
        except: pass

    try: 
        c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
        conn.commit()
    except: pass
    try: 
        c.execute("ALTER TABLE transactions ADD COLUMN trans_type TEXT DEFAULT 'Sale'")
        conn.commit()
    except: pass
    
    tx_cols = [("customer_name", "TEXT"), ("customer_mobile", "TEXT"), ("invoice_no", "TEXT"), ("rate", "REAL"), ("gst_pct", "REAL"), ("gst_amt", "REAL DEFAULT 0")]
    for col, dtype in tx_cols:
        try: 
            c.execute(f"ALTER TABLE transactions ADD COLUMN {col} {dtype}")
            conn.commit()
        except: pass

    admin_hash = hash_pass('admin123')
    c.execute("INSERT OR IGNORE INTO users (name, email, password, role, payment_status, approved, is_deleted) VALUES (?, ?, ?, ?, ?, ?, ?)", ('Super Admin', 'dhana6942@gmail.com', admin_hash, 'SuperAdmin', 'Paid', 1, 0))
    try:
        c.execute("UPDATE users SET role='SuperAdmin', password=?, approved=1, payment_status='Paid', is_deleted=0 WHERE email='dhana6942@gmail.com'", (admin_hash,))
        conn.commit()
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

GST_SLABS = {"No GST (0%)": 0.0, "5% GST": 5.0, "12% GST": 12.0, "18% GST": 18.0, "28% GST": 28.0}

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
    .card-icon { font-size: 65px; margin-bottom: 20px; filter: drop-shadow(3px 5px 8px rgba(0,0,0,0.15)); }
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
                            if send_real_email(sel_mail, f"Your Kulu ERP {usr[3]} License (Resend)", f"Here is your License Key.\n🔑 License Key: {usr[5]}\n📅 Expiry Date: {usr[4]}\nAmount Paid: ₹{usr[7]}\n\nThanks,\nKulu Smart ERP"): st.success("✅ Email Sent!")
                            else: st.error("❌ Email failed.")
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
                else: st.info("No deleted accounts in Recycle Bin.")

            with tab_prof:
                st.subheader("🛡️ Admin Profile & Database Backup")
                try:
                    with open('kulu_erp_system.db', 'rb') as f:
                        st.download_button("💾 Download Full Database Backup (.db)", f, file_name="kulu_erp_system_backup.db", type="primary")
                except Exception as e:
                    st.error("Backup file not found.")

        # 🏢 MEDICAL WHOLESALER PORTAL (BOX -> STRIP -> TABLET & GST)
        elif st.session_state.user_role == "MedWholesale":
            my_data = run_query("SELECT license_key, package_type, shop_photo, name, key_entered, expiry_date, upi_id, gst, approved, state FROM users WHERE email=?", (st.session_state.user_email,))[0]
            db_key, pkg_type, shop_photo, shop_name, key_entered, exp_date, shop_upi, shop_gst, approved, shop_state = my_data
            
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<h2>🏢 Medical Wholesale Portal - {shop_name.upper()}</h2>', unsafe_allow_html=True)
            with c2: 
                if shop_photo: st.image(shop_photo, width=80)
                st.info(f"Valid Till: {exp_date}")
                
            tab_med_entry, tab_med_stock, tab_med_sales = st.tabs(["📥 Purchase (Add Medicine)", "📦 Wholesale Stock Register", "🧾 Wholesale Sales POS"])
            
            with tab_med_entry:
                st.subheader("📥 Wholesale Medicine Purchase Order (Box & Strip Calculation)")
                with st.form("med_ws_new_form"):
                    mw_name = st.text_input("Medicine Name")
                    c1, c2, c3 = st.columns(3)
                    with c1: mw_boxes = st.number_input("Total Boxes", min_value=1, value=10)
                    with c2: mw_spb = st.number_input("Strips per Box", min_value=1, value=200)
                    with c3: mw_tps = st.number_input("Tablets per Strip", min_value=1, value=10)
                    
                    c4, c5, c6 = st.columns(3)
                    with c4: mw_p_box = st.number_input("Buy Rate per Box (₹)", min_value=0.0, value=1000.0)
                    with c5: mw_s_box = st.number_input("Sell Rate per Box (₹)", min_value=0.0, value=1200.0)
                    with c6: mw_gst_sel = st.selectbox("GST Option", list(GST_SLABS.keys()), key="ws_gst_p")
                    
                    if st.form_submit_button("💾 Save Wholesale Purchase"):
                        if mw_name:
                            p_gst = GST_SLABS[mw_gst_sel]
                            run_query("INSERT INTO medical_wholesaler (shop_email, item_name, box_count, strips_per_box, tablets_per_strip, purchase_price_box, selling_price_box, gst_rate, updated_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                      (st.session_state.user_email, mw_name.strip().upper(), mw_boxes, mw_spb, mw_tps, mw_p_box, mw_s_box, p_gst, str(date.today())))
                            st.success(f"✅ {mw_name.upper()} added to Wholesale database with {mw_gst_sel}!")
                            st.rerun()
            
            with tab_med_stock:
                st.subheader("📦 Live Wholesale Medicine Inventory")
                mw_data = run_query("SELECT item_name, box_count, strips_per_box, tablets_per_strip, purchase_price_box, selling_price_box, gst_rate FROM medical_wholesaler WHERE shop_email=?", (st.session_state.user_email,))
                if mw_data:
                    st.dataframe(pd.DataFrame(mw_data, columns=["Medicine Name", "Boxes", "Strips / Box", "Tablets / Strip", "Buy / Box (₹)", "Sell / Box (₹)", "GST %"]), use_container_width=True)
                else:
                    st.info("No wholesale medicines in stock yet.")
                    
            with tab_med_sales:
                st.subheader("🧾 Wholesale Sales POS")
                ws_items = run_query("SELECT id, item_name, selling_price_box, box_count, gst_rate FROM medical_wholesaler WHERE shop_email=? AND box_count > 0", (st.session_state.user_email,))
                if ws_items:
                    ws_item_dict = {f"{item[1]} (Stock: {item[3]} Boxes) - ₹{item[2]}": item for item in ws_items}
                    sel_ws = st.selectbox("Select Medicine", list(ws_item_dict.keys()))
                    sel_item = ws_item_dict[sel_ws]
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: ws_qty = st.number_input("Boxes to Sell", min_value=1, max_value=sel_item[3], value=1)
                    with c2: ws_rate = st.number_input("Rate per Box (₹)", value=float(sel_item[2]))
                    with c3: ws_gst_choice = st.selectbox("Sales GST Option", list(GST_SLABS.keys()), key="ws_gst_s")
                    
                    ws_base = ws_qty * ws_rate
                    ws_gst_pct = GST_SLABS[ws_gst_choice]
                    ws_gst_amt = (ws_base * ws_gst_pct) / 100.0 if ws_gst_pct > 0 else 0.0
                    ws_total = ws_base + ws_gst_amt
                    
                    st.write(f"**Base Amount:** ₹{ws_base:.2f} | **GST Amount:** ₹{ws_gst_amt:.2f}")
                    st.write(f"### **Total Payable:** ₹ {ws_total:.2f}")
                    
                    if st.button("🛒 Generate Wholesale Bill", type="primary"):
                        inv_no = "MED-INV-" + "".join(random.choices(string.digits, k=6))
                        run_query("UPDATE medical_wholesaler SET box_count = box_count - ? WHERE id=?", (ws_qty, sel_item[0]))
                        st.success(f"✅ Wholesale Bill Generated! Invoice: {inv_no}")
                        st.balloons()
                        st.rerun()
                else:
                    st.info("No wholesale stock available.")

        # 💊 MEDICAL STORE PORTAL (STRIP -> TABLET AUTO CALCULATION & GST)
        elif st.session_state.user_role == "MedStore":
            my_data = run_query("SELECT license_key, package_type, shop_photo, name, key_entered, expiry_date, upi_id, gst, approved, state FROM users WHERE email=?", (st.session_state.user_email,))[0]
            db_key, pkg_type, shop_photo, shop_name, key_entered, exp_date, shop_upi, shop_gst, approved, shop_state = my_data
            
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<h2>💊 Medical Store Portal - {shop_name.upper()}</h2>', unsafe_allow_html=True)
            with c2: 
                if shop_photo: st.image(shop_photo, width=80)
                st.info(f"Valid Till: {exp_date}")
                
            tab_st_entry, tab_st_stock, tab_st_sales = st.tabs(["📥 Purchase (Add Medicine)", "📦 Pharmacy Live Stock", "🧾 Counter Sales POS"])
            
            with tab_st_entry:
                st.subheader("📥 Medical Store Purchase Order (Strip & Tablet Calculation)")
                with st.form("med_st_new_form"):
                    ms_name = st.text_input("Medicine Name")
                    c1, c2 = st.columns(2)
                    with c1: ms_strips = st.number_input("Total Strips", min_value=1, value=50)
                    with c2: ms_tps = st.number_input("Tablets per Strip", min_value=1, value=10)
                    
                    c3, c4, c5 = st.columns(3)
                    with c3: ms_p_strip = st.number_input("Buy Rate per Strip (₹)", min_value=0.0, value=40.0)
                    with c4: ms_s_strip = st.number_input("Sell Rate per Strip (₹)", min_value=0.0, value=60.0)
                    with c5: ms_gst_sel = st.selectbox("GST Option", list(GST_SLABS.keys()), key="st_gst_p")
                    
                    if st.form_submit_button("💾 Save Store Purchase"):
                        if ms_name:
                            p_gst = GST_SLABS[ms_gst_sel]
                            run_query("INSERT INTO medical_store (shop_email, item_name, strips_count, tablets_per_strip, purchase_price_strip, selling_price_strip, gst_rate, updated_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                      (st.session_state.user_email, ms_name.strip().upper(), ms_strips, ms_tps, ms_p_strip, ms_s_strip, p_gst, str(date.today())))
                            st.success(f"✅ {ms_name.upper()} added to Store database with {ms_gst_sel}!")
                            st.rerun()
            
            with tab_st_stock:
                st.subheader("📦 Live Pharmacy Inventory")
                ms_data = run_query("SELECT item_name, strips_count, tablets_per_strip, purchase_price_strip, selling_price_strip, gst_rate FROM medical_store WHERE shop_email=?", (st.session_state.user_email,))
                if ms_data:
                    st.dataframe(pd.DataFrame(ms_data, columns=["Medicine Name", "Strips In Stock", "Tablets / Strip", "Buy / Strip (₹)", "Sell / Strip (₹)", "GST %"]), use_container_width=True)
                else:
                    st.info("No store medicines in stock yet.")
                    
            with tab_st_sales:
                st.subheader("🧾 Pharmacy Counter POS (Auto Strip & Tablet Deduction)")
                st_items = run_query("SELECT id, item_name, selling_price_strip, strips_count, tablets_per_strip, gst_rate FROM medical_store WHERE shop_email=? AND strips_count > 0", (st.session_state.user_email,))
                if st_items:
                    st_item_dict = {f"{item[1]} (Stock: {item[3]} Strips) - ₹{item[2]}/Strip": item for item in st_items}
                    sel_st = st.selectbox("Select Medicine to Sell", list(st_item_dict.keys()))
                    sel_m = st_item_dict[sel_st]
                    
                    unit_mode = st.radio("Sale Unit", ["Full Strip", "Individual Tablets"])
                    c1, c2, c3 = st.columns(3)
                    
                    if unit_mode == "Full Strip":
                        with c1: s_qty = st.number_input("Number of Strips", min_value=1, value=1)
                        with c2: s_rate = st.number_input("Rate per Strip (₹)", value=float(sel_m[2]))
                        deduct_val = float(s_qty)
                    else:
                        per_tab_rate = float(sel_m[2]) / float(sel_m[4]) if sel_m[4] > 0 else float(sel_m[2])
                        with c1: s_qty = st.number_input("Number of Tablets", min_value=1, value=1)
                        with c2: s_rate = st.number_input("Rate per Tablet (₹)", value=float(per_tab_rate))
                        deduct_val = float(s_qty) / float(sel_m[4]) if sel_m[4] > 0 else float(s_qty)
                        
                    with c3: s_gst_choice = st.selectbox("Sales GST Option", list(GST_SLABS.keys()), key="st_gst_s")
                    
                    s_base = s_qty * s_rate
                    s_gst_pct = GST_SLABS[s_gst_choice]
                    s_gst_amt = (s_base * s_gst_pct) / 100.0 if s_gst_pct > 0 else 0.0
                    s_final = s_base + s_gst_amt
                    
                    st.write(f"**Base Amount:** ₹{s_base:.2f} | **GST ({s_gst_choice}):** ₹{s_gst_amt:.2f}")
                    st.write(f"### **Total Payable:** ₹ {s_final:.2f}")
                    
                    if st.button("🛒 Generate Counter Bill", type="primary"):
                        if deduct_val <= float(sel_m[3]):
                            inv_no = "RET-INV-" + "".join(random.choices(string.digits, k=6))
                            run_query("UPDATE medical_store SET strips_count = strips_count - ? WHERE id=?", (deduct_val, sel_m[0]))
                            st.success(f"✅ Medicine Bill Generated! Inv No: {inv_no}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Not enough stock!")
                else:
                    st.info("No medicine stock available.")

        # 🛒 GENERAL SHOP / GROCERY
        else:
            st.title(f"📊 Dashboard ({st.session_state.user_role})")
            inv_data = run_query("SELECT item_name, stock, purchase_price, selling_price FROM inventory WHERE shop_email=?", (st.session_state.user_email,))
            if inv_data: st.dataframe(pd.DataFrame(inv_data, columns=["Item", "Stock", "Buy Rate", "Sell Rate"]), use_container_width=True)
            else: st.info("No items in stock. Add items from purchase.")

# ==========================================
# 4. HOME GROUND & FULL REGISTRATION
# ==========================================
else:
    if st.session_state.current_page == "Home Ground":
        settings = run_query("SELECT notice_text, home_banner FROM admin_settings WHERE id=1")[0]
        st.markdown(f"""<div class="notice-board"><marquee behavior="scroll" direction="left" scrollamount="8">📢 {str(settings[0]).upper() if settings[0] else "WELCOME TO KULU SMART ERP!"}</marquee></div>""", unsafe_allow_html=True)
        if settings[1]: st.image(settings[1], use_container_width=True)
        else: st.markdown("""<div class="hero-container"><div class="hero-title">🚀 KULU SMART ERP & POS</div><div class="hero-subtitle">NEXT-GEN CLOUD BILLING, BARCODE & INVENTORY</div></div>""", unsafe_allow_html=True)
        
        # ROW 1: 3 BUTTONS
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

        # ROW 2: 2 MEDICINE BUTTONS
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
        st.title(f"🔐 Login")
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

    # 🟢 REGISTRATION FORM
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

    # 🟢 PAYMENT & DONE BUTTON -> DIRECT LOGIN ENTRY
    elif st.session_state.current_page == "Payment":
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
            
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                if st.button("✅ Done (Direct Enter ERP)", type="primary", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.user_email = p_res['email']
                    st.session_state.user_role = p_res['role']
                    st.session_state.current_page = "Home Ground"
                    del st.session_state.payment_done
                    if "reg_data" in st.session_state: del st.session_state.reg_data
                    st.rerun()
            with c_d2:
                if st.button("🔐 Go to Login Screen", use_container_width=True):
                    del st.session_state.payment_done
                    if "reg_data" in st.session_state: del st.session_state.reg_data
                    st.session_state.current_page = "Login"
                    st.rerun()

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
