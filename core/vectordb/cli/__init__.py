"""Command line interface for :mod:`vectordb`."""

import argparse
from pathlib import Path
import logging
import os
import uvicorn

from .. import API_KEY_ENV_VAR, __version__

from ..db import VectorDB, INDEX_PATH, DATA_PATH, MODEL_NAME
from ..api import create_app


def main(argv: list[str] | None = None) -> None:
    """Run the ``vectordb`` command line interface."""

    parser = argparse.ArgumentParser(description="Vector DB CLI")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="show program's version number and exit",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="remove existing index and data before running",
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        default=INDEX_PATH,
        help="location of the HNSW index file",
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        default=DATA_PATH,
        help="location of the stored texts",
    )
    parser.add_argument(
        "--model-name",
        default=MODEL_NAME,
        help="embedding model to use",
    )
    parser.add_argument(
        "--max-elements",
        type=int,
        default=10000,
        help="maximum number of elements for the index",
    )
    parser.add_argument(
        "--ef-construction",
        type=int,
        default=200,
        help="HNSW ef_construction parameter",
    )
    parser.add_argument(
        "--M",
        type=int,
        default=16,
        help="HNSW M parameter",
    )
    parser.add_argument(
        "--ef",
        type=int,
        default=50,
        help="search ef parameter",
    )
    parser.add_argument(
        "--space",
        choices=["cosine", "l2", "ip"],
        default="cosine",
        help="distance metric for the HNSW index",
    )
    parser.add_argument(
        "--max-text-length",
        type=int,
        default=1000,
        help="maximum length of text entries",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        help="logging level (e.g. INFO, DEBUG)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("clear", help="delete stored index and texts and exit")
    serve = subparsers.add_parser("serve", help="start REST server")
    serve.add_argument("--host", default="0.0.0.0", help="host for REST server")
    serve.add_argument("--port", type=int, default=8000, help="port for REST server")
    serve.add_argument(
        "--workers",
        type=int,
        default=1,
        help="number of worker processes for REST server",
    )
    serve.add_argument(
        "--api-key",
        help=(
            "require this API key for REST requests "
            f"(or set {API_KEY_ENV_VAR} env var)"
        ),
    )
    add = subparsers.add_parser("add", help="add text")
    add.add_argument("text", help="text to add")
    query = subparsers.add_parser("query", help="query text")
    query.add_argument("text", help="text to query")
    query.add_argument(
        "--k",
        type=int,
        default=5,
        help="number of results to return",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    if args.command == "clear":
        VectorDB.clear(index_path=args.index_path, data_path=args.data_path)
        return

    if args.delete:
        VectorDB.clear(index_path=args.index_path, data_path=args.data_path)

    vdb = VectorDB(
        index_path=args.index_path,
        data_path=args.data_path,
        model_name=args.model_name,
        max_elements=args.max_elements,
        ef_construction=args.ef_construction,
        M=args.M,
        ef=args.ef,
        space=args.space,
        max_text_length=args.max_text_length,
    )

    if args.command == "serve":
        api_key = args.api_key or os.getenv(API_KEY_ENV_VAR)
        app = create_app(vdb, api_key=api_key)
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level.lower(),
            workers=args.workers,
        )
    elif args.command == "add":
        vdb.add_text(args.text)
    elif args.command == "query":
        print(vdb.search(args.text, k=args.k))
