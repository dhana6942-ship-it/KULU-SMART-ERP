import os
# Ee rendu lines valla ImageMagick error saswatham ga pothundi
os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

import streamlit as st
import time
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import speech_recognition as sr

if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="Auto Lyrical Video Maker", page_icon="🎬", layout="centered")

st.title("🎬 Auto-Lyrics Video Maker 🎶")
st.write("Video ane Song upload karo, automatic lyrics generate thai ne video upar aavi jashe!")
st.markdown("---")

uploaded_video = st.file_uploader("1. Video upload cheyandi (MP4)", type=["mp4"])
if uploaded_video:
    st.info("Mee original video:")
    st.video(uploaded_video)

uploaded_audio = st.file_uploader("2. Kotha song/music upload cheyandi (MP3) - deeni nunchi automatic ga lyrics vastayi", type=["mp3", "wav"])

if st.button("Auto Lyrical Video Banavo 🚀"):
    if uploaded_video and uploaded_audio:
        try:
            status_text = st.empty()
            status_text.info("Video process avuthondi, dayachesi vechi undandi...")
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
            
            status_text.info("Song nunchi automatic ga lyrics tistunnam...")
            progress_bar.progress(50)

            temp_wav_path = os.path.join("temp", "temp_audio.wav")
            audio_clip.write_audiofile(temp_wav_path, logger=None)

            recognizer = sr.Recognizer()
            extracted_lyrics = ""
            with sr.AudioFile(temp_wav_path) as source:
                audio_data = recognizer.record(source)
                try:
                    extracted_lyrics = recognizer.recognize_google(audio_data)
                except Exception:
                    extracted_lyrics = ""

            if not extracted_lyrics.strip():
                extracted_lyrics = "Music is playing... Enjoy the video"

            status_text.info("Live captions set chestunnam...")
            progress_bar.progress(70)

            words = extracted_lyrics.split()
            chunk_size = 5
            lines = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
            
            clips = [video_clip]
            
            if lines:
                line_duration = duration / len(lines)
                for i, line in enumerate(lines):
                    txt = TextClip(line, fontsize=45, color='yellow', bg_color='rgba(0,0,0,0.6)')
                    txt = txt.set_position(('center', 'bottom'))
                    txt = txt.set_start(i * line_duration).set_duration(line_duration)
                    clips.append(txt)

            status_text.info("Final video ready avuthondi...")
            progress_bar.progress(85)

            final_video = CompositeVideoClip(clips)
            
            output_path = os.path.join("temp", "auto_lyrical_status.mp4")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 Mee Auto-Lyrics video ready aindi!")
            st.balloons()
            
            st.info(f"🎤 AI dwara pakdela lyrics: {extracted_lyrics}")

            with open(output_path, "rb") as file:
                video_bytes = file.read()
            
            st.markdown("### 🎬 Final Video:")
            st.video(video_bytes)

            st.download_button("⬇️ Video Download Cheyandi", data=video_bytes, file_name="auto_lyrical.mp4", mime="video/mp4")

            video_clip.close()
            audio_clip.close()
            final_video.close()

        except Exception as e:
            st.error(f"❌ Error vachindi: {e}")
    else:
        st.error("Dayachesi Video mariyu Music rendu upload cheyandi.")
