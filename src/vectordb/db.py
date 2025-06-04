import json
from pathlib import Path
from typing import List

import hnswlib
from model2vec import StaticModel

INDEX_PATH = Path("index.bin")
DATA_PATH = Path("data.json")
MODEL_NAME = "cnmoro/Linq-Embed-Mistral-Distilled"


class VectorDB:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = StaticModel.from_pretrained(model_name)
        self.dim = self.model.dim
        self.index = hnswlib.Index(space="cosine", dim=self.dim)
        self.texts: List[str] = []
        if INDEX_PATH.exists() and DATA_PATH.exists():
            self.index.load_index(str(INDEX_PATH))
            self.texts = json.loads(DATA_PATH.read_text())
        else:
            self.index.init_index(max_elements=10000, ef_construction=200, M=16)
        self.index.set_ef(50)

    @staticmethod
    def clear():
        """Delete any persisted index and text data."""
        if INDEX_PATH.exists():
            INDEX_PATH.unlink()
        if DATA_PATH.exists():
            DATA_PATH.unlink()

    def save(self):
        self.index.save_index(str(INDEX_PATH))
        DATA_PATH.write_text(json.dumps(self.texts))

    def add_text(self, text: str):
        self.add_texts([text])

    def add_texts(self, texts: List[str]):
        vecs = self.model.encode(texts)
        start = len(self.texts)
        ids = list(range(start, start + len(texts)))
        self.index.add_items(vecs, ids)
        self.texts.extend(texts)
        self.save()

    def search(self, query: str, k: int = 5):
        vec = self.model.encode([query])[0]
        labels, distances = self.index.knn_query([vec], k=k)
        results = []
        for label, dist in zip(labels[0], distances[0]):
            results.append({"text": self.texts[label], "distance": float(dist)})
        return results
