"""Energy-based phrase segmentation for one audio source."""
import time

import numpy as np

from audio import SAMPLE_RATE


class Segmenter:
    """Feed blocks; get back a finished phrase after enough trailing silence."""

    def __init__(self, silence_rms=0.01, end_silence_s=0.6, max_phrase_s=8.0, min_phrase_s=0.4):
        self.silence_rms = silence_rms
        self.end_silence_s = end_silence_s
        self.max_phrase_s = max_phrase_s
        self.min_phrase_s = min_phrase_s
        self._reset()

    def _reset(self):
        self.blocks: list[np.ndarray] = []
        self.samples = 0
        self.silence_s = 0.0
        self.start_mono = 0.0
        self.last_speech_mono = 0.0

    def feed(self, block: np.ndarray, now: float | None = None):
        """Return (audio, start_mono, end_mono) when a phrase is complete, else None."""
        now = time.monotonic() if now is None else now
        dur = len(block) / SAMPLE_RATE
        speech = float(np.sqrt(np.mean(block**2))) >= self.silence_rms
        if speech:
            if not self.blocks:
                self.start_mono = now - dur
            self.last_speech_mono = now
            self.silence_s = 0.0
        elif not self.blocks:
            return None  # silence before any speech
        else:
            self.silence_s += dur
        self.blocks.append(block)
        self.samples += len(block)
        if self.silence_s >= self.end_silence_s or self.samples / SAMPLE_RATE >= self.max_phrase_s:
            return self._flush()
        return None

    def finish(self):
        return self._flush() if self.blocks else None

    def _flush(self):
        audio = np.concatenate(self.blocks)
        start, end = self.start_mono, self.last_speech_mono
        self._reset()
        if len(audio) / SAMPLE_RATE < self.min_phrase_s:
            return None
        return audio, start, end
