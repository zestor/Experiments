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

    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


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


def test_text_too_long(tmp_path):
    from vectordb import VectorDB, create_app

    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json", max_text_length=5)
    app = create_app(vdb)
    client = TestClient(app)

    resp = client.post("/add", json={"text": "toolong"})
    assert resp.status_code == 422


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


def test_health_does_not_require_api_key(tmp_path):
    from vectordb import VectorDB, create_app

    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json")
    app = create_app(vdb, api_key="secret")
    client = TestClient(app)

    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_add_exceeds_max_elements(tmp_path):
    from vectordb import VectorDB, create_app

    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json", max_elements=1)
    app = create_app(vdb)
    client = TestClient(app)

    resp = client.post("/add", json={"text": "one"})
    assert resp.status_code == 200

    resp = client.post("/add", json={"text": "two"})
    assert resp.status_code == 400


def test_api_logging(tmp_path, caplog):
    from vectordb import VectorDB, create_app

    caplog.set_level("INFO")
    vdb = VectorDB(index_path=tmp_path / "index.bin", data_path=tmp_path / "data.json")
    app = create_app(vdb)
    client = TestClient(app)

    client.post("/add", json={"text": "foo"})
    client.get("/search", params={"q": "foo", "k": 1})

    logs = caplog.text
    assert "add text" in logs
    assert "search q=foo k=1" in logs
