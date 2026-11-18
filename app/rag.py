"""Retrieval layer: TF-IDF index over attractions and travel tips (RAG)."""
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA = json.loads((Path(__file__).parent / "data" / "destinations.json").read_text(encoding="utf-8"))


class KnowledgeBase:
    def __init__(self, data=DATA):
        self.data = data
        self.docs = []  # {dest, kind, text, item}
        for dest, info in data.items():
            for a in info["attractions"]:
                text = f'{a["name"]}. {a["category"]}. {a["area"]}. {a["desc"]}'
                self.docs.append({"dest": dest, "kind": "attraction", "text": text, "item": a})
            for t in info["tips"]:
                self.docs.append({"dest": dest, "kind": "tip", "text": t, "item": t})
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vec.fit_transform([d["text"] for d in self.docs])

    def destinations(self):
        return sorted(self.data)

    def search(self, query, dest=None, kind=None, k=5):
        """Return top-k (score, doc) for a query, optionally filtered."""
        scores = cosine_similarity(self.vec.transform([query]), self.matrix)[0]
        hits = [(float(s), d) for s, d in zip(scores, self.docs)
                if (dest is None or d["dest"] == dest) and (kind is None or d["kind"] == kind)]
        return sorted(hits, key=lambda x: -x[0])[:k]

    def detect_destination(self, text):
        low = text.lower()
        return next((d for d in self.data if d.lower() in low), None)
