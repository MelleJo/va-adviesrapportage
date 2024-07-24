import streamlit as st
from pydub import AudioSegment
import tempfile
from streamlit_mic_recorder import mic_recorder

from utils.text_processing import update_gesprekslog
from openai import OpenAI
import logging
import io

# logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the OpenAI API key
client = OpenAI()
OpenAI.api_key = st.secrets["OPENAI_API_KEY"]

def split_audio(audio_bytes, max_duration_ms=30000):
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        chunks = []
        for i in range(0, len(audio), max_duration_ms):
            chunks.append(audio[i:i+max_duration_ms])
        return chunks
    except Exception as e:
        logger.error(f"Error in split_audio: {str(e)}")
        raise

def transcribe_audio(audio_bytes):
    logger.debug("Starting transcribe_audio")
    transcript_text = ""
    with st.spinner('Audio segmentatie wordt gestart...'):
        try:
            audio_segments = split_audio(audio_bytes)
            logger.debug(f"Audio split into {len(audio_segments)} segments")
        except Exception as e:
            logger.error(f"Error splitting audio: {str(e)}")
            st.error(f"Fout bij het segmenteren van het audio: {str(e)}")
            return "Segmentatie mislukt."

    total_segments = len(audio_segments)
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_text.text("Start transcriptie...")
    for i, segment in enumerate(audio_segments):
        logger.debug(f"Processing segment {i+1} of {total_segments}")
        progress_text.text(f'Bezig met verwerken van segment {i+1} van {total_segments} - {((i+1)/total_segments*100):.2f}% voltooid')
        with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as temp_file:
            segment.export(temp_file.name, format="wav")
            logger.debug(f"Segment exported to temporary file: {temp_file.name}")
            with open(temp_file.name, "rb") as audio_file:
                try:
                    transcription_response = client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-1",
                        response_format="text"
                    )
                    logger.debug(f"Transcription response received for segment {i+1}")
                    transcript_text += transcription_response + " "
                except Exception as e:
                    logger.error(f"Error transcribing segment {i+1}: {str(e)}")
                    st.error(f"Fout bij het transcriberen: {str(e)}")
                    continue
        progress_bar.progress((i + 1) / total_segments)
    progress_text.success("Transcriptie voltooid.")
    logger.debug(f"Transcription completed. Total length: {len(transcript_text)}")
    st.info(f"Transcript gegenereerd. Lengte: {len(transcript_text)}")
    return transcript_text.strip()

def process_audio_input(input_method):
    logger.debug(f"Starting process_audio_input with method: {input_method}")
    logger.debug(f"Current session state: {st.session_state}")

    if not st.session_state.get('processing_complete', False):
        if input_method == "Upload audio":
            uploaded_file = st.file_uploader("Upload an audio file", type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'])
            if uploaded_file is not None and not st.session_state.get('transcription_done', False):
                logger.debug(f"Audio file uploaded: {uploaded_file.name}")
                with st.spinner("Transcriberen van audio..."):
                    audio_bytes = uploaded_file.read()
                    transcript = transcribe_audio(audio_bytes)
                    logger.debug(f"Transcript generated. Length: {len(transcript)}")
                    st.session_state['transcript'] = transcript
                    logger.debug(f"Transcript saved to session state. Length: {len(st.session_state['transcript'])}")
                    st.info(f"Transcript gegenereerd. Lengte: {len(transcript)}")
                st.session_state['transcription_done'] = True
                logger.debug("Transcription marked as done")
                st.experimental_rerun()
        elif input_method == "Neem audio op":
            audio_data = mic_recorder(key="recorder", start_prompt="Start opname", stop_prompt="Stop opname", use_container_width=True, format="webm")
            if audio_data and 'bytes' in audio_data and not st.session_state.get('transcription_done', False):
                logger.debug("Audio recorded")
                with st.spinner("Transcriberen van audio..."):
                    transcript = transcribe_audio(audio_data['bytes'])
                    logger.debug(f"Transcript generated. Length: {len(transcript)}")
                    st.session_state['transcript'] = transcript
                    logger.debug(f"Transcript saved to session state. Length: {len(st.session_state['transcript'])}")
                    st.info(f"Transcript gegenereerd. Lengte: {len(transcript)}")
                st.session_state['transcription_done'] = True
                logger.debug("Transcription marked as done")
                st.experimental_rerun()
..