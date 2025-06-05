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


def test_logging(tmp_path, caplog):
    from vectordb import VectorDB
    caplog.set_level("INFO")

    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json")
    vdb.add_text("foo")

    assert any("Adding 1 texts" in m for m in caplog.text.splitlines())


def test_configurable_index(tmp_path):
    from vectordb import VectorDB

    vdb = VectorDB(
        index_path=tmp_path / "index.bin",
        data_path=tmp_path / "data.json",
        max_elements=500,
        ef_construction=100,
        M=8,
        ef=20,
        space="l2",
    )

    assert vdb.index.init_params == {
        "max_elements": 500,
        "ef_construction": 100,
        "M": 8,
    }
    assert vdb.index.ef == 20
    assert vdb.index.space == "l2"


def test_load_fallback(tmp_path, monkeypatch):
    from vectordb import VectorDB

    def bad_load(self, path):
        raise RuntimeError("broken")

    monkeypatch.setattr("vectordb.db.hnswlib.Index.load_index", bad_load)

    idx = tmp_path / "index.bin"
    data = tmp_path / "data.json"
    idx.write_text("junk")
    data.write_text("[]")

    vdb = VectorDB(index_path=idx, data_path=data)

    assert vdb.texts == []
    assert vdb.index.init_params


def test_search_invalid_k(tmp_path):
    from vectordb import VectorDB
    import pytest

    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json")
    vdb.add_text("hello")

    with pytest.raises(ValueError):
        vdb.search("hello", k=0)

    with pytest.raises(ValueError):
        vdb.search("hello", k=2)
