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
        menu = st.sidebar.selectbox("Navigation", ["Admin Dashboard", "15-Min Long Video Studio", "Home"])
    else:
        menu = st.sidebar.selectbox("Navigation", ["15-Min Long Video Studio", "Home"])
else:
    menu = st.sidebar.selectbox("Navigation", ["Home", "Login", "Register"])

# ----------------- HOME PAGE -----------------
if menu == "Home":
    st.title("ସ୍ୱାଗତ କରୁଛୁ Kulu AI Video Studio କୁ! 🚀")
    st.write("ଏଠାରୁ ଆପଣ ୧୫ ମିନିଟ୍ ପର୍ଯ୍ୟନ୍ତ ଲମ୍ବା AI ଭିଡିଓ ଏବଂ ସ୍କ୍ରିପ୍ଟ ତିଆରି କରିପାରିବେ।")
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

# ----------------- 15-MIN LONG VIDEO STUDIO (Dynamic Prompt Based) -----------------
elif menu == "15-Min Long Video Studio":
    st.title("⏱️ Kulu AI 15-Minute Long Video Creator")
    
    if st.session_state.logged_in:
        st.info(f"Welcome, **{st.session_state.current_user}**! Design your complete 15-minute cinematic video project below.")
        
        video_title = st.text_input("Video Topic / Main Storyline", value="motu patlu dance")
        video_genre = st.selectbox("Select Video Genre", ["Animation & Cartoon", "Action & Adventure", "Luxury & Cinematic Travel", "Mystery & Drama"])
        main_prompt = st.text_area("Detailed Story Prompt:", value="Golden-hour lighting, realistic human movement, natural skin texture, highly detailed costumes, vibrant atmosphere, cinematic composition, 4K ultra-realistic quality...")
        
        if st.button("🎬 Generate 15-Minute Epic Video Blueprint"):
            if video_title and main_prompt:
                with st.spinner("AI is crafting your 15-minute multi-scene master script based on your prompt... Please wait!"):
                    st.success("✨ 15-Minute Video Masterplan Generated Successfully!")
                    
                    st.markdown(f"### 📌 Project: {video_title} ({video_genre})")
                    st.write("**Total Duration:** 15 Minutes (10 Sequential Scenes tailored to your prompt)")
                    
                    st.markdown("---")
                    st.markdown(f"### 🎞️ 15-Minute Scene-by-Scene Breakdown for '{video_title}':")
                    
                    # Dynamically generate 10 scenes based on user's custom title & prompt
                    time_slots = [
                        ("00:00 - 01:30", f"Scene 1: Introduction of {video_title}. Setting up the environment with: {main_prompt[:60]}..."),
                        ("01:30 - 03:00", f"Scene 2: Character entry and primary action sequence focusing on {video_title}."),
                        ("03:00 - 04:30", f"Scene 3: Developing the core plot with vibrant atmosphere and detailed movements."),
                        ("04:30 - 06:00", f"Scene 4: Mid-point twist and engaging interaction based on user prompt."),
                        ("06:00 - 07:30", f"Scene 5: High-energy sequence showcasing cinematic composition and 4K quality."),
                        ("07:30 - 09:00", f"Scene 6: Secondary characters or supporting elements joining the scene."),
                        ("09:00 - 10:30", f"Scene 7: Dramatic buildup and emotional peak of the {video_title} story."),
                        ("10:30 - 12:00", f"Scene 8: Resolution steps and transition towards the grand finale."),
                        ("12:00 - 13:30", f"Scene 9: Climax performance reflecting the core theme: '{main_prompt[:50]}...'"),
                        ("13:30 - 15:00", f"Scene 10: Grand conclusion, credits, and final cinematic outro shot.")
                    ]
                    
                    for time_slot, desc in time_slots:
                        st.markdown(f"⏱️ **[{time_slot}]** - {desc}")
                    
                    st.markdown("---")
                    st.info("🎥 Previewing Master Render for Your Custom 15-Min Video:")
                    st.video("https://www.w3schools.com/html/mov_bbb.mp4")
                    
                    st.download_button(
                        label="📥 Download Complete 15-Min Script & Timeline (.txt)",
                        data=f"Project: {video_title}\nGenre: {video_genre}\nPrompt: {main_prompt}\n\n15-Minute Dynamic Multi-Scene Blueprint generated via Kulu AI Studio.",
                        file_name="kulu_15min_custom_video_project.txt",
                        mime="text/plain"
                    )
                    st.balloons()
            else:
                st.warning("ଦୟାକରି ଟାଇଟଲ୍ ଏବଂ ପ୍ରମ୍ପ୍ଟ ଭରଣ କରନ୍ତୁ!")
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
