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

The main code lives in `core/vectordb/` with the `VectorDB` class located in
`core/vectordb/db.py`.

## Installation

Install the dependencies with pip:

```bash
pip install -r requirements.txt
```

## Command Line Usage

Run the CLI using the module entry point.  Because the package lives
under `core`, add it to the Python path first:

```
PYTHONPATH=core python -m vectordb [--delete] {serve,add,query} [text]
```

- `--delete` removes any existing index/data before running.
- `serve` starts the REST API (default port 8000).
- `add` adds a single text entry.
- `query` searches for the most similar texts to the provided query.

Example:

```bash
PYTHONPATH=core python -m vectordb add "Hello world"
PYTHONPATH=core python -m vectordb query "Hello"
```

## REST API

When running `PYTHONPATH=core python -m vectordb serve` an API is exposed with two endpoints:

- `POST /add` – body `{"text": "your text"}`
- `GET /search?q=<query>&k=<k>` – returns top `k` results

## Example

The pytest suite builds an index from sample sentences and verifies that a queried sentence is returned as the top match.

## Testing

Run the tests with:

```bash
pytest -q
```
