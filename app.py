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
                 (id INTEGER PRIMARY KEY, shop_email TEXT, date TEXT, item_name TEXT, qty INTEGER, total_price REAL, profit REAL, is_gst INTEGER)''')
                 
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
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except: pass 

    try: c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
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

def generate_receipt_html(shop_name, item_name, qty, rate, gst, total_price, date_str):
    # CSS & HTML Format for Thermal Receipt Printer (58mm/80mm compatible)
    return f"""
    <div id="receipt" style="width: 300px; padding: 15px; border: 2px dashed #000; font-family: 'Courier New', Courier, monospace; margin: auto; background: #fff; color: #000;">
        <h3 style="text-align: center; margin: 0 0 10px 0;">{shop_name}</h3>
        <p style="text-align: center; font-size: 12px; margin: 0 0 15px 0;">Date: {date_str}<br>Cash Memo / Retail Invoice</p>
        <hr style="border-top: 1px dashed #000;">
        <table style="width: 100%; font-size: 14px;">
            <tr><td colspan="2"><b>Item:</b> {item_name}</td></tr>
            <tr><td><b>Qty:</b> {qty}</td><td style="text-align: right;"><b>Rate:</b> {rate}</td></tr>
            <tr><td><b>GST (%):</b> {gst}%</td><td style="text-align: right;"></td></tr>
        </table>
        <hr style="border-top: 1px dashed #000;">
        <h3 style="text-align: right; margin: 10px 0 0 0;">Total: ₹ {total_price:.2f}</h3>
        <p style="text-align: center; font-size: 12px; margin-top: 15px;">Thank You! Visit Again.</p>
    </div>
    <div style="text-align: center; margin-top: 15px;">
        <button onclick="var printContents = document.getElementById('receipt').innerHTML; var originalContents = document.body.innerHTML; document.body.innerHTML = printContents; window.print(); document.body.innerHTML = originalContents; window.location.reload();" style="padding: 10px 20px; font-size: 16px; font-weight: bold; cursor: pointer; background: #28a745; color: white; border: none; border-radius: 5px;">
            🖨️ Print Receipt
        </button>
    </div>
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

        # ---------------- WHOLESALER & RETAIL SHOP (POS + BARCODE) ----------------
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
                tab_dash, tab_inv, tab_pos, tab_rep = st.tabs(["📈 Dashboard", "📦 Add Inventory (Barcode)", "🧾 POS Billing (Scan & Print)", "📄 P&L Reports"])
                
                # --- TAB 1: DASHBOARD ---
                with tab_dash:
                    st.subheader("Financial Summary (Today)")
                    today_str = str(date.today())
                    sales_data = run_query("SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND date=?", (st.session_state.user_email, today_str))[0][0]
                    profit_data = run_query("SELECT SUM(profit) FROM transactions WHERE shop_email=? AND date=?", (st.session_state.user_email, today_str))[0][0]
                    c1, c2 = st.columns(2)
                    c1.metric("Today's Total Sales", f"₹ {sales_data if sales_data else 0.0}")
                    c2.metric("Today's Net Profit", f"₹ {profit_data if profit_data else 0.0}")

                # --- TAB 2: INVENTORY (WITH BARCODE) ---
                with tab_inv:
                    st.subheader("📦 Add Stock with Barcode")
                    st.write("Keep the cursor in the Barcode box and use your Scanner Machine to auto-type the code.")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        i_name = st.text_input("Product Name")
                        i_bcode = st.text_input("||||| Scan Barcode (Optional)")
                    with col2:
                        i_stock = st.number_input("Stock Quantity", min_value=1, value=1)
                        i_gst = st.number_input("GST Rate (%)", min_value=0.0, value=18.0)
                    with col3:
                        i_pprice = st.number_input("Purchase Rate (₹)", min_value=0.0)
                        auto_sell = i_pprice + (i_pprice * i_gst / 100)
                        i_sprice = st.number_input("Selling Rate (₹)", min_value=0.0, value=float(auto_sell))
                        
                    if st.button("➕ Add to Inventory", use_container_width=True):
                        if i_name and i_sprice > i_pprice:
                            run_query("INSERT INTO inventory (shop_email, item_name, purchase_price, selling_price, stock, gst_rate, barcode) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                      (st.session_state.user_email, i_name, i_pprice, i_sprice, i_stock, i_gst, i_bcode))
                            st.success(f"Item '{i_name}' added to inventory!")
                            st.rerun()
                        else: st.error("Please enter valid Product Name and Prices.")
                    
                    st.markdown("**Current Stock:**")
                    stocks = run_query("SELECT item_name, stock, selling_price, barcode FROM inventory WHERE shop_email=?", (st.session_state.user_email,))
                    st.dataframe(pd.DataFrame(stocks, columns=["Item", "Qty", "Rate", "Barcode"]), use_container_width=True)

                # --- TAB 3: POS BILLING (SCANNER + PRINT RECEIPT) ---
                with tab_pos:
                    st.subheader("🧾 Point of Sale (Barcode Scanner & Print)")
                    st.info("Click the box below and use your scanner. The product will be auto-selected.")
                    
                    # Barcode Scanner Input
                    scan_code = st.text_input("🔍 SCAN BARCODE HERE...", key="pos_scan")
                    
                    item_data = None
                    stock_items = run_query("SELECT id, item_name, selling_price, stock, gst_rate, purchase_price, barcode FROM inventory WHERE shop_email=? AND stock > 0", (st.session_state.user_email,))
                    
                    if stock_items:
                        item_dict = {f"{item[1]} - ₹{item[2]} (Stock: {item[3]})": item for item in stock_items}
                        
                        # Auto-Select via Barcode
                        default_index = 0
                        if scan_code:
                            for idx, item in enumerate(stock_items):
                                if str(item[6]) == str(scan_code):
                                    default_index = idx
                                    st.success(f"Barcode '{scan_code}' Matched: {item[1]}")
                                    break
                            else:
                                st.error("Barcode not found in stock!")
                        
                        sel_item = st.selectbox("Select Product Manually (If no scanner)", list(item_dict.keys()), index=default_index)
                        
                        # Load Item Details
                        item_data = item_dict[sel_item]
                        i_id, i_name, default_sprice, i_stock, default_gst, i_pprice, _ = item_data
                        
                        col1, col2, col3 = st.columns(3)
                        with col1: b_qty = st.number_input("Quantity", min_value=1, max_value=i_stock, value=1)
                        with col2: manual_price = st.number_input("Rate (₹)", min_value=0.0, value=float(default_sprice))
                        with col3: manual_gst = st.number_input("GST (%)", min_value=0.0, value=float(default_gst))
                            
                        is_gst_bill = st.checkbox("Calculate GST", value=True)
                        
                        # Auto Calculation
                        base_total = manual_price * b_qty
                        total_cost = i_pprice * b_qty
                        
                        if is_gst_bill:
                            tax_amount = (base_total * manual_gst) / 100
                            final_price = base_total + tax_amount
                            st.write(f"**Total: ₹ {final_price:.2f}** (Includes GST)")
                        else:
                            final_price = base_total
                            st.write(f"**Total: ₹ {final_price:.2f}** (No GST)")
                            
                        profit = base_total - total_cost

                        if st.button("🛒 Generate Bill & Print", use_container_width=True, type="primary"):
                            if b_qty <= i_stock:
                                # Save Transaction
                                run_query("UPDATE inventory SET stock = stock - ? WHERE id=?", (b_qty, i_id))
                                run_query("INSERT INTO transactions (shop_email, date, item_name, qty, total_price, profit, is_gst) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                          (st.session_state.user_email, str(date.today()), i_name, b_qty, final_price, profit, 1 if is_gst_bill else 0))
                                
                                st.success(f"✅ Sale Recorded Successfully! Total: ₹ {final_price:.2f}")
                                st.balloons()
                                
                                # Store HTML Receipt in Session to Display
                                st.session_state.print_receipt = generate_receipt_html(shop_name, i_name, b_qty, manual_price, manual_gst if is_gst_bill else 0, final_price, str(date.today()))
                            else: st.error("❌ Not enough stock!")
                            
                    else: st.warning("No stock available. Please add items in Inventory tab first.")

                    # --- SHOW THERMAL PRINT PREVIEW AFTER SALE ---
                    if "print_receipt" in st.session_state:
                        st.markdown("---")
                        st.subheader("🖨️ Customer Invoice / Receipt Preview")
                        st.info("Connect your Thermal Printer and click 'Print Receipt' below.")
                        components.html(st.session_state.print_receipt, height=450)
                        
                        if st.button("Clear Receipt"):
                            del st.session_state.print_receipt
                            st.rerun()

                # --- TAB 4: BALANCE SHEET / REPORTS ---
                with tab_rep:
                    st.subheader("📄 Business Balance Sheet")
                    t_sales = run_query("SELECT SUM(total_price), SUM(profit) FROM transactions WHERE shop_email=?", (st.session_state.user_email,))
                    sales_val = t_sales[0][0] or 0.0
                    net_profit = t_sales[0][1] or 0.0
                    
                    status = "✅ PROFIT" if net_profit >= 0 else "❌ LOSS"
                    
                    st.markdown(f"### Total Lifetime Sales: **₹ {sales_val:.2f}**")
                    st.markdown(f"### Net Business Status: **{status} (₹ {net_profit:.2f})**")

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
