import openai
import tempfile
from utils.audio_processing import split_audio
import logging
import streamlit as st
from config import OPENAI_API_KEY
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chains import LLMChain

openai.api_key = OPENAI_API_KEY
logger = logging.getLogger(__name__)

def transcribe_audio(file_path):
    logger.info(f"Starting transcribe_audio for file: {file_path}")
    transcript_text = ""
    try:
        audio_segments = split_audio(file_path)
        logger.info(f"Audio split into {len(audio_segments)} segments")
    except Exception as e:
        error_message = f"Error splitting audio: {str(e)}"
        logger.exception(error_message)
        st.error(error_message)
        return f"Transcriptie mislukt: {error_message}"

    total_segments = len(audio_segments)
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_text.text("Start transcriptie...")
    for i, segment in enumerate(audio_segments):
        logger.info(f"Processing segment {i+1} of {total_segments}")
        progress_text.text(f'Bezig met verwerken van segment {i+1} van {total_segments} - {((i+1)/total_segments*100):.2f}% voltooid')
        with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as temp_file:
            segment.export(temp_file.name, format="wav")
            logger.info(f"Segment exported to temporary file: {temp_file.name}")
            with open(temp_file.name, "rb") as audio_file:
                try:
                    transcription_response = openai.Audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-1",
                        response_format="text"
                    )
                    logger.info(f"Transcription response received for segment {i+1}")
                    transcript_text += transcription_response + " "
                except Exception as e:
                    error_message = f"Error transcribing segment {i+1}: {str(e)}"
                    logger.exception(error_message)
                    st.error(error_message)
                    return f"Transcriptie mislukt: {error_message}"
        progress_bar.progress((i + 1) / total_segments)
    progress_text.success("Transcriptie voltooid.")
    logger.info(f"Transcription completed. Total length: {len(transcript_text)}")
    st.info(f"Transcript gegenereerd. Lengte: {len(transcript_text)}")
    return transcript_text.strip()

def fill_fields(transcribed_text):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("You are a helpful assistant."),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.1,
        max_tokens=500,
        openai_api_key=OPENAI_API_KEY
    )

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
    )

    inputs = {
        "input": transcribed_text
    }

    response = chain(inputs)
    return response['text']