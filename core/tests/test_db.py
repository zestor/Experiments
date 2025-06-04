from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from vectordb import VectorDB


def test_add_and_search(tmp_path, monkeypatch):
    monkeypatch.setattr("vectordb.db.INDEX_PATH", tmp_path / "index.bin")
    monkeypatch.setattr("vectordb.db.DATA_PATH", tmp_path / "data.json")

    vdb = VectorDB()

    sentences = [f"This is sample sentence {i}" for i in range(1000)]
    vdb.add_texts(sentences)

    query = sentences[42]
    results = vdb.search(query, k=5)
    texts = [r["text"] for r in results]

    assert query in texts
