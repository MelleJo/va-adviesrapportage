from pydub import AudioSegment
import subprocess
import logging


logger = logging.getLogger(__name__)

def split_audio(file_path, max_duration_ms=30000):
    try:
        logger.info(f"Attempting to split audio file: {file_path}")
        
        # Check if ffprobe is available
        try:
            subprocess.run(["ffprobe", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info("FFprobe is available on the system")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"FFprobe is not available: {str(e)}")
            raise RuntimeError("FFmpeg/FFprobe is not installed or not found in the system path. Please install FFmpeg and make sure it's in your PATH.")

        # Attempt to load the audio file
        logger.info("Loading audio file with pydub")
        audio = AudioSegment.from_file(file_path)
        logger.info(f"Audio file loaded successfully. Duration: {len(audio)} ms")

        chunks = []
        for i in range(0, len(audio), max_duration_ms):
            chunk = audio[i:i+max_duration_ms]
            chunks.append(chunk)
            logger.info(f"Created chunk {len(chunks)} with duration {len(chunk)} ms")

        logger.info(f"Audio split into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.exception(f"Error in split_audio function: {str(e)}")
        raise RuntimeError(f"Error processing audio file: {str(e)}")