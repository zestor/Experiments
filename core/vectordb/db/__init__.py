import json
import logging
from pathlib import Path
from typing import List

import hnswlib
from model2vec import StaticModel

INDEX_PATH = Path("index.bin")
DATA_PATH = Path("data.json")
MODEL_NAME = "cnmoro/Linq-Embed-Mistral-Distilled"

logger = logging.getLogger(__name__)


class VectorDB:
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        *,
        index_path: Path = INDEX_PATH,
        data_path: Path = DATA_PATH,
        max_elements: int = 10000,
        ef_construction: int = 200,
        M: int = 16,
        ef: int = 50,
        space: str = "cosine",
        max_text_length: int = 1000,
    ) -> None:
        """Create a new ``VectorDB`` instance.

        Parameters
        ----------
        model_name:
            Name of the embedding model to load.
        index_path:
            Where to persist the vector index.
        data_path:
            Where to persist the stored texts.
        max_elements:
            Maximum number of elements to store in the index. Adding more
            texts than this limit will raise ``ValueError``.
        ef_construction:
            HNSW ``ef_construction`` parameter controlling build accuracy.
        M:
            HNSW ``M`` parameter controlling graph connectivity.
        ef:
            ``ef`` parameter used during search.
        space:
            Distance metric used by ``hnswlib`` (e.g. ``"cosine"``, ``"l2"``).
        max_text_length:
            Maximum length of text entries to store. Texts exceeding this
            length will raise ``ValueError`` when added.
        All numeric parameters must be greater than or equal to ``1``.
        """

        if max_elements < 1:
            raise ValueError("max_elements must be >= 1")
        if max_text_length < 1:
            raise ValueError("max_text_length must be >= 1")
        if ef_construction < 1:
            raise ValueError("ef_construction must be >= 1")
        if M < 1:
            raise ValueError("M must be >= 1")
        if ef < 1:
            raise ValueError("ef must be >= 1")

        self.index_path = Path(index_path)
        self.data_path = Path(data_path)
        self.max_elements = max_elements
        self.ef_construction = ef_construction
        self.M = M
        self.ef = ef
        self.space = space
        self.max_text_length = max_text_length

        logger.debug(
            "Initializing VectorDB with index_path=%s data_path=%s",
            self.index_path,
            self.data_path,
        )

        self.model = StaticModel.from_pretrained(model_name)
        self.dim = self.model.dim
        self.index = hnswlib.Index(space=space, dim=self.dim)
        self.texts: List[str] = []

        if self.index_path.exists() and self.data_path.exists():
            logger.debug("Loading existing index from %s", self.index_path)
            try:
                self.index.load_index(str(self.index_path))
                self.texts = json.loads(self.data_path.read_text())
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Failed to load index: %s; recreating", exc)
                self.index.init_index(
                    max_elements=max_elements,
                    ef_construction=ef_construction,
                    M=M,
                )
                self.texts = []
        else:
            logger.debug("Creating new index at %s", self.index_path)
            self.index.init_index(
                max_elements=max_elements,
                ef_construction=ef_construction,
                M=M,
            )
        self.index.set_ef(ef)

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
            logger.info("Deleting index file %s", index_path)
            Path(index_path).unlink()
        if Path(data_path).exists():
            logger.info("Deleting data file %s", data_path)
            Path(data_path).unlink()

    def save(self) -> None:
        """Persist the current index and texts to disk."""
        logger.debug("Saving index to %s and data to %s", self.index_path, self.data_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.index.save_index(str(self.index_path))
        self.data_path.write_text(json.dumps(self.texts))

    def add_text(self, text: str) -> None:
        self.add_texts([text])

    def add_texts(self, texts: List[str]) -> None:
        logger.info("Adding %d texts", len(texts))
        if len(self.texts) + len(texts) > self.max_elements:
            raise ValueError(
                f"adding {len(texts)} texts exceeds max_elements={self.max_elements}"
            )
        for t in texts:
            if len(t) > self.max_text_length:
                raise ValueError(
                    f"text length {len(t)} exceeds max_text_length={self.max_text_length}"
                )
        vecs = self.model.encode(texts)
        start = len(self.texts)
        ids = list(range(start, start + len(texts)))
        self.index.add_items(vecs, ids)
        self.texts.extend(texts)
        self.save()

    def search(self, query: str, k: int = 5) -> List[dict[str, float | str]]:
        """Return the ``k`` nearest texts to ``query``.

        Parameters
        ----------
        query:
            Text to search for.
        k:
            Number of results to return. Must be between 1 and the number of
            stored texts.
        """

        if k < 1:
            raise ValueError("k must be >= 1")
        if k > len(self.texts):
            raise ValueError("k exceeds number of stored texts")

        logger.debug("Searching for '%s' with k=%d", query, k)
        vec = self.model.encode([query])[0]
        labels, distances = self.index.knn_query([vec], k=k)
        results = []
        for label, dist in zip(labels[0], distances[0]):
            results.append({"text": self.texts[label], "distance": float(dist)})
        return results

    def count(self) -> int:
        """Return the number of stored texts."""
        return len(self.texts)
