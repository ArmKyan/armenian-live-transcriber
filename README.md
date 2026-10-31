# Armenian Live Transcriber

Listens to two audio sources at once: your microphone (labelled `Me`) and the system audio output, i.e. the other people on a call (labelled `Speaker 1`, `Speaker 2`, ...). Each finished phrase is transcribed in Armenian with a local fine-tuned Whisper model, translated to English with a local NLLB model, and printed in this format (illustrative example, not a measured run):

```
[00:01:12] Speaker 1
HY: Բարև, ինչպե՞ս ես։
EN: Hi, how are you?
    (latency 2.4s after end of speech)
```

Everything runs locally. Wav files can stand in for either source for testing (see Run). See "Honest status and limitations" below for what has and has not been tested.

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Models download from Hugging Face on first run (internet needed once; afterwards fully local). Roughly 5 GB in total.

## Audio setup (needed for live use)
The program needs two input devices: your microphone, and a loopback device that carries what you hear (the other people on the call).

**macOS:** `brew install blackhole-2ch`, open *Audio MIDI Setup*, create a *Multi-Output Device* with your speakers/headphones + *BlackHole 2ch*, and set it as the system output. BlackHole 2ch is then your loopback input.

**Windows:** enable *Stereo Mix* (Sound settings -> Recording -> show disabled devices), or install a virtual cable such as VB-Cable and route the call's output to it. Prefer the plain MME/DirectSound entries in the device list.

**Linux (PulseAudio/PipeWire):** use the "Monitor of ..." input as the loopback device.

## Run
```bash
python src/main.py --list-devices                         # find device indexes
python src/main.py --mic-device 1 --loopback-device 3     # live
```
Testing without hardware (wav files must be 16 kHz):
```bash
python src/main.py --input test_audio.hy.wav              # file as system audio
python src/main.py --mic-input me.wav --input others.wav  # both sources
# --fast skips real-time pacing, --no-diarize skips speaker model, --speaker-threshold, --silence-rms, --end-silence
```
Output: `[HH:MM:SS] Me | Speaker N`, then `HY:` and `EN:` lines and the latency after end of speech. On Windows set `$env:PYTHONUTF8="1"` and use a console font with Armenian glyphs (or redirect to a UTF-8 file).

## Architecture
```
mic device ----> capture thread -> Segmenter --\
                                                +--> queue --> ASR -> MT -> label -> terminal
loopback device -> capture thread -> Segmenter --/                       (Me / SpeakerTracker)
```
`audio.py` sources, `segment.py` energy-based phrase splitting, `transcribe.py` Whisper pipeline, `translate.py` NLLB, `speakers.py` ECAPA speaker matching, `device.py` picks CUDA/MPS/CPU, `main.py` wires them.

## Model choices (measured on 8 Common Voice clips; see `TESTS.md`, `DECISIONS.md`)
- **ASR: `Chillarmo/whisper-large-v3-turbo-armenian`.** Stock Whisper tiny/small/medium were garbled or error-prone for Armenian; this Armenian fine-tune gave readable, mostly correct text. Alternatives: `whisper-small-armenian-v2` (smaller, higher reported WER), `arampacha/whisper-large-hy`.
- **Translation: `facebook/nllb-200-distilled-1.3B`.** `opus-mt-hy-en` gave fluent but wrong English with a religious-text bias; NLLB-600M was better, 1.3B best.

## Honest status and limitations
- **Tested only with wav files, in Colab on a T4 GPU**: the whole pipeline (two sources, `Me`/`Speaker N` labels, Armenian ASR, English MT) ran end to end. **Not tested:** real microphone capture, real loopback capture, and speaker separation on a real conversation. Speaker labels matched ground truth on a small 3-speaker test at the default threshold 0.45; tune with `--speaker-threshold` for real calls.
- **Latency:** on a Colab T4 GPU, phrases took about 2-3 s (4.1 s once, when two sources finished together) after the end of speech after model warm-up (before warm-up the first phrases took 8-10 s). **CPU latency is not measured**; the ASR model is 0.8B parameters and likely needs a GPU or a fast modern CPU. A 2009 Core 2 Duo took 100-300 s per phrase with stock Whisper. Latency printed is measured from the end of speech to the printed line and includes the 0.8 s end-of-phrase silence wait (`--end-silence`).
- Models were checked by eye on 8 Common Voice clips, not as WER; real calls will be harder.
- One worker processes phrases in order; if it falls behind, latency grows silently.
- Speaker labels are per phrase (no mid-phrase changes), rely on a fixed threshold, and fail on overlapping speech.
- Energy-threshold segmentation, no VAD; Whisper may hallucinate text on noise.
- No echo handling (out of scope per the brief).

## Next steps
Measure and tune on the interview laptop, CTranslate2 conversion for speed, a backlog warning, VAD instead of RMS, tune the speaker threshold on real conversations.
