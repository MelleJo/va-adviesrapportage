import openai
import tempfile
from utils.audio_processing import split_audio
import logging
import streamlit as st
from config import OPENAI_API_KEY
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

openai.api_key = OPENAI_API_KEY
logger = logging.getLogger(__name__)

def transcribe_audio(file_path):
    logger.debug(f"Starting transcribe_audio for file: {file_path}")
    transcript_text = ""
    try:
        audio_segments = split_audio(file_path)
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
                    transcription_response = openai.Audio.transcriptions.create(
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

def fill_fields(transcribed_text):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=500,
        openai_api_key=OPENAI_API_KEY
    )

    tools = []  # Define your tools here if necessary

    agent = create_openai_tools_agent(
        llm,
        tools,
        prompt
    )

    response = agent.invoke({"input": transcribed_text, "chat_history": [], "intermediate_steps": []})
    return response['choices'][0]['text'].strip()
