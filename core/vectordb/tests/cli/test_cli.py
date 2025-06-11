from pathlib import Path
import sys
from io import StringIO  # noqa: F401 - imported for compatibility
import logging
import pytest

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
    main(args + ["query", "foo bar", "--k", "1"])
    captured = capsys.readouterr()
    assert "foo bar" in captured.out


def test_cli_serve(tmp_path, monkeypatch):
    called = {}

    def fake_run(app, host="0.0.0.0", port=8000, log_level="info", workers=1):
        called["app"] = app
        called["host"] = host
        called["port"] = port
        called["log_level"] = log_level
        called["workers"] = workers

    monkeypatch.setattr("uvicorn.run", fake_run)
    from vectordb.cli import main

    args = [
        "--index-path",
        str(tmp_path / "index.bin"),
        "--data-path",
        str(tmp_path / "data.json"),
    ]

    main(
        args
        + [
            "--log-level",
            "DEBUG",
            "serve",
            "--host",
            "127.0.0.1",
            "--port",
            "1234",
            "--workers",
            "2",
        ]
    )
    assert called.get("app") is not None
    assert called["host"] == "127.0.0.1" and called["port"] == 1234
    assert called["log_level"] == "debug"
    assert called["workers"] == 2


def test_cli_serve_api_key(tmp_path, monkeypatch):
    captured = {}

    def fake_create_app(vdb, api_key=None):
        captured["api_key"] = api_key
        return "app"

    monkeypatch.setattr("vectordb.cli.create_app", fake_create_app)
    monkeypatch.setattr(
        "uvicorn.run",
        lambda app, host="0", port=0, log_level="info", workers=1: None,
    )
    from vectordb.cli import main

    args = [
        "--index-path",
        str(tmp_path / "index.bin"),
        "--data-path",
        str(tmp_path / "data.json"),
    ]

    main(args + ["serve", "--api-key", "secret"])

    assert captured["api_key"] == "secret"


def test_cli_serve_api_key_env(tmp_path, monkeypatch):
    captured = {}

    def fake_create_app(vdb, api_key=None):
        captured["api_key"] = api_key
        return "app"

    from vectordb import API_KEY_ENV_VAR

    monkeypatch.setenv(API_KEY_ENV_VAR, "secret")
    monkeypatch.setattr("vectordb.cli.create_app", fake_create_app)
    monkeypatch.setattr(
        "uvicorn.run",
        lambda app, host="0", port=0, log_level="info", workers=1: None,
    )
    from vectordb.cli import main

    args = [
        "--index-path",
        str(tmp_path / "index.bin"),
        "--data-path",
        str(tmp_path / "data.json"),
    ]

    main(args + ["serve"])

    assert captured["api_key"] == "secret"


def test_cli_serve_host_port_env(tmp_path, monkeypatch):
    captured = {}

    def fake_run(app, host="0", port=0, log_level="info", workers=1):
        captured["host"] = host
        captured["port"] = port

    from vectordb import HOST_ENV_VAR, PORT_ENV_VAR

    monkeypatch.setenv(HOST_ENV_VAR, "1.2.3.4")
    monkeypatch.setenv(PORT_ENV_VAR, "1234")
    monkeypatch.setattr("uvicorn.run", fake_run)
    from vectordb.cli import main

    args = [
        "--index-path",
        str(tmp_path / "index.bin"),
        "--data-path",
        str(tmp_path / "data.json"),
    ]

    main(args + ["serve"])

    assert captured["host"] == "1.2.3.4"
    assert captured["port"] == 1234


def test_cli_serve_invalid_port_env(tmp_path, monkeypatch):
    captured = {}

    def fake_run(app, host="0", port=0, log_level="info", workers=1):
        captured["port"] = port

    from vectordb import PORT_ENV_VAR

    monkeypatch.setenv(PORT_ENV_VAR, "notanint")
    monkeypatch.setattr("uvicorn.run", fake_run)
    from vectordb.cli import main

    args = [
        "--index-path",
        str(tmp_path / "index.bin"),
        "--data-path",
        str(tmp_path / "data.json"),
    ]

    main(args + ["serve"])

    assert captured["port"] == 8000


def test_cli_index_data_env(tmp_path, monkeypatch):
    captured = {}

    class FakeVectorDB:
        def __init__(self, *, index_path, data_path, **kwargs):
            captured["index"] = index_path
            captured["data"] = data_path

        def add_text(self, text):
            pass

    monkeypatch.setattr("vectordb.cli.VectorDB", FakeVectorDB)

    from vectordb import INDEX_PATH_ENV_VAR, DATA_PATH_ENV_VAR

    index = tmp_path / "i.bin"
    data = tmp_path / "d.json"
    monkeypatch.setenv(INDEX_PATH_ENV_VAR, str(index))
    monkeypatch.setenv(DATA_PATH_ENV_VAR, str(data))

    from vectordb.cli import main

    main(["add", "foo"])

    assert captured["index"] == index
    assert captured["data"] == data


def test_cli_model_name_env(tmp_path, monkeypatch):
    captured = {}

    class FakeVectorDB:
        def __init__(self, *, model_name, **kwargs):
            captured["model"] = model_name

        def add_text(self, text):
            pass

    monkeypatch.setattr("vectordb.cli.VectorDB", FakeVectorDB)

    from vectordb import MODEL_NAME_ENV_VAR

    monkeypatch.setenv(MODEL_NAME_ENV_VAR, "another/model")

    from vectordb.cli import main

    main(["add", "foo"])

    assert captured["model"] == "another/model"


def test_cli_custom_params(tmp_path, monkeypatch):
    captured = {}

    class FakeVectorDB:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def add_text(self, text):
            captured["text"] = text

    monkeypatch.setattr("vectordb.cli.VectorDB", FakeVectorDB)
    from vectordb.cli import main

    args = [
        "--index-path",
        str(tmp_path / "index.bin"),
        "--data-path",
        str(tmp_path / "data.json"),
        "--model-name",
        "custom/model",
        "--max-elements",
        "500",
        "--ef-construction",
        "100",
        "--M",
        "8",
        "--ef",
        "20",
        "--space",
        "ip",
    ]

    main(args + ["add", "foo"])

    assert captured["max_elements"] == 500
    assert captured["ef_construction"] == 100
    assert captured["M"] == 8
    assert captured["ef"] == 20
    assert captured["space"] == "ip"
    assert captured["model_name"] == "custom/model"
    assert captured["text"] == "foo"


def test_cli_log_level(tmp_path, monkeypatch):
    levels = {}

    monkeypatch.setattr(
        "vectordb.cli.VectorDB",
        lambda **kwargs: type("D", (), {"add_text": lambda self, text: None})(),
    )

    def fake_basic(level):
        levels["level"] = level

    monkeypatch.setattr("logging.basicConfig", fake_basic)

    from vectordb.cli import main

    main(
        [
            "--index-path",
            str(tmp_path / "index.bin"),
            "--data-path",
            str(tmp_path / "data.json"),
            "--log-level",
            "DEBUG",
            "add",
            "foo",
        ]
    )

    assert levels["level"] == logging.DEBUG


def test_cli_log_level_env(tmp_path, monkeypatch):
    levels = {}

    monkeypatch.setattr(
        "vectordb.cli.VectorDB",
        lambda **kwargs: type("D", (), {"add_text": lambda self, text: None})(),
    )

    def fake_basic(level):
        levels["level"] = level

    monkeypatch.setattr("logging.basicConfig", fake_basic)

    from vectordb import LOG_LEVEL_ENV_VAR
    monkeypatch.setenv(LOG_LEVEL_ENV_VAR, "INFO")
    from vectordb.cli import main

    main(
        [
            "--index-path",
            str(tmp_path / "index.bin"),
            "--data-path",
            str(tmp_path / "data.json"),
            "add",
            "foo",
        ]
    )

    assert levels["level"] == logging.INFO


def test_cli_query_k_option(tmp_path, monkeypatch):
    captured = {}

    class FakeVectorDB:
        def __init__(self, **kwargs):
            pass

        def search(self, text, k=5):
            captured["k"] = k
            return [{"text": text}]

    monkeypatch.setattr("vectordb.cli.VectorDB", FakeVectorDB)
    from vectordb.cli import main

    main(
        [
            "--index-path",
            str(tmp_path / "index.bin"),
            "--data-path",
            str(tmp_path / "data.json"),
            "query",
            "foo",
            "--k",
            "3",
        ]
    )

    assert captured["k"] == 3


def test_cli_clear_command(tmp_path, monkeypatch):
    called = {}

    def fake_clear(index_path, data_path):
        called["index"] = index_path
        called["data"] = data_path

    monkeypatch.setattr("vectordb.cli.VectorDB.clear", staticmethod(fake_clear))
    from vectordb.cli import main

    main(
        [
            "--index-path",
            str(tmp_path / "index.bin"),
            "--data-path",
            str(tmp_path / "data.json"),
            "clear",
        ]
    )

    assert called["index"] == tmp_path / "index.bin"
    assert called["data"] == tmp_path / "data.json"


def test_cli_max_text_length(tmp_path, monkeypatch):
    from vectordb.cli import main

    called = {}

    class FakeVectorDB:
        def __init__(self, **kwargs):
            called.update(kwargs)

        def add_text(self, text):
            raise ValueError("too long")

    monkeypatch.setattr("vectordb.cli.VectorDB", FakeVectorDB)

    with pytest.raises(ValueError):
        main([
            "--index-path",
            str(tmp_path / "index.bin"),
            "--data-path",
            str(tmp_path / "data.json"),
            "--max-text-length",
            "5",
            "add",
            "toolong",
        ])

    assert called["max_text_length"] == 5


def test_cli_version_option(capsys):
    from vectordb.cli import main
    from vectordb import __version__

    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_cli_stats_command(tmp_path, capsys):
    from vectordb.cli import main

    args = [
        "--index-path",
        str(tmp_path / "index.bin"),
        "--data-path",
        str(tmp_path / "data.json"),
    ]

    main(args + ["add", "foo"])
    main(args + ["stats"])
    captured = capsys.readouterr()
    assert captured.out.strip().endswith("1")
