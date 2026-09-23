import os
import time
from pathlib import Path
from typing import List

import streamlit as st

from ai_engine import generate_story
from image_fetcher import download_images
from pdf_generator import generate_pdf

# app.py
# Streamlit frontend for StoryLearn AI


st.set_page_config(page_title="StoryLearn AI", layout="wide")

# Load CSS
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def sidebar_history():
    st.sidebar.markdown("**Topic History**")
    hist = st.session_state.get("history", [])
    for t in reversed(hist[-10:]):
        st.sidebar.button(t, key=f"hist_{t}")


def main():
    if "history" not in st.session_state:
        st.session_state.history = []

    st.sidebar.title("StoryLearn AI")
    dark = st.sidebar.checkbox("Dark mode", value=False)
    sidebar_history()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("# Learn with Story-style Explanations")
        topic = st.text_input("Enter a topic to learn (e.g., Photosynthesis)")
        if st.button("Generate Story", key="gen"):
            if not topic or not topic.strip():
                st.error("Please enter a topic to continue.")
                return

            # Add to history
            st.session_state.history.append(topic)

            # Progress UI
            progress = st.progress(0)
            status = st.empty()

            try:
                status.info("Generating explanation with AI...")
                progress.progress(10)
                ai_content = generate_story(topic)
                progress.progress(40)

                status.info("Downloading educational images...")
                images = download_images(topic, limit=4)
                progress.progress(70)

                status.info("Preparing final output...")
                time.sleep(0.6)
                progress.progress(100)
                status.success("Ready")

            except Exception as e:
                st.error(f"Failed: {e}")
                return

            # Display results
            st.markdown("---")
            st.markdown(f"## Story: {topic}")

            # Card layout
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(ai_content.get("story", ""))
            st.markdown("</div>", unsafe_allow_html=True)

            # Images with captions
            if images:
                st.markdown("### Images")
                cols = st.columns(len(images))
                for c, img in zip(cols, images):
                    with c:
                        st.image(img, use_column_width=True)
                        st.caption(Path(img).name)

            # Steps
            if ai_content.get("steps"):
                st.markdown("### Step-by-step Concept Flow")
                for i, s in enumerate(ai_content.get("steps", []), start=1):
                    st.markdown(f"**{i}.** {s}")

            # Key points highlighted
            if ai_content.get("key_points"):
                st.markdown("### Key Points")
                for kp in ai_content.get("key_points", []):
                    st.markdown(f"<div class='highlight'>{kp}</div>", unsafe_allow_html=True)

            # Summary
            if ai_content.get("summary"):
                st.markdown("### Summary")
                st.info(ai_content.get("summary"))

            # PDF generation and download
            try:
                pdf_bytes = generate_pdf(topic, ai_content, images)
                st.download_button(label="Download PDF", data=pdf_bytes, file_name=f"{topic}_story.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"PDF generation failed: {e}")

    with col2:
        st.markdown("## Controls & Tips")
        st.write("- Use simple topics for shorter stories")
        st.write("- You can toggle Dark mode in the sidebar")


if __name__ == "__main__":
    main()
