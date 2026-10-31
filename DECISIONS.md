# Architectural Decision Log (ADR)

## Record Format
- **Date**: YYYY-MM-DD
- **Context**: What problem are we solving?
- **Decision**: What choice was made?
- **Rationale**: Why this choice over alternatives?
- **Trade-offs**: What are the downsides or accepted limitations?

---

### ADR-001: Audio Ingestion & Device Selection Library
- **Date**: 2026-10-21
- **Context**: Need a robust Python library to list and record from arbitrary input and loopback audio devices across macOS/Linux/Windows.
- **Decision**: Use `sounddevice` combined with `numpy` buffers.
- **Rationale**: Lightweight, low overhead, C bindings to PortAudio, easy real-time buffer management.
- **Trade-offs**: Requires external system virtual audio cable setup (e.g., BlackHole on macOS).

---

### ADR-002: Model Selection for Armenian Speech Recognition (ASR)
- **Date**: 2026-10-21
- **Context**: Armenian is a low-resource language; must run local inference under strict latency constraints ($<5\text{s}$).
- **Decision**: `faster-whisper` (CTranslate2, CPU, int8), model size configurable via `--asr-model` (default `small`).
- **Rationale**: Whisper supports Armenian (`hy`); faster-whisper int8 on CPU is several times faster than reference Whisper, which matters for the 5 s budget. Model size is a flag so WER vs latency can be benchmarked on the target laptop.
- **Trade-offs**: Whisper's Armenian WER is high, especially for small models. Not benchmarked yet (no model download possible in the authoring sandbox). Fallback candidate: a fine-tuned Armenian Whisper/wav2vec2.

---

### ADR-003: Speaker Diarization Strategy for System Audio
- **Date**: 2026-10-21
- **Context**: Differentiate multiple speakers on the incoming system audio channel without external cloud APIs.
- **Decision**: TBD (Options: PyAnnote audio embeddings vs lightweight cosine similarity on speaker embeddings via SpeechBrain/resemble-enhance).
- **Rationale**: PyAnnote can be memory heavy; simpler embedding comparison per silence-cut segment may offer lower latency.
- **Trade-offs**: TBD.
---

### ADR-004: Translation Model (HY -> EN)
- **Date**: 2026-10-31
- **Context**: Need local Armenian->English text translation.
- **Decision**: HuggingFace `transformers` MarianMT-style pipeline, default `Helsinki-NLP/opus-mt-hy-en`, model id configurable via `--mt-model`.
- **Rationale**: Small, CPU-friendly. Model id is a flag because the default could not be verified from the authoring sandbox (Hugging Face unreachable); `facebook/nllb-200-distilled-600M` (`hye_Armn` -> `eng_Latn`) is the fallback candidate.
- **Trade-offs**: Quality for Armenian unknown until benchmarked.

---

### ADR-005: Scope of first version
- **Date**: 2026-10-31
- **Context**: Step-by-step guide targets a file-streaming walking skeleton.
- **Decision**: Simulate live audio from a .wav (1 s blocks); single speaker label. Dual capture, diarization and `Me` labelling deferred.
- **Trade-offs**: Does not yet meet brief items 1 and 4 (two live sources, speaker identification).
