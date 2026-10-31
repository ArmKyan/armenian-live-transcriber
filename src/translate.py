"""Local Armenian -> English translation: NLLB-200 distilled 1.3B."""
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from device import pick_device

DEFAULT_MODEL = "facebook/nllb-200-distilled-1.3B"


class Translator:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.device = pick_device()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, src_lang="hye_Armn")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device).eval()
        self.eng = self.tokenizer.convert_tokens_to_ids("eng_Latn")

    def translate(self, text: str) -> str:
        if not text:
            return ""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256).to(self.device)
        with torch.no_grad():
            out = self.model.generate(
                **inputs, forced_bos_token_id=self.eng, max_length=128, num_beams=2
            )
        return self.tokenizer.decode(out[0], skip_special_tokens=True)
