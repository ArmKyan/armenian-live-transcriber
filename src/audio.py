"""Audio sources. Every source yields 16 kHz mono float32 blocks.

stream_wav    - simulates a live source from a file
stream_device - captures a live input device (microphone, or a loopback device such as
                BlackHole / Stereo Mix / a PulseAudio monitor) with sounddevice
"""
import math
import queue
import sys
import time
from typing import Iterator

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

SAMPLE_RATE = 16_000


def stream_wav(path: str, block_seconds: float = 0.2, realtime: bool = True) -> Iterator[np.ndarray]:
    """Yield mono float32 blocks from a 16 kHz wav file. Fails loudly on other rates."""
    block_size = int(SAMPLE_RATE * block_seconds)
    with sf.SoundFile(path) as f:
        if f.samplerate != SAMPLE_RATE:
            raise ValueError(f"{path}: expected {SAMPLE_RATE} Hz, got {f.samplerate} Hz")
        for block in f.blocks(blocksize=block_size, dtype="float32"):
            if block.ndim > 1:
                block = block.mean(axis=1)
            yield block
            if realtime:
                time.sleep(block_seconds)


def list_devices() -> None:
    import sounddevice as sd

    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0:
            api = sd.query_hostapis(d["hostapi"])["name"]
            print(f"{i}: {d['name']}  [{d['max_input_channels']} ch, {int(d['default_samplerate'])} Hz, {api}]")


def stream_device(device: int, block_seconds: float = 0.2) -> Iterator[np.ndarray]:
    """Capture an input device forever. Opens it at its native rate and resamples to 16 kHz."""
    import sounddevice as sd

    info = sd.query_devices(device, "input")
    native = int(info["default_samplerate"])
    channels = min(int(info["max_input_channels"]), 2)
    g = math.gcd(native, SAMPLE_RATE)
    up, down = SAMPLE_RATE // g, native // g

    q: queue.Queue = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            print(f"audio status (device {device}): {status}", file=sys.stderr)
        q.put(indata.mean(axis=1).copy())

    with sd.InputStream(
        device=device,
        channels=channels,
        samplerate=native,
        dtype="float32",
        blocksize=int(native * block_seconds),
        callback=callback,
    ):
        while True:
            block = q.get()
            if native != SAMPLE_RATE:
                block = resample_poly(block, up, down).astype(np.float32)
            yield block
