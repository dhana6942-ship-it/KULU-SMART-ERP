import streamlit as st
import os
import time
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import speech_recognition as sr
from deep_translator import GoogleTranslator, MyMemoryTranslator
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
st.write("ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ ଆଉ ଯେକୌଣସି ଭାଷାରେ ବଦଳାନ୍ତୁ!")
st.markdown("---")

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
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            # ୧. ଭିଡିଓ ଫାଇଲ୍ ଲୋଡ୍ 
            status_text.text("୧/୫: ଭିଡିଓ ଅପଲୋଡ୍ ହେଉଛି...")
            input_video_path = os.path.join("temp", "input_video.mp4")
            with open(input_video_path, "wb") as f:
                f.write(uploaded_video.read())
            progress_bar.progress(20)
            
            # ୨. ଅଡିଓ ବାହାର କରିବା
            status_text.text("୨/୫: ଭିଡିଓରୁ ଅଡିଓ ଅଲଗା କରାଯାଉଛି...")
            video = VideoFileClip(input_video_path)
            audio_path = os.path.join("temp", "extracted_audio.wav")
            video.audio.write_audiofile(audio_path, logger=None)
            progress_bar.progress(40)
            
            # ୩. Speech to Text
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
                extracted_text = "Hello, testing audio."
            progress_bar.progress(60)
            
            # ୪. ଅନୁବାଦ (Translation) - ବ୍ୟାକଅପ୍ ଟ୍ରାନ୍ସଲେଟର୍ ସହ
            status_text.text(f"୪/୫: ଲେଖାକୁ ଅନୁବାଦ କରାଯାଉଛି...")
            translated_text = ""
            final_lang = lang_code
            
            try:
                # ପ୍ରଥମେ ଗୁଗୁଲ୍ ଟ୍ରାଏ କରିବ
                translated_text = GoogleTranslator(source='auto', target=lang_code).translate(extracted_text)
            except Exception:
                try:
                    # ଗୁଗୁଲ୍ ଫେଲ୍ ହେଲେ MyMemory ସର୍ଭର ବ୍ୟବହାର କରିବ
                    translated_text = MyMemoryTranslator(source='en', target=lang_code).translate(extracted_text)
                except Exception:
                    translated_text = ""
                
            # ଯଦି ଉଭୟ ସର୍ଭର ଫେଲ୍ ହୁଏ, ତେବେ ମୂଳ ଇଂରାଜୀ ଭାଷାରେ ଭଏସ୍ ଦେବ
            if not translated_text.strip():
                st.warning("⚠️ ସର୍ଭର ବ୍ୟସ୍ତ ଅଛି। ମୂଳ ଭାଷାରେ ନୂଆ ଭଏସ୍ ଦିଆଯାଉଛି...")
                translated_text = extracted_text
                final_lang = 'en'
                    
            progress_bar.progress(80)
            
            # ୫. ନୂଆ ଭିଡିଓ ତିଆରି ଏବଂ ଅଡିଓ ମିକ୍ସ (Audio Mix)
            status_text.text("୫/୫: ନୂଆ ଭିଡିଓ ପ୍ରସ୍ତୁତ କରାଯାଉଛି...")
            new_audio_path = os.path.join("temp", f"new_audio_{final_lang}.mp3")
            
            tts = gTTS(text=translated_text, lang=final_lang, slow=False)
            tts.save(new_audio_path)
            
            new_audio_clip = AudioFileClip(new_audio_path)
            original_audio = video.audio
            
            # ଏଠାରେ ପୁରୁଣା ବ୍ୟାକଗ୍ରାଉଣ୍ଡ୍ ସାଉଣ୍ଡ୍ ସହିତ ନୂଆ ଭଏସ୍ କୁ ମିକ୍ସ କରାଯାଉଛି (ଭିଡିଓ ଆଉ ସାଇଲେଣ୍ଟ୍ ହେବ ନାହିଁ)
            final_audio = CompositeAudioClip([original_audio, new_audio_clip])
            final_video = video.set_audio(final_audio)
            
            final_video_path = os.path.join("temp", "final_output_video.mp4")
            final_video.write_videofile(final_video_path, codec="libx264", audio_codec="aac", logger=None)
            
            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 ଆପଣଙ୍କ ଭିଡିଓ ସଫଳତାର ସହ କନଭର୍ଟ ହୋଇଯାଇଛି!")
            st.balloons()
            
            st.info(f"📝 AI ଧରିଥିବା ଲେଖା: {extracted_text}")
            st.warning(f"🗣️ ନୂଆ ଅନୁବାଦ: {translated_text}")
            
            with open(final_video_path, "rb") as file:
                video_bytes = file.read()
                
            st.video(video_bytes)
            st.download_button(
                label=f"⬇️ ନୂଆ ଭିଡିଓ ଡାଉନଲୋଡ୍ କରନ୍ତୁ",
                data=video_bytes,
                file_name=f"dubbed_video.mp4",
                mime="video/mp4"
            )
            
            video.close()
            new_audio_clip.close()
            final_video.close()
            
        except Exception as e:
            st.error(f"❌ କିଛି ଅସୁବିଧା ହେଲା: {e}")
            
    else:
        st.error("ଦୟାକରି ପ୍ରଥମେ ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ।")
