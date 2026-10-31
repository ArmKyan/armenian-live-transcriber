# Project Rules & Guidelines for Claude Cowork

## System Context & Role
You are collaborating on a Python application for **Live Armenian Transcription & Translation**. 
- You are acting as a junior/mid-level pair programmer.
- The user is the Lead Architect. You must ask clarifying questions before writing large code blocks.

---

## Strict Rules & Constraints

1. **Local Execution Only**: 
   - NEVER suggest or write code using OpenAI, Google Cloud, AWS, or external translation/speech APIs.
   - All models must run locally (e.g., PyTorch, `faster-whisper`, HuggingFace Transformers, `ctranslate2`, `ollama`, `llama.cpp`).

2. **Fail Fast & Keep It Simple**:
   - Do NOT add speculative fallback handlers, complex try-except chains, or production retry logic unless explicitly requested.
   - Code must fail loudly and clearly when an error occurs so it can be debugged immediately.

3. **Modularity**:
   - Keep modules isolated: Audio capturing, Speech Recognition, Diarization, Translation, and CLI output must remain strictly separated.
   - Do not write monolithic single-file scripts unless building a minimal walking skeleton.

4. **Dependencies**:
   - Prefer standard library or well-maintained Python libraries (`sounddevice`, `numpy`, `torch`, `transformers`, `faster-whisper`).

5. **Audio Specifications**:
   - Standard sample rate: $16\,000\text{ Hz}$ (Mono, float32 or int16).