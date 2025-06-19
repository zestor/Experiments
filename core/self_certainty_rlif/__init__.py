"""Self Certainty RLIF utilities.

This module implements dataset generation for Reinforcement Learning with
Internal Feedback (RLIF) based on *Learning to Reason Without External
Rewards*. It only relies on an OpenAI compatible API for inference and the
ability to upload a preference dataset.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Tuple
import json
import math
import time

import openai


@dataclass
class RLIFConfig:
    """Configuration for self-certainty preference generation."""

    model: str = "gpt-3.5-turbo"
    n: int = 4
    max_tokens: int = 512
    base_temperature: float = 0.7
    certainty_gap: float = 0.5
    max_retries: int = 3


class SelfCertaintyCalculator:
    """Calculate self-certainty using KL divergence from uniform."""

    def __init__(self, vocab_size: int = 50257) -> None:
        self.vocab_size = vocab_size
        self.uniform = 1.0 / vocab_size

    def from_response(self, response: dict) -> float:
        choice = response.get("choices", [{}])[0]
        probs = choice.get("logprobs", {}).get("content", [])
        if not probs:
            return 0.0
        total = 0.0
        count = 0
        for token in probs:
            lp = token.get("logprob")
            if lp is None:
                continue
            p = math.exp(lp)
            if p > 0:
                total += p * (math.log(p) - math.log(self.uniform))
                count += 1
        return total / count if count else 0.0


class OpenAIClient:
    """Wrapper around ``openai`` with simple retry logic."""

    def __init__(self, api_key: str | None = None, *, max_retries: int = 3) -> None:
        self.api_key = api_key
        self.max_retries = max_retries
        self.scorer = SelfCertaintyCalculator()

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> dict:
        for attempt in range(self.max_retries):
            try:
                return openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    logprobs=True,
                    top_logprobs=5,
                    api_key=self.api_key,
                )
            except Exception:  # pragma: no cover - network failures
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError("exceeded retries")

    def generate_responses(self, prompt: str, cfg: RLIFConfig) -> List[Tuple[str, float]]:
        responses: List[Tuple[str, float]] = []
        for i in range(cfg.n):
            temp = cfg.base_temperature + (i / max(1, cfg.n)) * 0.5
            resp = self.chat(
                [{"role": "user", "content": prompt}],
                model=cfg.model,
                max_tokens=cfg.max_tokens,
                temperature=temp,
            )
            text = resp["choices"][0]["message"]["content"]
            certainty = self.scorer.from_response(resp)
            responses.append((text, certainty))
            time.sleep(0.05)
        return responses


def generate_preferences(
    prompts: Iterable[str],
    *,
    config: RLIFConfig | None = None,
    api_key: str | None = None,
) -> List[Dict[str, str]]:
    """Generate preference data using self-certainty."""

    cfg = config or RLIFConfig()
    client = OpenAIClient(api_key, max_retries=cfg.max_retries)
    data: List[Dict[str, str]] = []

    for prompt in prompts:
        responses = client.generate_responses(prompt, cfg)
        if len(responses) < 2:
            continue
        responses.sort(key=lambda x: x[1], reverse=True)
        best, worst = responses[0], responses[-1]
        if best[1] - worst[1] < cfg.certainty_gap:
            continue
        data.append(
            {
                "prompt": prompt,
                "good_response": best[0],
                "bad_response": worst[0],
            }
        )
    return data


def save_jsonl(data: Iterable[Dict[str, str]], path: Path) -> None:
    """Save preference data as JSONL."""

    path = Path(path)
    with path.open("w") as fh:
        for row in data:
            json.dump(row, fh)
            fh.write("\n")


def upload_file(path: Path, *, purpose: str = "fine-tune") -> dict:
    """Upload ``path`` using the OpenAI API."""

    with Path(path).open("rb") as fh:
        return openai.File.create(file=fh, purpose=purpose)


__all__ = [
    "generate_preferences",
    "save_jsonl",
    "upload_file",
    "RLIFConfig",
    "OpenAIClient",
    "SelfCertaintyCalculator",
]
