import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kulu Smart ERP - Medical Store", page_icon="💊", layout="wide"
)

# --- DATABASE CONNECTION & SETUP (Strictly 2 Tables + Safe Old Data Preservation) ---
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

  # 2. Medicine Store / Retail Table
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

  # 3. Transactions Ledger (Safe & Protected for Old Data)
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

# --- TOP BANNER NOTIFICATION ---
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
                <h3>WHOLESALE MEDICINE</h3>
                <p style="font-size: 13px; color: #555;">Manage boxes, cartons, and bulk wholesale inventory.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

  with col3:
    st.markdown(
        """
            <div style="border: 2px solid #00cc96; padding: 20px; border-radius: 10px; text-align: center; background: #fff; color: #000; min-height: 180px;">
                <h2>🏷️</h2>
                <h3>MEDICINE STORE</h3>
                <p style="font-size: 13px; color: #555;">Manage strips, tablets, counter sales, and POS.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("<br><br>", unsafe_allow_html=True)
  st.markdown(
      """
        <div style="background: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>READY TO TRANSFORM YOUR BUSINESS?</h3>
            <p>Join thousands of businesses using Kulu Smart ERP today.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown(
      """
    <p style="text-align: center; color: gray; font-size: 12px; margin-top: 40px;">
    © 2026 Kulu Smart Solutions Global. Engineered for Excellence.
    </p>
    """,
      unsafe_allow_html=True,
  )

# --- 2. WHOLESALE MEDICINE (TABLE 1) ---
elif menu == "📦 Wholesale Medicine":
  st.subheader(
      "📦 Wholesale Medicine Management (Box / Carton & Optional GST)"
  )

  tab1, tab2 = st.tabs(["Add / Update Wholesale Item", "Wholesale Purchase"])

  with tab1:
    with st.form("ws_item_form"):
      item_name = st.text_input("Wholesale Medicine Name")
      box_count = st.number_input("Initial Boxes / Cartons", min_value=0, value=10)
      strips_per_box = st.number_input(
          "Packets/Strips per Box (e.g. 200)", min_value=1, value=200
      )
      tablets_per_strip = st.number_input(
          "Tablets per Strip", min_value=1, value=10
      )
      purchase_price_box = st.number_input(
          "Purchase Price per Box (₹)", min_value=0.0, value=1000.0
      )
      selling_price_box = st.number_input(
          "Selling Price per Box (₹)", min_value=0.0, value=1200.0
      )
      gst_rate = st.selectbox(
          "GST Rate (%) - Wholesale",
          [0.0, 5.0, 12.0, 18.0],
          format_func=lambda x: "No GST (0%)" if x == 0 else f"{x}%",
      )

      submitted = st.form_submit_button("Save Wholesale Item")
      if submitted and item_name:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                    INSERT INTO wholesale_medicines (item_name, box_count, strips_per_box, tablets_per_strip, purchase_price_per_box, selling_price_per_box, gst_rate, updated_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(item_name) DO UPDATE SET
                    box_count = box_count + ?,
                    purchase_price_per_box = ?,
                    selling_price_per_box = ?,
                    gst_rate = ?,
                    updated_date = ?
                """,
            (
                item_name,
                box_count,
                strips_per_box,
                tablets_per_strip,
                purchase_price_box,
                selling_price_box,
                gst_rate,
                str(datetime.now()),
                box_count,
                purchase_price_box,
                selling_price_box,
                gst_rate,
                str(datetime.now()),
            ),
        )
        conn.commit()
        conn.close()
        st.success(f"Wholesale medicine '{item_name}' saved successfully!")

    st.markdown("### 📋 Wholesale Inventory Table")
    conn = get_connection()
    df_ws = pd.read_sql("SELECT * FROM wholesale_medicines", conn)
    conn.close()
    if not df_ws.empty:
      st.dataframe(df_ws, use_container_width=True)
    else:
      st.info("No wholesale medicines found.")

  with tab2:
    st.markdown("### Wholesale Purchase Entry with Optional GST")
    conn = get_connection()
    df_ws = pd.read_sql("SELECT item_name FROM wholesale_medicines", conn)
    conn.close()

    if df_ws.empty:
      st.warning("Please add wholesale medicines first.")
    else:
      with st.form("ws_pur_form"):
        sel_item = st.selectbox("Select Wholesale Medicine", df_ws["item_name"])
        pur_boxes = st.number_input("Boxes Purchased", min_value=1, value=5)
        box_cost = st.number_input(
            "Cost Price per Box (₹)", min_value=0.0, value=800.0
        )
        gst_pct = st.selectbox(
            "Purchase GST %",
            [0.0, 5.0, 12.0, 18.0],
            format_func=lambda x: "No GST" if x == 0 else f"{x}%",
        )

        p_sub = st.form_submit_button("Confirm Wholesale Purchase")
        if p_sub:
          base = pur_boxes * box_cost
          gst_amt = base * (gst_pct / 100.0)
          net = base + gst_amt

          conn = get_connection()
          cursor = conn.cursor()
          cursor.execute(
              "UPDATE wholesale_medicines SET box_count = box_count + ? WHERE item_name = ?",
              (pur_boxes, sel_item),
          )
          cursor.execute(
              """
                        INSERT INTO transactions (tx_type, category, item_name, qty_units, total_amount, gst_amount, net_amount, tx_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  "Purchase",
                  "Wholesale",
                  sel_item,
                  f"{pur_boxes} Boxes",
                  base,
                  gst_amt,
                  net,
                  str(datetime.now()),
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              f"Successfully purchased {pur_boxes} boxes of {sel_item} (Total:"
              f" ₹{net:.2f})"
          )

# --- 3. MEDICINE STORE / RETAIL (TABLE 2) ---
elif menu == "🏷️ Medicine Store (Retail)":
  st.subheader("🏷️ Medicine Store Management (Strips, Tablets & Optional GST)")

  tab1, tab2 = st.tabs(["Add / Update Store Item", "Store Purchase Entry"])

  with tab1:
    with st.form("retail_item_form"):
      r_name = st.text_input("Store Medicine Name")
      r_strips = st.number_input("Initial Strips Count", min_value=0, value=100)
      r_t_per_s = st.number_input("Tablets per Strip", min_value=1, value=10)
      r_p_price = st.number_input(
          "Purchase Price per Strip (₹)", min_value=0.0, value=40.0
      )
      r_s_price = st.number_input(
          "Selling Price per Strip (₹)", min_value=0.0, value=60.0
      )
      r_gst = st.selectbox(
          "GST Rate (%) - Store",
          [0.0, 5.0, 12.0, 18.0],
          format_func=lambda x: "No GST (0%)" if x == 0 else f"{x}%",
      )

      r_submitted = st.form_submit_button("Save Store Item")
      if r_submitted and r_name:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                    INSERT INTO retail_medicines (item_name, strips_count, tablets_per_strip, purchase_price_per_strip, selling_price_per_strip, gst_rate, updated_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(item_name) DO UPDATE SET
                    strips_count = strips_count + ?,
                    purchase_price_per_strip = ?,
                    selling_price_per_strip = ?,
                    gst_rate = ?,
                    updated_date = ?
                """,
            (
                r_name,
                r_strips,
                r_t_per_s,
                r_p_price,
                r_s_price,
                r_gst,
                str(datetime.now()),
                r_strips,
                r_p_price,
                r_s_price,
                r_gst,
                str(datetime.now()),
            ),
        )
        conn.commit()
        conn.close()
        st.success(f"Medicine store item '{r_name}' saved successfully!")

    st.markdown("### 📋 Medicine Store Inventory Table")
    conn = get_connection()
    df_ret = pd.read_sql("SELECT * FROM retail_medicines", conn)
    conn.close()
    if not df_ret.empty:
      st.dataframe(df_ret, use_container_width=True)
    else:
      st.info("No store items found.")

  with tab2:
    st.markdown("### Store Purchase Entry with Optional GST")
    conn = get_connection()
    df_ret = pd.read_sql("SELECT item_name FROM retail_medicines", conn)
    conn.close()

    if df_ret.empty:
      st.warning("Please add store medicines first.")
    else:
      with st.form("ret_pur_form"):
        sel_r = st.selectbox("Select Store Medicine", df_ret["item_name"])
        pur_s = st.number_input("Strips Purchased", min_value=1, value=20)
        s_cost = st.number_input(
            "Cost Price per Strip (₹)", min_value=0.0, value=35.0
        )
        gst_p = st.selectbox(
            "Purchase GST %",
            [0.0, 5.0, 12.0, 18.0],
            format_func=lambda x: "No GST" if x == 0 else f"{x}%",
            key="r_p_gst",
        )

        rp_sub = st.form_submit_button("Confirm Store Purchase")
        if rp_sub:
          base = pur_s * s_cost
          gst_amt = base * (gst_p / 100.0)
          net = base + gst_amt

          conn = get_connection()
          cursor = conn.cursor()
          cursor.execute(
              "UPDATE retail_medicines SET strips_count = strips_count + ? WHERE item_name = ?",
              (pur_s, sel_r),
          )
          cursor.execute(
              """
                        INSERT INTO transactions (tx_type, category, item_name, qty_units, total_amount, gst_amount, net_amount, tx_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  "Purchase",
                  "Medicine Store",
                  sel_r,
                  f"{pur_s} Strips",
                  base,
                  gst_amt,
                  net,
                  str(datetime.now()),
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              f"Successfully purchased {pur_s} strips of {sel_r} (Total:"
              f" ₹{net:.2f})"
          )

# --- 4. POS BILLING & SALES ---
elif menu == "🛒 POS Billing & Sales":
  st.subheader(
      "🛒 POS Billing (Strip & Individual Tablet Calculation with GST)"
  )
  conn = get_connection()
  df_ret = pd.read_sql("SELECT * FROM retail_medicines", conn)
  conn.close()

  if df_ret.empty:
    st.warning("No store medicines available for billing.")
  else:
    with st.form("pos_billing_form"):
      cust_name = st.text_input("Customer Name", value="Walk-in Customer")
      med_sel = st.selectbox("Select Medicine for Billing", df_ret["item_name"])

      row = df_ret[df_ret["item_name"] == med_sel].iloc[0]
      t_per_strip = int(row["tablets_per_strip"])
      s_price_strip = float(row["selling_price_per_strip"])
      s_price_tablet = (
          s_price_strip / t_per_strip if t_per_strip > 0 else s_price_strip
      )
      stock_strips = int(row["strips_count"])

      st.info(
          f"Stock Available: {stock_strips} Strips | 1 Strip = {t_per_strip}"
          f" Tablets | Price/Tablet: ₹{s_price_tablet:.2f} | Price/Strip:"
          f" ₹{s_price_strip:.2f}"
      )

      billing_mode = st.radio(
          "Billing Unit Mode", ["Strips / Packets", "Individual Tablets (Pcs)"]
      )

      if billing_mode == "Strips / Packets":
        qty_val = st.number_input("Number of Strips", min_value=1, value=1)
        unit_rate = s_price_strip
        qty_label = f"{qty_val} Strips"
        deduct_stock = qty_val
      else:
        qty_val = st.number_input(
            "Number of Tablets (Pieces)", min_value=1, value=1
        )
        unit_rate = s_price_tablet
        qty_label = f"{qty_val} Tablets"
        deduct_stock = qty_val / t_per_strip

      bill_gst_pct = st.selectbox(
          "Sales GST %",
          [0.0, 5.0, 12.0, 18.0],
          format_func=lambda x: "No GST" if x == 0 else f"{x}%",
          key="bill_gst",
      )

      generate_bill = st.form_submit_button(
          "Complete Sale & Print Tax Invoice"
      )

      if generate_bill:
        subtotal = qty_val * unit_rate
        gst_val = subtotal * (bill_gst_pct / 100.0)
        grand_total = subtotal + gst_val

        if billing_mode == "Strips / Packets" and qty_val > stock_strips:
          st.error("Error: Insufficient stock available!")
        else:
          conn = get_connection()
          cursor = conn.cursor()
          cursor.execute(
              "UPDATE retail_medicines SET strips_count = strips_count - ? WHERE item_name = ?",
              (deduct_stock, med_sel),
          )
          cursor.execute(
              """
                        INSERT INTO transactions (tx_type, category, item_name, qty_units, total_amount, gst_amount, net_amount, tx_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  "Sales",
                  "Store POS",
                  med_sel,
                  qty_label,
                  subtotal,
                  gst_val,
                  grand_total,
                  str(datetime.now()),
              ),
          )
          conn.commit()
          conn.close()

          st.success("Sale completed and stock updated successfully!")

          # --- HALF A4 / A5 PRINT PREVIEW ---
          st.markdown("---")
          st.markdown("### 🖨️ Tax Invoice (Half A4 / A5 Print Format)")
          invoice_html = f"""
                    <div style="border: 2px dashed #333; padding: 15px; width: 65%; font-family: Arial, sans-serif; background: #fff; color: #000;">
                        <h3 style="text-align: center; margin: 0;">KULU SMART MEDICAL STORE</h3>
                        <p style="text-align: center; font-size: 12px; margin: 2px;">Link Road, Cuttack | Ph: 9853XXXXXX</p>
                        <hr>
                        <p><b>Customer:</b> {cust_name}</p>
                        <p><b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}</p>
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                            <tr style="border-bottom: 1px solid #000;">
                                <th style="text-align: left;">Item</th>
                                <th style="text-align: center;">Qty</th>
                                <th style="text-align: right;">Amount (₹)</th>
                            </tr>
                            <tr>
                                <td>{med_sel}</td>
                                <td style="text-align: center;">{qty_label}</td>
                                <td style="text-align: right;">{subtotal:.2f}</td>
                            </tr>
                        </table>
                        <hr>
                        <p style="text-align: right; margin: 2px;"><b>Subtotal:</b> ₹{subtotal:.2f}</p>
                        <p style="text-align: right; margin: 2px;"><b>GST ({bill_gst_pct}%):</b> ₹{gst_val:.2f}</p>
                        <p style="text-align: right; font-size: 16px; margin: 2px;"><b>Grand Total: ₹{grand_total:.2f}</b></p>
                        <p style="text-align: center; font-size: 11px; margin-top: 15px;">Thank you! Get Well Soon.</p>
                    </div>
                    """
          st.markdown(invoice_html, unsafe_allow_html=True)
          st.info(
              "Tip: Use browser print (Ctrl+P) and set paper layout to A5 /"
              " Half A4."
          )

# --- 5. GST SUMMARY & REPORTS ---
elif menu == "📋 GST Summary & Reports":
  st.subheader("📋 Government GST Summary & Filing Report")

  conn = get_connection()
  try:
    df_tx = pd.read_sql("SELECT * FROM transactions", conn)
  except Exception:
    df_tx = pd.DataFrame()
  conn.close()

  if not df_tx.empty:
    st.markdown("### All Transaction Records")
    st.dataframe(df_tx, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    sales_gst = df_tx[df_tx["tx_type"] == "Sales"]["gst_amount"].sum()
    purchase_gst = df_tx[df_tx["tx_type"] == "Purchase"]["gst_amount"].sum()
    net_gst = sales_gst - purchase_gst

    col1.metric("Output GST (Sales)", f"₹ {sales_gst:,.2f}")
    col2.metric("Input GST (Purchases)", f"₹ {purchase_gst:,.2f}")
    st.markdown(f"### Net GST Payable to Government: **₹ {net_gst:,.2f}**")
  else:
    st.info("No transaction data available.")

# --- 6. BALANCE SHEET ---
elif menu == "⚖️ Balance Sheet":
  st.subheader("⚖️ Financial Balance Sheet")

  conn = get_connection()
  try:
    df_tx = pd.read_sql("SELECT * FROM transactions", conn)
  except Exception:
    df_tx = pd.DataFrame()
  conn.close()

  tot_sales = (
      df_tx[df_tx["tx_type"] == "Sales"]["net_amount"].sum()
      if not df_tx.empty
      else 0.0
  )
  tot_pur = (
      df_tx[df_tx["tx_type"] == "Purchase"]["net_amount"].sum()
      if not df_tx.empty
      else 0.0
  )

  c1, c2 = st.columns(2)
  c1.metric("Total Sales Revenue", f"₹ {tot_sales:,.2f}")
  c2.metric("Total Purchase Expenditure", f"₹ {tot_pur:,.2f}")
  st.markdown("---")
  st.metric("Gross Business Margin", f"₹ {tot_sales - tot_pur:,.2f}")
