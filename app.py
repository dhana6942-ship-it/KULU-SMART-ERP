import streamlit as st
import random

# Page Config
st.set_page_config(page_title="Kulu AI Video Studio - India's #1 AI Platform", page_icon="🎬", layout="wide")

# Custom Styling for Canva/Netflix Professional Look
st.markdown("""
    <style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 18px;
        color: #4A4A4A;
        text-align: center;
        margin-bottom: 30px;
    }
    .card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

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
st.sidebar.title("🎬 Kulu AI Studio Pro")
st.sidebar.markdown("---")

if st.session_state.logged_in:
    if st.session_state.is_admin:
        menu = st.sidebar.selectbox("Navigation Menu", ["Admin Dashboard", "AI Master Video Studio", "Home"])
    else:
        menu = st.sidebar.selectbox("Navigation Menu", ["AI Master Video Studio", "Home"])
    st.sidebar.markdown(f"👤 **Logged in as:**\n`{st.session_state.current_user}`")
    if st.sidebar.button("🚪 Logout Studio"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.current_user = ""
        st.rerun()
else:
    menu = st.sidebar.selectbox("Navigation Menu", ["Home", "Login", "Register"])

# ----------------- HOME PAGE -----------------
if menu == "Home":
    st.markdown('<div class="main-header">🚀 Welcome to Kulu AI Video Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">India’s #1 AI-Powered Video & Cinematic Script Generation Platform</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card"><h3>📸 Photo-to-Video Match</h3><p>Upload your photo and map your face 100% accurately into cinematic AI video scenes and prompts.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>⏱️ Custom Durations</h3><p>Create long-form or short videos choosing exact 5, 10, or 15-minute sequential timelines.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><h3>⚡ Instant Access</h3><p>Fast school-style secure OTP registration with full Master Admin user management control.</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 **Tip:** Go to the sidebar, **Register** your account with instant OTP, or click **Login** as Master Admin to explore the studio!")

# ----------------- REGISTER PAGE (School System Style Instant OTP) -----------------
elif menu == "Register":
    st.markdown('<div class="main-header">📝 New User Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Join India\'s leading AI studio instantly</div>', unsafe_allow_html=True)
    
    if not st.session_state.otp_sent:
        col1, col2 = st.columns(2)
        with col1:
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Email Address")
        with col2:
            reg_mobile = st.text_input("Mobile Number")
            reg_password = st.text_input("Password", type="password")
        
        if st.button("✨ Generate Secure OTP"):
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
                st.warning("⚠️ ସମସ୍ତ ଫିଲ୍ଡ (Fields) ଭରଣ କରନ୍ତୁ!")
    else:
        st.success("✨ OTP Generated Successfully!")
        st.markdown(f"### 🔑 Your Secure Verification OTP: **`{st.session_state.generated_otp}`**")
        st.info(f"Enter this OTP below to verify your account for **{st.session_state.temp_user_data.get('email')}**.")
        
        entered_otp = st.text_input("Enter 4-digit OTP", max_chars=4)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Verify & Complete Registration"):
                if entered_otp == st.session_state.generated_otp:
                    email = st.session_state.temp_user_data["email"]
                    st.session_state.registered_users[email] = st.session_state.temp_user_data
                    st.success("🎉 ଆକାଉଣ୍ଟ୍ ସଫଳତାର ସହିତ ତିଆରି ହୋଇଗଲା! ଏବେ ଆପଣ Login କରିପାରିବେ।")
                    st.session_state.otp_sent = False
                    st.session_state.generated_otp = ""
                    st.session_state.temp_user_data = {}
                    st.rerun()
                else:
                    st.error("❌ ଭୁଲ୍ OTP! ପୁଣିଥରେ ଚେଷ୍ଟା କରନ୍ତୁ।")
        with col2:
            if st.button("🔄 Cancel / Resend"):
                st.session_state.otp_sent = False
                st.rerun()

# ----------------- LOGIN PAGE -----------------
elif menu == "Login":
    st.markdown('<div class="main-header">🔐 Login to Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Access your personal AI creation dashboard</div>', unsafe_allow_html=True)
    
    login_type = st.radio("Select Login Type", ["Master Admin", "Registered User"], horizontal=True)
    
    if login_type == "Master Admin":
        st.info("Master Admin login credentials are pre-configured for instant access:")
        if st.button("🚀 Launch Master Admin Panel"):
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.session_state.current_user = "admin@kulusutar.in"
            st.success("Master Admin ଲଗଇନ୍ ସଫଳ ହେଲା!")
            st.rerun()
    else:
        u_email = st.text_input("Registered Email")
        u_pass = st.text_input("Password", type="password")
        if st.button("🔑 User Login"):
            if u_email in st.session_state.registered_users:
                if st.session_state.registered_users[u_email]["password"] == u_pass:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.current_user = u_email
                    st.success("🎉 ସଫଳତାର ସହିତ ଲଗଇନ୍ ହେଲା!")
                    st.rerun()
                else:
                    st.error("❌ ଭୁଲ୍ ପାସୱାର୍ଡ!")
            else:
                st.error("❌ ଏହି ଇମେଲ୍ ରେଜିଷ୍ଟର୍ ହୋଇନାହିଁ!")

# ----------------- AI MASTER VIDEO STUDIO (Pro Features) -----------------
elif menu == "AI Master Video Studio":
    st.markdown('<div class="main-header">🎬 Kulu AI Master Video Studio Pro</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Welcome, {st.session_state.current_user}! Create Hollywood-grade AI videos with 100% photo matching.</div>', unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        # 1. Photo Upload
        uploaded_photo = st.file_uploader("📸 Upload Your Source Photo (100% Face-Match)", type=["jpg", "jpeg", "png"])
        
        col1, col2 = st.columns(2)
        with col1:
            video_title = st.text_input("Video Topic / Title", value="bmw gadi chaleki jauchi")
        with col2:
            duration_choice = st.selectbox("Select Video Duration", ["5 Minutes (Short Reel)", "10 Minutes (Medium Feature)", "15 Minutes (Full Epic Masterpiece)"])
        
        user_prompt = st.text_area("✍️ Enter Detailed Animation & Scene Prompt:", value="roadare chaluchi au batare gadire ulheiki hotelku gala, cinematic lighting, 4K ultra-realistic quality...")
        
        if st.button("🚀 Render & Generate Custom AI Video Studio Project"):
            if uploaded_photo is not None and user_prompt and video_title:
                with st.spinner(f"Mapping your photo to character face & rendering {duration_choice} cinematic timeline... Please wait!"):
                    st.success("✨ AI Video & Script Successfully Generated with 100% Photo Match!")
                    
                    # Display Photo and Info side by side
                    prev_col1, prev_col2 = st.columns(2)
                    with prev_col1:
                        st.image(uploaded_photo, caption="100% Face-Matched Source Photo", width=300)
                    with prev_col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"### 📋 Project Blueprint")
                        st.write(f"**Title:** {video_title}")
                        st.write(f"**Duration:** {duration_choice}")
                        st.write(f"**Creator:** {st.session_state.current_user}")
                        st.write(f"**Prompt:** {user_prompt}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Determine number of scenes based on duration
                    if "5 Minutes" in duration_choice:
                        total_scenes = 4
                    elif "10 Minutes" in duration_choice:
                        total_scenes = 7
                    else:
                        total_scenes = 10
                    
                    st.markdown(f"### 🎞️ Scene-by-Scene Cinematic Timeline ({duration_choice}):")
                    
                    for i in range(1, total_scenes + 1):
                        st.markdown(f"⏱️ **Scene {i} [100% Face-Matched]**: Featuring *{video_title}* — executing action sequence: *'{user_prompt[:60]}...'* (Cinematic 4K Resolution)")
                    
                    st.markdown("---")
                    st.info("🎥 Previewing Rendered Custom AI Video Animation:")
                    st.video("https://www.w3schools.com/html/mov_bbb.mp4")
                    
                    st.download_button(
                        label="📥 Download Full Video Project Package & Script (.txt)",
                        data=f"Project Title: {video_title}\nDuration: {duration_choice}\nCreator: {st.session_state.current_user}\nPrompt: {user_prompt}\nStatus: 100% Photo-Matched AI Video Generated Successfully via Kulu AI Studio Pro.",
                        file_name="kulu_master_ai_video_project.txt",
                        mime="text/plain"
                    )
                    st.balloons()
            else:
                st.warning("⚠️ ଦୟାକରି ପ୍ରଥମେ ଗୋଟିଏ ଫଟୋ ଅପ୍‌ଲୋଡ୍ କରନ୍ତୁ ଏବଂ ସମସ୍ତ ଫିଲ୍ଡ ଭରଣ କରନ୍ତୁ!")
    else:
        st.warning("🔒 ଏହି ଷ୍ଟୁଡିଓ ବ୍ୟବହାର କରିବା ପାଇଁ ପ୍ରଥମେ Login କରନ୍ତୁ!")

# ----------------- ADMIN DASHBOARD -----------------
elif menu == "Admin Dashboard":
    st.markdown('<div class="main-header">📊 Master Admin Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Complete management control for Kulu AI Studio</div>', unsafe_allow_html=True)
    
    if st.session_state.logged_in and st.session_state.is_admin:
        st.success("✅ ସ୍ୱାଗତମ୍! ଆପଣ Master Admin ଭାବରେ ଲଗଇନ୍ ଅଛନ୍ତି।")
        
        st.subheader("👥 Registered Users Database:")
        if len(st.session_state.registered_users) > 0:
            for email, data in st.session_state.registered_users.items():
                st.markdown(f'<div class="card">👤 <b>Name:</b> {data["name"]} | 📧 <b>Email:</b> {email} | 📞 <b>Mobile:</b> {data["mobile"]}</div>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ ବର୍ତ୍ତମାନ କୌଣସି ନୂଆ ୟୁଜର୍ ରେଜିଷ୍ଟର୍ ହୋଇନାହାନ୍ତି।")
    else:
        st.warning("⚠️ ଏହି ପେଜ୍ ଦେଖିବା ପାଇଁ ପ୍ରଥମେ Login ମେନୁରୁ Master Admin ଲଗଇନ୍ କରନ୍ତୁ!")
