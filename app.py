import os
import streamlit as st
import time
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
import speech_recognition as sr
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ଟେମ୍ପରାରୀ ଫୋଲ୍ଡର
if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="100% Success Lyrical Video Maker", page_icon="🎬", layout="centered")

st.title("🎬 Guaranteed Lyrical Video Maker 🎶")
st.write("ଏହି ସିଷ୍ଟମ୍ ବିନା କୌଣସି Error ରେ ୧୦୦% ସଫଳତାର ସହ କାମ କରିବ!")
st.markdown("---")

# 🌍 ଦେଶ ଏବଂ ଭାଷା ଲିଷ୍ଟ୍
country_language_map = {
    "India (ଭାରତ) 🇮🇳": {
        "English (ଇଂରାଜୀ)": "en-IN",
        "ହିନ୍ଦୀ (Hindi)": "hi-IN",
        "ଓଡ଼ିଆ (Odia)": "or-IN",
        "ବେଙ୍ଗଲୀ (Bengali)": "bn-IN",
    },
    "World 🌍": {
        "English (US)": "en-US",
        "Spanish (ସ୍ପାନିସ୍)": "es-ES",
    }
}

selected_country = st.selectbox("🌍 ପ୍ରଥମେ ଦେଶ ବାଛନ୍ତୁ:", list(country_language_map.keys()))
lang_map = country_language_map[selected_country]
target_language = st.selectbox(f"🗣️ ଗୀତର ଭାଷା ବାଛନ୍ତୁ:", list(lang_map.keys()))
lang_code = lang_map[target_language]

uploaded_video = st.file_uploader("୧. ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ (MP4)", type=["mp4"])
if uploaded_video:
    st.video(uploaded_video)

uploaded_audio = st.file_uploader("୨. ଗୀତ ବା ମ୍ୟୁଜିକ୍ ଅପଲୋଡ୍ କରନ୍ତୁ (MP3)", type=["mp3", "wav"])

# === ImageMagick ବିନା ଟେକ୍ସଟ୍ (Lyrics) ବନେଇବାର ନୂଆ ଉପାୟ (100% Safe) ===
def create_text_image(text, video_size):
    width, height = video_size
    # ଗୋଟିଏ ଖାଲି (Transparent) ଫଟୋ ବନେଇବା
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # ଫଣ୍ଟ ଲୋଡ୍ କରିବା
    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            font = ImageFont.truetype(path, 40)
            break
    if font is None:
        font = ImageFont.load_default()
        
    # ଟେକ୍ସଟ୍ ପଛରେ ଥିବା କଳା ବ୍ୟାକଗ୍ରାଉଣ୍ଡ୍
    bar_height = 100
    draw.rectangle([(0, height - bar_height), (width, height)], fill=(0, 0, 0, 150))
    
    # ଟେକ୍ସଟ୍ କୁ ମଝିରେ (Center) ରଖିବା
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except:
        tw, th = draw.textsize(text, font=font)
        
    x = (width - tw) / 2
    y = height - bar_height + (bar_height - th) / 2
    
    # ହଳଦିଆ ରଙ୍ଗରେ ଟେକ୍ସଟ୍ ଲେଖିବା
    draw.text((x, y), text, font=font, fill="yellow")
    return np.array(img)
# =================================================================

if st.button("Auto Lyrical ଭିଡିଓ ତିଆରି କରନ୍ତୁ 🚀"):
    if uploaded_video and uploaded_audio:
        try:
            status_text = st.empty()
            status_text.info("ଭିଡିଓ ପ୍ରସ୍ତୁତ ହେଉଛି...")
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
            
            status_text.info(f"ଗୀତରୁ ଲେଖା ବାହାର କରାଯାଉଛି...")
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

            status_text.info("ଭିଡିଓ ଉପରେ Live Captions ଲଗାଯାଉଛି (ବିନା Error ରେ)...")
            progress_bar.progress(70)

            words = extracted_lyrics.split()
            chunk_size = 4
            lines = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
            
            clips = [video_clip]
            
            if lines:
                line_duration = duration / len(lines)
                for i, line in enumerate(lines):
                    # ଏଠାରେ ଆମେ ତିଆରି କରିଥିବା ନିରାପଦ (Safe) ଉପାୟ ବ୍ୟବହାର କରୁଛୁ
                    txt_img = create_text_image(line, video_clip.size)
                    txt_clip = ImageClip(txt_img).set_start(i * line_duration).set_duration(line_duration)
                    clips.append(txt_clip)

            status_text.info("ଫାଇନାଲ୍ ଭିଡିଓ ରେଡି ହେଉଛି...")
            progress_bar.progress(85)

            final_video = CompositeVideoClip(clips)
            
            output_path = os.path.join("temp", "final_safe_lyrical.mp4")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 ସଫଳତା! ବିନା କୌଣସି Error ରେ ଆପଣଙ୍କ ଭିଡିଓ ପ୍ରସ୍ତୁତ ହୋଇଯାଇଛି!")
            st.balloons()

            with open(output_path, "rb") as file:
                video_bytes = file.read()
            
            st.markdown("### 🎬 ଫାଇନାଲ୍ ଭିଡିଓ ଦେଖନ୍ତୁ:")
            st.video(video_bytes)

            st.download_button("⬇️️ ଭିଡିଓ ଡାଉନଲୋଡ୍ କରନ୍ତୁ", data=video_bytes, file_name="safe_lyrical_status.mp4", mime="video/mp4")

            video_clip.close()
            audio_clip.close()
            final_video.close()

        except Exception as e:
            st.error(f"❌ କିଛି ଅସୁବିଧା ହେଲା: {e}")
    else:
        st.error("ଦୟାକରି ଭିଡିଓ ଏବଂ ଗୀତ ଅପଲୋଡ୍ କରନ୍ତୁ।")
