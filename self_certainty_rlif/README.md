# Self Certainty RLIF

This experiment implements **Reinforcement Learning with Internal Feedback (RLIF)** following the ideas from *Learning to Reason Without External Rewards*. It generates a preference dataset using a model's own self-certainty scores.

The implementation assumes only two operations are available:

1. **Inference** via an OpenAI compatible API.
2. **Uploading** a JSONL file containing `prompt`, `bad_response` and `good_response` fields.

Use `generate_preferences` to collect responses ranked by self-certainty, then save them with `save_jsonl` and upload the file using `upload_file`.
