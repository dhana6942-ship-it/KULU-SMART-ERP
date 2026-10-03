import streamlit as st
import os
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

# ଫୋଲ୍ଡର ତିଆରି
if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="Live Lyrical Video Maker", page_icon="🎬", layout="centered")

st.title("🎬 Live Lyrical Video Maker 🎶")
st.write("ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ, ନିଜର ଗୀତ ଦିଅନ୍ତୁ ଏବଂ ତା' ଉପରେ Live Captions ଲଗାଇ ଡାଉନଲୋଡ୍ କରନ୍ତୁ!")
st.markdown("---")

# ୧. ଭିଡିଓ ଅପଲୋଡ୍ ଏବଂ Preview (Mute/Unmute ଅପ୍ସନ୍ ସହ)
uploaded_video = st.file_uploader("୧. ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ (MP4)", type=["mp4"])

if uploaded_video:
    st.info("👀 ତଳେ ଆପଣଙ୍କ ଭିଡିଓ ଦେଖନ୍ତୁ (ଭିଡିଓର ଡାହାଣ ପାଖ ତଳେ ଥିବା ସ୍ପିକର୍ ଆଇକନ୍ ଚିପି ମୂଳ ସାଉଣ୍ଡକୁ Mute/Unmute କରିପାରିବେ):")
    st.video(uploaded_video)

# ୨. ନୂଆ ମ୍ୟୁଜିକ୍ ଅପଲୋଡ୍
uploaded_audio = st.file_uploader("୨. ନୂଆ ଗୀତ ବା ମ୍ୟୁଜିକ୍ ଦିଅନ୍ତୁ (MP3)", type=["mp3", "wav"])

# ୩. Live Captions ପାଇଁ ଲେଖା (ସବୁ ଭାଷାରେ ହୋଇପାରିବ)
st.write("୩. ଗୀତର ଲାଇନ୍ ଗୁଡ଼ିକ ଲେଖନ୍ତୁ (ପ୍ରତି ଲାଇନ୍ କୁ ଅଲଗା ଅଲଗା ଧାଡ଼ିରେ/Enter ମାରି ଲେଖନ୍ତୁ, ଯେମିତିକି ତାହା Live Caption ଭଳି ଗୋଟିଏ ପରେ ଗୋଟିଏ ଆସିବ):")
lyrics_text = st.text_area("Live Lyrics", "ଏଠାରେ ନିଜ ଭାଷାରେ ଲେଖନ୍ତୁ...\nଲାଇନ୍ ପରେ ଲାଇନ୍...\nଗୋଟିଏ ପରେ ଗୋଟିଏ ଆସିବ...")

if st.button("Live Lyrical ଭିଡିଓ ତିଆରି କରନ୍ତୁ 🚀"):
    if uploaded_video and uploaded_audio and lyrics_text:
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

            # ସମୟ ନିର୍ଦ୍ଧାରଣ (ସର୍ବାଧିକ 30 ସେକେଣ୍ଡ)
            duration = min(video_clip.duration, audio_clip.duration, 30)
            video_clip = video_clip.subclip(0, duration)
            audio_clip = audio_clip.subclip(0, duration)

            # ପୁରୁଣା ସାଉଣ୍ଡ ହଟାଇ ନୂଆ ଗୀତ ଲଗାଇବା
            video_clip = video_clip.set_audio(audio_clip)

            progress_bar.progress(50)

            # --- Live Caption System (ଲାଇନ୍ ପରେ ଲାଇନ୍ ଆସିବା) ---
            # ଲେଖାକୁ ଭାଗ ଭାଗ କରିବା
            lines = [line.strip() for line in lyrics_text.split('\n') if line.strip()]
            clips = [video_clip]
            
            if lines:
                # ଗୋଟିଏ ଲାଇନ୍ କେତେ ସମୟ ରହିବ ତାର ହିସାବ
                line_duration = duration / len(lines)
                
                for i, line in enumerate(lines):
                    # ହଳଦିଆ ରଙ୍ଗର ଲେଖା ଏବଂ କଳା ବ୍ୟାକଗ୍ରାଉଣ୍ଡ ଯାହାଦ୍ୱାରା ତାହା ସ୍ପଷ୍ଟ ଦେଖାଯିବ
                    txt = TextClip(line, fontsize=45, color='yellow', bg_color='rgba(0,0,0,0.6)')
                    txt = txt.set_position(('center', 'bottom'))
                    # ପ୍ରତି ଲାଇନ୍ ର ଆରମ୍ଭ ଏବଂ ଶେଷ ସମୟ ସେଟ୍ କରିବା
                    txt = txt.set_start(i * line_duration).set_duration(line_duration)
                    clips.append(txt)

            progress_bar.progress(70)

            # ଭିଡିଓ ଏବଂ ଲେଖାଗୁଡ଼ିକୁ ଏକାଠି ଯୋଡ଼ିବା
            final_video = CompositeVideoClip(clips)
            
            output_path = os.path.join("temp", "live_lyrical_status.mp4")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 ଆପଣଙ୍କ Live Lyrical ଭିଡିଓ ରେଡି ହୋଇଯାଇଛି!")
            st.balloons()

            with open(output_path, "rb") as file:
                video_bytes = file.read()
            
            st.markdown("### 🎬 ଫାଇନାଲ୍ ଭିଡିଓ ଦେଖନ୍ତୁ:")
            st.video(video_bytes)

            st.download_button("⬇️ ଏହି ଭିଡିଓକୁ ଡାଉନଲୋଡ୍ କରନ୍ତୁ", data=video_bytes, file_name="live_lyrical.mp4", mime="video/mp4")

            # ଫାଇଲ୍ ବନ୍ଦ କରିବା
            video_clip.close()
            audio_clip.close()
            final_video.close()

        except Exception as e:
            st.error(f"❌ କିଛି ଅସୁବିଧା ହେଲା: {e}")
    else:
        st.error("ଦୟାକରି ଭିଡିଓ, ଗୀତ ଏବଂ ଲେଖା ତିନୋଟି ଯାକ ଦିଅନ୍ତୁ।")
