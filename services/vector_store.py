import re

import numpy as np

from services.dataset_loader import dataset

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    faiss = None
    SentenceTransformer = None


BODY_HINTS = {
    "eyes": ["aankh", "ankh", "eye", "eyes", "vision", "jal", "burning"],
    "stomach": ["pet", "acidity", "gas", "khana", "digest", "stomach"],
    "head": ["sar", "sir", "head", "migraine", "pressure"],
    "throat": ["gala", "throat", "khansi", "cough"],
    "skin": ["skin", "khujli", "rash", "redness"],
    "energy": ["thakan", "weakness", "tired", "fatigue"],
    "mental": ["anxiety", "stress", "ghabrahat", "panic"],
}


def word_match(text, words):
    return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)


def detect_query_body_part(text: str):
    t = (text or "").lower()
    for part, words in BODY_HINTS.items():
        if word_match(t, words):
            return part
    return "general"


class SymptomVectorStore:
    def __init__(self):
        self.model = None
        self.index = None
        self.sentences = dataset.get_all_sentences()

        if not self.sentences or faiss is None or SentenceTransformer is None:
            return

        try:
            self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            embeddings = self.model.encode(
                self.sentences,
                normalize_embeddings=True
            ).astype("float32")
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            self.index.add(embeddings)
        except Exception:
            self.model = None
            self.index = None

    def _keyword_search(self, user_input, top_k):
        words = set(re.findall(r"[a-zA-Z\u0900-\u097F]+", (user_input or "").lower()))
        if not words:
            return []

        scored = []
        for idx, sentence in enumerate(self.sentences):
            sentence_words = set(re.findall(r"[a-zA-Z\u0900-\u097F]+", sentence.lower()))
            overlap = len(words & sentence_words)
            if overlap:
                scored.append((overlap, idx))

        scored.sort(reverse=True)
        return [idx for _, idx in scored[:top_k]]

    def search(self, user_input, top_k=5, threshold=0.35):
        if not self.sentences:
            return []

        if self.index is None or self.model is None:
            fallback = self._keyword_search(user_input, top_k)
            return fallback or [0]

        query_part = detect_query_body_part(user_input)
        query_vector = self.model.encode(
            [user_input],
            normalize_embeddings=True
        ).astype("float32")

        scores, indices = self.index.search(query_vector, top_k)
        filtered = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or score < threshold:
                continue

            entry_part = dataset.get_body_part(idx)
            if query_part != "general" and entry_part != query_part:
                continue

            filtered.append(int(idx))

        if not filtered and len(indices[0]) and indices[0][0] >= 0:
            filtered.append(int(indices[0][0]))

        return filtered


vector_store = SymptomVectorStore()
