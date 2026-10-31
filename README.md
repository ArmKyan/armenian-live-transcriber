# Armenian Live Transcriber (walking skeleton)

Streams a 16 kHz `.wav` file in 1-second blocks (simulating a live source), splits it into phrases on silence, transcribes Armenian with a local Whisper model, translates to English with a local MT model, and prints:

```
[00:00:06] Speaker 1
HY: ...
EN: ...
    (latency 1.84s)
```

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Models download from Hugging Face on first run (needs internet once; afterwards fully local).

## Run
```bash
python src/main.py --input test_audio.hy.wav          # real-time pacing
python src/main.py --input test_audio.hy.wav --fast   # no sleeping between blocks
# options: --asr-model small|medium|...   --mt-model <hf id>
```
Input must be 16 kHz (mono or stereo; stereo is averaged). Other rates fail loudly.

## Architecture
`audio.py` (block streamer) -> `main.py` (energy-based phrase segmentation) -> `transcribe.py` (faster-whisper, CPU int8, `language="hy"`) -> `translate.py` (transformers pipeline) -> terminal. Modules don't import each other; `main.py` wires them.

## Model choices
- **ASR: faster-whisper.** Whisper supports Armenian; CTranslate2 int8 on CPU is fast enough for a 5 s budget and runs on any laptop. Size is a flag (`small` default) so WER vs latency can be tuned. Alternatives: wav2vec2 Armenian fine-tunes (less robust, no punctuation), SeamlessM4T (heavy).
- **Translation: `Helsinki-NLP/opus-mt-hy-en`** (small, CPU-friendly), id configurable. Fallback: `facebook/nllb-200-distilled-600M` (`hye_Armn`). See `DECISIONS.md`.

## Status & honest limitations
- **Not yet benchmarked on real audio.** The authoring sandbox could not reach Hugging Face, so only the pipeline logic was tested, with stubbed models. The existence/quality of the default MT model id, Whisper's Armenian accuracy and the <5 s latency are unverified. Run Step 5 on your machine and fill in `TESTS.md`.
- File streaming only: no microphone or system-audio loopback capture (no `sounddevice` yet).
- Single hard-coded `Speaker 1` label: no `Me` label, no diarization.
- Silence segmentation is a fixed RMS threshold; noisy audio may not split. Phrases are capped at 8 s.
- Latency shown is ASR+MT time after the phrase closes, plus up to 1 s waiting for the silence block.

## Next steps
Live capture with `sounddevice` for mic + loopback (BlackHole), speaker embeddings for `Speaker N`, VAD instead of RMS, benchmark ASR sizes.
