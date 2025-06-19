from pathlib import Path

from self_certainty_rlif import generate_preferences, save_jsonl, upload_file, RLIFConfig


def test_generate_and_save(tmp_path):
    prefs = generate_preferences(["prompt"], config=RLIFConfig(n=2, certainty_gap=0.0))
    assert prefs[0]["prompt"] == "prompt"
    path = tmp_path / "out.jsonl"
    save_jsonl(prefs, path)
    assert path.read_text().strip()


def test_upload_file(tmp_path):
    f = tmp_path / "d.jsonl"
    f.write_text("{}\n")
    resp = upload_file(f)
    assert resp["id"] == "file-123"
