import streamlit as st
from services.langchain_service import transcribe_audio, fill_fields
from streamlit_mic_recorder import mic_recorder
import tempfile  # Zorg ervoor dat tempfile is geïmporteerd

import logging
logging.basicConfig(level=logging.INFO)

st.title("Financieel Advies Spraak naar Tekst")
st.write("Kies een methode om audio te verwerken:")
input_method = st.radio("", ["Upload audio", "Neem audio op"])

audio_data = None

if input_method == "Upload audio":
    audio_data = st.file_uploader("Upload een audiobestand", type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'])
elif input_method == "Neem audio op":
    audio_data = mic_recorder(key="recorder", start_prompt="Start opname", stop_prompt="Stop opname", use_container_width=True, format="webm")

if audio_data and not st.session_state.get('transcription_done', False):
    if input_method == "Upload audio":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tmp_audio.write(audio_data.getvalue())
            tmp_audio.flush()
            transcript = transcribe_audio(tmp_audio.name)
    elif input_method == "Neem audio op":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tmp_audio.write(audio_data['bytes'])
            tmp_audio.flush()
            transcript = transcribe_audio(tmp_audio.name)
    
    st.session_state['transcript'] = transcript
    st.session_state['transcription_done'] = True
    st.experimental_rerun()

if st.session_state.get('transcript'):
    transcript = st.session_state['transcript']
    st.write("Ingesproken tekst:")
    st.write(transcript)
    
    st.write("Ingevulde velden:")
    filled_fields = fill_fields(transcript)
    st.write(filled_fields)
