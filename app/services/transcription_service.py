from pathlib import Path
from typing import List
import whisper

model = whisper.load_model("base")

SUPPORTED_AUDIO_TYPES = {".wav", ".mp3"}

def transcribe_audio(file_path: str, filename: str) -> dict:
    ext = Path(filename).suffix.lower()
    
    if ext not in SUPPORTED_AUDIO_TYPES:
        raise ValueError("Unsupported audio file type for transcription")
    
    result = model.transcribe(file_path)
    
    return [{
        "text": result["text"],
        "metadata": {
            "filename": filename,
            "source": "transcription"
        }    
    }]