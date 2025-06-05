import argparse
from pathlib import Path
import uvicorn

from ..db import VectorDB, INDEX_PATH, DATA_PATH
from ..api import create_app


def main(argv=None):
    parser = argparse.ArgumentParser(description="Vector DB CLI")
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
    subparsers = parser.add_subparsers(dest="command", required=True)
    serve = subparsers.add_parser("serve", help="start REST server")
    serve.add_argument("--host", default="0.0.0.0", help="host for REST server")
    serve.add_argument(
        "--port", type=int, default=8000, help="port for REST server"
    )
    add = subparsers.add_parser("add", help="add text")
    add.add_argument("text", help="text to add")
    query = subparsers.add_parser("query", help="query text")
    query.add_argument("text", help="text to query")
    args = parser.parse_args(argv)

    if args.delete:
        VectorDB.clear(index_path=args.index_path, data_path=args.data_path)

    vdb = VectorDB(index_path=args.index_path, data_path=args.data_path)

    if args.command == "serve":
        app = create_app(vdb)
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.command == "add":
        vdb.add_text(args.text)
    elif args.command == "query":
        print(vdb.search(args.text, k=5))
