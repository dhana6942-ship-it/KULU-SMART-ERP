import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kulu Smart ERP - Medical Store", page_icon="💊", layout="wide"
)

# --- DATABASE CONNECTION & SETUP (Safe Migration - Old Data Preserved) ---
DB_NAME = "kulu_smart_erp.db"


def get_connection():
  return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
  conn = get_connection()
  cursor = conn.cursor()

  # 1. Wholesale Medicines Table
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

  # 2. Retail Medicines Table
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

  # 3. Transactions Table (Old Data 100% Safe)
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

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("💊 Kulu Smart ERP")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "Go to Menu",
    [
        "🏠 Home Page",
        "📦 Wholesale Inventory",
        "🏷️ Retail Inventory",
        "🛒 Sales (POS Billing)",
        "📋 GST Summary & Reports",
        "⚖️ Balance Sheet",
    ],
)

# --- 1. HOME PAGE ---
if menu == "🏠 Home Page":
  st.title("🌟 Welcome to Kulu Smart ERP")
  st.markdown("### Professional Medical Wholesale & Retail Management System")
  st.markdown("---")

  conn = get_connection()
  try:
    df_tx = pd.read_sql("SELECT * FROM transactions", conn)
    df_ws = pd.read_sql("SELECT * FROM wholesale_medicines", conn)
    df_ret = pd.read_sql("SELECT * FROM retail_medicines", conn)
  except Exception:
    df_tx = pd.DataFrame()
    df_ws = pd.DataFrame()
    df_ret = pd.DataFrame()
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

  c1, c2, c3 = st.columns(3)
  c1.metric("Total Sales Revenue", f"₹ {tot_sales:,.2f}")
  c2.metric("Total Purchase Cost", f"₹ {tot_pur:,.2f}")
  c3.metric(
      "Total Medicines Registered",
      f"{len(df_ws) + len(df_ret)} Items (Wholesale + Retail)",
  )

  st.markdown("---")
  st.subheader("🚀 Quick Navigation Shortcuts")
  col_a, col_b, col_c = st.columns(3)

  with col_a:
    st.info("📦 **Wholesale Section**\nManage boxes, cartons, and bulk entries.")
  with col_b:
    st.success(
        "🏷️ **Retail Section**\nManage strips, tablets, and counter sales."
    )
  with col_c:
    st.warning(
        "🛒 **POS Billing**\nGenerate half-A4 tax invoices instantly."
    )

  st.markdown("---")
  st.caption(
      "Kulu Smart ERP | Safe Database Engine Active (Old Data 100% Protected)"
  )

# --- 2. WHOLESALE INVENTORY ---
elif menu == "📦 Wholesale Inventory":
  st.subheader("📦 Wholesale Medicine Management (Box & Carton System)")

  tab1, tab2 = st.tabs(["Add / Update Wholesale Item", "Wholesale Purchase Entry"])

  with tab1:
    with st.form("wholesale_item_form"):
      item_name = st.text_input("Wholesale Medicine Name")
      box_count = st.number_input(
          "Initial Boxes / Cartons", min_value=0, value=10
      )
      strips_per_box = st.number_input(
          "Packets/Strips per Box (e.g., 20 or 200)", min_value=1, value=200
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
      gst_option = st.selectbox(
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
                gst_option,
                str(datetime.now()),
                box_count,
                purchase_price_box,
                selling_price_box,
                gst_option,
                str(datetime.now()),
            ),
        )
        conn.commit()
        conn.close()
        st.success(f"Wholesale item '{item_name}' saved successfully!")

    st.markdown("### 📋 Current Wholesale Inventory Table")
    conn = get_connection()
    df_ws = pd.read_sql("SELECT * FROM wholesale_medicines", conn)
    conn.close()
    if not df_ws.empty:
      st.dataframe(df_ws, use_container_width=True)
    else:
      st.info("No wholesale items found.")

  with tab2:
    st.markdown("### Wholesale Purchase Entry with Optional GST")
    conn = get_connection()
    df_ws = pd.read_sql("SELECT item_name FROM wholesale_medicines", conn)
    conn.close()

    if df_ws.empty:
      st.warning("Please add wholesale medicines first.")
    else:
      with st.form("ws_purchase_form"):
        sel_item = st.selectbox("Select Wholesale Medicine", df_ws["item_name"])
        pur_boxes = st.number_input("Boxes Purchased", min_value=1, value=1)
        unit_cost = st.number_input(
            "Cost Price per Box (₹)", min_value=0.0, value=500.0
        )
        gst_pct = st.selectbox(
            "Purchase GST %",
            [0.0, 5.0, 12.0, 18.0],
            format_func=lambda x: "No GST" if x == 0 else f"{x}%",
            key="ws_p_gst",
        )

        p_submit = st.form_submit_button("Confirm Wholesale Purchase")
        if p_submit:
          base_amt = pur_boxes * unit_cost
          gst_amt = base_amt * (gst_pct / 100.0)
          net_amt = base_amt + gst_amt

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
                  base_amt,
                  gst_amt,
                  net_amt,
                  str(datetime.now()),
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              f"Successfully purchased {pur_boxes} boxes of {sel_item} (Total:"
              f" ₹{net_amt:.2f})"
          )

# --- 3. RETAIL INVENTORY ---
elif menu == "🏷️ Retail Inventory":
  st.subheader("🏷️ Retail Medicine Store Management")

  tab1, tab2 = st.tabs(["Add / Update Retail Item", "Retail Purchase Entry"])

  with tab1:
    with st.form("retail_item_form"):
      r_item = st.text_input("Retail Medicine Name")
      r_strips = st.number_input("Initial Strips Count", min_value=0, value=50)
      r_t_per_s = st.number_input("Tablets per Strip", min_value=1, value=10)
      r_p_price = st.number_input(
          "Purchase Price per Strip (₹)", min_value=0.0, value=50.0
      )
      r_s_price = st.number_input(
          "Selling Price per Strip (₹)", min_value=0.0, value=70.0
      )
      r_gst = st.selectbox(
          "GST Rate (%) - Retail",
          [0.0, 5.0, 12.0, 18.0],
          format_func=lambda x: "No GST (0%)" if x == 0 else f"{x}%",
          key="r_gst_box",
      )

      r_sub = st.form_submit_button("Save Retail Item")
      if r_sub and r_item:
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
                r_item,
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
        st.success(f"Retail item '{r_item}' saved successfully!")

    st.markdown("### 📋 Current Retail Inventory Table")
    conn = get_connection()
    df_ret = pd.read_sql("SELECT * FROM retail_medicines", conn)
    conn.close()
    if not df_ret.empty:
      st.dataframe(df_ret, use_container_width=True)
    else:
      st.info("No retail items found.")

  with tab2:
    st.markdown("### Retail Purchase Entry with Optional GST")
    conn = get_connection()
    df_ret = pd.read_sql("SELECT item_name FROM retail_medicines", conn)
    conn.close()

    if df_ret.empty:
      st.warning("Please add retail medicines first.")
    else:
      with st.form("ret_purchase_form"):
        sel_r_item = st.selectbox("Select Retail Medicine", df_ret["item_name"])
        pur_strips = st.number_input("Strips Purchased", min_value=1, value=10)
        r_unit_cost = st.number_input(
            "Cost Price per Strip (₹)", min_value=0.0, value=40.0
        )
        r_gst_pct = st.selectbox(
            "Retail Purchase GST %",
            [0.0, 5.0, 12.0, 18.0],
            format_func=lambda x: "No GST" if x == 0 else f"{x}%",
            key="r_p_gst",
        )

        rp_submit = st.form_submit_button("Confirm Retail Purchase")
        if rp_submit:
          r_base = pur_strips * r_unit_cost
          r_gst_amt = r_base * (r_gst_pct / 100.0)
          r_net_amt = r_base + r_gst_amt

          conn = get_connection()
          cursor = conn.cursor()
          cursor.execute(
              "UPDATE retail_medicines SET strips_count = strips_count + ? WHERE item_name = ?",
              (pur_strips, sel_r_item),
          )
          cursor.execute(
              """
                        INSERT INTO transactions (tx_type, category, item_name, qty_units, total_amount, gst_amount, net_amount, tx_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  "Purchase",
                  "Retail",
                  sel_r_item,
                  f"{pur_strips} Strips",
                  r_base,
                  r_gst_amt,
                  r_net_amt,
                  str(datetime.now()),
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              f"Successfully purchased {pur_strips} strips of {sel_r_item}"
              f" (Total: ₹{r_net_amt:.2f})"
          )

# --- 4. SALES (POS BILLING WITH STRIP/TABLET CONVERSION & GST) ---
elif menu == "🛒 Sales (POS Billing)":
  st.subheader("🛒 POS Billing & Sales Entry")

  conn = get_connection()
  df_ret = pd.read_sql("SELECT * FROM retail_medicines", conn)
  conn.close()

  if df_ret.empty:
    st.warning(
        "No retail medicines found in inventory. Please add items in Retail"
        " Inventory first."
    )
  else:
    with st.form("pos_form"):
      customer_name = st.text_input("Customer Name", value="Walk-in Customer")
      item_sel = st.selectbox("Select Medicine", df_ret["item_name"])

      item_row = df_ret[df_ret["item_name"] == item_sel].iloc[0]
      t_per_s = int(item_row["tablets_per_strip"])
      price_per_strip = float(item_row["selling_price_per_strip"])
      price_per_tablet = (
          price_per_strip / t_per_s if t_per_s > 0 else price_per_strip
      )
      available_strips = int(item_row["strips_count"])

      st.info(
          f"Stock Available: {available_strips} Strips | 1 Strip = {t_per_s}"
          f" Tablets | Price/Tablet: ₹{price_per_tablet:.2f} | Price/Strip:"
          f" ₹{price_per_strip:.2f}"
      )

      sale_mode = st.radio(
          "Select Unit Type",
          ["Strips / Packets", "Individual Tablets (Pcs)"],
      )

      if sale_mode == "Strips / Packets":
        qty_num = st.number_input("Number of Strips", min_value=1, value=1)
        unit_price = price_per_strip
        qty_str = f"{qty_num} Strips"
        total_strips_to_deduct = qty_num
      else:
        qty_num = st.number_input(
            "Number of Tablets (Pieces)", min_value=1, value=1
        )
        unit_price = price_per_tablet
        qty_str = f"{qty_num} Tablets"
        total_strips_to_deduct = qty_num / t_per_s

      sales_gst_pct = st.selectbox(
          "Sales GST %",
          [0.0, 5.0, 12.0, 18.0],
          format_func=lambda x: "No GST" if x == 0 else f"{x}%",
          key="s_gst",
      )

      pos_submit = st.form_submit_button("Generate Bill & Complete Sale")

      if pos_submit:
        subtotal = qty_num * unit_price
        gst_val = subtotal * (sales_gst_pct / 100.0)
        grand_total = subtotal + gst_val

        if sale_mode == "Strips / Packets" and qty_num > available_strips:
          st.error("Error: Not enough stock available!")
        else:
          conn = get_connection()
          cursor = conn.cursor()
          cursor.execute(
              "UPDATE retail_medicines SET strips_count = strips_count - ? WHERE"
              " item_name = ?",
              (total_strips_to_deduct, item_sel),
          )
          cursor.execute(
              """
                        INSERT INTO transactions (tx_type, category, item_name, qty_units, total_amount, gst_amount, net_amount, tx_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  "Sales",
                  "Retail POS",
                  item_sel,
                  qty_str,
                  subtotal,
                  gst_val,
                  grand_total,
                  str(datetime.now()),
              ),
          )
          conn.commit()
          conn.close()

          st.success("Sale completed successfully!")

          # --- HALF A4 / A5 PRINT FORMAT PREVIEW ---
          st.markdown("---")
          st.markdown(
              "### 🖨️ Tax Invoice (Half A4 / A5 Print Format for Print)"
          )
          invoice_html = f"""
                    <div style="border: 2px dashed #333; padding: 15px; width: 60%; font-family: Arial, sans-serif; background: #fff; color: #000;">
                        <h3 style="text-align: center; margin: 0;">KULU SMART MEDICAL STORE</h3>
                        <p style="text-align: center; font-size: 12px; margin: 2px;">Link Road, Cuttack | Ph: 9853XXXXXX</p>
                        <hr>
                        <p><b>Customer:</b> {customer_name}</p>
                        <p><b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}</p>
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                            <tr style="border-bottom: 1px solid #000;">
                                <th style="text-align: left;">Item</th>
                                <th style="text-align: center;">Qty</th>
                                <th style="text-align: right;">Amount (₹)</th>
                            </tr>
                            <tr>
                                <td>{item_sel}</td>
                                <td style="text-align: center;">{qty_str}</td>
                                <td style="text-align: right;">{subtotal:.2f}</td>
                            </tr>
                        </table>
                        <hr>
                        <p style="text-align: right; margin: 2px;"><b>Subtotal:</b> ₹{subtotal:.2f}</p>
                        <p style="text-align: right; margin: 2px;"><b>GST ({sales_gst_pct}%):</b> ₹{gst_val:.2f}</p>
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
    st.subheader("GST Breakdown")
    col1, col2 = st.columns(2)

    sales_gst = df_tx[df_tx["tx_type"] == "Sales"]["gst_amount"].sum()
    purchase_gst = df_tx[df_tx["tx_type"] == "Purchase"]["gst_amount"].sum()
    net_gst_payable = sales_gst - purchase_gst

    col1.metric("Output GST (Collected on Sales)", f"₹ {sales_gst:,.2f}")
    col2.metric("Input GST (Paid on Purchases)", f"₹ {purchase_gst:,.2f}")

    st.markdown(
        f"### Net GST Payable to Government: **₹ {net_gst_payable:,.2f}**"
    )
  else:
    st.info("No transaction data available for GST calculation.")

# --- 6. BALANCE SHEET ---
elif menu == "⚖️ Balance Sheet":
  st.subheader("⚖️ Financial Balance Sheet")

  conn = get_connection()
  try:
    df_tx = pd.read_sql("SELECT * FROM transactions", conn)
  except Exception:
    df_tx = pd.DataFrame()
  conn.close()

  total_sales = (
      df_tx[df_tx["tx_type"] == "Sales"]["net_amount"].sum()
      if not df_tx.empty
      else 0.0
  )
  total_purchase = (
      df_tx[df_tx["tx_type"] == "Purchase"]["net_amount"].sum()
      if not df_tx.empty
      else 0.0
  )

  col1, col2 = st.columns(2)

  with col1:
    st.markdown("### 📥 Inflows (Revenue)")
    st.metric("Total Sales Revenue", f"₹ {total_sales:,.2f}")

  with col2:
    st.markdown("### 📤 Outflows (Expenses)")
    st.metric("Total Purchase Expenditure", f"₹ {total_purchase:,.2f}")

  st.markdown("---")
  gross_margin = total_sales - total_purchase
  st.metric("Estimated Gross Business Margin", f"₹ {gross_margin:,.2f}")
  st.success(
      "Balance sheet is generated automatically without affecting your"
      " historical data."
  )
