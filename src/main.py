"""Live pipeline: mic + system audio -> Armenian ASR -> English MT -> labelled terminal output.

Each source runs in its own thread (capture + phrase segmentation). Finished phrases go to one
queue; the main thread transcribes, translates, labels and prints them in order.
"""
import argparse
import queue
import threading
import time

from audio import list_devices, stream_device, stream_wav
from segment import Segmenter
from transcribe import DEFAULT_MODEL as ASR_MODEL
from transcribe import Transcriber
from translate import DEFAULT_MODEL as MT_MODEL
from translate import Translator

BLOCK_S = 0.2


def fmt_ts(seconds: float) -> str:
    s = max(0, int(seconds))
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def pump(name, blocks, silence_rms, jobs):
    """Capture thread: segment one source into phrases. Errors are passed to the main thread."""
    try:
        seg = Segmenter(silence_rms=silence_rms)
        for block in blocks:
            result = seg.feed(block)
            if result:
                jobs.put((name, *result))
        result = seg.finish()
        if result:
            jobs.put((name, *result))
        jobs.put(None)
    except BaseException as e:  # fail loudly: re-raised in the main thread
        jobs.put(e)


def build_sources(args):
    sources = []
    if args.mic_device is not None:
        sources.append(("mic", stream_device(args.mic_device, BLOCK_S)))
    if args.mic_input:
        sources.append(("mic", stream_wav(args.mic_input, BLOCK_S, realtime=not args.fast)))
    if args.loopback_device is not None:
        sources.append(("system", stream_device(args.loopback_device, BLOCK_S)))
    if args.input:
        sources.append(("system", stream_wav(args.input, BLOCK_S, realtime=not args.fast)))
    return sources


def run(args) -> None:
    sources = build_sources(args)
    asr = Transcriber(args.asr_model)
    mt = Translator(args.mt_model)
    tracker = None
    if any(name == "system" for name, _ in sources) and not args.no_diarize:
        from speakers import SpeakerTracker

        tracker = SpeakerTracker(args.speaker_threshold)

    t_session = time.monotonic()
    jobs: queue.Queue = queue.Queue()
    for name, blocks in sources:
        threading.Thread(target=pump, args=(name, blocks, args.silence_rms, jobs), daemon=True).start()
    print("Listening... (Ctrl+C to stop)", flush=True)

    finished = 0
    while finished < len(sources):
        try:
            job = jobs.get(timeout=0.5)
        except queue.Empty:
            continue
        if job is None:
            finished += 1
            continue
        if isinstance(job, BaseException):
            raise job
        name, audio, start, end = job
        hy = asr.transcribe(audio)
        if not hy:
            continue
        en = mt.translate(hy)
        if name == "mic":
            label = "Me"
        else:
            label = tracker.identify(audio) if tracker else "Speaker 1"
        print(f"[{fmt_ts(start - t_session)}] {label}")
        print(f"HY: {hy}")
        print(f"EN: {en}")
        print(f"    (latency {time.monotonic() - end:.2f}s after end of speech)\n", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Live Armenian transcription and English translation")
    p.add_argument("--list-devices", action="store_true", help="print input devices and exit")
    p.add_argument("--mic-device", type=int, help="input device index for your microphone ('Me')")
    p.add_argument("--loopback-device", type=int, help="input device index for system audio (other speakers)")
    p.add_argument("--mic-input", help="16 kHz wav to use as the microphone (testing)")
    p.add_argument("--input", help="16 kHz wav to use as system audio (testing)")
    p.add_argument("--fast", action="store_true", help="wav files: don't sleep between blocks")
    p.add_argument("--asr-model", default=ASR_MODEL)
    p.add_argument("--mt-model", default=MT_MODEL)
    p.add_argument("--silence-rms", type=float, default=0.01, help="block RMS below this is silence")
    p.add_argument("--speaker-threshold", type=float, default=0.45, help="cosine similarity to match a known speaker")
    p.add_argument("--no-diarize", action="store_true", help="label all system audio 'Speaker 1'")
    args = p.parse_args()
    if args.list_devices:
        list_devices()
    elif not (args.mic_device is not None or args.mic_input or args.loopback_device is not None or args.input):
        p.error("give at least one source: --mic-device/--loopback-device or --mic-input/--input")
    else:
        try:
            run(args)
        except KeyboardInterrupt:
            print("\nStopped.")
