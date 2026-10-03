import os
import streamlit as st
import time
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="Simple Lyrical Video Maker", page_icon="🎬", layout="centered")

st.title("🎬 Simple & Fast Lyrical Video Maker 🎶")
st.write("Video ane Song upload karo, potana lyrics lakho ane instant video download karo!")
st.markdown("---")

uploaded_video = st.file_uploader("1. Video upload karo (MP4)", type=["mp4"])
if uploaded_video:
    st.video(uploaded_video)

uploaded_audio = st.file_uploader("2. Song/Music upload karo (MP3)", type=["mp3", "wav"])

# Tame je pan ahiya lakho te seedhu video upar live caption banine aavse
lyrics_input = st.text_area("3. Video upar shu lakhvu chhe tey ahiya lakho (Lines ne Enter mari ne alag karo):", 
                           "Tumhi meri zindagi ho...\nDil ki har khushi ho...\nTumhi se hai mera jahan...")

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
            font = ImageFont.truetype(path, 40)
            break
    if font is None:
        font = ImageFont.load_default()
        
    bar_height = 100
    draw.rectangle([(0, height - bar_height), (width, height)], fill=(0, 0, 0, 180))
    
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

if st.button("Fast Lyrical Video Banavo 🚀"):
    if uploaded_video and uploaded_audio and lyrics_input:
        try:
            status_text = st.empty()
            status_text.info("Video process thai rahyo chhe, thodi rah juo...")
            progress_bar = st.progress(20)

            vid_path = os.path.join("temp", "input_vid.mp4")
            audio_path = os.path.join("temp", "input_audio.mp3")

            with open(vid_path, "wb") as f:
                f.write(uploaded_video.read())
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.read())

            progress_bar.progress(40)

            video_clip = VideoFileClip(vid_path)
            audio_clip = AudioFileClip(audio_path)

            duration = min(video_clip.duration, audio_clip.duration, 30)
            video_clip = video_clip.subclip(0, duration)
            audio_clip = audio_clip.subclip(0, duration)

            video_clip = video_clip.set_audio(audio_clip)
            
            progress_bar.progress(60)

            # Enter mari ne lakhele line ne alag karwanu
            lines = [line.strip() for line in lyrics_input.split('\n') if line.strip()]
            clips = [video_clip]
            
            if lines:
                line_duration = duration / len(lines)
                for i, line in enumerate(lines):
                    txt_img = create_text_image(line, video_clip.size)
                    txt_clip = ImageClip(txt_img).set_start(i * line_duration).set_duration(line_duration)
                    clips.append(txt_clip)

            progress_bar.progress(85)

            final_video = CompositeVideoClip(clips)
            
            output_path = os.path.join("temp", "final_fast_lyrical.mp4")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 Tamaro Lyrical Status Video ready thai gayo chhe!")
            st.balloons()

            with open(output_path, "rb") as file:
                video_bytes = file.read()
            
            st.markdown("### 🎬 Final Video View Karo:")
            st.video(video_bytes)

            st.download_button("⬇ Video Download Karo", data=video_bytes, file_name="lyrical_status.mp4", mime="video/mp4")

            video_clip.close()
            audio_clip.close()
            final_video.close()

        except Exception as e:
            st.error(f"❌ Kichi asuvidha thae chhe: {e}")
    else:
        st.error("Krupaya Video, Audio ane Lyrics text - trane cheejo barabar aapo.")
