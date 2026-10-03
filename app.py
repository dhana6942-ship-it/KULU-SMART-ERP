import os
import streamlit as st
import time
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
import speech_recognition as sr
from PIL import Image, ImageDraw, ImageFont
import numpy as np

if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="Guaranteed Lyrical Video Maker", page_icon="🎬", layout="centered")

st.title("🎬 100% Success Lyrical Video Maker 🎶")
st.write("Video ane Song upload karo, ane live captions sathe instant video download karo!")
st.markdown("---")

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

selected_country = st.selectbox("🌍 Prathme Desh Pasnd Karo:", list(country_language_map.keys()))
lang_map = country_language_map[selected_country]
target_language = st.selectbox(f"🗣️ Geet ni Bhasha Pasnd Karo:", list(lang_map.keys()))
lang_code = lang_map[target_language]

uploaded_video = st.file_uploader("1. Video upload karo (MP4)", type=["mp4"])
if uploaded_video:
    st.video(uploaded_video)

uploaded_audio = st.file_uploader("2. Geet/Music upload karo (MP3)", type=["mp3", "wav"])

# Navu option: Jo AI text na oolkhe to tame potanu custom lyrics pan aapi shako cho
custom_lyrics_input = st.text_area("3. [Optional] Video upar shu lakhvu chhe tey ahi lakho (Jethi live caption pakko aave):", 
                                  "Music is playing... Enjoy the status! 🎵")

def create_text_image(text, video_size):
    width, height = video_size
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            font = ImageFont.truetype(path, 36)
            break
    if font is None:
        font = ImageFont.load_default()
        
    bar_height = 90
    draw.rectangle([(0, height - bar_height), (width, height)], fill=(0, 0, 0, 160))
    
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except:
        tw, th = draw.textsize(text, font=font)
        
    x = max(10, (width - tw) / 2)
    y = height - bar_height + (bar_height - th) / 2
    
    draw.text((x, y), text, font=font, fill="yellow")
    return np.array(img)

if st.button("Auto Lyrical Video Banavo 🚀"):
    if uploaded_video and uploaded_audio:
        try:
            status_text = st.empty()
            status_text.info("Video process thai rahyo chhe...")
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
            
            status_text.info("Audio mathi text generate thay che...")
            progress_bar.progress(50)

            temp_wav_path = os.path.join("temp", "temp_audio.wav")
            audio_clip.write_audiofile(temp_wav_path, logger=None)

            extracted_lyrics = ""
            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(temp_wav_path) as source:
                    audio_data = recognizer.record(source)
                    extracted_lyrics = recognizer.recognize_google(audio_data, language=lang_code)
            except Exception:
                extracted_lyrics = ""

            # Jo AI text na pakde, to user e lakhele custom text use thase
            if not extracted_lyrics.strip():
                extracted_lyrics = custom_lyrics_input

            status_text.info("Live Captions video upar set thai rahya chhe...")
            progress_bar.progress(70)

            words = extracted_lyrics.split()
            chunk_size = 5
            lines = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
            if not lines:
                lines = [custom_lyrics_input]
            
            clips = [video_clip]
            
            if lines:
                line_duration = duration / len(lines)
                for i, line in enumerate(lines):
                    txt_img = create_text_image(line, video_clip.size)
                    txt_clip = ImageClip(txt_img).set_start(i * line_duration).set_duration(line_duration)
                    clips.append(txt_clip)

            status_text.info("Final video ready thay che...")
            progress_bar.progress(85)

            final_video = CompositeVideoClip(clips)
            
            output_path = os.path.join("temp", "final_safe_lyrical.mp4")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 Safalata! Tamaro Lyrical Status Video ready chhe!")
            st.balloons()

            st.info(f"🎤 Display thata lyrics: {extracted_lyrics}")

            with open(output_path, "rb") as file:
                video_bytes = file.read()
            
            st.markdown("### 🎬 Final Video View Karo:")
            st.video(video_bytes)

            st.download_button("⬇️️ Video Download Karo", data=video_bytes, file_name="lyrical_status.mp4", mime="video/mp4")

            video_clip.close()
            audio_clip.close()
            final_video.close()

        except Exception as e:
            st.error(f"❌ Kichi asuvidha thae chhe: {e}")
    else:
        st.error("Krupaya Video ane Audio banne upload karo.")
