import streamlit as st
from ai_api import create_gemini_chat, ask_gemini_chat
from utils.image_utils import image_to_base64
from PIL import Image
import io
import base64

def get_logo_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Page Config ---
st.set_page_config(page_title="Image Assistant", layout="wide")

# --- Custom CSS ---
def inject_custom_css():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
        }
        .chat-message {
            border-radius: 12px;
            padding: 10px 16px;
            margin-bottom: 8px;
            font-size: 16px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .chat-user {
            background-color: #DCF8C6;
            text-align: right;
            margin-left: auto;
        }
        .chat-assistant {
            background-color: #F1F0F0;
            text-align: left;
            margin-right: auto;
        }
        .stButton>button {
            border-radius: 8px;
            padding: 0.5em 1.5em;
            background-color: #4CAF50;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- App Title ---
col1, col2, col3 = st.columns([1, 2.5, 1])
with col2:
    logo_base64 = get_logo_base64("logo.png")

    st.markdown(
        f"""
        <div style='text-align: center;'>
            <img src='data:image/png;base64,{logo_base64}' width='400'>
        </div>
        """,
        unsafe_allow_html=True
    )


# --- Session State Init ---
for key in ["uploaded_file", "base64_image", "chat", "chat_history", "caption_text", "caption_chat"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0
if "prev_file_name" not in st.session_state:
    st.session_state["prev_file_name"] = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Top Bar with Reset + Mode Toggle ---
left_col, mid_col, right_col = st.columns([1, 5, 1])

with left_col:
    if st.button("🔄 New Chat"):
        keys_to_clear = ["uploaded_file", "base64_image", "chat", "chat_history", "caption_text", "caption_chat"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state["uploader_key"] += 1
        st.session_state["image_bytes"] = None
        st.rerun()

with right_col:
    if "mode" not in st.session_state:
        st.session_state.mode = "Chat with AI"

    if "mode_toggle_clicked" not in st.session_state:
        st.session_state.mode_toggle_clicked = False

    # Toggle button logic
    next_mode = "Caption" if st.session_state.mode == "Chat with AI" else "Chat"
    if st.button(f"Switch Mode"):
        st.session_state.mode_toggle_clicked = True


    if st.session_state.mode_toggle_clicked:
        st.session_state.mode = (
            "Get a caption" if st.session_state.mode == "Chat with AI"
            else "Chat with AI"
        )
        st.session_state.mode_toggle_clicked = False
        st.rerun()

mode = st.session_state.mode

with mid_col:
    st.markdown(
        f"<div style='text-align:center; font-size:18px;'>🧭 <b>Current Mode:</b> {mode}</div>",
        unsafe_allow_html=True
    )


# --- File Upload ---
uploader_key = st.session_state.get("uploader_key", 0)
uploaded_file = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"], key=uploader_key)

if uploaded_file:
    if uploaded_file.type not in ["image/jpeg", "image/png"]:
        st.error("❌ Invalid file type! Please upload JPG or PNG.")
    else:
        if uploaded_file.name != st.session_state["prev_file_name"]:
            st.session_state["caption_text"] = None
            st.session_state["caption_chat"] = None
            st.session_state["chat"] = None
            st.session_state["chat_history"] = []
            st.session_state["prev_file_name"] = uploaded_file.name

        st.session_state.uploaded_file = uploaded_file
        file_bytes = uploaded_file.read()
        st.session_state.base64_image = image_to_base64(file_bytes, max_size=(1024, 1024))
        st.session_state["image_bytes"] = file_bytes  #Save raw image bytes

        if mode == "Chat with AI" and st.session_state.chat is None:
            st.session_state.chat = create_gemini_chat(st.session_state.base64_image)
            
# --- Display Image (even after rerun) ---
if st.session_state.get("base64_image"):
    st.markdown(f"""
        <div style="
            max-width: 400px;
            margin: 0 auto 20px auto;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            background-color: #ffffff;
            text-align: center;
        ">
            <img src='data:image/jpeg;base64,{st.session_state.base64_image}' width='350' style="border-radius: 8px;" />
            <div style="margin-top: 8px; font-size: 14px; color: #666;">📷 Uploaded Image</div>
        </div>
    """, unsafe_allow_html=True)

# --- UI Modular Functions ---
def render_caption_ui():
    st.subheader("📝 Image Caption:")
    if st.session_state.caption_text is None:
        with st.spinner("Generating..."):
            if st.session_state.caption_chat is None:
                st.session_state.caption_chat = create_gemini_chat(st.session_state.base64_image)
            st.session_state.caption_text = ask_gemini_chat(
                st.session_state.caption_chat,
                "You are an image captioning expert for social media. Provide a short, accurate caption for the uploaded image."
            )
    st.write(st.session_state.caption_text)
    if st.button("🔁 Generate another caption"):
        with st.spinner("Regenerating..."):
            st.session_state.caption_text = ask_gemini_chat(
                st.session_state.caption_chat,
                "Generate 5 more captions for this image."
            )
        st.rerun()

def render_chat_ui():
    chat_container = st.container()
    with chat_container:
        for sender, msg in st.session_state.chat_history:
            with st.chat_message(sender):
                st.markdown(msg)
    st.divider()
    user_prompt = st.chat_input("Type your question about the image...")
    if user_prompt:
        st.session_state.chat_history.append(("user", user_prompt))
        with st.spinner("Thinking..."):
            reply = ask_gemini_chat(st.session_state.chat, user_prompt)
        st.session_state.chat_history.append(("assistant", reply))
        st.rerun()

# --- Mode Handler ---
if st.session_state.get("image_bytes"):
    if st.session_state.uploaded_file and mode == "Get a caption":
        render_caption_ui()
    elif st.session_state.uploaded_file and mode == "Chat with AI":
        render_chat_ui()
else:
    st.info("👆 Please upload an image to get started.")
