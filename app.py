import streamlit as st
from ai_api import create_gemini_chat, ask_gemini_chat
from utils.image_utils import image_to_base64
from PIL import Image
import io

st.set_page_config(page_title="Gemini Chat", layout="centered")
st.title("🧠📸 Gemini Vision Chat Assistant")

# --- Session State Init ---
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "base64_image" not in st.session_state:
    st.session_state.base64_image = None
if "chat" not in st.session_state:
    st.session_state.chat = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🛠 Options")
    mode = st.radio("Mode", ["Chat with image", "Get a caption"])
    if st.button("🔄 Reset Chat"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

# --- File Upload ---
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    if uploaded_file.type not in ["image/jpeg", "image/png"]:
        st.error("❌ Invalid file type! Please upload JPG or PNG.")
    else:
        st.session_state.uploaded_file = uploaded_file
        file_bytes = uploaded_file.read()
        st.session_state.base64_image = image_to_base64(file_bytes)

        image = Image.open(io.BytesIO(file_bytes))
        image.thumbnail((300, 300))
        st.image(image, caption="Uploaded Image", use_column_width=False)

        # Start new chat session with image if needed
        if mode == "Chat with image" and st.session_state.chat is None:
            st.session_state.chat = create_gemini_chat(st.session_state.base64_image)
            st.session_state.chat_history = []

# --- Caption Mode ---
if st.session_state.uploaded_file and mode == "Get a caption":
    st.subheader("📝 Image Caption:")
    with st.spinner("Generating..."):
        caption_chat = create_gemini_chat(st.session_state.base64_image)
        result = ask_gemini_chat(caption_chat, "Describe this image.")
    st.write(result)

# --- Chat Mode ---
elif st.session_state.uploaded_file and mode == "Chat with image":
    # Display chat history (bottom-up)
    chat_container = st.container()
    with chat_container:
        for sender, msg in st.session_state.chat_history:
            with st.chat_message(sender):
                st.markdown(msg)

    # Chat input field at bottom
    st.divider()
    user_prompt = st.chat_input("Type your question about the image...")

    if user_prompt:
        # Add user message
        st.session_state.chat_history.append(("user", user_prompt))
        with st.spinner("Thinking..."):
            reply = ask_gemini_chat(st.session_state.chat, user_prompt)
        st.session_state.chat_history.append(("assistant", reply))
        st.experimental_rerun()  # Auto-scroll to bottom after each message
