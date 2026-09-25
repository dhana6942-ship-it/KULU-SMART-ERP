import streamlit as st
import sqlite3
import pandas as pd
import random
import string
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
        ("expiry_date", "TEXT"), ("key_entered", "INTEGER DEFAULT 0")
    ]
    for col, dtype in cols_to_add:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except: pass 
        
    admin_cols_to_add = [("demo_price", "REAL DEFAULT 99.0"), ("six_month_price", "REAL DEFAULT 2499.0")]
    for col, dtype in admin_cols_to_add:
        try: c.execute(f"ALTER TABLE admin_settings ADD COLUMN {col} {dtype}")
        except: pass

    try: c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
    except: pass
    try: c.execute("ALTER TABLE transactions ADD COLUMN trans_type TEXT DEFAULT 'Sale'")
    except: pass

    # Super Admin Profile
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

# ==========================================
# 2. PAGE CONFIG & PREMIUM CSS
# ==========================================
st.set_page_config(page_title="Kulu Smart ERP", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .hero-container { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 50px 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }
    .hero-title { font-size: 48px; font-weight: 800; margin-bottom: 10px; letter-spacing: 1px; }
    .hero-subtitle { font-size: 20px; font-weight: 300; opacity: 0.9; }
    .feature-card { background: #ffffff; padding: 30px 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea; transition: transform 0.3s ease, box-shadow 0.3s ease; margin-bottom: 15px; height: 100%; }
    .feature-card:hover { transform: translateY(-8px); box-shadow: 0 12px 25px rgba(0,0,0,0.15); }
    .card-icon { font-size: 55px; margin-bottom: 15px; }
    .card-title { font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
    .card-text { font-size: 15px; color: #7f8c8d; line-height: 1.5; }
    .footer { text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid #eaeaea; color: #95a5a6; font-size: 14px; }
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
            tab1, tab2, tab3 = st.tabs(["🛡️ Client Management", "⚙️ License Pricing Setup", "🔐 Admin Profile"])
            
            with tab1:
                st.subheader("All Registered Clients")
                users = run_query("SELECT id, name, email, role, package_type, paid_amount, expiry_date, key_entered FROM users WHERE role != 'SuperAdmin' AND is_deleted=0")
                if users:
                    df = pd.DataFrame(users, columns=["ID", "Name", "Email", "Role", "Package", "Amount Paid", "Expiry Date", "Key Active?"])
                    df["Key Active?"] = df["Key Active?"].apply(lambda x: "Yes" if x==1 else "Pending")
                    st.dataframe(df, use_container_width=True)
                else: st.info("No active clients yet.")
                
            with tab2:
                st.subheader("⚙️ Set Payment Gateway & License Prices")
                st.info("ଏଠାରେ ଆପଣ ଲାଇସେନ୍ସ ଦାମ୍ (Price) ସେଟ୍ କରିପାରିବେ। ନୂଆ ଗ୍ରାହକ ଏହି ଦାମ୍ ଦେଖିବେ।")
                settings = run_query("SELECT upi_id, demo_price, monthly_price, six_month_price, yearly_price, lifetime_price, soft_gst FROM admin_settings WHERE id=1")[0]
                
                with st.form("price_settings"):
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
                        
                    if st.form_submit_button("Update Prices & Settings"):
                        run_query("UPDATE admin_settings SET upi_id=?, demo_price=?, monthly_price=?, six_month_price=?, yearly_price=?, lifetime_price=?, soft_gst=? WHERE id=1",
                                  (n_upi, n_demo, n_mon, n_six, n_yr, n_life, n_gst))
                        st.success("✅ Prices Updated Successfully!")
                        st.rerun()

            with tab3:
                st.subheader("🔐 Update Admin Profile")
                curr_admin = run_query("SELECT email, mobile, password FROM users WHERE email=?", (st.session_state.user_email,))[0]
                if "admin_update_step" not in st.session_state: st.session_state.admin_update_step = 1
                
                if st.session_state.admin_update_step == 1:
                    col1, col2 = st.columns(2)
                    with col1:
                        new_email = st.text_input("New Email ID", value=curr_admin[0])
                    with col2:
                        new_pass = st.text_input("New Password", type="password", value=curr_admin[2])
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
            my_data = run_query("SELECT license_key, package_type, shop_photo, name, key_entered, expiry_date FROM users WHERE email=?", (st.session_state.user_email,))[0]
            db_key = my_data[0]
            pkg_type = my_data[1]
            shop_name = my_data[3]
            key_entered = my_data[4]
            exp_date = my_data[5]
            
            # 🔴 CHECK IF LICENSE EXPIRED 🔴
            if str(date.today()) > str(exp_date):
                st.error("❌ ଧ୍ୟାନ ଦିଅନ୍ତୁ! ଆପଣଙ୍କ Software License ସରିଯାଇଛି (Expired)।")
                st.info(f"Expiry Date: {exp_date} | ଆପଣଙ୍କର ପୁରୁଣା ପ୍ୟାକେଜ୍: {pkg_type}")
                st.warning("ସଫ୍ଟୱେର୍ କୁ ପୁଣି ବ୍ୟବହାର କରିବା ପାଇଁ ଦୟାକରି Super Admin ଙ୍କ ସହ ଯୋଗାଯୋଗ କରନ୍ତୁ କିମ୍ବା ନୂଆ ପ୍ୟାକେଜ୍ କିଣନ୍ତୁ।")
                st.stop() # Stops loading the dashboard
                
            # 🔴 CHECK IF LICENSE KEY IS ENTERED 🔴
            if not key_entered:
                st.title("🔐 Software License Activation")
                st.warning("ସଫ୍ଟୱେର୍ ବ୍ୟବହାର କରିବା ପାଇଁ ଆପଣଙ୍କୁ License Key ଦେବାକୁ ପଡ଼ିବ।")
                st.info(f"ଆପଣ ରେଜିଷ୍ଟ୍ରେସନ୍ ସମୟରେ କିଣିଥିବା ({pkg_type}) ର License Key ଆପଣଙ୍କ ଇମେଲ୍ ID ({st.session_state.user_email}) କୁ ପଠାଯାଇଛି। ଦୟାକରି Gmail ଖୋଲି ଚେକ୍ କରନ୍ତୁ।")
                
                entered_key = st.text_input("🔑 Enter your License Key here:", placeholder="KULU-XXXXXXXXXXXX")
                
                if st.button("Activate My Software", type="primary"):
                    if entered_key.strip() == db_key:
                        run_query("UPDATE users SET key_entered=1 WHERE email=?", (st.session_state.user_email,))
                        st.success("✅ License Key Verified! Software Activated Successfully.")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ ଭୁଲ୍ ଲାଇସେନ୍ସ କି (Invalid License Key)! ଦୟାକରି ଇମେଲ୍ ଚେକ୍ କରନ୍ତୁ।")
                st.stop() # Stop here until key is verified
            
            # 🟢 IF LICENSE IS VALID & ENTERED, SHOW DASHBOARD 🟢
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<h2>📊 Gateway of Kulu ERP - {shop_name} ({st.session_state.user_role})</h2>', unsafe_allow_html=True)
            with c2: st.info(f"Valid Till: {exp_date}")
            
            # (Rest of the Wholesale/Retail Dashboards logic same as before)
            if st.session_state.user_role == "Wholesaler":
                tab_dash, tab_purch, tab_sales, tab_net = st.tabs(["📈 Dashboard", "📥 Purchase (Stock In)", "🧾 Sales (Stock Out)", "🏪 Retailer Network"])
            else:
                tab_dash, tab_purch, tab_sales = st.tabs(["📈 Dashboard", "📥 Purchase (Stock In)", "🧾 Sales (Stock Out)"])
            
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
                i_name = st.text_input("Product Name")
                i_qty = st.number_input("Purchase Quantity", min_value=1, value=1)
                i_pprice = st.number_input("Purchase Rate (₹)", min_value=0.0, step=10.0)
                i_sprice = st.number_input("Selling Rate (₹)", min_value=0.0, step=10.0)
                
                if st.button("💾 Save Purchase", use_container_width=True) and i_name:
                    run_query("INSERT INTO inventory (shop_email, item_name, purchase_price, selling_price, stock, gst_rate, barcode) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (st.session_state.user_email, i_name, i_pprice, i_sprice, i_qty, 0, ""))
                    run_query("INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst, trans_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (st.session_state.user_email, str(date.today()), i_name, i_qty, i_pprice*i_qty, 0, 0, 'Purchase'))
                    st.success(f"✅ Purchase Saved!")

            with tab_sales:
                st.subheader("🧾 Sales POS")
                stock_items = run_query("SELECT id, item_name, selling_price, stock, purchase_price FROM inventory WHERE shop_email=? AND stock > 0", (st.session_state.user_email,))
                if stock_items:
                    item_dict = {f"{item[1]} - ₹{item[2]} (Stock: {item[3]})": item for item in stock_items}
                    sel_item = st.selectbox("Select Product", list(item_dict.keys()))
                    i_id, i_name, default_sprice, i_stock, i_pprice = item_dict[sel_item]
                    s_qty = st.number_input("Quantity", min_value=1, max_value=i_stock, value=1)
                    
                    if st.button("🛒 Generate Sale Bill", type="primary"):
                        s_final_price = default_sprice * s_qty
                        profit = s_final_price - (i_pprice * s_qty)
                        run_query("UPDATE inventory SET stock = stock - ? WHERE id=?", (s_qty, i_id))
                        run_query("INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst, trans_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                  (st.session_state.user_email, str(date.today()), i_name, s_qty, s_final_price, profit, 0, 'Sale'))
                        st.success(f"✅ Sale Recorded! Total: ₹ {s_final_price:.2f}")

else:
    # --- LOGGED OUT VIEWS ---
    if st.session_state.current_page == "Home Ground":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">🚀 Kulu Smart ERP & POS</div>
            <div class="hero-subtitle">The Ultimate Cloud Billing, Barcode & Inventory Solution</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👑 Login as Admin", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "SuperAdmin"
                st.rerun()
        with col2:
            if st.button("🏢 Login as Wholesaler", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "Wholesaler"
                st.rerun()
        with col3:
            if st.button("🛒 Login as Shop", use_container_width=True): 
                st.session_state.current_page = "Login"
                st.session_state.login_role = "Shop"
                st.rerun()
            
        st.markdown("<br><hr>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🛒 Register / Buy License (Instant Access)", use_container_width=True, type="primary"): 
                st.session_state.current_page = "Register"
                st.rerun()

    elif st.session_state.current_page == "Login":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title(f"🔐 {st.session_state.login_role} Login")
        l_email = st.text_input("Email")
        l_pass = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            user = run_query("SELECT name, role, approved, is_deleted FROM users WHERE email=? AND password=?", (l_email, l_pass))
            if user:
                if user[0][1] == st.session_state.login_role:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user[0][1]
                    st.session_state.user_email = l_email
                    st.rerun()
                else: st.error("❌ Role Mismatch.")
            else: st.error("Invalid Credentials.")

    # 🔴 AUTOMATED PAYMENT GATEWAY & LICENSE GENERATION REGISTRATION 🔴
    elif st.session_state.current_page == "Register":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🛒 Buy Kulu ERP Software License")
        st.info("Payment କଲା ମାତ୍ରେ ଲାଇସେନ୍ସ କି (License Key) ସିଧା ଆପଣଙ୍କ ଇମେଲ୍ କୁ ପଠାଯିବ।")
        
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
                    # Auto Generate License & Expiry
                    new_key = generate_license()
                    exp_date = str(date.today() + timedelta(days=pkg_days))
                    
                    try:
                        # Auto-Approve directly after registration (Simulating Payment Gateway Success)
                        run_query("INSERT INTO users (name, email, password, role, payment_status, approved, utr_no, paid_amount, package_type, license_key, expiry_date, key_entered) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (r_name, r_email, r_pass, r_role, 'Paid', 1, r_utr, total_with_gst, pkg_name, new_key, exp_date, 0))
                        
                        st.success("✅ Payment Successful! Your License Key has been generated.")
                        
                        # Email the key
                        subject = f"Your Kulu ERP {pkg_name} License Key"
                        body = f"ନମସ୍କାର {r_name},\n\nଆପଣଙ୍କର Kulu Smart ERP ପ୍ୟାକେଜ୍ ({pkg_name}) ସଫଳତାର ସହ ରେଜିଷ୍ଟର୍ ହୋଇଛି!\n\n🔑 ଆପଣଙ୍କ License Key ହେଉଛି: {new_key}\n📅 Expiry Date: {exp_date}\n\nଦୟାକରି ସଫ୍ଟୱେର୍ ରେ ଲଗଇନ୍ କରି ଏହି କି (Key) ବ୍ୟବହାର କରି ଆକ୍ଟିଭେଟ୍ କରନ୍ତୁ।\n\nଧନ୍ୟବାଦ!"
                        
                        with st.spinner("Emailing your license key..."):
                            send_real_email(r_email, subject, body)
                            
                        st.balloons()
                        st.info("📧 ଲାଇସେନ୍ସ କି ଆପଣଙ୍କ ଇମେଲ୍ କୁ ପଠାଯାଇଛି। ଦୟାକରି ଲଗଇନ୍ ପେଜ୍ କୁ ଯାଇ ନିଜ ଆକାଉଣ୍ଟ ଖୋଲନ୍ତୁ।")
                        
                    except sqlite3.IntegrityError:
                        st.error("❌ ଏହି Email ପୂର୍ବରୁ ରେଜିଷ୍ଟର୍ ହୋଇସାରିଛି!")
                else: st.warning("Please fill all details to complete payment.")
