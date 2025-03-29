import streamlit as st
from ai_api import ask_gemini_vision
from utils.image_utils import image_to_base64
from PIL import Image

st.set_page_config(page_title="Gemini Vision Assistant", layout="centered")
st.title("Multi-Modal AI Assistant using Gemini")
st.write(
    "Upload an image and ask questions about it. Powered by Gemini's vision capabilities."
)

uploaded_image = st.file_uploader("", type=["jpg", "jpeg", "png"])
user_prompt = st.text_input("Ask something about the image:")

if uploaded_image and user_prompt:
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    with st.spinner("Analyzing..."):
        base64_image = image_to_base64(uploaded_image)
        result = ask_gemini_vision(user_prompt, base64_image)
    st.subheader("🧠 Gemini's Response:")
    st.write(result)
else:
    st.info("Please upload an image and enter a prompt to begin.")
