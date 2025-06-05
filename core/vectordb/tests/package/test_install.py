import subprocess
import sys
from pathlib import Path
import os
from importlib import resources


def test_editable_install(tmp_path):
    root = Path(__file__).resolve().parents[4]
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "-e",
        str(root),
        "--no-deps",
    ])

    # Provide stub modules for the CLI so it runs without optional deps
    stub = tmp_path / "stubs"
    stub.mkdir()
    (stub / "hnswlib.py").write_text("class Index:\n    def __init__(self,*a,**k): pass")
    (stub / "model2vec.py").write_text(
        "class StaticModel:\n    dim=3\n    @classmethod\n    def from_pretrained(cls,n):\n        return cls()\n    def encode(self,t):\n        return [[0,0,0] for _ in t]"
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(stub)

    out = subprocess.check_output(
        [sys.executable, "-m", "vectordb", "--help"], env=env
    )
    assert b"Vector DB CLI" in out

    assert resources.files("vectordb").joinpath("py.typed").is_file()
