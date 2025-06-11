# Experiments Vector DB

This repository provides a small example of using an in-memory vector
database built with [`hnswlib`](https://github.com/nmslib/hnswlib) and
serving it over a REST API with `FastAPI`.  Texts are embedded using a
model loaded from `model2vec`.

The project is organised using a *core layout*.  All package code lives
in `core/vectordb` which contains the database logic, REST API and a
small CLI entry point.

For a history of changes, see [CHANGELOG.md](CHANGELOG.md).

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
binds (these variables are also respected by the CLI), and `VECTORDB_API_KEY`
to require an API key for all requests. `VECTORDB_INDEX_PATH` and
`VECTORDB_DATA_PATH` can override the default locations of the index and stored
texts. `VECTORDB_MODEL_NAME` can set a default embedding model for both the
server and CLI.

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
- `--index-path` path to the HNSW index file (default `index.bin`, or set
  `VECTORDB_INDEX_PATH`, also exported as `vectordb.INDEX_PATH_ENV_VAR`).
- `--data-path` path to the stored texts file (default `data.json`, or set
  `VECTORDB_DATA_PATH`, also exported as `vectordb.DATA_PATH_ENV_VAR`).
  Parent directories are created automatically when saving.
- `--model-name` name of the embedding model to load (default `vectordb.db.MODEL_NAME`,
  or set `VECTORDB_MODEL_NAME`, also exported as `vectordb.MODEL_NAME_ENV_VAR`).
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
- `--host` address for the REST API when serving (default `0.0.0.0`, or set `VECTORDB_HOST`, also exported as `vectordb.HOST_ENV_VAR`).
- `--port` port number for the REST API when serving (default `8000`, or set `VECTORDB_PORT`, also exported as `vectordb.PORT_ENV_VAR`).
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

## Environment Variables

The application can be configured using several `VECTORDB_*` variables. Their
defaults are exposed via constants in `vectordb.__init__`.

| Variable | Description | Constant |
|----------|-------------|---------|
| `VECTORDB_HOST` | Address the REST API binds to when serving | `vectordb.HOST_ENV_VAR` |
| `VECTORDB_PORT` | Port for the REST API | `vectordb.PORT_ENV_VAR` |
| `VECTORDB_API_KEY` | Require this key for all requests | `vectordb.API_KEY_ENV_VAR` |
| `VECTORDB_INDEX_PATH` | Location of the HNSW index file | `vectordb.INDEX_PATH_ENV_VAR` |
| `VECTORDB_DATA_PATH` | Location of stored texts | `vectordb.DATA_PATH_ENV_VAR` |
| `VECTORDB_MODEL_NAME` | Default embedding model name | `vectordb.MODEL_NAME_ENV_VAR` |
| `VECTORDB_LOG_LEVEL` | Default log level for the CLI | `vectordb.LOG_LEVEL_ENV_VAR` |
| `VECTORDB_MAX_ELEMENTS` | Maximum number of elements for the index | `vectordb.MAX_ELEMENTS_ENV_VAR` |
| `VECTORDB_EF_CONSTRUCTION` | HNSW ef_construction parameter | `vectordb.EF_CONSTRUCTION_ENV_VAR` |
| `VECTORDB_M` | HNSW M parameter | `vectordb.M_ENV_VAR` |
| `VECTORDB_EF` | Search ef parameter | `vectordb.EF_ENV_VAR` |
| `VECTORDB_SPACE` | Distance metric for the HNSW index | `vectordb.SPACE_ENV_VAR` |
| `VECTORDB_MAX_TEXT_LENGTH` | Maximum length of text entries | `vectordb.MAX_TEXT_LENGTH_ENV_VAR` |

Example `.env` snippet:

```env
VECTORDB_HOST=0.0.0.0
VECTORDB_PORT=8000
VECTORDB_API_KEY=changeme
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on running tests,
code style, and crafting commit messages. After installing the dependencies,
set up the git hooks with:

```bash
pre-commit install
```

Issue and pull request templates are available in the `.github` directory to
ensure consistent reports and reviews.


## License

This project is licensed under the terms of the [MIT License](LICENSE).
