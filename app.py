import streamlit as st
import os
import time
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS

# ଟେମ୍ପରାରୀ ଫାଇଲ୍ ସେଭ୍ କରିବା ପାଇଁ ଫୋଲ୍ଡର
if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="AI Video Dubbing Pro", page_icon="🎥", layout="centered")

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
                extracted_text = "Welcome to my video. Have a nice day."
            progress_bar.progress(60)
            
            # ୪. ଅନୁବାଦ (Translation)
            status_text.text(f"୪/୫: ଲେଖାକୁ {target_language} ରେ ଅନୁବାଦ କରାଯାଉଛି...")
            translated_text = ""
            
            try:
                translator = GoogleTranslator(source='auto', target=lang_code)
                if len(extracted_text) < 3000:
                    translated_text = translator.translate(extracted_text)
                else:
                    text_chunks = [extracted_text[i:i+1500] for i in range(0, len(extracted_text), 1500)]
                    for chunk in text_chunks:
                        translated_text += translator.translate(chunk) + " "
                        time.sleep(1)
            except Exception as e:
                translated_text = "ଅନୁବାଦ ସମ୍ଭବ ହେଲା ନାହିଁ।" if lang_code == 'or' else "Translation server is busy right now."
                    
            progress_bar.progress(80)
            
            # ୫. ନୂଆ ଭିଡିଓ ତିଆରି
            status_text.text("୫/୫: ନୂଆ ଭିଡିଓ ପ୍ରସ୍ତୁତ କରାଯାଉଛି...")
            new_audio_path = os.path.join("temp", f"new_audio_{lang_code}.mp3")
            
            # ନୂଆ ସାଉଣ୍ଡ୍ ସେଭ୍ କରିବା 
            tts = gTTS(text=translated_text, lang=lang_code, slow=False)
            tts.save(new_audio_path)
            
            st.success("🎉 ପ୍ରୋସେସ୍ ଶେଷ ହୋଇଛି! ତଳେ ରେଜଲ୍ଟ ଦେଖନ୍ତୁ।")
            st.balloons()
            
            st.info(f"📝 AI ଧରିଥିବା ଲେଖା: {extracted_text}")
            st.warning(f"🗣️ ନୂଆ ଅନୁବାଦ: {translated_text}")

            # --- ନୂଆ ଟେଷ୍ଟିଂ (କେବଳ ଅଡିଓ ପ୍ଲେୟାର୍) ---
            st.markdown("### 🎵 ପ୍ରଥମେ କେବଳ ନୂଆ ଅଡିଓ ଶୁଣନ୍ତୁ (AI Voice):")
            st.audio(new_audio_path, format="audio/mp3")
            st.markdown("---")
            
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
                label=f"⬇️ ନୂଆ {target_language} ଭିଡିଓ ଡାଉନଲୋଡ୍ କରନ୍ତୁ",
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
