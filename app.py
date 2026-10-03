import streamlit as st
import os
import time
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS

# ଟେମ୍ପରାରୀ ଫାଇଲ୍ ସେଭ୍ କରିବା ପାଇଁ ଗୋଟିଏ ଫୋଲ୍ଡର ବନେଇବା
if not os.path.exists("temp"):
    os.makedirs("temp")

# ୱେବସାଇଟ୍ ର ଟାଇଟଲ୍ ଏବଂ ଡିଜାଇନ୍
st.set_page_config(page_title="AI Video Dubbing Pro", page_icon="🎥", layout="centered")

# --- ଲାଇସେନ୍ସ କି ଏବଂ ଡେମୋ ସିଷ୍ଟମ୍ (Sidebar) ---
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

# --- ମୁଖ୍ୟ ଡ୍ୟାସବୋର୍ଡ ---
st.title("🎥 AI Video Translation & Dubbing")
st.write("ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ ଆଉ ଯେକୌଣସି ଭାଷାରେ ବଦଳାନ୍ତୁ!")
st.markdown("---")

# ଭାଷା ଏବଂ ତାର କୋଡ୍ (Language Dictionary)
lang_map = {
    "ଓଡ଼ିଆ (Odia)": "or",
    "ହିନ୍ଦୀ (Hindi)": "hi",
    "ବେଙ୍ଗଲୀ (Bengali)": "bn",
    "ତେଲୁଗୁ (Telugu)": "te",
    "English (ଇଂରାଜୀ)": "en"
}

target_language = st.selectbox("ଆପଣ ଭିଡିଓଟିକୁ କେଉଁ ଭାଷାରେ ଡବିଂ କରିବାକୁ ଚାହୁଁଛନ୍ତି?", list(lang_map.keys()))
lang_code = lang_map[target_language]

uploaded_video = st.file_uploader("ଏଠାରେ ଆପଣଙ୍କ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ (mp4)", type=["mp4"])

if st.button("ଭିଡିଓ କନଭର୍ଟ କରନ୍ତୁ 🚀"):
    if uploaded_video is not None:
        try:
            # ପ୍ରୋଗ୍ରେସ୍ ଷ୍ଟେଟସ୍ ଦେଖାଇବା ପାଇଁ
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            # ୧. ଭିଡିଓ ସେଭ୍ କରିବା
            status_text.text("୧/୫: ଭିଡିଓ ଫାଇଲ୍ ଲୋଡ୍ ହେଉଛି...")
            input_video_path = os.path.join("temp", "input_video.mp4")
            with open(input_video_path, "wb") as f:
                f.write(uploaded_video.read())
            progress_bar.progress(20)
            
            # ୨. ଭିଡିଓରୁ ଅଡିଓ କାଢ଼ିବା
            status_text.text("୨/୫: ଭିଡିଓରୁ ଅଡିଓ ବାହାର କରାଯାଉଛି...")
            video = VideoFileClip(input_video_path)
            audio_path = os.path.join("temp", "extracted_audio.wav")
            video.audio.write_audiofile(audio_path, logger=None)
            progress_bar.progress(40)
            
            # ୩. ଅଡିଓରୁ ଟେକ୍ସଟ୍ (Speech to Text)
            status_text.text("୩/୫: ଅଡିଓକୁ ଲେଖାରେ ପରିଣତ କରାଯାଉଛି (AI Processing)...")
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                try:
                    extracted_text = recognizer.recognize_google(audio_data)
                except:
                    extracted_text = "Hello, this is a default text as speech recognition failed."
            progress_bar.progress(60)
            
            # ୪. ଭାଷା ଅନୁବାଦ (Translation)
            status_text.text(f"୪/୫: ଲେଖାକୁ {target_language} ରେ ଅନୁବାଦ କରାଯାଉଛି...")
            translated_text = GoogleTranslator(source='auto', target=lang_code).translate(extracted_text)
            progress_bar.progress(80)
            
            # ୫. ନୂଆ ଭାଷାରେ ଅଡିଓ ବନେଇବା ଏବଂ ଭିଡିଓ ସହ ଯୋଡ଼ିବା
            status_text.text("୫/୫: ନୂଆ ଭିଡିଓ ପ୍ରସ୍ତୁତ କରାଯାଉଛି (Text-to-Speech & Sync)...")
            new_audio_path = os.path.join("temp", f"new_audio_{lang_code}.mp3")
            tts = gTTS(text=translated_text, lang=lang_code, slow=False)
            tts.save(new_audio_path)
            
            # ନୂଆ ଅଡିଓକୁ ଭିଡିଓ ସହ ଯୋଡ଼ିବା
            new_audio_clip = AudioFileClip(new_audio_path)
            final_video = video.set_audio(new_audio_clip)
            final_video_path = os.path.join("temp", "final_output_video.mp4")
            
            # ଭିଡିଓ ସେଭ୍ କରିବା (ଭିଡିଓ ଲମ୍ବ ଅନୁସାରେ ଟିକେ ସମୟ ଲାଗିବ)
            final_video.write_videofile(final_video_path, codec="libx264", audio_codec="aac", logger=None)
            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 ଆପଣଙ୍କ ଭିଡିଓ ସଫଳତାର ସହ କନଭର୍ଟ ହୋଇଯାଇଛି!")
            st.balloons()
            
            # ଭିଡିଓ ଦେଖାଇବା ଆଉ ଡାଉନଲୋଡ୍ ବଟନ୍ ଦେବା
            with open(final_video_path, "rb") as file:
                video_bytes = file.read()
                
            st.video(video_bytes)
            
            st.download_button(
                label=f"⬇️ {target_language} ଭିଡିଓ ଡାଉନଲୋଡ୍ କରନ୍ତୁ",
                data=video_bytes,
                file_name=f"dubbed_video_{lang_code}.mp4",
                mime="video/mp4"
            )
            
            # ମେମୋରୀ ଫ୍ରି କରିବା ପାଇଁ ଫାଇଲ୍ ବନ୍ଦ କରିବା
            video.close()
            new_audio_clip.close()
            final_video.close()
            
        except Exception as e:
            st.error(f"ଭିଡିଓ ପ୍ରୋସେସ୍ କରିବାରେ ଅସୁବିଧା ହେଲା: {e}")
            
    else:
        st.error("ଦୟାକରି ପ୍ରଥମେ ଗୋଟିଏ ଭିଡିଓ ଫାଇଲ୍ ଅପଲୋଡ୍ କରନ୍ତୁ।")
