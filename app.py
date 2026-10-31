import html
import time
from pathlib import Path

import streamlit as st

from ai_engine import generate_story
from pdf_generator import generate_pdf

# app.py
# Streamlit frontend for StoryLearn AI
# Safe version: no web images. Pictures are emojis only.

st.set_page_config(page_title="StoryLearn AI", layout="wide")

# Load CSS
css_path = Path(__file__).parent / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def esc(x) -> str:
    """Make text safe before putting it inside HTML."""
    return html.escape(str(x))


def sidebar_history():
    st.sidebar.markdown("**Topic History**")
    hist = st.session_state.get("history", [])
    for i, t in enumerate(reversed(hist[-10:])):
        st.sidebar.button(t, key=f"hist_{i}_{t}")


def show_result(topic: str, ai_content: dict):
    title = ai_content.get("title") or topic
    icon = ai_content.get("icon") or "📚"

    st.markdown("---")

    # Big emoji picture for the topic (safe, no web images)
    st.markdown(
        f"<div style='font-size:90px;text-align:center'>{esc(icon)}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"## {esc(title)}")

    # Story / explanation
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(esc(ai_content.get("story", "")))
    st.markdown("</div>", unsafe_allow_html=True)

    # Steps with one emoji each
    steps = ai_content.get("steps", [])
    if steps:
        st.markdown("### Step-by-step Concept Flow")
        icons = ai_content.get("step_icons", [])
        for i, s in enumerate(steps):
            step_icon = icons[i] if i < len(icons) else "🔹"
            st.markdown(f"**{esc(step_icon)} {i + 1}.** {esc(s)}")

    # Key points
    key_points = ai_content.get("key_points", [])
    if key_points:
        st.markdown("### Key Points")
        for kp in key_points:
            st.markdown(
                f"<div class='highlight'>{esc(kp)}</div>",
                unsafe_allow_html=True,
            )

    # Summary
    if ai_content.get("summary"):
        st.markdown("### Summary")
        st.info(ai_content["summary"])

    # PDF download (no images inside)
    try:
        pdf_bytes = generate_pdf(topic, ai_content, [])
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"{topic}_story.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.error(f"PDF generation failed: {e}")

    # Report button
    if st.button("Report a problem with this content", key="report"):
        st.warning("Thank you. Please also tell your teacher or the app owner what you saw.")


def main():
    if "history" not in st.session_state:
        st.session_state.history = []

    st.sidebar.title("StoryLearn AI")
    st.sidebar.checkbox("Dark mode", value=False)
    sidebar_history()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("# Learn with Story-style Explanations")
        topic = st.text_input("Enter a topic to learn (e.g., Photosynthesis, Cricket, Music)")

        if st.button("Generate Story", key="gen"):
            if not topic or not topic.strip():
                st.error("Please enter a topic to continue.")
                return

            topic = topic.strip()
            st.session_state.history.append(topic)

            progress = st.progress(0)
            status = st.empty()

            try:
                status.info("Generating explanation with AI...")
                progress.progress(20)
                ai_content = generate_story(topic)
                progress.progress(70)

                status.info("Preparing final output...")
                time.sleep(0.4)
                progress.progress(100)
                status.success("Ready")
            except Exception as e:
                st.error(f"Failed: {e}")
                return

            show_result(topic, ai_content)

    with col2:
        st.markdown("## Controls & Tips")
        st.write("- Use simple school topics for best results")
        st.write("- Every picture is an emoji, so nothing unsafe can appear")
        st.write("- Use Download PDF to save your notes")


if __name__ == "__main__":
    main()