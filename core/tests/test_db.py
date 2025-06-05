from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_add_and_search(tmp_path, monkeypatch):
    from vectordb import VectorDB
    monkeypatch.setattr("vectordb.db.INDEX_PATH", tmp_path / "index.bin")
    monkeypatch.setattr("vectordb.db.DATA_PATH", tmp_path / "data.json")

    vdb = VectorDB()
    sentences = [f"This is sample sentence {i}" for i in range(20)]
    vdb.add_texts(sentences)

    query = sentences[5]
    results = vdb.search(query, k=5)
    texts = [r["text"] for r in results]

    assert query in texts


def test_persistence_and_clear(tmp_path, monkeypatch):
    idx = tmp_path / "index.bin"
    data = tmp_path / "data.json"
    monkeypatch.setattr("vectordb.db.INDEX_PATH", idx)
    monkeypatch.setattr("vectordb.db.DATA_PATH", data)

    from vectordb import VectorDB
    vdb = VectorDB()
    vdb.add_text("hello world")
    assert vdb.search("hello world", k=1)[0]["text"] == "hello world"

    vdb2 = VectorDB()
    assert vdb2.search("hello world", k=1)[0]["text"] == "hello world"

    VectorDB.clear()
    assert not idx.exists()
    assert not data.exists()
