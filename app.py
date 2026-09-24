import streamlit as st
import time

# ୱେବସାଇଟ୍ ସେଟିଂସ୍
st.set_page_config(page_title="Kulu AI Video Studio", layout="wide")

# Custom CSS (ପ୍ରଫେସନାଲ୍ SaaS ଲୁକ୍ ପାଇଁ)
st.markdown("""
<style>
.main-title {text-align: center; color: #6d28d9; font-size: 3rem; font-weight: bold;}
.sub-title {text-align: center; color: #4b5563; font-size: 1.2rem; margin-bottom: 30px;}
.price-card {border: 2px solid #e5e7eb; border-radius: 10px; padding: 20px; text-align: center; background-color: #f9fafb; transition: 0.3s;}
.price-card:hover {border-color: #6d28d9; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); transform: translateY(-5px);}
</style>
""", unsafe_allow_html=True)

# Session State ପାଇଁ Login ଟ୍ରାକିଂ
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False

# ----------------- HOME PAGE (LOGGED OUT) -----------------
if not st.session_state.user_logged_in:
    st.markdown("<div class='main-title'>Kulu AI Video Studio 🚀</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Text ରୁ 15 ମିନିଟ୍ ର ପ୍ରଫେସନାଲ୍ AI ଭିଡିଓ ବନାନ୍ତୁ - ଯେକୌଣସି ଭାଷାରେ!</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login / Register", "💎 Pricing Plans", "🌐 Features"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### 🔑 User Login")
            phone = st.text_input("Mobile Number")
            password = st.text_input("Password", type="password")
            if st.button("Login securely", type="primary"):
                if phone and password:
                    st.success("Login Successful!")
                    st.session_state.user_logged_in = True
                    st.rerun()
                else:
                    st.error("ଦୟାକରି ଫୋନ୍ ନମ୍ବର ଏବଂ ପାସୱାର୍ଡ ଦିଅନ୍ତୁ।")
        with col2:
            st.markdown("### 🎁 New User? Free Trial")
            st.info("ଆଜି ଆକାଉଣ୍ଟ ଖୋଲନ୍ତୁ ଏବଂ 1 ଟି ଭିଡିଓ ବନେଇବାର Free Credit ପାଆନ୍ତୁ!")
            n_name = st.text_input("Full Name")
            n_phone = st.text_input("Mobile Number (New)")
            if st.button("Create Account & Get Free Credit"):
                st.success("Account Created! ଆପଣଙ୍କୁ 1 Free Credit ମିଳିଛି। ଦୟାକରି Login କରନ୍ତୁ।")
                
    with tab2:
        st.subheader("Choose Your Credit Plan (Pay with UPI)")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<div class='price-card'><h3>Starter</h3><h2>₹99</h2><p>1 Video (Up to 15 mins)</p><p>Standard Quality</p><button style='width:100%;'>Buy Now</button></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='price-card' style='border-color:#6d28d9;'><h3>Creator (Popular)</h3><h2>₹499</h2><p>10 Videos</p><p>HD Quality + All Languages</p><button style='width:100%; background:#6d28d9; color:white;'>Buy Now</button></div>", unsafe_allow_html=True)
        with c3:
            st.markdown("<div class='price-card'><h3>Pro Agency</h3><h2>₹999</h2><p>30 Videos</p><p>4K Quality + No Watermark</p><button style='width:100%;'>Buy Now</button></div>", unsafe_allow_html=True)

# ----------------- APP PAGE (LOGGED IN) -----------------
else:
    st.sidebar.title("Kulu AI Studio")
    st.sidebar.success("🟢 Online | Balance: 1 Credit")
    if st.sidebar.button("Logout"):
        st.session_state.user_logged_in = False
        st.rerun()
        
    st.title("🎬 Create New AI Video")
    st.info("ଆପଣଙ୍କର କାହାଣୀ ଲେଖନ୍ତୁ, ଭାଷା ବାଛନ୍ତୁ ଆଉ ମ୍ୟାଜିକ୍ ଦେଖନ୍ତୁ!")
    
    # ତୁମର ମାଷ୍ଟରଷ୍ଟ୍ରୋକ୍: ସବୁ ଭାଷାର ଅପ୍ସନ୍!
    lang_col, char_col = st.columns(2)
    language = lang_col.selectbox("🗣️ Select Video Language", [
        "Odia (ଓଡ଼ିଆ)", "Hindi (हिंदी)", "English", 
        "Bengali (বাংলা)", "Telugu (తెలుగు)", "Tamil (தமிழ்)"
    ])
    character = char_col.selectbox("🦸‍♂️ Select Character", [
        "Motu & Patlu Style", "Professional News Anchor", 
        "Anime Style", "Storyteller Grandpa"
    ])
    
    script = st.text_area("📝 Type your story or script here...", height=200, placeholder="ଉଦାହରଣ: ଏକଦା ଗୋଟିଏ ଗାଁରେ ଦୁଇଜଣ ସାଙ୍ଗ ରହୁଥିଲେ...")
    
    if st.button("✨ Generate Video Now (Costs 1 Credit)", type="primary"):
        if script:
            with st.spinner(f"AI is creating your video in {language}... Please wait."):
                # ଏଠାରେ ଆମେ ଭବିଷ୍ୟତରେ ଅସଲି AI API କୋଡ୍ ଯୋଡ଼ିବା
                time.sleep(3) 
                st.success("✅ Video Generation Successful! (This is a UI demo)")
                # ଡେମୋ ପାଇଁ ଗୋଟିଏ ସାଧାରଣ ଭିଡିଓ ଦେଖାଉଛି
                st.video("https://www.w3schools.com/html/mov_bbb.mp4") 
        else:
            st.error("ଦୟାକରି ପ୍ରଥମେ କିଛି କାହାଣୀ ବା ସ୍କ୍ରିପ୍ଟ ଲେଖନ୍ତୁ!")
