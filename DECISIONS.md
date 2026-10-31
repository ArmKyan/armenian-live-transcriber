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
- **Trade-offs**: Requires external system virtual audio cable setup (e.g., BlackHole on macOS). Status 2026-10-31: implemented, UNTESTED on real devices. Blocks are resampled to 16 kHz one at a time, so tiny edge artefacts are possible.

---

### ADR-002: Model Selection for Armenian Speech Recognition (ASR)
- **Date**: 2026-10-31
- **Context**: Armenian is low-resource; must run locally with a 5 s budget.
- **Decision**: `Chillarmo/whisper-large-v3-turbo-armenian` (Whisper large-v3-turbo fine-tuned on Common Voice 20 Armenian, 0.8B, Apache-2.0), loaded with `transformers` pipeline.
- **Rationale**: Measured on 8 Common Voice clips in Colab. Stock faster-whisper `small` was mostly garbled; stock `medium` was partly right (e.g. clip 1) with many word errors; `tiny` output Latin gibberish. The turbo fine-tune produced readable, mostly correct Armenian; chosen over `whisper-small-armenian-v2` (reported WER 24.0% vs 15.3% self-reported) after side-by-side comparison. Also considered: `arampacha/whisper-large-hy` (22.4% WER, large-v2, heavier).
- **Trade-offs**: 0.8B params is heavy. Not measured against the 5 s limit yet on target hardware; the author's card suggests a GPU with 8 GB. Stock Whisper-small on a 2009 Core 2 Duo took 100-300 s per phrase. WERs are self-reported on Common Voice, which our test clips come from, so real conversational accuracy is likely worse. Possible speed-up: convert to CTranslate2 and use faster-whisper.

---

### ADR-003: Speaker Diarization Strategy for System Audio
- **Date**: 2026-10-31
- **Context**: Tell apart several people on the system-audio channel, locally, with stable labels for the session.
- **Decision**: Online identification, not full diarization: each finished phrase is embedded with SpeechBrain ECAPA-TDNN (`speechbrain/spkrec-ecapa-voxceleb`, CPU) and matched by cosine similarity to running speaker centroids; below threshold (default 0.45, `--speaker-threshold`) it becomes a new speaker. Phrases under 1 s never create or update a speaker.
- **Rationale**: Simple, no heavy pyannote pipeline, one embedding per phrase fits the latency budget. Microphone audio is always `Me` and is never embedded.
- **Trade-offs**: First test (Colab, 8 Common Voice clips as one system source): plausible but unverified labels; five phrases merged into one speaker. The 0.45 threshold is still a guess and needs tuning on a real conversation. Overlapping speech, very short phrases and similar voices will mislabel. One phrase = one speaker (no mid-phrase speaker change).

---

### ADR-004: Translation Model (HY -> EN)
- **Date**: 2026-10-31
- **Context**: Need local Armenian->English text translation.
- **Decision**: `facebook/nllb-200-distilled-1.3B` (`hye_Armn` -> `eng_Latn`).
- **Rationale**: Compared on the same Armenian text from 8 clips. `Helsinki-NLP/opus-mt-hy-en` produced fluent but wrong English with a strong religious-text bias ("Jehovah's Witnesses", repeated phrases). NLLB-600M was clearly better; NLLB-1.3B read best (about 0.5-0.8 s per sentence on a Colab GPU). NLLB-3.3B scores higher still on a public FLORES-200 hye->en leaderboard but was not tested here.
- **Trade-offs**: Larger and slower than 600M; CPU timing not yet measured. Some errors remain from domain vocabulary and upstream ASR mistakes.

---

### ADR-005: Scope of first version (superseded)
- **Date**: 2026-10-31
- **Decision**: Started as a file-streaming walking skeleton. Superseded by ADR-006.

---

### ADR-006: Live two-source pipeline
- **Date**: 2026-10-31
- **Decision**: One capture+segmentation thread per source (mic, system); finished phrases go to one queue; the main thread runs ASR, MT and labelling sequentially and prints. Wav files can stand in for either source (`--mic-input`, `--input`).
- **Rationale**: Capture never blocks on slow models; one worker avoids two big models competing for the CPU/GPU.
- **Trade-offs**: If processing is slower than speech the queue grows and latency grows with it (no dropping or warning yet). UNTESTED live.
