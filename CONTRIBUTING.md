# Contributing

Thank you for considering contributing to this project! To help us maintain consistency and high quality, please follow these guidelines.

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the test suite to ensure everything works:
   ```bash
   pytest -q
   ```

## Commit Messages

When you submit a pull request, include a clear summary of the change and specify which software architecture “ility” or best practice it addresses. Example:

```
Improve maintainability by adding type hints to VectorDB
```

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions.
- Keep functions small and focused.
- Add docstrings for public functions and classes.

## Pull Requests

1. Create a new branch for your change.
2. Ensure `pytest -q` passes.
3. Document your change in the pull request description, mentioning the targeted “ility”.

We appreciate your contributions!
