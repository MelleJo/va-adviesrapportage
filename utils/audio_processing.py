from pydub import AudioSegment
import subprocess
import os

def split_audio(file_path, max_duration_ms=30000):
    try:
        # Check if ffprobe is available
        subprocess.run(["ffprobe", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("FFmpeg/FFprobe is not installed or not found in the system path. Please install FFmpeg and make sure it's in your PATH.")

    try:
        audio = AudioSegment.from_file(file_path)
        chunks = []
        for i in range(0, len(audio), max_duration_ms):
            chunks.append(audio[i:i+max_duration_ms])
        return chunks
    except Exception as e:
        raise RuntimeError(f"Error processing audio file: {str(e)}")