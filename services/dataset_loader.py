import json
import os


class SymptomDataset:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tagged_path = os.path.join(base_dir, "data", "symptom_dataset_tagged.json")
        plain_path = os.path.join(base_dir, "data", "symptom_dataset.json")
        self.path = tagged_path if os.path.exists(tagged_path) else plain_path
        self.entries = self._load_entries()

    def _load_entries(self):
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as file:
            raw = json.load(file)

        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            for key in ("data", "entries", "symptoms"):
                value = raw.get(key)
                if isinstance(value, list):
                    return value
        return []

    def get_all_sentences(self):
        sentences = []
        for entry in self.entries:
            sentence = (
                entry.get("user_sentence")
                or entry.get("symptom")
                or entry.get("query")
                or entry.get("interpreted_meaning")
                or entry.get("friendly_explanation_english")
            )
            if sentence:
                sentences.append(str(sentence))
        return sentences

    def get_entry(self, index):
        try:
            return self.entries[int(index)]
        except (TypeError, ValueError, IndexError):
            return None

    def get_body_part(self, index):
        entry = self.get_entry(index) or {}
        return str(entry.get("body_part") or entry.get("category") or "general").lower()


dataset = SymptomDataset()
