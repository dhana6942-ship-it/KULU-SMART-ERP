import streamlit as st
import os
import time
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from deep_translator import MyMemoryTranslator, GoogleTranslator
from gtts import gTTS

# ଟେମ୍ପରାରୀ ଫାଇଲ୍ ସେଭ୍ କରିବା ପାଇଁ ଫୋଲ୍ଡର
if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="AI Video Dubbing Pro", page_icon="🎥", layout="centered")

# --- ଲାଇସେନ୍ସ କି ---
st.sidebar.header("🔑 License Activation")
st.sidebar.write("ଲମ୍ବା ଭିଡିଓ ପାଇଁ ପ୍ରୋ-କି (Pro Key) ବ୍ୟବହାର କରନ୍ତୁ।")

user_key = st.sidebar.text_input("Enter License Key:", type="password")
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
st.write("ପ୍ରଥମେ ନିଜର ଦେଶ ବାଛନ୍ତୁ ଆଉ ସେହି ଦେଶର ସ୍ଥାନୀୟ ଭାଷାରେ ଭିଡିଓ ଡବିଂ କରନ୍ତୁ 🌍!")
st.markdown("---")

# 🌍 Country to Local Language Mapping (ଦେଶ ଅନୁସାରେ ଭାଷା)
country_language_map = {
    "India (ଭାରତ) 🇮🇳": {
        "ଓଡ଼ିଆ (Odia)": "or",
        "ହିନ୍ଦୀ (Hindi)": "hi",
        "ବେଙ୍ଗଲୀ (Bengali)": "bn",
        "ତେଲୁଗୁ (Telugu)": "te",
        "ତାମିଲ୍ (Tamil)": "ta",
        "ମରାଠୀ (Marathi)": "mr",
        "ଗୁଜରାଟୀ (Gujarati)": "gu",
        "ମାଲାୟାଲାମ୍ (Malayalam)": "ml",
        "କନ୍ନଡ (Kannada)": "kn",
        "ପଞ୍ଜାବୀ (Punjabi)": "pa",
        "ଉର୍ଦ୍ଦୁ (Urdu)": "ur"
    },
    "USA / UK / Australia 🇺🇸🇬🇧": {
        "English (ଇଂରାଜୀ)": "en"
    },
    "Spain / Latin America 🇪🇸": {
        "Spanish (ସ୍ପାନିସ୍)": "es"
    },
    "France 🇫🇷": {
        "French (ଫ୍ରେଞ୍ଚ୍)": "fr"
    },
    "Germany 🇩🇪": {
        "German (ଜର୍ମାନ)": "de"
    },
    "Japan 🇯🇵": {
        "Japanese (ଜାପାନୀ)": "ja"
    },
    "China 🇨🇳": {
        "Chinese (ଚାଇନିଜ୍)": "zh-CN"
    },
    "Middle East (Arab) 🇦🇪": {
        "Arabic (ଆରବିକ୍)": "ar"
    },
    "Russia 🇷🇺": {
        "Russian (ରୁଷିଆନ୍)": "ru"
    },
    "South Korea 🇰🇷": {
        "Korean (କୋରିଆନ୍)": "ko"
    },
    "Bangladesh 🇧🇩": {
        "Bengali (ବେଙ୍ଗଲୀ)": "bn"
    },
    "Pakistan 🇵🇰": {
        "Urdu (ଉର୍ଦ୍ଦୁ)": "ur",
        "Punjabi (ପଞ୍ଜାବୀ)": "pa",
        "Sindhi (ସିନ୍ଧି)": "sd"
    }
}

# ୧. ଦେଶ ବାଛିବାର ଅପ୍ସନ୍ (Country Selection)
selected_country = st.selectbox("🌍 ପ୍ରଥମେ ଦେଶ ବାଛନ୍ତୁ (Select Country):", list(country_language_map.keys()))

# ୨. ସେହି ଦେଶର ସ୍ଥାନୀୟ ଭାଷା ବାଛିବାର ଅପ୍ସନ୍ (Language Selection)
lang_map = country_language_map[selected_country]
target_language = st.selectbox(f"🗣️ ଏବେ {selected_country} ର ସ୍ଥାନୀୟ ଭାଷା ବାଛନ୍ତୁ:", list(lang_map.keys()))
lang_code = lang_map[target_language]

uploaded_video = st.file_uploader("ଏଠାରେ ଆପଣଙ୍କ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ (mp4)", type=["mp4"])

if st.button("ଭିଡିଓ କନଭର୍ଟ କରନ୍ତୁ 🚀"):
    if uploaded_video is not None:
        try:
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            # ଭିଡିଓ ଲୋଡ୍ 
            status_text.text("୧/୫: ଭିଡିଓ ଅପଲୋଡ୍ ହେଉଛି...")
            input_video_path = os.path.join("temp", "input_video.mp4")
            with open(input_video_path, "wb") as f:
                f.write(uploaded_video.read())
            progress_bar.progress(20)
            
            # ଅଡିଓ ବାହାର କରିବା
            status_text.text("୨/୫: ଭିଡିଓରୁ ଅଡିଓ ଅଲଗା କରାଯାଉଛି...")
            video = VideoFileClip(input_video_path)
            audio_path = os.path.join("temp", "extracted_audio.wav")
            video.audio.write_audiofile(audio_path, logger=None)
            progress_bar.progress(40)
            
            # Speech to Text
            status_text.text("୩/୫: ଅଡିଓକୁ ଲେଖାରେ ପରିଣତ କରାଯାଉଛି...")
            recognizer = sr.Recognizer()
            extracted_text = ""
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                try:
                    extracted_text = recognizer.recognize_google(audio_data)
                except Exception:
                    extracted_text = ""
            
            if not extracted_text.strip():
                extracted_text = "Welcome to my video. The audio was not clear."
            progress_bar.progress(60)
            
            # ଅନୁବାଦ (Translation)
            status_text.text(f"୪/୫: ଲେଖାକୁ {target_language} ରେ ଅନୁବାଦ କରାଯାଉଛି...")
            translated_text = ""
            
            try:
                translator = MyMemoryTranslator(source='en', target=lang_code)
                if len(extracted_text) < 500:
                    translated_text = translator.translate(extracted_text)
                else:
                    text_chunks = [extracted_text[i:i+499] for i in range(0, len(extracted_text), 499)]
                    for chunk in text_chunks:
                        translated_text += translator.translate(chunk) + " "
                        time.sleep(1)
            except Exception:
                try:
                    translated_text = GoogleTranslator(source='auto', target=lang_code).translate(extracted_text)
                except:
                    translated_text = extracted_text 
                    
            progress_bar.progress(80)
            
            # ନୂଆ ଭିଡିଓ ଓ ଭଏସ୍ ତିଆରି
            status_text.text("୫/୫: ନୂଆ ଭିଡିଓ ପ୍ରସ୍ତୁତ କରାଯାଉଛି...")
            new_audio_path = os.path.join("temp", f"new_audio_{lang_code}.mp3")
            
            try:
                tts = gTTS(text=translated_text, lang=lang_code, slow=False)
                tts.save(new_audio_path)
            except Exception:
                st.warning(f"⚠️ {target_language} ର ଭଏସ୍ ସପୋର୍ଟ ମିଳିଲା ନାହିଁ। ବର୍ତ୍ତମାନ ଇଂରାଜୀ ଭଏସ୍ ଦିଆଯାଉଛି।")
                tts = gTTS(text=translated_text, lang='en', slow=False)
                tts.save(new_audio_path)
            
            st.success("🎉 ପ୍ରୋସେସ୍ ଶେଷ ହୋଇଛି! ତଳେ ରେଜଲ୍ଟ ଦେଖନ୍ତୁ।")
            st.balloons()
            
            st.info(f"📝 AI ଧରିଥିବା ଲେଖା: {extracted_text}")
            st.warning(f"🗣️ ନୂଆ ଅନୁବାଦ: {translated_text}")

            st.markdown("### 🎵 ପ୍ରଥମେ କେବଳ ନୂଆ ଅଡିଓ ଶୁଣନ୍ତୁ (AI Voice):")
            st.audio(new_audio_path, format="audio/mp3")
            st.markdown("---")
            
            # ଶେଷ ଭିଡିଓ ପ୍ରସ୍ତୁତି
            new_audio_clip = AudioFileClip(new_audio_path)
            final_video = video.set_audio(new_audio_clip)
            
            final_video_path = os.path.join("temp", "final_output_video.mp4")
            final_video.write_videofile(final_video_path, codec="libx264", audio_codec="aac", logger=None)
            
            progress_bar.progress(100)
            status_text.empty()
            
            st.markdown("### 🎬 ନୂଆ ଭିଡିଓ ଦେଖନ୍ତୁ:")
            with open(final_video_path, "rb") as file:
                video_bytes = file.read()
                
            st.video(video_bytes)
            st.download_button(
                label=f"⬇️ ନୂଆ ଭିଡିଓ ଡାଉନଲୋଡ୍ କରନ୍ତୁ",
                data=video_bytes,
                file_name=f"local_dubbed_video_{lang_code}.mp4",
                mime="video/mp4"
            )
            
            video.close()
            new_audio_clip.close()
            final_video.close()
            
        except Exception as e:
            st.error(f"❌ କିଛି ଅସୁବିଧା ହେଲା: {e}")
            
    else:
        st.error("ଦୟାକରି ପ୍ରଥମେ ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ।")
