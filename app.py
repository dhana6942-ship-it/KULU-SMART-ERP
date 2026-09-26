import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kulu Smart ERP & POS", page_icon="💊", layout="wide"
)

# --- DATABASE CONNECTION & SETUP ---
DB_NAME = "kulu_smart_erp.db"


def get_connection():
  return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
  conn = get_connection()
  cursor = conn.cursor()

  # 1. Wholesale Medicine Table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS wholesale_medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE,
            box_count INTEGER,
            strips_per_box INTEGER,
            tablets_per_strip INTEGER,
            purchase_price_per_box REAL,
            selling_price_per_box REAL,
            gst_rate REAL,
            updated_date TEXT
        )
    """)

  # 2. Retail/Store Medicines Table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS retail_medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE,
            strips_count INTEGER,
            tablets_per_strip INTEGER,
            purchase_price_per_strip REAL,
            selling_price_per_strip REAL,
            gst_rate REAL,
            updated_date TEXT
        )
    """)

  # 3. Transactions Ledger (Safe for Old Data)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_type TEXT,
            category TEXT,
            item_name TEXT,
            qty_units TEXT,
            total_amount REAL,
            gst_amount REAL,
            net_amount REAL,
            tx_date TEXT
        )
    """)

  conn.commit()
  conn.close()


init_db()

# --- TOP BANNER ---
st.markdown(
    """
    <div style="background-color: #FFEB3B; padding: 10px; text-align: center; border-radius: 5px; font-weight: bold; color: #000;">
        📢 WELCOME TO KULU SMART ERP! PREMIUM POS SOFTWARE. HELP NO - ONLY WHATSAPP CHATING-8910223342 MAIL ID -DHANA6942@GMAIL.COM
    </div>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🧭 Navigation Hub")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "Select Section",
    [
        "🏠 Home Page",
        "👑 Super Admin",
        "📦 Wholesale Medicine",
        "🏷️ Medicine Store (Retail)",
        "🛒 POS Billing & Sales",
        "📋 GST Summary & Reports",
        "⚖️ Balance Sheet",
    ],
)

# --- 1. HOME PAGE ---
if menu == "🏠 Home Page":
  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 30px; border-radius: 10px; text-align: center; color: white; margin-top: 20px;">
            <h1>🚀 KULU SMART ERP & POS</h1>
            <p>NEXT-GEN CLOUD BILLING, BARCODE & INVENTORY</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown("<br>", unsafe_allow_html=True)

  col1, col2, col3 = st.columns(3)

  with col1:
    st.markdown(
        """
            <div style="border: 2px solid #ff4b4b; padding: 20px; border-radius: 10px; text-align: center; background: #fff; color: #000; min-height: 180px;">
                <h2>👑</h2>
                <h3>SUPER ADMIN</h3>
                <p style="font-size: 13px; color: #555;">Control software licensing and global system settings.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

  with col2:
    st.markdown(
        """
            <div style="border: 2px solid #1c83e1; padding: 20px; border-radius: 10px; text-align: center; background: #fff; color: #000; min-height: 180px;">
                <h2>📦</h2>
                <h3>WHOLESALE HUB</h3>
                <p style="font-size: 13px; color: #555;">Manage massive B2B sales and track retailer network.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

  with col3:
    st.markdown(
        """
            <div style="border: 2px solid #00cc96; padding: 20px; border-radius: 10px; text-align: center; background: #fff; color: #000; min-height: 180px;">
                <h2>🛒</h2>
                <h3>RETAIL POS</h3>
                <p style="font-size: 13px; color: #555;">Lightning fast barcode billing & smart inventory tools.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

# --- 2. SUPER ADMIN ---
elif menu == "👑 Super Admin":
  st.subheader("👑 Super Admin Control Center")
  conn = get_connection()
  df_ws = pd.read_sql("SELECT * FROM wholesale_medicines", conn)
  df_ret = pd.read_sql("SELECT * FROM retail_medicines", conn)
  conn.close()
  c1, c2 = st.columns(2)
  c1.metric("Wholesale Table Items", len(df_ws))
  c2.metric("Retail Store Table Items", len(df_ret))

# --- 3. WHOLESALE MEDICINE ---
elif menu == "📦 Wholesale Medicine":
  st.subheader("📦 Wholesale Medicine (Separate Table 1)")
  tab1, tab2 = st.tabs(["Add Wholesale Item", "Wholesale Purchase"])

  with tab1:
    with st.form("ws_form"):
      name = st.text_input("Wholesale Item Name")
      boxes = st.number_input("Box Count", min_value=0, value=10)
      s_box = st.number_input("Strips per Box", min_value=1, value=200)
      t_strip = st.number_input("Tablets per Strip", min_value=1, value=10)
      p_price = st.number_input("Purchase Price per Box", min_value=0.0, value=1000.0)
      s_price = st.number_input("Selling Price per Box", min_value=0.0, value=1200.0)
      gst = st.selectbox("GST Rate", [0.0, 5.0, 12.0, 18.0])
      if st.form_submit_button("Save Wholesale"):
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """INSERT INTO wholesale_medicines VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(item_name) DO UPDATE SET box_count=box_count+?""",
            (name, boxes, s_box, t_strip, p_price, s_price, gst, str(datetime.now()), boxes)
        )
        conn.commit()
        conn.close()
        st.success("Saved successfully!")
    
    conn = get_connection()
    st.dataframe(pd.read_sql("SELECT * FROM wholesale_medicines", conn))
    conn.close()

  with tab2:
    st.markdown("### Wholesale Purchase")
    conn = get_connection()
    df_ws = pd.read_sql("SELECT item_name FROM wholesale_medicines", conn)
    conn.close()
    if not df_ws.empty:
      with st.form("ws_p"):
        item = st.selectbox("Item", df_ws["item_name"])
        qty = st.number_input("Boxes", min_value=1, value=1)
        cost = st.number_input("Cost per Box", min_value=0.0, value=500.0)
        gst_p = st.selectbox("GST %", [0.0, 5.0, 12.0, 18.0])
        if st.form_submit_button("Confirm"):
          base = qty * cost
          g_amt = base * (gst_p / 100.0)
          conn = get_connection()
          c = conn.cursor()
          c.execute("UPDATE wholesale_medicines SET box_count = box_count + ? WHERE item_name = ?", (qty, item))
          c.execute("INSERT INTO transactions VALUES (NULL, 'Purchase', 'Wholesale', ?, ?, ?, ?, ?, ?)", 
                    ("Purchase", item, f"{qty} Boxes", base, g_amt, base+g_amt, str(datetime.now())))
          conn.commit()
          conn.close()
          st.success("Purchase recorded!")

# --- 4. MEDICINE STORE (RETAIL) ---
elif menu == "🏷️ Medicine Store (Retail)":
  st.subheader("🏷️ Medicine Store / Retail (Separate Table 2)")
  tab1, tab2 = st.tabs(["Add Store Item", "Store Purchase"])

  with tab1:
    with st.form("ret_form"):
      name = st.text_input("Store Item Name")
      strips = st.number_input("Strips Count", min_value=0, value=50)
      t_strip = st.number_input("Tablets per Strip", min_value=1, value=10)
      p_price = st.number_input("Purchase Price per Strip", min_value=0.0, value=40.0)
      s_price = st.number_input("Selling Price per Strip", min_value=0.0, value=60.0)
      gst = st.selectbox("GST Rate", [0.0, 5.0, 12.0, 18.0])
      if st.form_submit_button("Save Store Item"):
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """INSERT INTO retail_medicines VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(item_name) DO UPDATE SET strips_count=strips_count+?""",
            (name, strips, t_strip, p_price, s_price, gst, str(datetime.now()), strips)
        )
        conn.commit()
        conn.close()
        st.success("Saved successfully!")

    conn = get_connection()
    st.dataframe(pd.read_sql("SELECT * FROM retail_medicines", conn))
    conn.close()

  with tab2:
    st.markdown("### Store Purchase")
    conn = get_connection()
    df_ret = pd.read_sql("SELECT item_name FROM retail_medicines", conn)
    conn.close()
    if not df_ret.empty:
      with st.form("ret_p"):
        item = st.selectbox("Item", df_ret["item_name"])
        qty = st.number_input("Strips", min_value=1, value=10)
        cost = st.number_input("Cost per Strip", min_value=0.0, value=30.0)
        gst_p = st.selectbox("GST %", [0.0, 5.0, 12.0, 18.0])
        if st.form_submit_button("Confirm Purchase"):
          base = qty * cost
          g_amt = base * (gst_p / 100.0)
          conn = get_connection()
          c = conn.cursor()
          c.execute("UPDATE retail_medicines SET strips_count = strips_count + ? WHERE item_name = ?", (qty, item))
          c.execute("INSERT INTO transactions VALUES (NULL, 'Purchase', 'Medicine Store', ?, ?, ?, ?, ?, ?)", 
                    ("Purchase", item, f"{qty} Strips", base, g_amt, base+g_amt, str(datetime.now())))
          conn.commit()
          conn.close()
          st.success("Store purchase recorded!")

# --- 5. POS BILLING & SALES ---
elif menu == "🛒 POS Billing & Sales":
  st.subheader("🛒 POS Billing Counter (Retail)")
  conn = get_connection()
  df_ret = pd.read_sql("SELECT * FROM retail_medicines", conn)
  conn.close()

  if not df_ret.empty:
    with st.form("pos_f"):
      cust = st.text_input("Customer Name", value="Walk-in")
      item = st.selectbox("Select Medicine", df_ret["item_name"])
      row = df_ret[df_ret["item_name"] == item].iloc[0]
      t_per_s = int(row["tablets_per_strip"])
      p_strip = float(row["selling_price_per_strip"])
      p_tab = p_strip / t_per_s if t_per_s > 0 else p_strip
      stock = int(row["strips_count"])

      st.info(f"Available Stock: {stock} Strips | 1 Strip = {t_per_s} Tablets | Tablet Price: ₹{p_tab:.2f} | Strip Price: ₹{p_strip:.2f}")
      mode = st.radio("Unit Mode", ["Strips", "Individual Tablets"])

      if mode == "Strips":
        qty = st.number_input("Number of Strips", min_value=1, value=1)
        rate = p_strip
        label = f"{qty} Strips"
        deduct = qty
      else:
        qty = st.number_input("Number of Tablets", min_value=1, value=1)
        rate = p_tab
        label = f"{qty} Tablets"
        deduct = qty / t_per_s

      gst_pct = st.selectbox("GST %", [0.0, 5.0, 12.0, 18.0])
      if st.form_submit_button("Complete Sale & Invoice"):
        sub = qty * rate
        g_val = sub * (gst_pct / 100.0)
        net = sub + g_val
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE retail_medicines SET strips_count = strips_count - ? WHERE item_name = ?", (deduct, item))
        c.execute("INSERT INTO transactions VALUES (NULL, 'Sales', 'Store POS', ?, ?, ?, ?, ?, ?)", 
                  ("Sales", item, label, sub, g_val, net, str(datetime.now())))
        conn.commit()
        conn.close()
        st.success(f"Sale completed! Grand Total: ₹{net:.2f}")

# --- 6. GST SUMMARY ---
elif menu == "📋 GST Summary & Reports":
  st.subheader("📋 GST Summary")
  conn = get_connection()
  df = pd.read_sql("SELECT * FROM transactions", conn)
  conn.close()
  if not df.empty:
    st.dataframe(df)
  else:
    st.info("No records found.")

# --- 7. BALANCE SHEET ---
elif menu == "⚖️ Balance Sheet":
  st.subheader("⚖️ Balance Sheet")
  conn = get_connection()
  df = pd.read_sql("SELECT * FROM transactions", conn)
  conn.close()
  tot_s = df[df["tx_type"]=="Sales"]["net_amount"].sum() if not df.empty else 0.0
  tot_p = df[df["tx_type"]=="Purchase"]["net_amount"].sum() if not df.empty else 0.0
  st.metric("Total Sales", f"₹{tot_s:,.2f}")
  st.metric("Total Purchase", f"₹{tot_p:,.2f}")
