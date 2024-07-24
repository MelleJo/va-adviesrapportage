import streamlit as st
from streamlit_mic_recorder import mic_recorder

def audio_input(input_method):
    if input_method == "Upload audio":
        return st.file_uploader("Upload an audio file", type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'])
    elif input_method == "Neem audio op":
        return mic_recorder(key="recorder", start_prompt="Start opname", stop_prompt="Stop opname", use_container_width=True, format="webm")
