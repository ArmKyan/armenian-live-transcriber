# Test Cases & QA Validation Protocol

## 1. Unit & Functional Test Cases

| ID | Module | Scenario | Expected Outcome | Status |
|---|---|---|---|---|
| TC-01 | Audio | List audio devices | CLI cleanly lists all input/loopback device indexes | Pending |
| TC-02 | Audio | Capture 5s audio buffer | Array shape matches $(16000 \times 5,)$ at $16\text{kHz}$ | Pending |
| TC-03 | ASR | Standard Armenian audio input | Text output correctly transcribes phrase accurately | Pending |
| TC-04 | Translation | Armenian text input | Valid, coherent English translation generated | Pending |
| TC-05 | Diarization | Two distinct voices in sequence | Assigned distinct speaker tags (`Speaker 1`, `Speaker 2`) | Pending |

---

## 2. End-to-End Latency Benchmark

- **Metric**: Elapsed time from end of voice stream segment to CLI rendering.
- **Requirement**: Latency $\le 5.0\text{ seconds}$.

```text
[Audio Stream Ends] ---> [ASR Done] ---> [Translation Done] ---> [CLI Rendered]
      │                                                               │
      └────────────────────── Total Latency ──────────────────────────┘
```

---

## 3. Evaluation Dataset Log

| Audio File | Ground Truth (HY) | Expected (EN) | ASR Output | NMT Output | WER / Quality | Latency |
|---|---|---|---|---|---|---|
| `sample_01.wav` | Բարև, ինչպե՞ս ես։ | Hi, how are you? | | | | |
| `sample_02.wav` | Լավ եմ, շնորհակալություն։ | I'm fine, thank you. | | | | |
---

## 4. Colab Model Comparison (2026-10-31, Common Voice hy-AM clips, 8 samples)

| Stage | Model | Result |
|---|---|---|
| ASR | faster-whisper tiny | Latin-script gibberish |
| ASR | faster-whisper small (stock) | Mostly garbled Armenian |
| ASR | faster-whisper medium (stock) | Partly correct, many word errors |
| ASR | Chillarmo/whisper-large-v3-turbo-armenian | Readable, mostly correct (chosen) |
| MT | opus-mt-hy-en | Fluent but often wrong; religious-text bias |
| MT | NLLB-200-distilled-600M | Much better |
| MT | NLLB-200-distilled-1.3B | Best of the three (chosen) |

Latency on the target laptop: **not yet measured** with the final models. On a 2009 Core 2 Duo the earlier stock-Whisper runs took ~100-300 s per phrase (far above the 5 s limit).

## 5. Full pipeline in Colab, T4 GPU (2026-10-31)
Run: `--mic-input clip_1.wav --input test_audio.hy.wav` (wav files stand in for live devices; no real microphone or loopback tested).
- Mic phrase labelled `Me`; system phrases `Speaker 1..4`. Armenian and English both good.
- Latency after end of speech: first three phrases 8.2 s, 10.4 s, 5.6 s (cold start + queue behind it); remaining phrases 1.96-3.62 s. Fix: model warm-up before listening (added, not re-measured).
- Clip 6 was split mid-sentence by the 0.6 s end-of-phrase silence; the second half got its own speaker. Fix: `--end-silence`, default 0.8 s (not re-measured).
- Speaker labels: 8 clips -> 4 labels, five phrases merged into `Speaker 3`. Ground truth (who spoke which clip) unknown; tune `--speaker-threshold`.
- fp16 on CUDA added to the ASR model afterwards; not re-measured.

## 6. Still untested
Real microphone capture, real loopback capture (BlackHole / Stereo Mix), CPU latency on a modern laptop, speaker separation on a real conversation.
