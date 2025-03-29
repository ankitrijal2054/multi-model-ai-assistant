import streamlit as st
from ai_api import create_gemini_chat, ask_gemini_chat
from utils.image_utils import image_to_base64
from PIL import Image
import io

st.set_page_config(page_title="Gemini Chat", layout="centered")
st.title("🧠📸 Gemini Vision Chat Assistant")

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

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🛠 Options")
    mode = st.radio("Mode", ["Chat with image", "Get a caption"])
    if st.button("🔄 Reset Chat"):
        keys_to_clear = ["uploaded_file", "base64_image", "chat", "chat_history", "caption_text", "caption_chat"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state["uploader_key"] += 1
        st.experimental_rerun()

# --- File Upload ---
uploader_key = st.session_state.get("uploader_key", 0)
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key=uploader_key)

if uploaded_file:
    if uploaded_file.type not in ["image/jpeg", "image/png"]:
        st.error("❌ Invalid file type! Please upload JPG or PNG.")
    else:
        # Detect new image upload
        if uploaded_file.name != st.session_state["prev_file_name"]:
            st.session_state["caption_text"] = None
            st.session_state["caption_chat"] = None
            st.session_state["chat"] = None
            st.session_state["chat_history"] = []
            st.session_state["prev_file_name"] = uploaded_file.name

        st.session_state.uploaded_file = uploaded_file
        file_bytes = uploaded_file.read()
        st.session_state.base64_image = image_to_base64(file_bytes, max_size=(1024, 1024))

        image = Image.open(io.BytesIO(file_bytes))
        image.thumbnail((400, 400))
        st.image(image, caption="Uploaded Image", use_column_width=False)

        if mode == "Chat with image" and st.session_state.chat is None:
            st.session_state.chat = create_gemini_chat(st.session_state.base64_image)

# --- UI Modular Functions ---
def render_caption_ui():
    st.subheader("📝 Image Caption:")
    if st.session_state.caption_text is None:
        with st.spinner("Generating..."):
            if st.session_state.caption_chat is None:
                st.session_state.caption_chat = create_gemini_chat(st.session_state.base64_image)
            st.session_state.caption_text = ask_gemini_chat(
                st.session_state.caption_chat,
                "You are an image captioning expertfor social media. Provide a short, accurate caption for the uploaded image."
            )
    st.write(st.session_state.caption_text)
    if st.button("🔁 Generate another caption"):
        with st.spinner("Regenerating..."):
            st.session_state.caption_text = ask_gemini_chat(
                st.session_state.caption_chat,
                "Generate 5 more captions for this image."
            )
        st.experimental_rerun()

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
        st.experimental_rerun()

# --- Mode Handler ---
if st.session_state.uploaded_file and mode == "Get a caption":
    render_caption_ui()
elif st.session_state.uploaded_file and mode == "Chat with image":
    render_chat_ui()
