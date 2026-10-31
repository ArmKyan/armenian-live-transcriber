"""Local Armenian speech recognition: Whisper large-v3-turbo fine-tuned on Armenian."""
import numpy as np
from transformers import pipeline

from device import pick_device

DEFAULT_MODEL = "Chillarmo/whisper-large-v3-turbo-armenian"


class Transcriber:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.pipe = pipeline("automatic-speech-recognition", model=model_name, device=pick_device())

    def transcribe(self, audio: np.ndarray) -> str:
        """Convert a 16 kHz mono float32 array to Armenian text."""
        out = self.pipe(
            {"raw": audio, "sampling_rate": 16_000},
            generate_kwargs={"language": "armenian", "task": "transcribe"},
        )
        return out["text"].strip()
