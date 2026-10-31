"""Local Armenian -> English translation using HuggingFace transformers."""
from transformers import pipeline

DEFAULT_MODEL = "Helsinki-NLP/opus-mt-hy-en"


class Translator:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.pipe = pipeline("translation", model=model_name, device=-1)

    def translate(self, text: str) -> str:
        if not text:
            return ""
        return self.pipe(text, max_length=256)[0]["translation_text"]
