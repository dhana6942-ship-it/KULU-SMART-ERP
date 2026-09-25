import streamlit as st
import sqlite3
import pandas as pd
import random
import string

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_db():
    conn = sqlite3.connect('kulu_erp_system.db')
    c = conn.cursor()
    
    # Users Table (Added shop_photo column)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, 
                 payment_status TEXT, approved INTEGER, aadhar TEXT, pan TEXT, gst TEXT, mobile TEXT,
                 utr_no TEXT, paid_amount REAL, package_type TEXT, license_key TEXT, is_deleted INTEGER DEFAULT 0, shop_photo BLOB)''')
                 
    # Admin Settings Table 
    c.execute('''CREATE TABLE IF NOT EXISTS admin_settings
                 (id INTEGER PRIMARY KEY, upi_id TEXT, monthly_price REAL, yearly_price REAL, lifetime_price REAL, soft_gst REAL)''')
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN utr_no TEXT")
        c.execute("ALTER TABLE users ADD COLUMN paid_amount REAL")
        c.execute("ALTER TABLE users ADD COLUMN package_type TEXT")
        c.execute("ALTER TABLE users ADD COLUMN license_key TEXT")
        c.execute("ALTER TABLE users ADD COLUMN is_deleted INTEGER DEFAULT 0")
        c.execute("ALTER TABLE users ADD COLUMN shop_photo BLOB")
    except:
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
st.set_page_config(page_title="Kulu ERP Master", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .card-admin { background-color: #ffebee; padding: 20px; border-radius: 10px; border-top: 5px solid #f44336; text-align: center; margin-bottom: 15px;}
    .card-whole { background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-top: 5px solid #2196f3; text-align: center; margin-bottom: 15px;}
    .card-shop { background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-top: 5px solid #4caf50; text-align: center; margin-bottom: 15px;}
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #333; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SESSION STATES
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_page" not in st.session_state: st.session_state.current_page = "Home Ground"
if "login_role" not in st.session_state: st.session_state.login_role = None
if "admin_update_step" not in st.session_state: st.session_state.admin_update_step = 1

# ==========================================
# 4. APP ROUTING
# ==========================================
if st.session_state.logged_in:
    menu = st.sidebar.radio("Navigation", ["My Dashboard", "Logout"])
    
    if menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.current_page = "Home Ground"
        st.rerun()
        
    elif menu == "My Dashboard":
        settings = run_query("SELECT upi_id, monthly_price, yearly_price, lifetime_price, soft_gst FROM admin_settings WHERE id=1")[0]
        
        # ---------------- SUPER ADMIN ----------------
        if st.session_state.user_role == "SuperAdmin":
            st.title("👑 Super Admin Control Panel")
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛡️ Client Approvals", "⚙️ Pricing & Settings", "♻️ Data Recovery", "🔐 Profile & Security", "🖼️ Shop Photos Control"])
            
            with tab1:
                st.subheader("Pending & Active Clients")
                users = run_query("SELECT id, name, email, role, package_type, utr_no, paid_amount, license_key, approved FROM users WHERE role != 'SuperAdmin' AND is_deleted=0")
                if users:
                    df = pd.DataFrame(users, columns=["ID", "Name", "Email", "Role", "Package", "UTR No", "Amount Paid", "License Key", "Status"])
                    df["Status"] = df["Status"].apply(lambda x: "Active" if x==1 else "Pending")
                    st.dataframe(df, use_container_width=True)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        app_email = st.selectbox("Select User Email", df['Email'])
                    with c2:
                        if st.button("✅ Approve & Generate License"):
                            new_key = generate_license()
                            run_query("UPDATE users SET approved=1, payment_status='Paid', license_key=? WHERE email=?", (new_key, app_email))
                            st.success(f"Approved! License Key: {new_key}")
                            st.rerun()
                    with c3:
                        if st.button("🗑️ Delete/Suspend User"):
                            run_query("UPDATE users SET is_deleted=1 WHERE email=?", (app_email,))
                            st.warning("User moved to Data Recovery.")
                            st.rerun()
                else:
                    st.info("No active or pending clients.")
            
            with tab2:
                st.subheader("Set Software Prices & Payment Details")
                with st.form("admin_settings"):
                    col1, col2 = st.columns(2)
                    with col1:
                        n_upi = st.text_input("Your UPI ID", value=settings[0])
                        n_mon = st.number_input("Monthly Package Price (₹)", value=float(settings[1]))
                        n_year = st.number_input("1 Year Package Price (₹)", value=float(settings[2]))
                    with col2:
                        n_life = st.number_input("Lifetime Package Price (₹)", value=float(settings[3]))
                        n_gst = st.number_input("GST on Software (%)", value=float(settings[4]))
                        
                    if st.form_submit_button("Update Settings"):
                        run_query("UPDATE admin_settings SET upi_id=?, monthly_price=?, yearly_price=?, lifetime_price=?, soft_gst=? WHERE id=1",
                                  (n_upi, n_mon, n_year, n_life, n_gst))
                        st.success("Software Pricing & Settings Updated!")
                        st.rerun()

            with tab3:
                st.subheader("♻️ Recover Deleted Accounts")
                del_users = run_query("SELECT email, name, role FROM users WHERE is_deleted=1")
                if del_users:
                    for d_u in del_users:
                        col1, col2 = st.columns([3, 1])
                        col1.write(f"🗑️ {d_u[1]} ({d_u[2]}) - {d_u[0]}")
                        if col2.button(f"Restore {d_u[0]}"):
                            run_query("UPDATE users SET is_deleted=0 WHERE email=?", (d_u[0],))
                            st.success("Account Restored Successfully!")
                            st.rerun()
                else:
                    st.info("Recycle Bin is empty. No deleted data.")

            with tab4:
                st.subheader("🔐 Update Admin ID & Password")
                curr_admin = run_query("SELECT email, mobile, password FROM users WHERE email=?", (st.session_state.user_email,))[0]
                
                if st.session_state.admin_update_step == 1:
                    col1, col2 = st.columns(2)
                    with col1:
                        new_email = st.text_input("New Email ID", value=curr_admin[0])
                        new_mobile = st.text_input("New Mobile No.", value=curr_admin[1] if curr_admin[1] else "")
                    with col2:
                        new_pass = st.text_input("New Password", type="password", value=curr_admin[2])
                        
                    if st.button("📩 Send OTP to Confirm Changes"):
                        st.session_state.admin_otp = str(random.randint(100000, 999999))
                        st.session_state.update_data = {"email": new_email, "mobile": new_mobile, "pass": new_pass}
                        st.session_state.admin_update_step = 2
                        st.rerun()
                        
                elif st.session_state.admin_update_step == 2:
                    st.success(f"📧 EMAIL SENT! (Mock Test OTP: **{st.session_state.admin_otp}** )")
                    e_otp = st.text_input("Enter 6-digit OTP")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Verify & Save Changes"):
                            if e_otp == st.session_state.admin_otp:
                                d = st.session_state.update_data
                                try:
                                    run_query("UPDATE users SET email=?, mobile=?, password=? WHERE email=?", 
                                              (d['email'], d['mobile'], d['pass'], st.session_state.user_email))
                                    st.success("🎉 Profile & Password Updated Successfully!")
                                    st.session_state.user_email = d['email']
                                    st.session_state.admin_update_step = 1
                                    st.rerun()
                                except sqlite3.IntegrityError:
                                    st.error("❌ ଏହି ଇମେଲ୍ ID ପୂର୍ବରୁ ରେଜିଷ୍ଟର୍ ହୋଇଛି! ଏକ ନୂଆ ଇମେଲ୍ ଦିଅନ୍ତୁ।")
                            else:
                                st.error("❌ Invalid OTP.")
                    with c2:
                        if st.button("🚫 Cancel"):
                            st.session_state.admin_update_step = 1
                            st.rerun()

            # NEW: SUPER ADMIN PHOTO CONTROL
            with tab5:
                st.subheader("🖼️ Master Control: Shop Photos")
                st.write("View and manage profile photos uploaded by your clients.")
                clients_with_photos = run_query("SELECT email, name, role, shop_photo FROM users WHERE role != 'SuperAdmin' AND is_deleted=0 AND shop_photo IS NOT NULL")
                if clients_with_photos:
                    for cl in clients_with_photos:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.image(cl[3], width=120)
                        with col2:
                            st.write(f"**Business Name:** {cl[1]} ({cl[2]})")
                            st.write(f"**Email ID:** {cl[0]}")
                            if st.button(f"🗑️ Remove Photo of {cl[1]}", key=f"del_{cl[0]}"):
                                run_query("UPDATE users SET shop_photo=NULL WHERE email=?", (cl[0],))
                                st.success("Photo removed successfully!")
                                st.rerun()
                        st.markdown("---")
                else:
                    st.info("No clients have uploaded their shop photos yet.")

        # ---------------- WHOLESALER / SHOP DASHBOARD ----------------
        else:
            my_data = run_query("SELECT license_key, package_type, shop_photo, name FROM users WHERE email=?", (st.session_state.user_email,))[0]
            
            c1, c2 = st.columns([3, 1])
            with c1:
                st.title(f"🏢 {my_data[3]} ({st.session_state.user_role})")
                st.info(f"**License Key:** {my_data[0] if my_data[0] else 'Pending Approval'} | **Package:** {my_data[1]}")
            with c2:
                if my_data[2]:
                    st.image(my_data[2], width=120, caption="Shop Photo")
                else:
                    st.write("📷 No Shop Photo")
                    
            tab1, tab2, tab3 = st.tabs(["📊 Business Stats", "📦 Inventory / Bills", "📸 Upload Shop Photo"])
            
            with tab1: st.info("Daily sales and metrics will be displayed here.")
            with tab2: st.info("Billing and Inventory modules will be added here.")
            
            # NEW: SHOP PHOTO UPLOAD FEATURE
            with tab3:
                st.subheader("📸 Set Your Profile / Shop Photo")
                st.write("This photo will be displayed on your dashboard and visible to the Super Admin.")
                
                uploaded_photo = st.file_uploader("Choose a valid image file", type=["jpg", "jpeg", "png"])
                if uploaded_photo is not None:
                    if st.button("💾 Save Photo"):
                        photo_bytes = uploaded_photo.getvalue()
                        run_query("UPDATE users SET shop_photo=? WHERE email=?", (photo_bytes, st.session_state.user_email))
                        st.success("🎉 Photo successfully uploaded!")
                        st.rerun()
                
                if my_data[2]:
                    st.markdown("---")
                    st.write("### Your Current Photo:")
                    st.image(my_data[2], width=300)
                    if st.button("🗑️ Delete My Photo"):
                        run_query("UPDATE users SET shop_photo=NULL WHERE email=?", (st.session_state.user_email,))
                        st.success("Your photo has been deleted.")
                        st.rerun()

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

    # ---------------- LOGIN ----------------
    elif st.session_state.current_page == "Login":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title(f"🔐 {st.session_state.login_role} Login")
        l_email = st.text_input("Email")
        l_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            user = run_query("SELECT name, role, approved, is_deleted FROM users WHERE email=? AND password=?", (l_email, l_pass))
            if user:
                if user[0][3] == 1:
                    st.error("❌ Your account has been Suspended/Deleted by Admin.")
                elif user[0][1] == st.session_state.login_role:
                    if user[0][2] == 1:
                        st.session_state.logged_in = True
                        st.session_state.user_role = user[0][1]
                        st.session_state.user_email = l_email
                        st.rerun()
                    else:
                        st.warning("⏳ Payment pending approval. Waiting for License Key.")
                else:
                    st.error("❌ Role Mismatch.")
            else:
                st.error("Invalid Credentials.")

    # ---------------- REGISTER & PAYMENT ----------------
    elif st.session_state.current_page == "Register":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        
        st.title("🛒 Buy Kulu ERP Software")
        settings = run_query("SELECT upi_id, monthly_price, yearly_price, lifetime_price, soft_gst FROM admin_settings WHERE id=1")[0]
        gst_pct = settings[4]
        
        st.subheader("Step 1: Choose Package & Register")
        with st.form("reg_form"):
            r_role = st.selectbox("Role", ["Wholesaler", "Shop"])
            r_name = st.text_input("Business Name")
            r_email = st.text_input("Email")
            r_pass = st.text_input("Password", type="password")
            
            st.markdown("---")
            p_type = st.radio("Select Software Package", [
                f"Monthly (₹{settings[1]} + {gst_pct}% GST)", 
                f"1 Year (₹{settings[2]} + {gst_pct}% GST)", 
                f"Lifetime (₹{settings[3]} + {gst_pct}% GST)"
            ])
            
            st.markdown(f"**Pay to UPI ID:** `{settings[0]}`")
            r_utr = st.text_input("Enter UTR / Transaction No. (Required)")
            r_amt = st.number_input("Total Amount Paid (Including GST)", min_value=0.0)
            
            submit = st.form_submit_button("Submit Registration & Payment")
            
            if submit:
                if r_name and r_email and r_pass and r_utr and r_amt > 0:
                    pack = p_type.split(" ")[0]
                    try:
                        run_query("INSERT INTO users (name, email, password, role, payment_status, approved, utr_no, paid_amount, package_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (r_name, r_email, r_pass, r_role, 'Pending', 0, r_utr, r_amt, pack))
                        st.success("✅ Payment Submitted! Super Admin will verify your UTR and assign a License Key.")
                    except:
                        st.error("❌ Email already registered.")
                else:
                    st.warning("Please fill all fields and enter valid UTR/Amount.")

    # ---------------- FORGOT PASSWORD ----------------
    elif st.session_state.current_page == "Forgot Password":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
            
        st.title("🔑 Reset Password (All Users)")
        if "forgot_step" not in st.session_state: st.session_state.forgot_step = 1
        
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
                    st.success("✅ Password updated! Click 'Back to Home' to Login.")
                    st.session_state.forgot_step = 1
                else:
                    st.warning("Password cannot be empty.")
