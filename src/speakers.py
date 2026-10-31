"""Online speaker identification: ECAPA-TDNN embeddings + cosine matching to running centroids."""
import numpy as np
import torch
from speechbrain.inference.speaker import EncoderClassifier

from audio import SAMPLE_RATE


class SpeakerTracker:
    """Gives each distinct voice a stable label (Speaker 1, Speaker 2, ...) for the session."""

    def __init__(self, threshold: float = 0.45, min_seconds: float = 1.0):
        self.threshold = threshold
        self.min_seconds = min_seconds
        self.encoder = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="models/spkrec-ecapa-voxceleb",
            run_opts={"device": "cpu"},
        )
        self.centroids: list[np.ndarray] = []
        self.counts: list[int] = []

    def _embed(self, audio: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            e = self.encoder.encode_batch(torch.from_numpy(audio).unsqueeze(0))
        e = e.squeeze().cpu().numpy()
        return e / np.linalg.norm(e)

    def identify(self, audio: np.ndarray) -> str:
        emb = self._embed(audio)
        if not self.centroids:
            self._add(emb)
            return "Speaker 1"
        sims = [float(emb @ c) for c in self.centroids]
        best = int(np.argmax(sims))
        long_enough = len(audio) / SAMPLE_RATE >= self.min_seconds
        if sims[best] >= self.threshold:
            if long_enough:
                self._update(best, emb)
            return f"Speaker {best + 1}"
        if not long_enough:
            return f"Speaker {best + 1}"  # too short to trust as a new voice
        self._add(emb)
        return f"Speaker {len(self.centroids)}"

    def _add(self, emb):
        self.centroids.append(emb)
        self.counts.append(1)

    def _update(self, i, emb):
        n = self.counts[i]
        c = (self.centroids[i] * n + emb) / (n + 1)
        self.centroids[i] = c / np.linalg.norm(c)
        self.counts[i] = n + 1
