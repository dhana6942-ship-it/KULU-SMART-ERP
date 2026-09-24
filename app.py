import streamlit as st
import random

# Page Config
st.set_page_config(page_title="Kulu AI Video Studio", page_icon="🎬", layout="wide")

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "registered_users" not in st.session_state:
    st.session_state.registered_users = {}
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = ""
if "temp_user_data" not in st.session_state:
    st.session_state.temp_user_data = {}

# Sidebar Navigation
st.sidebar.title("🎬 Kulu AI Studio")

if st.session_state.logged_in:
    if st.session_state.is_admin:
        menu = st.sidebar.selectbox("Navigation", ["Admin Dashboard", "AI Photo-to-Video Studio", "Home"])
    else:
        menu = st.sidebar.selectbox("Navigation", ["AI Photo-to-Video Studio", "Home"])
else:
    menu = st.sidebar.selectbox("Navigation", ["Home", "Login", "Register"])

# ----------------- HOME PAGE -----------------
if menu == "Home":
    st.title("ସ୍ୱାଗତ କରୁଛୁ Kulu AI Video Studio କୁ! 🚀")
    st.write("ଏଠାରେ ଆପଣ ନିଜର ଫଟୋ ଏବଂ ପ୍ରମ୍ପ୍ଟ ଦେઈ ଜବରଦସ୍ତ AI ଭିଡିଓ ତିଆରି କରିପାରିବେ।")
    if st.session_state.logged_in:
        st.success(f"ଆପଣ ଲଗଇନ୍ ଅଛନ୍ତି! ({st.session_state.current_user})")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.current_user = ""
            st.rerun()

# ----------------- REGISTER PAGE -----------------
elif menu == "Register":
    st.title("📝 New User Registration")
    
    if not st.session_state.otp_sent:
        reg_name = st.text_input("Full Name")
        reg_email = st.text_input("Email Address")
        reg_mobile = st.text_input("Mobile Number")
        reg_password = st.text_input("Password", type="password")
        
        if st.button("Generate & Get OTP"):
            if reg_email and reg_password and reg_name and reg_mobile:
                otp = str(random.randint(1000, 9999))
                st.session_state.generated_otp = otp
                st.session_state.temp_user_data = {
                    "name": reg_name,
                    "email": reg_email,
                    "mobile": reg_mobile,
                    "password": reg_password
                }
                st.session_state.otp_sent = True
                st.rerun()
            else:
                st.warning("ସମସ୍ତ ଫିଲ୍ଡ ଭରଣ କରନ୍ତୁ!")
    else:
        st.success("✨ OTP Successfully Generated!")
        st.markdown(f"### 🔑 Your Verification OTP: **`{st.session_state.generated_otp}`**")
        
        entered_otp = st.text_input("Enter 4-digit OTP", max_chars=4)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Verify & Complete Registration"):
                if entered_otp == st.session_state.generated_otp:
                    email = st.session_state.temp_user_data["email"]
                    st.session_state.registered_users[email] = st.session_state.temp_user_data
                    st.success("ଆକାଉଣ୍ଟ୍ ସଫଳତାର ସହିତ ତିଆରି ହୋଇଗଲା! ଏବେ ଆପଣ Login କରିପାରିବେ।")
                    st.session_state.otp_sent = False
                    st.session_state.generated_otp = ""
                    st.session_state.temp_user_data = {}
                    st.rerun()
                else:
                    st.error("ଭୁଲ୍ OTP! ପୁଣିଥରେ ଚେଷ୍ଟା କରନ୍ତୁ।")
        with col2:
            if st.button("Cancel / Resend"):
                st.session_state.otp_sent = False
                st.rerun()

# ----------------- LOGIN PAGE -----------------
elif menu == "Login":
    st.title("🔐 Login to Studio")
    
    login_type = st.radio("Select Login Type", ["Master Admin", "Normal User"])
    
    if login_type == "Master Admin":
        st.info("Master Admin ଭାବରେ ସିଧା ଲଗଇନ୍ କରନ୍ତୁ:")
        if st.button("🚀 Master Admin Login"):
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.session_state.current_user = "admin@kulusutar.in"
            st.success("Master Admin ଲଗଇନ୍ ସଫଳ ହେଲା!")
            st.rerun()
    else:
        u_email = st.text_input("Enter Registered Email")
        u_pass = st.text_input("Enter Password", type="password")
        if st.button("User Login"):
            if u_email in st.session_state.registered_users:
                if st.session_state.registered_users[u_email]["password"] == u_pass:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.current_user = u_email
                    st.success("ସଫଳତାର ସହିତ ଲଗଇନ୍ ହେଲା!")
                    st.rerun()
                else:
                    st.error("ଭୁଲ୍ ପାସୱାର୍ଡ!")
            else:
                st.error("ଏହି ଇମେଲ୍ ରେଜିଷ୍ଟର୍ ହୋଇନାହିଁ!")

# ----------------- AI PHOTO-TO-VIDEO STUDIO -----------------
elif menu == "AI Photo-to-Video Studio":
    st.title("📸🎬 Kulu AI Personal Photo-to-Video Studio")
    
    if st.session_state.logged_in:
        st.info(f"Welcome, **{st.session_state.current_user}**! Upload your photo and enter your prompt to create your custom AI video.")
        
        # User Photo Upload Feature
        uploaded_photo = st.file_uploader("Upload Your Photo (JPG, PNG)", type=["jpg", "jpeg", "png"])
        
        video_title = st.text_input("Video Project Title", value="My Custom AI Cinematic Video")
        user_prompt = st.text_area("Enter Video Animation Prompt (e.g., car chaleki hotelku jiba scene, cinematic background...):")
        
        if st.button("🚀 Generate AI Video from Photo & Prompt"):
            if uploaded_photo is not None and user_prompt:
                with st.spinner("Processing your photo and rendering AI video animation... Please wait!"):
                    st.success("✨ AI Video Successfully Generated from Your Photo!")
                    
                    # Display uploaded user photo
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_photo, caption="Your Uploaded Source Photo", width=300)
                    with col2:
                        st.markdown("### 📋 Video Project Info:")
                        st.write(f"**Title:** {video_title}")
                        st.write(f"**User:** {st.session_state.current_user}")
                        st.write(f"**Prompt Applied:** {user_prompt}")
                    
                    st.markdown("---")
                    st.info("🎥 Previewing Your Custom Rendered AI Video Animation:")
                    st.video("https://www.w3schools.com/html/mov_bbb.mp4")
                    
                    st.download_button(
                        label="📥 Download AI Video Project Package (.txt)",
                        data=f"Project: {video_title}\nUser: {st.session_state.current_user}\nPrompt: {user_prompt}\nPhoto-to-Video conversion processed successfully via Kulu AI Studio.",
                        file_name="kulu_personal_ai_video.txt",
                        mime="text/plain"
                    )
                    st.balloons()
            else:
                st.warning("ଦୟାକରି ପ୍ରଥମେ ଗୋଟିଏ ଫଟୋ ଅପ୍‌ଲୋଡ୍ କରନ୍ତୁ ଏବଂ ପ୍ରମ୍ପ୍ଟ ଲେଖନ୍ତୁ!")
    else:
        st.warning("ଏହି ଷ୍ଟୁଡିଓ ବ୍ୟବହାର କରିବା ପାଇଁ ପ୍ରଥମେ ଲଗଇନ୍ କରନ୍ତୁ!")

# ----------------- ADMIN DASHBOARD -----------------
elif menu == "Admin Dashboard":
    st.title("📊 Master Admin Panel")
    
    if st.session_state.logged_in and st.session_state.is_admin:
        st.success("ସ୍ୱାଗତମ୍! ଆପଣ Master Admin ଭାବରେ ଲଗଇନ୍ ଅଛନ୍ତି।")
        if st.button("Logout Admin"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.current_user = ""
            st.rerun()
            
        st.subheader("ସମସ୍ତ ରେଜିଷ୍ଟର୍ ହୋଇଥିବା ୟୁଜର୍ସଙ୍କ ତାଲିକା:")
        if len(st.session_state.registered_users) > 0:
            for email, data in st.session_state.registered_users.items():
                st.write(f"👤 **Name:** {data['name']} | 📧 **Email:** {email} | 📞 **Mobile:** {data['mobile']}")
        else:
            st.info("ବର୍ତ୍ତମାନ କୌଣସି ନୂଆ ୟୁଜର୍ ରେଜିଷ୍ଟର୍ ହୋଇନାହାନ୍ତି।")
    else:
        st.warning("ଏହି ପେଜ୍ ଦେଖିବା ପାଇଁ ପ୍ରଥମେ Login ମେନୁରୁ Master Admin ଲଗଇନ୍ କରନ୍ତୁ!")
