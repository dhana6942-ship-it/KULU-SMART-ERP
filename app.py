import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText

# Page Config
st.set_page_config(page_title="Kulu AI Video Studio", page_icon="🎬", layout="wide")

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "registered_users" not in st.session_state:
    st.session_state.registered_users = {}  # {email: {"name": name, "mobile": mobile, "password": password}}
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = ""
if "temp_user_data" not in st.session_state:
    st.session_state.temp_user_data = {}

# Email Sending Function (OTP)
def send_otp_email(receiver_email, otp_code):
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"
    
    subject = "Kulu AI Video Studio - Registration OTP"
    body = f"Hello,\n\nYour OTP for registration is: {otp_code}\n\nPlease enter this code to verify your account.\n\nThank You!"
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# Sidebar Navigation
st.sidebar.title("🎬 Kulu AI Studio")
menu = st.sidebar.selectbox("Navigation", ["Home", "Login", "Register", "Admin Dashboard"])

# ----------------- HOME PAGE -----------------
if menu == "Home":
    st.title("ସ୍ୱାଗତ କରୁଛୁ Kulu AI Video Studio କୁ! 🚀")
    st.write("ଏଠାରୁ ଆପଣ ଜବରଦସ୍ତ AI ଭିଡିଓ ଏବଂ କଣ୍ଟେଣ୍ଟ୍ ତିଆରି କରିପାରିବେ।")
    if st.session_state.logged_in:
        st.success(f"ଆପଣ ଲଗଇନ୍ ଅଛନ୍ତି! (Role: {'Admin (Master)' if st.session_state.is_admin else 'User'})")

# ----------------- REGISTER PAGE WITH OTP -----------------
elif menu == "Register":
    st.title("📝 New User Registration")
    
    if not st.session_state.otp_sent:
        reg_name = st.text_input("Full Name")
        reg_email = st.text_input("Email Address")
        reg_mobile = st.text_input("Mobile Number")
        reg_password = st.text_input("Password", type="password")
        
        if st.button("Send OTP"):
            if reg_email and reg_password and reg_name:
                otp = str(random.randint(1000, 9999))
                st.session_state.generated_otp = otp
                st.session_state.temp_user_data = {
                    "name": reg_name,
                    "email": reg_email,
                    "mobile": reg_mobile,
                    "password": reg_password
                }
                
                success = send_otp_email(reg_email, otp)
                if success:
                    st.session_state.otp_sent = True
                    st.success("OTP ଆପଣଙ୍କ ଇମେଲ୍‌କୁ ପଠାଯାଇଛି! ଦୟାକରି ଚେକ୍ କରନ୍ତୁ।")
                    st.rerun()
                else:
                    st.error("ମେଲ୍ ପଠାଇବାରେ ସମସ୍ୟା ହେଲା। ଦୟାକରି ଠିକ୍ Gmail credentials ଦିଅନ୍ତୁ।")
            else:
                st.warning("ସମସ୍ତ ଫିଲ୍ଡ ଭରଣ କରନ୍ତୁ!")
    else:
        st.info(f"Enter the 4-digit OTP sent to {st.session_state.temp_user_data.get('email')}")
        entered_otp = st.text_input("Enter OTP", max_chars=4)
        
        if st.button("Verify & Register"):
            if entered_otp == st.session_state.generated_otp:
                email = st.session_state.temp_user_data["email"]
                st.session_state.registered_users[email] = st.session_state.temp_user_data
                st.success("ଆକାଉଣ୍ଟ୍ ସଫଳତାର ସହିତ ତିଆରି ହୋଇଗଲା! ଏବେ ଆପଣ Login କରିପାରିବେ।")
                st.session_state.otp_sent = False
                st.session_state.generated_otp = ""
                st.session_state.temp_user_data = {}
            else:
                st.error("ଭୁଲ୍ OTP! ପୁଣିଥରେ ଚେଷ୍ଟା କରନ୍ତୁ।")

# ----------------- LOGIN PAGE (User & Master Admin) -----------------
elif menu == "Login":
    st.title("🔐 Login to Studio")
    
    login_email = st.text_input("Email or Admin ID")
    login_password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Master Admin Check
        if login_email == "admin@kulusutar.in" and login_password == "kulu12345":
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.success("Master Admin ଭାବରେ ସଫଳତାର ସହିତ ଲଗଇନ୍ ହେଲା!")
            st.rerun()
        # Normal Registered User Check
        elif login_email in st.session_state.registered_users:
            if st.session_state.registered_users[login_email]["password"] == login_password:
                st.session_state.logged_in = True
                st.session_state.is_admin = False
                st.success("ସଫଳତାର ସହିତ ଲଗଇନ୍ ହେଲା!")
                st.rerun()
            else:
                st.error("ଭୁଲ୍ ପାସୱାର୍ଡ!")
        else:
            st.error("ଏହି ଇମେଲ୍ ରେଜିଷ୍ଟର୍ ହୋଇନାହିଁ!")

# ----------------- ADMIN DASHBOARD (Master ID Panel) -----------------
elif menu == "Admin Dashboard":
    st.title("📊 Master Admin Panel")
    
    if st.session_state.logged_in and st.session_state.is_admin:
        st.subheader("ସମସ୍ତ ରେଜିଷ୍ଟର୍ ହୋଇଥିବା ୟୁଜର୍ସଙ୍କ ତାଲିକା:")
        if len(st.session_state.registered_users) > 0:
            for email, data in st.session_state.registered_users.items():
                st.write(f"👤 **Name:** {data['name']} | 📧 **Email:** {email} | 📞 **Mobile:** {data['mobile']}")
        else:
            st.info("ବର୍ତ୍ତମାନ କୌଣସି ନୂଆ ୟୁଜର୍ ରେଜିଷ୍ଟର୍ ହୋଇନାହାନ୍ତି।")
    else:
        st.warning("ଏହି ପେଜ୍ ଦେଖିବା ପାଇଁ ଆପଣଙ୍କୁ Master Admin ଭାବରେ ଲଗଇନ୍ କରିବାକୁ ପଡ଼ିବ!")
        st.text("Master Admin ID: admin@kulusutar.in")
        st.text("Master Admin Password: kulu12345")
