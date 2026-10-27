"""Run with: python -m streamlit run app.py"""
from pathlib import Path
import os
import streamlit as st
from hybrid_chatbot import reply

st.set_page_config(page_title="Campus Companion", page_icon="🌿", layout="centered")
st.markdown(f"<style>{Path(__file__).with_name('style.css').read_text()}</style>", unsafe_allow_html=True)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("ended", False)
server_key = os.environ.get("GEMINI_API_KEY", "")
if not server_key:
    try:
        server_key = st.secrets.get("GEMINI_API_KEY", "")
    except FileNotFoundError:
        server_key = ""

with st.sidebar:
    st.markdown("## 🌿 Campus Companion")
    st.caption("A little guidance. A smoother campus day.")
    if st.button("＋ New chat", key="new_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.ended = False
    st.divider()
    st.markdown("#### Your assistant")
    st.write("Library · Registration · Fees · Exams · IT support")
    st.divider()
    st.markdown("#### Connect Gemini")
    api_key = st.text_input("Gemini API key", type="password", help="Optional. Leave empty to use the five campus FAQs.").strip() or server_key
    st.divider()
    st.markdown("#### Student details")
    st.markdown("**G. Dulakshi Manel Wijethunga**")
    st.write("Student ID: 2026/MC/DIT/2418")
    st.write("ICT Diploma · Batch 03")
    st.caption("Meridians Campus of Higher Education")

st.markdown("""
<div class="brand-line">CAMPUS COMPANION <span>STUDENT SERVICES</span></div>
<div class="hero">
  <div class="eyebrow">YOUR CAMPUS, A LITTLE SIMPLER</div>
  <h1>Good questions.<br>Helpful answers.</h1>
  <p>From library hours to your next exam.<br>Ask away. We’ll help you find your next step.</p>
</div>
""", unsafe_allow_html=True)

selected = None
if not st.session_state.messages:
    st.subheader("What can we help with?")
    topics = [
        ("library", "📚 Library", "What are the library hours?"),
        ("registration", "📝 Registration", "How do I register?"),
        ("fees", "💳 Fees", "How can I pay fees?"),
        ("exams", "🎓 Exams", "What are the exam rules?"),
        ("support", "💻 IT support", "Where is IT support?"),
    ]
    columns = st.columns(3)
    for index, (key, label, question) in enumerate(topics):
        if columns[index % 3].button(label, key=f"topic_{key}", use_container_width=True):
            selected = question
    st.caption("Choose a topic above, or write your own question below.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask about campus life…", disabled=st.session_state.ended) or selected
if prompt and prompt.strip():
    answer = "Please try again."
    if prompt.strip().lower() in ("exit", "quit", "bye"):
        answer = "Goodbye! Good luck with your studies. Click New chat whenever you need a hand."
        st.session_state.ended = True
    else:
        client = None
        try:
            if api_key:
                from google import genai
                client = genai.Client(api_key=api_key, http_options={"timeout": 30000})
            answer = reply(prompt, client)
        except Exception:
            answer = reply(prompt) + " If you entered a key, check your Gemini setup."
        finally:
            if client is not None:
                client.close()
    st.session_state.messages.extend([
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": answer},
    ])
    st.rerun()

if st.session_state.ended:
    st.info("This chat has ended. Select New chat in the sidebar to start again.")
