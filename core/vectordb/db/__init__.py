import json
from pathlib import Path
from typing import List

import hnswlib
from model2vec import StaticModel

INDEX_PATH = Path("index.bin")
DATA_PATH = Path("data.json")
MODEL_NAME = "cnmoro/Linq-Embed-Mistral-Distilled"


class VectorDB:
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        *,
        index_path: Path = INDEX_PATH,
        data_path: Path = DATA_PATH,
    ):
        """Create a new ``VectorDB`` instance.

        Parameters
        ----------
        model_name:
            Name of the embedding model to load.
        index_path:
            Where to persist the vector index.
        data_path:
            Where to persist the stored texts.
        """

        self.index_path = Path(index_path)
        self.data_path = Path(data_path)

        self.model = StaticModel.from_pretrained(model_name)
        self.dim = self.model.dim
        self.index = hnswlib.Index(space="cosine", dim=self.dim)
        self.texts: List[str] = []

        if self.index_path.exists() and self.data_path.exists():
            self.index.load_index(str(self.index_path))
            self.texts = json.loads(self.data_path.read_text())
        else:
            self.index.init_index(max_elements=10000, ef_construction=200, M=16)
        self.index.set_ef(50)

    @staticmethod
    def clear(index_path: Path = INDEX_PATH, data_path: Path = DATA_PATH) -> None:
        """Delete any persisted index and text data.

        Parameters
        ----------
        index_path:
            Location of the saved index file.
        data_path:
            Location of the saved text file.
        """

        if Path(index_path).exists():
            Path(index_path).unlink()
        if Path(data_path).exists():
            Path(data_path).unlink()

    def save(self) -> None:
        """Persist the current index and texts to disk."""
        self.index.save_index(str(self.index_path))
        self.data_path.write_text(json.dumps(self.texts))

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
