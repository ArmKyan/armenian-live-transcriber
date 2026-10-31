"""End-to-end pipeline: simulated live audio -> Armenian ASR -> English MT -> terminal."""
import argparse
import time

import numpy as np

from audio import SAMPLE_RATE, stream_wav
from transcribe import Transcriber
from translate import DEFAULT_MODEL, Translator

SILENCE_RMS = 0.01      # block RMS below this counts as silence
END_SILENCE_BLOCKS = 1  # silent 1 s blocks that close a phrase
MAX_PHRASE_BLOCKS = 8   # force a flush so latency stays bounded


def fmt_ts(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def run(args: argparse.Namespace) -> None:
    asr = Transcriber(args.asr_model)
    mt = Translator(args.mt_model)

    phrase: list[np.ndarray] = []
    silent = 0
    phrase_start = 0.0
    position = 0.0

    def flush() -> None:
        nonlocal phrase, silent
        audio = np.concatenate(phrase)
        phrase, silent = [], 0
        t0 = time.perf_counter()
        hy = asr.transcribe(audio)
        if not hy:
            return
        en = mt.translate(hy)
        latency = time.perf_counter() - t0
        print(f"[{fmt_ts(phrase_start)}] Speaker 1")
        print(f"HY: {hy}")
        print(f"EN: {en}")
        print(f"    (latency {latency:.2f}s)\n", flush=True)

    for block in stream_wav(args.input, realtime=not args.fast):
        rms = float(np.sqrt(np.mean(block**2)))
        if rms >= SILENCE_RMS:
            if not phrase:
                phrase_start = position
            phrase.append(block)
            silent = 0
        elif phrase:
            silent += 1
            if silent >= END_SILENCE_BLOCKS:
                flush()
        position += len(block) / SAMPLE_RATE
        if len(phrase) >= MAX_PHRASE_BLOCKS:
            flush()
    if phrase:
        flush()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="16 kHz .wav file to stream")
    p.add_argument("--asr-model", default="small")
    p.add_argument("--mt-model", default=DEFAULT_MODEL)
    p.add_argument("--fast", action="store_true", help="don't sleep between blocks")
    run(p.parse_args())
