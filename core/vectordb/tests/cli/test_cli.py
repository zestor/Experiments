from pathlib import Path
import sys
from io import StringIO

# Allow importing the ``vectordb`` package when running tests directly.
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def test_cli_add_and_query(tmp_path, monkeypatch, capsys):
    from vectordb.cli import main
    monkeypatch.setattr("vectordb.db.INDEX_PATH", tmp_path / "index.bin")
    monkeypatch.setattr("vectordb.db.DATA_PATH", tmp_path / "data.json")

    main(["add", "foo bar"])
    main(["query", "foo bar"])
    captured = capsys.readouterr()
    assert "foo bar" in captured.out


def test_cli_serve(tmp_path, monkeypatch):
    monkeypatch.setattr("vectordb.db.INDEX_PATH", tmp_path / "index.bin")
    monkeypatch.setattr("vectordb.db.DATA_PATH", tmp_path / "data.json")

    called = {}
    def fake_run(app, host="0.0.0.0", port=8000):
        called["app"] = app
        called["host"] = host
        called["port"] = port
    monkeypatch.setattr("uvicorn.run", fake_run)
    from vectordb.cli import main

    main(["serve"])
    assert called.get("app") is not None
    assert called["host"] == "0.0.0.0" and called["port"] == 8000
