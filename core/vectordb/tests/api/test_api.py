from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient


def test_rest_endpoints(tmp_path, monkeypatch):
    monkeypatch.setattr("vectordb.db.INDEX_PATH", tmp_path / "index.bin")
    monkeypatch.setattr("vectordb.db.DATA_PATH", tmp_path / "data.json")

    from vectordb import VectorDB, create_app
    vdb = VectorDB()
    app = create_app(vdb)
    client = TestClient(app)

    resp = client.post("/add", json={"text": "foo"})
    assert resp.status_code == 200

    resp = client.get("/search", params={"q": "foo", "k": 1})
    assert resp.status_code == 200
    assert resp.json()[0]["text"] == "foo"
