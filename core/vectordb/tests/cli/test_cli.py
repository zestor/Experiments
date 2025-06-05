from pathlib import Path
import sys
from io import StringIO  # noqa: F401 - imported for compatibility

# Allow importing the ``vectordb`` package when running tests directly.
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def test_cli_add_and_query(tmp_path, capsys):
    from vectordb.cli import main

    args = [
        "--index-path",
        str(tmp_path / "index.bin"),
        "--data-path",
        str(tmp_path / "data.json"),
    ]

    main(args + ["add", "foo bar"])
    main(args + ["query", "foo bar"])
    captured = capsys.readouterr()
    assert "foo bar" in captured.out


def test_cli_serve(tmp_path, monkeypatch):
    called = {}
    def fake_run(app, host="0.0.0.0", port=8000):
        called["app"] = app
        called["host"] = host
        called["port"] = port
    monkeypatch.setattr("uvicorn.run", fake_run)
    from vectordb.cli import main

    args = [
        "--index-path",
        str(tmp_path / "index.bin"),
        "--data-path",
        str(tmp_path / "data.json"),
    ]

    main(args + ["serve", "--host", "127.0.0.1", "--port", "1234"])
    assert called.get("app") is not None
    assert called["host"] == "127.0.0.1" and called["port"] == 1234
