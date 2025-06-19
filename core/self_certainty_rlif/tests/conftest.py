from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class DummyChatCompletion:
    calls = 0

    @classmethod
    def create(
        cls,
        model="",
        messages=None,
        max_tokens=None,
        temperature=None,
        logprobs=False,
        top_logprobs=0,
        api_key=None,
    ):
        cls.calls += 1
        logprob = -0.1 * cls.calls
        return {
            "choices": [
                {
                    "message": {"content": f"answer{cls.calls}"},
                    "logprobs": {"content": [{"logprob": logprob}]},
                }
            ]
        }

class DummyFile:
    @classmethod
    def create(cls, file, purpose="fine-tune"):
        return {"id": "file-123", "purpose": purpose}

openai_stub = types.SimpleNamespace(ChatCompletion=DummyChatCompletion, File=DummyFile)
sys.modules.setdefault("openai", openai_stub)
