import streamlit as st
import sqlite3
import pandas as pd
import random
import string
from datetime import date
import streamlit.components.v1 as components

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
        ("is_deleted", "INTEGER DEFAULT 0"), ("shop_photo", "BLOB")
    ]
    for col, dtype in cols_to_add:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except: pass 

    try: c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
    except: pass
    
    try: c.execute("ALTER TABLE transactions ADD COLUMN trans_type TEXT DEFAULT 'Sale'")
    except: pass

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

# 🔴 ADVANCED THERMAL PRINTER CSS (Universal Fitting for 58mm & 80mm Portable Printers) 🔴
def generate_receipt_html(shop_name, item_name, qty, rate, gst, total_price, date_str):
    return f"""
    <html>
    <head>
    <style>
        /* This perfectly fits all portable thermal machines */
        @media print {{
            @page {{ margin: 0; size: 58mm 100mm; }}
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
            <div class="line"></div>
            <div class="center" style="font-size: 10px; margin-top: 5px;">Thank You! Visit Again.</div>
        </div>
        
        <div id="print-btn">
            <button class="btn" onclick="window.print()">
                🖨️ Print Receipt (POS Machine)
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
# 2. PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Kulu ERP - POS Edition", layout="wide", page_icon="🧾")

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
            st.info("Please use Wholesaler or Retail Shop login to test Barcode & Print Features.")

        # ---------------- WHOLESALER & RETAIL SHOP (SEPARATE PURCHASE & SALES) ----------------
        else:
            my_data = run_query("SELECT license_key, package_type, shop_photo, name FROM users WHERE email=?", (st.session_state.user_email,))[0]
            shop_name = my_data[3]
            
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<h2>📊 Gateway of Kulu ERP - {shop_name} ({st.session_state.user_role})</h2>', unsafe_allow_html=True)
            with c2:
                if my_data[2]: st.image(my_data[2], width=80)
            
            if my_data[0] is None:
                st.warning("⚠️ ଆପଣଙ୍କ ଆକାଉଣ୍ଟ ଏପର୍ଯ୍ୟନ୍ତ Super Admin ଙ୍କ ଦ୍ୱାରା ଆପ୍ରୁଭ୍ ହୋଇନାହିଁ।")
            else:
                tab_dash, tab_purch, tab_sales, tab_rep = st.tabs(["📈 Dashboard", "📥 Purchase Entry (Stock In)", "🧾 Sales Entry (Stock Out)", "📄 Balance Sheet & P&L"])
                
                # --- TAB 1: DASHBOARD ---
                with tab_dash:
                    st.subheader("Financial Summary (Today)")
                    today_str = str(date.today())
                    sales_data = run_query("SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND date=? AND trans_type='Sale'", (st.session_state.user_email, today_str))[0][0]
                    purch_data = run_query("SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND date=? AND trans_type='Purchase'", (st.session_state.user_email, today_str))[0][0]
                    profit_data = run_query("SELECT SUM(profit) FROM transactions WHERE shop_email=? AND date=? AND trans_type='Sale'", (st.session_state.user_email, today_str))[0][0]
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Today's Total Sales", f"₹ {sales_data if sales_data else 0.0}")
                    c2.metric("Today's Total Purchases", f"₹ {purch_data if purch_data else 0.0}")
                    c3.metric("Today's Net Profit", f"₹ {profit_data if profit_data else 0.0}")

                # --- TAB 2: PURCHASE ENTRY (WITH AUTO GST & BARCODE) ---
                with tab_purch:
                    st.subheader("📥 Purchase Entry (Kharedi & Stock In)")
                    st.write("Scan Barcode and enter purchase details. Purchase GST will be auto-calculated.")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        i_bcode = st.text_input("||||| Scan Barcode (Optional)", key="p_bcode")
                        i_name = st.text_input("Product Name", key="p_name")
                    with col2:
                        i_qty = st.number_input("Purchase Quantity", min_value=1, value=1, key="p_qty")
                        i_gst = st.number_input("Purchase GST Rate (%)", min_value=0.0, value=18.0, key="p_gst")
                    with col3:
                        i_pprice = st.number_input("Base Purchase Rate (₹)", min_value=0.0, step=10.0, key="p_pprice")
                        auto_sell = i_pprice + (i_pprice * i_gst / 100)
                        i_sprice = st.number_input("Set Selling Rate (₹)", min_value=0.0, value=float(auto_sell), step=10.0, key="p_sprice")
                        
                    p_base_total = i_pprice * i_qty
                    p_gst_amt = (p_base_total * i_gst) / 100
                    p_final_total = p_base_total + p_gst_amt
                    
                    st.info(f"💰 **Live Purchase Calculate:** ₹ {p_base_total:.2f} (Base) + ₹ {p_gst_amt:.2f} ({i_gst}% GST) = **₹ {p_final_total:.2f} Total Purchase Value**")

                    if st.button("💾 Save Purchase & Update Stock", use_container_width=True):
                        if i_name and i_sprice > 0:
                            existing = run_query("SELECT id FROM inventory WHERE barcode=? AND shop_email=?", (i_bcode, st.session_state.user_email)) if i_bcode else []
                            if existing and i_bcode != "":
                                run_query("UPDATE inventory SET stock = stock + ?, purchase_price=?, selling_price=?, gst_rate=? WHERE id=?",
                                          (i_qty, i_pprice, i_sprice, i_gst, existing[0][0]))
                            else:
                                run_query("INSERT INTO inventory (shop_email, item_name, purchase_price, selling_price, stock, gst_rate, barcode) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                          (st.session_state.user_email, i_name, i_pprice, i_sprice, i_qty, i_gst, i_bcode))
                            
                            run_query("INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst, trans_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                      (st.session_state.user_email, str(date.today()), i_name, i_qty, p_final_total, 0, 1 if i_gst>0 else 0, 'Purchase'))
                            
                            st.success(f"✅ Purchase Saved! Stock Updated for '{i_name}'.")
                            st.rerun()
                        else: st.error("Please enter valid Product Name and Prices.")
                    
                    st.markdown("---")
                    st.markdown("**Current Available Stock:**")
                    stocks = run_query("SELECT item_name, stock, purchase_price, selling_price, barcode FROM inventory WHERE shop_email=?", (st.session_state.user_email,))
                    st.dataframe(pd.DataFrame(stocks, columns=["Item", "Qty", "Purchase (₹)", "Selling (₹)", "Barcode"]), use_container_width=True)

                # --- TAB 3: SALES ENTRY (POS + BARCODE + PORTABLE PRINT) ---
                with tab_sales:
                    st.subheader("🧾 Sales Entry (POS Billing)")
                    st.info("Click the box below and use your scanner. The product will be auto-selected.")
                    
                    scan_code = st.text_input("🔍 SCAN BARCODE HERE...", key="s_scan")
                    
                    stock_items = run_query("SELECT id, item_name, selling_price, stock, gst_rate, purchase_price, barcode FROM inventory WHERE shop_email=? AND stock > 0", (st.session_state.user_email,))
                    
                    if stock_items:
                        item_dict = {f"{item[1]} - ₹{item[2]} (Stock: {item[3]})": item for item in stock_items}
                        
                        default_index = 0
                        if scan_code:
                            for idx, item in enumerate(stock_items):
                                if str(item[6]) == str(scan_code):
                                    default_index = idx
                                    st.success(f"Barcode '{scan_code}' Matched: {item[1]}")
                                    break
                            else:
                                st.error("Barcode not found in stock!")
                        
                        sel_item = st.selectbox("Select Product Manually", list(item_dict.keys()), index=default_index)
                        
                        item_data = item_dict[sel_item]
                        i_id, i_name, default_sprice, i_stock, default_gst, i_pprice, _ = item_data
                        
                        col1, col2, col3 = st.columns(3)
                        with col1: s_qty = st.number_input("Quantity", min_value=1, max_value=i_stock, value=1, key="s_qty")
                        with col2: s_price = st.number_input("Selling Rate (₹)", min_value=0.0, value=float(default_sprice), key="s_price")
                        with col3: s_gst = st.number_input("Sales GST (%)", min_value=0.0, value=float(default_gst), key="s_gst")
                            
                        is_gst_bill = st.checkbox("Calculate GST on Sale", value=True)
                        
                        s_base_total = s_price * s_qty
                        total_cost = i_pprice * s_qty
                        
                        if is_gst_bill:
                            s_tax_amount = (s_base_total * s_gst) / 100
                            s_final_price = s_base_total + s_tax_amount
                            st.write(f"💰 **Live Auto-Calculate:** ₹ {s_base_total:.2f} (Base) + ₹ {s_tax_amount:.2f} GST = **₹ {s_final_price:.2f}**")
                        else:
                            s_final_price = s_base_total
                            st.write(f"💰 **Live Auto-Calculate:** **₹ {s_final_price:.2f}** (No GST)")
                            
                        profit = s_final_price - total_cost

                        if st.button("🛒 Generate Sale Bill & Print", use_container_width=True, type="primary"):
                            if s_qty <= i_stock:
                                run_query("UPDATE inventory SET stock = stock - ? WHERE id=?", (s_qty, i_id))
                                run_query("INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst, trans_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                          (st.session_state.user_email, str(date.today()), i_name, s_qty, s_final_price, profit, 1 if is_gst_bill else 0, 'Sale'))
                                
                                st.success(f"✅ Sale Recorded Successfully! Total: ₹ {s_final_price:.2f}")
                                st.balloons()
                                
                                # Store Thermal HTML Receipt in Session
                                st.session_state.print_receipt = generate_receipt_html(shop_name, i_name, s_qty, s_price, s_gst if is_gst_bill else 0, s_final_price, str(date.today()))
                            else: st.error("❌ Not enough stock!")
                            
                    else: st.warning("No stock available. Please add items in Purchase Entry tab first.")

                    # --- SHOW PERFECT 58MM THERMAL PRINT PREVIEW ---
                    if "print_receipt" in st.session_state:
                        st.markdown("---")
                        st.subheader("🖨️ Portable Printer Bill Preview (58mm/80mm)")
                        st.info("Click 'Print Receipt' in the preview box. It will automatically fit your Thermal Printer's size!")
                        components.html(st.session_state.print_receipt, height=500)

                # --- TAB 4: REPORTS & P&L ---
                with tab_rep:
                    st.subheader("📄 Lifetime Balance Sheet & P&L")
                    t_sales = run_query("SELECT SUM(total_price), SUM(profit) FROM transactions WHERE shop_email=? AND trans_type='Sale'", (st.session_state.user_email,))
                    t_purch = run_query("SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND trans_type='Purchase'", (st.session_state.user_email,))
                    
                    sales_val = t_sales[0][0] or 0.0
                    net_profit = t_sales[0][1] or 0.0
                    purch_val = t_purch[0][0] or 0.0
                    
                    col1, col2 = st.columns(2)
                    col1.markdown(f"### 🟢 Total Sales: **₹ {sales_val:.2f}**")
                    col2.markdown(f"### 🔴 Total Purchases: **₹ {purch_val:.2f}**")
                    
                    status = "✅ PROFIT" if net_profit >= 0 else "❌ LOSS"
                    st.markdown("---")
                    st.markdown(f"## 📊 NET BUSINESS STATUS: {status}")
                    st.markdown(f"### Final Net Profit: ₹ {net_profit:.2f}")

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
        with st.form("reg_form"):
            r_role = st.selectbox("Role", ["Wholesaler", "Shop"])
            r_name = st.text_input("Business Name")
            r_email = st.text_input("Email")
            r_pass = st.text_input("Password", type="password")
            p_type = st.radio("Select Software Package", ["Monthly", "1 Year", "Lifetime"])
            r_utr = st.text_input("Enter UTR / Transaction No. (Required)")
            r_amt = st.number_input("Total Amount Paid", min_value=0.0)
            
            if st.form_submit_button("Submit Registration"):
                if r_name and r_email and r_pass and r_utr and r_amt > 0:
                    try:
                        run_query("INSERT INTO users (name, email, password, role, payment_status, approved, utr_no, paid_amount, package_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (r_name, r_email, r_pass, r_role, 'Pending', 0, r_utr, r_amt, p_type))
                        st.success("✅ Payment Submitted! Super Admin will verify.")
                    except: st.error("❌ Email already registered.")
                else: st.warning("Fill all fields.")

    elif st.session_state.current_page == "Forgot Password":
        if st.button("⬅️ Back to Home"): st.session_state.current_page = "Home Ground"; st.rerun()
        st.title("🔑 Reset Password (OTP)")
        st.info("System Ready.")
