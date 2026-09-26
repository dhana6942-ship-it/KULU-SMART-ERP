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
  msg["Subject"] = subject
  msg["From"] = f"Kulu Smart ERP <{sender_email}>"
  msg["To"] = receiver_email
  try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, app_password)
    server.send_message(msg)
    server.quit()
    return True
  except Exception as e:
    return False


# ==========================================
# 1. DATABASE SETUP (Safe 2 Tables Added)
# ==========================================
def init_db():
  conn = sqlite3.connect("kulu_erp_system.db", timeout=20)
  conn.execute("PRAGMA journal_mode=WAL;")
  c = conn.cursor()
  c.execute(
      """CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, payment_status TEXT, approved INTEGER)"""
  )
  c.execute(
      """CREATE TABLE IF NOT EXISTS admin_settings (id INTEGER PRIMARY KEY, upi_id TEXT, monthly_price REAL, yearly_price REAL, lifetime_price REAL, soft_gst REAL)"""
  )
  c.execute(
      """CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, shop_email TEXT, item_name TEXT, purchase_price REAL, selling_price REAL, stock INTEGER, gst_rate REAL, barcode TEXT)"""
  )
  c.execute(
      """CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, shop_email TEXT, date TEXT, item_name TEXT, qty INTEGER, total_price REAL, profit REAL, is_gst INTEGER, trans_type TEXT)"""
  )

  # --- WHOLESALE & RETAIL SEPARATE TABLES ---
  c.execute("""
        CREATE TABLE IF NOT EXISTS wholesale_medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_email TEXT,
            item_name TEXT,
            box_count INTEGER,
            strips_per_box INTEGER,
            tablets_per_strip INTEGER,
            purchase_price_per_box REAL,
            selling_price_per_box REAL,
            gst_rate REAL,
            barcode TEXT,
            updated_date TEXT
        )
    """)

  c.execute("""
        CREATE TABLE IF NOT EXISTS retail_medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_email TEXT,
            item_name TEXT,
            strips_count INTEGER,
            tablets_per_strip INTEGER,
            purchase_price_per_strip REAL,
            selling_price_per_strip REAL,
            gst_rate REAL,
            barcode TEXT,
            updated_date TEXT
        )
    """)

  cols_to_add = [
      ("utr_no", "TEXT"),
      ("paid_amount", "REAL"),
      ("package_type", "TEXT"),
      ("license_key", "TEXT"),
      ("is_deleted", "INTEGER DEFAULT 0"),
      ("shop_photo", "BLOB"),
      ("expiry_date", "TEXT"),
      ("key_entered", "INTEGER DEFAULT 0"),
      ("upi_id", "TEXT"),
      ("owner_name", "TEXT"),
      ("pan_gst_no", "TEXT"),
      ("address", "TEXT"),
      ("state", "TEXT"),
      ("aadhar", "TEXT"),
      ("pan", "TEXT"),
      ("gst", "TEXT"),
      ("mobile", "TEXT"),
  ]
  for col, dtype in cols_to_add:
    try:
      c.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
    except:
      pass

  admin_cols_to_add = [
      ("demo_price", "REAL DEFAULT 99.0"),
      ("monthly_price", "REAL DEFAULT 499.0"),
      ("six_month_price", "REAL DEFAULT 2499.0"),
      ("yearly_price", "REAL DEFAULT 4999.0"),
      ("lifetime_price", "REAL DEFAULT 9999.0"),
      (
          "notice_text",
          "TEXT DEFAULT 'WELCOME TO KULU SMART ERP! PREMIUM POS SOFTWARE.'",
      ),
      ("home_banner", "BLOB"),
  ]
  for col, dtype in admin_cols_to_add:
    try:
      c.execute(f"ALTER TABLE admin_settings ADD COLUMN {col} {dtype}")
    except:
      pass

  try:
    c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
  except:
    pass
  try:
    c.execute(
        "ALTER TABLE transactions ADD COLUMN trans_type TEXT DEFAULT 'Sale'"
    )
  except:
    pass

  tx_cols = [
      ("customer_name", "TEXT"),
      ("customer_mobile", "TEXT"),
      ("invoice_no", "TEXT"),
      ("rate", "REAL"),
      ("gst_pct", "REAL"),
      ("gst_amt", "REAL DEFAULT 0"),
  ]
  for col, dtype in tx_cols:
    try:
      c.execute(f"ALTER TABLE transactions ADD COLUMN {col} {dtype}")
    except:
      pass

  admin_hash = hash_pass("admin123")
  c.execute(
      "INSERT OR IGNORE INTO users (name, email, password, role, payment_status,"
      " approved, is_deleted) VALUES (?, ?, ?, ?, ?, ?, ?)",
      (
          "Super Admin",
          "dhana6942@gmail.com",
          admin_hash,
          "SuperAdmin",
          "Paid",
          1,
          0,
      ),
  )
  try:
    c.execute(
        "UPDATE users SET role='SuperAdmin', password=?, approved=1,"
        " payment_status='Paid', is_deleted=0 WHERE email='dhana6942@gmail.com'",
        (admin_hash,),
    )
  except:
    pass
  c.execute(
      "INSERT OR IGNORE INTO admin_settings (id, upi_id, monthly_price,"
      " yearly_price, lifetime_price, soft_gst) VALUES (1, 'kulusutar@ybl', 499,"
      " 4999, 9999, 18)"
  )
  conn.commit()
  conn.close()


init_db()


def run_query(query, params=()):
  conn = sqlite3.connect("kulu_erp_system.db", timeout=20)
  conn.execute("PRAGMA journal_mode=WAL;")
  c = conn.cursor()
  c.execute(query, params)
  conn.commit()
  data = c.fetchall()
  conn.close()
  return data


def generate_license():
  return "KULU-" + "".join(
      random.choices(string.ascii_uppercase + string.digits, k=12)
  )


# 🔴 SALES RECEIPT HTML 🔴
def generate_receipt_html(
    shop_name,
    item_name,
    qty,
    rate,
    gst_pct,
    gst_amt,
    total_price,
    date_str,
    shop_upi="",
    cust_name="",
    cust_mob="",
    inv_no="",
    base_amt=0,
):
  qr_html = ""
  if shop_upi:
    safe_shop_name = urllib.parse.quote(shop_name)
    upi_url = f"upi://pay?pa={shop_upi}&pn={safe_shop_name}&am={total_price:.2f}&cu=INR"
    qr_img_src = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={urllib.parse.quote(upi_url)}"
    qr_html = f"""<div class="center" style="margin-top: 15px;"><img src="{qr_img_src}" alt="Scan to Pay" width="90" height="90" style="border: 2px solid #000; padding: 2px;"><div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Scan to Pay ₹ {total_price:.2f}</div></div>"""
  cust_info = f"""<div class="line"></div><div style="font-size: 11px; margin-bottom: 5px;"><b>Customer:</b> {cust_name.upper()}<br><b>Mob:</b> {cust_mob}</div>""" if cust_name or cust_mob else ""
  inv_info = (
      f"<div class='center' style='font-size: 10px; margin-bottom:"
      f" 5px;'>Inv No: {inv_no}</div>"
      if inv_no
      else ""
  )
  gst_html = (
      f"<tr><td>Base Amount:</td><td class='right'>₹"
      f" {base_amt:.2f}</td></tr><tr><td>GST ({gst_pct}%):</td><td"
      f" class='right'>(+) ₹ {gst_amt:.2f}</td></tr>"
      if gst_pct > 0
      else ""
  )
  return f"""<html><head><style>@media print {{ @page {{ margin: 0; size: 58mm auto; }} body {{ margin: 0; padding: 0; background: #fff; }} #print-btn {{ display: none; }} }} body {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; color: #000; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f4f4f4; padding: 20px; }} .receipt-box {{ width: 58mm; min-width: 220px; max-width: 100%; margin: 0 auto; padding: 10px; text-align: left; background: #fff; border: 1px solid #ccc; }} .center {{ text-align: center; }} .line {{ border-top: 1px dashed #000; margin: 8px 0; }} .bold {{ font-weight: bold; }} table {{ width: 100%; font-size: 12px; margin: 5px 0; border-collapse: collapse; }} .right {{ text-align: right; }} .btn {{ padding: 10px 20px; font-size: 16px; font-weight: bold; cursor: pointer; background: #28a745; color: white; border: none; border-radius: 5px; margin-top: 20px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }}</style></head><body><div class="receipt-box"><div class="center bold" style="font-size: 16px;">{shop_name.upper()}</div><div class="center" style="font-size: 10px; margin-bottom: 5px;">Invoice / Cash Memo</div>{inv_info}<div class="center" style="font-size: 11px;">Date: {date_str}</div>{cust_info}<div class="line"></div><div><span class="bold">Item:</span> {item_name.upper()}</div><table><tr><td>Qty: {qty}</td><td class="right">Rate: ₹ {rate:.2f}</td></tr>{gst_html}</table><div class="line"></div><div class="right bold" style="font-size: 15px;">Total: ₹ {total_price:.2f}</div>{qr_html}<div class="line"></div><div class="center" style="font-size: 10px; margin-top: 5px;">Thank You! Visit Again.</div></div><div id="print-btn"><button class="btn" onclick="window.print()">🖨️ Print Receipt & QR Code</button><br><br></div></body></html>"""


# 🔴 PURCHASE REPORT HTML 🔴
def generate_purchase_report_html(shop_name, date_str, purchases):
  rows = ""
  tot_base = 0
  tot_gst = 0
  tot_net = 0
  for p in purchases:
    base = p[1] * p[2]
    tot_base += base
    tot_gst += p[4]
    tot_net += p[5]
    rows += f"<tr><td>{str(p[0]).upper()}</td><td>{p[1]}</td><td>₹{p[2]:.2f}</td><td>{p[3]}%</td><td>₹{p[4]:.2f}</td><td>₹{p[5]:.2f}</td></tr>"
  return f"""<html><head><style>@media print {{ @page {{ margin: 0; size: 80mm auto; }} body {{ margin: 0; padding: 0; background: #fff; }} #print-btn {{ display: none; }} }} body {{ font-family: Arial, sans-serif; font-size: 12px; color: #000; padding: 20px; }} .receipt-box {{ width: 80mm; min-width: 300px; max-width: 100%; margin: 0 auto; padding: 15px; background: #fff; border: 1px solid #ccc; }} .center {{ text-align: center; }} .line {{ border-top: 1px dashed #000; margin: 10px 0; }} .bold {{ font-weight: bold; }} table {{ width: 100%; font-size: 11px; margin: 10px 0; border-collapse: collapse; text-align: left; }} th, td {{ padding: 4px; border-bottom: 1px dotted #ccc; }} .right {{ text-align: right; }} .btn {{ padding: 10px 20px; font-size: 16px; font-weight: bold; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px; margin-top: 20px; display: block; width: 100%; }}</style></head><body><div class="receipt-box"><div class="center bold" style="font-size: 18px;">{shop_name.upper()}</div><div class="center" style="font-size: 12px; margin-bottom: 5px;">Daily Purchase Entry Report</div><div class="center" style="font-size: 12px;">Date: {date_str}</div><div class="line"></div><table><tr><th>Item</th><th>Qty</th><th>Rate</th><th>GST%</th><th>Tax</th><th>Total</th></tr>{rows}</table><div class="line"></div><div class="right bold">Total Base Amount: ₹ {tot_base:.2f}</div><div class="right bold">Total GST Paid: (+) ₹ {tot_gst:.2f}</div><div class="right bold" style="font-size: 16px; margin-top: 5px;">Net Purchase Value: ₹ {tot_net:.2f}</div><div class="line"></div><div class="center" style="font-size: 11px; margin-top: 5px;">* Verify this report with Seller's Invoice *</div></div><div id="print-btn"><button class="btn" onclick="window.print()">🖨️ Print Purchase Report</button></div></body></html>"""


def generate_gst_report_html(df_gst, tot_gst, shop_name):
  rows = ""
  for _, r in df_gst.iterrows():
    rows += f"<tr><td>{r['Invoice']}</td><td>{r['Date']}</td><td>{str(r['Customer']).upper()}</td><td>₹{r['Base Value (₹)']:.2f}</td><td>{r['GST %']}%</td><td>₹{r['GST Amount (₹)']:.2f}</td><td>₹{r['Total Value (₹)']:.2f}</td></tr>"
  return f"""<html><head><style>body {{ font-family: Arial, sans-serif; padding: 20px; }} table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }} th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }} th {{ background-color: #f2f2f2; }} .header {{ text-align: center; margin-bottom: 30px; }} .summary {{ margin-top: 30px; padding: 15px; background: #eef9f1; border-radius: 8px; }} @media print {{ #print-btn {{ display: none; }} }}</style></head><body><div class="header"><h2>GST Sales & Liability Report</h2><h3>{shop_name.upper()}</h3><p>Report Generated on: {str(date.today())}</p></div><button id="print-btn" onclick="window.print()" style="padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 5px;">🖨️ Print PDF for CA</button><table><tr><th>Invoice No</th><th>Date</th><th>Customer</th><th>Base Value</th><th>GST Slab</th><th>GST Amount</th><th>Total Value</th></tr>{rows}</table><div class="summary"><h3>Tax Liability Summary</h3><h4>Total GST Collected: ₹ {tot_gst:.2f}</h4></div></body></html>"""


# ==========================================
# 2. PAGE CONFIG & UI CSS
# ==========================================
st.set_page_config(page_title="Kulu Smart ERP", layout="wide", page_icon="🚀")

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stAppDeployButton, [data-testid="stAppDeployButton"], [data-testid="manage-app-button"] {display: none !important; visibility: hidden !important;}
    .viewerBadge_container, .viewerBadge_link, div[class*="viewerBadge"], div[class*="manage-app"] {display: none !important; visibility: hidden !important;}
    iframe[src*="badge"] {display: none !important; visibility: hidden !important;}
    .stDecoration {display: none !important;}
    .viewerBadge_link__1S_gx {display: none !important; visibility: hidden !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {display: none !important; visibility: hidden !important;}
    .st-emotion-cache-16txtl3 {padding-top: 0rem;}
    
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
        padding: 50px 30px; border-radius: 25px; text-align: center; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.08); border: 1px solid rgba(0,0,0,0.05); 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); margin-bottom: 25px; height: 100%; 
    }
    .feature-card:hover { transform: translateY(-20px) scale(1.02); box-shadow: 0 30px 50px rgba(0,0,0,0.15); }
    
    .border-admin { border-top: 8px solid #ff0844; } 
    .border-wholesale { border-top: 8px solid #0052D4; } 
    .border-shop { border-top: 8px solid #11998e; }
    
    .card-icon { font-size: 75px; margin-bottom: 25px; filter: drop-shadow(3px 5px 8px rgba(0,0,0,0.15)); transition: transform 0.3s ease; }
    .feature-card:hover .card-icon { transform: scale(1.15) rotate(5deg); }
    
    .card-title { font-size: 28px; font-weight: 800; color: #1a1a1a; margin-bottom: 15px; text-transform: uppercase;}
    .card-text { font-size: 16px; color: #555; line-height: 1.7; font-weight: 500; margin-bottom: 25px; }
    
    .register-section { 
        background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%); 
        padding: 60px 40px; border-radius: 25px; text-align: center; 
        margin-top: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.08); 
        border: 1px solid rgba(0,0,0,0.05); 
    }
    .footer { text-align: center; margin-top: 80px; padding-top: 25px; border-top: 1px solid #eaeaea; color: #999; font-size: 15px; font-weight: 600; letter-spacing: 1px; padding-bottom: 20px;}
    </style>
""",
    unsafe_allow_html=True,
)

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "current_page" not in st.session_state:
  st.session_state.current_page = "Home Ground"
if "login_role" not in st.session_state:
  st.session_state.login_role = None

INDIAN_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
]

if st.session_state.logged_in:
  menu = st.sidebar.radio("Navigation", ["Gateway of ERP", "Logout"])
  if menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.session_state.current_page = "Home Ground"
    st.rerun()

  elif menu == "Gateway of ERP":
    if st.session_state.user_role == "SuperAdmin":
      admin_data = run_query(
          "SELECT shop_photo FROM users WHERE email=?",
          (st.session_state.user_email,),
      )[0]
      c1, c2 = st.columns([4, 1])
      with c1:
        st.title("👑 Super Admin Control Panel")
      with c2:
        if admin_data[0]:
          st.image(admin_data[0], width=100)

      tab_act, tab_set, tab_rec, tab_prof = st.tabs(
          ["✅ Active Clients", "⚙️ Pricing & Banner", "♻️ Data Recovery", "🔐 Admin Profile"]
      )

      with tab_act:
        active = run_query(
            "SELECT email, name, role, package_type, expiry_date, license_key,"
            " owner_name, paid_amount FROM users WHERE approved=1 AND role !="
            " 'SuperAdmin' AND is_deleted=0"
        )
        if active:
          st.dataframe(
              pd.DataFrame(
                  active,
                  columns=[
                      "Email",
                      "Business Name",
                      "Role",
                      "Package",
                      "Expiry",
                      "License Key",
                      "Owner",
                      "Paid",
                  ],
              ),
              use_container_width=True,
          )
          c1, c2 = st.columns(2)
          with c1:
            sel_mail = st.selectbox(
                "Select Email to Resend License", [a[0] for a in active]
            )
            if st.button("📧 Manual Resend Mail"):
              usr = [u for u in active if u[0] == sel_mail][0]
              if send_real_email(
                  sel_mail,
                  f"Your Kulu ERP {usr[3]} License (Resend)",
                  f"Here is your requested License Key.\n🔑 License Key:"
                  f" {usr[5]}\n📅 Expiry Date: {usr[4]}\nAmount Paid:"
                  f" ₹{usr[7]}\n\nThanks,\nKulu Smart ERP",
              ):
                st.success("✅ Email Sent!")
              else:
                st.error("❌ Failed to send email.")
          with c2:
            sel_del = st.selectbox(
                "Select Email to Suspend", [a[0] for a in active]
            )
            if st.button("🗑️ Suspend User"):
              run_query(
                  "UPDATE users SET is_deleted=1 WHERE email=?", (sel_del,)
              )
              st.success("Suspended!")
              st.rerun()
        else:
          st.write("No active clients.")

      with tab_set:
        settings = run_query(
            "SELECT upi_id, demo_price, monthly_price, six_month_price,"
            " yearly_price, lifetime_price, soft_gst, notice_text, home_banner"
            " FROM admin_settings WHERE id=1"
        )[0]
        if settings[8]:
          st.image(settings[8], use_container_width=True)
          if st.button("🗑️ Delete Home Banner"):
            run_query(
                "UPDATE admin_settings SET home_banner=NULL WHERE id=1"
            )
            st.rerun()
        new_banner = st.file_uploader(
            "Upload New Home Banner", type=["jpg", "png", "jpeg"]
        )
        if new_banner and st.button("💾 Save New Banner"):
          run_query(
              "UPDATE admin_settings SET home_banner=? WHERE id=1",
              (new_banner.read(),),
          )
          st.success("Banner updated!")
          st.rerun()

        with st.form("price_settings"):
          n_notice = st.text_input("📢 Notice Board Text", value=settings[7])
          c1, c2, c3 = st.columns(3)
          with c1:
            n_upi = st.text_input("UPI ID", value=settings[0])
            n_demo = st.number_input("Demo Price", value=float(settings[1]))
          with c2:
            n_mon = st.number_input("Monthly Price", value=float(settings[2]))
            n_six = st.number_input("6 Months Price", value=float(settings[3]))
          with c3:
            n_yr = st.number_input("1 Year Price", value=float(settings[4]))
            n_life = st.number_input(
                "Lifetime Price", value=float(settings[5])
            )
            n_gst = st.number_input("GST %", value=float(settings[6]))
          if st.form_submit_button("Update Prices"):
            run_query(
                "UPDATE admin_settings SET upi_id=?, demo_price=?,"
                " monthly_price=?, six_month_price=?, yearly_price=?,"
                " lifetime_price=?, soft_gst=?, notice_text=? WHERE id=1",
                (
                    n_upi,
                    n_demo,
                    n_mon,
                    n_six,
                    n_yr,
                    n_life,
                    n_gst,
                    n_notice,
                ),
            )
            st.success("✅ Updated!")
            st.rerun()

      with tab_rec:
        del_users = run_query(
            "SELECT email, name, role FROM users WHERE is_deleted=1 AND role !="
            " 'SuperAdmin'"
        )
        if del_users:
          for d_u in del_users:
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.error(f"{d_u[1]} ({d_u[0]})")
            if c2.button(f"♻️ Restore", key=f"res_{d_u[0]}"):
              run_query(
                  "UPDATE users SET is_deleted=0 WHERE email=?", (d_u[0],)
              )
              st.rerun()
            if c3.button(f"❌ Delete", key=f"pdel_{d_u[0]}"):
              run_query("DELETE FROM users WHERE email=?", (d_u[0],))
              st.rerun()
        else:
          st.info("No deleted accounts found.")

      with tab_prof:
        st.subheader("🛡️ Admin Profile & Database Backup")
        try:
          with open("kulu_erp_system.db", "rb") as f:
            st.download_button(
                "💾 Download Full Database Backup (.db)",
                f,
                file_name="kulu_erp_system_backup.db",
                type="primary",
            )
        except Exception as e:
          st.error("Backup file not found.")

        curr_admin = run_query(
            "SELECT email, mobile, password FROM users WHERE email=?",
            (st.session_state.user_email,),
        )[0]
        new_email = st.text_input("New Email ID", value=curr_admin[0])
        new_pass = st.text_input(
            "New Password (will be encrypted)", type="password"
        )
        if st.button("Update Profile"):
          new_hash = hash_pass(new_pass) if new_pass else curr_admin[2]
          run_query(
              "UPDATE users SET email=?, password=? WHERE email=?",
              (new_email, new_hash, st.session_state.user_email),
          )
          st.session_state.user_email = new_email
          st.success("Updated!")
          st.rerun()

    else:
      my_data = run_query(
          "SELECT license_key, package_type, shop_photo, name, key_entered,"
          " expiry_date, upi_id, gst, approved, state FROM users WHERE email=?",
          (st.session_state.user_email,),
      )[0]
      (
          db_key,
          pkg_type,
          shop_photo,
          shop_name,
          key_entered,
          exp_date,
          shop_upi,
          shop_gst,
          approved,
          shop_state,
      ) = my_data

      if str(date.today()) > str(exp_date):
        st.error("❌ Your Software License has expired.")
        st.stop()
      if not key_entered:
        st.title("🔐 Software License Activation")
        entered_key = st.text_input(
            "🔑 Enter License Key (Check your Email):",
            placeholder="KULU-XXXXXXXXXXXX",
        )
        if st.button("Activate Software", type="primary"):
          if entered_key.strip() == db_key:
            run_query(
                "UPDATE users SET key_entered=1 WHERE email=?",
                (st.session_state.user_email,),
            )
            st.success("✅ Activated!")
            st.balloons()
            st.rerun()
          else:
            st.error("❌ Invalid Key!")
        st.stop()

      c1, c2 = st.columns([3, 1])
      with c1:
        st.markdown(
            f"<h2>📊 Gateway of Kulu ERP - {shop_name.upper()}"
            f" ({st.session_state.user_role})</h2>",
            unsafe_allow_html=True,
        )
      with c2:
        if shop_photo:
          st.image(shop_photo, width=80)
        st.info(f"Valid Till: {exp_date}")

      if st.session_state.user_role == "Wholesaler":
        tab_dash, tab_stock, tab_purch, tab_sales, tab_hist, tab_gst_rep, tab_net, tab_prof = st.tabs(
            [
                "📈 Dash",
                "📦 Stock",
                "📥 Purchase",
                "🧾 Sales POS",
                "🖨️ History",
                "📊 GST Reports",
                "🏪 Network",
                "⚙️ Settings",
            ]
        )
      else:
        tab_dash, tab_stock, tab_purch, tab_sales, tab_hist, tab_gst_rep, tab_prof = st.tabs(
            [
                "📈 Dash",
                "📦 Stock",
                "📥 Purchase",
                "🧾 Sales POS",
                "🖨️ History",
                "📊 GST Reports",
                "⚙️ Settings",
            ]
        )

      with tab_dash:
        st.subheader("Financial Summary (Today)")
        today_str = str(date.today())
        sales_data = run_query(
            "SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND"
            " date=? AND trans_type='Sale'",
            (st.session_state.user_email, today_str),
        )[0][0]
        purch_data = run_query(
            "SELECT SUM(total_price) FROM transactions WHERE shop_email=? AND"
            " date=? AND trans_type='Purchase'",
            (st.session_state.user_email, today_str),
        )[0][0]
        profit_data = run_query(
            "SELECT SUM(profit) FROM transactions WHERE shop_email=? AND"
            " date=? AND trans_type='Sale'",
            (st.session_state.user_email, today_str),
        )[0][0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Sales", f"₹ {float(sales_data or 0):.2f}")
        c2.metric("Total Purchases", f"₹ {float(purch_data or 0):.2f}")
        c3.metric("Net Profit", f"₹ {float(profit_data or 0):.2f}")

      with tab_stock:
        st.subheader("📦 Live Stock Register & Valuation")
        inv_data = run_query(
            "SELECT item_name, stock, purchase_price, selling_price FROM"
            " inventory WHERE shop_email=?",
            (st.session_state.user_email,),
        )
        sales_today = run_query(
            "SELECT item_name, SUM(qty) FROM transactions WHERE shop_email=? AND"
            " date=? AND trans_type='Sale' GROUP BY item_name",
            (st.session_state.user_email, today_str),
        )
        sales_dict = {row[0]: row[1] for row in sales_today}
        purchases_today = run_query(
            "SELECT item_name, SUM(qty) FROM transactions WHERE shop_email=? AND"
            " date=? AND trans_type='Purchase' GROUP BY item_name",
            (st.session_state.user_email, today_str),
        )
        purchases_dict = {row[0]: row[1] for row in purchases_today}

        tot_stock_qty = 0
        tot_stock_val = 0
        tot_out_qty = 0
        tot_out_val = 0
        stock_list = []

        if inv_data:
          for row in inv_data:
            i_name = str(row[0]).upper()
            curr_stock = row[1]
            buy_price = row[2]
            sell_price = row[3]
            stock_in = purchases_dict.get(row[0], 0)
            stock_out = sales_dict.get(row[0], 0)
            val = curr_stock * buy_price
            out_val = stock_out * sell_price
            tot_stock_qty += curr_stock
            tot_stock_val += val
            tot_out_qty += stock_out
            tot_out_val += out_val
            stock_list.append(
                [i_name, stock_in, stock_out, curr_stock, buy_price, val]
            )

          c1, c2, c3, c4 = st.columns(4)
          c1.metric("Total Available Stock (Qty)", f"{tot_stock_qty}")
          c2.metric("Total Stock Amount (Value)", f"₹ {tot_stock_val:.2f}")
          c3.metric("Today Out Stock (Sold Qty)", f"{tot_out_qty}")
          c4.metric("Today Out Amount (Sold Value)", f"₹ {tot_out_val:.2f}")
          st.markdown("---")
          st.dataframe(
              pd.DataFrame(
                  stock_list,
                  columns=[
                      "Product Name",
                      "Today IN (Qty)",
                      "Today OUT (Qty)",
                      "Current Stock",
                      "Buy Rate (₹)",
                      "Total Stock Value (₹)",
                  ],
              ),
              use_container_width=True,
          )
        else:
          st.info("କୌଣସି ଷ୍ଟକ୍ ନାହିଁ।")

      with tab_purch:
        st.subheader("📥 Add Inventory (Purchase Entry)")
        i_bcode = st.text_input(
            "||||| Scan Barcode Here (Use Machine) 👇", key="p_bcode"
        )
        existing_item = (
            run_query(
                "SELECT item_name, purchase_price, selling_price FROM"
                " inventory WHERE barcode=? AND shop_email=?",
                (i_bcode, st.session_state.user_email),
            )
            if i_bcode
            else []
        )
        def_name = (
            str(existing_item[0][0]).upper() if existing_item else ""
        )
        def_buy = float(existing_item[0][1]) if existing_item else 0.0
        def_sell = float(existing_item[0][2]) if existing_item else 0.0
        if existing_item:
          st.success(
              f"Item found: {def_name}. Enter quantity to purchase!"
          )

        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
          raw_i_name = st.text_input(
              "Product Name", value=def_name, key="p_name"
          )
          i_name = str(raw_i_name).strip().upper()
        with c2:
          i_qty = st.number_input("Qty", min_value=1, value=1, key="p_qty")
        with c3:
          gst_options = {
              "No GST (0%)": 0,
              "5% GST": 5,
              "12% GST": 12,
              "18% GST": 18,
              "28% GST": 28,
          }
          p_gst_pct = gst_options[
              st.selectbox("Purchase GST Slab", list(gst_options.keys()))
          ]
        with c4:
          i_pprice = st.number_input(
              "Buy Rate Base (₹)",
              min_value=0.0,
              value=def_buy,
              step=10.0,
              key="p_pprice",
          )
          i_sprice = st.number_input(
              "Sell Rate (₹)",
              min_value=0.0,
              value=(
                  def_sell
                  if def_sell > 0
                  else float(i_pprice + (i_pprice * 0.18))
              ),
              step=10.0,
              key="p_sprice",
          )

        if (
            st.button(
                "💾 Save Purchase & Add to Report",
                use_container_width=True,
                type="primary",
            )
            and i_name
        ):
          p_base = i_pprice * i_qty
          p_gst_amt = (p_base * p_gst_pct) / 100
          p_final_total = p_base + p_gst_amt
          if existing_item:
            run_query(
                "UPDATE inventory SET stock = stock + ?, purchase_price=?,
