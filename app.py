import streamlit as st
import os
import time
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from deep_translator import MyMemoryTranslator, GoogleTranslator
from gtts import gTTS
import gtts.lang  # ଦୁନିଆର ସବୁ ଭାଷା ଆଣିବା ପାଇଁ ନୂଆ ସିଷ୍ଟମ୍

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
st.write("ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ ଆଉ ବିଶ୍ୱର ଯେକୌଣସି ଭାଷାରେ ବଦଳାନ୍ତୁ 🌍!")
st.markdown("---")

# 🌍 ଦୁନିଆର ସବୁ ଭାଷା ଅଟୋମେଟିକ୍ ଆଣିବା (Dynamic Languages)
try:
    all_langs = gtts.lang.tts_langs()
    # ଡ୍ରପ୍ ଡାଉନ୍ ପାଇଁ ନାମ ଏବଂ କୋଡ୍ ସେଟ୍ କରିବା
    lang_map = {f"{name} ({code})": code for code, name in all_langs.items()}
except Exception:
    # ଯଦି କିଛି Error ଆସେ, ତେବେ ଏହି ଡିଫଲ୍ଟ ଭାଷା ଦେଖାଇବ
    lang_map = {
        "Hindi (hi)": "hi", "Bengali (bn)": "bn", "Telugu (te)": "te",
        "Tamil (ta)": "ta", "English (en)": "en", "Spanish (es)": "es",
        "French (fr)": "fr", "German (de)": "de", "Japanese (ja)": "ja"
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
                extracted_text = "Welcome to my video. The audio was not clear."
            progress_bar.progress(60)
            
            # ୪. ନୂଆ ଟ୍ରାନ୍ସଲେସନ୍ 
            status_text.text(f"୪/୫: ଲେଖାକୁ {target_language} ରେ ଅନୁବାଦ କରାଯାଉଛି...")
            translated_text = ""
            
            try:
                # ପ୍ରଥମେ MyMemoryTranslator (ଗୁଗୁଲ୍ ବ୍ଲକ୍ ରୁ ବଞ୍ଚିବା ପାଇଁ)
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
                    # ଯଦି ତାହା କାମ ନକରେ ତେବେ ଗୁଗୁଲ୍ ବ୍ୟବହାର କରିବ
                    translated_text = GoogleTranslator(source='auto', target=lang_code).translate(extracted_text)
                except:
                    translated_text = extracted_text 
                    
            progress_bar.progress(80)
            
            # ୫. ନୂଆ ଭିଡିଓ ଓ ଭଏସ୍ ତିଆରି (World Languages TTS)
            status_text.text("୫/୫: ନୂଆ ଭିଡିଓ ପ୍ରସ୍ତୁତ କରାଯାଉଛି...")
            new_audio_path = os.path.join("temp", f"new_audio_{lang_code}.mp3")
            
            try:
                tts = gTTS(text=translated_text, lang=lang_code, slow=False)
                tts.save(new_audio_path)
            except Exception:
                # ଯଦି କୌଣସି ଅଜଣା ଭାଷାରେ ଭଏସ୍ ସପୋର୍ଟ ନଥାଏ, ତେବେ Error ନଦେଇ ଡିଫଲ୍ଟ ଇଂରାଜୀରେ କହିବ
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
                file_name=f"world_dubbed_video.mp4",
                mime="video/mp4"
            )
            
            video.close()
            new_audio_clip.close()
            final_video.close()
            
        except Exception as e:
            st.error(f"❌ କିଛି ଅସୁବିଧା ହେଲା: {e}")
            
    else:
        st.error("ଦୟାକରି ପ୍ରଥମେ ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ।")
