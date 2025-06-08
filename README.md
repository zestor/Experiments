# Experiments Vector DB

This repository provides a small example of using an in-memory vector
database built with [`hnswlib`](https://github.com/nmslib/hnswlib) and
serving it over a REST API with `FastAPI`.  Texts are embedded using a
model loaded from `model2vec`.

The project is organised using a *core layout*.  All package code lives
in `core/vectordb` which contains the database logic, REST API and a
small CLI entry point.

## Features

- Add text entries and persist them on disk.
- Perform nearest neighbour search over stored texts.
- Optional REST API server to interact with the database.
- Automatically rebuilds the index if loading existing data fails.
- Validates query parameters to prevent invalid searches.
- Codebase annotated with Python type hints for readability.
- Includes a `py.typed` marker so type checkers can use those hints.

The main code lives in `core/vectordb/` with the `VectorDB` class located in
`core/vectordb/db/`.

## Installation

Install the package in editable mode so the CLI can be run directly:

```bash
pip install -e .
```

This repository uses `pyproject.toml` with `setuptools` so it can be installed
like any other Python package. The automated test suite runs on Python 3.10,
3.11, and 3.12 to ensure broad compatibility.

## Docker

You can build a Docker image to run the REST API in a container:

```bash
docker build -t vectordb .
# run with default host/port
docker run -p 8000:8000 vectordb
# or override host/port via environment variables
docker run -p 8080:8080 -e VECTORDB_HOST=0.0.0.0 -e VECTORDB_PORT=8080 vectordb
```

The container exposes port `8000` and starts the server using the default
settings. Set `VECTORDB_HOST` and `VECTORDB_PORT` to change where the server
binds, and `VECTORDB_API_KEY` to require an API key for all requests.

## Command Line Usage

Run the CLI using the installed entry point:

```
vectordb [--delete] [--index-path INDEX] [--data-path DATA] {serve,add,query,clear,stats} [text]
```

You can also invoke it as a module:

```
python -m vectordb [--delete] [--index-path INDEX] [--data-path DATA] {serve,add,query,clear,stats} [text]
```

- `--delete` removes any existing index/data before running.
- `--index-path` path to the HNSW index file (default `index.bin`).
- `--data-path` path to the stored texts file (default `data.json`).
  Parent directories are created automatically when saving.
- `--model-name` name of the embedding model to load.
- `--max-elements` maximum items to store in the index (default `10000`).
  Adding more than this will raise an error. Value must be at least `1`.
- `--ef-construction` `ef_construction` parameter for building the index (default `200`).
- `--M` `M` parameter controlling HNSW connectivity (default `16`).
- `--ef` `ef` parameter used during search (default `50`).
- `--k` number of nearest neighbours to return when querying (default `5`).
- `--space` distance metric for the index: `cosine`, `l2`, or `ip`.
- `--max-text-length` maximum length of text entries (default `1000`). Value must be at least `1`.
- `--log-level` set the logging level for CLI operations and REST server logs.
- `--version` show the installed `vectordb` version and exit.
- `serve` starts the REST API (use `--host` and `--port` to configure it).
- `--api-key` require this key in the `X-API-Key` header when serving.
 - `VECTORDB_API_KEY` environment variable can also supply the API key (also
   exposed as the constant `vectordb.API_KEY_ENV_VAR`).
- `--host` address for the REST API when serving (default `0.0.0.0`).
- `--port` port number for the REST API when serving (default `8000`).
- `--workers` number of worker processes for the REST API (default `1`).
- `add` adds a single text entry.
- `query` searches for the most similar texts to the provided query.
- `clear` removes any stored index and texts then exits.
- `stats` prints the number of stored texts.

Example:

```bash
vectordb add "Hello world"
vectordb query "Hello"
vectordb stats
```

## REST API

When running `vectordb serve` an API is exposed with four endpoints:

 - `GET /health` – simple health check returning `{"status": "ok"}`
 - `POST /add` – body `{"text": "your text"}`
 - `GET /search?q=<query>&k=<k>` – returns top `k` results
 - `GET /stats` – returns `{"count": <number>}`

 The API validates input:

- Text must be non-empty.
- `k` must be at least 1 and not exceed the number of stored texts.
- Adding a text when the database is full returns a `400` error.

If the server was started with an API key (via `--api-key` or the
`VECTORDB_API_KEY` environment variable), all endpoints except `/health` must
include the same value in the `X-API-Key` header or a `401` error will be
returned. The environment variable name is also exported as
`vectordb.API_KEY_ENV_VAR`.

## Example

The pytest suite builds an index from sample sentences and verifies that a queried sentence is returned as the top match.

## Testing

Run the tests with:

```bash
pytest -q
```

The repository includes a GitHub Actions workflow that automatically runs the
test suite on pushes and pull requests. This ensures changes remain stable and
reduces manual effort when contributing.

## Logging

`vectordb` uses Python's standard `logging` module. Configure the log level in
your application or via the CLI's `--log-level` option to see debug output and
control Uvicorn server verbosity:

- API endpoints log when texts are added or searches are executed so usage can
  be monitored in production.

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on running tests, code style, and crafting commit messages.


## License

This project is licensed under the terms of the [MIT License](LICENSE).
