from pathlib import Path
import sys

# ``vectordb`` lives two directories above ``tests`` so ensure it is importable.
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def test_add_and_search(tmp_path):
    from vectordb import VectorDB

    idx = tmp_path / "index.bin"
    data = tmp_path / "data.json"
    vdb = VectorDB(index_path=idx, data_path=data)
    sentences = [f"This is sample sentence {i}" for i in range(20)]
    vdb.add_texts(sentences)

    query = sentences[5]
    results = vdb.search(query, k=5)
    texts = [r["text"] for r in results]

    assert query in texts


def test_persistence_and_clear(tmp_path):
    idx = tmp_path / "index.bin"
    data = tmp_path / "data.json"

    from vectordb import VectorDB
    vdb = VectorDB(index_path=idx, data_path=data)
    vdb.add_text("hello world")
    assert vdb.search("hello world", k=1)[0]["text"] == "hello world"

    vdb2 = VectorDB(index_path=idx, data_path=data)
    assert vdb2.search("hello world", k=1)[0]["text"] == "hello world"

    VectorDB.clear(index_path=idx, data_path=data)
    assert not idx.exists()
    assert not data.exists()
