from pathlib import Path
import sys
import json
import types
import pytest

# Make sure the ``core`` directory is on the import path for the tests.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class DummyModel:
    dim = 3

    @classmethod
    def from_pretrained(cls, name):
        return cls()

    def encode(self, texts):
        arr = []
        for t in texts:
            h = hash(t) & 0xFFFFFFFF
            arr.append([(h >> (i * 8)) & 0xFF for i in range(self.dim)])
        return arr

class DummyIndex:
    def __init__(self, space="cosine", dim=3):
        self.space = space
        self.dim = dim
        self.vectors = {}
        self.init_params = {}
        self.ef = None

    def init_index(self, max_elements=10000, ef_construction=200, M=16):
        self.init_params = {
            "max_elements": max_elements,
            "ef_construction": ef_construction,
            "M": M,
        }

    def set_ef(self, ef):
        self.ef = ef

    def add_items(self, vecs, ids):
        for vec, idx in zip(vecs, ids):
            self.vectors[int(idx)] = vec

    def knn_query(self, vecs, k=5):
        labels = []
        distances = []
        for vec in vecs:
            dists = []
            for idx, v in self.vectors.items():
                dist = float(sum((a - b) ** 2 for a, b in zip(vec, v)) ** 0.5)
                dists.append((dist, idx))
            dists.sort(key=lambda x: x[0])
            top = dists[:k]
            labels.append([idx for _, idx in top])
            distances.append([dist for dist, _ in top])
        return labels, distances

    def save_index(self, path):
        Path(path).write_text(json.dumps({str(k): v for k, v in self.vectors.items()}))

    def load_index(self, path):
        data = json.loads(Path(path).read_text())
        self.vectors = {int(k): v for k, v in data.items()}

hnswlib_stub = types.ModuleType("hnswlib")
hnswlib_stub.Index = DummyIndex
sys.modules.setdefault("hnswlib", hnswlib_stub)

model2vec_stub = types.ModuleType("model2vec")
model2vec_stub.StaticModel = DummyModel
sys.modules.setdefault("model2vec", model2vec_stub)

@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    import vectordb.db as db
    monkeypatch.setattr(db, "StaticModel", DummyModel)
    monkeypatch.setattr(db.hnswlib, "Index", DummyIndex)
    yield
