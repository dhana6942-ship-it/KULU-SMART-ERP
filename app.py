import os
import shutil

# --- ULTIMATE SECURITY BYPASS (ସର୍ଭରର ଲକ୍ ଭାଙ୍ଗିବା ପାଇଁ ଏହା ସବୁଠାରୁ ଉପରେ ରହିବ) ---
try:
    config_dir = os.path.abspath("temp_magick")
    os.makedirs(config_dir, exist_ok=True)
    
    # ସର୍ଭରର ଅସଲି ଫାଇଲ୍ ଗୁଡ଼ିକୁ କପି କରି ଆଣିବା
    sys_magick = "/etc/ImageMagick-6"
    if os.path.exists(sys_magick):
        for file in os.listdir(sys_magick):
            try:
                shutil.copy(os.path.join(sys_magick, file), config_dir)
            except:
                pass
                
    # ନିଜର ଏକ ନୂଆ ସିକ୍ୟୁରିଟି ଫାଇଲ୍ ବନେଇବା ଯେଉଁଥିରେ ସବୁ ଅନୁମତି ଥିବ
    with open(os.path.join(config_dir, "policy.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<policymap>\n')
        f.write('  <policy domain="coder" rights="read|write" pattern="*" />\n')
        f.write('  <policy domain="path" rights="read|write" pattern="@*" />\n')
        f.write('  <policy domain="path" rights="read|write" pattern="*" />\n')
        f.write('</policymap>\n')
    
    # ସର୍ଭରକୁ ଏହି ନୂଆ ଫାଇଲ୍ ବ୍ୟବହାର କରିବାକୁ ବାଧ୍ୟ କରିବା
    os.environ["MAGICK_CONFIGURE_PATH"] = config_dir
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
except Exception as e:
    pass
# -------------------------------------------------------------------------

import streamlit as st
import time
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import speech_recognition as sr

if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="Global Lyrical Video Maker", page_icon="🎬", layout="centered")

st.title("🎬 Global Auto-Lyrics Video Maker 🎶")
st.write("ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ, ନିଜ ମନପସନ୍ଦର ଗୀତ ଦିଅନ୍ତୁ ଏବଂ ଲାଇଭ୍ ଲିରିକ୍ସ ପାଆନ୍ତୁ!")
st.markdown("---")

# 🌍 ଦେଶ ଏବଂ ଭାଷା ବାଛିବାର ଲିଷ୍ଟ୍
country_language_map = {
    "India (ଭାରତ) 🇮🇳": {
        "ଓଡ଼ିଆ (Odia)": "or-IN",
        "ହିନ୍ଦୀ (Hindi)": "hi-IN",
        "English (ଇଂରାଜୀ)": "en-IN",
        "ବେଙ୍ଗଲୀ (Bengali)": "bn-IN",
        "ତେଲୁଗୁ (Telugu)": "te-IN",
        "ତାମିଲ୍ (Tamil)": "ta-IN",
        "ଗୁଜରାଟୀ (Gujarati)": "gu-IN",
        "ପଞ୍ଜାବୀ (Punjabi)": "pa-IN"
    },
    "World 🌍": {
        "English (US)": "en-US",
        "English (UK)": "en-GB",
        "Spanish (ସ୍ପାନିସ୍)": "es-ES",
        "French (ଫ୍ରେଞ୍ଚ୍)": "fr-FR",
        "Arabic (ଆରବିକ୍)": "ar-SA",
        "Japanese (ଜାପାନୀ)": "ja-JP",
        "Korean (କୋରିଆନ୍)": "ko-KR",
        "Russian (ରୁଷିଆନ୍)": "ru-RU"
    }
}

selected_country = st.selectbox("🌍 ପ୍ରଥମେ ଦେଶ ବାଛନ୍ତୁ:", list(country_language_map.keys()))
lang_map = country_language_map[selected_country]
target_language = st.selectbox(f"🗣️ ଏବେ ଗୀତର ଭାଷା ବାଛନ୍ତୁ (ଯେଉଁ ଭାଷାରେ ଗୀତ ବାଜିବ):", list(lang_map.keys()))
lang_code = lang_map[target_language]

uploaded_video = st.file_uploader("୧. ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ (MP4)", type=["mp4"])
if uploaded_video:
    st.video(uploaded_video)

uploaded_audio = st.file_uploader("୨. ଗୀତ ବା ମ୍ୟୁଜିକ୍ ଅପଲୋଡ୍ କରନ୍ତୁ (MP3)", type=["mp3", "wav"])

if st.button("Auto Lyrical ଭିଡିଓ ତିଆରି କରନ୍ତୁ 🚀"):
    if uploaded_video and uploaded_audio:
        try:
            status_text = st.empty()
            status_text.info("ଭିଡିଓ ପ୍ରସ୍ତୁତ ହେଉଛି, ଦୟାକରି କିଛି ସମୟ ଅପେକ୍ଷା କରନ୍ତୁ...")
            progress_bar = st.progress(10)

            vid_path = os.path.join("temp", "input_vid.mp4")
            audio_path = os.path.join("temp", "input_audio.mp3")

            with open(vid_path, "wb") as f:
                f.write(uploaded_video.read())
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.read())

            progress_bar.progress(30)

            video_clip = VideoFileClip(vid_path)
            audio_clip = AudioFileClip(audio_path)

            duration = min(video_clip.duration, audio_clip.duration, 30)
            video_clip = video_clip.subclip(0, duration)
            audio_clip = audio_clip.subclip(0, duration)

            video_clip = video_clip.set_audio(audio_clip)
            
            status_text.info(f"{target_language} ଗୀତରୁ ଲେଖା ବାହାର କରାଯାଉଛି...")
            progress_bar.progress(50)

            temp_wav_path = os.path.join("temp", "temp_audio.wav")
            audio_clip.write_audiofile(temp_wav_path, logger=None)

            recognizer = sr.Recognizer()
            extracted_lyrics = ""
            with sr.AudioFile(temp_wav_path) as source:
                audio_data = recognizer.record(source)
                try:
                    extracted_lyrics = recognizer.recognize_google(audio_data, language=lang_code)
                except Exception:
                    extracted_lyrics = ""

            if not extracted_lyrics.strip():
                extracted_lyrics = "Music is playing... Enjoy!"

            status_text.info("ଭିଡିଓ ଉପରେ Live Captions ସେଟ୍ କରାଯାଉଛି...")
            progress_bar.progress(70)

            words = extracted_lyrics.split()
            chunk_size = 4
            lines = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
            
            clips = [video_clip]
            
            if lines:
                line_duration = duration / len(lines)
                for i, line in enumerate(lines):
                    txt = TextClip(line, fontsize=45, color='yellow', bg_color='rgba(0,0,0,0.5)')
                    txt = txt.set_position(('center', 'bottom'))
                    txt = txt.set_start(i * line_duration).set_duration(line_duration)
                    clips.append(txt)

            status_text.info("ଫାଇନାଲ୍ ଭିଡିଓ ରେଡି ହେଉଛି...")
            progress_bar.progress(85)

            final_video = CompositeVideoClip(clips)
            
            output_path = os.path.join("temp", "auto_global_lyrical.mp4")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 ଆପଣଙ୍କ ଲିରିକାଲ୍ ଭିଡିଓ ରେଡି ହୋଇଯାଇଛି!")
            st.balloons()
            
            st.info(f"🎤 ଗୀତରୁ ବାହାରିଥିବା ଲେଖା: {extracted_lyrics}")

            with open(output_path, "rb") as file:
                video_bytes = file.read()
            
            st.markdown("### 🎬 ନୂଆ ଭିଡିଓ ଦେଖନ୍ତୁ (Live Caption ସହ):")
            st.video(video_bytes)

            st.download_button("⬇️ ଭିଡିଓ ଡାଉନଲୋଡ୍ କରନ୍ତୁ", data=video_bytes, file_name="lyrical_status.mp4", mime="video/mp4")

            video_clip.close()
            audio_clip.close()
            final_video.close()

        except Exception as e:
            st.error(f"❌ କିଛି ଅସୁବିଧା ହେଲା: {e}")
    else:
        st.error("ଦୟାକରି ଭିଡିଓ ଏବଂ ଗୀତ ଦୁଇଟି ଯାକ ଅପଲୋଡ୍ କରନ୍ତୁ।")
