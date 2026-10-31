"""Local Armenian speech recognition using faster-whisper (CPU, int8)."""
import numpy as np
from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self, model_size: str = "small"):
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio: np.ndarray) -> str:
        """Convert a 16 kHz mono float32 array to Armenian text."""
        segments, _ = self.model.transcribe(
            audio, language="hy", beam_size=1, vad_filter=True
        )
        return " ".join(s.text.strip() for s in segments).strip()
