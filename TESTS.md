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