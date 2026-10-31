"""Simulated live audio stream: reads a .wav file in fixed-size blocks."""
import time
from typing import Iterator

import numpy as np
import soundfile as sf

SAMPLE_RATE = 16_000


def stream_wav(path: str, block_seconds: float = 1.0, realtime: bool = True) -> Iterator[np.ndarray]:
    """Yield mono float32 blocks at 16 kHz, as a live microphone would.

    Fails loudly if the file is not 16 kHz (no silent resampling).
    If realtime is True, sleeps one block duration between blocks.
    """
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
