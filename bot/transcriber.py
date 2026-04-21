import whisper
import os
import tempfile

model = None

def load_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("Whisper model loaded!")
    return model

def transcribe_audio(file_path: str) -> str:
    try:
        m = load_model()
        result = m.transcribe(file_path)
        return result["text"].strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return None