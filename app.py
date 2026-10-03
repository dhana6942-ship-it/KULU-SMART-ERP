import streamlit as st

# ୱେବସାଇଟ୍ ର ଟାଇଟଲ୍ ଏବଂ ଡିଜାଇନ୍
st.set_page_config(page_title="AI Video Dubbing Pro", page_icon="🎥", layout="centered")

# --- ଲାଇସେନ୍ସ କି ଏବଂ ଡେମୋ ସିଷ୍ଟମ୍ (Sidebar) ---
st.sidebar.header("🔑 License Activation")
st.sidebar.write("ଲମ୍ବା ଭିଡିଓ ପାଇଁ ପ୍ରୋ-କି (Pro Key) ବ୍ୟବହାର କରନ୍ତୁ।")

# ୟୁଜର୍ ଲାଇସେନ୍ସ କି ଏଣ୍ଟର୍ କରିବେ (ପାସୱାର୍ଡ ଭଳି ଲୁଚି ରହିବ)
user_key = st.sidebar.text_input("Enter License Key:", type="password")

# ଏହା ହେଉଛି ଆପଣଙ୍କର ସିକ୍ରେଟ୍ ଲାଇସେନ୍ସ କି
VALID_PRO_KEY = "KULU-PRO-2026"

is_pro_user = False
if user_key == VALID_PRO_KEY:
    st.sidebar.success("✅ Pro Version Activated!")
    is_pro_user = True
elif user_key != "":
    st.sidebar.error("❌ Invalid Key! Please try again.")

if not is_pro_user:
    st.sidebar.warning("⚠️ Demo Mode Active (Max 5 mins)")

# --- ମୁଖ୍ୟ ଡ୍ୟାସବୋର୍ଡ ---
st.title("🎥 AI Video Translation & Dubbing")
st.write("ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ ଆଉ ଯେକୌଣସି ଭାଷାରେ ବଦଳାନ୍ତୁ!")
st.markdown("---")

st.subheader("ଭିଡିଓର ସମୟସୀମା ବାଛନ୍ତୁ:")

# ଲାଇସେନ୍ସ ଅନୁସାରେ ଅପ୍ସନ୍ ଦେଖାଇବା
if is_pro_user:
    video_duration = st.radio(
        "ଆପଣଙ୍କ ଭିଡିଓ କେତେ ଲମ୍ବା ଅଟେ? (Pro Access)",
        ("⏱️ ୧୦ ସେକେଣ୍ଡ ରୁ ୫ ମିନିଟ୍ (Local Languages)", "⏳ ୫ ମିନିଟ୍ ରୁ ୪ ଘଣ୍ଟା (All Global Languages)")
    )
else:
    video_duration = st.radio(
        "ଆପଣଙ୍କ ଭିଡିଓ କେତେ ଲମ୍ବା ଅଟେ? (Demo Access)",
        ("⏱️ ୧୦ ସେକେଣ୍ଡ ରୁ ୫ ମିନିଟ୍ (Local Languages)",)
    )
    st.info("💡 ୪ ଘଣ୍ଟା ପର୍ଯ୍ୟନ୍ତ ଭିଡିଓ ଅପଲୋଡ୍ କରିବାକୁ ଏବଂ ସବୁ ଭାଷା ପାଇବାକୁ ଲାଇସେନ୍ସ କି (License Key) ବ୍ୟବହାର କରନ୍ତୁ।")

# ଭିଡିଓ ଲମ୍ବ ଅନୁସାରେ ଭାଷା ବାଛିବା
if "୪ ଘଣ୍ଟା" in video_duration:
    language_options = ("English (ଇଂରାଜୀ)", "Spanish (ସ୍ପାନିସ୍)", "French (ଫ୍ରେଞ୍ଚ)", "German (ଜର୍ମାନ)", "Arabic (ଆରବିକ୍)", "ଓଡ଼ିଆ (Odia)", "ହିନ୍ଦୀ (Hindi)")
else:
    language_options = ("ଓଡ଼ିଆ (Odia)", "ହିନ୍ଦୀ (Hindi)", "ବେଙ୍ଗଲୀ (Bengali)", "ତେଲୁଗୁ (Telugu)", "ତାମିଲ (Tamil)", "ମରାଠୀ (Marathi)", "ଭୋଜପୁରୀ (Bhojpuri)")

target_language = st.selectbox("ଆପଣ ଭିଡିଓଟିକୁ କେଉଁ ଭାଷାରେ ଡବିଂ କରିବାକୁ ଚାହୁଁଛନ୍ତି?", language_options)

st.markdown("---")

# ଭିଡିଓ ଅପଲୋଡ୍
uploaded_video = st.file_uploader("ଏଠାରେ ଆପଣଙ୍କ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ (mp4, mov)", type=["mp4", "mov"])

# କନଭର୍ଟ ବଟନ୍
if st.button("ଭିଡିଓ କନଭର୍ଟ କରନ୍ତୁ 🚀"):
    if uploaded_video is not None:
        st.success("ଭିଡିଓ ସଫଳତାର ସହ ଅପଲୋଡ୍ ହେଲା!")
        if is_pro_user:
            st.info(f"✨ Pro Processing Mode: {video_duration}")
        else:
            st.info(f"⚙️ Demo Processing Mode: {video_duration}")
            
        st.warning(f"ଭିଡିଓଟିକୁ {target_language} ଭାଷାରେ ପରିବର୍ତ୍ତନ କରାଯାଉଛି... ଦୟାକରି ଅପେକ୍ଷା କରନ୍ତୁ।")
    else:
        st.error("ଦୟାକରି ପ୍ରଥମେ ଗୋଟିଏ ଭିଡିଓ ଫାଇଲ୍ ଅପଲୋଡ୍ କରନ୍ତୁ।")
