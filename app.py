import streamlit as st
import os
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

# ଫୋଲ୍ଡର ତିଆରି କରିବା
if not os.path.exists("temp"):
    os.makedirs("temp")

st.set_page_config(page_title="Lyrical Video Status Maker", page_icon="🎬", layout="centered")

st.title("🎬 AI Lyrical Video Maker 🎶")
st.write("ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ, ନିଜ ପସନ୍ଦର ଗୀତ ଲଗାନ୍ତୁ ଏବଂ ତା' ଉପରେ ଲେଖା (Lyrics) ଦେଖାନ୍ତୁ!")
st.markdown("---")

# ୟୁଜର୍ ଠାରୁ ଭିଡିଓ, ମ୍ୟୁଜିକ୍ ଆଉ ଲେଖା ନେବା
uploaded_video = st.file_uploader("୧. ଗୋଟିଏ ଭିଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ (MP4)", type=["mp4"])
uploaded_audio = st.file_uploader("୨. ଗୋଟିଏ ମ୍ୟୁଜିକ୍ ବା ଗୀତ ଅପଲୋଡ୍ କରନ୍ତୁ (MP3)", type=["mp3", "wav"])
lyrics_text = st.text_area("୩. ଭିଡିଓ ଉପରେ କ'ଣ ଲେଖା ହେବ (Lyrics)?", "ତୁମେ ମୋର ପ୍ରଥମ ପ୍ରେମ...\nଆଉ ତୁମେ ହିଁ ମୋର ଶେଷ...")

if st.button("ଷ୍ଟାଟସ୍ ଭିଡିଓ ତିଆରି କରନ୍ତୁ 🚀"):
    if uploaded_video and uploaded_audio and lyrics_text:
        try:
            status_text = st.empty()
            status_text.info("ଭିଡିଓ ପ୍ରସ୍ତୁତ ହେଉଛି, ଦୟାକରି କିଛି ସମୟ ଅପେକ୍ଷା କରନ୍ତୁ...")
            progress_bar = st.progress(10)

            # ଫାଇଲ୍ ସେଭ୍ କରିବା
            vid_path = os.path.join("temp", "input_vid.mp4")
            audio_path = os.path.join("temp", "input_audio.mp3")

            with open(vid_path, "wb") as f:
                f.write(uploaded_video.read())
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.read())
            
            progress_bar.progress(30)

            # ଭିଡିଓ ଏବଂ ଅଡିଓ କୁ ଲୋଡ୍ କରିବା
            video_clip = VideoFileClip(vid_path)
            audio_clip = AudioFileClip(audio_path)

            # ସମୟ ସେଟ୍ କରିବା (ଭିଡିଓ ଏବଂ ଅଡିଓ ଭିତରୁ ଯିଏ ଛୋଟ ଥିବ ସେତିକି ରଖିବା, ଅତିବେଶୀରେ 30 ସେକେଣ୍ଡ)
            duration = min(video_clip.duration, audio_clip.duration, 30)
            
            video_clip = video_clip.subclip(0, duration)
            audio_clip = audio_clip.subclip(0, duration)

            progress_bar.progress(50)

            # ନୂଆ ଅଡିଓକୁ ଭିଡିଓରେ ଲଗାଇବା (ପୁରୁଣା ସାଉଣ୍ଡ୍ ଆପେ ଆପେ କଟିଯିବ)
            video_clip = video_clip.set_audio(audio_clip)

            # ଲେଖା (Lyrics) କୁ ଭିଡିଓ ଉପରେ ଲଗାଇବା
            txt_clip = TextClip(lyrics_text, fontsize=40, color='white', bg_color='rgba(0,0,0,0.5)')
            # ଲେଖାଟିକୁ ଭିଡିଓର ତଳ ମଝି ଭାଗରେ (center, bottom) ରଖିବା
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(duration)

            progress_bar.progress(70)

            # ଭିଡିଓ ଏବଂ ଲେଖାକୁ ଏକାଠି ଯୋଡ଼ିବା
            final_video = CompositeVideoClip([video_clip, txt_clip])

            # ଫାଇନାଲ୍ ଭିଡିଓ ସେଭ୍ କରିବା
            output_path = os.path.join("temp", "lyrical_video_status.mp4")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

            progress_bar.progress(100)
            status_text.empty()
            
            st.success("🎉 ଆପଣଙ୍କ ଲିରିକାଲ୍ ଷ୍ଟାଟସ୍ ଭିଡିଓ ପ୍ରସ୍ତୁତ ହୋଇଯାଇଛି!")
            st.balloons()

            # ଭିଡିଓ ଦେଖାଇବା ଏବଂ ଡାଉନଲୋଡ୍ ଅପ୍ସନ୍
            with open(output_path, "rb") as file:
                video_bytes = file.read()
            st.video(video_bytes)

            st.download_button("⬇️ ନୂଆ ଷ୍ଟାଟସ୍ ଭିଡିଓ ଡାଉନଲୋଡ୍ କରନ୍ତୁ", data=video_bytes, file_name="lyrical_video_status.mp4", mime="video/mp4")

            # ବ୍ୟବହାର ହୋଇଥିବା ଫାଇଲ୍ ଗୁଡ଼ିକୁ ବନ୍ଦ କରିବା
            video_clip.close()
            audio_clip.close()
            final_video.close()

        except Exception as e:
            st.error(f"❌ କିଛି ଅସୁବିଧା ହେଲା: {e}")
            st.warning("ଯଦି 'ImageMagick' Error ଆସୁଛି, ତେବେ ପୂର୍ବରୁ କୁହାଯାଇଥିବା 'packages.txt' ଫାଇଲ୍ ଟି GitHub ରେ ବନାନ୍ତୁ।")
    else:
        st.error("ଦୟାକରି ଭିଡିଓ, ଗୀତ ଏବଂ ଲେଖା - ଏହି ୩ଟି ଯାକ ନିଶ୍ଚିତ ଦିଅନ୍ତୁ।")
