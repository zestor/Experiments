from pathlib import Path
import sys

# Add the repository's ``core`` directory to the Python path so ``vectordb``
# can be imported when running the tests from any location.
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402


def test_rest_endpoints(tmp_path):
    from vectordb import VectorDB, create_app

    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json")
    app = create_app(vdb)
    client = TestClient(app)

    resp = client.post("/add", json={"text": "foo"})
    assert resp.status_code == 200

    resp = client.get("/search", params={"q": "foo", "k": 1})
    assert resp.status_code == 200
    assert resp.json()[0]["text"] == "foo"


def test_validation_errors(tmp_path):
    from vectordb import VectorDB, create_app

    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json")
    app = create_app(vdb)
    client = TestClient(app)

    resp = client.post("/add", json={"text": ""})
    assert resp.status_code == 422

    resp = client.get("/search", params={"q": "foo", "k": 0})
    assert resp.status_code == 422

    resp = client.get("/search", params={"q": "foo", "k": 1})
    assert resp.status_code == 400


def test_api_key_required(tmp_path):
    from vectordb import VectorDB, create_app

    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json")
    app = create_app(vdb, api_key="secret")
    client = TestClient(app)

    resp = client.post("/add", json={"text": "foo"})
    assert resp.status_code == 401

    resp = client.post("/add", json={"text": "foo"}, headers={"X-API-Key": "secret"})
    assert resp.status_code == 200


def test_api_key_invalid(tmp_path):
    from vectordb import VectorDB, create_app

    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json")
    app = create_app(vdb, api_key="secret")
    client = TestClient(app)

    resp = client.post("/add", json={"text": "foo"}, headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401
