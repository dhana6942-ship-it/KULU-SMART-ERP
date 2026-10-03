import os
# ImageMagick Error ne fix karva mate aa line sabthi upar hovi joiye
os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

import streamlit as st
import time
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import speech_recognition as sr

# Temp folder create karva mate
if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="Auto Lyrical Video Maker", page_icon="🎬", layout="centered")

st.title("🎬 Auto-Lyrics Video Maker 🎶")
st.write("Video ane Song upload karo, automatic lyrics generate thai ne video upar aavi jashe!")
st.markdown("---")

uploaded_video = st.file_uploader("1. Video upload karo (MP4)", type=["mp4"])
if uploaded_video:
    st.info("Tamaro original video:")
    st.video(uploaded_video)

uploaded_audio = st.file_uploader("2. Nvu song/music upload karo (MP3) - aa mathi automatic lyrics aavshe", type=["mp3", "wav"])

if st.button("Auto Lyrical Video Banavo 🚀"):
    if uploaded_video and uploaded_audio:
        try:
            status_text = st.empty()
            status_text.info("Video process thai rahyo chhe, thodi rah juo...")
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
            
            status_text.info("Song mathi automatic lyrics nikali rahya chhe...")
            progress_bar.progress(50)

            # Song mathi text (lyrics) nikalva mate WAV ma convert karvu jaruri chhe
            temp_wav_path = os.path.join("temp", "temp_audio.wav")
            audio_clip.write_audiofile(temp_wav_path, logger=None)

            recognizer = sr.Recognizer()
            extracted_lyrics = ""
            with sr.AudioFile(temp_wav_path) as source:
                audio_data = recognizer.record(source)
                try:
                    # Audio mathi automatic text extract
                    extracted_lyrics = recognizer.recognize_google(audio_data)
                except Exception:
                    extracted_lyrics = ""

            if not extracted_lyrics.strip():
                extracted_lyrics = "Music is playing... Enjoy the video"

            status_text.info("Live captions set thai rahya chhe...")
            progress_bar.progress(70)

            # Lyrics ne chhuta padva mate (4-5 shabdo no ek bhaag)
            words = extracted_lyrics.split()
            chunk_size = 5
            lines = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
            
            clips = [video_clip]
            
            if lines:
                line_duration = duration / len(lines)
                for i, line in enumerate(lines):
                    # TextClip ma error na aave te mate configuration add karel chhe
                    txt = TextClip(line, fontsize=45, color='yellow', bg_color='rgba(0,0,0,0.6)')
                    txt = txt.set_position(('center', 'bottom'))
                    txt = txt.set_start(i * line_duration).set_duration(line_duration)
                    clips.append(txt)

            status_text.info("Final video ready thai rahyo chhe...")
            progress_bar.progress(85)

            final_video = CompositeVideoClip(clips)
            
            output_path = os.path.join("temp", "auto_lyrical_status.mp4")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 Tamaro Auto-Lyrics video ready chhe!")
            st.balloons()
            
            st.info(f"🎤 AI dwara pakdela lyrics: {extracted_lyrics}")

            with open(output_path, "rb") as file:
                video_bytes = file.read()
            
            st.markdown("### 🎬 Final Video:")
            st.video(video_bytes)

            st.download_button("⬇️ Video Download Karo", data=video_bytes, file_name="auto_lyrical.mp4", mime="video/mp4")

            video_clip.close()
            audio_clip.close()
            final_video.close()

        except Exception as e:
            st.error(f"❌ Error aavi: {e}")
    else:
        st.error("Krupaya Video ane Music banne upload karo.")
