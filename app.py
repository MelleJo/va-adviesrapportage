import streamlit as st
from services.openai_service import transcribe_audio
from services.summarization_service import summarize_text
from components.ui_components import audio_input
import tempfile  # Voeg deze import toe

# Logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

st.title("Financieel Advies Spraak naar Tekst")
st.write("Kies een methode om audio te verwerken:")
input_method = st.radio("", ["Upload audio", "Neem audio op"])

audio_data = audio_input(input_method)

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
    
    department = st.selectbox("Selecteer de afdeling:", ["Financieel Advies", "Particulieren", "Schadeafdeling", "Bedrijven"])
    if st.button("Genereer samenvatting"):
        summary = summarize_text(transcript, department)
        st.session_state['summary'] = summary
        st.session_state['summarization_done'] = True
        st.experimental_rerun()

if st.session_state.get('summary'):
    st.write("Samenvatting:")
    st.write(st.session_state['summary'])
