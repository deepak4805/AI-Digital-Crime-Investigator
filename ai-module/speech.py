import whisper
import os
from analyzer import analyze_evidence

_model = None


def get_whisper_model():
    global _model
    if _model is None:
        print("Loading Whisper model...")
        _model = whisper.load_model("base")
        print("Whisper model loaded successfully")
    return _model


def transcribe_audio(audio_path):
    model = get_whisper_model()
    result = model.transcribe(audio_path)
    return result.get("text", "").strip()


if __name__ == "__main__":
    audio_path = "sample_data/sample_audio.wav.m4a"

    if not os.path.exists(audio_path):
        print("Audio file not found:")
        print(audio_path)
    else:
        # Step 1: Audio -> Text
        transcript = transcribe_audio(audio_path)

        print("\n===== AUDIO TRANSCRIPT =====\n")
        print(transcript)

        # Step 2: Text -> AI Analysis
        analysis = analyze_evidence(transcript)

        print("\n===== AI ANALYSIS OF AUDIO =====\n")
        print(analysis)
