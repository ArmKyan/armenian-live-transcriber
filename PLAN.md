# PLAN: Live Armenian Transcription & Translation Pipeline

## 1. Goal & Requirements
- **Goal**: Listen to live dual-channel audio (Microphone + System Output), transcribe spoken Armenian locally, translate to English, perform speaker diarization, and display output in the terminal with $< 5\text{s}$ latency.
- **Key Constraints**:
  - 100% Local Models (No cloud APIs).
  - Target Language: Armenian ($\text{HY}$) $\rightarrow$ English ($\text{EN}$).
  - Hardware/OS specific setups (e.g., Virtual Loopback / BlackHole).
  - Speaker Labels: Microphone $\rightarrow$ `Me`; System Audio $\rightarrow$ `Speaker 1`, `Speaker 2`, etc.

---

## 2. Architecture & Modules

```
┌─────────────────────────┐      ┌─────────────────────────┐
│     Microphone Input    │      │   System Audio Loopback │
│  (Hardware Mic / Local) │      │  (BlackHole / Loopback) │
└────────────┬────────────┘      └────────────┬────────────┘
             │                                │
             ▼                                ▼
    ┌─────────────────┐              ┌─────────────────┐
    │ Audio Capture A │              │ Audio Capture B │
    └────────┬────────┘              └────────┬────────┘
             │                                │
             │  (Label: "Me")                 │  (System Audio Stream)
             │                                ▼
             │                       ┌─────────────────┐
             │                       │ Diarization /   │
             │                       │ Speaker ID      │
             │                       └────────┬────────┘
             │                                │ (Label: "Speaker N")
             └────────────────┬───────────────┘
                              │
                              ▼
                   ┌────────────────────┐
                   │ Armenian ASR       │
                   │ (Local Model)      │
                   └──────────┬─────────┘
                              │
                              ▼
                   ┌────────────────────┐
                   │ Translation        │
                   │ (HY -> EN Local)   │
                   └──────────┬─────────┘
                              │
                              ▼
                   ┌────────────────────┐
                   │ Terminal UI Stream │
                   └────────────────────┘
```

---

## 3. Module Specifications & Interfaces

### Module 1: Audio Ingestion (`src/audio.py`)
- **Inputs**: Audio device index/name for Mic and System Loopback.
- **Outputs**: Standardized PCM audio chunks / buffer queues (e.g., $16\text{kHz}$ mono float32 tensors/arrays).
- **Risks**: Device sample rate mismatches, missing loopback drivers on target OS, audio buffer overruns/underruns.

### Module 2: Speaker Diarization / Attribution (`src/diarization.py`)
- **Inputs**: Raw system audio stream chunks.
- **Outputs**: Speaker identifier tag (`Speaker 1`, `Speaker 2`, etc.) maintained consistently across frames.
- **Risks**: Heavy compute footprint leading to backpressure and exceeding the $5\text{s}$ latency requirement.

### Module 3: Speech Recognition / ASR (`src/transcription.py`)
- **Inputs**: Audio segment (Armenian audio buffer).
- **Outputs**: Armenian text string (`HY`).
- **Candidate Models**: Whisper-small/medium (fine-tuned variants), SeamlessM4T, or Wav2Vec2 Armenian.

### Module 4: Translation (`src/translation.py`)
- **Inputs**: Armenian text string.
- **Outputs**: English text string (`EN`).
- **Candidate Models**: NMT (e.g., Opus-MT `hy-en`), SeamlessM4T, or local LLM via Ollama/llama.cpp.

### Module 5: Orchestrator & CLI Output (`src/main.py`)
- **Inputs**: Synchronized outputs from ASR, Diarization, and NMT.
- **Outputs**: Streamed formatted terminal output `[HH:MM:SS] Speaker X | HY: ... | EN: ...`.

---

## 4. Execution Strategy & Milestones

1. **Walking Skeleton (Milestone 1)**:
   - Capture Mic input only $\rightarrow$ local Whisper ASR $\rightarrow$ mock translation $\rightarrow$ print to terminal.
2. **Dual-Channel Audio Ingestion (Milestone 2)**:
   - Integrate system audio loopback capture alongside microphone capture.
3. **Diarization Integration (Milestone 3)**:
   - Apply local speaker identification/diarization to system audio.
4. **Translation & Pipeline Latency Tuning (Milestone 4)**:
   - Integrate Armenian-to-English translation and optimize buffer sizing to ensure processing latency $< 5\text{s}$.